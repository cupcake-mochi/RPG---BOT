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

## Publicação e conferência

Código **9a00097**, branch `codex/mundo-era-revolucao`, PR 66 em rascunho.
Commit aplicado no app existente 1773761486581; startup às **23:49:31 de 18/10**,
Brasília, online em cinco servidores e sem Error/Fatal. Mantidos 1.000 MB.
12/12 verificações passaram no console publicado; a frase exata do usuário
retornou Belo Horizonte na API real em **1,52 s**, sem modelo.
`console-publicado.txt` e `console-publicado.jpg`. Console desconectado ao final.

Backup posterior íntegro, privado e fora do Git: **67/67 arquivos iguais ao ZIP**.
.env, closure_lab.db e campanha idênticos. Dois bancos com quick_check ok e
esquemas idênticos. bot.sqlite3 mudou apenas pela expiração da conversa recente
e seus participantes e pela coluna estado do painel periódico; demais tabelas
idênticas. Não se sobrescreveu o banco para forçar igualdade.
`conferencia-publicacao.json` contém somente o agregado sem conteúdo privado.

ZIP: `entregas/closure-lab-clima-bh-2026-10-18.zip` na pasta de trabalho,
SHA256 `c984d01ee65f1c5fc741145f05b4368a6d4cbf35389efb8101b8a6117140bf46`.
Sem merge. Não repetir publicação por rotina. Uma nova resposta generativa
exige modelo disponível e orçamento de teste; não é certificada aqui.

## Ampliação pedida pelo usuário: outras cidades

A correção é gramatical, sem exceção especial para BH. Acrescentados dois testes:
**150 combinações**, 18 nomes completos e sete apelidos × seis construções.
São Paulo, Rio de Janeiro, Curitiba, Porto Alegre, Brasília, Florianópolis,
Manaus, Recife, Salvador, Natal, Fortaleza, Goiânia, Vitória, Lisboa, Londres,
Paris, Nova York e Saint-Étienne; apelidos sampa/sp/rj/cwb/poa/bsb/floripa.
Cada combinação verifica extração, consulta nominal esperada, coordenadas e
contexto resultante sem Tóquio. Quatro negativos cotidianos e a fronteira entre
frases também passaram. `matriz-cidades.log`, classe OutrasCidades.

Os mesmos 35 testes de clima passaram no código extraído do ZIP, com esses dois
testes novos incluídos (`cidades-no-pacote.log`). Nenhum código de execução mudou
após a suíte completa de 844; o total dessa suíte permanece o medido, separado
dos dois novos testes. O pacote publicado não precisou de outra implantação.

Os testes simulados não certificam disponibilidade externa nem qualidade de
resposta generativa. Não foram feitas chamadas pagas ou mensagens de teste.

**Verificação externa ampliada:** 8/8 consultas reais da frase “qual o clima
atual de …?” passaram na Discloud: São Paulo, rj/Rio de Janeiro, Curitiba,
poa/Porto Alegre, bsb/Brasília, Manaus, Lisboa e Tóquio. Tempos observados entre
0,014 s e 1,055 s; cada cidade consultada uma vez, sem repetir falhas, usando
apenas as APIs gratuitas de geocodificação/previsão. Não certifica a
meteorologia nem disponibilidade futura; confirma a recuperação da cidade e
o formato do dado atual naquele momento. `cidades-reais.txt` e
`cidades-reais.jpg`; script `teste-cidades-remoto.py`. Nenhum modelo ou mensagem.
Além disso, **97 testes de clima + integração Discord passaram sobre o código
do ZIP** após acrescentar a matriz (`cidades-integracao-no-pacote.log`).
Console desconectado. Não houve nova alteração de runtime ou implantação.
