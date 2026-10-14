# Polimento de perguntas do sistema (13/10/2026)

Bateria de perguntas variadas sobre o Ciclo Maldito contra a página de teste (Closure v0.23,
Kal'tsit v0.18, lorebook v1.2, livro R44 / sistema v0.359), conferindo cada resposta com o
`livro.jsonl` e, por amostra, com o PDF R44 (as regras conferidas batem com o PDF).

**Modelo:** Claude Haiku rodando como subagente (a cota grátis do Gemini estava esgotada). Cada
subagente recebeu o prompt de sistema e um lote de situações montadas pelo próprio JS da página.
Limite do método: no primeiro lote (11 a 16 situações por arquivo) houve vazamento entre
situações; `pro01`, `reg10` na Kal'tsit e `cam15`, `dig01`, `seg02` na Closure responderam certo
sem ter o trecho no contexto, porque o trecho estava em outra situação do mesmo lote. Na rodada
da busca nova usei 3 por lote e a instrução de não usar trecho de outra situação. Antes de
fechar, vale repetir as perguntas no Gemini (site) quando a cota voltar.

## Resultado em uma linha

Quase todo erro vem da **busca do livro**, não do prompt nem do modelo: quando o trecho certo
chega, o Haiku respondeu certo em todas as perguntas conferidas (números, custos, CDs, tabelas).
Quando não chega, ele diz que não achou (comportamento da v0.18 funcionando) ou, pior, responde
com o trecho errado que veio.

| Busca | Bateria (59 com trecho esperado) | Perguntas novas, escritas depois (27) | Livro puxado em papo comum (8) |
| ----- | ------------------------------- | ------------------------------------- | ------------------------------ |
| Atual (v0.23 / v0.18) | 38 | 20 | 0 |
| Busca v2 | 52 | 22 | 0 |
| Busca v2 + lorebook proposto | 57 | 22 | 0 |

A bateria foi usada pra desenhar a busca nova, então o número honesto de generalização é o das
perguntas novas: 20 → 22, sem nenhum falso positivo em conversa comum.

## Por que a busca atual erra (com exemplo)

1. **Nota mínima 6 corta pergunta de uma palavra só.** "o que posso fazer no meu turno?",
   "como faço uma ficha?", "como eu subo de nível?" ficam com uma palavra útil cada e não chegam a 6.
2. **Seguimento não herda o assunto.** O lorebook olha as últimas mensagens, mas a busca do livro
   só olha a mensagem atual. "e no nível 7?", "e quanto custa?", "e fora de lugar propício?"
   ficam sem trecho. Em `seg03` o Haiku ainda respondeu sobre o assunto errado (Analista em vez de
   Socorrista) misturando com o histórico.
3. **Título de seção não pesa.** "Olhos Em Mim funciona como?" nem passa o filtro de "pergunta
   de regra"; "o que acontece quando minha vida chega a zero?" perde "Vida a zero" pra página do
   Bastião; "o crítico dobra o bônus?" traz Aparar e Golpe Cirúrgico antes de "Dano e crítico", e
   a resposta saiu misturada com Golpe Cirúrgico.
4. **Âncora genérica do lorebook ocupa as vagas.** "Abrir Caminho custa quanto PE?" aciona os
   termos Caminho e PE; as duas âncoras (`ab--ab-caminho`, `rotas--rotas`) enchem as 2 vagas e a
   página de Abrir Caminho não entra. Resposta: "não achei Abrir Caminho".
5. **Sem tolerância a erro de digitação nem a conjugação.** "qias as habilidads do evocadr no
   nv 2" e "como estabilizo um aliado caído?" (o livro diz "estabilizar") não acham nada.
6. **Filtro de "pergunta de regra" estreito.** "posso me esconder no meio do combate?" e
   "posso jogar de restrição celestial?" não passam.
7. **Pergunta de intenção não tem âncora.** A entrada "Criar um personagem" do lorebook é a única
   do grupo sistema sem âncora; "sou novo, por onde começo?" e "me explica o sistema" ficam sem
   trecho. "o que eu ganho no nível 5?" não acha a tabela de progressão.
8. **Número de nível é descartado** (`tok` só pega palavras com 3+ caracteres), então "nível 7"
   vira só "nível". Para Caminho isso é compensado pela tabela de progressão; o bônus atual só
   reconhece a tabela do Guia, porque procura "progressao" no nome da âncora.

## Proposta

Arquivos em `proposta/`. Nada foi editado nos arquivos da thread da personalidade.

- **`busca_v2.js`**: substitui o bloco `// ---------- livro: ...` do `modelo.html` até
  `// ---------- estado da conversa`, e a chamada passa a mandar a última mensagem do usuário:
  `blocosLivro(msg, a.termos, turnos.filter(t => t.de === "user").slice(-1).map(t => t.texto).join(" "))`.
  O `aplicar.py` faz as duas trocas. O que muda:
  - raiz de 6 letras pra palavra longa ("estabilizo" acha "estabilizar", "evocadr" acha "evocador");
  - erro de uma letra no meio da palavra é corrigido pela palavra do livro mais comum ("funsiona");
  - sinônimo de mesa pequeno (caindo/cair → queda, voar → voo, upar → nível, shikigami → invocação,
    desmaiou → inconsciente);
  - título de seção com 2+ palavras escrito na pergunta vale +10 ("Olhos Em Mim", "Vida a zero");
    palavra da pergunta no título da seção vale +3;
  - palavra rara que é título de seção ("latente", "exaustão") também abre a busca;
  - mensagem curta ou que começa com "e ..." herda as palavras da anterior (peso 0,5), mas só se
    a anterior era pergunta de regra ("boa tarde" seguido de "e aí, tudo certo?" não puxa livro);
  - a tabela de progressão de qualquer Caminho ou Trilha ganha o bônus de nível, não só a do Guia;
  - até 3 blocos: o melhor da busca vem antes da âncora genérica do lorebook; o segundo da busca só
    entra se chegar a 60% do primeiro. Contexto médio sobe de 4,5 mil pra 5,2 mil caracteres.
- **`lorebook_proposta.json`** (aplicar no `gerar_lorebook_kaltsit.py`):
  - "Criar um personagem" ganha âncora `ab--ab-criacao` e chaves ("faço uma ficha", "sou novo",
    "nunca joguei", "começar a jogar"...);
  - entradas novas "Subir de nível" (`progressao--prog-inicio`), "O que ganho por nível"
    (`progressao--prog-tabela-inicial`) e "O sistema" (`ab--ab-apresentacao`);
  - "Oripatia em mesa" ganha "personagem é infectado", "infectado na ficha"... (hoje "meu personagem
    é infectado, isso muda algo na ficha?" não aciona a entrada certa);
  - "Classe" passa a dizer que quem pergunta a "classe" do personagem quase sempre quer dizer
    Caminho. Hoje "qual a classe mais forte?" foi respondida nas duas personagens como Classe de
    feitiço ("a maior é a Classe 7, com 21 pontos"). As duas últimas não foram testadas com modelo.

O site do Render monta a página com o mesmo `montar_pagina.py`, então a mudança chega lá quando a
thread do site portar a versão nova.

## Respostas com a busca nova (Haiku, conferidas no livro)

Todas certas e com o número do livro:

- "quanto de dano eu tomo caindo de 10 metros?" → 3d6 de Concussão, 1d6 por 3 m completos.
- "como estabilizo um aliado caído?" → Ação Padrão, Medicina CD 14, alvo Inconsciente e Morrendo.
- "posso me esconder no meio do combate?" → Furtividade contra CD 10 + Percepção, precisa de cobertura.
- "o que eu ganho no nível 5?" → linha da tabela (Maestria 1, 4 espaços, Classe máxima 2, 3 de Classe 0), não é marco.
- "como distribuo os atributos?" → 9 pontos, nenhum acima de 3, 0 permitido.
- "Abrir Caminho custa quanto PE?" / "e quanto custa?" → 1 PE, Ação Bônus, uma vez por turno.
- "e o socorrista?" → Cuidado Preparado, +2 PE, 1d8 + Inteligência ou Essência.
- "e no 15?" (depois de Bastião nível 7) → Duro de Matar.
- "me explica o sistema" → apresentação do livro, sem regra inventada.
- "o crítico dobra o bônus?" → não, atributo e fixos entram uma vez (sem Golpe Cirúrgico no meio).

## O que continua aberto

- **Pergunta que compara duas coisas** ("diferença entre latente e descendente?") traz só uma
  delas; o Haiku então disse "não achei latente" sem responder a metade que tinha.
- **Item específico dentro de tabela grande**: "qual o dano da katana?" não acha a tabela de
  Lâminas (a palavra aparece em 6 páginas e a de Relíquias ganha).
- "posso voar?", "esquiva funciona como", "como funciona iniciativa" e "posso atacar duas vezes
  no turno?" ainda caem em página vizinha.
- O fallback "me diga o capítulo ou a habilidade" aparece até quando a pessoa citou o nome certo;
  com a busca nova isso cai muito, mas o texto pede algo que um jogador novo não sabe dar.

## Reproduzir

```
cd "Closure Lab/Closure"
python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
python3 avaliacao-perguntas/2026-10-13/proposta/aplicar.py /tmp/pagina.html /tmp/v2.html
python3 avaliacao-perguntas/2026-10-13/proposta/aplicar_lore.py /tmp/v2.html /tmp/v2l.html
B=avaliacao-perguntas/2026-10-13/bateria
for p in pagina v2 v2l; do node $B/montar.js /tmp/$p.html $B/holdout.json /tmp/ho_$p.json kal 14 >/dev/null; done
python3 $B/avaliar2.py $B/holdout.json /tmp/ho_pagina.json /tmp/ho_v2.json /tmp/ho_v2l.json
```

`montar.js` roda o JS da própria página no Node (sem navegador) e grava o prompt exato de cada
pergunta; `avaliar2.py` confere se o trecho esperado entrou. Respostas do Haiku em `respostas/`.
