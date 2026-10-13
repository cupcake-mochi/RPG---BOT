# Política de privacidade do bot Closure Lab

Vale a partir de 13/10/2026. Este texto descreve o que o bot faz com dados de quem está num servidor onde ele foi adicionado. O bot é a Kal'tsit e a Closure, as duas guias do servidor para o RPG Ciclo Maldito.

Quem responde pelo bot é o Mizuki, que o criou e o mantém. Para falar com ele, mande mensagem no servidor da guilda ou abra um pedido em <https://github.com/cupcake-mochi/RPG---BOT/issues>.

## O que o bot lê

O bot recebe as mensagens dos canais em que tem permissão de leitura. Ele olha cada uma só para decidir se alguém chamou uma das personagens: pelo nome, por menção ou respondendo a uma mensagem dela. Mensagem que não chama ninguém não é guardada nem enviada a lugar nenhum; dela fica só a hora, por 15 minutos e só na memória do programa, para o bot saber se o canal está quieto ou movimentado.

O bot não lê mensagem privada.

## O que o bot guarda

| O que | Para quê | Por quanto tempo |
| --- | --- | --- |
| O texto da mensagem em que você chamou uma personagem | Tirar, uma vez por dia, fatos curtos sobre você | Até as 4h30 (horário de Brasília) do dia seguinte, no máximo. Depois é apagado |
| Fatos curtos sobre você, até 15 | Ela lembrar de você nas próximas conversas | Até você apagar. Passando de 15, o mais antigo sai |
| Seus pronomes, se você informar | Tratar você do jeito certo | Até você apagar |
| Seu ID do Discord, a hora e o canal de cada vez que você chamou uma delas | Contar em quantos dias vocês conversaram | Até você apagar |
| Um número de 0 a 3 por personagem (a paciência dela com você) e um código embaralhado da sua última pergunta | Reconhecer pergunta repetida em seguida. O código não permite recuperar o texto | Até você apagar |
| O texto das últimas 30 respostas de cada personagem em cada canal | Ela não repetir a mesma frase | Substituído pelas respostas novas |
| O ID das mensagens que as personagens enviaram | Reconhecer quando alguém responde a elas | Enquanto o bot existir |
| Quantidade de texto e tempo de cada chamada ao modelo de IA, sem o conteúdo | Controlar o custo | Enquanto o bot existir |

Os fatos vêm de duas fontes: do que você mesmo escreve com `/meu_fato` e do que você disse ao chamar uma personagem. Entra o que você falou sobre você: personagem que joga, mesa, gostos, como prefere ser respondido.

O bot não guarda fato sobre saúde, dinheiro, religião, política, orientação sexual, relacionamento, cor ou etnia, idade, endereço ou contato, nem fato sobre outra pessoa. Há um filtro para isso no pedido ao modelo e outro no programa. Filtro falha: se aparecer na sua lista algo que não devia, apague com `/esquecer_fato` e avise.

O texto guardado (mensagens do dia, fatos, pronomes e respostas das personagens) fica cifrado no disco.

## Com quem o bot compartilha

Para escrever a resposta, o bot envia um pedido a um modelo de IA do Google (Gemini). Vão nesse pedido: a mensagem em que você chamou a personagem, as mensagens recentes dessa conversa com ela, seu nome de exibição, seus pronomes e os fatos escolhidos para aquela resposta. O ID do Discord das pessoas não é enviado; a única exceção é o do dono do bot.

O bot usa dois acessos ao Gemini:

- **A cota gratuita da API do Gemini**, que é a primeira tentativa. Pelos termos do Google, o conteúdo enviado por esse acesso pode ser usado pelo Google para melhorar os produtos e os modelos dele, e pode ser lido por revisores humanos, depois de separado da conta de quem enviou.
- **A Vertex AI, paga**, quando a cota gratuita acaba e sempre na leitura diária que tira os fatos. Por esse acesso o Google não usa o conteúdo para melhorar produtos.

O clima vem do serviço Open-Meteo. O bot envia a ele só o nome ou as coordenadas do lugar pedido, nada sobre quem pediu.

O bot não vende dados, não mostra anúncio e não repassa dados a mais ninguém.

## Como ver e apagar o que é seu

- `/meus_dados` mostra tudo o que o bot guarda sobre você. Só você vê a resposta.
- `/meu_fato` acrescenta um fato e `/esquecer_fato` tira um.
- `/meus_pronomes` define ou limpa os pronomes.
- `/apagar_meus_dados` apaga na hora os fatos, os pronomes, as mensagens do dia e o histórico de quando você chamou cada personagem.

Se você saiu do servidor ou não consegue usar os comandos, peça ao Mizuki pelos contatos do começo deste texto.

O que já foi enviado ao Google para gerar uma resposta não é apagado por esses comandos: fica sujeito aos prazos do próprio Google.

## Idade

O Discord exige pelo menos 13 anos, ou a idade mínima do país de quem usa. O bot não é feito para quem tem menos que isso e não guarda idade.

## Mudanças

Quando este texto mudar, a data do começo muda junto e a mudança aparece no histórico do arquivo, que é público.
