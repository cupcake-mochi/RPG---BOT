# Recuperar conferências de leitura

28/10/2026 · etapa 7 parcial, PR84. Não publicado. Criação continua bloqueada.

## O que foi implementado

`conferencias_banco.py` mantém no SQLite o resultado de financeiro e progressão,
nessa ordem. Usa uma fonte **já cadastrada** e sua autorização atual. Não cria
uma cópia nem atesta que o arquivo é descartável ou foi inicializado pelo bot.
Essa estrutura ainda não é o diário da futura criação/escrita.

Schema 7: uma operação por servidor/personagem, até 32 KiB cifrados, validade
absoluta de 30 minutos. Guarda referência, contexto, versão Drive inicial,
contrato fixado, recibos e resultados resumidos dos domínios completos. Não
guarda grade, entrada financeira, nota, token de acesso ou cursor de página.
Em claro ficam só as chaves de consulta, iniciador, ID aleatório da operação,
contador e horários. Conteúdo e metadados correspondentes são autenticados pela
cifra; copiar o envelope para outro registro ou estender o prazo em SQL recusa.

A referência vincula usuário, servidor, personagem, arquivo, conexão, revisão
e geração. O contexto também inclui a autorização Google e as revisões de
configuração/modelo do servidor. O contexto incorpora o ID aleatório da
operação: uma auditoria da rodada anterior não pode ser adotada na nova, mesmo
com arquivo/versão iguais. Outro membro, inclusive administrador, não
retoma a operação do iniciador. Membro/cargo atual deve ser reconfirmado pelo
adaptador do serviço; banco não substitui uma consulta ao Discord.

`conferir_dominio_persistido` usa o worker real `DadosAsync`, o transporte REST
e o auditor determinístico existentes. O callback externo reconfirma contexto;
o adaptador também consulta estado/prazo no banco antes/depois de cada GET e
após aguardar cota. Ao terminar, observa novamente a versão Drive, fecha a
conferência e só então grava o domínio numa transação. Bilhete/revisão antigos
não avançam duas vezes, inclusive com dois processos abrindo o mesmo SQLite.

## Interrupção e recuperação

1. Abrir o plano confiável e iniciar a operação com a versão Drive observada.
2. Ler um domínio inteiro; resultado só é persistido após a observação final.
3. Se houver falha antes do commit, esse domínio recomeça na primeira página.
4. Após reiniciar o processo, retomar com membro autenticado, renovar o OAuth
   em memória e revalidar contexto/versão antes da próxima leitura.
5. Um domínio já salvo não precisa ser relido para continuar o seguinte.
   Isso aproveita evidência **histórica**, sem provar um snapshot conjunto.
6. Mudança de arquivo, autorização, geração, configuração, modelo, contrato ou
   versão Drive impede continuar. Nunca troca a versão original silenciosamente.

Repetir/retomar não estende o prazo. Relógio anterior ao início também recusa.
Há descarte explícito apenas do histórico local; não limpa células, arquivo
Google ou diário do produtor. Operação nova não adota resultado antigo.
Não há endpoint, comando Discord ou criação liberados por esse adaptador.

## Exclusão, chaves e backup

Troca de fonte, reconexão, revogação e desconexão removem as conferências da
fonte. Exclusão do personagem remove por chave estrangeira. Exclusão global do
usuário remove também operações iniciadas como revisor de personagens alheios.
A manutenção apaga expiradas. A abertura reaplica o registro de revogações.
A rotação recifra o estado completo, sem recibo interno preso à chave antiga.

Reinício normal preserva a operação dentro do prazo. Backup local remove todas
as conferências da cópia antes de cifrá-la; uma restauração não recupera esse
trabalho nem dispensa uma nova consulta Google. Cadastros/conexões confirmados
continuam sujeitos às regras já existentes do backup e do registro de remoções.

## Validação e limites

Testes usam SQLite real, worker em thread e HTTP simulado, com a grade sintética
baseada no contrato público do produtor. Abrangem interrupção na página, reinício
entre domínios, revisão concorrente, versão alterada, confirmação final,
revogação/prazo durante cota, confidencialidade, exclusão, rotação e backup.
179 regressões existentes passaram em 26,592 s. A revisão encontrou reutilização
indevida de uma auditoria anterior ao descarte: caso novo falhou antes da
correção; vínculo ao ID da operação impede esse reaproveitamento. Os resultados
finais: 25 novos aprovados em 56,257 s; somados às 179 regressões, **204 testes
distintos locais**, zero falhas na versão final. Código `4f2122d1dfc44716adefd77392c5e238724d29f3`: [CI completo 40747877347](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40747877347)
aprovado em 28/10 às **15:49:39 Brasília**, 1.410 executados/1.409 aprovados/um
opcional, zero falhas, 293,160 s. 25 novos + 179 regressões locais aprovados.
Fechamento posterior só documental [skip ci], sem repetir suíte ou publicação.
 As primeiras tentativas também corrigiram fixtures que reconectavam
a conta inadvertidamente ou esperavam exceção interna após sanitização do transporte;
nenhuma guarda foi relaxada para passar os testes.

O produtor PR31 não foi alterado nesta rodada. Não houve Google/Discord real,
escopo novo, Apps Script, chamada de modelo, merge ou publicação. Pacote atual
continua sem Carteira. Pacote regenerado: 90 arquivos, CRC íntegro e todos os
bytes iguais aos fontes; sem env/bancos/campanha. SHA256
`20e0f456bd7decd1f17d115539471e3039e2692eec89d12134b42bc86fec2b7b`.
Não foi publicado. Todos os quatro indicadores de liberação permanecem falsos.

Ainda faltam: composição da fila e renovação/autorização reais no serviço;
cópia descartável e diário de escrita com reconciliação; propriedades do GS e
demais domínios; preservação global/arte, automações/treinos/notas/responsável;
e prova integrada usando o OAuth próprio das Guias. Sem esses itens, não liberar
criação. Próximo: compor a execução de leitura no serviço sem rota pública e
validar cancelamento/revogação/fila; planejar a escrita separadamente, sem
presumir que Sheets oferece escrita condicional atômica por versão Drive.
GPT-6.1 Sol / Alto para implementar; Médio para revisão focal.

## Próximo passo no serviço

Compor uma operação interna, sem abrir criação ou aceitar método/faixa/arquivo
arbitrário do navegador. Usar a fila existente, com chave que inclua iniciador
e operação; manter cotas por conta Google e renovar sob a trava de conexão.
Reconfirmar membro/cargos por `Provedores.membro` antes de cada contexto; o
callback deve retornar o contexto de `contexto_operacao_rest` com esse membro
atual, não guardar um hash constante da primeira solicitação. Renovação de
refresh segue o fluxo já usado em Consultas, sem pôr token no estado persistido.

Iniciar só com referência autorizada e versão recém-observada. Para retomar,
recuperar o bilhete interno, obter credencial atual e chamar o adaptador de cada
domínio restante. Não reaproveitar um objeto PlanoGrade entre processos ou
aceitar cursor do cliente. Exercitar troca/revogação enquanto aguarda fila/cota,
concorrência, prazo e cancelamento. Depois, prova de leitura em descartável pelo
OAuth próprio, distinta do conector Google. O diário de cópia/escrita fica para
uma implementação própria com reconciliação; nenhuma dessas leituras o substitui.
