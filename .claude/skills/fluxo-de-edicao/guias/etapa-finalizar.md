# Etapa: finalizar (acabamento, exportação e conferência)

A última etapa de uma **edição completa**: o acabamento da imagem, o áudio final, o arquivo que sobe para a plataforma e uma conferência antes de publicar. Vale para qualquer tipo de vídeo. Quem revisa num programa de edição pode fazer parte dela à mão; nesse caso, a etapa cuida só do que a pessoa delegar e da conferência.

Entra depois de tudo travado (cortes ou montagem, animações ou letra, câmera ou efeitos, som).

## 1. Acabamento da imagem (o "look")
- **Igualar antes de estilizar.** Material de fontes diferentes (episódios, jogos, câmeras) chega com contraste, saturação e nitidez diferentes. Primeiro aproxime as cenas entre si (um script mede brilho e saturação por cena e aponta as que destoam); só depois aplique o estilo.
- **O estilo é um só, por cima de tudo**, e vem do perfil (`identidade.md`): curva de contraste, cor dominante, grão, vinheta, brilho nas luzes, barras. Pode variar por seção (mais frio no verso, mais quente no refrão) se o roteiro pedir.
- **O que fica por cima e o que fica por baixo do texto:** a cor e o contraste, por baixo (a letra e as animações já têm as cores da identidade); grão e vinheta, por cima de tudo, para colar as camadas.
- **Uma vez só.** Efeito de lente, grão e nitidez aplicados no render das animações e de novo aqui somam em dobro (`oficio-motion.md` §10).
- Com programa de edição, o look pode ir como uma camada de ajuste que a pessoa liga, ou como um arquivo de cor (LUT). Teste curto primeiro.

## 2. Áudio final
- **Clipe musical:** a música é a master. Não comprimir, não equalizar, não normalizar: ela já foi masterizada. Só os efeitos sonoros são ajustados em volta dela. Confira o **pico real** depois de somar os efeitos (música masterizada não tem folga; um impacto por cima pode estourar).
- **Vídeo falado:** a mixagem fina é da pessoa. Se ela delegar: voz no alvo, música de fundo abaixando sob a voz, efeitos nos níveis do perfil.
- **Volume para a plataforma:** as plataformas igualam o volume percebido (em geral, só abaixando o que passa do alvo). Pesquise o alvo atual da plataforma dela e meça o arquivo final (loudness integrada e pico real). Anote os números no resumo.

## 3. Exportação
- **Um render de conferência primeiro** (resolução baixa, rápido). O final, na resolução cheia, só depois da conferência.
- Formato, codec, taxa de bits e áudio conforme a recomendação **atual** da plataforma (pesquise). Taxa de quadros igual à do projeto.
- Versão no nome (`<projeto>_final_v01`). Nunca sobrescrever.
- Render em segundo plano.

## 4. Conferência (script + olhar)
Um script confere o arquivo final e recusa o que não bater:
- duração igual à da sequência (e à da música, no clipe);
- **sincronia no começo e no fim:** o mesmo evento (uma batida forte, uma palavra) medido nos dois extremos. Diferença crescente é erro de taxa de quadros;
- quadros pretos ou congelados fora do planejado;
- marcadores de "ASSET FALTANDO" que sobraram na imagem;
- flashes por segundo dentro do limite (`etapa-efeitos.md` §4);
- loudness e pico real;
- no clipe: todo texto de tela igual à letra aprovada.

Depois, o **olhar**: 8–12 quadros espalhados (texto dentro da área segura, nada cortado, cor coerente) e o primeiro e o último segundos.

**Segundo olhar:** é o melhor momento para uma crítica de espectador. O Gemini assiste ao vídeo inteiro (proxy) e responde: os 5 momentos mais fracos, onde a atenção cai, algum erro visível. Trechos que ele apontar são reconferidos com fps alto antes de virar correção.

## 5. Extras (só o que a pessoa pediu na entrevista)
- **Legenda `.srt`:** sai pronta da transcrição ou da letra alinhada, por linha.
- **Quadros para a capa:** 6–10 quadros fortes, sem texto, na resolução cheia.
- **Versão vertical curta** (um refrão, o gancho): recorte seguindo o assunto, letra reposicionada para a área segura do formato. É quase uma etapa à parte: combine antes.
- **Créditos:** a lista para a descrição (instrumental, fontes, sons e ícones com licença que pede crédito).
- **Capítulos:** os tempos das seções.

## 6. Revisão e fecho
- A pessoa assiste ao render de conferência e pede por tempo. O Claude converte para a etapa dona do problema ("a letra em 1:12" é da etapa de letra) e **avisa** que a correção é lá; coisa pequena de acabamento resolve aqui.
- Aprovado: render final, conferência de novo, resumo com os números medidos e o caminho do arquivo.
- Lembre o caderno de aprendizados: o fim do vídeo é a melhor hora de aplicar o que foi anotado.
