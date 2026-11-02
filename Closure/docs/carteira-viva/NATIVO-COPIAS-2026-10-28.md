# Cópia real após perda de resposta

28/10/2026 · etapa 7B, PR84 em rascunho. **Sem publicação.**
Código ensaiado: `9cb8a84a9afa151c26fd1c5eeed829c6312651db`.
Nenhum código mudou nesta rodada; o fechamento é somente documental.

## Escopo e acesso

O Drive conectado preparou um modelo privado DESCARTÁVEL a partir da oficial
Ciclo Maldito. O Google confirmou propriedade pessoal e permissão única de
proprietário, sem compartilhamento. Somente esse modelo foi escolhido no Picker
do OAuth próprio das Guias. Não usar a cópia preparatória como prova de que
`Consultas.copiar_modelo` funcionou: a prova do método está separada abaixo.

O pedido específico para autorizar `drive.file`, selecionar apenas essa
DESCARTÁVEL e criar uma segunda cópia recebeu a confirmação humana “Pode seguir”.
A autorização não depende de responder pelo formulário de perguntas: a resposta
textual direta ao pedido concreto também vale. Não foi necessário pedir outro ok.
A solicitação local anterior expirou antes de concluir o Google; uma nova entrada
foi aberta com os mesmos cliente/escopo/conta e finalidade. A conexão foi confirmada
com nome fictício em uma base nova, sem reutilizar cadastro/campanha reais.

O modelo foi configurado **somente no banco do piloto**, usando a identidade e
os privilégios atuais observados no Discord. Isso não altera a configuração do
bot em produção. O serviço local, no loopback, invocou o método interno de cópia
com fila/cotas, worker e renovação OAuth reais. Não houve comando/rota pública
nova, Gateway adicional, serviço Google/escopo/intent novo ou chamada de modelo.

## Um POST, resposta perdida

A primeira chamada terminou em **23,411 s**, com `ErroProvedor/copia_incerta`.
A instrumentação registrou uma tentativa de POST Drive, sem uma resposta HTTP
correspondente. O serviço já havia gravado `enviada` antes de fazer a requisição.

O executor de ensaio estava preparado para descartar deliberadamente uma
resposta HTTP200, mas **essa injeção não aconteceu**: não havia resposta para
descartar. A perda foi observada no transporte real. O limite HTTP é de 15 s;
o tipo original da exceção de rede não foi retido, portanto não afirmar uma
causa de rede mais específica a partir do código genérico.

Na fase de cópia, separada da conexão/preparação:

| Requisição | Tentativas | Respostas registradas |
|---|---:|---|
| Discord: membro | 10 GET | 10 HTTP200 |
| Discord: servidor | 10 GET | 10 HTTP200 |
| Discord: cargos | 10 GET | 10 HTTP200 |
| Google OAuth | 1 POST | 1 HTTP200 |
| Drive: versão da origem | 1 GET | 1 HTTP200 |
| Drive: copiar | **1 POST** | **Nenhuma** |

São 33 tentativas e 32 respostas HTTP200. Não chamar a ausência de resposta de
HTTP200 recebido pelo produto nem afirmar que nenhum arquivo foi criado.
Nenhum POST de repetição foi enviado nessa chamada.

## Reinício e reconciliação

O piloto foi encerrado, a porta liberada e o serviço reiniciado com o mesmo
banco/chave. A conexão confirmada foi reutilizada, sem novo consentimento Google.
A mesma identificação de pedido abriu o diário `enviada`.

A retomada encontrou um único candidato pelos três marcadores privados do app,
observou esse destino e reconferiu a versão do modelo. Terminou em
**21,293 s**, com **zero POSTs Drive**:

- 45 GETs Discord: 15 de membro, 15 de servidor e 15 de definições de cargos;
- um POST Google OAuth para renovar a concessão cifrada;
- três GETs Drive: busca, metadados da cópia e versão do modelo;
- **zero GETs Sheets** nessa fase.

As 49 respostas da reconciliação foram HTTP200. A preparação do processo
reiniciado teve outros seis GETs Discord, contados à parte. Não houve injeção
na busca ou nos metadados: eram respostas reais do Google.

A identificação aceitou somente um arquivo diferente da origem, do tipo Sheets,
autorizado ao app, próprio da conta, privado, fora de lixeira/Drive compartilhado,
com permissão única de proprietário e marcadores corretos. A origem conservou
a versão fixada antes do envio. Um metadado independente pelo Drive conectado
confirmou o título genérico da cópia, a localização no My Drive e a privacidade.

Resultado do produto: `copia_identificada=true`, `inicializacao_concluida=false`,
`criacao_disponivel=false`. Não cadastrou a cópia nova como personagem e não
entregou uma ficha inicializada. A única cópia preparatória veio do conector;
o **único POST do método novo** gerou a segunda descartável encontrada na retomada.

## Revogação e limpeza

Depois de salvar as contagens, o piloto foi desligado. A concessão Google do
ensaio foi revogada, com HTTP200. Essa revogação afeta o acesso dessa conta ao
projeto, não apenas um arquivo; não alterou o token/segredo do bot Discord.

Uma nova tentativa do mesmo pedido recebeu HTTP400 no OAuth e o provedor
retornou `revogada`: nove GETs Discord, um POST OAuth e **zero GET/POST Drive**.
O diário anterior não foi servido como acesso atual e não houve nova cópia.
A exclusão global dos dados fictícios foi aplicada apenas na base exclusiva
do piloto. Estado final: zero personagens, zero conexões ativas, zero segredos
de conexão e zero diários de cópia; integridade `ok` tanto no cadastro quanto
no ledger. Registros mínimos de remoção/auditoria não são chamados de apagados.
A porta 8876 ficou livre.

Para limpar os arquivos pelo Drive, a cópia gerada foi movida do My Drive para
a mesma pasta privada do modelo descartável; metadados relidos confirmaram o
novo pai e a permissão única do proprietário. Só então os **dois arquivos de
ensaio** foram selecionados e enviados à lixeira recuperável. A interface
confirmou “2 itens movidos para a lixeira”. Não esvaziou lixeira nem alterou
outras planilhas, permissões ou pastas. As abas criadas para o teste foram fechadas;
a aba original do usuário foi preservada.

Nenhuma célula foi escrita, nenhuma rotina Apps Script foi executada e nenhuma
ficha oficial/de jogador foi alterada. Não abrir a cópia no editor Sheets como
se isso fosse inspeção neutra de automações: o ensaio ficou em API/Picker/Drive.
Configuração privada, banco, IDs pessoais/temporários, credenciais, tickets e
capturas de consentimento ficam fora do Git e do pacote.

## O que este ensaio ainda não comprova

- Limpeza do conteúdo herdado, diário de escrita de células ou pós-estado de
  financeiro/progressão. O contrato de inicialização continua incompleto no serviço.
- Preservação e ativação do Apps Script, propriedades, recálculo/arte, automações,
  treinos/notas e novo responsável. `files.copy` bem-sucedido não certifica esses itens.
- Restore de backup com Google real, destinos compartilhados/duplicados reais,
  outro jogador/revisor/administrador, carga ou criação pública. Esses casos
  continuam distintos dos testes offline e da revisão integrada posterior.
- Disponibilidade universal: a primeira chamada perdeu resposta; a recuperação
  foi segura, mas não existe promessa de rede sem falhas ou de exatamente uma
  entrega. Não aumentar os prazos comuns nem repetir POST para esconder incerteza.

O caminho observado de cópia/recuperação da **7B** tem agora prova nativa.
Próximo: **7C**, diário de escrita restrito ao contrato e reconciliação do
financeiro em uma nova descartável; depois demais domínios/preservação e prova
integral (**7D**). `criar_por_modelo` continua incondicionalmente bloqueado.
Etapas 8–10 continuam na fila. Sol Alto para implementar; Médio para revisar.

## Git e testes

O [CI 40772021442](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40772021442)
do código ensaiado passou em 28/10 às 18:32:26 Brasília: **1.486 executados,
1.485 aprovados e um opcional pulado**, zero falhas, 300,149 s. A prova nativa
não acrescenta casos unittest a essa contagem. Não repetir suíte ou regenerar ZIP
por este relatório; não houve alteração de código após aquele CI.

Branch `codex/carteira-viva-etapa-7`, PR84 dependente da PR83. Main remota do
bot reconferida `de424478a7a120ecb43bd0c79eb93774d446fae6`. Produtor PR31 intacto.
Sem merge ou publicação; o código da Carteira continua fora da Discloud e do
pacote do bot de conversas. Este registro não certifica o estado instalado.
