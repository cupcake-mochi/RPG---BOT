# Coleta de faixas em lotes

29/10/2026 · PR 84 · checkpoint para desligamento solicitado pelo usuário.
Implementação, testes direcionados e CI completo aprovados. Revisão final e prova
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

## Fechamento e transferência · 29/10

Código `2f23f765e7d62cd2ff4ec31731bcaf7c1775061f`: [CI 40810907135](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40810907135)
aprovado em 29/10 às 00:19:49 Brasília: **1.620 executados, 1.619 aprovados, um
opcional pulado**, zero falhas, 360,438 s. Resultado conferido pelos logs completos
e pelo job; não apenas pelo selo da PR. Fechamento posterior só documental,
sem repetir suíte ou pacote. [Prompt para o Claude](CONTINUAR-NO-CLAUDE-2026-10-29.md).

## Retomar

1. Conferir remoto, branch codex/carteira-viva-etapa-7, PR 84 e topo da fila.
2. O CI do código 2f23f76 passou conforme registro acima. Conferir se houve
   commits posteriores antes de reutilizar essa evidência; os 1.593 anteriores
   validam apenas 10df9c2. Não repetir bateria extensa por mudança documental.
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

## Revisão final e preparo do ensaio nativo · 29/10 (Claude)

Revisados parser, limites, expiração entre entregas, cancelamento e buffers do
`LeitorGradeRest` agrupado, `DiagnosticoGrade` e `diagnostico_servico`.

**Defeito comprovado e corrigido:** `Provedores._json` deixava escapar
`RecursionError` cru quando a resposta, dentro do teto de bytes, tinha aninhamento
profundo (ex.: 200 mil colchetes). Agora vira `ErroProvedor('temporario')`, como os
demais JSON inválidos; `segredos.py` já tratava o mesmo caso. Regressão
`test_json_aninhado_dentro_do_teto_recusa_como_erro_do_provedor`: falha sem a
correção, passa com ela, e confirma um único GET sem retry. Suíte completa local
após a correção: **1.621 executados, 1.620 aprovados, um opcional pulado, zero
falhas**, 651,481 s (máquina local; o CI da PR é a referência oficial).

**Conferido sem defeito:** startRow/startColumn omitidos quando zero; resposta com
aba extra, faltante, renomeada ou redimensionada recusa; bloco ausente, duplicado ou
estranho recusa o lote inteiro antes de entregar prefixo; sobreposição e mesmo início
nunca dividem lote; teto 4 MiB igual ao da página individual; prazo reconferido antes
de cada entrega e de cada GET; `CancelledError` propaga e o diagnóstico descarta tudo;
`aclosing` fecha o iterador. Limite aceito e registrado: dentro de um lote, as páginas
2–4 são entregues logo após a pós-checagem do GET, sem nova reconferência de acesso
por página (o acesso foi conferido antes e depois do HTTP que as trouxe).

**Hipóteses que só o ensaio nativo decide** (o código falha fechado em todas):
H1 com vários ranges o Google devolve só as abas pedidas (provado só com um range);
H2 vários ranges da mesma aba chegam numa entrada com vários blocos `data[]`, como diz
a referência de GridData; H3 um GET de quatro faixas cabe nos 15 s de timeout.

**Ensaio preparado, não executado.** Kit privado fora do Git, pasta 700/arquivos 600
em `carteira-piloto/etapa7-coleta-agrupada-20261029`: gera banco/chave/token novos
sem imprimir valores, runner desacoplado do terminal (`setsid`/`nohup`) com estado,
PID e batimento a cada 5 s, registro por chamada sem URL/ID/token (categoria, status,
ms e número de faixas de cada GET Sheets), commit testado gravado no resultado,
escrita Drive/Sheets bloqueada no transporte, e limpeza adaptada da rodada anterior.
Critério de aceite na progressão: duas amostras 8/8, zero mudanças, quatro
indicadores falsos e **exatamente 6 GETs Sheets** (2 de metadados + 4 de quatro
faixas), contra 18 em 28/10. Falta o ponto externo: cópia descartável nova na conta
certa e login/consentimento/Picker feitos pela pessoa. Nenhum OAuth, cópia, grant ou
chamada Google desta rodada.

## Ensaio nativo · 29/10 — aprovado

Progressão agrupada em fonte descartável real: duas amostras 8/8, zero mudanças,
**6 GETs Sheets e 109 HTTP200** (contra 18 e 253 em 28/10), H1–H3 confirmadas, limpeza
completa. [Relatório](NATIVO-COLETA-AGRUPADA-2026-10-29.md).

## Medição financeira pronta para lotes · 29/10 (desligada no serviço)

Usos do leitor mapeados: o diagnóstico já agrupa nos dois domínios; leem página por
página `financeiro_plano.medir` (leitura antes da escrita financeira),
`conferencia_inicializacao.coletar_conferir` e `conferencias_banco` (auditoria).
Só o primeiro foi tocado.

`medir` passou a consumir `leitor.paginas()` com `aclosing`, conferindo que os índices
chegam em ordem; erro em qualquer página descarta a medição e não pede lotes seguintes.
**`financeiro_servico` continua criando o leitor individual**: o comportamento em uso
não muda. Quatro regressões novas: plano financeiro agrupado idêntico ao individual
(mesmos hashes e pedidos) com menos GETs; fórmula em EXTRATO para no lote dela sem ler
SALÁRIOS; versão alterada no segundo lote recusa sem plano; página fora de ordem recusa
e fecha o iterador. Suíte completa local: **1.625 executados, 1.624 aprovados, um
opcional pulado, zero falhas**, 673,442 s.

Divisão offline do domínio financeiro: livros com 5.000 linhas, 50 faixas → 37 lotes
(as faixas dos livros já enchem o teto de 4.096 células); livros com 200 linhas,
21 faixas → 6 lotes. O ganho fica nas 18 faixas pequenas das guardas.

**Para ligar no serviço** (trocar para `agrupar=True` em `financeiro_servico`) falta um
ensaio nativo do **diagnóstico financeiro** agrupado — leitura apenas, já implementado —
em descartável nova da mesma conta do consentimento, comparando com a leitura individual.
Auditoria segue individual até lá.

## Ensaio nativo financeiro · 29/10 — individual × agrupado iguais

Diagnóstico financeiro com a primeira coleta individual e a segunda agrupada: 25/25 páginas
nas duas, **zero diferenças**, páginas em 11 GETs Sheets contra 25. Primeira tentativa recusada
corretamente (`conflito` na conferência do modelo, cópia recém-criada ainda mudando).
[Relatório](NATIVO-FINANCEIRO-AGRUPADO-2026-10-29.md).
