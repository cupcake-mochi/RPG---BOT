# Rodar a conexão de fichas

28/10: observação de membro atual com prova do banco para dono/cargo explícito;
privilégios completos quando necessários, sem cache. Perfil simulado do dono:
Discord 1.686→578, Google 183 preservados. Sem endpoint/criação ou publicação.
[Prova e limites](OBSERVACAO-MEMBRO-2026-10-28.md).

28/10: conferência interna integrada a fila/cotas/OAuth, retomada e proteção da
rotação de credencial em cancelamento. Sem endpoint/comando, criação ou escrita.
Schema 7, conforme [conferência no serviço](SERVICO-CONFERENCIA-2026-10-28.md).
Entradas abaixo descrevem o histórico da implementação.

28/10: conferência interna por contrato REST para financeiro/progressão e recibo
cifrado histórico, sem nova rota/comando/schema ou escrita. O custo de progressão
agora é lido da CONFIGURAÇÃO: oito páginas. [Escopo e limites](CONFERENCIA-REST-2026-10-28.md).

28/10: novo transporte interno de grade REST, só financeiro/progressão, com
contexto/cota por GET e versão por página. Ainda sem rota ou criação; composição
no serviço e adaptação de estado/contrato pendentes.
[Escopo e testes](COLETA-REST-2026-10-28.md).

28/10: guarda interna de leitura versionada e páginas sem checkpoint no produtor
estão em teste, sem nova rota/endpoint. A execução do produtor com o escopo
atual ainda depende de adaptador; não habilitar scripts.run nem ampliar acesso
por pressuposição. [Contrato e limites](LEITURA-VERSIONADA-2026-10-28.md).

27/10: a validação de modelo usa sondagem 2. Primeiro lê os metadados de grade;
depois solicita intervalos explícitos para os três históricos financeiros,
entradas/notas de missão e caixas pendentes. Limite físico de 5.000 linhas
por histórico, 512 KiB por resposta Google e timeout HTTP de 15 s, sem relaxamento
de limites. Referência é salva somente após confirmação com versão estável.
Isso não libera criação nem adiciona rotas/escopos de escrita. Ver a
[proposta de inicialização](INICIALIZACAO-PRODUTOR.md).

Etapa 7 parcial: schema 6, comandos `/personagem modelos` e
`/personagem modelo_configurar escolha:...` (`/character templates` e
`/character set_template`). `oficiais` restaura o padrão, `era`/`ciclo`
selecionam oficial e `servidor` abre OAuth/Picker para o administrador.
Salvar escolha não libera cópia nem muda personagens cadastrados.
`/interno/galeria/acao/criar_por_modelo` é uma recusa explícita, sem escrita
Google; não existe opção de configuração para ativar. O cadastro existente
continua em `/personagem cadastrar` ou `/character register`.
O fluxo interno `acao=modelo` conserva cookie, CSRF, prazo de dez minutos e
revalidação de Administrator/dono. A escolha só é gravada na confirmação.
Ver [ETAPA-7.md](ETAPA-7.md) para execução, limites e bloqueios.

A demonstração local inclui links de modelo PT/EN, só com contas e arquivos
fictícios, acessíveis pela página inicial de `--demo`. Não necessita OAuth
privado nem testa acesso Google real. A configuração privada do piloto real
ficou no SSD Linux e não foi recriada no Windows.

Serviço separado do bot. Ainda não está publicado. Piloto local com contas reais concluído
conforme [NATIVO-ETAPA-3.md](NATIVO-ETAPA-3.md). Não substituir o app das Guias por este serviço.

## Demonstração local

Na raiz do repositório:

```sh
Closure/.venv/bin/python -m pip install -r Closure/carteira/requirements.txt
PYTHONPATH=Closure/src Closure/.venv/bin/python -m carteira_viva --demo --porta 8876
```

Abra `http://127.0.0.1:8876/`. O banner identifica contas e arquivos fictícios.
O banco temporário é descartado ao encerrar. Discord, Google e seleção de
arquivo são simulados; o restante percorre as rotas, cookies e banco reais do
serviço. Isso não valida o Google Picker, o consentimento ou o login nativos.
Não publicar essa demonstração em endereço externo.

## Piloto com contas reais

Preparar clientes próprios antes. Não usar credenciais da Arquivista. Ler
[ACESSO-GOOGLE.md](ACESSO-GOOGLE.md), incluindo hospedagem e confirmação de
permissões. No piloto, usar apenas servidor e planilha descartáveis.

As seguintes variáveis devem ser fornecidas pelo ambiente, fora do Git:

| Variável | Conteúdo |
|---|---|
| `CARTEIRA_PUBLIC_ORIGIN` | Origem HTTPS exata, sem caminho nem barra final |
| `CARTEIRA_DATABASE_PATH` | Caminho persistente e privado do banco próprio |
| `CARTEIRA_ENCRYPTION_KEYS` | Chaves Fernet separadas por vírgula; primeira cifra, demais permitem migração |
| `CARTEIRA_SERVICE_TOKEN` | Segredo aleatório de pelo menos 32 caracteres, compartilhado só com a ponte do bot |
| `CARTEIRA_DISCORD_CLIENT_ID` / `CARTEIRA_DISCORD_CLIENT_SECRET` | Cliente OAuth Discord próprio |
| `CARTEIRA_DISCORD_BOT_TOKEN` | Token do bot autorizado nos servidores do piloto; usado para conferir membros/cargos |
| `CARTEIRA_GOOGLE_CLIENT_ID` / `CARTEIRA_GOOGLE_CLIENT_SECRET` | Cliente OAuth Google do tipo web |
| `CARTEIRA_GOOGLE_PROJECT_NUMBER` | Número do mesmo projeto do cliente/Picker |
| `CARTEIRA_PICKER_API_KEY` | Chave restrita às APIs e origens necessárias ao Picker |
| `CARTEIRA_GUILDS` | IDs dos servidores permitidos, separados por vírgula |
| `CARTEIRA_DEV` | `1` apenas para permitir HTTP em loopback no piloto local |

O serviço não lê automaticamente o `.env` das Guias. Não passar segredos em
argumentos de linha de comando, URLs, prints ou mensagens. Guardar as chaves
separadamente dos bancos e backups. Não iniciar dois processos sobre o mesmo
banco: o serviço usa um único processo e uma thread dedicada ao SQLite.

Para o piloto local, a origem pode ser `http://127.0.0.1:8876`, com DEV=1,
e os retornos exatos são:

- `http://127.0.0.1:8876/oauth/discord/retorno`
- `http://127.0.0.1:8876/oauth/google/retorno`

Cadastrar esses retornos nos respectivos clientes. Habilitar Drive, Sheets e
Picker. Configurar o consentimento externo em teste e os usuários de teste.
Restringir a chave do Picker conforme a documentação Google; comprovar seu
funcionamento antes de publicação. O escopo `drive.file` permite leitura e
escrita dos arquivos escolhidos, mas este código só lê. Discord pede apenas
`identify`; a participação é conferida com a API do bot, sem ler mensagens.

Depois de fornecer as variáveis por um mecanismo privado:

```sh
PYTHONPATH=Closure/src Closure/.venv/bin/python -m carteira_viva --porta 8876
```

O piloto local não atende jogadores de outros computadores. Para produção,
precisa de HTTPS, disco persistente, backup/recuperação e origem pública
aprovada. A Discloud Gold inspecionada não comporta o serviço de site segundo
os requisitos documentados; não contratar upgrade automaticamente.

## Ponte com o Discord

`carteira_viva.ponte_discord` é uma extensão opcional **não carregada** pelo
bot atual. A futura integração precisa carregar a extensão e sincronizar os
comandos em um ambiente de teste, sem iniciar bot duplicado de produção.
Além de cadastrar, trocar arquivo e reconectar, a etapa 5 oferece galeria,
cartão, consulta privada, apresentação e cargo revisor. Comandos e nomes
PT/EN: [ETAPA-5.md](ETAPA-5.md). Respostas seguem o idioma configurado no
servidor, com fallback anterior do fluxo de conexão. Links de conexão são
privados e exigem a mesma conta Discord. Não anunciar como recurso publicado.

A ponte usa `CARTEIRA_API_URL` (origem HTTPS do serviço) e
`CARTEIRA_SERVICE_TOKEN`. O piloto loopback pode começar por uma chamada local
controlada ao endpoint `POST /interno/conexoes`, autenticada pelo segredo,
com servidor, usuário, ação e personagem. Essa entrada ainda confere o membro
com o Discord; identidade do navegador nunca é aceita como prova. Não salvar
corpos, cabeçalhos ou links de conexão em relatórios.

## Operação e recuperação

- `/saude` informa somente que o processo responde. Não comprova Google ou Discord.
- Links duram dez minutos. Reiniciar o serviço encerra tentativas abertas;
  conexões já confirmadas permanecem cifradas.
- A limpeza local roda a cada minuto, sem consultar todas as fichas no Google.
- Máximo de oito requisições simultâneas, três tentativas abertas por usuário
  e dez inícios por minuto. Não é medição de capacidade de produção.
- Sem logs de acesso no servidor embutido. Proxy/hospedagem também devem
  ocultar querystrings de conexão/callback, cookies e cabeçalhos de autorização.
- Backup próprio cifrado e registro de exclusões: seguir [BANCO.md](BANCO.md).
  Tentativas OAuth pendentes não entram na cópia de recuperação.
- O SDK do Picker usa URL interna de iframe contendo access token: não
  registrar/exportar URLs desse iframe. A página usa strict-origin para
  fornecer só a origem à chave restrita, sem caminhos/querystrings; layout do
  SDK fica no CSS local, mantendo style-src self e scripts sem unsafe-inline.
- O empacotador do bot continua excluindo a Carteira. Não há ZIP de site
  pronto para enviar; preparar implantação própria após fechar configuração
  e testes nativos. Atualizar o bot sozinho não publica este serviço.

Authlib 1.9.1 está fixada; o adaptador httpx 0.28.1 foi testado. A biblioteca
avisa que esse adaptador será substituído por httpx2 em versão futura. Rever a
migração antes de atualizar Authlib; não ignorar o aviso em uma atualização.

## Leitura completa e análise privada (etapa 4)

Além das variáveis de conexão, fornecer **as duas** para habilitar o motor:

- `CARTEIRA_BOOK_DATA`: diretório `Closure/dados`, com o livro/catálogos compatíveis.
- `CARTEIRA_CAMPAIGNS_PATH`: arquivo local confiável no formato do cadastro de
  campanhas das Guias. Para piloto isolado sem exceções, usar arquivo fictício
  com `{}`. Ausência/erro no arquivo configurado interrompe a análise.

Não criar um cadastro novo a partir de dados enviados pelo jogador. Para
campanha real, o operador precisa fornecer a fonte confiável atual e definir
como ela será atualizada no serviço separado. O formato e o motor existentes
são reaproveitados; não há sincronização automática entre hosts nesta etapa.

Rotas **internas**, chamadas somente pela ponte autenticada do bot:

| POST | Efeito |
|---|---|
| `/interno/personagens/{id}/atualizar` | Consulta sob demanda; cache fresco de até 60 s; devolve metadados |
| `/interno/personagens/{id}/analisar` | Leitura atual + motor + campanha confiável; resultado privado |
| `/interno/personagens/{id}/analise` | Abre resultado salvo após conferir novamente permissões e revisões |

Cabeçalho `Authorization: Bearer <segredo de serviço>` e corpo somente
`{"servidor":"ID do servidor","usuario":"ID do ator da interação"}`. O serviço
revalida o membro pelo Discord; a ponte precisa obter esse ator da interação,
nunca de um campo preenchido pelo usuário. Nenhuma dessas rotas deve ficar
acessível no frontend com o segredo de serviço. Há lista fechada de operações;
não existe método de banco escolhido pelo cliente.

Todos os retornos são privados e sem cache HTTP. Campos completos da ficha
não saem na atualização; a análise expõe somente resultado e proveniência a
quem tem capacidade. Erro de leitura retorna 422, conflito de revisão 409,
acesso recusado 403 e fila/cota local excedida 429. Falhas de provedor devolvem
código genérico, sem URL/corpo/token do Google. O cliente deve explicar a falha,
sem tentar exportação pública como atalho para autorização ausente.

O CLI usa `handler_cancellation=True`. Outro runner aiohttp precisa manter
essa opção para cancelar consultas quando o último cliente desconectar.
As ações SQL já enviadas continuam protegidas por transação/revisões; não
prometer cancelamento de gravação já confirmada.

Resultados e limites; piloto nativo básico passou, avançados pendentes: [ETAPA-4.md](ETAPA-4.md).
Os novos comandos/botões foram integrados na ponte opcional na etapa 5,
sem carregá-la no bot de produção. Não publicar o serviço
no app de bot nem gerar um ZIP de produção por causa desta etapa isolada.

## Galeria interna (etapa 5)

`POST /interno/galeria` aceita servidor, usuário e opcionais dono/depois.
`POST /interno/galeria/acao/cargo_revisor` aceita cargo e permitir booleano.
`POST /interno/galeria/{id}/{acao}` tem lista fechada: cartao, cartao_salvo,
detalhes, analisar, analise_salva, editar, preparar, confirmar, cancelar, imagem
e enviar_imagem. JSON permanece limitado a 16 KiB. Contexto vem da interação
real e o segredo de serviço nunca chega ao navegador/jogador.

Upload é corpo binário de até 1 MiB, com X-Carteira-Servidor e
X-Carteira-Usuario fornecidos pela ponte autenticada. O retorno da ação imagem
é WebP, depois de revalidar membro, responsável e imagem atual. As demais
respostas são JSON privado sem cache, até 8 MiB no cliente da ponte.
A rota de imagem não é uma URL pública para embed: a ponte envia anexo.
Pasta de mídia, permissões, retenção e backup: ETAPA-5.md.

A ponte aceita HTTP apenas com CARTEIRA_DEV=1 e origem loopback explícita;
produção exige HTTPS. Nenhuma porta nova é aberta pelo bot em produção.

## Carteira no navegador (etapa 6)

O mesmo serviço atende `/carteira/{servidor}` e
`/carteira/{servidor}/{personagem}`. O título do cartão da ponte Discord aponta
para a segunda rota. O link não contém credencial nem transfere acesso.
Na demonstração, abra `/carteira/111`: há contas fictícias de responsável e
membro comum e três personagens. Não publicar o demo ou usar dados reais nele.

O login pede apenas identify no Discord e reutiliza o retorno OAuth já
configurado. Não há nova autorização Google para abrir um cartão cadastrado.
A página oferece galeria básica aos membros atuais e detalhes/análise só ao
responsável, admin ou revisor autorizado. Atualizar consulta uma ficha; a lista
não dispara leitura em lote. A análise usa o motor determinístico e entrega
uma página privada de cada vez. A página é de leitura; trocar arquivo ou
apresentação continua no Discord.

A interface aceita PT/EN. Essa preferência acompanha o login e não muda o
idioma configurado no servidor. Sessões não vão para localStorage, URLs ou
backup. Logout/expiração invalidam o acesso no serviço; identidade do ator
nunca vem do corpo JSON. A imagem usa rota autenticada da mesma origem, sem
URL pública. CSP da Carteira não abre iframes nem scripts externos; a tela de
conexão/Picker conserva sua política separada.

Rotas, tempos, limites e evidências: [ETAPA-6.md](ETAPA-6.md).
O cookie de navegador não substitui o bearer da ponte interna. Não distribuir
esse segredo no JavaScript nem abrir os métodos internos ao frontend.

Antes de publicar, continuam obrigatórios HTTPS persistente, disco privado,
backup/restore comprovado e campanha/idioma autoritativos entre bot e serviço.
Os pilotos loopback não provam acesso de celular físico ou hospedagem pública.
