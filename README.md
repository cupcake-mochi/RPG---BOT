# RPG---BOT

**Publicado · 21/10 às 13:25 (Brasília):** idioma PT-BR/inglês, lore original/Nova Terra por servidor e links públicos na conversa. Dois bots auditados após implantação; 944 testes das Guias e 149 da Arquivista, além de 36 JS. [Estado atual e limites](Closure/docs/RETOMADA-PUBLICO.md).

**Guias de criação · 21/10:** `GC:guia criar` orienta da cópia à emissão;
`GC:guia planilha` explica abas e configurações; `GC:guia ficha` explica a
análise. [Conteúdo e fontes](Closure/docs/GUIAS-DE-USO.md).

**Ficha R53 · 19/10:** consumidor ANALISE 12 na PR 67; 13 análises reais no
Discord, cópias nativas e XLSX conferidos. Suíte: 882 executados, 881 aprovados,
1 opcional pulado. Cartões R53 não equivalem à auditoria integral do livro.
[Bateria, fichas de teste e limites](Closure/dados/ficha/BATERIA-NATIVA-R53.md).

Continuações “E de BH?” e perguntas inteiras em `GC:clima` corrigidas e publicadas
em 19/10, com regressões dos fluxos e dados reais conferidos.
[Fechamento atual](Closure/pesquisa/validacao/2026-10-19-clima-seguimento/relatorio.md).

Correção de “clima atual de BH” publicada na Discloud em 18/10 às 23:49,
com consulta real conferida e sem chamar IA nos testes.
[Diagnóstico, testes e limites](Closure/pesquisa/validacao/2026-10-18-clima-bh/relatorio.md).

Atualização de mundo publicada na Discloud em 18/10/2026, com autorização:
[fontes da Era da Revolução](Closure/dados/mundo/LEIA-ME.md) para as duas guias,
sem as três pastas excluídas. [Testes e conferência da publicação](Closure/pesquisa/validacao/2026-10-18-mundo-nomes/relatorio.md).

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

O projeto `Closure/` consome o contrato ANALISE 12/R53 e preserva compatibilidade comprovada com formatos anteriores. A suíte atual tem 944 testes (943 aprovados, um opcional pulado). A análise é parcial; a auditoria integral do corpus R53, dados ausentes do produtor e decisões do mestre continuam separados. [Contrato e cobertura](Closure/dados/ficha/INTEGRACAO-B47.md) · [Retomada R53](Closure/docs/RETOMADA-R53.md).
