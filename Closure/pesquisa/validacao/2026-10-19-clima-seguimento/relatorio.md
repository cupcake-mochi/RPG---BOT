# Continuação de clima e pergunta inteira no comando

A captura do usuário mostrou dois fluxos que ficaram fora da bateria anterior:
“E de BH?” depois da pergunta sobre SP e
“GC:clima E como tá o clima de Belo Horizonte?”. A correção anterior de
“clima atual de X” não cobria esses caminhos. O teste de cidades não certificava
continuações nem a extração do argumento do comando. Isso está corrigido nesta
rodada, sem atribuir o novo caso a timeout de modelo.

## Evidência e causa

Logs de 18/10: às 23:58:18, SP teve contexto meteorológico disponível; o Gemini
expirou, a Vertex respondeu às 23:58:45. Às 23:58:51 houve seguimento e resposta
da Vertex às 23:59:02, sem consulta de clima entre eles. A captura mostra a
resposta admitindo não ter olhado BH. O texto do usuário não é copiado aos logs.

O reconhecedor aceitava apenas “e em/no/na …”; “e de …” ficava sem dados.
O comando passava o argumento inteiro para a geocodificação, tratando a frase
como nome de cidade. Três regressões novas falharam no código anterior, em dez
subcasos/asserções (`regressao-antes.log`).

## Implementação

- `pergunta_clima` resolve a pergunta explícita ou a continuação curta, com
  vocativo opcional, ancorada no começo e dependente do assunto meteorológico.
- A conversa recompõe essa sequência dos turnos existentes: várias trocas de
  cidade funcionam; uma fala de outro assunto encerra a sequência. Não há novo
  estado persistido, banco ou migração; expiração e exclusão continuam iguais.
- `/clima` e `GC:clima` aceitam cidade simples, pergunta inteira ou troca curta
  de cidade, extraindo somente o local antes da geocodificação. Comando já
  declara assunto meteorológico; não requer conversa anterior nem modelo.
- Apelidos, geocodificação, cache, fontes de mundo/Shiki, B47, mídia, cards,
  fila/custo e prazos de modelos preservados. Nome completo e alias continuam
  com chaves de geocodificação distintas; uma expectativa inicial de teste
  pressupunha compartilhamento entre elas e foi corrigida para o comportamento
  existente, sem tornar a leitura permissiva ou alterar cache.

Passaram 100 testes direcionados de clima/Discord, também 100 no código
extraído do ZIP, incluindo as três regressões. Suíte completa e publicação
serão registradas após conclusão. Ensaios sem IA;
não certificam a resposta generativa final nem disponibilidade futura das APIs.
