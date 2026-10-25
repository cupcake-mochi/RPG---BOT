"""Criação e consulta das fichas oficiais (versão pública 1.0; contrato técnico R53, ANALISE 12).

Os dois modelos oficiais e a diferença entre versão da ficha, do bot e do livro: dados/ficha/MODELOS.md.

Fontes e revisões: docs/GUIAS-DE-USO.md. Conteúdo estático, sem ler ou editar planilhas.
"""
import re
import unicodedata


def orientacao_ficha(mensagem: str, historico=()) -> str:
    """Recupera os próprios guias para a conversa, inclusive perguntas de continuação.

    Só texto editorial entra no contexto de referência; a pergunta seleciona
    páginas, nunca é interpolada como instrução. Não lê fichas nem chama IA.
    """
    consulta = unicodedata.normalize("NFKD", " ".join((*historico, mensagem)))
    consulta = consulta.encode("ascii", "ignore").decode().lower()
    temas = (
        (r"\b(emiti\w*|emiss\w*|carteira|issu\w*)\b", CRIAR[1][13]),
        (r"\b(salari\w*|salary|salaries|credit\w*|fechamento\w*|participa\w*|pay\w*)\b", PLANILHA[1][12]),
        (r"\b(dinheiro|iene\w*|gasto\w*|ganho\w*|extrato|saldo|o86|w86|money|yen|spend\w*|income|balance)\b", PLANILHA[1][6]),
        (r"\b(miss\w*|corrigi\w*|correc\w*|data\w*|date\w*|mission\w*|android|celular|mobile)\b", PLANILHA[1][13]),
        (r"\b(paleta\w*|palette\w*|cores|colors?|colours?|recarreg\w*)\b", PLANILHA[1][1]),
        (r"\b(invoca\w*|recolhid\w*|pontinho|summon\w*|collaps\w*)\b", PLANILHA[1][5]),
    )
    paginas = [(titulo, texto) for padrao, (titulo, texto) in temas if re.search(padrao, consulta)]
    if not paginas:
        return ""
    return ("[Referência de uso das fichas oficiais Era da Revolução e Ciclo Maldito, versão pública 1.0 "
            "(contrato técnico R53; 1.0 não é a revisão do livro nem a versão do bot). "
            "Use somente os trechos pertinentes à dúvida; isto não executa ações nem certifica saldo, emissão ou salário. "
            "As instruções atuais substituem as antigas sobre saldo manual, emissão e rotina diária.\n\n" +
            "\n\n".join(titulo + "\n" + texto for titulo, texto in paginas) + "]")

CRIAR = ("Criar uma ficha", (
    ("1. Faça sua própria cópia",
     "Há dois modelos oficiais: a [Ficha · Era da "
     "Revolução](https://docs.google.com/spreadsheets/d/1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k/edit) e a "
     "[Ficha · Ciclo Maldito](https://docs.google.com/spreadsheets/d/1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw/edit). "
     "Abra o que a sua mesa indicar, entre na sua conta Google e use **Arquivo → Fazer uma cópia**. "
     "Dê um nome que identifique seu personagem e preencha essa cópia.\n\n"
     "O **1.0** no cabeçalho e no número da carteira é a versão pública da ficha. Ele não indica a revisão do livro "
     "nem a versão do bot.\n\n"
     "Este roteiro vai da ficha vazia até a emissão na **CARTEIRA**. As abas ficam na parte de baixo da "
     "planilha. Se uma seção estiver recolhida, abra pelo **+** ao lado das linhas ou acima das colunas.\n\n"
     "Use os campos de preenchimento e os menus. Preserve as fórmulas e as abas ocultas. As contas e os cartões "
     "dependem delas. Para consultar a função de cada aba, abra `GC:guia planilha`."),
    ("2. Combine o início da campanha",
     "Antes de distribuir pontos, pergunte ao mestre o **nível inicial**, o **Grau**, os recursos e quais opções estão disponíveis. "
     "Pense também no nome, na ideia do personagem e no motivo para estar com o grupo.\n\n"
     "O padrão do livro é **nível 2 e Grau 4**. Nível mede progressão; Grau é a patente. "
     "Começar em nível maior não concede um Grau maior automaticamente.\n\n"
     "Em **CONFIGURAÇÃO**, confira **REGRAS DE CAMPANHA** com o mestre. CAMPANHA em branco mantém o valor do livro; "
     "preencha apenas mudanças combinadas e registre o motivo. Não altere uma regra para esconder um aviso.\n\n"
     "Preencha a identificação na **CARTEIRA** e os dados de história na **FICHA PESSOAL**. "
     "Deixe a emissão para o fim. Se houver progressão além do início combinado, registrem os pontos de experiência (XP) e os ganhos correspondentes; "
     "não escreva por cima do nível calculado."),
    ("3. Distribua os atributos",
     "Na **FICHA**, distribua os pontos entre **Força, Destreza, Constituição, Inteligência e Essência** nos campos de atributo base.\n\n"
     "Na criação padrão, são **9 pontos**, com cada atributo entre **0 e 3**. "
     "Exemplo: Força 3, Destreza 2, Constituição 2, Inteligência 1 e Essência 1 somam 9. "
     "Essa é uma distribuição possível, não uma escolha obrigatória.\n\n"
     "Confira o total disponível e os requisitos das escolhas que pretende fazer. Você pode redistribuir enquanto monta a ficha. "
     "Se a campanha mudou esses limites, use os valores acordados na etapa anterior.\n\n"
     "**Buff/Debuff** é para um ajuste concedido por uma regra ou efeito. Não use essa caixa para completar pontos da criação."),
    ("4. Escolha a Origem e suas capacidades",
     "Escolha a **Origem** no menu da **FICHA** e leia sua entrada no livro. "
     "Ela determina capacidades, treinos e quais rotas de poder você pode seguir.\n\n"
     "Na **FICHA PESSOAL**, preencha o traço e escolha **uma marcante e duas menores elegíveis**. "
     "Leia requisitos, frequência e efeito completos. Ter a opção no menu não dispensa esses requisitos.\n\n"
     "Registre os **Legados de história** quando fizerem parte do personagem. Eles descrevem vínculos e acontecimentos; "
     "não concedem bônus numéricos nem substituem a marcante e as menores.\n\n"
     "**Sem Técnica** é uma opção própria das Origens que a permitem. Se usar conteúdo criado para a mesa, "
     "combine a definição com o mestre e consulte `GC:guia custom` antes de adotá-lo."),
    ("5. Escolha Caminho e Trilha",
     "Na **FICHA**, escolha seu **Caminho** e uma **Trilha desse Caminho**, quando o nível permitir. "
     "Leia as seções Características e Progressão dos dois no livro.\n\n"
     "Bastião favorece proteção; Vanguarda, ofensiva; Guia, apoio; Emanador, conjuração; "
     "Evocador, entidades; Incursor, mobilidade e precisão. Use isso para escolher o estilo que quer jogar.\n\n"
     "Registre as escolhas das habilidades recebidas no seu nível, os treinos e os recursos correspondentes. "
     "Uma habilidade com opções ainda precisa dessas escolhas, mesmo quando a ficha já mostra sua descrição.\n\n"
     "No início padrão de nível 2, você já recebe a primeira Trilha. No nível 1, ela e as habilidades de nível 2 "
     "ficam para quando alcançar esse nível."),
    ("6. Marque perícias, ofícios e resistências",
     "Na **FICHA**, marque os treinos de perícias, ofícios e **Testes de Resistência (TR)** que suas escolhas concedem.\n\n"
     "Na criação padrão, a Origem dá uma perícia de sua lista e uma livre, mais dois ofícios. "
     "Você pode trocar **os dois ofícios por uma perícia livre**, anotando a troca. "
     "O Caminho acrescenta duas perícias indicadas e cinco livres.\n\n"
     "Antes de outros benefícios ou trocas, isso dá **9 perícias e 2 ofícios**, ou **10 perícias sem ofícios**. "
     "Se trocar perícias por treino em arma quando seu Caminho permitir, retire essas escolhas da conta e anote a arma na **FICHA PESSOAL**.\n\n"
     "Escolha um TR treinado pela Origem e outro pelo Caminho, diferentes entre si. "
     "Defina **Força ou Destreza para o TR Físico** na criação; essa escolha permanece fixa. "
     "Repetir treino não soma Maestria duas vezes. Confira as substituições permitidas pelo livro."),
    ("7. Prepare sua técnica, Manejos ou Katas",
     "Abra a **FICHA AMALDIÇOADA**. A rota acompanha a Origem escolhida na FICHA. "
     "Preencha o bloco inicial de acordo com o que aparece para sua rota.\n\n"
     "**Técnica inata:** escreva o conceito e o **Fundamento**, a regra que explica o que seu poder faz. "
     "Escolha o **ATRIBUTO DE CONJURAÇÃO** na FICHA e confira seu espelho na técnica. "
     "Defina os tipos de dano, o Selo, a Expressão e os estados das Famílias. "
     "O padrão do Fundamento tem duas Livres e três Fechadas; as demais ficam Neutras.\n\n"
     "**Sem Técnica:** escolha a semente e prepare Manejos pelas regras da rota. "
     "**Técnica Marcial:** defina o equipamento do estilo e prepare Katas. "
     "Use as substituições e os recursos próprios desses capítulos.\n\n"
     "O conceito precisa sustentar as aplicações que você vai criar. Combine essa interpretação com o mestre."),
    ("8. Monte uma capacidade por vez",
     "Na **FICHA AMALDIÇOADA**, abra um cartão da modalidade permitida e escolha uma **Classe disponível**. "
     "Preencha o nome e **COMO É**: quem afeta, como resolve, alcance, duração e quando o efeito termina.\n\n"
     "Escolha a **Forma** e distribua pontos inteiros em **DANO, CURA e PV TEMP.** (pontos de vida temporários) conforme a função pretendida. "
     "Selecione Melhorias e Restrições; confira custo, devolução, saldo e PE, os pontos de energia. "
     "Nas modalidades de dados fixos, escolha a função no campo próprio.\n\n"
     "Leia os avisos e compare o texto com as peças. **SÓ EM SI** significa afetar exclusivamente quem executa; "
     "na Forma Toque, isso não devolve pontos. **VÁLIDO** indica o estado mecânico do cartão, não a autorização do mestre.\n\n"
     "Ao mudar a Classe, espere a atualização terminar antes de editar. As versões ficam guardadas por Classe; "
     "não sobrescreva resultados calculados. Repita o processo para as demais capacidades disponíveis."),
    ("9. Confira os espaços e as habilidades recebidas",
     "Confira o orçamento de **ESPAÇOS** na FICHA AMALDIÇOADA. "
     "Na técnica inata de nível 2, são **três espaços conhecidos**, além de **dois feitiços de Classe 0** contados à parte. "
     "Rotas e benefícios específicos podem mudar suas escolhas.\n\n"
     "Feitiços, Talentos pagos, Domínio e entidades podem disputar esse orçamento conforme suas regras. "
     "Ter cartões vazios disponíveis não significa ter espaços para usar todos. "
     "Registre benefícios gratuitos nas posições próprias para não cobrar nem conceder espaços duas vezes.\n\n"
     "Confira **APTIDÕES E REFINO** e os Talentos recebidos. Use Refino ou Lapidação conforme a rota e anote escolhas "
     "e requisitos. Liberação, Técnica Máxima e Domínio só entram quando você tiver acesso.\n\n"
     "Se houver pacto, registre efeito, custo e condição reais com o mestre; deixe os campos de pacto vazios quando não houver um."),
    ("10. Preencha entidades, se houver",
     "Se seu personagem tem uma entidade, abra **INVOCAÇÕES** e preencha uma ficha para ela. Se não tem, siga "
     "para o equipamento; não é preciso inventar uma só para ocupar a aba.\n\n"
     "Escolha o tipo, registre nome, aquisição, nível e Classe conforme as regras dessa entidade. Distribua "
     "atributos, Famílias, treinos e Talentos próprios dela. Não copie automaticamente os valores do "
     "personagem: uma domada, por exemplo, tem progressão própria.\n\n"
     "Monte a básica e as especiais disponíveis nos cartões da entidade e confira seu orçamento de espaços. "
     "Anote condições de manifestação, comando e manutenção. Repertório conhecido e entidades ativas são coisas "
     "diferentes.\n\n"
     "Leve ao mestre as permissões de aquisição e os limites de uso conjunto. O bot não comprova esse histórico "
     "nem certifica toda interação entre entidades.\n\n"
     "As invocações **2 a 6 e 8 a 12** ficam recolhidas. Abra pelo **+ da lateral esquerda**. No celular, se o "
     "+ parecer um pontinho, toque no **« do canto** para abrir a lateral. A caixa de ajuda fica no topo de "
     "INVOCAÇÕES (AB2:AR4)."),
    ("11. Compre e equipe seus itens",
     "Na **FICHA PESSOAL**, registre os equipáveis, itens, quantidades e onde ficam guardados. Depois selecione "
     "o que está em uso: mãos, proteção e escudo devem corresponder ao inventário.\n\n"
     "Na criação padrão de Grau 4, você recebe **um Traje 1 e ¥150.000** para os demais itens. Escolha "
     "situação, TR e perícias do Traje conforme o livro. Desconte as compras do dinheiro e registre munição e "
     "suprimentos. Armas de fogo têm preço de criação próprio e podem exigir autorização.\n\n"
     "Confira treino, Força, mãos, acesso e Volume, inclusive do traje vestido. O limite normal de carga é **5 "
     "+ Força**, antes de alterações concedidas.\n\n"
     "A ficha começa com **¥150.000 no EXTRATO**, como Saldo inicial. Na caixa **± GASTO / GANHO** da FICHA "
     "PESSOAL (O86), digite **-500** para gastar ou **2000** para ganhar. Espere a caixa limpar antes do "
     "próximo lançamento. Veja o saldo em **TOTAL DISPONÍVEL (W86)**: ele inclui extrato, salários e o "
     "lançamento ainda na caixa. Não lance o mesmo salário de novo."),
    ("12. Revise os valores e o estado inicial",
     "Volte à **FICHA** e confira Vida, PE ou recurso da rota, Integridade, Defesa, Proteção, "
     "deslocamento, acerto, CD, Maestria e treinos. **CD (Classe de Dificuldade)** é a dificuldade contra a qual o alvo faz uma resistência; "
     "ela não é o bônus de ataque.\n\n"
     "Compare os totais com Caminho, Origem, nível e equipamento. Se algo estiver errado, corrija a entrada que o gerou, "
     "sem substituir a fórmula pelo número desejado. Vida rolada só entra quando combinada com o mestre.\n\n"
     "Preencha os recursos atuais conforme o começo da história. Se o personagem começa recuperado, confira se os valores "
     "atuais correspondem aos máximos. Estados como Exaustão e Sequelas devem refletir a situação real.\n\n"
     "Revise descrições e avisos em todas as partes preenchidas. Campos de capacidades ainda não adquiridas podem ficar vazios."),
    ("13. Analise e feche a revisão com o mestre",
     "Espere as contas terminarem. Envie sua cópia com **GC:ficha seguido do link** ou use `/ficha analisar`. "
     "Se preferir arquivo, baixe **Arquivo → Fazer download → Microsoft Excel (.xlsx)** e anexe ao comando. "
     "O resultado aparece no canal; por link, o bot precisa ter acesso de leitura.\n\n"
     "Leia Resumo, Correções e revisão e Limites da análise. Corrija as entradas e **envie uma nova análise** depois de editar. "
     "As setas só percorrem o resultado anterior. `GC:guia ficha` explica esse painel em detalhes.\n\n"
     "Com o mestre, feche requisitos, aprendizado, progressão, COMO É, alvos, efeitos narrativos, pactos e customizações. "
     "**Zero erros não é aprovação. MESTRE VIU é um lembrete**, sem conceder autorização no bot. "
     "Se houver conteúdo próprio, a aprovação cadastrada precisa corresponder à definição exata e ao servidor.\n\n"
     "Quando a revisão estiver resolvida e o mestre liberar a ficha, siga para a emissão."),
    ("14. Finalize na Carteira: EMITIR",
     "Terminou a ficha? Escreva o nome do personagem na CARTEIRA e marque EMITIR, ao lado de 'Não emitida'. O "
     "salário só começa a contar a partir desse dia. Se marcar no dia errado, corrija a data de emissão em "
     "CONFIGURAÇÃO (só dá para adiantar).\n\n"
     "Depois da revisão com o mestre, use **CARTEIRA!AT3** ou **CONFIGURAÇÃO!O39**. A data é a de hoje em "
     "Brasília; a caixa se desmarca sozinha depois de salvar. Aguarde de 5 a 15 segundos e confira a data. "
     "Marcar EMITIR de novo não muda a data.\n\n"
     "Para corrigir, escreva **dd/mm/aaaa em CONFIGURAÇÃO!O38**, entre a emissão atual e hoje. Sem emissão, só "
     "vale hoje. Datas para trás, futuras ou inválidas são recusadas com aviso em O46. Os salários vencidos "
     "ficam pagos; a correção faz o ciclo aberto recomeçar na data nova.\n\n"
     "A emissão não envia a ficha ao bot nem registra aprovação do mestre. O salário é calculado por fórmula, "
     "sem ativar rotina diária. Veja os detalhes em `GC:guia planilha` e mantenha recursos, gastos e missões "
     "atualizados."),
))

PLANILHA = ("Conhecer a planilha", (
    ("Por onde começar e como abrir as seções",
     "Este é o guia de consulta da ficha. Para preencher do começo ao fim, use **GC:guia criar**. Para "
     "interpretar a avaliação do bot, use **GC:guia ficha**.\n\n"
     "As sete abas de uso são **CARTEIRA, FICHA, FICHA AMALDIÇOADA, INVOCAÇÕES, FICHA PESSOAL, GLOSSÁRIO e "
     "CONFIGURAÇÃO**. Elas aparecem na parte de baixo; use a navegação de abas se não couberem na tela.\n\n"
     "Os sinais **+ e −** na margem abrem e recolhem grupos de linhas ou colunas. Recolher só esconde a seção; "
     "não apaga suas escolhas. Em CONFIGURAÇÃO, vários painéis ficam lado a lado, à direita.\n\n"
     "Menus e caixas de seleção recebem escolhas; resultados e espelhos vêm de outras partes. Se tiver dúvida, "
     "leia a nota do campo e confira a barra de fórmulas antes de escrever. As abas técnicas ocultas guardam "
     "catálogos, contas e registros; preserve-as.\n\n"
     "No Android, os menus personalizados e a rotina de abertura não rodam. Use os campos de edição; uma edição "
     "pode levar de 5 a 15 segundos para responder."),
    ("CARTEIRA · identificação e emissão",
     "A CARTEIRA apresenta o documento do personagem: identificação, imagem, patente e data de emissão. Ela não "
     "substitui os registros mecânicos das outras abas.\n\n"
     "Preencha a identificação nos campos próprios e confira os dados espelhados. Use a imagem do personagem na "
     "área reservada sem cobrir as informações do documento. O Grau deve ser o combinado com o mestre; ele não "
     "é o nível de progressão.\n\n"
     "Escolha **PALETA em C27**. A troca em lote leva uns **20 segundos** e muda a ficha inteira de uma vez. "
     "Até as cores mudarem, **não feche nem recarregue a página**, como avisa C29. CONFIGURAÇÃO mantém sua "
     "paleta fixa.\n\n"
     "Com a ficha pronta, marque **EMITIR**, ao lado de **Não emitida**, em AT3. O salário só conta a partir "
     "desse dia. A caixa se desmarca ao salvar; marcar novamente não muda a data. Para corrigir, use "
     "CONFIGURAÇÃO!O38, somente para frente e até hoje. Veja os detalhes em **Como emitir a carteira e "
     "acompanhar salários**."),
    ("FICHA · atributos, recursos e combate",
     "A FICHA reúne atributos, perícias, ofícios, Testes de Resistência (TR), Caminho, Trilha, Origem e os principais valores de combate. "
     "Aqui você acompanha recursos e estados como Vida, energia, Integridade, Sequelas e Exaustão.\n\n"
     "Separe **base**, **Buff/Debuff**, **total**, **atual** e **máximo**. Distribua pontos na base; "
     "registre ajustes nos campos próprios; acompanhe o gasto no atual. O total e o máximo são resultados das contas.\n\n"
     "Os menus de atributo de conjuração, acerto e TR Físico, quando aplicáveis, precisam corresponder às escolhas da criação. "
     "Equipamento e pontos de experiência (XP) vêm de registros da FICHA PESSOAL: corrija a origem do dado.\n\n"
     "O menu de descanso aplica as recuperações previstas. Escolha o descanso realmente realizado e confira o aviso do que mudou. "
     "Não o use para ajustar livremente os máximos."),
    ("FICHA AMALDIÇOADA · poderes e habilidades",
     "Esta aba guarda a rota de capacidades: Fundamento e feitiços, Manejos ou Katas, conforme a Origem. "
     "O bloco inicial reúne conceito, atributo, tipos de dano, Selo, Expressão e Famílias, quando aplicáveis.\n\n"
     "O orçamento mostra espaços disponíveis e ocupados. Talentos pagos, Regra Própria, Domínio e invocações "
     "podem consumir espaços conforme as regras. Classe 0 e benefícios gratuitos têm contagens ou posições próprias.\n\n"
     "As seções também incluem Talentos, Aptidões e Refino, pactos e capacidades avançadas. "
     "Preencha apenas o que recebeu e guarde a fonte de aquisição. A existência do campo não libera seu uso.\n\n"
     "As Famílias indicam acesso e custos das peças. Nas rotas especiais, use as substituições do capítulo correspondente. "
     "Mudar só a descrição não altera automaticamente a mecânica da montagem."),
    ("Como montar e editar uma habilidade",
     "Os cartões são editados **no próprio local**. Abra o grupo da capacidade, escolha uma Classe disponível e espere carregar. "
     "Depois preencha nome, COMO É, Forma, funções, pontos, Melhorias e Restrições.\n\n"
     "**COMO É** explica alvos, resolução, alcance, duração e condições de uso. "
     "As colunas DANO, CURA e PV TEMP. distribuem pontos; os resultados mostram dados, custo e avisos. "
     "Modalidades com dados fixos têm seleção própria de função.\n\n"
     "A ficha conserva versões por Classe. Ao trocar, espere a atualização terminar antes de editar. "
     "Se houver uma edição pendente, a troca pode precisar ser repetida. Não copie um resultado por cima da fórmula para forçar a versão.\n\n"
     "**VÁLIDO/REVISAR** descreve a montagem mecânica. Requisitos, narrativa e autorização continuam com o mestre. "
     "Liberação e Técnica Máxima usam seus cartões e requisitos próprios."),
    ("INVOCAÇÕES · fichas das entidades",
     "Cada entidade tem sua própria ficha, com tipo, nível, Classe, atributos, Famílias, treinos, Talentos, "
     "recursos e cartões de capacidades. Abra seus grupos de linhas para consultar o restante.\n\n"
     "A aquisição e o tipo determinam a progressão. Uma entidade não herda automaticamente os atributos, as "
     "Famílias ou o nível atual do personagem. Confira a distribuição e os limites próprios.\n\n"
     "Registre a básica, as especiais e outros benefícios efetivamente recebidos. Anote o que exige "
     "manifestação, comando ou manutenção e quais recursos são compartilhados.\n\n"
     "A lista de entidades conhecidas não informa, por si só, quais estão ativas numa cena. Confira esse estado "
     "e os limites de uso com o mestre. Sem entidades no personagem, esta aba pode ficar sem preenchimento.\n\n"
     "As invocações **2 a 6 e 8 a 12** ficam recolhidas. Abra pelo **+ da lateral esquerda**. No celular, se o "
     "+ parecer um pontinho, toque no **« do canto** para abrir a lateral. A caixa de ajuda fica no topo de "
     "INVOCAÇÕES (AB2:AR4)."),
    ("FICHA PESSOAL · história, itens e missões",
     "Aqui ficam o dossiê, traço, capacidades da Origem, Legados de história, equipamento, treinos em armas, "
     "inventário, carga, dinheiro e o painel de missões e pontos de experiência (XP).\n\n"
     "Registre quantidades e Volume e selecione o que está vestido ou nas mãos. Ter uma arma no inventário não "
     "significa estar com ela equipada ou ter treino. Confira os avisos de Força, acesso e excesso de carga.\n\n"
     "O painel de missões fica à direita, em colunas recolhidas. Abra o **+** acima delas para registrar "
     "missão, tipo e os ajustes concedidos. O XP alimenta a progressão; não invente missões para alcançar o "
     "nível desejado.\n\n"
     "Em **± GASTO / GANHO (O86)**, digite **-500** para gastar ou **2000** para ganhar. O lançamento vai para "
     "**EXTRATO** (Data, Valor, Origem), e a caixa limpa; aguarde isso antes do próximo. A ficha começa com "
     "**¥150.000**, registrados como Saldo inicial.\n\n"
     "O dinheiro está em **TOTAL DISPONÍVEL (W86)**: soma o lançamento ainda na caixa, o extrato e os salários "
     "do livro e pendentes. O86 não é o saldo. Não lance salário de novo. Para ver EXTRATO no PC, use **Ver → "
     "Mostrar → EXTRATO**; a aba é oculta. Preserve os registros. Os **últimos 10 créditos salariais** ficam em "
     "CONFIGURAÇÃO, seção 14, K81:P90, mais recentes primeiro."),
    ("GLOSSÁRIO · entender os termos",
     "Abra o GLOSSÁRIO quando não souber o que um atributo, perícia, ofício ou termo da ficha significa. "
     "Ele serve como consulta rápida enquanto você preenche ou joga.\n\n"
     "Para um procedimento completo, consulte o capítulo do livro: criação, equipamento, Fundamento, "
     "Caminho, Origem ou progressão, conforme a dúvida. `/livro` abre o PDF configurado no bot.\n\n"
     "Consulte a **versão atual do livro de regras** e confira a edição usada pela mesa. "
     "Se houver diferença entre o livro, a ficha e a resposta do bot, compare o trecho correspondente com o mestre."),
    ("CONFIGURAÇÃO · regras da campanha",
     "CONFIGURAÇÃO reúne regras da mesa, bônus e mudanças e cadastros próprios. "
     "Não é necessário preencher tudo para criar um personagem com as regras padrão.\n\n"
     "Em **REGRAS DE CAMPANHA**, compare **LIVRO**, **CAMPANHA**, **EM USO** e **MOTIVO**. "
     "CAMPANHA em branco conserva o livro; **zero é um valor informado**, não um campo vazio. "
     "Registre apenas mudanças autorizadas e sua justificativa.\n\n"
     "Os controles incluem nível inicial, limites de atributos, treinos, deslocamento, Morrendo, curva de XP e vida rolada. "
     "Se a mesa usa vida rolada, registrem as rolagens nos campos próprios; não substituam a vida máxima calculada.\n\n"
     "Uma alteração na cópia não muda a campanha cadastrada no bot. "
     "Se houver divergência, o mestre e o responsável pelo bot precisam conferir os dois registros."),
    ("Progressão · XP, marcos e novas escolhas",
     "O nível acompanha os pontos de experiência (XP) registrados na FICHA PESSOAL e o início definido para a campanha. "
     "Preencha as recompensas reais das missões; não edite a fórmula do nível para avançar o personagem.\n\n"
     "Ao subir, confira vida, energia, Maestria, maior Classe, espaços e habilidades de Caminho e Trilha. "
     "Nos marcos, registre a escolha recebida: **Corpo, Refino ou Leque**, conforme as regras e os requisitos da rota. "
     "Uma conta atualizada não escolhe automaticamente por você.\n\n"
     "Corpo, treinos, Leque e opções de especialização precisam aparecer nos registros correspondentes. "
     "Uma capacidade gratuita deve ocupar sua posição própria, sem ser cobrada como escolha paga outra vez.\n\n"
     "O mestre confere a ordem das aquisições, os limites de avanço por missão e eventuais requisitos de Limiar. "
     "O bot não reconstrói esse histórico a partir do nível final. Depois das novas escolhas, faça outra análise."),
    ("CONFIGURAÇÃO · bônus e mudanças",
     "Use **BÔNUS E MUDANÇAS** para um efeito que realmente altera uma caixa da ficha. "
     "Escolha a **CAIXA**, o modo **COMO**, o **VALOR**, o **TIPO DE FONTE** e a **FONTE**. "
     "Marque **LIGADO** enquanto o efeito se aplicar. Desmarcar o guarda sem aplicá-lo.\n\n"
     "**Somar** acrescenta ao cálculo e ao Buff/Debuff existente. "
     "**Trocar por** fixa o resultado final naquele valor, inclusive zero. "
     "Duas trocas ligadas para a mesma caixa geram conflito.\n\n"
     "Exemplo: um efeito autorizado de +2 em Defesa usa Somar 2; "
     "um efeito que define Defesa 15 usa Trocar por 15. Esses números são exemplos de preenchimento, não benefícios concedidos.\n\n"
     "Escreva qual habilidade, pacto, item ou decisão justifica a mudança. "
     "Não aplique a mesma fonte de novo no Buff/Debuff. Ao terminar o efeito, desmarque LIGADO e confira o total."),
    ("CONFIGURAÇÃO · cadastrar regras e opções próprias",
     "Os cadastros se distribuem em painéis à direita: gerais, Caminho/Trilha, Perícias, Ofícios, Famílias, "
     "Melhorias, Restrições, Tipos de dano, Formas, Aptidões/Bênçãos, Talentos, Tipos e Talentos de entidade. "
     "Use o índice e os grupos de colunas para abrir o painel desejado.\n\n"
     "Escolha o tipo e um nome único. Se houver **BASE DO LIVRO**, os campos deixados em branco podem herdar seus valores. "
     "Preencha as diferenças nos campos estruturados e registre a regra completa no texto. Sem base, complete os campos exigidos.\n\n"
     "Leia os avisos antes de escolher o conteúdo nos menus da ficha. "
     "**MESTRE VIU é um lembrete**, não uma aprovação registrada no bot. "
     "Descrição livre não cria automação nem bônus numérico.\n\n"
     "Abra `GC:guia custom` para a revisão e o cadastro da aprovação exata. "
     "Mesmo aprovado, um cartão com peça própria pode continuar sem recálculo independente."),
    ("Como emitir a carteira e acompanhar salários",
     "Em **CONFIGURAÇÃO → Emissão e salários** (seção 14), confira a situação em **O46**, próximo fechamento em "
     "**O48**, créditos em **O49**, referência do Grau em **O50**, início do ciclo em **O69**, participações em "
     "**O70**, previsão em **O71** e último fechamento em **O72**.\n\n"
     "**O salário só conta depois de EMITIR** na CARTEIRA (AT3) ou CONFIGURAÇÃO (O39). A caixa se desmarca ao "
     "salvar; marcar de novo não muda a data. Para corrigir, digite dd/mm/aaaa em **O38**, da emissão atual até "
     "hoje; sem emissão, só hoje. A correção preserva salários vencidos e reinicia o ciclo aberto. Datas "
     "recusadas aparecem em O46.\n\n"
     "O padrão é um período de **30 dias**, pelo **Grau no fechamento**, mínimo de **25%** e **100% com 3 "
     "participações**. Pesos: Curta 1, Padrão 1, Longa 2, Final de arco 3, Solo simples 1 e Solo complexa 1. "
     "Mude regras apenas com o mestre.\n\n"
     "O cálculo é **na hora, por fórmula**, inclusive no Android: não exige ativar conferência diária nem abrir "
     "menu. O pendente já entra no TOTAL DISPONÍVEL. **Últimos 10 créditos**, em K81:P90, reúne livro e "
     "pendente, mais recente primeiro. Para consultar o livro, no PC use **Ver → Mostrar → SALÁRIOS**, uma aba "
     "oculta; preserve os registros.\n\n"
     "O bot não certifica datas de missão nem o histórico salarial, emissão ou saldo: esses dados não são "
     "exportados pela ANALISE atual."),
    ("Como registrar missões e atualizar a ficha",
     "Para uma missão contar no acompanhamento salarial, preencha **nome e tipo válido** no painel da FICHA "
     "PESSOAL. A ficha registra data e identidade. Corrigir o texto conserva a data; para substituir por outra "
     "missão, limpe primeiro o nome antigo.\n\n"
     "**No celular ou PC**, use a caixa **CORRIGIR DATA**, acima de MAIS MISSÕES: nome da missão em **BI11** e "
     "data real em **BO11**, como dd/mm/aaaa. Aguarde de 5 a 15 segundos. A própria caixa mostra **✓ nome: "
     "data** ou **⚠ motivo**. Nome inexistente ou repetido, data inválida, futura ou de período já pago exigem "
     "correção; não invente outra data para contornar o aviso. O pendente recalcula, sem alterar pagamentos já "
     "fechados.\n\n"
     "O app do Android não executa os menus personalizados nem a rotina de abertura. Use os campos de edição "
     "para emissão, gasto/ganho, correção de data e paleta.\n\n"
     "Antes da sessão, confira recursos, equipamento, munição e efeitos ligados. Depois, registre gastos, "
     "recuperação, missões e ganhos autorizados. Para uma nova análise, envie o link ou XLSX atualizado; o "
     "painel antigo não acompanha edições. Se algo falhar, confira os avisos e informe a aba e a ação ao "
     "responsável. Preserve fórmulas e registros ocultos."),
))
