# RPG---BOT

Atualização de mundo preparada: [fontes autorizadas da Era da Revolução](Closure/dados/mundo/LEIA-ME.md)
para Kal'tsit e Closure, sem as três pastas excluídas pelo criador. Publicação
separada da integração B47 já instalada.

Bot de Discord da guilda do **Ciclo Maldito**: tira dúvida de regra, corrige ficha e conversa
na voz de uma personagem de Arknights (Kal'tsit de dia, Closure de noite).

## Estrutura

| Pasta | O que é |
|---|---|
| [`Closure/`](Closure/) | Projeto atual. Comece pelo [`Closure/README.md`](Closure/README.md). |
| `Closure/dados/personagem/` | Cards, voz, exemplos e avaliações da Kal'tsit e da Closure. |
| `Closure/dados/sistema/` | Texto do Ciclo Maldito usado como base de consulta. |
| [`Closure/src/`](Closure/src/LEIA-ME.md) | Código do bot novo: plantão das duas personagens, webhook, registro e clima. |
| `Closure/ferramentas/` | Scripts (extração de corpus, geração de card, bateria no Gemini, página de teste). |
| `Closure/docs/`, `Closure/pesquisa/` | Decisões, planejamento e pesquisas. |
| [`Closure Legado/`](Closure%20Legado/) | Bot antigo (`closure_lab.py`, discord.py + Gemini), guardado como referência. |

## O que não está no repositório

- `.env` e qualquer chave: use o [`.env.exemplo`](.env.exemplo) como modelo.
- PDFs (livro do Ciclo Maldito, livro de F&M): ficam na pasta local.
- `closure_lab.db`: dados de execução do bot antigo.
- A chave de clima (OpenWeatherMap) do bot antigo: fica só na cópia local de `Closure Legado/closure_lab.py`, no PC. Aqui o código lê `WEATHER_API_KEY` do `.env`.
- `Closure/dados/corpus_*`: falas extraídas do jogo, regeneráveis com `Closure/ferramentas/extrair_corpus.py`.

## Análise B47

O projeto `Closure/` integra o contrato ANALISE 11 da ficha atual. Revisão vigente: 822 testes (821 aprovados, um opcional pulado). Código 40d32a7 da PR 65 implantado com autorização, sem novo merge; 44 análises reais no Discord (13 básicas, 28 avançadas do consumidor e três após implantação). Cartões vazios, cores por página e responsividade validados. PR 65 aberta, segunda pessoa no painel, recálculos nativos ampliados e limites do produtor/mestre continuam separados. [Contrato, cobertura e execução](Closure/dados/ficha/INTEGRACAO-B47.md) · [Retomada da integração](Closure/docs/RETOMADA-B47.md).
