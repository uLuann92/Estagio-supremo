"""
medir_corpo.py - fita métrica para a malha do personagem, comparada com os corpos padrão.

Lê um ou mais .obj (corpo, cabeça), em pé em pose A, e mede como um alfaiate: altura, quantas cabeças,
entrepernas, largura de ombros e de quadril, e as voltas de pescoço, peito, cintura, quadril, coxa e panturrilha
(fita esticada: o contorno convexo da fatia). Compara com Scripts/corpos_padrao.json, na altura do personagem.

Uso:
  python Scripts/medir_corpo.py corpo.obj cabeca.obj --padrao garoto_13_14
  python Scripts/medir_corpo.py corpo.obj cabeca.obj --padrao masculino --variante forte --altura 163
  python Scripts/medir_corpo.py corpo.obj --padrao feminino --out Saved/Review/<data>/corpo_emma.json

Como tirar o .obj: exporte o corpo e a cabeça do MetaHuman em FBX (botão direito > Asset Actions > Export) e
converta no Blender (sem abrir janela):
  blender -b --python-expr "import bpy,sys; bpy.ops.wm.read_factory_settings(use_empty=True); \
[bpy.ops.import_scene.fbx(filepath=f) for f in sys.argv[sys.argv.index('--')+1:-1]]; \
bpy.ops.wm.obj_export(filepath=sys.argv[-1], export_materials=False)" -- corpo.fbx cabeca.fbx personagem.obj

Unidade (m, cm, mm) e eixo de cima são detectados sozinhos. Sem dependência além do numpy.
Saída: tabela, JSON e código 0 (dentro do padrão) ou 1 (fora).
"""

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STEP = 0.25  # cm entre fatias


def load_obj(paths):
    verts, faces = [], []
    for path in paths:
        base = len(verts)
        local = 0
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.split()
                    verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
                    local += 1
                elif line.startswith("f "):
                    idx = []
                    for tok in line.split()[1:]:
                        i = int(tok.split("/")[0])
                        idx.append(base + (i - 1 if i > 0 else local + i))
                    for k in range(1, len(idx) - 1):
                        faces.append([idx[0], idx[k], idx[k + 1]])
    if not verts or not faces:
        sys.exit("Nenhuma malha lida de: " + ", ".join(paths))
    return np.array(verts, float), np.array(faces, int)


def orient(v, up=None):
    """Devolve vértices em cm com colunas (largura, altura, profundidade) e o chão em zero."""
    ext = v.max(0) - v.min(0)
    up_axis = {"x": 0, "y": 1, "z": 2}[up] if up else int(np.argmax(ext))
    rest = [a for a in range(3) if a != up_axis]
    width_axis, depth_axis = (rest[0], rest[1]) if ext[rest[0]] >= ext[rest[1]] else (rest[1], rest[0])
    out = v[:, [width_axis, up_axis, depth_axis]].copy()
    h = out[:, 1].max() - out[:, 1].min()
    scale = 100.0 if h < 3 else (0.1 if h > 1000 else 1.0)
    out *= scale
    out[:, 1] -= out[:, 1].min()
    return out


def cross_section(v, f, h, ymin=None, ymax=None):
    """Segmentos (N, 2, 2) em (largura, profundidade) onde o plano de altura h corta a malha."""
    if ymin is None:
        y = v[f][:, :, 1]
        ymin, ymax = y.min(1), y.max(1)
    tri = f[(ymin < h) & (ymax > h)]
    if len(tri) == 0:
        return np.zeros((0, 2, 2))
    p = v[tri]                       # (T, 3, 3)
    pts, valid = [], []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        ya, yb = p[:, a, 1], p[:, b, 1]
        cross = (ya - h) * (yb - h) < 0
        t = np.where(cross, (h - ya) / np.where(cross, yb - ya, 1), 0)
        q = p[:, a] + (p[:, b] - p[:, a]) * t[:, None]
        pts.append(q[:, [0, 2]])
        valid.append(cross)
    pts, valid = np.stack(pts, 1), np.stack(valid, 1)       # (T, 3, 2), (T, 3)
    keep = valid.sum(1) >= 2
    pts, valid = pts[keep], valid[keep]
    order = np.argsort(~valid, axis=1, kind="stable")[:, :2]  # os dois lados cortados de cada triângulo
    return np.take_along_axis(pts, order[:, :, None], axis=1)


def components(segs, eps=0.5):
    """Agrupa segmentos que se tocam (mesmo com malhas separadas encostadas, como corpo e cabeça)."""
    n = len(segs)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    cells = {}
    for i, seg in enumerate(segs):
        for p in seg:
            key = (int(np.floor(p[0] / eps)), int(np.floor(p[1] / eps)))
            cells.setdefault(key, []).append(i)
    for (cx, cz), ids in cells.items():
        near = list(ids)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if dx or dz:
                    near += cells.get((cx + dx, cz + dz), [])
        r0 = find(near[0])
        for j in near[1:]:
            rj = find(j)
            if rj != r0:
                parent[rj] = r0
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return [segs[ids].reshape(-1, 2) for ids in groups.values()]


def hull_perimeter(points):
    pts = sorted(set(map(tuple, np.round(points, 4))))
    if len(pts) < 3:
        return 0.0

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = np.array(lower[:-1] + upper[:-1])
    return float(np.sum(np.linalg.norm(hull - np.roll(hull, -1, axis=0), axis=1)))


class Body(object):
    def __init__(self, v, f):
        self.v, self.f = v, f
        y = v[f][:, :, 1]
        self.ymin, self.ymax = y.min(1), y.max(1)
        self.H = float(v[:, 1].max())
        band = v[(v[:, 1] > 0.45 * self.H) & (v[:, 1] < 0.75 * self.H)]
        self.cx = float((v[:, 0].max() + v[:, 0].min()) / 2)
        self.cz = float(np.median(band[:, 2]))
        self.cache = {}

    def comps(self, h):
        key = round(h, 3)
        if key not in self.cache:
            self.cache[key] = components(cross_section(self.v, self.f, h, self.ymin, self.ymax))
        return self.cache[key]

    def central(self, h):
        best, best_d = None, 1e9
        for c in self.comps(h):
            x0, x1 = c[:, 0].min(), c[:, 0].max()
            z0, z1 = c[:, 1].min(), c[:, 1].max()
            if x0 <= self.cx <= x1 and z0 <= self.cz <= z1:
                return c
            d = abs((x0 + x1) / 2 - self.cx) + abs((z0 + z1) / 2 - self.cz)
            if d < best_d:
                best, best_d = c, d
        return best

    def contains_center(self, h):
        return any(c[:, 0].min() <= self.cx <= c[:, 0].max() for c in self.comps(h))

    def heights(self, a, b):
        return np.arange(a, b + 1e-9, STEP)

    def width(self, c):
        return float(c[:, 0].max() - c[:, 0].min()) if c is not None and len(c) else 0.0

    def crotch(self):
        for h in self.heights(0.40 * self.H, 0.58 * self.H)[::-1]:
            if not self.contains_center(h):
                return float(h + STEP)
        return None

    def front_sign(self):
        """+1 se a frente é profundidade positiva: o pé avança mais para a frente do que o calcanhar para trás."""
        ank = self.v[(self.v[:, 1] > 0.035 * self.H) & (self.v[:, 1] < 0.05 * self.H)]
        foot = self.v[self.v[:, 1] < 0.02 * self.H]
        if len(ank) == 0 or len(foot) == 0:
            return 1
        c = np.median(ank[:, 2])
        return 1 if (foot[:, 2].max() - c) >= (c - foot[:, 2].min()) else -1

    def chin(self):
        """Ponta do queixo: onde o perfil da frente mais recua, descendo do rosto para o pescoço."""
        s = self.front_sign()
        hs = self.heights(0.80 * self.H, 0.885 * self.H)
        prof = []
        for h in hs:
            c = self.central(h)
            prof.append(np.nan if c is None else float((c[:, 1] * s).max()))
        prof = np.array(prof)
        win = max(1, int(1.5 / STEP))
        best_h, best_drop = None, 0.0
        for i in range(len(hs) - win):
            if np.isnan(prof[i]) or np.isnan(prof[i + win]):
                continue
            drop = prof[i + win] - prof[i]   # subindo: pescoço -> queixo, a frente avança
            if drop > best_drop:
                best_drop, best_h = drop, hs[i + win]
        return (float(best_h), best_drop) if best_h is not None and best_drop > 1.5 else (None, best_drop)

    def extreme(self, a, b, fn, pick, guard_width=None):
        best_h, best_v = None, None
        for h in self.heights(a, b):
            c = self.central(h)
            if c is None:
                continue
            if guard_width and self.width(c) > guard_width:
                continue      # o braço encostou na fatia
            val = fn(c)
            if best_v is None or (val > best_v if pick == "max" else val < best_v):
                best_h, best_v = h, val
        return best_h, best_v

    def legs(self, h):
        cs = [c for c in self.comps(h) if abs(c[:, 0].mean() - self.cx) < 0.15 * self.H]
        return sorted(cs, key=lambda c: -hull_perimeter(c))[:2]


def measure(body):
    H = body.H
    out = {"altura": round(H, 1)}
    notes = []
    crotch = body.crotch()
    out["entrepernas"] = round(crotch, 1) if crotch else None
    chin_h, drop = body.chin()
    if chin_h:
        out["cabeca_altura"] = round(H - chin_h, 1)
        out["cabecas"] = round(H / (H - chin_h), 2)
    else:
        notes.append("queixo não achado no perfil (recuo de %.1f cm); confira a altura da cabeça à mão" % drop)

    chest_ref = body.central(0.70 * H)
    guard = body.width(chest_ref) * 1.25 if chest_ref is not None else None
    _, out["peito"] = body.extreme(0.69 * H, 0.74 * H, hull_perimeter, "max", guard)
    _, out["cintura"] = body.extreme(0.57 * H, 0.68 * H, hull_perimeter, "min", guard)
    hip_lo = (crotch or 0.46 * H) + 2.0
    hip_h, out["quadril"] = body.extreme(hip_lo, 0.57 * H, hull_perimeter, "max", guard)
    _, out["quadril_largura"] = body.extreme(hip_lo, 0.57 * H, body.width, "max", guard)
    neck_top = (chin_h - 1.0) if chin_h else 0.855 * H
    _, out["pescoco"] = body.extreme(0.83 * H, neck_top, hull_perimeter, "min")

    sh = body.central(0.815 * H)
    w = body.width(sh)
    if w > 0.35 * H:
        notes.append("pose em T ou braço alto: largura de ombros não medida (use pose A)")
        out["ombros_largura"] = None
    else:
        out["ombros_largura"] = round(w, 1)

    if crotch:
        thighs = [max((hull_perimeter(c) for c in body.legs(h)), default=0) for h in body.heights(crotch - 6, crotch - 1)]
        out["coxa"] = max(thighs) if thighs else None
    calves = [max((hull_perimeter(c) for c in body.legs(h)), default=0) for h in body.heights(0.17 * H, 0.27 * H)]
    out["panturrilha"] = max(calves) if calves else None
    for k in ("peito", "cintura", "quadril", "quadril_largura", "pescoco", "coxa", "panturrilha"):
        if out.get(k) is not None:
            out[k] = round(out[k], 1)
    return out, notes


def compare(meas, std_name, variant, height, data):
    std = data["corpos"][std_name]
    tol = data["tolerancia"]
    k = (height or meas["altura"]) / std["altura"]
    delta = data["variantes"].get(variant or "magro", {})
    rows, ok_all = [], True

    def add(name, target, got, kind, what):
        nonlocal ok_all
        if got is None:
            rows.append({"medida": name, "alvo": round(target, 1), "medido": None, "erro_pct": None, "passou": False, "o_que_e": what})
            ok_all = False
            return
        err = abs(got - target) / target
        ok = err <= tol[kind]
        ok_all &= ok
        rows.append({"medida": name, "alvo": round(target, 1), "medido": got, "erro_pct": round(err * 100, 1), "passou": ok, "o_que_e": what})

    if height:
        add("altura", height, meas["altura"], "altura", "altura total pedida")
    if meas.get("cabecas") is not None:
        err = abs(meas["cabecas"] - std["cabecas"])
        ok = err <= tol["cabecas"]
        ok_all &= ok
        rows.append({"medida": "cabecas", "alvo": std["cabecas"], "medido": meas["cabecas"], "erro_pct": None,
                     "diferenca": round(err, 2), "passou": ok, "o_que_e": "altura dividida pela altura da cabeça"})
    else:
        rows.append({"medida": "cabecas", "alvo": std["cabecas"], "medido": None, "passou": False, "o_que_e": "queixo não achado"})
        ok_all = False
    for name, spec in std["medidas"].items():
        if spec.get("manual") or spec.get("osso") or name not in meas:
            continue
        target = spec["cm"] * k * (1 + delta.get(name, 0.0))
        add(name, target, meas[name], spec["tipo"], spec["o_que_e"])
    return rows, ok_all


def main():
    ap = argparse.ArgumentParser(description="Fita métrica da malha do personagem contra os corpos padrão.")
    ap.add_argument("obj", nargs="+", help="um ou mais .obj (corpo, cabeça) do personagem em pose A")
    ap.add_argument("--padrao", default="garoto_13_14", help="garoto_13_14, feminino ou masculino")
    ap.add_argument("--variante", default="magro", help="magro, medio, forte ou acima_do_peso")
    ap.add_argument("--altura", type=float, help="altura pedida para este personagem em cm (padrão: a do corpo padrão)")
    ap.add_argument("--cima", choices=["x", "y", "z"], help="eixo de cima, se a detecção errar")
    ap.add_argument("--out", help="salva o resultado em JSON")
    args = ap.parse_args()

    with open(os.path.join(HERE, "corpos_padrao.json"), encoding="utf-8") as f:
        data = json.load(f)
    if args.padrao not in data["corpos"]:
        sys.exit("padrão desconhecido: %s (use %s)" % (args.padrao, ", ".join(data["corpos"])))
    std = data["corpos"][args.padrao]
    if args.variante not in std["variantes"]:
        sys.exit("a variante %s não existe para %s (use %s)" % (args.variante, args.padrao, ", ".join(std["variantes"])))

    v, f = load_obj(args.obj)
    body = Body(orient(v, args.cima), f)
    meas, notes = measure(body)
    height = args.altura or std["altura"]
    rows, ok = compare(meas, args.padrao, args.variante, height, data)

    print("\nFITA MÉTRICA · %s · padrão %s (%s), altura alvo %.1f cm" % (", ".join(os.path.basename(p) for p in args.obj),
                                                                       args.padrao, args.variante, height))
    for r in rows:
        got = "—" if r["medido"] is None else ("%.2f" % r["medido"] if r["medida"] == "cabecas" else "%.1f cm" % r["medido"])
        tgt = ("%.2f" % r["alvo"]) if r["medida"] == "cabecas" else "%.1f cm" % r["alvo"]
        err = "" if r.get("erro_pct") is None else "%5.1f%%" % r["erro_pct"]
        if r["medida"] == "cabecas" and r.get("diferenca") is not None:
            err = "±%.2f" % r["diferenca"]
        print("  %-18s alvo %-10s medido %-10s %7s  %s" % (r["medida"], tgt, got, err, "ok" if r["passou"] else "FORA"))
    for n in notes:
        print("  aviso: " + n)
    print("  (braço, punho, mão, pé e os segmentos entre articulações: Scripts/medir_esqueleto.py dentro da Unreal)")
    print("== %s ==" % ("DENTRO DO PADRÃO" if ok else "FORA DO PADRÃO"))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"padrao": args.padrao, "variante": args.variante, "altura_alvo": height, "medidas": meas,
                       "comparacao": rows, "avisos": notes, "passou": ok}, fh, ensure_ascii=False, indent=2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
