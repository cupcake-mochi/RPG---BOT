# A voz da Closure já existe em inglês; o pt-BR tem que ser construído

**Existe material oficial suficiente para minerar a voz dela, mas nada em português.** Nos dados do jogo, a Closure tem 1.557 falas de história em inglês, japonês e coreano (até nov/2025) e 2.096 em chinês (até out/2026), já extraídas para `dados/corpus_closure/`. Como operadora jogável ela só existe no CN (lançada com o evento Critical Phase Transition em 01/05/2026 07:00 no horário da China, 30/04 à noite em Brasília; global "TBA"), então as 38 falas de operadora e o arquivo pessoal existem só em chinês, sem tradução nem de fã na wiki em inglês. Português não há: Arknights não tem pt-BR, o Endfield tem texto oficial em pt-BR mas a Closure não aparece nele, e não achei tradução de fã. O caminho é minerar a ficha de voz do inglês, usar o chinês como árbitro, transcriar para pt-BR com regras escritas e medir com teste cego humano, porque LLM-juiz erra demais nesse tipo de julgamento.

Notas completas em [research_notes/Fontes multilíngues e método de fidelidade/](../research_notes/Fontes%20multil%C3%ADngues%20e%20m%C3%A9todo%20de%20fidelidade/).

## O que existe, por idioma

| Idioma | Falas de história | Falas de operadora e arquivo | Fonte |
|---|---|---|---|
| Chinês (original) | 2.096 em 120 arquivos | 38 falas + 9 blocos de arquivo | `ArknightsGameData`, dados de 08/10/2026 |
| Inglês | 1.557 em 77 arquivos | não existe ainda | `ArknightsGameData_YoStar`, **parado em nov/2025** |
| Japonês | 1.557 | não existe ainda | idem |
| Coreano | 1.557 | não existe ainda | idem |
| Português | nada | nada | — |

- EN, JP e KR traduzem arquivo por arquivo, então as falas alinham entre si e com o CN nos 77 arquivos em comum.
- O espelho global está parado há 11 meses. Falas dela em eventos do global depois de nov/2025 não estão no corpus.
- Onde ela mais fala em inglês: evento `act8mini`, Operator Records de Snowsant, Weedy, Thermal-EX e Ines, e capítulos 9, 10, 14 e 15 da história principal.
- O Endfield em pt-BR (localizado pela Logrus IT, só texto) serve de glossário oficial de termos do universo, não de fala dela.

## Como transformar isso numa Closure em pt-BR

1. **Ficha de voz tirada do corpus.** Contar tamanho de fala, bordões ("Heh heh~"), como ela chama cada pessoa e os temas que voltam (vender, cobrar, comer, cansaço de engenheira, segredo pago). Cada traço cita 2 ou 3 falas reais. Perfil escrito antes da fala tende a contradizer a fala (BEYOND DIALOGUE, 2024).
2. **Inglês como base, chinês como árbitro.** O EN já é transcriado para soar natural fora do chinês; o CN diz o que ela quis dizer e tem o material mais novo.
3. **Transcriação com regras escritas**, não tradução literal: forma fixa para o Doutor, til mantido, gíria leve e atual, trocadilho de dinheiro refeito em português, nomes próprios no inglês do global ou no pt-BR oficial do Endfield.
4. **Dois usos do corpus:** 3 a 5 falas transcriadas a mão fixas no card, e um índice das falas EN de onde o bot puxa 2 ou 3 parecidas com a conversa do momento (abordagem do ChatHaruhi). Isso encaixa nos passos 3 e 4 do relatório anterior.

## Como saber se ficou fiel

- **Teste de quem falou:** ~20 falas reais transcriadas misturadas com ~20 do bot para os mesmos gatilhos; 3 a 5 pessoas que conhecem a Closure tentam separar. Acerto perto de 50% é o objetivo.
- **Nota de 1 a 5 em 6 critérios** tirados do CharacterEval: natural em português, jeito de falar, atitude, acerto de lore, não inventa lore, variedade.
- **LLM-juiz só para triagem.** No PersonaEval (2025), o melhor LLM acertou ~69% em identificar quem está falando, contra 90,8% de humanos.

## O que não foi confirmado

| Ponto | Situação | Como conferir |
|---|---|---|
| Data de lançamento no global | wiki diz "TBA" | acompanhar a wiki/anúncios |
| Falas dela no global depois de nov/2025 | fora do espelho | achar espelho global atualizado ou extrair do cliente |
| Closure no Endfield | nenhuma fonte achada; wiki do Endfield bloqueia leitura automática | abrir a wiki à mão |
| END Wiki em português ter diálogo e ser pt-BR | página "sobre" não diz | abrir a versão em português |
| Mecanismo de busca do ChatHaruhi | resumo não detalha | PDF do paper |
| Números do PersonaEval e CharacterEval | lidos do resumo e da página HTML | PDFs |
| Exemplos em inglês no prompt mantêm o estilo em pt-BR? | nenhum estudo achado | o próprio teste cego |
| Tradução de fã pt-BR da Closure | não achada; grupos fechados não indexam | perguntar na comunidade BR |

## Conclusão

A primeira pesquisa disse que o ativo do projeto é um conjunto de arquivos de texto. Esta mostra que a matéria-prima já está no disco: ~1.500 falas em inglês e ~2.100 em chinês. O trabalho que falta é humano e em português: ler o corpus, escrever a ficha de voz, transcriar os exemplos e rodar o teste cego. Nenhuma dessas etapas depende de escolher modelo ou gastar com API.

Fontes: [ArknightsGameData](https://github.com/Kengxxiao/ArknightsGameData) · [ArknightsGameData_YoStar](https://github.com/Kengxxiao/ArknightsGameData_YoStar) · [Closure na wiki.gg](https://arknights.wiki.gg/wiki/Closure) · [lista de lançamentos](https://arknights.wiki.gg/wiki/Operator/List/Release) · [Logrus IT, Endfield](https://games.logrusit.com/en/news/arknights-endfield/) · [END Wiki](https://end.wiki/fr/about/) · [ChatHaruhi](https://arxiv.org/abs/2308.09597) · [BEYOND DIALOGUE](https://arxiv.org/abs/2408.10903) · [PersonaEval](https://arxiv.org/abs/2508.10014v1) · [CharacterEval](https://arxiv.org/html/2401.01275v1) · [LocalizeDirect, transcriação](https://localizedirect.com/posts/transcreation-in-video-game-localization)
