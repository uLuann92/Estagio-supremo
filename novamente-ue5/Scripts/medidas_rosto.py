"""
medidas_rosto.py - a ficha de medidas do rosto do protagonista, tirada da referência, e a comparação com o jogo.

Marca 478 pontos no rosto (MediaPipe), alinha pela linha das pupilas e mede tudo que a foto deixa medir:
larguras, alturas, ângulos, proporções, assimetria e as cores (pele, cabelo, íris, lábio, sobrancelha, roupa).
As medidas saem em fração da distância entre os cantos externos dos olhos (não dependem do tamanho da foto)
e em centímetros estimados a partir da distância entre as pupilas (--dip-cm, padrão 6,0 cm para 13-14 anos).

Uso:
  pip install mediapipe opencv-python numpy
  python Scripts/medidas_rosto.py --ficha Referencias/luan_crianca_close.jpg --out Referencias/ficha_luan.json
  python Scripts/medidas_rosto.py --comparar Referencias/ficha_luan.json --shot Saved/Review/<data>/Rev_05_Rosto_Close_q4.png
  python Scripts/medidas_rosto.py --comparar ... --shot ... --com-expressao    (quando a expressão da referência foi repetida)
  python Scripts/medidas_rosto.py --comparar ... --shot ... --com-cor          (foto na luz da referência: cores contam)

As medidas de "identidade" (osso, olho, nariz, largura do rosto) valem sempre. As de "expressão" (boca, queixo com
a boca aberta, sobrancelha levantada, abertura do olho) só reprovam com --com-expressao, porque dependem da pose.
Orelha e perfil não aparecem na malha de pontos: confira por sobreposição da vista de perfil.

Saída: tabela no terminal, JSON e código 0 (passou) ou 1 (reprovou).
"""

import argparse
import json
import math
import os
import sys
import urllib.request

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fidelidade as F  # noqa: E402  (mesmo modelo de rosto e mesma leitura de imagem)

SEG_URL = ("https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/"
           "float32/latest/selfie_multiclass_256x256.tflite")
SEG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos", "selfie_multiclass_256x256.tflite")
SEG_CLASSES = {1: "cabelo", 2: "pele_corpo", 3: "pele_rosto", 4: "roupa"}

TOL_IDENTIDADE = 0.03   # 3% em cada medida de identidade
TOL_EXPRESSAO = 0.06    # 6% nas de expressão (só com --com-expressao)
TOL_ANGULO = 2.0        # graus
TOL_MEDIA = 0.02        # erro médio das medidas de identidade
TOL_COR = 6.0           # Delta E 2000 das cores iluminadas (só com --com-cor, na luz da referência)
TOL_PELE = 5.0          # Delta E 2000 da pele das bochechas
CORES = ["pele_rosto", "cabelo", "sobrancelhas", "iris_dir", "iris_esq", "labios", "roupa"]

# (nome, pontos, tipo de medida, identidade?, o que é)
# tipo: "d" distância, "v" só a componente vertical, "h" só a horizontal
MEDIDAS = [
    ("dist_pupilas", (468, 473), "d", True, "centro de uma pupila ao da outra"),
    ("largura_olho_dir", (33, 133), "d", True, "canto externo ao interno, olho direito do personagem"),
    ("largura_olho_esq", (362, 263), "d", True, "canto interno ao externo, olho esquerdo"),
    ("distancia_entre_olhos", (133, 362), "d", True, "entre os cantos internos"),
    ("largura_iris", None, "d", True, "diâmetro da íris (média dos dois olhos)"),
    ("largura_testa", (54, 284), "h", True, "testa, na altura das entradas"),
    ("largura_temporas", (127, 356), "h", True, "têmporas, na linha dos olhos"),
    ("largura_macas", (234, 454), "h", True, "maior largura do rosto, nas maçãs"),
    ("largura_mandibula", (172, 397), "h", True, "ângulo da mandíbula"),
    ("largura_mandibula_baixa", (136, 365), "h", True, "mandíbula entre o ângulo e o queixo"),
    ("largura_queixo", (148, 377), "h", True, "queixo"),
    ("largura_ponte_nariz", (193, 417), "h", True, "ponte do nariz entre os olhos"),
    ("largura_nariz", (129, 358), "h", True, "asas do nariz"),
    ("largura_sobrancelha_dir", (70, 107), "h", True, "sobrancelha direita, da ponta de fora à de dentro"),
    ("largura_sobrancelha_esq", (336, 300), "h", True, "sobrancelha esquerda"),
    ("entre_sobrancelhas", (107, 336), "h", True, "vão entre as sobrancelhas"),
    ("testa_ate_glabela", (10, 9), "v", True, "do alto da testa medida ao meio das sobrancelhas"),
    ("glabela_ate_base_nariz", (9, 2), "v", True, "terço médio: meio das sobrancelhas à base do nariz"),
    ("comprimento_nariz", (168, 2), "v", True, "raiz do nariz à base"),
    ("raiz_ate_ponta_nariz", (168, 1), "v", True, "raiz do nariz à ponta"),
    ("pupilas_ate_base_nariz", ("pupilas", 2), "v", True, "linha das pupilas à base do nariz"),
    ("filtro", (2, 0), "v", True, "base do nariz ao contorno do lábio de cima"),
    ("largura_boca", (61, 291), "d", False, "canto a canto da boca"),
    ("arco_do_cupido", (37, 267), "h", False, "picos do arco do lábio de cima"),
    ("labio_superior", (0, 13), "v", False, "altura do lábio de cima"),
    ("labio_inferior", (14, 17), "v", False, "altura do lábio de baixo"),
    ("abertura_boca", (13, 14), "v", False, "entre os lábios"),
    ("labio_ate_queixo", (17, 152), "v", False, "lábio de baixo à ponta do queixo"),
    ("base_nariz_ate_queixo", (2, 152), "v", False, "terço inferior"),
    ("altura_rosto_visivel", (10, 152), "v", False, "alto da testa medida à ponta do queixo"),
    ("pupilas_ate_boca", ("pupilas", "boca"), "v", False, "linha das pupilas ao meio da boca"),
    ("abertura_olho_dir", (159, 145), "v", False, "pálpebra de cima à de baixo"),
    ("abertura_olho_esq", (386, 374), "v", False, "pálpebra de cima à de baixo"),
    ("sobrancelha_ate_olho_dir", (105, 159), "v", False, "pico da sobrancelha à pálpebra"),
    ("sobrancelha_ate_olho_esq", (334, 386), "v", False, "pico da sobrancelha à pálpebra"),
]
ANGULOS = [
    ("inclinacao_olhos", True, "canto externo acima do interno é positivo (graus)"),
    ("inclinacao_sobrancelhas", False, "da ponta de dentro ao pico (graus)"),
    ("angulo_mandibula_frontal", True, "no ângulo da mandíbula, entre a maçã e o queixo, vista de frente (graus)"),
]
PROPORCOES = [
    ("quintos", True, "largura das maçãs dividida pela largura média do olho (o clássico é 5)"),
    ("mandibula_por_macas", True, "largura da mandíbula dividida pela das maçãs"),
    ("nariz_por_entre_olhos", True, "largura do nariz dividida pela distância entre os olhos"),
    ("indice_facial", False, "largura das maçãs dividida pela altura visível do rosto"),
    ("boca_por_nariz", False, "largura da boca dividida pela do nariz"),
]

LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LIPS_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
BROW_R = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
EYE_R = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
EYE_L = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
BROW_L = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]


def align(pts):
    """Gira e centraliza os pontos para a linha das pupilas ficar horizontal."""
    r, l = pts[468], pts[473]
    ang = math.atan2(l[1] - r[1], l[0] - r[0])
    c, s = math.cos(-ang), math.sin(-ang)
    rot = np.array([[c, -s], [s, c]])
    return (pts - (r + l) / 2) @ rot.T, math.degrees(ang)


def point(pts, key):
    if key == "pupilas":
        return (pts[468] + pts[473]) / 2
    if key == "boca":
        return (pts[13] + pts[14]) / 2
    return pts[key]


def measure(pts, a, b, kind):
    pa, pb = point(pts, a), point(pts, b)
    if kind == "v":
        return abs(pb[1] - pa[1])
    if kind == "h":
        return abs(pb[0] - pa[0])
    return float(np.linalg.norm(pb - pa))


def angle_at(p, a, b):
    v1, v2 = a - p, b - p
    cosang = np.dot(v1, v2) / max(np.linalg.norm(v1) * np.linalg.norm(v2), 1e-9)
    return math.degrees(math.acos(max(-1.0, min(1.0, cosang))))


def tilt(inner, outer):
    """Inclinação da linha interno->externo; y cresce para baixo na imagem."""
    return math.degrees(math.atan2(inner[1] - outer[1], abs(outer[0] - inner[0])))


def lab_hex(bgr_pixels):
    """Cor mediana e a cor das partes iluminadas (acima do 70º percentil de luz)."""
    px = np.asarray(bgr_pixels, np.uint8).reshape(-1, 3)
    L = cv2.cvtColor(px.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB)[:, 0, 0]
    lit = px[L >= np.percentile(L, 70)]

    def one(sel):
        med = np.median(sel, axis=0).astype(np.uint8)
        lab = cv2.cvtColor(med.reshape(1, 1, 3), cv2.COLOR_BGR2LAB)[0, 0].astype(float)
        b, g, r = [int(x) for x in med]
        return [round(float(lab[0]) * 100 / 255, 1), round(float(lab[1]) - 128, 1), round(float(lab[2]) - 128, 1)], "#%02X%02X%02X" % (r, g, b)

    lab, hx = one(px)
    lab_lit, hx_lit = one(lit)
    return {"lab": lab, "hex": hx, "lab_iluminado": lab_lit, "hex_iluminado": hx_lit, "pixels": int(len(px))}


def poly_mask(shape, pts, idx):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.round(pts[idx]).astype(np.int32)], 255)
    return m


def colors(bgr, raw):
    """Cores medianas das regiões (sob a luz da foto)."""
    out = {}
    h, w = bgr.shape[:2]
    # íris: anel entre a pupila e a borda, só dentro da abertura do olho (sem pálpebra e cílio), sem reflexo
    yy, xx = np.mgrid[0:h, 0:w]
    for side, c, e, contour in (("iris_dir", 468, (469, 471), EYE_R), ("iris_esq", 473, (474, 476), EYE_L)):
        rad = np.linalg.norm(raw[e[0]] - raw[e[1]]) / 2
        d = np.hypot(xx - raw[c][0], yy - raw[c][1])
        ring = (d > rad * 0.35) & (d < rad * 0.9) & (poly_mask(bgr.shape, raw, contour) > 0)
        px = bgr[ring]
        if len(px) < 20:
            continue
        L = cv2.cvtColor(px.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB)[:, 0, 0]
        px = px[(L >= np.percentile(L, 30)) & (L < 0.85 * 255)]
        if len(px):
            out[side] = lab_hex(px)
    cheeks = F.skin_lab(bgr, raw)
    if cheeks:
        out["bochechas_lab"] = [round(float(x), 1) for x in cheeks]
    lips = cv2.subtract(poly_mask(bgr.shape, raw, LIPS_OUTER), poly_mask(bgr.shape, raw, LIPS_INNER))
    if lips.any():
        out["labios"] = lab_hex(bgr[lips > 0])
    brows = cv2.bitwise_or(poly_mask(bgr.shape, raw, BROW_R), poly_mask(bgr.shape, raw, BROW_L))
    if brows.any():
        px = bgr[brows > 0]
        L = cv2.cvtColor(px.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB)[:, 0, 0]
        px = px[L <= np.percentile(L, 40)]   # os fios, não a pele entre eles
        out["sobrancelhas"] = lab_hex(px)
    try:
        seg = segment(bgr)
    except Exception as e:  # sem o modelo de segmentação, as outras cores continuam
        out["aviso_segmentacao"] = str(e)
        return out
    for cls, name in SEG_CLASSES.items():
        px = bgr[seg == cls]
        if len(px) > 200:
            out[name] = lab_hex(px)
    return out


def segment(bgr):
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    import mediapipe as mp
    if not os.path.exists(SEG_PATH):
        os.makedirs(os.path.dirname(SEG_PATH), exist_ok=True)
        print("Baixando o modelo de segmentação do MediaPipe (uma vez só)...")
        urllib.request.urlretrieve(SEG_URL, SEG_PATH)
    options = vision.ImageSegmenterOptions(base_options=mp_python.BaseOptions(model_asset_path=SEG_PATH),
                                           output_category_mask=True)
    with vision.ImageSegmenter.create_from_options(options) as seg:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        res = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
        mask = np.squeeze(res.category_mask.numpy_view()).astype(np.uint8)
        if mask.shape != bgr.shape[:2]:
            mask = cv2.resize(mask, (bgr.shape[1], bgr.shape[0]), interpolation=cv2.INTER_NEAREST)
        return mask


def ficha(detector, path, dip_cm):
    bgr = F.read_image(path)
    raw = F.landmarks(detector, bgr)
    if raw is None:
        sys.exit("Nenhum rosto encontrado em " + path)
    pts, roll = align(raw)
    unit = float(np.linalg.norm(pts[33] - pts[263]))
    cm_per_unit = dip_cm / (float(np.linalg.norm(pts[468] - pts[473])) / unit)
    rows = []
    for name, pair, kind, ident, desc in MEDIDAS:
        if name == "largura_iris":
            val = (np.linalg.norm(pts[469] - pts[471]) + np.linalg.norm(pts[474] - pts[476])) / 2
        else:
            val = measure(pts, pair[0], pair[1], kind)
        frac = float(val) / unit
        rows.append({"medida": name, "valor": round(frac, 4), "cm": round(frac * cm_per_unit, 2), "identidade": ident, "o_que_e": desc})

    ang = {
        "inclinacao_olhos": (tilt(pts[133], pts[33]) + tilt(pts[362], pts[263])) / 2,
        "inclinacao_sobrancelhas": (tilt(pts[107], pts[105]) + tilt(pts[336], pts[334])) / 2,
        "angulo_mandibula_frontal": (angle_at(pts[172], pts[234], pts[152]) + angle_at(pts[397], pts[454], pts[152])) / 2,
    }
    for name, ident, desc in ANGULOS:
        rows.append({"medida": name, "valor": round(ang[name], 2), "graus": True, "identidade": ident, "o_que_e": desc})

    v = {r["medida"]: r["valor"] for r in rows}
    eye = (v["largura_olho_dir"] + v["largura_olho_esq"]) / 2
    prop = {
        "quintos": v["largura_macas"] / eye,
        "mandibula_por_macas": v["largura_mandibula"] / v["largura_macas"],
        "nariz_por_entre_olhos": v["largura_nariz"] / v["distancia_entre_olhos"],
        "indice_facial": v["largura_macas"] / v["altura_rosto_visivel"],
        "boca_por_nariz": v["largura_boca"] / v["largura_nariz"],
    }
    for name, ident, desc in PROPORCOES:
        rows.append({"medida": name, "valor": round(prop[name], 4), "razao": True, "identidade": ident, "o_que_e": desc})

    mid = (pts[168][0] + pts[152][0]) / 2
    assim = {
        "olhos_pct": abs(v["largura_olho_dir"] - v["largura_olho_esq"]) / eye * 100,
        "boca_pct": abs(abs(pts[61][0] - mid) - abs(pts[291][0] - mid)) / unit * 100,
        "macas_pct": abs(abs(pts[234][0] - mid) - abs(pts[454][0] - mid)) / unit * 100,
    }
    return {
        "imagem": os.path.basename(path),
        "unidade": "fração da distância entre os cantos externos dos olhos",
        "unidade_cm": round(cm_per_unit, 3),
        "dip_cm_ancora": dip_cm,
        "giro_cabeca_graus": round(roll, 2),
        "giro_lateral": round(float((pts[1][0] - (pts[234][0] + pts[454][0]) / 2) / unit), 3),
        "medidas": rows,
        "assimetria": {k: round(x, 2) for k, x in assim.items()},
        "cores": colors(bgr, raw),
    }


def compare(ref, shot, with_expr, with_color=False):
    by = {r["medida"]: r for r in shot["medidas"]}
    rows, ident_errs, passed = [], [], True
    if abs(ref["giro_lateral"] - shot["giro_lateral"]) > 0.05:
        passed = False
    for r in ref["medidas"]:
        s = by[r["medida"]]
        counts = r["identidade"] or with_expr
        if r.get("graus"):
            err = abs(s["valor"] - r["valor"])
            ok = err <= TOL_ANGULO
            shown = "%.1f°" % err
        else:
            err = abs(s["valor"] - r["valor"]) / max(abs(r["valor"]), 1e-6)
            ok = err <= (TOL_IDENTIDADE if r["identidade"] else TOL_EXPRESSAO)
            shown = "%.1f%%" % (err * 100)
            if r["identidade"]:
                ident_errs.append(err)
        if counts and not ok:
            passed = False
        rows.append({"medida": r["medida"], "ref": r["valor"], "jogo": s["valor"], "erro": shown, "dentro": ok,
                     "conta": counts, "passou": ok or not counts, "identidade": r["identidade"]})
    mean = float(np.mean(ident_errs)) if ident_errs else 0.0
    if mean > TOL_MEDIA:
        passed = False
    colors_rows = []
    rc, sc = ref.get("cores", {}), shot.get("cores", {})
    pairs = [("bochechas", rc.get("bochechas_lab"), sc.get("bochechas_lab"), TOL_PELE)]
    pairs += [(k, rc[k]["lab_iluminado"], sc[k]["lab_iluminado"], TOL_COR) for k in CORES if k in rc and k in sc]
    for name, a, b, tol in pairs:
        if a is None or b is None:
            continue
        de = F.delta_e_2000(a, b)
        ok = de <= tol
        if with_color and not ok:
            passed = False
        colors_rows.append({"cor": name, "delta_e": round(de, 1), "limite": tol, "dentro": ok, "conta": with_color})
    failed = [x["medida"] for x in sorted((x for x in rows if not x["passou"]), key=lambda x: x["medida"])]
    failed += ["cor " + c["cor"] for c in colors_rows if c["conta"] and not c["dentro"]]
    if abs(ref["giro_lateral"] - shot["giro_lateral"]) > 0.05:
        failed.insert(0, "ângulo da cabeça diferente da referência (refaça a foto no mesmo ângulo)")
    if mean > TOL_MEDIA:
        failed.insert(0, "erro médio de identidade %.1f%%" % (mean * 100))
    return {"passou": passed, "erro_medio_identidade_pct": round(mean * 100, 2), "linhas": rows, "cores": colors_rows,
            "giro_lateral_ref": ref["giro_lateral"], "giro_lateral_jogo": shot["giro_lateral"],
            "reprovadas": failed}


def print_ficha(f):
    print("\nFICHA · %s  (1 unidade = %.2f cm pela âncora de %.1f cm entre as pupilas)" % (f["imagem"], f["unidade_cm"], f["dip_cm_ancora"]))
    for r in f["medidas"]:
        tag = "" if r["identidade"] else "  (expressão)"
        if r.get("graus"):
            print("  %-28s %7.2f°%s" % (r["medida"], r["valor"], tag))
        elif r.get("razao"):
            print("  %-28s %7.3f %s" % (r["medida"], r["valor"], tag))
        else:
            print("  %-28s %7.4f   ~%5.2f cm%s" % (r["medida"], r["valor"], r["cm"], tag))
    print("  assimetria: " + ", ".join("%s %.1f" % kv for kv in f["assimetria"].items()))
    for k, c in f["cores"].items():
        if isinstance(c, dict):
            print("  cor %-14s mediana %s Lab %s · iluminada %s Lab %s" % (k, c["hex"], c["lab"], c["hex_iluminado"], c["lab_iluminado"]))
        elif k == "bochechas_lab":
            print("  cor bochechas      Lab %s" % (c,))


def print_compare(c):
    print("\nCOMPARAÇÃO (identidade até %.0f%% cada, média até %.0f%%; ângulos até %.0f°)" % (TOL_IDENTIDADE * 100, TOL_MEDIA * 100, TOL_ANGULO))
    for r in c["linhas"]:
        flag = "ok" if r["dentro"] else ("ERRO" if r["conta"] else "fora")
        note = "" if r["conta"] else "  (expressão, não conta)"
        print("  %-28s ref %8.4f  jogo %8.4f  %7s  %s%s" % (r["medida"], r["ref"], r["jogo"], r["erro"], flag, note))
    for r in c.get("cores", []):
        flag = "ok" if r["dentro"] else ("ERRO" if r["conta"] else "fora")
        note = "" if r["conta"] else "  (cor, não conta sem --com-cor)"
        print("  cor %-24s Delta E %5.1f (limite %.0f)  %s%s" % (r["cor"], r["delta_e"], r["limite"], flag, note))
    print("  giro lateral: ref %.3f, jogo %.3f" % (c["giro_lateral_ref"], c["giro_lateral_jogo"]))
    print("  erro médio de identidade: %.2f%%" % c["erro_medio_identidade_pct"])
    print("== %s ==" % ("PASSOU" if c["passou"] else "REPROVOU: " + ", ".join(c["reprovadas"]) if c["reprovadas"] else "REPROVOU"))


def main():
    ap = argparse.ArgumentParser(description="Ficha de medidas do rosto e comparação com o jogo.")
    ap.add_argument("--ficha", help="imagem de referência para tirar a ficha")
    ap.add_argument("--comparar", help="ficha JSON da referência")
    ap.add_argument("--shot", help="foto do jogo no mesmo ângulo e lente da referência")
    ap.add_argument("--out", help="salva o resultado em JSON")
    ap.add_argument("--dip-cm", type=float, default=6.0, help="distância entre as pupilas em cm (âncora dos cm estimados)")
    ap.add_argument("--com-expressao", action="store_true", help="a expressão da referência foi repetida: as medidas de expressão contam")
    ap.add_argument("--com-cor", action="store_true", help="a foto foi feita na luz da referência (sala de lookdev): as cores contam")
    args = ap.parse_args()
    if not (args.ficha or (args.comparar and args.shot)):
        ap.error("use --ficha IMAGEM, ou --comparar FICHA.json --shot FOTO")

    detector = F.load_model()
    try:
        if args.ficha:
            result = ficha(detector, args.ficha, args.dip_cm)
            print_ficha(result)
            ok = True
        else:
            with open(args.comparar, encoding="utf-8") as fh:
                ref = json.load(fh)
            shot = ficha(detector, args.shot, ref.get("dip_cm_ancora", args.dip_cm))
            result = compare(ref, shot, args.com_expressao, args.com_cor)
            result["ficha_jogo"] = shot
            print_compare(result)
            ok = result["passou"]
    finally:
        detector.close()
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
