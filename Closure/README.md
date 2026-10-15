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
Ciclo Maldito v0.359 / R44, e em 14/10 com o v0.364 / R51 (511 blocos). O esqueleto da fase 1 está em `src/closure_bot/` (13/10): o chat
responde e já roda na Discloud; os detalhes de execução ficam em `src/LEIA-ME.md`.

- **Kal'tsit** (plantão das 9h às 21h): card v0.30 aprovado e aplicado localmente em 14/10; histórico em `docs/DECISOES.md`.
- **Closure** (plantão das 21h às 9h): card v0.37 aprovado e aplicado localmente em 14/10, com exemplo de explicação inteira de habilidade.
- **Lorebook** v2.0 (97 entradas), com o livro R51 e os ajustes de busca de 14/10, na página montada localmente (`ferramentas/pagina_teste/`).
- **Consulta do livro (busca v10, 15/10):** nomes exatos prevalecem sobre palavras parecidas; confirmações conservam a fonte por até seis mensagens anteriores. Recomendações recebem um panorama literal dos Caminhos/Trilhas, incluindo o treino com armas da Parceria. A personalização da Origem conserva a permissão e a escolha padrão juntas. Auditoria local encontrou a fonte esperada nos 425 títulos únicos, sem avaliar respostas do modelo. [Revisão e limites](pesquisa/validacao/2026-10-15-consulta-livro-v10/relatorio.txt). Os cinco testes no Discord de 14/10 pertencem à busca v9; a v10 ainda precisa dessa confirmação.
- **Discloud (14/10):** Mizuki confirmou as regressões antigas, cinco perguntas de regra e os quatro painéis ANALISE 2 no Discord. O painel paginado também foi confirmado por ele às 23h05.
- **Painel de ficha (14/10):** resumo e páginas por assunto, seletor direto e botões primeira/anterior/próxima/última com emojis padrão. Controles públicos por dez minutos; encerrados, a mensagem volta ao resumo. Buffs identificados, números agrupados e detalhes longos repartidos sem perder itens. Sem modelo na análise ou na navegação.
- **TR, perícias e carga (15/10):** ANALISE formato 4 com 5.381 chaves, preservando as 4.896 anteriores. Bônus e quantidades refeitos das escolhas; ajustes ficam para o mestre. Carga usa o catálogo do livro e posições completas; fórmula legada exata vira pendência amarela. Página própria no painel. Formato 3 reservado ao trabalho de CONFIGURAÇÃO, ainda sem integração. [Revisão e testes](pesquisa/validacao/2026-10-15-ficha-tr-pericias/relatorio.txt).
- **Equipamento e trunfos (15/10):** requisitos de Força/patente, Defesa com armas reconhecidas, ataque armado e bônus de resolução das entidades; extras da Principal separados e trunfos da domada pelo nível dela. Reserva Profunda distingue o acréscimo do livro do Buff legado. Carga pessoal sem entradas completas permanece não certificada. Esta foi a etapa anterior a TR/perícias; CONFIGURAÇÃO segue no outro chat. Relatório em `pesquisa/validacao/2026-10-15-ficha-equipamento-trunfos/relatorio.txt`.
- **Repertório e Talentos (14/10):** capacidade recalculada pela progressão, aplicações gratuitas de Leque/Coexistência separadas das vagas comuns, Talentos por Categoria/nível, Regra Própria e Domínio pelo custo total atual e entidades por espaço conhecido. Concessões de Talentos pela Origem sem vinculação ficam por possibilidades, sem certificar o total. Relatório em `pesquisa/validacao/2026-10-14-ficha-repertorio/relatorio.txt`.
- **Contas de feitiço (14/10):** alcance/área e tipo de resolução conferidos, totais de Apoio/Cura e limites da Onda ampliados; Controle, Remate e Alma com verificações adicionais. Distribuição, texto e permissões continuam explícitos como revisão manual. Divergências exatas do gerador recebem pendência, sem certificar o valor. Detalhes em `pesquisa/validacao/2026-10-14-ficha-efeitos/relatorio.txt`.
- **ANALISE 2 (14/10):** 4.896 chaves, preservando as 2.650 antigas. Quatro cópias preenchidas e calculadas no Google cobrem Fundamento/Classe 0/Máxima, domada com Buff, criação/Principal e Kaori anterior com feitiços. Conferência de Famílias, números das entidades e Talentos ampliada; as quatro cópias foram aprovadas também no Discord. Cobertura e limites em `pesquisa/validacao/2026-10-14-analise-v2/relatorio.txt`. Argon congelado; CONFIGURAÇÃO segue no outro chat.
- **Proposta compacto v3 (14/10):** revisão pontual de identidade, fatos pessoais, gênero e cuidado; textos e perguntas inéditas preparados, sem API ou ativação. 228 testes locais passaram. A melhoria de comportamento ainda precisa de medição. [Proposta](pesquisa/propostas/compacto-v3/revisao.txt) · [Prompt de revisão no Claude](docs/REVISAO-CLAUDE-ARGON.txt).
- **Compacto v2 (14/10):** 12 pares completos; Argon com média US$ 0,00499 e mediana 3,54 s, Flash compacto US$ 0,00187 e 18,86 s, com créditos promocionais estimados. Argon foi melhor na recusa de tarefa embutida; Flash compacto teve regressão e não foi liberado no bot. V2 opcional só para Argon, desligada; Flash original continua padrão. 222 testes locais passam. [Resultados e limites](pesquisa/validacao/2026-10-14-compacto-v2/relatorio.txt).
- **Argon compacto experimental (14/10):** redução medida de 54% no custo do Argon nos mesmos casos; cerca de 19% acima do Flash da rodada anterior, com qualidade ainda desigual. Modo misto por canais, limite separado e perfil opcional preparados, desligados. [Revisão e resultados](pesquisa/validacao/2026-10-14-argon-compacto-v1/relatorio.txt).
- **Argon original no chat (14/10):** integração validada na Vertex global, com `low`, saída limitada a 4096 e Flash de reserva. Reflexão permanece no Flash. Em 17 pares completos, Argon custou 2,64× o Flash; Flash continua padrão. [Relatório e respostas](pesquisa/validacao/2026-10-14-argon/relatorio.txt).
- **Teste 4 — Corpo Amaldiçoado (14/10):** leitura real confirma PE 40 (36 + 4 de Núcleo Dependente). O bot agora avisa que essa menor não possui barra de Integridade, em vez de certificar os 60 calculados pela ficha. 277 testes: 276 passaram, um online opcional pulado. Planilha preservada; reteste posterior confirmado pelo Mizuki na Discloud.
- **Regressões da ficha (14/10):** Defesa fixa distingue zero, fórmula normal pendente e valor adulterado; notas do mesmo treino extra são agrupadas. Sem nome, o painel usa Caminho e nível conferidos. 275 testes executados: 274 passaram e um online opcional foi pulado. [Fila e validação](dados/ficha/TESTES-FICHAS-14-10.md).
- **Fase 3, correção de ficha (14/10):** o bot lê a aba oculta `ANALISE` da ficha (pelo `.xlsx` ou pelo link), refaz vida, PE, Integridade, proteção e Defesa pelo livro, confere Caminho, Trilha e Origem e junta os avisos da ficha. As contas básicas batem em quatro casos, incluindo a Kaori do livro. O comando `/ficha analisar` responde com um painel no canal e está ligado desde 14/10; magia e entidades receberam conferência parcial ampliada pela ANALISE 2. Divergências da ficha com o livro em [`dados/ficha/DIVERGENCIAS-FICHA.md`](dados/ficha/DIVERGENCIAS-FICHA.md). [Contrato da ANALISE](dados/ficha/CONTRATO-ABA-BOT.md).
- **Crédito do Google AI Pro:** ativado em 13/10/2026; a Vertex já respondeu com os cards
  atuais (fim de `pesquisa/reports/Qual IA usar no bot.md`).

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
