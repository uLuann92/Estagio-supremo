Você é um produtor musical e editor de clipes. Ouça esta música inteira (rap/R&B em português, ~6 min 21 s). A letra escrita está anexada.

Responda SÓ com um JSON com estas chaves:
- "bpm_estimado": número, e "bpm_alternativo" (metade ou dobro, se fizer sentido)
- "tom_e_clima": uma frase
- "secoes": lista em ordem, cada item {"nome" (use os nomes da letra: intro, pre_hook_1, hook_1, verso_1, pre_hook_2, hook_2, verso_2, ponte, quebra_1, verso_3, quebra_2, hook_final, outro; acrescente "instrumental" onde houver trecho sem voz), "inicio" e "fim" em segundos com uma casa decimal, "energia" de 1 a 5, "descricao" em uma frase: o que a batida e a voz fazem}
- "acentos": lista dos 12 momentos mais fortes da música {"tempo" em segundos, "o_que" (drop, pausa, virada, grito, entrada de 808…)}
- "diferencas_da_letra": lista de trechos em que o que é cantado difere da letra escrita (linha omitida, repetida, palavra trocada), com o tempo aproximado
- "vozes": quantas vozes cantam e como se alternam

Tempos aproximados são aceitáveis, mas não invente seções que você não ouviu. Se não tiver certeza de um limite, diga em "descricao".
