"""
preparar_referencias.py - corta a prancha 2x2 do render (frente, costas, perfil, três quartos) em quatro
imagens, com os nomes que o fidelidade.py e o revisor esperam em Referencias/.

Uso:
  python Scripts/preparar_referencias.py caminho/da/prancha_2x2.jpg [pasta_de_saida]

Gera: luan_crianca_frente.jpg, luan_crianca_costas.jpg, luan_crianca_perfil.jpg, luan_crianca_34.jpg
Coloque também em Referencias/, à mão: luan_crianca_close.jpg (o close do render) e capa_v1.jpg a capa_v3.jpg.
"""

import os
import sys

import cv2


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "Referencias"
    img = cv2.imread(src, cv2.IMREAD_COLOR)
    if img is None:
        sys.exit("Não consegui abrir: " + src)
    os.makedirs(out, exist_ok=True)
    h, w = img.shape[:2]
    names = [["luan_crianca_frente", "luan_crianca_costas"], ["luan_crianca_perfil", "luan_crianca_34"]]
    for row in range(2):
        for col in range(2):
            tile = img[row * h // 2:(row + 1) * h // 2, col * w // 2:(col + 1) * w // 2]
            path = os.path.join(out, names[row][col] + ".jpg")
            cv2.imwrite(path, tile, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print("gravado " + path)


if __name__ == "__main__":
    main()
