# Frente 1: quanto material oficial existe dos outros personagens

> Nota de pesquisa, 12/10/2026. Mesmos dados da pesquisa anterior (`ArknightsGameData` zh_CN até 08/10/2026; `ArknightsGameData_YoStar` en_US até nov/2025), contagem por script na tag `[name="..."]` dos arquivos de história.

## Números

- História em inglês: **308.029 falas** de **5.186 nomes** de falante distintos. Em chinês: 372.628 falas de 7.117 nomes.
- No inglês, **130 personagens têm 500 falas ou mais**, e **28 têm mais de 1.000**.
- Falas de operadora (secretária, conversas, promoção etc.): no espelho EN, os **374 operadores jogáveis** até nov/2025 têm todas, ~42 falas cada, em EN, JP e KR. Operadores lançados depois disso no global ficam de fora do espelho; os do CN têm tudo em chinês.

## Top 40 em falas de história (inglês)

| # | Nome | Falas | # | Nome | Falas |
|---|---|---|---|---|---|
| 1 | Amiya | 6.160 | 21 | Horn | 1.173 |
| 2 | Kal'tsit | 5.811 | 22 | Hoederer | 1.153 |
| 3 | ??? (falante oculto) | 4.289 | 23 | Muelsyse | 1.149 |
| 4 | Ch'en | 2.794 | 24 | Arturia | 1.129 |
| 5 | W | 2.137 | 25 | Hibiscus | 1.100 |
| 6 | Silence | 1.587 | 26 | Leto | 1.099 |
| 7 | Siege | 1.577 | 27 | Hoshiguma | 1.076 |
| 8 | Blaze | 1.560 | 28 | Lava | 1.056 |
| 9 | **Closure** | 1.557 | 29 | Ines | 980 |
| 10 | Federico | 1.465 | 30 | Lavinia | 975 |
| 11 | Talulah | 1.441 | 31 | Lee | 968 |
| 12 | Theresa | 1.394 | 32 | Zuo Le | 966 |
| 13 | Gavial | 1.329 | 33 | Yato | 962 |
| 14 | Enciodes | 1.325 | 34 | Gladiia | 941 |
| 15 | Ebenholz | 1.319 | 35 | Mostima | 937 |
| 16 | Skadi | 1.317 | 36 | Bagpipe | 919 |
| 17 | Exusiai | 1.289 | 37 | Swire | 908 |
| 18 | Jessica | 1.236 | 38 | Liskarm | 895 |
| 19 | Magallan | 1.215 | 39 | Delphine | 894 |
| 20 | Texas | 1.203 | 40 | Wei Yenwu | 882 |

Lista completa (nomes com 20+ falas) salva em `Closure/dados/falantes_historia_en_US.csv` e `falantes_historia_zh_CN.csv`.

## Cuidados

- A contagem é por **texto da tag**, não por personagem. Formas alternativas viram nomes separados (ex.: alter, nome com título, "Skadi" vs "Skadi the Corrupting Heart" se a tag mudar), e nomes iguais de personagens diferentes se somam. Para um personagem específico, conferir as variantes antes de confiar no número.
- "???" é qualquer falante não revelado na cena; não é um personagem.
- O inglês está parado em nov/2025; personagens que cresceram no CN depois disso aparecem menores aqui.

## Inferência

- A Closure é a 9ª personagem nomeada que mais fala no inglês. O método da pesquisa anterior (minerar a ficha de voz do corpus e transcriar) serve igual para qualquer um desses ~130 personagens com 500+ falas; o extrator `[name="..."]` só precisa do nome certo.
