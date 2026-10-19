# Clima de BH — frase atual e silêncio por timeout

O usuário relatou que a última tentativa, “qual o clima atual de bh?”, ficou
sem resposta e pediu conferir os logs. A autorização anterior de atualizar a
Discloud após correções permanece válida nesta continuação.

## Dois problemas separados

1. Logs de 18/10/2026: gatilho da Closure às 23:39:43; Gemini sem resposta em
   12 s, depois Vertex sem resposta em 60 s; última mensagem 1561569509192761365
   encerrada sem fala às 23:40:56. Não houve traceback de clima. Os logs não
   guardam o texto da pergunta, portanto a associação é com a última tentativa
   indicada pelo usuário. A reserva cautelar de US$ 0,056834 é consumo incerto,
   **não uma cobrança confirmada**. `logs-tentativa.txt`.
2. Reprodução determinística da frase exata: o gatilho reconhecia clima, mas
   não extraía BH porque “atual” separava clima de “de”. A cidade ausente
   disparava a leitura padrão de Tóquio. O apelido BH → Belo Horizonte,
   corrigido em 14/10, continuava presente e funcional; esta construção não
   estava coberta. `regressao-antes.log`: três testes novos falham (oito
   asserções/subcasos) no código anterior, sem erros de preparação.

A correção permite marcadores temporais atual/hoje/agora antes de de/do/da
quando ligados ao assunto clima/temperatura/tempo. O recorte continua limitado
à frase da pergunta e não extrai “preciso de ajuda”. Uma linha de log informa
cidade selecionada e disponibilidade da leitura, sem copiar a mensagem ou
adicionar chamadas de rede. Apelidos, cache, painel diário e `/clima` preservados.

Os prazos, a fila e o comportamento de silêncio quando todos os modelos falham
não foram alterados. Não se atribui o timeout à falha do extrator: são etapas
separadas. `/clima lugar:BH` e `GC:clima BH` usam os dados diretamente, sem modelo.

## Validação

- 95 testes direcionados de clima e camada Discord passaram; três novos testes
  incluem sete construções de frase, geocodificação/coordenadas e passagem do
  dado correto para as duas guias, com rede/modelo simulados.
- 35 testes passaram usando o código extraído do ZIP, incluindo o comportamento
  já estabelecido quando o modelo não responde. `testes-pacote.log`.
- Consulta real gratuita na Discloud antes da publicação: a frase com “atual”
  ainda devolvia lugar None; “qual o clima de bh?” recuperou Belo Horizonte em
  **1,048 s**. Assim se confirmou que a API estava acessível na hospedagem
  durante essa verificação; o acesso local havia expirado sem resposta.
  `clima-remoto-antes.txt`. Nenhuma chamada de IA ou mensagem ao Discord.
- Pacote conferido contra os fontes: 67 arquivos; **somente
  src/closure_bot/clima.py mudou desde a v2 publicada**. Núcleo de mundo,
  B47, memória, mídia, cards, aprovações e configuração preservados.
  `pacote.json`. ZIP sem credenciais, bancos ou cadastro de campanha.

A suíte completa terminou: **844 executados, 843 aprovados e um online opcional
pulado**, 306,847 s, sem falhas/erros. `suite-completa.log`. Cópia sincronizada
dos fontes no runtime local com as mesmas dependências, sem dados de produção.
O fechamento da publicação será registrado após a conferência remota.
Os testes simulados não certificam disponibilidade externa nem qualidade de
resposta generativa. Não foram feitas chamadas pagas ou mensagens de teste.
