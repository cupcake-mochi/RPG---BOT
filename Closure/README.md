# Closure

> Ponto de entrada do projeto. Aqui fica o resumo e o índice das pesquisas;
> o detalhe de cada uma mora em `pesquisa/`.

## Resumo

Bot de Discord para o servidor da guilda que joga **Ciclo Maldito**, o sistema de mesa de
Jujutsu Kaisen do Mizuki ([`cupcake-mochi/JJK---Project`](https://github.com/cupcake-mochi/JJK---Project)).
Ele tira dúvida de regra, corrige ficha e conversa na voz de uma personagem de Arknights.

## Objetivos

1. Consulta das regras do Ciclo Maldito pelo chat, citando a fonte.
2. Comandos de análise e correção de ficha.
3. Personalidade de uma personagem de Arknights, interativa no servidor.

## Estado atual

**Fase 0 (organizar a pasta) concluída** em 12/10/2026: `dados/sistema/` sincronizado com o
Ciclo Maldito v0.359 / R44. O código do bot (fase 1) ainda não começou: a personalidade
(fase 4) vem primeiro.

- **Kal'tsit** (plantão das 9h às 21h): card v0.13 em teste (naturalidade, 13/10), v1.2 = card v0.11 é a última congelada (`dados/personagem/kaltsit/VERSAO.md`).
- **Closure** (plantão das 21h às 9h): card v0.19, exemplos e vida feitos; pente fino em andamento; falta o teste no
  Gemini 3.8 Flash e congelar a v1 (`dados/personagem/closure/ESTADO.md`).
- **Crédito do Google AI Pro:** a ativação travou na conta de faturamento do Google Cloud
  (fim de `pesquisa/reports/Qual IA usar no bot.md`).

Pra retomar numa conversa nova: [`docs/PROMPT-CONTINUIDADE.md`](docs/PROMPT-CONTINUIDADE.md).
O plano completo está em [`docs/PLANEJAMENTO.md`](docs/PLANEJAMENTO.md) e
[`docs/PLANO-PERSONALIDADE.md`](docs/PLANO-PERSONALIDADE.md), e as decisões em
[`docs/DECISOES.md`](docs/DECISOES.md).

## Pesquisas

Cada pesquisa ganha um arquivo em `pesquisa/` e uma linha nesta tabela.

| Tema | Pergunta que responde | Status | Arquivo |
| ---- | --------------------- | ------ | ------- |
| Modelo próprio ou API; como alimentar o bot | Vale treinar/hospedar um modelo ou seguir em API? Como fazer a personagem soar natural e fiel ao original? | Concluída em 12/10/2026 (com pontos a conferir listados no fim do relatório) | [relatório](pesquisa/reports/Bot%20de%20personagem%20modelo%20ou%20API.md) · [notas](pesquisa/research_notes/Bot%20de%20personagem%20modelo%20ou%20API/) |
| Fontes multilíngues e método de fidelidade | Existe material das personagens de Arknights/Endfield em outros idiomas ou pt-BR? Qual a melhor metodologia para o bot soar como a original? | Concluída em 12/10/2026 (com pontos a conferir listados no relatório) | [relatório](pesquisa/reports/Fontes%20multil%C3%ADngues%20e%20m%C3%A9todo%20de%20fidelidade.md) · [notas](pesquisa/research_notes/Fontes%20multil%C3%ADngues%20e%20m%C3%A9todo%20de%20fidelidade/) |
| Outros personagens e traduções pt-BR | Quanto material existe dos outros personagens? Alguém já traduziu algum para pt-BR? | Concluída em 12/10/2026 | [relatório](pesquisa/reports/Outros%20personagens%20e%20tradu%C3%A7%C3%B5es%20pt-BR.md) · [notas](pesquisa/research_notes/Outros%20personagens%20e%20tradu%C3%A7%C3%B5es%20pt-BR/) |

Validação das três pesquisas (12/10/2026): [pesquisa/validacao/](pesquisa/validacao/).

Já confirmado na fonte: Endfield tem texto oficial em pt-BR (vozes só CN/EN/JP/KR); a Closure é operadora jogável no servidor CN desde 01/05/2026 07:00 no horário da China, que é 30/04 às 20:00 em Brasília (global ainda sem data) e as falas de operadora dela existem só em chinês. As falas dela na história (1.557 em EN/JP/KR, 2.096 em CN) estão extraídas em `dados/corpus_closure/`.

## Estrutura de pastas

| Pasta | O que vai nela |
| ----- | -------------- |
| `docs/` | `PLANEJAMENTO.md` (fases), `DECISOES.md` (o porquê de cada decisão) e especificações. |
| `pesquisa/` | Relatórios e notas de pesquisa, uma por tema, com fonte e conclusão. |
| `referencias/` | Material de terceiros: PDFs, links salvos, documentação. |
| `dados/sistema/` | **Cópia gerada** das regras do Ciclo Maldito. Não editar; atualizar pelo `ferramentas/sincronizar.py`. |
| `dados/ficha/` | Contrato da aba oculta da ficha e fichas de teste. |
| `dados/corpus_closure/`, `dados/corpus_kaltsit/` | Falas das personagens extraídas do jogo (história, ficha de operadora, Loja) e os bancos sem lore. |
| `dados/personagem/` | Card, exemplos e lorebook da personagem do bot. |
| `ferramentas/` | Scripts de apoio, como o sincronizador. |
| `src/` | Código do bot. |

## Legado

O material anterior está em [`../Closure Legado/`](../Closure%20Legado/) e não é
alterado por este projeto — serve só de consulta:

- `closure_lab.py` — bot de Discord (discord.py + Gemini) para fichas de
  *Feiticeiros & Maldições*, hospedado na Discloud.
- `closure_lab.db` — banco SQLite do bot.
- `discloud.config`, `requirements.txt` — configuração de deploy e dependências.
- `Feiticeiros & Maldições - Livro de Regras v2.5.2 - Polido.pdf` — livro de regras.
