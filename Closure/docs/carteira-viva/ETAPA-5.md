# Galeria e cartões no Discord

Etapa 5 · 26/10/2026. Branch `codex/carteira-viva-etapa-5`, baseada na etapa 4
(`df703ec`, PR 81, CI verde). A ponte continua opcional e fora do pacote do bot
em produção. Esta entrega não é publicação da Carteira.

## O que o jogador pode fazer

- `/personagens [jogador]` abre a galeria daquele jogador no servidor atual.
  A lista tem até 20 personagens por página e não consulta o Google para cada
  nome. Escolher um cartão próprio permite atualizar uma ficha por vez.
- `/personagem ver` abre um cartão; os botões de detalhes e análise respondem
  em privado. Nome, origem e caminho vêm da última leitura válida, quando
  disponíveis. O cartão informa a hora e avisa quando precisa de atualização.
- `/personagem analisar` relê a fonte e usa o motor determinístico existente.
  A cor escolhida para o cartão não muda as cores de erros da análise.
- `/personagem editar_cartao` abre um formulário de título, frase, cor e campos
  visíveis. Primeiro aparece uma prévia privada; só **Salvar cartão** confirma.
  Uma edição antiga não sobrescreve um cartão ou vínculo que mudou.
- `/personagem imagem` recebe um anexo estático PNG, JPEG ou WebP de até 1 MiB.
  A imagem também passa por prévia e confirmação. Não recebe URL arbitrária.
- Cadastrar, trocar arquivo e reconectar conservam o fluxo da etapa 3.
- `/personagem cargo_revisor` permite ao dono do servidor ou administrador
  adicionar/remover um cargo de revisão. Essa capacidade não permite editar.

Também há `/characters` e `/character`, com os subcomandos `register`,
`replace_sheet`, `reconnect`, `view`, `analyse`, `edit_card`, `image` e
`reviewer_role`. As respostas usam o idioma configurado no servidor; o nome e
os textos escritos pelo jogador são preservados. Não há tradução por modelo.
Os atalhos de conexão anteriores permanecem compatíveis.

Idade e clã ainda não vêm da exportação atual da ficha. São campos opcionais
de apresentação no contrato; não se inferem esses valores de texto livre nem
se afirma que já estão disponíveis como edição no formulário do Discord.
O nome ainda não tem link para a Carteira web: essa página entra na etapa 6.
O link Google aparece somente na consulta privada e continua sujeito à
permissão do próprio Google.

## Privacidade e confirmação

Qualquer membro pode ver somente a projeção básica permitida pelo servidor e
pelo jogador. Não há arquivo Google, campos completos ou resultado mecânico
na resposta da galeria. Responsável, dono do servidor, administrador e cargo
revisor explícito podem consultar os detalhes. Somente o responsável altera a
apresentação ou troca o arquivo. `Manage Guild` e cargos de idioma/lore não
herdam revisão. Nenhuma célula da planilha é escrita.

Cada ação consulta a identidade/cargos atuais pelo Discord. Um 404 de membro
registra saída; falha de rede não é tratada como saída. Clique de outro usuário
recebe orientação para abrir seus próprios controles. Prévia vale dez minutos,
é ligada ao ator/servidor/personagem e exige a mesma versão de perfil, máscara
pública, configuração e fonte na confirmação. Abrir o formulário só reapresenta
valores já recebidos pelo responsável; enviar e salvar revalidam tudo.

Páginas privadas de análise revalidam acesso, fonte, leitura e campanha a cada
navegação. Não se pode recolher texto ou link que alguém já viu ou copiou.
Mensagens antigas e anexos Discord não se atualizam nem desaparecem sozinhos
quando o perfil muda; abra uma galeria nova para a apresentação atual. Menções
inseridas pelo jogador são neutralizadas e envios usam `AllowedMentions.none`.

## Imagens e armazenamento

A decodificação roda em processo separado sem credenciais, com dois trabalhos
simultâneos, prazo de 20 s, até quatro milhões de pixels, limite de memória de
256 MiB e CPU de 3 s no Linux. Animação e formatos não permitidos são recusados.
A saída é WebP de até 1024 × 1024, sem metadados. Pillow 12.3.0 está fixada no
requirements do serviço separado.

Os arquivos ficam cifrados na pasta privada `imagens/`, ao lado do banco.
Identificadores opacos, pasta 0700 e arquivos 0600. O bot baixa a imagem numa
rota autenticada e envia um anexo ao Discord; não há endpoint público nem
URL do Google/CDN armazenada como fonte permanente.

Há teto local de 128 MiB de arquivos cifrados, dez imagens por usuário/dia e
cinco prévias abertas. Arquivo órfão com mais de 24 h é eliminado; imagem atual
ou de prévia válida é preservada. Uma falha entre salvar arquivo e confirmar a
prévia pode deixar órfão até a limpeza. Isso não é teste de capacidade global
nem substitui a etapa 9 de operação/limites.

O backup SQLite **não inclui as imagens**. Para recuperação, parar o serviço,
copiar cadastro, registro atual de remoções e a pasta cifrada de imagens para
armazenamento privado. Guardar as chaves separadamente. Prévia e OAuth abertos
não são restaurados. A rotação atual reescreve os envelopes do banco, não os
arquivos de imagem: manter as chaves antigas enquanto qualquer imagem/backup
precisar delas. Não descartar uma chave só porque a migração SQL passou.
Há teste de cópia/restauração da mídia com chave atual + anterior; recuperação
operacional completa de toda a instalação continua para a etapa 9.

## Validação e limites

Testes locais novos: banco/cifra/migração 3→4, prévias concorrentes, edição
antiga, privacidade, leitura sob demanda, remoção de cargos, saída/retorno,
listas grandes, botões/modais PT/EN, limites Discord, imagem falsa/animada,
excesso de pixels, falha do worker, orçamento e restauração da mídia.
Google/Discord são simulados nessa suíte; HTTP, banco, cifra, worker e motor
são reais. A análise reaproveita o JSON e o apresentador existentes sem alterar
os dados antes da decodificação.

A fixture histórica de migração v1 foi corrigida: agora remove também as novas
tabelas v4 antes de simular um banco antigo. Nenhuma expectativa mecânica foi
alterada para deixar os testes verdes.

Suíte completa local: **1.237 executados, 1.236 aprovados, um opcional pulado,
zero falhas**, 744,951 s. Reteste final da interface: **19/19**; inclui uma
regressão acrescentada depois da coleta completa. Portanto são **1.238 testes
distintos** no código final, 60 novos nesta etapa. O CI final deve confirmar
a coleta completa antes de apresentar esse total como execução única.

Piloto Discord: duas contas reais, 23 personagens sintéticos e Google fictício.
Galeria própria/alheia/vazia, duas páginas, PT/EN, prévia/salvamento e análise
privada com navegação passaram. A conta comum não recebeu botões privados na
sua galeria alheia; tentativa direta de análise foi recusada. Não é prova de
leitura de 23 planilhas reais. Não houve escrita Google ou chamada de modelo.
A limpeza e a volta da instância hospedada serão registradas ao encerrar.
Não declarar duas contas validadas, navegação real ou publicação a partir de
AsyncMocks. O piloto nativo básico de leitura Google já passou na etapa 4;
não foi repetido nem convertido em prova nativa de cenários avançados.

Pendentes: Carteira web (6), modelo do servidor (7), edições permitidas (8),
operação/escala/recuperação (9), publicação final (10), cenários nativos ainda
não observados e sincronização autoritativa de campanha entre hosts. Sem
merge dos PRs dependentes, sem chamadas pagas e sem mudança nas fichas oficiais.
