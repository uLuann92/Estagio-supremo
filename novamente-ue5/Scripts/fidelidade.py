"""
fidelidade.py - mede o quanto uma foto do jogo bate com a referência do NOVAMENTE.

Não é opinião: marca 478 pontos no rosto (MediaPipe) nas duas imagens e compara as proporções
(olhos, nariz, boca, maçãs, mandíbula, altura do rosto), o tom de pele das bochechas (Delta E 2000)
e o clima da imagem inteira (luz média, contraste, saturação, calor, sombras e altas luzes).

Uso (no PC, dentro do projeto):
  pip install mediapipe opencv-python numpy
  python Scripts/fidelidade.py --ref Referencias/luan_crianca_frente.jpg --shot Saved/Review/<data>/rev05_rosto_frente.png
  python Scripts/fidelidade.py --ref ... --shot ... --out Saved/Review/<data>/fidelidade.json
  python Scripts/fidelidade.py --pares Referencias/pares.json --dir Saved/Review/<data>     (a rodada inteira)

A foto do jogo precisa estar no MESMO ângulo e enquadramento da referência (câmera de revisão do rosto).
O tom de pele só vale quando a luz também é a mesma: use a cena de lookdev que recria o render.

Saída: tabela no terminal, JSON opcional e código de saída 0 (passou) ou 1 (reprovou).
"""

import argparse
import glob
import json
import math
import os
import sys
import urllib.request

import cv2
import numpy as np

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modelos", "face_landmarker.task")

# Tolerâncias (proporções em fração da distância entre os cantos externos dos olhos).
FACE_MEAN_MAX = 0.03      # erro médio até 3%
FACE_SINGLE_MAX = 0.07    # nenhuma medida acima de 7%
SKIN_DELTA_E_MAX = 5.0    # tom de pele (Delta E 2000), só com a luz da referência
STYLE_L_MAX = 8.0         # luz média (L* de 0 a 100)
STYLE_CONTRAST_MAX = 0.15 # contraste relativo
STYLE_WARMTH_MAX = 4.0    # calor (b* médio)

# Pontos do MediaPipe Face Mesh.
P = dict(
    eye_r_out=33, eye_r_in=133, eye_r_up=159, eye_r_dn=145,
    eye_l_in=362, eye_l_out=263, eye_l_up=386, eye_l_dn=374,
    brow_r=105, brow_l=334, nasion=168, subnasale=2, nose_r=129, nose_l=358,
    mouth_r=61, mouth_l=291, lip_top=0, lip_bottom=17, chin=152, forehead=10,
    cheek_r=234, cheek_l=454, jaw_r=172, jaw_l=397, nose_tip=1,
)
# Medidas que mudam com a expressão (boca aberta, olho arregalado): aparecem, mas não reprovam.
EXPRESSION = {"abertura_olhos", "altura_labios", "boca_ao_queixo"}
CHEEK_R = [117, 118, 101, 36, 205, 187, 123]
CHEEK_L = [346, 347, 330, 266, 425, 411, 352]


def load_model():
    if not os.path.exists(MODEL_PATH):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        print("Baixando o modelo de rosto do MediaPipe (uma vez só)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    from mediapipe.tasks.python import BaseOptions
    from mediapipe.tasks.python import vision
    options = vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=MODEL_PATH), num_faces=1)
    return vision.FaceLandmarker.create_from_options(options)


def read_image(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        sys.exit("Não consegui abrir a imagem: %s" % path)
    return img


def landmarks(detector, bgr):
    import mediapipe as mp
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    result = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if not result.face_landmarks:
        return None
    h, w = bgr.shape[:2]
    return np.array([[p.x * w, p.y * h] for p in result.face_landmarks[0]], dtype=np.float64)


def face_metrics(pts):
    d = lambda a, b: float(np.linalg.norm(pts[P[a]] - pts[P[b]]))
    base = d("eye_r_out", "eye_l_out")
    m = {
        "largura_olhos": (d("eye_r_out", "eye_r_in") + d("eye_l_in", "eye_l_out")) / 2,
        "entre_olhos": d("eye_r_in", "eye_l_in"),
        "largura_nariz": d("nose_r", "nose_l"),
        "comprimento_nariz": d("nasion", "subnasale"),
        "largura_boca": d("mouth_r", "mouth_l"),
        "largura_macas": d("cheek_r", "cheek_l"),
        "largura_mandibula": d("jaw_r", "jaw_l"),
        "altura_rosto": d("forehead", "chin"),
        "nariz_ao_queixo": d("subnasale", "chin"),
        "sobrancelha_ao_olho": (d("brow_r", "eye_r_up") + d("brow_l", "eye_l_up")) / 2,
        "abertura_olhos": (d("eye_r_up", "eye_r_dn") + d("eye_l_up", "eye_l_dn")) / 2,
        "altura_labios": d("lip_top", "lip_bottom"),
        "boca_ao_queixo": d("lip_bottom", "chin"),
    }
    ratios = {k: v / base for k, v in m.items()}
    # Giro da cabeça: onde a ponta do nariz cai entre os dois olhos (0 = de frente).
    mid = (pts[P["eye_r_out"]] + pts[P["eye_l_out"]]) / 2
    yaw = float((pts[P["nose_tip"]][0] - mid[0]) / base)
    return ratios, yaw


def to_lab(bgr):
    lab = cv2.cvtColor(bgr.astype(np.float32) / 255.0, cv2.COLOR_BGR2LAB)
    return lab  # L 0..100, a/b em torno de 0


def delta_e_2000(lab1, lab2):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cm = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dh = h2p - h1p
    if C1p * C2p == 0:
        dh = 0
    elif dh > 180:
        dh -= 360
    elif dh < -180:
        dh += 360
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lm, Cmp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hm = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hm = (h1p + h2p) / 2
    else:
        hm = (h1p + h2p + 360) / 2 if (h1p + h2p) < 360 else (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm))
         + 0.32 * math.cos(math.radians(3 * hm + 6)) - 0.20 * math.cos(math.radians(4 * hm - 63)))
    dtheta = 30 * math.exp(-(((hm - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cmp ** 7 / (Cmp ** 7 + 25 ** 7))
    Sl = 1 + (0.015 * (Lm - 50) ** 2) / math.sqrt(20 + (Lm - 50) ** 2)
    Sc = 1 + 0.045 * Cmp
    Sh = 1 + 0.015 * Cmp * T
    Rt = -math.sin(math.radians(2 * dtheta)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))


def skin_lab(bgr, pts):
    mask = np.zeros(bgr.shape[:2], np.uint8)
    for poly in (CHEEK_R, CHEEK_L):
        cv2.fillPoly(mask, [pts[poly].astype(np.int32)], 255)
    lab = to_lab(bgr)
    sel = lab[mask > 0]
    return [float(x) for x in np.median(sel, axis=0)] if len(sel) else None


def style_stats(bgr):
    lab = to_lab(bgr)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    return {
        "luz_media": float(L.mean()),
        "contraste": float(L.std()),
        "saturacao": float(np.hypot(a, b).mean()),
        "calor_b": float(b.mean()),
        "sombras_pct": float((L < 15).mean() * 100),
        "altas_luzes_pct": float((L > 90).mean() * 100),
    }


def compare(detector, ref_path, shot_path, want_face=True, judge_skin=True, style_scale=1.0):
    """Compara uma foto do jogo com uma referência. Devolve o relatório (dict)."""
    ref, shot = read_image(ref_path), read_image(shot_path)
    report = {"ref": ref_path, "shot": shot_path, "passou": True, "motivos": []}

    if want_face:
        pr, ps = landmarks(detector, ref), landmarks(detector, shot)
        if pr is None or ps is None:
            report["rosto"] = None
            which = "referência" if pr is None else "foto do jogo"
            report["motivos"].append("nenhum rosto encontrado na %s" % which)
            report["passou"] = False
        else:
            rr, yaw_r = face_metrics(pr)
            rs, yaw_s = face_metrics(ps)
            rows = []
            judged = []
            for k in rr:
                err = abs(rs[k] - rr[k]) / max(rr[k], 1e-6)
                rows.append({"medida": k, "ref": round(rr[k], 4), "jogo": round(rs[k], 4), "erro_pct": round(err * 100, 2),
                             "conta": k not in EXPRESSION})
                if k not in EXPRESSION:
                    judged.append(err)
            mean_err, max_err = float(np.mean(judged)), float(np.max(judged))
            report["rosto"] = {"medidas": rows, "erro_medio_pct": round(mean_err * 100, 2), "erro_max_pct": round(max_err * 100, 2),
                               "giro_ref": round(yaw_r, 3), "giro_jogo": round(yaw_s, 3)}
            if abs(yaw_r - yaw_s) > 0.05:
                report["motivos"].append("ângulo diferente da referência (giro %.3f contra %.3f): refaça a foto no mesmo ângulo" % (yaw_s, yaw_r))
                report["passou"] = False
            if mean_err > FACE_MEAN_MAX:
                report["motivos"].append("proporções do rosto: erro médio %.1f%% (máximo %.0f%%)" % (mean_err * 100, FACE_MEAN_MAX * 100))
                report["passou"] = False
            if max_err > FACE_SINGLE_MAX:
                worst = max((r for r in rows if r["conta"]), key=lambda r: r["erro_pct"])
                report["motivos"].append("%s errado em %.1f%% (máximo %.0f%%)" % (worst["medida"], worst["erro_pct"], FACE_SINGLE_MAX * 100))
                report["passou"] = False

            sr, ss = skin_lab(ref, pr), skin_lab(shot, ps)
            if sr and ss:
                de = delta_e_2000(sr, ss)
                report["pele"] = {"lab_ref": [round(x, 2) for x in sr], "lab_jogo": [round(x, 2) for x in ss], "delta_e_2000": round(de, 2)}
                if de > SKIN_DELTA_E_MAX and judge_skin:
                    report["motivos"].append("tom de pele: Delta E %.1f (máximo %.0f)" % (de, SKIN_DELTA_E_MAX))
                    report["passou"] = False

    sr, ss = style_stats(ref), style_stats(shot)
    report["estilo"] = {"ref": {k: round(v, 2) for k, v in sr.items()}, "jogo": {k: round(v, 2) for k, v in ss.items()}}
    if abs(ss["luz_media"] - sr["luz_media"]) > STYLE_L_MAX * style_scale:
        report["motivos"].append("luz média %.1f contra %.1f da referência" % (ss["luz_media"], sr["luz_media"]))
        report["passou"] = False
    if abs(ss["contraste"] - sr["contraste"]) / max(sr["contraste"], 1e-6) > STYLE_CONTRAST_MAX * style_scale:
        report["motivos"].append("contraste %.1f contra %.1f da referência" % (ss["contraste"], sr["contraste"]))
        report["passou"] = False
    if abs(ss["calor_b"] - sr["calor_b"]) > STYLE_WARMTH_MAX * style_scale:
        report["motivos"].append("calor da imagem (b*) %.1f contra %.1f" % (ss["calor_b"], sr["calor_b"]))
        report["passou"] = False
    return report


def print_report(report):
    ss, sr = report["estilo"]["jogo"], report["estilo"]["ref"]
    print("\nFIDELIDADE · %s  x  %s" % (os.path.basename(report["shot"]), os.path.basename(report["ref"])))
    if report.get("rosto"):
        print("\n  Rosto (fração da distância entre os olhos)")
        for r in report["rosto"]["medidas"]:
            flag = "" if r["conta"] else "  (expressão, não conta)"
            print("   %-20s ref %.4f  jogo %.4f  erro %5.1f%%%s" % (r["medida"], r["ref"], r["jogo"], r["erro_pct"], flag))
        print("   erro médio %.1f%% · pior %.1f%%" % (report["rosto"]["erro_medio_pct"], report["rosto"]["erro_max_pct"]))
    if report.get("pele"):
        print("  Pele: Delta E 2000 = %.1f" % report["pele"]["delta_e_2000"])
    print("  Estilo: " + ", ".join("%s %.1f/%.1f" % (k, ss[k], sr[k]) for k in sr))
    print("  %s" % ("PASSOU" if report["passou"] else "REPROVOU"))
    for m in report["motivos"]:
        print("   - " + m)


def run_batch(detector, pairs_path, review_dir):
    """
    pares.json: {"Rev_05_Rosto_Frente": {"ref": "luan_crianca_frente.jpg"},
                 "Rev_01_Rua": {"ref": "capa_v3.jpg", "rosto": false}}
    Procura <dir>/<câmera>_q<qualidade>.png. Na qualidade mais alta tudo conta; nas outras o estilo tem
    50% mais de folga e o tom de pele não reprova (a luz simplificada muda a pele, a geometria não).
    """
    with open(pairs_path, encoding="utf-8") as f:
        pairs = json.load(f)
    ref_dir = os.path.dirname(os.path.abspath(pairs_path))
    reports = []
    for cam, cfg in pairs.items():
        if not os.path.isfile(os.path.join(ref_dir, cfg["ref"])):
            reports.append({"ref": cfg["ref"], "shot": cam, "passou": False, "estilo": {"ref": {}, "jogo": {}},
                            "motivos": ["referência %s não está em Referencias/ (o autor precisa colocar)" % cfg["ref"]]})
            continue
        shots = sorted(glob.glob(os.path.join(review_dir, cam + "_q*.png")))
        if not shots:
            reports.append({"ref": cfg["ref"], "shot": cam, "passou": False, "motivos": ["foto da câmera %s não encontrada" % cam],
                            "estilo": {"ref": {}, "jogo": {}}})
            continue
        top = max(int(os.path.splitext(x)[0].rsplit("_q", 1)[1]) for x in shots)
        for shot in shots:
            tier = int(os.path.splitext(shot)[0].rsplit("_q", 1)[1])
            r = compare(detector, os.path.join(ref_dir, cfg["ref"]), shot, want_face=cfg.get("rosto", True),
                        judge_skin=cfg.get("pele", True) and tier == top, style_scale=1.0 if tier == top else 1.5)
            r["camera"], r["qualidade"] = cam, tier
            reports.append(r)
    return reports


def main():
    ap = argparse.ArgumentParser(description="Compara fotos do jogo com as referências do NOVAMENTE.")
    ap.add_argument("--ref", help="imagem de referência (render, capa)")
    ap.add_argument("--shot", help="foto do jogo no mesmo ângulo")
    ap.add_argument("--pares", help="lote: Referencias/pares.json (câmera -> referência)")
    ap.add_argument("--dir", help="lote: pasta da rodada em Saved/Review/<data-hora>")
    ap.add_argument("--out", help="salva o resultado em JSON (no lote, padrão <dir>/fidelidade.json)")
    ap.add_argument("--sem-pele", action="store_true", help="não reprova pelo tom de pele (luz diferente da referência)")
    args = ap.parse_args()
    if not ((args.ref and args.shot) or (args.pares and args.dir)):
        ap.error("use --ref e --shot, ou --pares e --dir")

    detector = load_model()
    try:
        if args.pares:
            reports = run_batch(detector, args.pares, args.dir)
        else:
            reports = [compare(detector, args.ref, args.shot, judge_skin=not args.sem_pele)]
    finally:
        detector.close()

    for r in reports:
        if r.get("estilo", {}).get("ref"):
            print_report(r)
        else:
            print("\n%s: REPROVOU\n   - %s" % (r["shot"], "; ".join(r["motivos"])))
    passed = all(r["passou"] for r in reports)
    print("\n== %s: %d de %d fotos dentro da referência ==" % ("PASSOU" if passed else "REPROVOU", sum(r["passou"] for r in reports), len(reports)))

    out = args.out or (os.path.join(args.dir, "fidelidade.json") if args.dir else None)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"passou": passed, "fotos": reports}, f, ensure_ascii=False, indent=2)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
