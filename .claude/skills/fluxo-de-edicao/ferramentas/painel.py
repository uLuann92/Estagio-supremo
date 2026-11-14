#!/usr/bin/env python3
"""Painéis de mangá para animar: fatiar a página, montar máscaras e separar camadas.

Precisa de: numpy, pillow e opencv-python-headless (pip install).

  painel.py fatiar pagina.png --saida paineis/            página -> um PNG por quadro + folha numerada
  painel.py mascaras painel.png --json elementos.json --saida mascaras/
                                                          resposta do Gemini (caixas e máscaras) -> PNGs
  painel.py camadas painel.png --mascara m1.png m2.png --saida camadas/
                                                          recorta cada camada e fecha o buraco do fundo

O ofício (o que conferir, quando refazer à mão): guias/etapa-paineis.md
"""
import argparse
import base64
import io
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image


def ler_cinza(caminho):
    img = cv2.imdecode(np.fromfile(caminho, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        sys.exit(f"ERRO: não consegui abrir {caminho}")
    return img


def ler_cor(caminho):
    img = cv2.imdecode(np.fromfile(caminho, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"ERRO: não consegui abrir {caminho}")
    return img


def gravar(caminho, img):
    ok, buf = cv2.imencode(os.path.splitext(caminho)[1], img)
    if not ok:
        sys.exit(f"ERRO: não consegui gravar {caminho}")
    buf.tofile(caminho)


# ---------- fatiar ----------

def cmd_fatiar(a):
    cinza = ler_cinza(a.pagina)
    cor = ler_cor(a.pagina)
    h, w = cinza.shape
    # tudo o que não é papel vira "tinta"; fechar une o traço da moldura ao conteúdo do quadro
    tinta = (cinza < a.branco).astype(np.uint8) * 255
    k = max(3, int(min(h, w) * 0.004)) | 1
    tinta = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    contornos, _ = cv2.findContours(tinta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    caixas = []
    for c in contornos:
        x, y, cw, ch = cv2.boundingRect(c)
        if cw * ch >= a.area_minima * w * h and cw > w * 0.08 and ch > h * 0.04:
            caixas.append([x, y, cw, ch])
    if not caixas:
        sys.exit("ERRO: nenhum quadro achado. Página sem calha branca (sangrada)? Recorte à mão ou mude --branco.")
    # ordem de leitura: fileiras de cima para baixo; dentro da fileira, direita -> esquerda (mangá)
    caixas.sort(key=lambda b: b[1])
    fileiras, atual = [], [caixas[0]]
    for b in caixas[1:]:
        topo = min(c[1] for c in atual)
        base = max(c[1] + c[3] for c in atual)
        if b[1] < topo + (base - topo) * 0.5:
            atual.append(b)
        else:
            fileiras.append(atual)
            atual = [b]
    fileiras.append(atual)
    ordem = []
    for f in fileiras:
        ordem += sorted(f, key=lambda b: b[0], reverse=(a.leitura == "manga"))
    os.makedirs(a.saida, exist_ok=True)
    base_nome = os.path.splitext(os.path.basename(a.pagina))[0]
    folha = cor.copy()
    itens = []
    for i, (x, y, cw, ch) in enumerate(ordem, 1):
        nome = f"{base_nome}_q{i:02d}.png"
        gravar(os.path.join(a.saida, nome), cor[y:y + ch, x:x + cw])
        itens.append({"id": f"q{i:02d}", "arquivo": nome, "x": x, "y": y, "largura": cw, "altura": ch,
                      "inteiro": bool(x > 2 and y > 2 and x + cw < w - 2 and y + ch < h - 2)})
        cv2.rectangle(folha, (x, y), (x + cw, y + ch), (0, 0, 255), max(3, w // 300))
        tam = max(1.2, w / 500)
        cv2.putText(folha, str(i), (x + 14, y + int(40 * tam)), cv2.FONT_HERSHEY_SIMPLEX, tam, (0, 0, 255),
                    max(3, int(tam * 2.5)))
    gravar(os.path.join(a.saida, f"{base_nome}_folha.jpg"), folha)
    with open(os.path.join(a.saida, f"{base_nome}_quadros.json"), "w", encoding="utf-8") as f:
        json.dump({"pagina": os.path.basename(a.pagina), "largura": w, "altura": h, "leitura": a.leitura,
                   "quadros": itens}, f, ensure_ascii=False, indent=1)
    print(f"{len(itens)} quadro(s) em {a.saida}. Confira a folha numerada: {base_nome}_folha.jpg")


# ---------- máscaras a partir da resposta do Gemini ----------

def carregar_json_solto(caminho):
    """Lê o JSON mesmo que venha dentro de um bloco ```json … ```."""
    with open(caminho, encoding="utf-8") as f:
        t = f.read().strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    d = json.loads(t)
    if isinstance(d, dict):
        for v in d.values():
            if isinstance(v, list):
                return v
        return [d]
    return d


def cmd_mascaras(a):
    cinza = ler_cinza(a.painel)
    h, w = cinza.shape
    elementos = carregar_json_solto(a.json)
    os.makedirs(a.saida, exist_ok=True)
    feitos = []
    for i, e in enumerate(elementos, 1):
        caixa = e.get("box_2d") or e.get("caixa")
        if not caixa or len(caixa) != 4:
            print(f"  elemento {i} sem caixa: pulado")
            continue
        # convenção do Gemini: [y0, x0, y1, x1] em milésimos da imagem
        y0, x0, y1, x1 = [float(v) for v in caixa]
        x0, x1 = sorted((int(x0 / 1000 * w), int(x1 / 1000 * w)))
        y0, y1 = sorted((int(y0 / 1000 * h), int(y1 / 1000 * h)))
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
        if x1 - x0 < 4 or y1 - y0 < 4:
            print(f"  elemento {i} com caixa vazia: pulado")
            continue
        masc = np.zeros((h, w), np.uint8)
        origem = "caixa"
        bruto = e.get("mask") or e.get("mascara")
        if isinstance(bruto, str) and len(bruto) > 100:
            try:
                dados = base64.b64decode(bruto.split(",", 1)[-1])
                m = np.array(Image.open(io.BytesIO(dados)).convert("L"))
                m = cv2.resize(m, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
                masc[y0:y1, x0:x1] = np.where(m > 127, 255, 0)
                origem = "mascara"
            except Exception as erro:
                print(f"  elemento {i}: máscara ilegível ({erro}); usando a silhueta dentro da caixa")
        if origem == "caixa":
            masc[y0:y1, x0:x1] = silhueta(cinza[y0:y1, x0:x1], a.branco)
            origem = "silhueta"
        rotulo = str(e.get("label") or e.get("nome") or f"elemento{i}")
        limpo = "".join(c if c.isalnum() else "_" for c in rotulo.lower())[:30].strip("_") or f"elemento{i}"
        nome = f"m{i:02d}_{limpo}.png"
        gravar(os.path.join(a.saida, nome), masc)
        feitos.append({"arquivo": nome, "rotulo": rotulo, "origem": origem,
                       "caixa": [x0, y0, x1 - x0, y1 - y0], "cobre": round(float((masc > 0).mean()), 3)})
        print(f"  {nome}: {origem}, cobre {feitos[-1]['cobre'] * 100:.0f}% do quadro")
    with open(os.path.join(a.saida, "mascaras.json"), "w", encoding="utf-8") as f:
        json.dump(feitos, f, ensure_ascii=False, indent=1)
    print("Confira cada máscara sobre o quadro antes de separar as camadas (o contorno costuma pedir retoque).")


def silhueta(recorte, branco):
    """Dentro de uma caixa, a figura fechada pelo traço: o papel ligado à borda da caixa fica de fora."""
    tinta = (recorte < branco).astype(np.uint8)
    k = max(3, int(min(recorte.shape) * 0.012)) | 1
    fechado = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    papel = (1 - fechado).astype(np.uint8)
    h, w = papel.shape
    borda = np.zeros((h + 2, w + 2), np.uint8)
    pintado = papel.copy()
    for x in range(0, w, 4):
        for y in (0, h - 1):
            if pintado[y, x] == 1:
                cv2.floodFill(pintado, borda, (x, y), 2)
    for y in range(0, h, 4):
        for x in (0, w - 1):
            if pintado[y, x] == 1:
                cv2.floodFill(pintado, borda, (x, y), 2)
    dentro = (pintado != 2).astype(np.uint8)
    # fica só o maior bloco ligado (tira linhas de velocidade soltas)
    n, rot, est, _ = cv2.connectedComponentsWithStats(dentro, 8)
    if n > 1:
        maior = 1 + int(np.argmax(est[1:, cv2.CC_STAT_AREA]))
        dentro = (rot == maior).astype(np.uint8)
    return dentro * 255


# ---------- camadas ----------

def cmd_camadas(a):
    cor = ler_cor(a.painel)
    h, w = cor.shape[:2]
    os.makedirs(a.saida, exist_ok=True)
    uniao = np.zeros((h, w), np.uint8)
    info = []
    for i, caminho in enumerate(a.mascara, 1):
        m = ler_cinza(caminho)
        if m.shape != (h, w):
            m = cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST)
        m = np.where(m > 127, 255, 0).astype(np.uint8)
        m[uniao > 0] = 0  # a primeira máscara é a da frente: as de trás não repetem os pixels dela
        if not m.any():
            print(f"  {os.path.basename(caminho)}: vazia depois de tirar as camadas da frente; pulada")
            continue
        uniao |= m
        alfa = cv2.GaussianBlur(m, (0, 0), a.suave) if a.suave > 0 else m
        alfa = np.where(m > 0, np.maximum(alfa, 128), alfa)  # suaviza só a borda de fora
        ys, xs = np.where(alfa > 8)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rgba = np.dstack([cor[y0:y1, x0:x1], alfa[y0:y1, x0:x1]])
        nome = f"camada_{i:02d}.png"
        gravar(os.path.join(a.saida, nome), rgba)
        info.append({"arquivo": nome, "mascara": os.path.basename(caminho), "ordem": i,
                     "x": int(x0), "y": int(y0), "largura": int(x1 - x0), "altura": int(y1 - y0)})
    if not info:
        sys.exit("ERRO: nenhuma camada saiu das máscaras.")
    # fundo: fecha o buraco deixado pelas camadas. Bom para movimentos pequenos; buraco grande pede retoque.
    k = max(3, int(a.folga)) | 1
    buraco = cv2.dilate(uniao, np.ones((k, k), np.uint8))
    fundo = cv2.inpaint(cor, buraco, a.raio, cv2.INPAINT_TELEA)
    gravar(os.path.join(a.saida, "fundo.png"), fundo)
    with open(os.path.join(a.saida, "camadas.json"), "w", encoding="utf-8") as f:
        json.dump({"painel": os.path.basename(a.painel), "largura": w, "altura": h, "fundo": "fundo.png",
                   "buraco_no_fundo": round(float((buraco > 0).mean()), 3), "camadas": info},
                  f, ensure_ascii=False, indent=1)
    pct = (buraco > 0).mean() * 100
    print(f"{len(info)} camada(s) + fundo em {a.saida}. O buraco fechado cobre {pct:.0f}% do quadro.")
    if pct > 35:
        print("Aviso: buraco grande. O fundo refeito serve para pouco movimento; para muito, peça um fundo limpo.")


def main():
    p = argparse.ArgumentParser(description="Painéis de mangá para animar.")
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fatiar", help="separa a página em quadros")
    f.add_argument("pagina")
    f.add_argument("--saida", required=True)
    f.add_argument("--leitura", choices=["manga", "ocidental"], default="manga",
                   help="manga: da direita para a esquerda (padrão)")
    f.add_argument("--branco", type=int, default=235, help="acima deste cinza (0-255) é papel")
    f.add_argument("--area-minima", type=float, default=0.02, help="fração mínima da página para ser um quadro")
    f.set_defaults(f=cmd_fatiar)

    m = sub.add_parser("mascaras", help="transforma a resposta do Gemini em máscaras PNG")
    m.add_argument("painel")
    m.add_argument("--json", required=True, help="resposta com box_2d [y0,x0,y1,x1 em milésimos], label e mask (opcional)")
    m.add_argument("--saida", required=True)
    m.add_argument("--branco", type=int, default=235)
    m.set_defaults(f=cmd_mascaras)

    c = sub.add_parser("camadas", help="recorta as camadas e fecha o buraco do fundo")
    c.add_argument("painel")
    c.add_argument("--mascara", nargs="+", required=True, help="da frente para trás (branco = a camada)")
    c.add_argument("--saida", required=True)
    c.add_argument("--suave", type=float, default=1.2, help="suavização da borda, em pixels")
    c.add_argument("--folga", type=int, default=9, help="quanto o buraco do fundo passa da máscara, em pixels")
    c.add_argument("--raio", type=int, default=7, help="raio do preenchimento do fundo")
    c.set_defaults(f=cmd_camadas)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
