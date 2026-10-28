# Leitura com observação de versão

28/10/2026 · etapa 7 parcial, PR84. Não publicada. Main produtor ef361cc e
bot main de42447 reconferidas; criar_por_modelo continua bloqueado.

## Código entregue

`carteira_viva/leitura_temporal.py` é um coordenador interno em memória.
Recebe callbacks confiáveis para plano/página e contexto, nunca um endereço
ou função enviado pelo navegador. Ainda não está ligado a rota, comando ou
transporte de execução remota do produtor.

O fluxo observa a versão Drive antes/depois do plano e de cada lote. Todas as
observações precisam coincidir com a mesma versão inicial; uma diferença
invalida a rodada, sem adotar uma versão nova no meio. Uma observação adicional
fecha a leitura depois da última página. O número fica como texto, sem converter
para float; testes usam versão acima da precisão inteira do JavaScript.

Contexto inclui a autorização/fonte que o integrador deve reconferir em cada
espera; callback precisa devolver o mesmo hash de contexto confiável. Mudança,
negação, revogação ou resposta fora do protocolo impede o avanço. Isso não
substitui autorização real do servidor/Google nem a prova do código instalado.
O callback deve compor usuário, servidor, fonte/conexão/modelo e respectivas
revisões, sem receber essa afirmação do cliente. Essa composição/ponte permanece
uma etapa de integração, não um endpoint implementado neste módulo.

Uma trava local serializa avanços da operação. Repetir a última página aceita
revalida acesso/versão mas não lê outra nem avança duas vezes. Cancelamento ou
erro temporário não confirma progresso; a tentativa seguinte lê o mesmo lote
sob a versão original. Não há retentativas automáticas infinitas ou chamadas
pagas. A integração ainda deve usar fila/cotas e backoff do serviço.

Prazo padrão de 30 min, só configurável no código até 1 h; espera conta no prazo.
Não armazena token. Estado/contadores são transitórios; reinício do serviço exige
nova leitura, sem repetir limpezas. Não adicionar restauração de cursor enviado
pelo navegador. Persistência futura exigirá contexto/cifra/concorrência próprios.
Retorno público de progresso não contém arquivo, nome privado ou hashes internos.

Ao finalizar, `versao_drive_estavel_observada=true` significa apenas que não
houve diferença nas observações autenticadas. O resultado é histórico:
`consistencia_temporal_verificada`, imagens, conferência final e criação
continuam falsos. Cálculos externos podem mudar sem uma edição comum; não tratar
esse observador como snapshot do resultado de todas as fórmulas.

## Falha comprovada na leitura anterior

`Provedores.ler_analise` aceitava versão vazia, desde que fosse string igual nas
duas observações. Reproduzido offline na base 73c2914: retornou análise/versão
vazia depois de três GETs. Código atual recusa na primeira observação, sem pedir
ANALISE. Não alterar a expectativa para aceitar metadado incompleto.

Novo `Provedores.versao_arquivo` centraliza validação do ID, MIME, autorização,
lixeira e versão numérica textual de 1–30 dígitos, mantendo o transporte GET
oficial/Bearer, limites, timeout e ausência de redirecionamento anteriores.
O leitor existente agora usa esse mesmo método antes/depois. Sondagem de modelo
e demais funcionalidades não foram afrouxadas ou substituídas.

## Produtor e contrato de saída

Produtor [PR31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
2427024: plano e páginas de quatro perfis, sem gravar células ou propriedades.
Máximo 631 perfis em 158 páginas. O leitor anterior com checkpoint permanece
separado; não apagar ou migrar seu diário automaticamente.

A amostra em `src/testes/fixtures/carteira_conferencia_pagina_v1.json` foi gerada
pelas funções GS reais em VM e copiada sem edição. O teste Python aceita essa
saída. Não é chamada Google entre os repositórios, prova de autenticação nem
execução nativa do produtor. A implementação é rejeitada se campos, páginas,
assinaturas ou indicadores de liberação divergirem do contrato.

## Dependência real de execução

O escopo concedido continua `drive.file`. Não presumir que ele habilite
`scripts.run`: o Google exige implantação executável, projeto Cloud padrão
compartilhado e token cobrindo todos os escopos do projeto. As funções do
protótipo recebem objeto Spreadsheet interno, que também não é parâmetro JSON
remoto. Nenhum executável foi publicado, escopo ampliado ou consentimento pedido.

Para manter a permissão por arquivo escolhido, a próxima entrega deve adaptar
validação/estado à leitura Sheets REST/backend, ou preparar uma rota específica
de execução e suas permissões para decisão separada. Não habilitar criação,
usar credenciais da Arquivista ou trocar drive.file por acesso geral para
contornar essa dependência. Automação do produtor, responsável, isolamento e
prova nativa seguem pendentes junto de preservação global, arte e orçamento.

## Testes e pacote

24 testes novos + 47 de leitura/modelos: 71 direcionados locais aprovados,
com HTTP simulado. Incluem edição entre/durante páginas, conteúdo restaurado,
contexto/acesso alterado, erro antes/depois da leitura, cancelamento, concorrência,
prazo, limites/protocolo, ausência de vazamento e todos os 631 perfis em lotes.
CI completo em fechamento; esperado 1.338 executados com um opcional pulado.

Pacote ignorado regenerado sem .env: 90 arquivos, CRC íntegro, cada entrada
comparada aos fontes. Sem credenciais, bancos, cadastro de campanha ou Carteira;
SHA256 de276427fbfbf2a2b8e32c6cb2af8acd3fcf0d498e5e6b71f667cb0da1492eef.
O módulo novo continua fora do pacote/runtime publicado. Não houve deploy,
merge, Google/Discord real, escopo novo ou chamada de modelo nesta rodada.
Sol Alto para adaptador/integração; Médio para revisão focal.

## Fontes oficiais consultadas

- [Drive File.version](https://developers.google.com/workspace/drive/api/reference/rest/v3/files):
  contador crescente de alterações, mantido como string.
- [Proteção de conteúdo](https://developers.google.com/workspace/drive/api/guides/content-restrictions):
  não é registro imutável nem congela resultados calculados.
- [Execução Apps Script](https://developers.google.com/apps-script/api/how-tos/execute):
  requisitos de projeto, implantação, token e tipos de parâmetros.
