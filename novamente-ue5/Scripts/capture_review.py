"""
capture_review.py - fotos de revisão do Largo, sempre dos mesmos ângulos, para comparar rodada a rodada
com as referências (capa v1 a v3 e o render 3D do Luan criança) e com a rodada anterior.

Gera Saved/Review/<data-hora>/ com:
  editor_*.png   ângulos fixos do cenário (luz, materiais, chuva, cúpula, chão molhado)
  luta_*.png     a luta rodando de verdade (Play in Editor): abertura, descida, golpes, quedas
  desempenho.png a luta com "stat unit" e "stat gpu" na tela
  REVISAO.md     a lista do que conferir em cada foto (portões R1 a R8 do Docs/ROADMAP.md)

Precisa do editor com janela (renderiza de verdade), não do modo -run=pythonscript:
  UnrealEditor.exe "C:/caminho/Novamente.uproject" -ExecutePythonScript="C:/caminho/novamente-ue5/Scripts/capture_review.py"
ou, com o editor aberto: Tools > Execute Python Script...

Variáveis opcionais:
  NOV_MAP=/Game/.../L_Mutirao   outro mapa (padrão: o Largo)
  NOV_TIERS=4,1                 qualidades a fotografar (4 cinematográfica, 3 épica, 2 alta, 1 média, 0 baixa).
                                A 4 é a verdade visual, independente da potência do PC; a 1 prova que o estilo
                                se sustenta no médio.
  NOV_CAPTURE=editor|pie|all    (padrão all; a luta em Play só roda no Largo)
  NOV_QUIT=1                    fecha o editor no fim
  NOV_RES=2560x1440             resolução

Câmeras de revisão: toda CameraActor do mapa com uma tag começando em "Rev_" (Rev_01_Rua, Rev_05_Rosto_Frente...)
é fotografada com o enquadramento e a lente dela. Sem nenhuma no mapa, valem os ângulos fixos do Largo.
"""

import datetime
import glob
import os
import shutil

import unreal

LARGO = "/Game/Novamente/Maps/L_Largo"
MAP = os.environ.get("NOV_MAP", LARGO)
TIERS = [int(t) for t in os.environ.get("NOV_TIERS", "4,1").split(",") if t.strip()]
MODE = os.environ.get("NOV_CAPTURE", "all").lower()
RES = os.environ.get("NOV_RES", "1920x1080")
QUIT = os.environ.get("NOV_QUIT") == "1"

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

STAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), "Review", STAMP)
SHOTS_DIR = unreal.Paths.convert_relative_path_to_full(unreal.Paths.screen_shot_dir())

# Ângulos fixos (posição, ponto para onde olha). Luan começa em Y=+160, Igor em Y=-160, lona a 90 cm.
EDITOR_SHOTS = [
    ("editor_01_transmissao", (650, 0, 175), (0, 0, 160)),
    ("editor_02_rosto_luan", (70, 95, 243), (0, 160, 240)),
    ("editor_03_rosto_igor", (70, -95, 250), (0, -160, 248)),
    ("editor_04_largo_teatro", (2600, 1400, 420), (-5500, 0, 2200)),
    ("editor_05_cupula", (-1300, 1100, 650), (-5500, 0, 2200)),
    ("editor_06_chao_molhado", (-500, 1300, 35), (-2200, 0, 0)),
    ("editor_07_octogono_alto", (520, 520, 900), (0, 0, 90)),
]

CHECKLIST = """# Revisão {stamp}

Mapa: {map} · qualidades: {tiers} (4 = cinematográfica, 1 = média)

## Câmeras de revisão (Rev_*) e fidelidade
- Rode `python Scripts/fidelidade.py --pares Referencias/pares.json --dir <esta pasta>` para medir rosto, pele e clima
  contra as referências. Os números vão para fidelidade.json.
- O revisor-visual escreve o PARECER.md nesta pasta. Sem PARECER.md, a rodada não conta.
- O visual na qualidade 1 pode perder detalhe, mas não pode perder o estilo: mesma paleta, mesmo contraste,
  mesma leitura de material e silhueta.

Compare cada foto com as referências (capa v1 a v3, render 3D) e com a rodada anterior.
Marque OK ou descreva o problema com o arquivo e o que mudar.

## Cenário (R1, R2)
- editor_04 / editor_05: a fachada é rosa com frisos brancos? A cúpula lê como azulejo verde, amarelo e azul?
  Nada de Japão, templo, cerejeira, sol baixo. É noite de chuva em Manaus.
- editor_06: a pedra portuguesa em ondas pretas e brancas aparece? O chão está molhado, com reflexos dos postes laranja?
- editor_01: a neblina segura a luz dos refletores? O octógono tem contraste de capa (luz dura de cima, sombra funda)?

## Personagens (R3, R4)
- editor_02 / editor_03: pele com poros e brilho de suor (não argila), olhos com umidade, cabelo em fios.
  Luan: pardo claro, quase branco, 1,63 m, magro e cansado. Igor: mais alto, cabeça raspada, bravo.
- Proporção de lutador real (sem ombro de super-herói), mãos com bandagem, luvas de MMA.

## Luta (R5, R6)
- luta_*: a câmera fica de lado, com o teatro ao fundo? Os golpes conectam (sem mão atravessando o rosto)?
- As reações têm peso (hit-stop, cabeça vira, corpo cede)? A queda é física e o levantar é animado?
- A interface é legível sem cobrir a luta?

## Sombra e Leis (R7)
- Visão do Caos: imagem fria e lenta. Sombra: duotone na cor dela, garras nas bordas, olhos no céu.
- Realidade 2: preto e branco com grão.

## Desempenho (R8)
- desempenho.png: frame abaixo de 16,6 ms (60 fps) na máquina alvo? GPU e Game separados.
"""


def log(msg):
    unreal.log("[Novamente] " + msg)


def existing_shots():
    return set(glob.glob(os.path.join(SHOTS_DIR, "**", "*.png"), recursive=True))


class Runner(object):
    """Executa passos com espera entre eles, um por quadro do editor (o editor precisa renderizar)."""

    def __init__(self, steps):
        self.steps = steps
        self.index = 0
        self.timer = 0.0
        self.known = existing_shots()
        self.handle = unreal.register_slate_post_tick_callback(self.tick)

    def tick(self, delta):
        self.timer += delta
        if self.index >= len(self.steps):
            unreal.unregister_slate_post_tick_callback(self.handle)
            return
        wait, fn = self.steps[self.index]
        if self.timer >= wait:
            self.timer = 0.0
            self.index += 1
            try:
                fn()
            except Exception as e:
                unreal.log_error("[Novamente] passo %d falhou: %s" % (self.index, e))

    def collect(self, name):
        """Move a foto nova da pasta padrão para a pasta da revisão com o nome do ângulo."""
        now = existing_shots()
        fresh = sorted(now - self.known, key=os.path.getmtime)
        self.known = now
        if not fresh:
            unreal.log_warning("[Novamente] nenhuma foto nova para " + name)
            return
        shutil.move(fresh[-1], os.path.join(OUT, name + ".png"))
        log("foto: " + name)


def console(command, world=None):
    unreal.SystemLibrary.execute_console_command(world or ues.get_editor_world(), command)


def shot(world=None):
    console("HighResShot " + RES, world)


def review_cameras():
    """CameraActors do mapa com tag Rev_*, em ordem de tag."""
    found = []
    for actor in eas.get_all_level_actors():
        if not isinstance(actor, unreal.CameraActor):
            continue
        for tag in actor.get_editor_property("tags"):
            name = str(tag)
            if name.startswith("Rev_"):
                found.append((name, actor))
                break
    return sorted(found, key=lambda item: item[0])


def res_xy():
    w, h = RES.lower().split("x")
    return int(w), int(h)


def build_steps(runner_ref):
    steps = []

    if MODE in ("editor", "all"):
        cameras = review_cameras()
        for tier in TIERS:
            steps.append((0.3, lambda tier=tier: console("Scalability %d" % tier)))
            if cameras:
                for tag, cam in cameras:
                    def take(cam=cam, tag=tag, tier=tier):
                        w, h = res_xy()
                        unreal.AutomationLibrary.take_high_res_screenshot(w, h, "%s_q%d.png" % (tag, tier), cam)
                    steps.append((1.5, take))                  # tempo para Lumen e sombras assentarem
                    steps.append((2.0, lambda tag=tag, tier=tier: runner_ref[0].collect("%s_q%d" % (tag, tier))))
            elif MAP == LARGO:
                for name, pos, target in EDITOR_SHOTS:
                    def place(pos=pos, target=target):
                        location = unreal.Vector(*pos)
                        rotation = unreal.MathLibrary.find_look_at_rotation(location, unreal.Vector(*target))
                        ues.set_level_viewport_camera_info(location, rotation)
                    steps.append((0.5, place))
                    steps.append((1.5, lambda: shot()))
                    steps.append((1.5, lambda name=name, tier=tier: runner_ref[0].collect("%s_q%d" % (name, tier))))
            else:
                unreal.log_warning("[Novamente] nenhuma câmera Rev_* em %s: coloque CameraActors com tags Rev_01..." % MAP)
        steps.append((0.3, lambda: console("Scalability %d" % max(TIERS))))

    if MODE in ("pie", "all") and (MAP == LARGO or MODE == "pie"):
        def game_world():
            return ues.get_game_world()

        def game_mode():
            return unreal.GameplayStatics.get_game_mode(game_world())

        steps.append((0.5, lambda: les.editor_request_begin_play()))
        steps.append((5.0, lambda: shot(game_world())))
        steps.append((1.5, lambda: runner_ref[0].collect("luta_00_abertura")))
        steps.append((0.2, lambda: game_mode().start_fight()))
        steps.append((1.6, lambda: shot(game_world())))
        steps.append((1.5, lambda: runner_ref[0].collect("luta_01_descida")))
        # O Igor avança e bate num Luan parado: golpes, reações, quedas, ground and pound.
        for i in range(10):
            steps.append((0.5, lambda: shot(game_world())))
            steps.append((1.0, lambda i=i: runner_ref[0].collect("luta_%02d" % (i + 2))))
        steps.append((0.2, lambda: console("stat unit", game_world())))
        steps.append((0.1, lambda: console("stat gpu", game_world())))
        steps.append((2.0, lambda: shot(game_world())))
        steps.append((1.5, lambda: runner_ref[0].collect("desempenho")))
        steps.append((0.2, lambda: les.editor_request_end_play()))

    def finish():
        with open(os.path.join(OUT, "REVISAO.md"), "w", encoding="utf-8") as f:
            f.write(CHECKLIST.format(stamp=STAMP, map=MAP, tiers=", ".join(str(t) for t in TIERS)))
        log("revisão pronta em " + OUT)
        if QUIT:
            unreal.SystemLibrary.quit_editor()

    steps.append((1.0, finish))
    return steps


def main():
    os.makedirs(OUT, exist_ok=True)
    les.load_level(MAP)
    runner_ref = [None]
    runner_ref[0] = Runner(build_steps(runner_ref))
    log("capturando em " + OUT)


main()
