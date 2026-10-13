# Validação da pesquisa 2: "Fontes multilíngues e método de fidelidade"

> 12/10/2026. Legenda: ✅ confere · 🔼 confirmado agora · ✏️ corrigido · ⚠️ continua aberto.

| # | Afirmação | Resultado | Como conferi |
|---|---|---|---|
| 1 | Closure tem 1.557 falas em EN/JP/KR e 2.096 em CN | ✅ | recontagem no corpus salvo |
| 2 | EN, JP e KR alinham arquivo a arquivo | ✅ mesmos 77 arquivos e **mesma contagem em cada arquivo** nos três | script sobre `dados/corpus_closure/` |
| 3 | O CN alinha com o global nos arquivos em comum | ✅ 77 de 77 arquivos com a mesma contagem; o CN só tem arquivos a mais | idem |
| 4 | Lançada no CN em 30/04/2026 | ✏️ as duas datas valem. O evento Critical Phase Transition (`act4mainss`, 相变临界) começa em 01/05/2026 07:00 no horário da China = 30/04 20:00 em Brasília. README, relatório e nota ajustados | `activity_table` do CN |
| 5 | Global sem data ("TBA") | ✅ | wiki.gg, lista de lançamentos |
| 6 | 38 falas de operadora e 9 blocos de arquivo, só em chinês | ✅ | `charword_table` e `handbook_info_table` |
| 7 | Espelho do global parado em nov/2025 | ✅ último commit 13/11/2025 | git log do repositório |
| 8 | Endfield com texto pt-BR oficial, sem voz (Logrus IT) | ✅ | página da Logrus, 30/01/2026 |
| 9 | ChatHaruhi busca falas do roteiro por similaridade | 🔼 confirmado no PDF: cosseno, ~1.500 tokens de trechos | arXiv 2308.09597 |
| 10 | PersonaEval: LLM ~69% contra humanos 90,8% | ✅ (resumo) | arXiv 2508.10014 |
| 11 | CharacterEval: 13 métricas em 4 dimensões, CharacterRM com 12 anotadores | ✅ | arXiv 2401.01275 |
| 12 | Falas buscadas ficam em inglês no prompt | ✏️ virou questão aberta: contradiz o passo 3 da pesquisa 1. Decidir no teste cego | ver validação 01 |
| 13 | Closure não está no Endfield | ⚠️ continua sem fonte; nada achado a favor nem contra | — |
| 14 | END Wiki em português tem diálogo pt-BR | ⚠️ não conferido | — |
