# Closure: canon e corte de tempo

> Etapa 0 do `docs/PLANO-PERSONALIDADE.md`, 12/10/2026. Cada fato cita de onde saiu.
> Corpus em `dados/corpus_closure/` (ver o `LEIA-ME.md` de lá), gerado por `ferramentas/extrair_corpus.py`.
> Citação "arquivo:linha" = linha do roteiro no corpus. Traduções do chinês são minhas.

> **Referência, não vai pro bot (decisão do Mizuki, 12/10/2026).** A Closure do bot vive no
> mundo do Ciclo Maldito. Daqui sai só o que explica a personalidade dela; nomes, lugares e
> eventos de Arknights ficam de fora do card, dos exemplos e do lorebook.

## Âncoras literais (nomes e termos, como estão no jogo)

| Termo | EN | CN | Onde |
| ----- | -- | -- | ---- |
| Nome | Closure | 可露希尔 | todas as falas |
| Apelido | "Clo" (Cliffheart); Kal'tsit dá bronca com "Clo-sure!" | — | `act7mini_st06:494`; fala da Kal'tsit antes de `act4d0_st07:252` |
| Como os robôs chamam | "Master Closure" | 可露希尔主人 | `story_cast3_1_1`; `story_closur_1_1:992` |
| Cargo | Chief Engineer; "head of Engineering" | 罗德岛总工程师 | `act4d0_st07:108`, `story_snsant_1_1:709`; arquivo CN |
| Cargo no tutorial (2019) | "Rhodes Island Reliability Engineer" | 罗德岛舰船可靠性工程师 | `obt/guide/l0-11/0_building_init.txt:22` |
| Raça | Sarkaz, **Vampire** (no EN, "Sanguinarch" é outra coisa: o título do senhor dos vampiros) | 萨卡兹, 血魔 | `act8mini_st06:164`; arquivo CN |
| Apelido que ela mesma se deu | "Destroyer of the Kazdel Information World" | 卡兹戴尔百强青年 ("top 100 jovens de Kazdel", **autoproclamado**) | `act8mini_st06:180`; fala de operadora "晋升后交谈2" |
| O que ela chefia (CN) | — | 采购部负责人 (chefe de Compras), "e mais vários departamentos" | arquivo CN, "客观履历" |

## A decisão que vem antes de tudo: qual Closure

| Momento | O que ela é | Onde está o texto | Global tem? |
| ------- | ----------- | ----------------- | ----------- |
| Até o Episódio 15 | Engenheira-chefe brincalhona, foge de trabalho, provoca a Kal'tsit, séria na crise | 1.557 falas EN (cap. 8 a 15, eventos, 14 registros de outras operadoras) | Sim |
| Depois do Ep. 15, com a Kal'tsit morta | Assume as decisões finais de quase todos os departamentos; dorme 4 h por dia em 4 pedaços; tenta trazer a Kal'tsit de volta (relatório de progresso nº 1.860 a 1.864, "progresso: 0") | Arquivo pessoal CN; registro `story_closur_1_1` (170 falas); fase `tr28` | **Não.** Cap. 16 saiu no global em 19/03/2026 mas não está no espelho EN; o resto chega em 14/10/2026 |
| Ep. 17 e falas de operadora | É ela quem descobre como trazer a Kal'tsit de volta; depois que a Kal'tsit volta, reclama de ainda carregar o trabalho | 250 falas CN do cap. 17 e `tr28`; 38 falas de operadora CN | Chega em 14/10/2026 |

**Recomendação (inferência, decisão do Mizuki):** cortar a voz no **Ep. 15 em EN**, como foi feito com a
Kal'tsit clássica. O material CN não muda a personalidade: reforça os mesmos traços (piada de cobrança,
reclamar de cansaço, cuidar dos outros sem admitir). Ele entra na `voz.md` só como reforço, sempre marcado CN.

Fontes: [Closure na wiki](https://arknights.wiki.gg/wiki/Closure),
[lista de lançamentos](https://arknights.wiki.gg/wiki/Operator/List/Release),
[Critical Phase Transition](https://arknights.wiki.gg/wiki/Critical_Phase_Transition),
[Episódio 16](https://arknights.wiki.gg/wiki/Episode_16).

## Ela é operadora jogável? Sim, desde 2026. Antes era NPC

- **Antes:** NPC. Cuidava da Loja do jogo e foi "the only NPC who has an animated model until her
  introduction as an Operator"; foi também a primeira personagem com sprite animado, na tela da Loja.
  *([Trivia](https://arknights.wiki.gg/wiki/Closure/Trivia))*
- **CN:** operadora 6★, Vanguarda da subclasse Tactician (`TIER_6`, `PIONEER`, `tactician` em
  `character_table.json`, id `char_4228_closur`), entra pelo recrutamento padrão (`招募寻访`; a lista de
  lançamentos não marca como limitada). O registro de operadora dela libera em `1777590000` =
  **01/05/2026 07:00 na China** (30/04 às 20:00 em Brasília). A lista da wiki diz 2026-04-30, provavelmente
  por fuso. Veio junto com a Kal'tsit·Esperanta, no evento Critical Phase Transition (aniversário de 7 anos do CN).
- **Global:** a lista de lançamentos da wiki ainda diz **"TBA"** (conferido em 12/10/2026). Mas a página do
  evento Critical Phase Transition no global (14/10/2026, 08:00 UTC-7) dá a ela bônus de confiança e o
  módulo TAC-X, e um guia de terceiros ([topuplive](https://www.topuplive.com/news/arknights-critical-phase-transition-banner-guide.html), 28/09/2026,
  "based on future content planning") diz que ela entra no banner. **Provável: global em 14/10/2026. Não confirmado.**
- **Vozes:** JP Manami Numakura, CN Hou Xiaofei, EN Carla Tassara, KR Min Ah. Arte: Liyu黎. *(wiki)*
- **Falas de operadora e arquivo pessoal:** só em CN (`operadora_zh_CN.json`). O espelho EN parou em 13/11/2025.

## Fatos de antes do Ep. 15 (EN, valem em qualquer servidor)

- **Engenheira-chefe da Rhodes Island**: "My sense of responsibility as Chief Engineer of Rhodes Island
  has suddenly awakened!" (`act4d0_st07:108`); "as the head of Engineering, I'm declaring..."
  (`story_snsant_1_1:709`). Assumiu a engenharia logo depois de entrar: "Not long after I took charge
  of Rhodes Island's engineering..." (`act8mini_st06:216`).
- **Vampira Sarkaz de família antiga**: "A family of vampires. You can smell the rotten stench in the
  words alone, right?" (`act8mini_st06:164`). Não liga pras artes de vampiro: "I was never into stuff like
  that, not even one bit." (`:169`). Não sabe usar arte de sangue: "I don't know how to use Arts to rip all
  your blood out of your body" (`level_main_14-18_end:210`). Enxerga no escuro: "I'm a vampire, of
  course I can see." (`act4d0_st07:232`).
- **Hacker na juventude, num sótão em Kazdel**: "I hid my signature in the nooks and crannies of all kinds
  of data... they called me the 'Destroyer of the Kazdel Information World.'" (`act8mini_st06:179-180`);
  "I only wanna do what I wanna do, and that's why I never stepped out of my little garret." (`:171`).
- **Recrutada pela Theresa**, que abriu a porta trancada do sótão: "she told me she was looking for someone
  to break the shackles of tradition, and for that she needed an engineer" (`act8mini_st06:194`). Aceitou
  "because of the curiosity" (`:201`). Conheceu o Doctor no ponto de encontro (`:202`). Fez parte de Babel.
- **Conhece a Kal'tsit há 12 anos**: "But in these twelve years, you haven't had tea with me even once!"
  (`story_kalts_1_1:304`). Ela fazia um balão de ar quente elétrico ligando a energia de três distritos
  quando Babel a procurou (fala da Kal'tsit antes de `:300`).
- **Faz os robôs da Rhodes Island**: Lancet-2, Castle-3, THRM-EX e Friston-3 são "assigned by Engineer
  Closure" (`character_table.json` EN, campo `itemUsage`). O Castle-3 foi configurado pra ter ela como
  pessoa favorita (`handbook_info_table.json`, perfil do Castle-3).
- **Trotes famosos** (contados pelos outros): o "'Closure's Midnight Video Market' at twelve o'clock for three
  months straight" e o ar-condicionado em 36 graus (Kal'tsit, antes de `act4d0_st07:27` e `:45`; PRTS,
  antes de `act8mini_st06:338`).
- **Amiga da Warfarin**, a outra vampira: "Your blood doesn't even smell of machine oil these days."
  (Warfarin, antes de `level_main_15-18_end:635`).
- **Ela mesma se chama de "criadora da Rhodes Island"**: "Kazdel's genius engineer and the creator of Rhodes
  Island—Closure!" (`story_robin_1_1:624`). É exagero dela, não fato.

## Fatos só do CN (marcar como spoiler/CN até sair no global)

Do arquivo pessoal (`operadora_zh_CN.json`):
- Ficha: 20 anos de experiência de engenharia, nascida em Kazdel, aniversário 10/12, Sarkaz, 158 cm, não
  infectada; densidade de cristal de Originium no sangue um pouco alta (0,14u/L) por mexer com
  equipamento (`基础档案`, `临床诊断分析`).
- "Uma das mais antigas da Rhodes Island". **Enquanto a Kal'tsit esteve fora, decidia por último em todos os
  departamentos, menos o Médico**; depois da volta dela, parte disso continuou com a Closure. Sente-se
  dividida: "por baixo da casca de malandra, a responsabilidade de veterana" não deixa ela devolver o peso
  (`档案资料二`).
- Na juventude montou rede de rádio e retransmissoras caseiras por Kazdel com amigos; o primeiro aparelho
  eletrônico dela foi tirado de um Sankta morto: "那个人不该那么死的" ("essa pessoa não devia ter morrido
  assim") (`档案资料三`).
- Hacker que destruía bancos de dados por raiva; mais tarde entendeu que queria "espírito de código aberto".
  Lista de vampiros: não detesta a Warfarin, quase não detesta o Entelechia (隐德来希), detesta o
  Duq'arael (杜卡雷), e "não quer ver nem morta" os próprios pais (`档案资料四`).
- O próprio arquivo é uma piada de cobrança: "Este documento é conteúdo pago... fale com a Closure pra
  comprar acesso", e o registro de promoção termina com "您通过ZOOT快捷支付消费：180000龙门币" ("Você pagou
  180.000 LMD pelo ZOOT") (`档案资料一`, `晋升记录`).

Das falas de operadora e do cap. 17:
- A Kal'tsit volta e a Closure não quer mais ser responsável: "我真的不想当罗德岛的负责人啊！" ("Eu não quero
  ser a responsável pela Rhodes Island!") (`晋升后交谈1`). Saiu pra campo "pra fugir do trabalho"
  (`干员报到`).
- Na fase `tr28` ela registra "第1860—1864次进展报告... 进展：0" (relatórios 1.860 a 1.864 da
  ressurreição, progresso zero) e diz "我向凯尔希保证过，不会再让你或阿米娅独自背上那么多压力了" ("Prometi pra
  Kal'tsit que não ia mais deixar você ou a Amiya carregando tanta pressão sozinhos").
- No cap. 17 é ela quem acha a chave pra trazer a Kal'tsit de volta: "生命其实类似一个长期运行的进程，不是一段静态代码"
  ("a vida é tipo um processo rodando há muito tempo, não um código parado"), um "自我调用的闭环" (laço
  que chama a si mesmo) (`level_main_17-17_end`). O nome "Closure" vem do conceito de programação
  ([etimologia na wiki](https://arknights.wiki.gg/wiki/Closure)); a ligação com essa cena é inferência minha.

## O que mudou depois (marcar)

| Fato | Antes | Depois | Status |
| ---- | ----- | ------ | ------ |
| Jogável | NPC da Loja e da engenharia | Operadora 6★ | CN desde 01/05/2026; global provável 14/10/2026, **não confirmado** |
| Título | "Reliability Engineer" no tutorial de 2019 (EN e CN) | "Chief Engineer" / 总工程师 | Mudou cedo; usar "engenheira-chefe" |
| Quem manda na Rhodes Island | A Kal'tsit; a Closure foge de inspeção | Com a Kal'tsit morta, a Closure decide; depois da volta, divide | Só CN (arquivo, cap. 17, falas de operadora) |
| A Kal'tsit | Viva até o Ep. 15 | Morre no Ep. 15 (global já tem); volta no Ep. 17 graças à Closure | A volta só no CN até 14/10/2026 |
| Ficha (idade, altura, aniversário) | Não existia | Arquivo CN | Só CN |

## O que não usar como canon

- "Creator of Rhodes Island" e "the Closure difference" são autoelogio, não fato.
- "Clovisia" (390 falas) é outra personagem; a busca por "Clo" pega ela. O extrator usa a tag exata.
- A wiki diz que o nome dela vem da Ada Lovelace e que o drone dela se chama Lambda
  ([Trivia](https://arknights.wiki.gg/wiki/Closure/Trivia)); nenhum dos dois aparece nas falas do corpus.
  Não usar sem conferir.
- Idade em anos: não achei em lugar nenhum. Ela diz "I'm still a pretty young gal myself" (`story_kalts_1_1:328`)
  e a Nian acha que ela tem a idade da Lava (antes de `act6d5_st03:1067`), mas vampiro vive muito. Não inventar.

## Ainda por conferir

- Se ela sai mesmo no global em 14/10/2026, e se o texto EN das falas de operadora bate com a tradução minha.
- As 2 falas dela no cap. 16 (já no global desde 19/03/2026) não estão no corpus EN.
- O espelho EN está parado em 13/11/2025; depois de 14/10 vai ter fala dela em EN que ele não pega.
