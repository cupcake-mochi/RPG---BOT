# Política de privacidade do Guias do Ciclo

Atualizada em 21/10/2026.

Eu sou o Mizuki e mantenho o Guias do Ciclo, o bot da Kal'tsit e da Closure. Aqui está o que ele faz com os dados de quem conversa com elas. Qualquer pedido sobre isso, me chame no servidor da guilda ou comente nesta página.

## O que o bot lê

O bot vê as mensagens dos canais em que está, mas só usa as que chamam uma das duas, pelo nome, por menção ou respondendo a uma mensagem delas, e a mensagem seguinte de quem ela acabou de responder, se vier em até 3 minutos e ninguém tiver falado no meio. O resto não é guardado nem enviado para lugar nenhum. Ele não lê mensagem privada.

## O que fica guardado

Quando você chama uma delas, o texto da mensagem fica guardado até as 4h30 da manhã seguinte, no horário de Brasília. Nessa hora o bot tira do texto alguns fatos curtos sobre você e apaga o resto. Pedidos atendidos localmente só com links públicos não entram nessa leitura diária.

Para retomar depois de um reinício, o bot também guarda as últimas 12 falas da conversa por canal e personagem, incluindo as respostas. Esse histórico deixa de ser usado após 30 minutos sem conversa ou às próximas 4h30, o que vier primeiro. A limpeza roda a cada minuto enquanto o bot está ligado e na retomada. O histórico usa a mesma proteção do banco; apagar seus dados também remove a conversa recente em que você participou.

Quando você envia um link do YouTube numa conversa com as guias, o bot pode consultar o título e o canal do vídeo. Só o identificador do vídeo é enviado nessa consulta, sem seu nome nem o restante da mensagem. Esses metadados acompanham a conversa recente. Nomes de anexos e prévias textuais podem acompanhar o pedido. Quando a leitura de mídia estiver habilitada no canal, o bot pode baixar e enviar ao acesso pago do Google uma mídia da mensagem: imagem reduzida, até três quadros de uma animação ou áudio de até 30 segundos. Isso inclui links diretos para arquivos GIF hospedados no Discord. Nos GIFs enviados pelo seletor, o bot usa a prévia associada ao link para buscar o arquivo no Klipy, Tenor ou Giphy, ou na cópia servida pelo Discord. Se a prévia do Tenor estiver ausente ou não trouxer um arquivo compatível, o bot pode consultar a página pública daquele GIF para localizar a mídia. Essas consultas enviam apenas o endereço da página ou do arquivo, sem seu nome nem o restante da conversa. Se a prévia representar o GIF como vídeo, só os quadros da animação são usados, sem áudio. Arquivos são preparados temporariamente em memória, sem guardar o binário no banco ou em arquivo local; não são reenviados nos próximos turnos. Uma nota sobre o tipo de mídia e verificações simples do arquivo acompanha o histórico recente, e a resposta pode conter uma descrição ou transcrição. Quando o trecho processado está completamente sem som, o bot pode informar isso localmente, sem enviar o áudio ao Google. O arquivo não entra na reflexão diária. Links do YouTube continuam sendo identificados pelo título/canal, sem reprodução. O bot não entra em chamadas de voz.

Depois disso fica guardado:

- até 15 fatos sobre você por contexto de servidor e mundo, como o personagem que você joga, a sua mesa e como prefere ser respondido. Você também pode escrever os seus com /meu_fato;
- seus pronomes, se você informar;
- seu ID do Discord e quando você chamou cada uma, para contar em quantos dias vocês já conversaram e reconhecer pergunta repetida. Junto fica uma nota da paciência de cada uma com você.

As últimas respostas delas em cada canal também ficam guardadas, para não repetirem a mesma frase.

Quem administra o servidor pode habilitar reações e opiniões adultas não gráficas com /responder_nsfw e limitar a um canal com /nsfw_canal. A opção começa desativada e só vale nos canais marcados como NSFW no Discord. Essa preferência e o canal escolhido ficam no banco por servidor, inclusive após reiniciar, até serem alterados por quem administra. Ela não muda a leitura de mensagens, o tratamento de mídia nem os prazos de conversa descritos acima. Não autoriza encenação sexual e não desativa as restrições do Google.

Quem tem Gerenciar servidor também pode cadastrar até 20 atalhos de comandos com /atalho. O bot guarda o ID do servidor, o nome curto e o comando ou guia de destino, até o atalho ser alterado ou removido. Os nomes só aceitam letras, números e sublinhado; os destinos vêm de uma lista de comandos públicos. Os atalhos aparecem na página Abreviações da ajuda daquele servidor e podem acompanhar o contexto enviado ao Google para as guias explicarem como usar os comandos. Eles são configurações do servidor, não fatos pessoais nem aprovações de ficha. /apagar_meus_dados não remove configurações compartilhadas do servidor; quem administra pode retirar um atalho por /atalho remover.

O bot não guarda fato sobre saúde, dinheiro, religião, política, relacionamento, idade, endereço, contato ou outro dado sensível, nem fato sobre outra pessoa. Tem um filtro para isso e ele pode errar. Se aparecer na sua lista algo que não devia, apague com /esquecer_fato e me avise.

## Idioma, mundo e cargos autorizados

O bot guarda por servidor o idioma, a opção de lore Nova Terra, até 20 IDs de cargos autorizados e uma revisão da configuração. Esses dados permanecem até serem alterados por quem administra ou removidos pelo mantenedor. Os cargos delegados podem mudar idioma e lore; cadastrar ou remover esses cargos exige Administrador ou Gerenciar servidor. Essa configuração não concede permissões no Discord.

Cada servidor começa com a base original de Arknights, exceto os três servidores da campanha definidos pelo mantenedor, que começam com Nova Terra. A opção pode ser ligada ou desligada por `/lnt`. As regras do RPG são uma base separada. O contexto dos fatos pessoais considera tanto o servidor quanto o mundo escolhido. Pronomes continuam sendo uma preferência pessoal compartilhada. Fatos antigos sem origem ficam disponíveis apenas na consulta de legado e não entram automaticamente nas conversas.

Ao mudar idioma ou mundo, o histórico recente do canal deixa de ser usado na próxima interação atendida. Os fatos dos outros contextos continuam guardados, mas não são incluídos naquela resposta. A leitura diária pode agrupar mensagens de vários contextos numa chamada ao Google, usando identificadores temporários diferentes e instrução para manter os fatos separados. O bot não envia os IDs reais dos servidores nessa leitura. A opção de idioma da Arquivista é independente.

Os pedidos reconhecidos de links do livro, modelo oficial de ficha, privacidade e termos podem ser atendidos localmente. Esse caminho não chama o modelo nem analisa a mídia da mensagem.

## Para onde os dados vão

O texto das respostas é gerado pelo Gemini, um serviço do Google. A cada resposta vão para lá a mensagem em que você chamou a personagem, as mensagens recentes dessa conversa, seu nome de exibição, seus pronomes e os fatos usados naquela resposta. Seu ID do Discord não vai.

O bot tenta primeiro a cota gratuita do Gemini. Pelos termos do Google, o que passa por ela pode ser usado pelo Google para desenvolver e melhorar os serviços dele e pode ser lido por revisores humanos, já separado da conta de quem enviou. Quando a cota gratuita não responde, sempre na leitura das 4h30 e nos pedidos em que uma mídia é enviada para análise, o bot usa o acesso pago, em que o Google não faz esse uso.

Os dados não são vendidos nem repassados a mais ninguém.

## Como ver e apagar

/meus_dados mostra os fatos do contexto atual, e só você vê a resposta. Use a opção legado para consultar fatos antigos sem origem, ou todos para receber um arquivo privado com seus fatos de todos os contextos. /esquecer_fato também permite excluir um fato do legado. /esquecer_fato tira um fato, /meus_pronomes muda os pronomes e /apagar_meus_dados apaga tudo na hora. Se você saiu do servidor, me peça que eu apago.

O que já foi enviado ao Google não é apagado por esses comandos e segue os prazos do Google.

## Mudanças

Quando este texto mudar, a data do começo muda junto.

---

# Guias do Ciclo privacy policy — English

Updated October 21, 2026. Maintainer: Mizuki. Contact me through the guild server or a comment on this page for questions or deletion requests.

## Messages and media

The bot processes messages that call Kal’tsit or Closure by name, mention or reply, and an eligible immediate follow-up within three minutes. Unrelated messages are not retained or sent to the model. The bot does not read direct messages or join voice calls.

Accepted conversation text is retained until the next daily cleanup at 04:30 Brasília time. That process extracts brief personal facts and deletes the source text. Locally handled public-link requests are excluded from that extraction. To recover conversations after a restart, up to 12 recent turns per channel and character are retained until 30 minutes of inactivity or the next daily cleanup, whichever comes first. Cleanup runs every minute while online and on startup. Deleting your data also removes recent conversations in which you participated.

YouTube links may be checked for their title and channel using only the video identifier. The bot does not play the video. Attachment names and previews may accompany a request. Where media reading is enabled, one item may be downloaded and sent to Google’s paid model service: a reduced image, up to three animation frames, or up to 30 seconds of audio. GIFs may be obtained through Discord, Klipy, Tenor or Giphy previews; a public Tenor page may be consulted if its preview is missing or unsuitable. These requests send only the page or file address to the hosting service. A video preview of a GIF is processed as animation frames, without sound.

Media files are prepared temporarily in memory, without retaining the binary in the database or local files or resending it on later turns. A media-type note, basic checks and any resulting description or transcript may appear in the recent conversation. Completely silent audio may be identified locally without sending it to Google. The media file is excluded from daily fact extraction.

## Stored preferences and facts

The bot stores up to 15 brief personal facts per server-and-world context, your pronouns if provided, your Discord user ID and interaction dates, repeat-question information and each character’s patience state. Recent character replies also help avoid repetition. Facts may be added with `/meu_fato`. Sensitive facts, facts about other people and information about health, finances, religion, politics, relationships, age, address or contact details are filtered. Filters can make mistakes; remove unwanted facts and contact the maintainer.

Server settings include language, Nova Terra mode, up to 20 delegated role IDs, a configuration revision, public command shortcuts and adult-response settings. They persist until changed by an authorized person or removed by the maintainer. Up to 20 public shortcuts may be configured; their names and destinations may be included in conversational context to explain commands. Adult responses start disabled, apply only in Discord age-restricted channels, allow non-graphic reactions and opinions, and do not authorize sexual roleplay or disable Google’s restrictions.

Original Arknights is the default world outside the maintainer’s three campaign servers. `/lnt` can enable or disable Nova Terra, including in those servers. Tabletop rules remain a separate source. Facts are scoped to the server and selected world; pronouns are shared personal preferences. Legacy facts without an origin are retained for private access but are not automatically injected into conversations. Changing language or world invalidates the channel’s recent context on its next accepted interaction. Other contexts’ facts remain stored but are not included in that reply. Daily extraction may batch different contexts in one Google request, using separate temporary identifiers and instructions to keep them separate, without sending real server IDs. Arquivista language settings are independent.

Administrators or members with Manage Server may delegate language and lore controls. Delegated roles cannot delegate further or gain Discord permissions through this feature. Personal data deletion does not remove shared server settings.

## Services receiving data

Ordinary conversational replies use Google Gemini. Requests may include your message, recent conversation, display name, pronouns and facts used for that reply, without your Discord ID. The service first tries its free allowance, whose data may be used by Google to improve its services and reviewed by humans under Google’s terms. Paid access is used when that allowance does not respond, for daily extraction and for media analysis; Google does not use that paid data for those improvement purposes. Data is not sold or passed to other parties beyond the services described here.

Recognized requests for the rulebook, official sheet template, privacy policy or terms can be answered locally using public links, without a model or media request.

## Access and deletion

`/meus_dados` privately shows facts in the current context. Its legacy option accesses unscoped older facts; its all-contexts option exports your own facts in a private file. `/esquecer_fato` removes a fact, including a legacy fact when selected. `/meus_pronomes` changes pronouns. `/apagar_meus_dados` deletes your personal data across contexts. If you have left the server, contact the maintainer. These commands do not erase information already sent to Google; Google’s retention terms apply there.

The date at the beginning changes when this policy is updated.
