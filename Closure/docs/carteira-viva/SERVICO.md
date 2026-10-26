# Rodar a conexão de fichas

Serviço separado do bot. Ainda não está publicado nem configurado para contas
reais. Não substituir o app das Guias por este serviço.

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
Ela oferece cadastrar, trocar arquivo e reconectar no grupo `/personagem`;
os links são privados e exigem a mesma conta Discord. Respostas PT/EN seguem
o idioma da interação. Traduções dos nomes e integração com o idioma do
servidor entram na etapa 5; não anunciar esses comandos como disponíveis.

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
- O empacotador do bot continua excluindo a Carteira. Não há ZIP de site
  pronto para enviar; preparar implantação própria após fechar configuração
  e testes nativos. Atualizar o bot sozinho não publica este serviço.

Authlib 1.9.1 está fixada; o adaptador httpx 0.28.1 foi testado. A biblioteca
avisa que esse adaptador será substituído por httpx2 em versão futura. Rever a
migração antes de atualizar Authlib; não ignorar o aviso em uma atualização.
