"""Guias de uso escritos à mão: abrir um guia não consulta ficha, memória ou modelo."""
from __future__ import annotations

import re
import unicodedata

import discord

from .guias_ficha import CRIAR, PLANILHA
from .guia_mestre import MESTRE


# (título da página, texto). Cada página trata de uma tarefa, com exemplos copiáveis.
ASSUNTOS = {
    "geral": ("Comece por aqui", (
        ("O que você quer fazer?",
         "As guias conversam sobre o mundo do Ciclo Maldito, tiram dúvidas de regra e conferem partes da ficha.\n\n"
         "**Criar uma ficha:** preencher do começo até a emissão na Carteira.\n"
         "**Conhecer a planilha:** consultar abas, configurações e salários.\n"
         "**Analisar uma ficha:** enviar a planilha e entender a análise.\n"
         "**Revisar uma ficha como mestre:** cruzar o painel com a revisão humana.\n"
         "**Customizações:** levar uma criação ao mestre e entender a aprovação.\n"
         "**Livro:** consultar as regras e conferir a fonte.\n"
         "**Conversa, mídia e memória:** falar com elas e cuidar dos seus dados.\n"
         "**Clima:** consultar uma cidade. **Servidor:** configurar os recursos administrativos.\n\n"
         "Escolha um assunto no menu abaixo. Use as setas para continuar dentro dele."),
        ("Comandos para começar",
         "`/ajuda` ou `GC:ajuda` mostra a lista de comandos. Este guia explica como usá-los.\n\n"
         "A página **Abreviações** da ajuda reúne os nomes curtos. `GC:ab` abre essa página diretamente; "
         "os comandos completos continuam funcionando.\n\n"
         "`GC:guia ficha` abre o passo a passo da análise. Você também pode usar `/ficha guia` "
         "ou `/guia` e escolher **Analisar uma ficha** no campo **assunto**.\n\n"
         "Para montar o personagem, use `GC:guia criar`. Para consultar abas e configurações da ficha, "
         "use `GC:guia planilha`. Esses assuntos também aparecem no menu de `/guia`.\n\n"
         "Para outros temas, troque a última palavra: `GC:guia clima`, `GC:guia mídia`, "
         "`GC:guia memória` ou `GC:guia servidor`.\n\n"
         "Pela barra, só você vê o guia. Com `GC:`, ele aparece no canal. "
         "Abrir um guia não altera nenhuma configuração."),
    )),
    "criar": CRIAR,
    "planilha": PLANILHA,
    "mestre": MESTRE,
    "ficha": ("Analisar uma ficha", (
        ("1. Prepare e envie a ficha",
         "Este assunto explica a análise do bot. Para montar a ficha do zero, abra `GC:guia criar`; "
         "para conhecer suas abas, abra `GC:guia planilha`.\n\n"
         "Preencha sua cópia da ficha atual no Google Planilhas. Depois de trocar a Classe de um cartão, "
         "espere os campos e as contas terminarem de atualizar.\n\n"
         "**Pelo link:** use `/ficha analisar` com o campo **link**, ou escreva `GC:ficha` seguido do endereço da planilha. "
         "O bot precisa conseguir abrir esse link para leitura.\n\n"
         "**Pelo arquivo:** no Google Planilhas, vá a **Arquivo → Fazer download → Microsoft Excel (.xlsx)**. "
         "Envie o arquivo em `/ficha analisar`, no campo **arquivo**, ou anexe à mesma mensagem de `GC:ficha`.\n\n"
         "Envie uma fonte por vez. Se preferir não abrir o acesso à planilha, use o XLSX. "
         "O resultado da análise aparece no canal para você e o mestre consultarem."),
        ("2. Leia o resultado",
         "Comece pelo **Resumo** e abra **Correções e revisão** quando houver algo a resolver.\n\n"
         "**Vermelho:** há um erro identificado na página.\n"
         "**Amarelo:** há uma pendência, uma revisão do mestre ou algo que o bot não consegue conferir.\n"
         "**Verde:** os valores mostrados naquela página passaram pelas verificações feitas.\n\n"
         "A cor vale para a página aberta. O rodapé mantém o resultado geral da ficha. "
         "Use o seletor ou as setas para ver Personagem, Feitiços, Invocações e **Limites da análise**, quando aparecerem.\n\n"
         "**Zero erros não é aprovação da ficha.** VÁLIDO/REVISAR no cartão é um estado da conta da planilha; "
         "a autorização de usar a habilidade na mesa continua com o mestre."),
        ("3. Corrija e analise de novo",
         "Se aparecer **está 4, o certo é 3**, confira a escolha e os pontos no cartão correspondente. "
         "Corrija a entrada da ficha, sem trocar uma fórmula só para fazer o aviso desaparecer.\n\n"
         "Se faltar informação ou aprovação, complete o cadastro ou converse com o mestre. "
         "A página **Limites da análise** explica as partes que ficaram de fora.\n\n"
         "Depois de salvar, envie o link ou um novo XLSX para analisar novamente. "
         "As setas navegam pelo resultado que já foi calculado; elas não atualizam a análise.\n\n"
         "Os controles encerram após dez minutos sem uso. Para abrir outro painel, repita o comando."),
        ("4. O que revisar com o mestre",
         "Para o roteiro completo, use **GC:guia mestre** ou **/ficha mestre**. "
         "Use **Limites da análise** como lista de revisão e compare as escolhas com o livro da mesa.\n\n"
         "**Aprendizado e progressão:** quando a habilidade foi adquirida, quais marcos e treinos a concederam "
         "e se os requisitos livres foram atendidos. Um total compatível não comprova esse histórico.\n\n"
         "**COMO É:** quem pode ser alvo, como o efeito é resolvido, alcance, duração, frequência, "
         "dependência entre parcelas e situações em que termina. O texto precisa combinar com as peças escolhidas.\n\n"
         "**Casos especiais:** distribuição entre alvos, efeitos narrativos, interações de Alma, "
         "estados ativos de entidades e qualquer parte que o painel declare não conferida. "
         "Não deduza uma entrada ausente do resultado que você quer validar."),
        ("5. Quando a leitura não termina",
         "**Sem acesso ao link:** confira a permissão de leitura ou envie o XLSX.\n\n"
         "**Fórmula sem resultado calculado:** espere o Google terminar as contas e baixe um novo XLSX pelo próprio "
         "Google Planilhas. Salvar o arquivo em outro editor pode deixar fórmulas sem os resultados que o bot precisa ler.\n\n"
         "**Cartão ainda salvando:** espere a troca de Classe terminar e tente de novo. "
         "O bot pode reler o link; se a versão continuar incompleta, o cartão fica pendente.\n\n"
         "**Formato antigo ou exportação incompleta:** confira se está usando uma cópia atual da ficha, "
         "com a aba de exportação ANALISE preservada. Se persistir, envie ao responsável pelo bot a mensagem de erro "
         "e diga se usou link ou XLSX."),
    )),
    "custom": ("Customizações e mestre", (
        ("Da ideia à aprovação",
         "Combine a criação com o mestre e registre a definição nos campos próprios da ficha. "
         "Informe a base do livro quando houver uma, os requisitos, o funcionamento e os limites.\n\n"
         "**MESTRE VIU é um lembrete.** Marcar essa caixa não envia nem concede uma aprovação no bot. "
         "Hoje, o responsável pelo bot registra a aprovação combinada com o mestre para aquela definição e servidor.\n\n"
         "Se a análise pedir aprovação, leve a definição completa ao mestre e ao responsável pelo cadastro. "
         "Depois de registrada, analise novamente. Não existe um comando de jogador que aprove a própria criação."),
        ("O que uma aprovação permite conferir",
         "A aprovação vale para a **definição exata**. Alterar base, atributo, efeito ou outra parte relevante "
         "pode exigir uma aprovação nova, mesmo mantendo o nome.\n\n"
         "Aprovar uma descrição não faz o bot transformar prosa em bônus numérico. "
         "Um ajuste numérico precisa estar registrado no campo estruturado correspondente e ter sua origem confirmada.\n\n"
         "Cartões que usam Melhoria, Restrição ou Forma própria podem continuar **sem recálculo independente do bot**. "
         "Leia esse aviso e confira a conta e o efeito com o mestre.\n\n"
         "Exemplo: uma perícia aprovada para Inteligência não fica automaticamente aprovada para Essência. "
         "Para revisar o restante da ficha, abra o assunto **Analisar uma ficha** neste menu."),
    )),
    "livro": ("Livro e regras", (
        ("Consultar e conferir a regra",
         "`/livro` ou `GC:livro` abre o PDF configurado no bot.\n\n"
         "Para uma dúvida, chame uma das guias: `kal, como funciona Integridade?` "
         "ou `closure, quais são os limites dessa Melhoria?`. Diga a habilidade, Classe e as escolhas relevantes "
         "quando elas fizerem diferença na resposta.\n\n"
         "Confira a fonte e a edição usadas na mesa. A edição do PDF pode ser mais recente que partes da base "
         "de consulta ou das verificações do bot. Se houver diferença, leve o trecho ao mestre.\n\n"
         "Uma resposta na conversa ajuda a explicar a regra; ela não registra uma aprovação de customização "
         "nem substitui a análise determinística da ficha."),
    )),
    "clima": ("Clima", (
        ("Consultar uma cidade",
         "Use `/clima lugar:Belo Horizonte` ou `GC:clima BH`. Sem lugar, a consulta é de Tóquio.\n\n"
         "Outros exemplos: `GC:clima São Paulo` e `GC:clima Curitiba`. "
         "Se o nome tiver mais de um resultado possível, escreva também o estado ou país.\n\n"
         "Na conversa, você pode perguntar `closure, qual o clima atual de BH?`. "
         "Depois da resposta, uma continuação como `e de SP?` consulta a outra cidade.\n\n"
         "O comando direto consulta os dados sem precisar gerar uma fala com IA. "
         "Se a conversa demorar ou falhar, tente `/clima`. Para configurar o painel diário, "
         "abra o assunto **Servidor**."),
    )),
    "conversa": ("Conversa", (
        ("Chamar e continuar uma conversa",
         "Chame `kal` ou `closure` num canal em que o bot atende. Responder a uma mensagem delas também vale; "
         "logo depois de uma resposta, você pode continuar sem repetir o nome.\n\n"
         "A Kal'tsit fica de plantão das 9h às 21h; a Closure, das 21h às 9h, no horário de Brasília. "
         "`/status` mostra quem está de plantão e ajuda a conferir se o bot está respondendo.\n\n"
         "Para ajuda com uma ficha, use o comando de análise. Mandar uma pergunta para a personagem não "
         "faz a conversa registrar aprovações do mestre.\n\n"
         "Se não houver resposta, confira o canal, tente `/ping` e depois repita o pedido. "
         "O bot estar online não garante que o serviço de IA esteja disponível naquele momento."),
    )),
    "midia": ("Imagens, GIFs e áudio", (
        ("Enviar mídia e dizer o que você quer saber",
         "Envie a imagem, o GIF ou o áudio junto do pedido: `closure, o que está escrito aqui?` "
         "ou `kal, quantas vezes esse som se repete?`. A leitura de mídia precisa estar ativada pelo responsável pelo bot.\n\n"
         "GIFs do seletor e alguns links de mídia podem usar a prévia que o Discord entrega. "
         "Se o link falhar, anexe o arquivo. Links antigos de anexos podem expirar.\n\n"
         "Áudio continua sujeito a dúvidas de escuta: ruído, música e sons parecidos podem confundir a interpretação. "
         "Um GIF é observado por alguns quadros, não por todos os instantes.\n\n"
         "**Um link do YouTube não entrega o áudio do vídeo.** Reconhecer o título de uma música não significa "
         "ter escutado aquela gravação. Se precisar retomar um detalhe de um anexo antigo, envie o arquivo novamente."),
        ("Regras em imagem e conteúdo adulto",
         "Se a pergunta for sobre uma regra mostrada na imagem ou dita num áudio, escreva também a pergunta "
         "e o nome da regra no chat. Isso ajuda a buscar a fonte certa do livro.\n\n"
         "As guias podem comentar arte e reconhecer representações das personagens quando houver elementos suficientes. "
         "Uma imagem não comprova que elas viveram a cena.\n\n"
         "Reações adultas não gráficas dependem da configuração do servidor e da marcação NSFW do canal. "
         "Elas não incluem ERP ou encenação sexual, e os limites do provedor continuam valendo. "
         "Quem administra o servidor encontra o passo a passo no assunto **Servidor**."),
    )),
    "memoria": ("Memória e seus dados", (
        ("Ver, acrescentar e corrigir lembranças",
         "`/meus_dados` mostra os pronomes e fatos guardados sobre você, além dos detalhes da memória de conversa. "
         "A resposta aparece só para você.\n\n"
         "`/meus_pronomes` define como as personagens tratam você. Sem texto, volta à forma neutra.\n\n"
         "`/meu_fato` guarda uma informação curta e permitida, como seu personagem ou uma preferência de conversa. "
         "Evite informações sensíveis: o bot não registra esse tipo de dado como fato.\n\n"
         "`/esquecer_fato numero:2` remove o fato de número 2 da lista mostrada em `/meus_dados`. "
         "Esses comandos pessoais são usados pela barra, para não publicar seus dados no canal."),
        ("Apagar dados e separar as duas memórias",
         "`/apagar_meus_dados` apaga os dados pessoais guardados pelo bot. **A exclusão não tem volta.** "
         "Se quiser retirar só uma lembrança, use `/esquecer_fato`.\n\n"
         "A conversa recente e os fatos duradouros têm funções diferentes. "
         "Uma informação pode sair do contexto recente sem ter sido escolhida como fato. "
         "Consulte `/meus_dados` para ver o que de fato ficou guardado.\n\n"
         "A memória de conversa não é o cadastro de aprovação de uma ficha. "
         "Dizer que o mestre aprovou algo no chat não registra essa aprovação na análise. "
         "Para isso, consulte o assunto **Customizações e mestre**.\n\n"
         "`/ajuda` também traz os links de privacidade e termos quando estiverem configurados."),
    )),
    "servidor": ("Configuração do servidor", (
        ("Criar e remover atalhos do servidor",
         "Os atalhos padrão já funcionam, como **GC:g** para guia e **GC:f** para analisar ficha. "
         "`GC:ab` abre a lista de abreviações na ajuda, incluindo as deste servidor.\n\n"
         "Para cadastrar outro, quem tem **Gerenciar servidor** usa **/atalho definir**. "
         "Em **nome**, escreva só o nome curto, sem GC:. Em **destino**, escolha um comando ou guia da lista. "
         "Exemplo: nome `revisar`, destino **Guia: Revisar uma ficha como mestre**; depois, use `GC:revisar`.\n\n"
         "`/atalho listar` consulta os próprios do servidor; `/atalho remover` retira o nome informado. "
         "Os nomes completos e os atalhos padrão permanecem. São até 20 próprios, sem substituir um nome existente.\n\n"
         "O atalho vale somente neste servidor e aceita os argumentos do destino, como um link depois de um atalho de ficha. "
         "Ele não guarda uma frase livre nem executa ações administrativas. "
         "Reabra a ajuda depois de mudar um atalho para atualizar a lista."),
        ("Painel diário e diagnóstico",
         "Os comandos de configuração exigem a permissão **Gerenciar servidor**. "
         "Este guia só explica o uso; não modifica o servidor.\n\n"
         "`/clima_canal canal:#clima` escolhe onde o painel diário de Tóquio aparece. "
         "Sem informar um canal, usa o canal em que você executou o comando.\n\n"
         "`/clima_canal_desligar` desliga esse painel no servidor. Isso não impede consultas individuais de clima.\n\n"
         "`/ping` confere se o bot responde. `/status` mostra informações do funcionamento e do plantão. "
         "Se o bot não conseguir publicar o painel, confira as permissões de enviar mensagens e inserir links no canal."),
        ("Configurar reações adultas",
         "`/responder_nsfw ativar:Sim` liga as reações adultas não gráficas no servidor; "
         "`ativar:Não` desliga. Sem opção, o comando mostra o estado atual.\n\n"
         "`/nsfw_canal canal:#chat` limita o recurso a esse canal e seus tópicos. "
         "`/nsfw_canal todos:Sim` retira essa restrição. Sem opções, mostra a configuração.\n\n"
         "**Sem um canal escolhido, o modo vale em todos os canais marcados como NSFW onde o bot já atende.** "
         "Ele ainda precisa estar ligado por `/responder_nsfw`. O canal em que você usa o comando não é "
         "escolhido automaticamente.\n\n"
         "A opção permite reações e opiniões no jeito das personagens, sem ERP ou encenação sexual. "
         "Ela não remove os limites do provedor."),
    )),
}

APELIDOS = {"inicio": "geral", "ajuda": "geral", "analise": "ficha", "fichas": "ficha",
            "criacao": "criar", "criar ficha": "criar", "ficha criar": "criar",
            "manual": "planilha", "abas": "planilha", "ficha aprofundada": "planilha",
            "configuracao ficha": "planilha", "configuracoes da ficha": "planilha",
            "customizacoes": "custom", "aprovacao": "custom", "revisao": "mestre", "revisao do mestre": "mestre", "regras": "livro",
            "tempo": "clima", "chat": "conversa", "imagens": "midia", "gif": "midia", "audio": "midia",
            "dados": "memoria", "meus_dados": "memoria", "configuracao": "servidor", "nsfw": "servidor"}


def assunto(texto: str | None) -> str | None:
    limpo = unicodedata.normalize("NFKD", texto or "geral").encode("ascii", "ignore").decode().lower().strip()
    limpo = re.sub(r"\s+", " ", limpo) or "geral"
    return APELIDOS.get(limpo, limpo) if APELIDOS.get(limpo, limpo) in ASSUNTOS else None


def paginas(tema: str) -> list[discord.Embed]:
    titulo, textos = ASSUNTOS[tema]
    saida = []
    for i, (nome, texto) in enumerate(textos, 1):
        embed = discord.Embed(title=f"Como usar · {titulo}", description=texto, color=0x2E8B57)
        embed.set_author(name=nome)
        # O paginador separa o rodapé por “ · ”. Preserve o subtítulo no mesmo
        # segmento para distinguir, por exemplo, os três painéis CONFIGURAÇÃO.
        rotulo = re.sub(r"^\d+\.\s+", "", nome).replace(" · ", ": ")
        embed.set_footer(text=f"Página {i} de {len(textos)} · {rotulo} · GC:guia {tema} · só orientação; não executa ações")
        saida.append(embed)
    return saida
