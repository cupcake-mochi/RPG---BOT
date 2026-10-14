# Perguntas do R51 (14/10/2026)

`r51.json`: 17 perguntas sobre o que mudou do R44 ao R51 (Morrendo, Sequelas, Recomposição, Segundo Fôlego, Origens novas, Legado de história, Sem Técnica, Restrição Celestial, Ataque sem Prenúncio, Olho adicional do Híbrido, ofício do Corpo Amaldiçoado). Mesmo formato das baterias de `2026-10-13/bateria/`. Escritas depois de ler os blocos, então não são cegas.

Rodar, de dentro de "Closure Lab/Closure":

    python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
    node avaliacao-perguntas/2026-10-13/bateria/montar.js /tmp/pagina.html avaliacao-perguntas/2026-10-14-r51/r51.json /tmp/saida.json kal 14
    python3 avaliacao-perguntas/2026-10-13/bateria/avaliar2.py avaliacao-perguntas/2026-10-14-r51/r51.json /tmp/saida.json

| Página | r51 | bateria | holdout 1 a 6 |
| ------ | --- | ------- | ------------- |
| livro R44, busca v8 | 15/17 | 59/59 | 27, 35, 35, 27, 38, 37 |
| livro R51, busca v8 | 15/17 | 58/59 | 26, 34, 32, 27, 37, 37 |
| livro R51, busca v8 com os três ajustes de 14/10 | 16/17 | 58/59 | 27, 34, 32, 27, 38, 37 |

Os três ajustes (`ferramentas/pagina_teste/modelo.html`): "recomposição" tem raiz própria e não se mistura com "recompensa"; "0 de vida", "0 pv" e "0 hp" viram "zero"; "feto" procura "híbrido".

Ainda erra:
- r06 ("quantas rodadas eu tenho pra ser socorrido se já tenho uma sequela?"): "socorrido" puxa a Trilha Socorrista do Guia, já no R44.
- t12 e t13 (holdout3) perguntam do Legado que dava benefício; no R51 ele não dá mais, e o gabarito ficou velho.
- cam11, n32 e t15: o bloco certo ficou em segundo ou terceiro por décimos, efeito do livro maior.
