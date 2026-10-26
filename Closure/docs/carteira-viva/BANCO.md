# Banco de personagens

Etapa 2 · 26/10/2026. Implementação em `src/carteira_viva/`. O módulo ainda
não é carregado pelas Guias, não abre portas e não registra comandos Discord.
OAuth e dados reais continuam fora desta etapa.

## Arquivos e chaves

O serviço futuro terá dois arquivos próprios, no mesmo volume persistente:

- `carteira.sqlite3`: cadastro, conexões, perfis, leituras e análises;
- `carteira.remocoes.sqlite3`: registro mínimo de personagens excluídos e
  versões de autorização revogadas/desconectadas.

Não apontar o módulo para os bancos de conversas das Guias ou da Arquivista.
Cada banco tem identificação de aplicação e versão; arquivo alheio ou versão
mais nova é recusado. Se o cadastro existente perdeu o registro de remoções,
a abertura falha: não recriar esse registro vazio e fingir que está recuperado.

Novos arquivos têm permissão `0600` no Unix. A chave de cifra é obrigatória,
própria da Carteira e externa ao Git/banco. Perfis, credenciais, snapshots e
resultados de análise são cifrados. IDs Discord, IDs opacos de personagem,
tempos, contagens, capacidades e referências técnicas necessárias às consultas
ficam em claro. Nenhuma imagem ou planilha inteira é armazenada aqui.

Envelopes cifrados incluem o contexto: tipo do dado, servidor/personagem ou
conexão/usuário/versão da autorização. Copiar um envelope para outra identidade
ou registro não deve permitir sua leitura. Conta Google e cliente ficam no
envelope e têm hashes separados para localizar uma conexão existente.

## Schema e migrações

Schema atual: **3**. Migração 1 cria as tabelas de domínio; migração 2 acrescenta
pedidos e auditoria; migração 3 acrescenta tentativas web cifradas. A sequência é transacional. Não há banco de produção de
uma versão anterior deste recurso; o teste de migração usa uma fixture v1.

| Tabela | Uso |
|---|---|
| `servidores`, `cargos` | Campos públicos permitidos e capacidades explícitas de revisão/edição |
| `conexoes` | Uma conexão por usuário Discord, identidade Google e cliente OAuth |
| `personagens` | Vários personagens por jogador/servidor, com ID estável e perfil próprio |
| `fontes` | Arquivo, conexão, versão do contrato, revisão e geração da leitura |
| `leituras` | Só a última leitura válida por personagem |
| `analises` | Só o último resultado salvo, ligado à leitura e à revisão da campanha |
| `pedidos` | Identificador de repetição, assinatura dos argumentos e ID do resultado |
| `web_fluxos` | Tentativas de conexão cifradas, estado OAuth de uso único e validade de dez minutos |
| `auditoria` | Ação, ator, personagem e horário, sem conteúdo privado da ficha |
| `remocoes.exclusoes` | IDs de personagens removidos, para reaplicar na restauração |
| `remocoes.autorizacoes` | Versões de autorização bloqueadas, para não reativar consentimento antigo |

Não foi criado um novo sistema de aprovação mecânica. `campanha_revisao` é
referência do resultado; a integração da etapa 4 precisa conferir a campanha
atual e reaproveitar as aprovações por definição exata do motor existente.
O campo `analise.fonte_atual` só compara fonte e leitura: não aprova ficha nem
garante que a campanha continua igual.

## Interface interna

Todas as identidades vêm de um adaptador autenticado **do servidor**. Não
converter JSON do navegador diretamente em `Membro`, nem publicar estes
métodos como endpoints sem as guardas da etapa 3.

| Método | Comportamento |
|---|---|
| `configurar` | Dono/admin define capacidades e apresentação; cargos de lore não são importados |
| `conectar` | Persiste autorização já validada pelo adaptador OAuth; não faz login no Google |
| `cadastrar` | Responsável atual confirma cadastro; arquivo deve ter sido validado pelo adaptador Google |
| `listar`, `cartao` | Galeria paginada só do servidor, com campos públicos por lista positiva |
| `personalizar` | Dono altera o perfil local; não escreve na planilha |
| `detalhes` | Dono/admin/revisor autorizado consulta fonte e dados privados ainda válidos |
| `trocar_arquivo` | Dono confirma fonte nova com revisão esperada; conserva ID e perfil |
| `reservar_leitura`, `gravar_leitura` | Serviço recebe uma referência e grava só se ela ainda for válida |
| `gravar_analise` | Serviço salva resultado para a leitura atual; não calcula nem aprova |
| `desconectar` | Dono remove a credencial e bloqueia acesso privado de todos os vínculos da conexão |
| `marcar_revogada` | Adaptador Google informa a versão de autorização que falhou; resposta antiga não revoga uma nova |
| `registrar_saida`, `registrar_retorno` | Adaptador Discord confirmado controla ocultação e prazo de retorno |
| `excluir` | Dono remove personagem e dados relacionados, sem apagar arquivo Google |
| `apagar_usuario` | Pedido global com identidade comprovada, inclusive após saída do servidor |
| `limpar` | Manutenção local das retenções; não consulta planilhas |
| `rotacionar_chave` | Reescreve os envelopes numa transação; falha conserva a chave anterior |

`_credencial` é exclusivamente para o adaptador Google do serviço. O retorno
nunca entra na API, nas mensagens ou no modelo de linguagem. Sua versão de
autorização deve acompanhar erros de renovação para que uma resposta atrasada
não invalide um login novo.

Cadastro e troca recebem uma chave de pedido de uso estável durante repetição.
Repetir o mesmo pedido não cria personagem nem troca arquivo duas vezes.
Reutilizar a chave com outros dados gera conflito. O banco guarda esses pedidos
por sete dias. Edições de jogo continuam indisponíveis; uma operação financeira
futura precisará de contrato próprio de repetição e confirmação.

## Concorrência e leitura

Cada fonte tem revisão crescente. Cada reserva de leitura também tem uma
geração. Uma troca, revogação, desconexão, nova autorização ou reserva mais
recente invalida resultados anteriores em andamento. Gravar uma leitura
consome sua referência; a mesma resposta não pode ser aplicada outra vez.

As transações usam `BEGIN IMMEDIATE`, chaves estrangeiras e restrição de
arquivo único por servidor. A prova usa duas operações intercaladas e falha
de gravação simulada; não é ensaio de vários servidores de aplicação.

Usar um único serviço responsável pelo banco. A conexão Python é síncrona e
não deve ser compartilhada entre threads. O serviço web futuro precisa de
fila/worker próprio, sem bloquear o processamento das conversas do bot.
SQLite não será compartilhado pela rede.

## Retenção

Consultas já deixam de devolver leitura/análise expirada mesmo antes da
limpeza física. Após saída detectada, o personagem fica oculto imediatamente;
retorno em até 30 dias pode reativá-lo. Depois disso ele é removido.

`limpar()` remove snapshots após 24 horas, análises após sete dias, pedidos
após sete dias, auditoria após 90 dias e conexões sem vínculos após 24 horas.
Excluir um personagem é imediato; a conexão de outro personagem é preservada.
O registro de exclusões/bloqueios fica por 31 dias; backups de mais de 30 dias
são recusados. Isso permite retirar esses registros sem aceitar um backup
antigo que pudesse restaurar os dados removidos.

O serviço da etapa 3 liga a limpeza local a cada minuto e confere membros
e cargos nas ações de conexão. O banco sozinho não descobre saídas nem
mudanças de cargo; eventos gerais de saída/retorno ainda precisam da
integração Discord. Tentativas web expiram em dez minutos e são eliminadas
ao abrir/reiniciar o banco. Imagens ficam para a galeria.

## Backup e recuperação

`backup.gravar_backup` usa a API de backup do SQLite para obter uma cópia
consistente e cifra o arquivo em blocos autenticados. Não carrega o banco
inteiro em memória. O formato verifica ordem, integridade, fim do arquivo,
identidade do banco e prazo. Backup existente nunca é sobrescrito.
Tentativas web são removidas da cópia antes da cifra; cadastros e conexões
confirmadas permanecem. Uma restauração não reabre retornos OAuth antigos.

Manter uma cópia do cadastro **e uma cópia atual do registro de remoções**.
Para copiar o segundo, usar `registro_remocoes=True`. Preservar a chave fora
dos arquivos. O registro de remoções precisa ser atualizado nas cópias de
recuperação após exclusões/desconexões; um backup antigo do cadastro não pode
ser usado como se também fosse o registro atual de remoções.

Para recuperar:

1. Parar o serviço da Carteira; manter os bots existentes separados.
2. Recuperar o registro de remoções mais recente, se necessário, com
   `restaurar_remocoes`. Confirmar que ele inclui os últimos pedidos removidos.
3. `restaurar_backup` grava o cadastro em um **destino novo**, exigindo esse
   registro externo e a chave correta. Não sobrescreve banco aberto/existente.
4. A abertura reaplica exclusões e bloqueios de autorização antes de servir
   dados, e confere identificação/integridade.
5. Confirmar chaves, configuração, cargos/membros atuais e estado Google.
   Só então apontar o serviço para o banco recuperado.

Se o registro atual também foi perdido, não é possível inferir exclusões
posteriores a uma cópia antiga. A rotina recusa sua ausência; recuperação
nessa situação exige apuração do operador, sem promessa de recuperar eventos
que não foram preservados. Não publicar automaticamente um banco incompleto.

`limpar_backups` só remove arquivos `.cvb` deste cadastro cujos metadados
autenticam e cuja idade passou de 30 dias. Preserva links, arquivos de outro
cadastro e metadados inválidos. Gerar/conferir o novo backup antes da limpeza.
Depois de rotacionar a chave do banco, guardar a chave antiga até expirar os
backups feitos com ela; a restauração aceita um conjunto de chaves.

## Limites desta entrega

- Até 8 MiB de JSON por snapshot/resultado; recusa explícita, sem truncar campos.
- Até 2 GiB de banco por arquivo de backup. Esses são limites de proteção,
  não capacidade comprovada para mil personagens.
- Perfil com campos tipados e texto limitado; upload, validação de imagem e
  escape de menções/renderização ficam para a galeria.
- O banco armazena resultados de análise; a conexão com o motor e a campanha
  reais continua na etapa 4. Aprovações e decisão do mestre permanecem separadas.
- HTTP/OAuth implementados localmente na etapa 3; teste nativo e publicação
  pendentes. Nenhuma escrita de ficha ou comando novo instalado em produção.
- Sem ensaio de queda de energia ou falha física do disco. O teste de rollback
  injeta uma falha SQL; desempenho/carga ficam na etapa 9.

## Referências

- [Transações com bancos anexados](https://www.sqlite.org/lang_attach.html):
  a atomicidade entre arquivos exige banco principal em disco e sem WAL.
  Por isso cadastro e registro usam journal `DELETE` e sincronização `FULL`.
- [API de backup SQLite](https://www.sqlite.org/backup.html): cópia consistente
  sem copiar um arquivo ativo por fora do SQLite.
- [Fernet e rotação de chave](https://cryptography.io/en/latest/fernet/):
  envelopes autenticados e leitura com múltiplas chaves.
