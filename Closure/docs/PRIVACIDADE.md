# Política de privacidade do Guias do Ciclo

Atualizada em 15/10/2026.

Eu sou o Mizuki e mantenho o Guias do Ciclo, o bot da Kal'tsit e da Closure. Aqui está o que ele faz com os dados de quem conversa com elas. Qualquer pedido sobre isso, me chame no servidor da guilda ou comente nesta página.

## O que o bot lê

O bot vê as mensagens dos canais em que está, mas só usa as que chamam uma das duas, pelo nome, por menção ou respondendo a uma mensagem delas, e a mensagem seguinte de quem ela acabou de responder, se vier em até 3 minutos e ninguém tiver falado no meio. O resto não é guardado nem enviado para lugar nenhum. Ele não lê mensagem privada.

## O que fica guardado

Quando você chama uma delas, o texto da mensagem fica guardado até as 4h30 da manhã seguinte, no horário de Brasília. Nessa hora o bot tira do texto alguns fatos curtos sobre você e apaga o resto.

Para retomar depois de um reinício, o bot também guarda as últimas 12 falas da conversa por canal e personagem, incluindo as respostas. Esse histórico deixa de ser usado após 30 minutos sem conversa ou às próximas 4h30, o que vier primeiro. A limpeza roda a cada minuto enquanto o bot está ligado e na retomada. O histórico usa a mesma proteção do banco; apagar seus dados também remove a conversa recente em que você participou.

Quando você envia um link do YouTube numa conversa com as guias, o bot pode consultar o título e o canal do vídeo. Só o identificador do vídeo é enviado nessa consulta, sem seu nome nem o restante da mensagem. Esses metadados acompanham a conversa recente. Nomes de anexos e prévias textuais podem acompanhar o pedido. Quando a leitura de mídia estiver habilitada no canal, o bot pode baixar e enviar ao acesso pago do Google uma mídia da mensagem: imagem reduzida, até três quadros de uma animação ou áudio de até 30 segundos. Isso inclui GIFs enviados pelo seletor do Discord: o bot usa a prévia associada ao link para buscar o arquivo no Klipy, Tenor ou Giphy, ou na cópia servida pelo Discord. Essa busca envia apenas o endereço da mídia, sem seu nome nem o restante da conversa. Se a prévia representar o GIF como vídeo, só os quadros da animação são usados, sem áudio. Arquivos são preparados temporariamente em memória, sem guardar o binário no banco ou em arquivo local; não são reenviados nos próximos turnos. Uma nota sobre o tipo de mídia e verificações simples do arquivo acompanha o histórico recente, e a resposta pode conter uma descrição ou transcrição. Quando o trecho processado está completamente sem som, o bot pode informar isso localmente, sem enviar o áudio ao Google. O arquivo não entra na reflexão diária. Links do YouTube continuam sendo identificados pelo título/canal, sem reprodução. O bot não entra em chamadas de voz.

Depois disso fica guardado:

- até 15 fatos sobre você, como o personagem que você joga, a sua mesa e como prefere ser respondido. Você também pode escrever os seus com /meu_fato;
- seus pronomes, se você informar;
- seu ID do Discord e quando você chamou cada uma, para contar em quantos dias vocês já conversaram e reconhecer pergunta repetida. Junto fica uma nota da paciência de cada uma com você.

As últimas respostas delas em cada canal também ficam guardadas, para não repetirem a mesma frase.

O bot não guarda fato sobre saúde, dinheiro, religião, política, relacionamento, idade, endereço, contato ou outro dado sensível, nem fato sobre outra pessoa. Tem um filtro para isso e ele pode errar. Se aparecer na sua lista algo que não devia, apague com /esquecer_fato e me avise.

## Para onde os dados vão

O texto das respostas é gerado pelo Gemini, um serviço do Google. A cada resposta vão para lá a mensagem em que você chamou a personagem, as mensagens recentes dessa conversa, seu nome de exibição, seus pronomes e os fatos usados naquela resposta. Seu ID do Discord não vai.

O bot tenta primeiro a cota gratuita do Gemini. Pelos termos do Google, o que passa por ela pode ser usado pelo Google para desenvolver e melhorar os serviços dele e pode ser lido por revisores humanos, já separado da conta de quem enviou. Quando a cota gratuita não responde, sempre na leitura das 4h30 e nos pedidos em que uma mídia é enviada para análise, o bot usa o acesso pago, em que o Google não faz esse uso.

Os dados não são vendidos nem repassados a mais ninguém.

## Como ver e apagar

/meus_dados mostra o que o bot guarda sobre você, e só você vê a resposta. /esquecer_fato tira um fato, /meus_pronomes muda os pronomes e /apagar_meus_dados apaga tudo na hora. Se você saiu do servidor, me peça que eu apago.

O que já foi enviado ao Google não é apagado por esses comandos e segue os prazos do Google.

## Mudanças

Quando este texto mudar, a data do começo muda junto.
