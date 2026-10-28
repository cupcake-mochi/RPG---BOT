# Permissões com menos consultas

28/10/2026 · etapa 7 parcial, PR84. Não publicado. Criação bloqueada.

## Mudança

O fluxo anterior buscava membro, servidor e definições de cargos em cada
contexto, mesmo quando o banco já autorizava a leitura por ser o dono da ficha
ou por um cargo explícito de revisão. O perfil simulado maior fez 1.686 GETs
Discord para 183 GETs Google.

`Provedores.membro_para_leitura` sempre faz um GET novo do membro e recebe um
callback **interno do backend**. O Membro básico contém identidade, participação
e IDs dos cargos atuais, sem flags de Administrator/dono/gerenciar servidor.
O banco verifica a referência, o acesso à ficha, as revisões e o contexto da
operação com esse Membro. Só um resultado booleano True permite usar o básico.
Não aceita flag, Membro, cargo ou callback enviados por cliente HTTP/Discord.

A regra de leitura já permite dono OU cargo revisor explícito OU Administrator
OU dono do servidor. Quando dono/cargo explícito bastam, buscar privilégios
adicionais não mudaria a autorização. Se o básico não permite, o provedor
consulta servidor/definições de cargos e calcula os privilégios como antes,
usando a mesma resposta atual do membro, sem GET duplicado.

Não há cache, TTL ou reutilização de autorização. Todos os pontos de observação
foram conservados, inclusive fila, antes/depois da cota/rede e entrega por cliente.
Acesso básico negado pode exigir prova completa; conflito de fonte/contrato,
prazo, erro de API ou dado inválido não vira permissão. A comprovação completa
é novamente validada no banco. `membro()` comum segue sempre com três consultas.
Payload de membro/roles malformado recusa antes de chamar a prova básica.

## Medição controlada

Mesmo cenário de dono, 5.000 linhas, contrato real e HTTP externo simulado:

| Requisições | Antes | Depois |
|---|---:|---:|
| Discord GET | 1.686 | 578 |
| Google GET | 183 | 183 |
| Reserva de cota Google | 183 | 183 |
| OAuth POST | 1 | 1 |

Redução Discord: **65,72%**. O serviço da base `16a36b3` foi executado no mesmo
cenário; o teste do orçamento falhou antes e passou depois. Os resultados
mecânicos permaneceram sem erros e todos os indicadores de liberação falsos.
A instrumentação repete um cenário já contado nos testes, sem somar teste novo.
Não mede latência, custo ou cotas nativas.

O ganho vale para dono da ficha/cargo explícito. Administrador ou dono de servidor
que precise dessas prerrogativas continua com a observação completa de três
requisições; essa permissão não exige configurar cargo adicional no bot.
O revisor que perde o cargo, mas mantém Administrator, continua por prova completa.

## Testes e continuação

18 novos: observação atual/flags, fallback completo, payload inválido, erro/limite
sem reusar sucesso, booleano estrito, contexto em conflito, dono/revisor,
Administrator/dono de servidor alterados durante cota, cargo retirado no banco,
fonte trocada, entrega após perda de acesso e transição de cargo para admin.
17 passaram no lote em 34,633 s; o adicional de transição em 5,688 s.
44 regressões de serviço/provedores em 67,995 s e 82 de consultas/web/modelos
em 39,085 s: **144 testes locais distintos**, zero falhas finais.
Suíte completa aguardando CI desta rodada.

Nenhuma guarda de leitura foi removida, nenhum escopo/intent/acesso novo, schema
ou endpoint. Sem conta real, escrita Google, modelo pago, merge ou deploy.
Produtor PR31 intacto; main bot de42447/produtor ef361cc reconferidas.

Próximo: prova integrada pelo OAuth próprio das Guias em uma cópia descartável,
medindo cotas/latência e preservando todos os bloqueios. Incluir dono, cargo
explícito, administrador e resposta 429, sem tratar contador simulado como prova
nativa. Retomada é leitura histórica, não inicialização. Depois permanecem cópia/
diário de escrita com reconciliação, propriedades e demais domínios, preservação
global/arte, automações/treinos/notas/responsável. Não liberar criação pelo CI.
Sol Alto para integrar/ensaiar; Médio para revisão focal.

Pacote ignorado regenerado/conferido: 90 arquivos, CRC e bytes dos fontes iguais,
sem env/Carteira/bancos/campanha, não publicado. SHA256
`ac8202500f18821d426670108101f315a01d985221405a175ceb023faac95b95`.
