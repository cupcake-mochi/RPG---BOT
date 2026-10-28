# Cópia com recuperação de resposta perdida

**Atualização posterior:** o caminho observado de cópia/recuperação foi
validado com Google real: resposta perdida, reinício, identificação sem segundo
POST e recusa após revogação. Duas descartáveis na lixeira/piloto encerrado.
[Relatório nativo](NATIVO-COPIAS-2026-10-28.md). O texto abaixo registra a entrega
offline anterior; os avisos de ensaio pendente são históricos.

28/10/2026 · etapa 7 parcial · PR84 em rascunho, dependente da PR83.
**Implementação interna, validada offline. Não publicada nem ensaiada no Google.**
O ensaio nativo anterior testou leitura/retomada, não este transporte de cópia.

## Por que ainda estamos na etapa 7

A etapa original juntou configuração do modelo e criação opcional. Criar exige
inicializar uma planilha inteira sem herdar dados nem quebrar suas automações.
O planejamento subestimou esse tamanho; leitura aprovada não encerra criação.
Para tornar o avanço verificável, acompanhar estes blocos:

| Bloco | Entrega | Estado |
|---|---|---|
| 7A | Escolha do modelo; acesso, leitura e retomada | Implementados; prova nativa do dono registrada |
| 7B | Copiar uma vez e recuperar resposta perdida | Backend implementado nesta rodada; prova nativa pendente |
| 7C | Limpar e inicializar a cópia, com diário de escrita | Protótipos no produtor; integração REST ainda pendente |
| 7D | Preservação, automações, demais domínios e ensaio completo | Pendente; necessário antes de liberar criação |

Etapas 8–10 continuam separadas: edição autorizada, revisão/carga e publicação.
Não trocar o número da etapa para ocultar trabalho ainda não entregue.

## O que entrou no bot

`Consultas.copiar_modelo` é um método **interno**, sem rota HTTP, botão ou comando.
Lê o modelo da configuração real do servidor; não aceita ID de fonte/destino,
faixa de células ou permissões enviados por um formulário. A conexão Google
precisa pertencer ao iniciador, mesmo se outro membro tiver Administrator.
Cadastro normal e `criar_por_modelo` continuam separados; este último sempre
recusa. Uma cópia identificada não é personagem cadastrado ou ficha limpa.

O método compartilha fila, cotas e trava/renovação Google com as análises.
Revalida membro atual, conexão, versão da autorização e revisão do modelo antes
e depois da rede/cota. Troca do modelo ou reconexão não adota o pedido antigo.
O OAuth usa o cliente já configurado e somente `drive.file`.

As [operações files.copy](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/copy)
e [files.list](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list)
aceitam esse escopo; isso não garante que o jogador tenha acesso ao modelo.
A observação inicial exige arquivo autorizado ao app. Não reutiliza a concessão
do administrador que configurou um modelo privado. O fluxo de seleção/acesso
a esse modelo pelo jogador ainda precisa de prova nativa e de interface.
Não tornar o modelo público, compartilhar ou ampliar escopos automaticamente.

## Diário e envio

Schema **8**: `copias_rest`, com conteúdo cifrado por servidor/iniciador/operação.
Pedido é armazenado como hash; origem, destino, versões e autorização ficam no
envelope. O iniciador repete a mesma identificação do pedido para obter a mesma
operação. Alterar conexão/escolha com essa identificação causa conflito.

1. `preparada`: fonte vem da configuração; o serviço observa e fixa sua versão.
2. `enviada`: transação confirma o estado **antes do POST**. Só um trabalhador
   pode armar o envio, inclusive com duas instâncias do banco.
3. `identificada`: adaptador observou a cópia e suas permissões; o serviço
   reconferiu a versão do modelo e o contexto. Não significa inicialização.

O único POST usa `files.copy` na origem, um nome genérico e o destino `root`
da conta do jogador. Não há destino de pasta vindo do cliente, transferência
de propriedade, compartilhamento ou escrita em células. A resposta tem limite
de 32 KiB, sem redirects, retry automático, logs de token ou corpo externo.

A cópia recebe [appProperties](https://developers.google.com/workspace/drive/api/guides/properties)
privadas do app: nonce de operação de 256 bits, hash da origem e protocolo.
Não contém ID Discord, nome do jogador, segredo ou histórico da ficha.
Resposta aceita não basta: um GET precisa comprovar outro ID, tipo Sheets,
autorização ao app, propriedade da conta atual, ausência de lixeira/Drive
compartilhado, `shared=false`, permissão única de proprietário e marcadores
esperados. Arquivo de origem nunca vira destino. A versão do Drive é uma
guarda de conflito; não certifica recálculo, imagens ou automações copiadas.

## Falha, reinício e backup

Depois de `enviada`, nenhuma tentativa do mesmo pedido repete o POST, mesmo
após timeout, cancelamento, 429 ou resposta inválida. Só busca pelos três
marcadores e observa o candidato. Inclui lixeira na busca: descartar o arquivo
não é motivo para criar outro silenciosamente.

Zero resultados mantém o estado incerto; não prova ausência de uma cópia cujo
POST perdeu resposta. Mais de um resultado, paginação restante ou busca
incompleta causam recusa. Nunca escolher o primeiro candidato. Reconciliar uma
cópia ainda não prova seu conteúdo ou autoriza a limpeza dela.

Um backup pode ser anterior a um envio ocorrido no banco vivo. Por isso, na
**cópia do backup**, `preparada` vira `enviada`, com o envelope cifrado coerente.
Restaurar só permite reconciliar; o banco vivo não é alterado. Se o backup ainda
não tinha a versão original do modelo, a integração não a inventa para adotar
a cópia. Essa situação permanece bloqueada para revisão, sem novo POST.
Não é garantia de entrega exatamente uma vez; prioriza não duplicar arquivos.

Operação pendente não expira silenciosamente: pode ter criado arquivo no
Google. Há no máximo uma pendente por iniciador/servidor, 64 registros totais
por iniciador/servidor e 10.000 no banco. Identificadas têm retenção de 30 dias
após a última observação. A idempotência não é promessa além dessa retenção.
Pendentes pinam a conexão contra coleta de órfãs. Revogação/reconexão bloqueia
uso do diário antigo; não recria a concessão ou repete o POST.

Rotação de cifra inclui o diário. Exclusão global remove seus registros e
guarda somente o nonce mínimo no ledger por 31 dias, impedindo reaparição num
backup ainda válido (até 30 dias). O ledger migra de **1 para 2** na mesma
transação; versões futuras recusam. Nenhuma operação apaga o arquivo Google.

## Preparação do próximo ensaio real

Após os testes offline, foi criada pelo Drive conectado uma nova cópia privada
DESCARTÁVEL do Ciclo, com apenas o proprietário nas permissões. Ela será o
modelo de teste; a fonte oficial não foi escrita. O piloto próprio foi iniciado
no loopback usando base/chave novas e os mesmos clientes Google/Discord.
A identificação Discord concluiu; o Google está no consentimento de drive.file,
**aguardando autorização do usuário** para selecionar só essa descartável e
criar uma segunda cópia. Ainda não houve cadastro confirmado ou POST de cópia
pelo método novo. Nenhum resultado nativo de cópia é declarado neste fechamento.

O executor privado está preparado para descartar deliberadamente uma resposta
HTTP200 do POST e, após reinício, exercitar a busca por marcador. Isso testa
recuperação pelo serviço real; não deve virar falha injetada no produto.
A nova cópia e o piloto ficam pendentes para esse ensaio, não foram limpos ainda.
Ao terminar/recusar: revogar a concessão de teste, excluir só os dados fictícios,
encerrar o piloto e enviar as cópias novas para a lixeira recuperável.
URLs OAuth/tickets/IDs pessoais/credenciais e arquivos privados ficam fora do Git.
O ensaio anterior de **leitura**, já encerrado, continua separado no relatório
[NATIVO-CONFERENCIA-2026-10-28.md](NATIVO-CONFERENCIA-2026-10-28.md).

## Testes e limites

29 testes novos aprovados em 5,586 s no lote inicial completo; após endurecer
validações booleanas, os mesmos 29 passaram em 4,312 s. Cobrem um POST, resposta perdida,
reinício, concorrência/coalescência e dois workers, cancelamento, 429, falha de
observação, origem como destino, candidato duplicado/busca incompleta, isolamento
por dono/servidor, troca de modelo e concessão, perda de autorização na cota,
compartilhamento indevido, backup sem replay, exclusão/restauração, rotação,
retenção e migrações. Dados fictícios e HTTP simulado; nenhuma conta real.

As regressões de migração antigas criavam schemas 1/3/4/5/6 removendo tabelas
posteriores manualmente. Passaram a remover também a tabela nova de schema 8;
manter essa tabela e rebaixar só o número não representa uma base histórica.
Nenhuma expectativa de autorização ou mecanismo foi afrouxada.

Os lotes locais totalizam **197 testes distintos aprovados**, 29 novos e 168
anteriores, com zero falhas finais. A execução ampliada de 189 levou 162,772 s
e revelou uma fixture histórica de migração incompleta; o caso corrigido passou
em 0,134 s. Os seis testes novos adicionais entram no lote de 29 acima, sem
somar repetições. O primeiro CI completo (40771002103, código `5b67ccb`) executou 1.486 testes
em 248,815 s: duas falhas de preparação histórica dos schemas 3/4 e um opcional
pulado. Essas fixtures também passaram a excluir a tabela de schema 8; os dois
casos passaram localmente em 0,178 s. O [CI final 40772021442](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40772021442),
no código `9cb8a84a9afa151c26fd1c5eeed829c6312651db`, passou em 28/10 às
**18:32:26 Brasília**: **1.486 executados/1.485 aprovados/um opcional pulado**,
zero falhas, 300,149 s. O fechamento seguinte é somente documental [skip ci];
não repetir a suíte nem publicar por ele.

Pacote ignorado regenerado: 90 arquivos/CRC/fontes iguais, sem env, Carteira,
bancos ou cadastro de campanha; SHA256
`d1fa170bd1c56b281f0b56cccc41bf565bf7eb5ad356e1c13a998c7e11f5d89e`.
Não publicado. A Carteira continua fora desse pacote do bot de conversas.

Faltam: prova nativa da cópia pelo OAuth do jogador; tratamento assistido dos
pedidos incertos/órfãos; integração do diário de escrita de células e sua
reconciliação; demais domínios/propriedades; preservação/arte, automações,
treinos/notas/responsável e conferência conjunta. A rotina não limpa, emite,
concede acesso a outra pessoa, cadastra personagem ou libera criação.
Não expandir um retry para contornar a incerteza nem entregar uma cópia bruta.

Próximo bloco de código: plano de escrita restrito ao contrato em cópia
comprovada, diário antes de cada lote e reconciliação do pós-estado em vez de
reexecutar efeitos. Começar pelo financeiro; compor leitura e demais domínios
somente após guardas e preservação demonstradas. Sol Alto; revisão Médio.
