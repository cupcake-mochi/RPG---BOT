# Closure: contagem da voz (números brutos da etapa 1)

> 12/10/2026. Gerado por `ferramentas/contar_voz.py` sobre `dados/corpus_closure/`. Só número; a leitura
> está na `voz.md`. Os padrões (regex) estão no topo do script, pra conferir o que cada linha conta.
> Porcentagem = falas com a marca / falas da personagem. O elenco de comparação é medido direto nos roteiros
> do clone YoStar (13/11/2025), com a mesma régua. As linhas "campo:" são contagem por palavra-chave e pegam
> falso positivo; servem pra comparar entre personagens, não como número exato do traço.

Comando:

    python ferramentas/contar_voz.py --corpus dados/corpus_closure/historia_en_US.jsonl --nome Closure \
        --raiz <clone YoStar> --comparar "Kal'tsit" --comparar Amiya --comparar W --comparar Warfarin \
        --comparar Theresa --comparar Exusiai --comparar Feist

## EN, história (1.557 falas)

| Medida | Closure | Kal'tsit | Amiya | W | Warfarin | Theresa | Exusiai | Feist |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| falas | 1557 | 5811 | 6160 | 2137 | 469 | 1394 | 1289 | 881 |
| mediana | 11 | 12 | 8.0 | 9 | 13 | 11.0 | 9 | 9 |
| media | 12.6 | 13.2 | 9.5 | 10.5 | 14.2 | 11.7 | 10.7 | 10.3 |
| p90 | 25 | 26 | 21 | 21 | 28 | 23 | 22 | 22 |
| curtas<=3 | 254 (16.3%) | 899 (15.5%) | 1569 (25.5%) | 444 (20.8%) | 49 (10.4%) | 248 (17.8%) | 242 (18.8%) | 210 (23.8%) |
| só reticência | 30 (1.9%) | 253 (4.4%) | 257 (4.2%) | 91 (4.3%) | 10 (2.1%) | 60 (4.3%) | 19 (1.5%) | 39 (4.4%) |
| ! | 350 (22.5%) | 115 (2.0%) | 896 (14.5%) | 203 (9.5%) | 32 (6.8%) | 12 (0.9%) | 335 (26.0%) | 114 (12.9%) |
| !!+ | 1 (0.1%) | 0 (0.0%) | 22 (0.4%) | 3 (0.1%) | 0 (0.0%) | 0 (0.0%) | 3 (0.2%) | 0 (0.0%) |
| ?! / !? | 40 (2.6%) | 8 (0.1%) | 65 (1.1%) | 36 (1.7%) | 7 (1.5%) | 0 (0.0%) | 20 (1.6%) | 10 (1.1%) |
| ? | 437 (28.1%) | 594 (10.2%) | 1020 (16.6%) | 761 (35.6%) | 100 (21.3%) | 247 (17.7%) | 421 (32.7%) | 195 (22.1%) |
| ~ | 6 (0.4%) | 0 (0.0%) | 2 (0.0%) | 20 (0.9%) | 0 (0.0%) | 0 (0.0%) | 30 (2.3%) | 0 (0.0%) |
| reticências | 384 (24.7%) | 1007 (17.3%) | 2622 (42.6%) | 502 (23.5%) | 71 (15.1%) | 398 (28.6%) | 238 (18.5%) | 266 (30.2%) |
| travessão | 93 (6.0%) | 202 (3.5%) | 241 (3.9%) | 148 (6.9%) | 26 (5.5%) | 38 (2.7%) | 53 (4.1%) | 40 (4.5%) |
| fala entre parênteses (pensamento) | 19 (1.2%) | 33 (0.6%) | 82 (1.3%) | 23 (1.1%) | 6 (1.3%) | 1 (0.1%) | 33 (2.6%) | 3 (0.3%) |
| gagueira (W-Why) | 7 (0.4%) | 0 (0.0%) | 43 (0.7%) | 6 (0.3%) | 3 (0.6%) | 1 (0.1%) | 2 (0.2%) | 12 (1.4%) |
| letra esticada (sooo) | 17 (1.1%) | 0 (0.0%) | 9 (0.1%) | 6 (0.3%) | 0 (0.0%) | 0 (0.0%) | 13 (1.0%) | 2 (0.2%) |
| palavra em CAIXA ALTA | 30 (1.9%) | 7 (0.1%) | 10 (0.2%) | 6 (0.3%) | 2 (0.4%) | 0 (0.0%) | 12 (0.9%) | 1 (0.1%) |
| riso: heh / heh heh | 3 (0.2%) | 3 (0.1%) | 2 (0.0%) | 7 (0.3%) | 1 (0.2%) | 1 (0.1%) | 4 (0.3%) | 0 (0.0%) |
| riso: hehe / hehehe | 4 (0.3%) | 0 (0.0%) | 10 (0.2%) | 7 (0.3%) | 0 (0.0%) | 1 (0.1%) | 11 (0.9%) | 2 (0.2%) |
| riso: eheh / ehehe | 2 (0.1%) | 0 (0.0%) | 3 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| riso: haha / ahaha | 8 (0.5%) | 0 (0.0%) | 17 (0.3%) | 11 (0.5%) | 1 (0.2%) | 1 (0.1%) | 12 (0.9%) | 13 (1.5%) |
| riso: hee hee / teehee | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1 (0.1%) | 2 (0.2%) | 0 (0.0%) |
| riso: pfft / pff | 0 (0.0%) | 0 (0.0%) | 1 (0.0%) | 3 (0.1%) | 1 (0.2%) | 1 (0.1%) | 0 (0.0%) | 0 (0.0%) |
| riso (qualquer) | 17 (1.1%) | 3 (0.1%) | 32 (0.5%) | 28 (1.3%) | 3 (0.6%) | 4 (0.3%) | 29 (2.2%) | 15 (1.7%) |
| 'Heh heh~' exato | 1 (0.1%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| abre com interjeição | 162 (10.4%) | 30 (0.5%) | 276 (4.5%) | 142 (6.6%) | 18 (3.8%) | 31 (2.2%) | 157 (12.2%) | 33 (3.7%) |
| com gíria/informal | 305 (19.6%) | 180 (3.1%) | 370 (6.0%) | 352 (16.5%) | 39 (8.3%) | 55 (3.9%) | 208 (16.1%) | 58 (6.6%) |
| contração | 740 (47.5%) | 1894 (32.6%) | 2354 (38.2%) | 1020 (47.7%) | 234 (49.9%) | 434 (31.1%) | 666 (51.7%) | 421 (47.8%) |
| forma sem contração (I do not, it is) | 1 (0.1%) | 137 (2.4%) | 25 (0.4%) | 0 (0.0%) | 1 (0.2%) | 20 (1.4%) | 0 (0.0%) | 1 (0.1%) |
| palavras 10+ letras (% das palavras) | 2.9 | 4.3 | 2.8 | 1.6 | 2.5 | 2.7 | 2.0 | 2.2 |
| campo: dinheiro / loja | 47 (3.0%) | 71 (1.2%) | 49 (0.8%) | 35 (1.6%) | 5 (1.1%) | 11 (0.8%) | 43 (3.3%) | 28 (3.2%) |
| campo: máquina / técnica | 215 (13.8%) | 268 (4.6%) | 93 (1.5%) | 19 (0.9%) | 10 (2.1%) | 16 (1.1%) | 8 (0.6%) | 37 (4.2%) |
| campo: cansaço / trabalho / comida | 96 (6.2%) | 150 (2.6%) | 158 (2.6%) | 36 (1.7%) | 21 (4.5%) | 50 (3.6%) | 47 (3.6%) | 41 (4.7%) |
| campo: auto-título (genius, Chief Engineer...) | 9 (0.6%) | 3 (0.1%) | 0 (0.0%) | 1 (0.0%) | 0 (0.0%) | 1 (0.1%) | 0 (0.0%) | 0 (0.0%) |
| campo: provoca pela idade (old hag, as old as) | 4 (0.3%) | 2 (0.0%) | 2 (0.0%) | 32 (1.5%) | 1 (0.2%) | 0 (0.0%) | 2 (0.2%) | 0 (0.0%) |
| campo: pega no flagra / desculpa rápida | 10 (0.6%) | 3 (0.1%) | 0 (0.0%) | 2 (0.1%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1 (0.1%) |
| campo: vergonha (stop / don't say it) | 6 (0.4%) | 5 (0.1%) | 6 (0.1%) | 18 (0.8%) | 1 (0.2%) | 0 (0.0%) | 0 (0.0%) | 1 (0.1%) |
| campo: autoelogio | 19 (1.2%) | 24 (0.4%) | 20 (0.3%) | 4 (0.2%) | 3 (0.6%) | 7 (0.5%) | 9 (0.7%) | 8 (0.9%) |
| Doctor/Doc | 110 (7.1%) | 241 (4.1%) | 581 (9.4%) | 10 (0.5%) | 11 (2.3%) | 112 (8.0%) | 1 (0.1%) | 34 (3.9%) |
| vocativo (início ou fim) | 60 (3.9%) | 287 (4.9%) | 374 (6.1%) | 34 (1.6%) | 18 (3.8%) | 113 (8.1%) | 34 (2.6%) | 41 (4.7%) |
| respostas a outra pessoa | 792 (50.9%) | 2257 (38.8%) | 2616 (42.5%) | 985 (46.1%) | 239 (51.0%) | 595 (42.7%) | 763 (59.2%) | 498 (56.5%) |
| continua fala dela | 762 (48.9%) | 3521 (60.6%) | 3494 (56.7%) | 1141 (53.4%) | 229 (48.8%) | 788 (56.5%) | 516 (40.0%) | 382 (43.4%) |

**Interjeição que abre a fala:** oh (34), huh (32), hm (12), uh (11), whoa (10), hmm (8), eh (7), ugh (6), uhh (5), ah (4), phew (4), ahem (4), nope (4), hmph (3), wow (3)

**Gíria / informal (falas com a palavra):** like (111), gonna (32), yeah (28), alright (19), guys (17), stuff (17), okay (15), kinda (15), gotta (13), super (12), wanna (10), seriously (8), crap (8), dammit (6), lemme (5), nope (5), yep (4), hell (4), totally (3), y'know (3)

**Vocativo (nome no começo ou no fim da fala):** Doctor (20), Kal'tsit (10), Amiya (7), Doc (4), Snowsant (4), Feist (3), Mayer (3), Jessica (2), PRTS (2), Mon3tr (1), Siege (1), Horn (1), Specter (1), THRM-EX (1)

**Palavras que mais voltam (fora as vazias):** doctor (105), time (75), way (62), rhodes (60), kal'tsit (55), island (48), good (40), make (37), amiya (36), work (35), look (35), take (34), little (34), need (32), sure (31), something (30), first (29), down (28), already (27), though (27), off (27), wait (27), course (26), other (26), let (25), keep (25), tell (25), things (24), thing (24), thought (24), never (24), drones (23), alright (23), give (22), data (22), told (22), want (22), lot (21), equipment (21), kind (21)

**Quem falou antes, quando não é ela:** Kal'tsit (120), Mayer (80), Snowsant (68), Feist (60), PRTS (45), Amiya (43), Nian (23), Specter (20), Conviction (17), Jessica (16), ??? (15), Friston-3 (15), Fang (13), Siege (13), Rockrock (13), Logistics Operator (13), Shirayuki (13), Warfarin (12), Assistant Operator (12), Misery (11), Blaze (10), Robin (10), Weedy (10), Rhodes Island Operator (8), Executor (8)

**Falas com '!' por tipo de cena:** eventos e outros: 114/460 (24.8%), história principal: 150/594 (25.3%), registros de operador: 86/503 (17.1%)


## CN: Closure (história e falas de operadora)

    python ferramentas/contar_voz.py --corpus dados/corpus_closure/historia_zh_CN.jsonl --nome 可露希尔 \
        --zh --operadora dados/corpus_closure/operadora_zh_CN.json

| Marca | história (todas) | operadora |
| --- | --- | --- |
| falas | 2096 | 38 |
| caracteres, mediana | 16.0 | 26.5 |
| ～ / ~ | 4 (0.2%) | 1 (2.6%) |
| ！ | 451 (21.5%) | 12 (31.6%) |
| ？ | 501 (23.9%) | 19 (50.0%) |
| …… | 612 (29.2%) | 12 (31.6%) |
| —— | 188 (9.0%) | 8 (21.1%) |
| 嘿嘿 / 嘿 | 19 (0.9%) | 1 (2.6%) |
| 哈哈 | 10 (0.5%) | 0 (0.0%) |
| 呜 (choro/manha) | 16 (0.8%) | 1 (2.6%) |
| 啦 | 54 (2.6%) | 2 (5.3%) |
| 嘛 | 39 (1.9%) | 1 (2.6%) |
| 呢 | 58 (2.8%) | 4 (10.5%) |
| 哼 | 7 (0.3%) | 0 (0.0%) |
| 诶 / 欸 / 哎 | 51 (2.4%) | 0 (0.0%) |
| 哇 | 18 (0.9%) | 0 (0.0%) |
| 唔 | 30 (1.4%) | 0 (0.0%) |
| 咳 (ahem) | 12 (0.6%) | 0 (0.0%) |
| 钱/龙门币/付费/收费 | 32 (1.5%) | 6 (15.8%) |

## CN: Kal'tsit, pra comparar (história, 5.956 falas)

| Marca | história (todas) |
| --- | --- |
| falas | 5956 |
| caracteres, mediana | 18.0 |
| ～ / ~ | 0 (0.0%) |
| ！ | 115 (1.9%) |
| ？ | 575 (9.7%) |
| …… | 1183 (19.9%) |
| —— | 250 (4.2%) |
| 嘿嘿 / 嘿 | 0 (0.0%) |
| 哈哈 | 0 (0.0%) |
| 呜 (choro/manha) | 0 (0.0%) |
| 啦 | 0 (0.0%) |
| 嘛 | 0 (0.0%) |
| 呢 | 38 (0.6%) |
| 哼 | 2 (0.0%) |
| 诶 / 欸 / 哎 | 1 (0.0%) |
| 哇 | 0 (0.0%) |
| 唔 | 7 (0.1%) |
| 咳 (ahem) | 1 (0.0%) |
| 钱/龙门币/付费/收费 | 38 (0.6%) |

## Por interlocutor (EN): "!" e "?" nas respostas dela

| Fala antes de | Respostas | Com "!" | Com "?" |
| ------------- | --------- | ------- | ------- |
| Kal'tsit | 120 | 18,3% | 32,5% |
| Mayer (colega engenheira) | 80 | 16,2% | 33,8% |
| Snowsant (júnior que ela orienta) | 68 | 16,2% | 41,2% |
| Feist (colega em zona de guerra) | 60 | 38,3% | 36,7% |
| PRTS (o sistema da nave) | 45 | 20,0% | 24,4% |
| Amiya | 43 | 32,6% | 37,2% |

Outras contagens soltas (EN, todas as falas): "Doctor" 105, "Doc" 6, "Kal'tsit" 61 (com "Dr." só 3),
o próprio nome "Closure" 10, palavrão leve (dammit, damn, crap, hell, ass, prick, dipshit) 23 falas (1,5%),
"girl/kid/boy" pra júnior 17, "Ahem" 4.

## Leitura humana: amostra de 130 respostas

`--amostra 130 --seed 12`: respostas a outra pessoa, espalhadas por todos os 77 arquivos. Classificação
minha, uma categoria por fala:

| Tipo de fala | Falas | % |
| ------------ | ----- | - |
| Técnica / trabalho, neutra (relatório, plano, "On it!") | 30 | 23% |
| Brincadeira: provocação, exagero, desculpa esfarrapada, piada | 29 | 22% |
| Reação curta (Huh?, Nope., Right., ......) | 27 | 21% |
| Tensão de crise (susto, aviso, "Hold on!") | 21 | 16% |
| Séria ou afetiva (opinião, conselho, preocupação) | 13 | 10% |
| Outras (cordial, se gabando sem piada) | 10 | 8% |

A brincadeira se concentra nos eventos e registros (20 das 29; 9 na história principal). Na história principal ela está quase
sempre em crise ou trabalhando.
