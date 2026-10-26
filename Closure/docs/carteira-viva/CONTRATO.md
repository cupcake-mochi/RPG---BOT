# Contrato da Carteira viva

Etapa 1 · 26/10/2026 · versão de contrato 1. Não é uma API publicada.
Decisões de implementação para as etapas seguintes do [plano](PLANO.md).
Mudanças incompatíveis exigem nova versão, migração e teste de preservação.

## Identidade e responsabilidade

O personagem pertence a um cadastro de **servidor + identificador estável**.
O responsável é um usuário Discord. Nome, apelido, arquivo Google e conta
Google podem mudar; nenhum deles substitui o identificador do personagem.
Um usuário pode ter vários personagens. O mesmo arquivo em servidores
diferentes nunca compartilha campanha, autorização ou análise automaticamente.

Ao cadastrar, o jogador confirma: “Esta é minha ficha e posso cadastrá-la
neste servidor”. Acesso de editor no Google não comprova autoria de personagem.
Se o arquivo já estiver registrado no servidor, mostrar a opção de procurar
o responsável/equipe; nunca substituir o dono pelo último usuário que o enviou.
Transferência exige confirmação do responsável e do destinatário, ou fluxo
administrativo separado com motivo e auditoria. Não faz parte da prova local.

Membro ausente não consulta nem altera cadastro. `Administrator` e dono do
servidor têm revisão privada e configuração. `Manage Guild` sozinho não
concede essas novas capacidades. Cargos de idioma/lore não são reaproveitados.
Revisor não é editor. Até a etapa 8, **nenhuma edição da planilha está liberada**.

## Dados e armazenamento

| Entidade | Dados principais | Restrições |
|---|---|---|
| Servidor | idioma, modelo, cargos de revisão/edição, campos públicos permitidos | Administrador/dono configura; não delegar implicitamente por cargo de lore |
| Personagem | ID aleatório, servidor, responsável, estado, nome de exibição | Chave composta por servidor/ID; não usar nome como chave |
| Conexão Google | usuário Discord, identidade Google estável, cliente OAuth, segredo cifrado, estado | Credenciais nunca nos cartões, logs, relatórios ou respostas da API |
| Fonte | personagem, arquivo, conexão, revisão inteira crescente, contrato detectado | Troca exige revisão esperada; vínculo por servidor e arquivo é único |
| Perfil | título, frase, campos de apresentação, cor, referência da imagem | Não armazenar imagem em SQL; validar tamanho e formato na etapa 5 |
| Snapshot | fonte/revisão, campos tipados, horário de leitura, versão de schema | Só última leitura válida; ausente, vazio e zero são diferentes |
| Análise | origem do snapshot, campanha/revisão, achados, horário | Não equivale à aprovação; mudança da fonte invalida resultado corrente |
| Aprovação | definição exata, autor, servidor, validade e fonte/conteúdo relevante | Preservar motor atual; autorização não transforma prosa em número |
| Operação | identidade, tipo, revisão esperada, prazo e resultado | Um pedido confirmado não executa duas vezes |
| Auditoria | ação, ator, ID interno, hora e resultado | Sem conteúdo integral da ficha, token ou email Google |

SQLite próprio, inicialmente um único processo responsável pela escrita.
Frontend e bot não abrem cópias independentes do banco para tentar sincronizar
depois. Frontend chama o serviço; o bot usa cliente autenticado desse serviço.
Chamadas internas precisam de credencial de serviço e verificação de contexto,
nunca um endpoint público que aceite `usuario_id` como prova de identidade.

A conexão Google pode atender vários personagens do mesmo usuário. Revogação
conhecida afeta todos os vínculos dessa conexão, inclusive em outros servidores.
Desvincular só um personagem não revoga a conta inteira. O cadastro permanece
independente do armazenamento de fatos pessoais das conversas das guias.

### Prazos definidos para a implementação

| Informação | Prazo inicial |
|---|---|
| Tentativa de conexão/seleção e prévia | 10 minutos; cancelamento remove imediatamente |
| Sessão web | 30 minutos sem uso, máximo de 8 horas; permissões revalidadas por ação |
| Cache fresco de leitura | Até 60 segundos; análise explícita exige leitura atual estável |
| Snapshot privado sem nova consulta | 24 horas; depois apagar e reler quando necessário |
| Análise salva para consulta do dono/equipe | 7 dias, sempre identificada pela fonte e horário |
| Personagem após saída do responsável | Ocultar imediatamente quando detectado; guardar 30 dias para retorno, depois remover |
| Auditoria mínima | 90 dias, sem snapshot, segredo ou valores de lançamentos |
| Exclusão pedida pelo dono | Bloquear imediatamente; apagar perfil, vínculo, snapshot e análise em até 24 horas |
| Conexão sem nenhum vínculo/fluxo | Apagar credencial em até 24 horas; não revogar concessão Google de outros vínculos |
| Imagem sem referência | Remover em até 24 horas |
| Backups privados | Rotação de 30 dias; arquivos cifrados e acesso restrito |

Esses são prazos do novo recurso, não mudanças nas retenções atuais do bot.
A exclusão deve constar num registro mínimo de remoções para não ressuscitar
dados ao restaurar backup. Reaplicar remoções posteriores à data do backup
antes de reabrir o serviço. Dados que o usuário já enviou publicamente no
Discord não podem ser recolhidos de cópias feitas por terceiros.

## O que cada resposta contém

**Cartão aos membros:** identificador opaco da carteira, nome, responsável
Discord, título/frase e apenas os campos de apresentação liberados pelo dono
e pelo servidor. Campos candidatos: idade, clã, Origem e Caminho. Imagem e cor
são opcionais. Sem email, URL Google, conta Google, erros de análise, histórico
ou snapshot mecânico. Nome/Imagem de personagem não são extraídos por suposição.

**Área privada:** dados tipados da ficha, fonte, horário e resultado da análise,
depois de verificar participação e capacidade. Mostrar “Última leitura…”
quando o Google estiver temporariamente indisponível e o cache ainda for válido.
Revogação conhecida bloqueia o snapshot privado. Não anunciar perda de acesso
instantânea no Google se o serviço ainda não fez nova consulta.

**API:** construir respostas por lista positiva de campos. Nunca serializar
a linha do banco inteira. Variação de identidade/servidor deve alterar também
as chaves de cache; usar `Cache-Control: private, no-store` nas respostas
privadas e nas páginas de conexão. Tokens não vão ao modelo de linguagem.

## Fluxo de conexão

1. Interação privada no Discord, originada de membro atual, cria tentativa
   vinculada ao servidor, usuário, ação e revisão esperada da fonte.
2. Página web identifica o usuário por OAuth Discord `identify`. Verificar
   igualdade com quem iniciou; confirmar participação atual pelo bot/serviço.
   Não pedir email Discord nem acesso às mensagens.
3. Criar sessão protegida e estado OAuth de uso único por provedor. Expiração,
   proteção CSRF, cookie `Secure`, `HttpOnly`, `SameSite=Lax` e rotação após login.
   Usar biblioteca OAuth mantida e PKCE quando suportado pelo fluxo escolhido;
   estado e sessão continuam necessários. O protótipo não implementa essa camada.
4. OAuth Google web com `drive.file` e renovação offline. Não pedir Drive inteiro.
   Identidade Google pode ser confirmada por `about.user.permissionId` do Drive,
   sem precisar do email. Confirmar suporte/estabilidade no adaptador real.
5. Google Picker web seleciona um Sheets; backend confirma `isAppAuthorized`,
   tipo, acesso, lixeira e contrato. O retorno do Picker sozinho não basta.
6. Prévia privada mostra o arquivo escolhido e o efeito da ação. Confirmar
   responsabilidade e vínculo. Só então persistir a conexão/fonte ativa.
7. Cancelamento/erro não altera vínculo anterior. Tentativas incompletas
   podem expirar no reinício; conexões já confirmadas devem sobreviver.

Solicitar consentimento Google de novo apenas quando necessário. Uma resposta
de renovação nem sempre inclui novo refresh token: manter o anterior se for
a mesma identidade e continuar válido. Não reutilizar token de outra conta.
Mudança de conta Google é uma reconexão explícita, diferente de trocar arquivo.

### Rotas propostas, ainda não disponíveis

| Rota | Função | Guarda |
|---|---|---|
| `POST /interno/conexoes` | Bot inicia tentativa | Serviço autenticado + interação Discord comprovada |
| `GET /conectar` | Identifica tentativa e abre login | Não concede acesso só por conhecer o link |
| `GET /oauth/discord/retorno` | Confirma identidade Discord | Código/estado/sessão/usuário esperado |
| `GET /oauth/google/retorno` | Recebe autorização Google | Código/estado/sessão/escopo/conta |
| `POST /conexoes/selecao` | Valida escolha do Picker | Sessão + CSRF + metadados da API |
| `POST /conexoes/confirmar` | Confirma cadastro/troca | Membro atual + revisão esperada + transação |
| `POST /conexoes/cancelar` | Descarta tentativa | Mesma sessão e identidade |
| `POST /personagens/{id}/atualizar` | Relê ficha vinculada | Servidor/membro/capacidade + fila |

Não colocar código OAuth ou token nos logs de acesso de callbacks. Remover
parâmetros sensíveis da URL ao redirecionar. Página de conexão sem publicidade
ou analytics; `Referrer-Policy: strict-origin` envia só a origem, sem caminho
ou parâmetros, e permite validar a chave restrita do Picker. O aplicativo
não grava access token em armazenamento local ou URLs próprias. O SDK do
Google passa esse token ao iframe oficial por URL interna; não registrar,
exportar ou publicar URLs desse iframe. Renovação e segredo ficam no servidor.

## Troca, atualização e edições

“Atualizar dados” conserva arquivo e revisão do vínculo. “Trocar arquivo da
ficha” confirma uma fonte nova, aumenta a revisão e invalida o resultado de
análise anterior. O antigo arquivo não é alterado nem apagado. Uma resposta
em andamento carrega a revisão original e é descartada se a fonte mudou.

Edição de jogo não é efeito colateral de cadastrar ou reconectar. Primeira
fase não escreve nenhuma célula. A candidata para a etapa 8 é alteração de
recurso atual, mas **nenhum campo está aprovado para escrita ainda**: falta
provar validação, efeitos e concorrência no produtor. Salário, emissão, XP,
Classe, fórmula e aprovação ficam indisponíveis sem contrato próprio.

O mesmo vale para parâmetros iniciais de uma cópia na etapa 7: não escrever
nível/XP por endereço fixo sem identificar versão e lógica da ficha. Copiar
arquivo não ativa automaticamente gatilhos instaláveis. Precisamos de testes
nativos da planilha, não só de uma resposta `200` da API.

## Limites da prova executável

`pesquisa/carteira_viva/` modela as decisões acima com respostas fictícias.
Tem permissões, estados de uso único, sessão, cifra, confirmação transacional,
revisão de fonte e persistência para ensaiar um reinício. Não contém servidor
HTTP, OAuth real, Google Picker, análise completa, exclusão/retenção automática,
transferência de dono nem comandos Discord.

O banco da prova duplica envelopes por vínculo para manter o ensaio pequeno.
Na etapa 2, [conexões, migrações e retenção foram implementadas](BANCO.md)
no pacote separado `src/carteira_viva`, sem promover o laboratório a serviço.
A prova é
de um processo síncrono: não comprova vários workers, falhas de disco ou carga.
Na etapa 3, substituir identidades fornecidas pelos testes por adaptadores
autenticados. Não expor os métodos da prova diretamente como rotas públicas.

## Resultado Google e cache XLSX

Na leitura autenticada da etapa 4, Sheets entrega valores calculados e erros
efetivos. Resultados vazios normais podem ser omitidos; continuam vazios na
normalização, sem completar entradas por suposição. Não inferir cache XLSX a
partir dessa ausência. No arquivo XLSX, a guarda de fórmula sem resultado
calculado permanece obrigatória. A paridade nativa dos 18.393 campos e achados
foi conferida conforme NATIVO-ETAPA-4.md. Não baixar as fórmulas extensas da
ANALISE para tentar tratar os dois transportes como o mesmo formato.
