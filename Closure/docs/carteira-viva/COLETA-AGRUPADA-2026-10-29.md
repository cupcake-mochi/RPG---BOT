# Coleta de faixas em lotes

29/10/2026 · PR 84 · checkpoint para desligamento solicitado pelo usuário.
Implementação e testes direcionados salvos; revisão final, CI completo e prova
nativa do agrupamento ainda pendentes. Criação continua bloqueada.

## Mudança

LeitorGradeRest aceita agrupar=True somente no backend; padrão False preserva a
leitura individual. Apenas o serviço de diagnóstico ativa os lotes nesta rodada.
Financeiro e auditoria existentes continuam usando pagina individual.

Cada lote tem até quatro faixas consecutivas, sem sobreposição, com soma de até
4.096 células. Um GET usa ranges repetidos, campos e teto HTTP de 4 MiB existentes.
Acesso atual/cota/acesso e pós-checagem continuam em cada HTTP, com versão Drive
antes/depois do GET. Não há TTL de autorização, cache entre GETs, adoção de versão,
aumento de cota, retry ou fallback silencioso após resposta grande/429/inválida.

Toda resposta é validada antes de entregar o prefixo: identidade do arquivo,
abas/dimensões, âncoras exatas, blocos ausentes/duplicados/estranhos e limites.
A ordem retornada pelo Google é normalizada para a ordem original do plano.
Páginas mantêm identidade, cobertura e hashes lógicos; a linha 5.000 é preservada.
O iterador é fechado explicitamente ao interromper e reconfere o prazo entre
entregas do mesmo lote. Nenhum schema, endpoint ou permissão nova.

A API permite múltiplos ranges: https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/get
Offsets dos blocos: https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/sheets#GridData

## Verificação já realizada

- 164 testes direcionados aprovados em 76,131 s, incluindo grade, diagnóstico,
  serviço, conferência e financeiro; mais um teste de expiração entre páginas
  do mesmo lote, aprovado em 0,027 s. 165 casos distintos, 27 novos.
- A/B com HTTP fictício, mesma progressão e mesmo resumo: 253→109 chamadas totais,
  Sheets 18→6, Drive 42→18, membro 188→80. É redução simulada de chamadas, não
  medição de velocidade real. As oito páginas continuam comparadas.
- Leitura individual/agrupada comparadas, respostas reordenadas, falha no último
  bloco, privacidade/acesso, cota, 429, tamanho, cancelamento e limites cobertos.
- Fixtures passaram a representar múltiplos ranges; duas expectativas de número
  de GETs foram atualizadas mantendo a contagem das faixas lógicas.

## Retomar

1. Conferir remoto, branch codex/carteira-viva-etapa-7, PR 84 e topo da fila.
2. Conferir CI do commit deste checkpoint. Os 1.593 anteriores validam 10df9c2,
   não o agrupamento. Não declarar suíte completa aprovada antes de ler o resultado.
3. Revisar parser/limites/fechamento do iterador. Comando direcionado em Closure/src:
   ../.venv/bin/python -m unittest testes.test_carteira_grade_lotes testes.test_carteira_grade_inicializacao testes.test_carteira_diagnostico_grade testes.test_carteira_diagnostico_servico testes.test_carteira_conferencia_inicializacao testes.test_carteira_financeiro_rest
4. Prova nativa agrupada exige fonte descartável e grant novos. Não reutilizar a
   fonte na lixeira ou o grant revogado do relatório NATIVO-DIAGNOSTICO-2026-10-28.
   Comparar apenas o escopo realmente lido; nenhuma prova financeira nova ocorreu.
5. Só depois avaliar uso no financeiro/auditoria. Propriedades, demais domínios,
   concorrência, preservação e prova integral continuam pendentes; etapas 8–10 também.

Nenhum novo ensaio autenticado, modelo pago, oficial/jogador/produtor alterado,
merge ou Discloud. Sem recursos de piloto novos nesta rodada. Sol Alto; revisão Médio.

Pacote ignorado regenerado/verificado: 90 arquivos, CRC/fontes iguais,
sem Carteira/env/bancos/campanha; SHA256 `2cd99a32b3f01391eea5e717b8683bba8c55e704261ceab423ddd9fee86816c9`. Não publicado.
