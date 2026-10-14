# Polimento de perguntas e busca do livro (13/10/2026)

- `RELATORIO.md` e `proposta/`: rodada 1 (bateria de 59 perguntas, busca v2, lorebook proposto).
- `rodada2/` a `rodada8/`: uma proposta de busca por rodada (`proposta/busca_vN.js` + `aplicarN.py`), cada uma com `LEIA.md` (o que mudou e números) e `rodar.sh` (compara a página atual com a proposta em todas as baterias). A v8 é a mais nova.
- `bateria/`: bateria.json (59), holdout.json, holdout2 a holdout6 (holdout4, 5 e 6 escritas às cegas, por agente que só leu o livro), montar.js e avaliar2.py.
- `rodada2/bateria/`: buracos, conversas reais rotuladas (conversas.json, 200 falas), frases sem "?", casos das conversas 10 a 13 com histórico.
- `ferramentas/`: depuração da busca (porque.js, termos.js, causa.js).

Medida cega (busca da época, antes de ajustar em cima da bateria): holdout4 23/30, holdout5 29/38, holdout6 34/38.
