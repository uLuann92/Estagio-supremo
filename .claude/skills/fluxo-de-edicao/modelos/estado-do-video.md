# Modelo: estado do vídeo e o script de estado

Cada vídeo tem um arquivo de estado em `_CLAUDE/projeto.json`. É a memória do fluxo: sobrevive ao `/clear` e a qualquer conversa nova.

## Esqueleto (cresce a cada etapa)

```json
{
  "projeto": "2026-01-15_Nome",
  "perfil": "<nome do perfil>",
  "ferramentas": { "hyperframes": "<versão fixa deste vídeo>" },
  "etapas": {
    "iniciar": "concluido",
    "preparar": "concluido",
    "cortes": "aguardando_aprovacao",
    "motion_mapa": "pendente"
  },
  "midia": { "...": "arquivos, fps, proxies, sync, áudio principal" },
  "transcricao": { "...": "caminhos dos arquivos por câmera e dos silêncios" },
  "notas_edicao": [ { "id": "n01", "texto": "usa esse take", "etapa": "cortes", "interpretacao": "..." } ],
  "cortes": { "versao": 1, "segmentos": [ { "id": "s001", "video": "cam01", "inicio": 3.10, "fim": 15.62, "texto": "..." } ] },
  "marcadores": [ { "id": "m001", "video": "cam01", "tempo": 48.3, "tipo": "duvida_take", "texto": "..." } ],
  "motions": { "trechos": {}, "itens": [ { "id": "mo01", "status": "aprovado", "render": { "arquivo": "...", "versao": 1 } } ] },
  "camera": { "movimentos": [], "recortes": [] },
  "sfx": { "itens": [], "recortes": [] },
  "pendencias": [ { "id": "p01", "etapa": "motion_render", "texto": "mo05 mais lento" } ]
}
```

No clipe musical, os blocos `transcricao`, `notas_edicao`, `cortes`, `motions` e `camera` dão lugar a:

```json
{
  "musica": { "arquivo": "...", "fps": 23.976, "bpm": 140, "offset": 0.213, "leitura": "metade", "compassos": 96,
              "secoes": [ { "nome": "refrao1", "compasso_ini": 17, "compasso_fim": 24, "energia": 5 } ],
              "testes": { "clique": "ok em <data>", "karaoke": "ok em <data>" },
              "arquivos": { "batidas": "...", "letra_por_palavra": "...", "mapa": "..." } },
  "cenas": { "indice": "...", "total": 842, "herois": ["c0412", "c0388"] },
  "roteiro": { "itens": [ { "id": "rt017", "compasso": 17, "cena": "c0412", "apice_no_tempo": 1, "letra": "bloco_destaque", "fx": ["flash_forte", "punch"], "status": "aprovado" } ] },
  "montagem": { "versao": 1, "segmentos": [ { "id": "s001", "cena": "c0412", "inicio": 12.50, "fim": 14.21, "frame_seq": 0, "velocidade": 1.0 } ] },
  "letra": { "secoes": [ { "id": "lt03", "secao": "refrao1", "render": { "arquivo": "...", "versao": 2 } } ] },
  "efeitos": { "base": {}, "destaques": [ { "id": "fx07", "compasso": 33, "tempo": 1, "tipo": "congelamento", "forca": "forte" } ] },
  "segundo_olhar": [ { "id": "so03", "etapa": "roteiro", "uso": "parecer", "arquivo": "_CLAUDE/segundo-olhar/roteiro_refrao1_01.md", "resultado": "adotei 2 de 5; 1 divergência decidida por <nome>" } ]
}
```

- Tempos na música ficam em **compasso e tempo** (e em frames, calculados pela grade). Segundos soltos, só no tempo do arquivo de origem das cenas.
- O bloco `segundo_olhar` existe em qualquer tipo de vídeo, quando o Gemini está ligado.
- Status de etapa: `pendente`, `em_andamento`, `aguardando_aprovacao`, `aguardando_<pessoa>`, `concluido`, `nao_precisa`.
- Tempos de corte e marcadores ficam no **tempo do arquivo de origem** (não da sequência): sobrevivem a novas versões do corte.
- Ids estáveis (`s001`, `mo04`, `cam07`, `sfx12`): é por eles que a pessoa pede ajustes.

## O script de estado
Escreva cedo (na etapa de iniciar ou preparar) um script pequeno que lê e muda o estado sem abrir o arquivo inteiro:
- `status`: as etapas, o que foi feito por trecho, as pendências e os alertas. Um alerta aparece, por exemplo, quando o corte mudou depois do plano de animação.
- `<bloco>`: um resumo legível de um bloco, e `--json` para o bloco completo.
- `--item <id>`: um item inteiro.
- `--set <caminho> <valor>` e `--etapa <etapa>=<status>`.
- `--pendencia <etapa> "<texto>"` e `--resolver <id>`.

Ele economiza muito limite. Num vídeo longo, o estado inteiro tem dezenas de milhares de tokens.
