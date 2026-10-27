# Carteira no navegador

Etapa 6 · 26/10/2026. Branch `codex/carteira-viva-etapa-6`, base `52ca144`
da etapa 5/PR 82. Implementação concluída, PR 83 em rascunho; **não publicada**. PRs dependentes
77–83 não foram mescladas. O bot em produção permanece separado.

## Uso

O título do cartão da ponte opcional abre `/carteira/servidor/personagem`.
A pessoa entra com Discord e precisa participar daquele servidor. O link
sozinho não dá acesso. “Público” significa outros membros do servidor, sem
indexação global. A galeria mostra até 20 opções por página, o responsável,
a apresentação permitida e o horário da leitura. Abrir um cartão próprio ou
como revisor permite atualização sob demanda; a lista não lê todas as fichas.

Detalhes e análise têm área privada, com as mesmas capacidades do Discord.
A análise reaproveita o motor e o apresentador existentes, inclusive as cores
locais de erro/pendência. O navegador recebe só a página solicitada da análise,
sem o snapshot completo. Navegar revalida cargos, fonte, leitura e campanha;
não é uma troca local entre páginas privadas já guardadas no HTML.

A imagem é baixada de rota autenticada do mesmo serviço, com autorização
atual. O arquivo continua cifrado fora do SQL; não há URL pública de mídia nem
parâmetro para buscar uma prévia privada. URL Google aparece só após consulta
privada autorizada e o próprio Google continua verificando seu acesso.

Textos PT/EN, controle de idioma apenas da página, foco de teclado, estados de
carregamento e tela pequena. Troca de arquivo/apresentação permanece no Discord;
esta entrega é de leitura. Nenhuma célula é escrita e nenhuma análise aprova a
ficha por si só. Valores livres são texto, sem HTML arbitrário ou links vindos
do perfil. Botão Encerrar sessão continua disponível durante uma consulta.

## Sessão

- OAuth Discord identify, Authlib/PKCE e o mesmo retorno já configurado.
  O dispatcher distingue o estado da Carteira dos fluxos de conexão Google.
- Cookie opaco HttpOnly, SameSite=Lax, Secure e prefixo __Host- em HTTPS.
  Nenhum bearer de serviço ou token OAuth vai ao frontend.
- Estado OAuth de uso único, ligado ao cookie, com dez minutos. Cookie e CSRF
  são trocados após login. Um state de outro navegador não encerra a sessão atual.
- Trinta minutos sem uso e máximo de oito horas; uso não renova o máximo.
  Logout/expiração são reconferidos após esperas e antes da resposta. Logout
  durante OAuth não permite que o callback recrie a sessão.
- Participação/cargos são conferidos nas ações. Saída detectada encerra a
  sessão; perda apenas de cargo recusa o privado. Dados já vistos ou copiados
  não podem ser recolhidos. A interface limpa o privado ao perder acesso,
  expirar, sair e voltar de página restaurada pelo navegador.
- Sessões/PKCE/CSRF cifrados no schema 5; cookie e estado têm hashes separados.
  Sessões não entram no backup e são encerradas em reinício, restore, rotação
  de chave e exclusão global dos dados do próprio usuário. Cadastro e conexões Google confirmadas permanecem.
- Até 512 sessões e dez inícios de login por sessão anônima. Limites locais,
  não uma garantia de proteção global contra abuso; rever na etapa 9.

O serviço usa um único banco/worker, sem cópia sincronizada no frontend.
Respostas privadas/no-store, Vary Cookie, sem CORS, CORP same-origin e CSP
restrita a arquivos próprios na Carteira. A conexão/Picker conserva sua CSP
separada. Formulários exigem Origin exata e CSRF; identidade nunca vem de JSON.

## Rotas

- GET `/carteira/{servidor}` e `/{personagem}`: HTML genérico, sem dados da ficha.
- GET `/api/carteira/{servidor}/sessao`: estado do próprio login e CSRF.
- POST `/api/carteira/{servidor}/entrar`: inicia identify; não pede Google.
- POST `/api/carteira/sair`: invalida a sessão no servidor.
- GET `/api/carteira/{servidor}/galeria`: projeção básica por dono/cursor.
- GET `/api/carteira/{servidor}/personagens/{id}`: cartão básico salvo.
- POST `.../{id}/atualizar`, `/detalhes`, `/analisar`, `/analise`: ações fechadas,
  autorizadas. Atualizar reutiliza até 60 s; analisar relê; analise abre salva.
- GET `.../{id}/imagem`: bytes WebP, somente apresentação pública permitida.

O início do login aceita só personagem e idioma, ambos opcionais.
O método de análise aceita só página e idioma. Não recebe usuário, campanha,
regra, aprovação, nome de método do banco ou destino de escrita.

## Testes e situação

- 40 regressões novas: 18 de sessão, 21 HTTP e uma do link do cartão Discord.
  HTTP/SQLite/cifra reais com provedores fictícios. Cobrem estado/cookie/CSRF,
  login em outro navegador, troca de idioma, logout/expiração durante leitura
  ou callback, mudança de cargo/fonte/campanha e projeções sem snapshot.
- Primeira bateria nova: 37/37, 48,613 s. Depois dos ajustes de texto/idioma e
  link, conjunto final direcionado: 60/60, 79,765 s, incluindo interface Discord.
- CI completo do código final `0c9a15f760bc3d3d437e2fa85b231223306a7576`:
  **1.282 executados, 1.281 aprovados, um online opcional pulado e zero falhas**,
  261,589 s. [Run 40423286577](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40423286577).
  Execução normal de unittest no Linux, com núcleo e dependências do serviço.
- Navegador real, demonstração com três personagens e duas identidades fictícias:
  troca de personagem, detalhes, análise e segunda página, PT/EN, idioma mantido
  após login, galeria vazia, cartão alheio sem ações privadas e logout passaram.
  Logout limpou texto privado e link Google do DOM. Galeria vazia conserva a URL
  sem personagem, inclusive após recarregar. Teclado alcançou o seletor de idioma
  e a consulta moveu foco para o título. Conferência não equivale a auditoria
  completa com leitor de tela.
- Tela de 390×844 conferida, sem rolagem horizontal (documento 390 px), lista
  compacta e botões de pelo menos 44 px. Capturas locais de computador/celular,
  somente dados fictícios. Não foi teste em celular físico.
- Revisão de clareza: nomes/datas aparecem como texto, sem `<@…>`/`<t:…>` do
  Discord; o rodapé web não promete o prazo dos botões Discord. Preferência
  PT/EN não traduz o texto livre do jogador nem altera configuração do servidor.

### Login real e limpeza

OAuth identify no app oficial das Guias passou em loopback, com a conta
principal já conectada. Participação, nome e cargos vieram da API Discord real;
não foi iniciado outro Gateway ou instalado comando temporário. Três personagens
fictícios ficaram num banco isolado do piloto. A leitura Google foi substituída
por dados fictícios, sem credencial funcional ou acesso a planilha real.

Passaram: login e cookie, galeria, atualização do nome do cartão, análise privada
e navegação para a página 2 de 5. A ficha sintética é intencionalmente incompleta:
resumo com zero erros e 61 pendências, sem fingir aprovação. Logout limpou campos
e link privados; outra aba voltou a exigir login após recarregar.

As abas compartilham a sessão da Carteira. Abrir outra aba do Discord não troca
a identidade dessa sessão: o nome conectado permanece visível, e é preciso sair
da Carteira para trocar de conta. Por isso, esta prova nativa usou **uma conta
Discord real**, sem declarar uma segunda identidade OAuth testada. A visão de
membro comum foi validada na demonstração e nos testes HTTP; a prova com duas
contas reais da etapa 5 é separada.

Após o ensaio: serviço parado e porta loopback fechada; três personagens e sua
conexão fictícia removidos. Conferidos zero personagens, conexões, sessões,
leituras e análises; integrity_check `ok`. Registro mínimo de remoções preservado
no diretório privado, fora do Git. Abas do usuário restauradas. Não houve nova
autorização Google, chamada paga, mudança de segredo, escrita em ficha ou
interferência na Discloud. Captura nativa fica privada, sem OAuth/código/token.

A prova Google real anterior é NATIVO-ETAPA-4.md, não uma nova aprovação de
fichas avançadas pelo navegador.

### Última guarda

Na revisão de limpeza foi reproduzido um defeito: apagar os dados de um usuário
não encerrava suas sessões web já abertas. Corrigido em `0c9a15f`: a exclusão
agora retira essas sessões na mesma transação, preservando a sessão de outro
usuário. Regressão falhou antes e passou depois; 18/18 testes de sessões após a
correção. O CI completo desse commit passou com os 1.282 testes registrados
acima. O checkpoint anterior `9da98dd` teve 1.281/1.280/1 opcional, zero falhas
em 181,852 s (run 40422158315); a regressão final acrescenta o caso restante.

O ensaio local precisou aguardar a inicialização do processo após mudanças de
backend. Foi usado um runner de laboratório com tick no loop; esse ajuste não
entra no serviço e não é solução de desempenho para produção. O disco externo
apresenta lentidão. Medir rede, leituras e repetição de consultas de participação
no host da etapa 9, sem reduzir a conferência de permissões depois das esperas.

Manifesto de produção continua com 90 arquivos, sem Carteira; não houve novo
ZIP/deploy. HTTPS persistente, campanha/idioma autoritativos entre bot e serviço,
saída de membros por eventos, medição de host, restore e baterias nativas
avançadas continuam requisitos antes da publicação. Não houve modelo pago,
Gateway duplicado ou alteração de ficha oficial/jogador.

## Depois desta etapa

Restarão quatro etapas: 7 (modelo do servidor), 8 (edições permitidas),
9 (operação/recuperação/escala) e 10 (publicação). O plano recomenda
**GPT-6 Astra · Alto** para validar o contrato da etapa 7 antes de implementar
cópias. Não alterar modelos oficiais e não presumir que cópia ativa gatilhos.
