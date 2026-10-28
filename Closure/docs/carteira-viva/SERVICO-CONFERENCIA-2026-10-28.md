# Conferência na fila do serviço

28/10/2026 · etapa 7 parcial, PR84. Não publicado. Criação bloqueada.

## Implementação

`Consultas.conferir_inicializacao(servidor, usuario, personagem, retomar=False)`
compõe o auditor REST com `DadosAsync`, a fila e as cotas já usadas nas análises.
É um método interno, sem endpoint, botão ou comando novo. Só recebe o ID de um
personagem cadastrado; arquivo e conexão vêm do banco, não de uma URL do cliente.
Não copia, limpa ou altera planilhas. Todos os indicadores de liberação seguem falsos.

Pedidos iguais do mesmo iniciador coalescem. A chave inclui servidor, fonte,
autorização, iniciador e, na retomada, a operação. A fila reconfirma a fonte ao
iniciar; troca de arquivo/autorização durante a espera recusa antes do OAuth.
Uma operação ainda válida precisa ser retomada ou descartada explicitamente:
começar de novo não incrementa a geração e destrói a possibilidade de retomada.

A fila admite prazos internos por pedido, finitos e no máximo 30 minutos.
Esta operação usa 20 minutos de execução e 21,5 minutos totais para o cliente.
Consultas comuns conservam os 60/90 segundos anteriores. Coalescência não altera
o prazo do trabalho existente; capacidade, justiça por grupo e cancelamento
continuam compartilhados. Os 30 minutos absolutos do registro persistido também
continuam valendo, inclusive enquanto a retomada espera na fila.

## Acesso e cotas

O serviço consulta membro/cargos atuais pela API Discord antes de cada contexto.
O auditor também verifica banco/prazo por GET e após aguardar cota. Não usa um
hash constante nem o Membro capturado ao entrar na fila como prova de acesso.
As cotas Google por conta/projeto são as mesmas do objeto Consultas, compartilhadas
com a análise. Conta chega à cota apenas por hash. GETs de metadados/versão e a
observação inicial também contam. Nenhuma grade é escrita.

A reserva usa referência autorizada. O OAuth é renovado sob a trava de conexão
compartilhada com as análises; cliente diferente recusa antes de enviar o refresh.
Uma resposta `invalid_grant` só revoga aquela versão da autorização, preservando
uma reconexão posterior. Erro temporário não revoga. Token perto de expirar
interrompe a leitura; a retomada renova de novo, sem aproveitar domínio incompleto.

O token de acesso vive em memória. O refresh rotacionado fica cifrado, com
comparação transacional da autorização **e do refresh anterior**. Troca de ficha
ou perda de cargo durante o OAuth nega a consulta, mas preserva a rotação da mesma
concessão para o dono. Conexão revogada, excluída, reautorizada ou já renovada por
outra resposta não é recriada/sobrescrita. Esse método de manutenção é interno,
sem identidade/permissão de leitura ou rota pública concedida ao chamador.

Cancelar durante o OAuth conclui somente a manutenção da credencial já iniciada,
sob a trava e com prazo total de 30 segundos, antes de propagar o cancelamento.
Não começa leitura de ficha após o cancelamento. O serviço aguarda essa limpeza
antes de liberar a tarefa; cancelar um entre vários clientes preserva os demais.
Timeout/perda de resposta da rede não permite inferir um token desconhecido;
pode exigir reconexão, sem afirmar garantia de entrega exatamente uma vez.

## Retomada

`retomar=True` usa o registro cifrado existente, sem renovar sua validade.
Renova a credencial e observa novamente a versão Drive, incluindo quando ambos
os domínios já estavam salvos e só faltava entregar a resposta. Versão divergente
recusa antes de reler células. Domínio interrompido recomeça na primeira página;
financeiro já salvo não é refeito para continuar progressão.

Cada cliente que aguardava a tarefa consulta novamente membro e resultado no
banco antes da resposta. Não compartilha um dict mutável nem entrega arquivo,
conta, contexto, ID da operação, tokens ou grade no resultado. Evidência continua
histórica, sem certificação de snapshot conjunto ou aprovação da ficha.

## Validação e pendências

Testes percorrem HTTP real de Provedores/Authlib com transporte simulado para
Discord/Google, worker em thread, SQLite cifrado, fila, coletor e auditor reais.
Dados são fictícios e baseados no contrato público; não acessam contas externas.
A fixture de OAuth informa expires_at no mesmo relógio simulado do serviço.
O perfil de 5.000 linhas exige 183 GETs Google: um inicial, 154 financeiros e 28
de progressão; todos reservam cota. Retomada só de progressão usa 29.

Duas regressões de perda da rotação (mudança de fonte/cargo) e a de cancelamento
falharam antes e passam após as correções. As expectativas de negação de acesso
foram preservadas. 39 testes do lote serviço/fila passaram em 56,709 s (26 novos do serviço,
três novos da fila e dez já existentes). Mais 137 regressões de consultas/web/
banco/recuperação passaram em 88,386 s: **176 testes locais distintos**, zero
falhas finais. A primeira fixture corrigiu apenas o parâmetro auxiliar `nome`
que colidia com o campo de cadastro, e expires_at para o relógio simulado.
Nenhuma expectativa mecânica ou guarda de acesso foi flexibilizada. Suíte
completa aguardando CI desta rodada.

Não mede cotas/latência reais do Discord ou Google. A checagem de membro/cargos
usa requisições reais por contexto, sem cache de permissão; volume e limites do
Discord ainda precisam de medição nativa. Falha/limite da API interrompe sem
entregar dados, sem retry infinito e sem revogar um grant por erro temporário.

Faltam prova integrada pelo OAuth das Guias em descartável e composição futura
com a criação. Depois: cópia e diário de escrita com reconciliação, propriedades
do Apps Script e demais domínios, preservação global/arte, automações/treinos/
notas/responsável. A leitura pronta não substitui essas etapas. Não ampliar
escopo, publicar Apps Script, liberar criação ou implantar pelo sucesso do CI.
Produtor PR31 intacto; sem Google/Discord real, modelo pago, merge ou deploy.
Sol Alto para integrar/provar a próxima parte; Médio para revisão focal.

Pacote ignorado regenerado/conferido: 90 arquivos, CRC e bytes dos fontes iguais,
sem env/Carteira/bancos/campanha; não publicado. SHA256
`7fdfc73e7e6d805f277102d2ccf44871e268e739553a324a1d8c93ddcfd5bb23`.
