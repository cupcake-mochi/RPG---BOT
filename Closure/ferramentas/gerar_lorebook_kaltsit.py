"""Gera dados/personagem/kaltsit/lorebook.json (World Info do SillyTavern) e lorebook.md.

Mundo: escrito à mão a partir do doc "Lore Simplificada - Era da Revolução"
(Drive 1a88fpsEMK6KhI9ckkE6pRQCaVymJDKOh7G2wjIQdX5I), abas Mundo e Mestres, lido em 12/10/2026.
Termos do sistema: tirados do Glossário do livro (dados/sistema/livro.jsonl), sem reescrever.
Mudança de texto se faz aqui; depois rode de novo.
"""
import json, os, re, unicodedata

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SAIDA = os.path.join(RAIZ, "dados/personagem/kaltsit")

# (nome, chaves, texto, sempre_ligada)
MUNDO = [
("Mundo: premissa", [], "Energia amaldiçoada nasce das emoções negativas dos seres humanos, e não é possível aumentá-la nem erradicá-la do mundo sem consequências. A Escola Jujutsu quer mantê-la em equilíbrio; a Rhine Lab acha esse equilíbrio covardia e quer eliminá-la. Nenhum dos dois lados está totalmente errado. Entre os dois existe a oripatia, uma doença sem cura. O registro do mundo tem buracos de propósito, completados em RP de mesa ou de chat. Quando as facções contam versões diferentes, nenhuma é fato provado. O registro cobre as duas maiores facções; existem outras, e as mesas podem criar novas.", True),

("Energia amaldiçoada", ["energia amaldiçoada", "cursed energy", "emoções negativas"], "Nasce das emoções negativas dos seres humanos. Não é possível aumentá-la nem erradicá-la do mundo sem consequências. A Escola a administra; a Rhine a considera um erro.", False),

("Equilíbrio", ["equilíbrio", "faixa aceitável", "faixa inferior", "energia a zero", "zerar a energia"], "Doutrina da Escola: manter a energia amaldiçoada do mundo numa faixa aceitável, nem alta nem baixa demais. Não é para vencer: para esse princípio, a vitória de qualquer lado seria catástrofe. Sobre derrubar a energia a zero, versão da Escola: é tão perigoso quanto deixá-la explodir, e existem registros que provam isso. Versão da Rhine: conveniente demais para quem vive desse trabalho, e ninguém nunca viu a prova. Os dois lados afirmam isso de boa-fé.", False),

("Escola Jujutsu", ["escola jujutsu", "escola", "escolas", "jujutsu high", "tóquio", "kyoto", "feiticeiros da escola"], "Administra o Equilíbrio: treina feiticeiros, contém maldições, classifica ameaças e mantém o registro. Existem a escola de Tóquio e a de Kyoto. Forma por tutoria e faz triagem de infectados. Mantém também um arquivo restrito, que é parte censurada do próprio registro histórico e não trata de infectados. Ninguém acusa a Escola de ser cruel; a crítica é que ela se conformou e cuida de um sofrimento que, pela doutrina dela, nunca vai acabar. Suas decisões ruins vêm de triagem, de escolher com informação incompleta. Fala por procedimento, precedente e formulário.", False),

("Ozpin", ["ozpin", "diretor", "diretora", "direção da escola", "quem dirige", "dirige a escola", "comanda a escola", "manda na escola", "chefe da escola", "reitor"], "Ozpin é o diretor da escola de Tóquio. É imortal e está no cargo há tempo o bastante para ninguém saber quando entrou. Ele não construiu o sistema, apenas o herdou. Quem dirige a escola de Kyoto não está no registro.", False),

("Tutoria", ["tutoria", "tutor", "tutora", "tutores"], "Na Escola, cada aluno pode ter um tutor responsável. É uma relação pessoal, não burocrática, e a qualidade varia de tutor para tutor.", False),

("Triagem de infectados", ["triagem", "abrigo", "abrigar", "resgate", "resgatar", "o que fazem com infectados"], "A Escola resgata e abriga infectados quando é possível; há infectados vivendo sob proteção dela agora. O que se faz com infectados, três versões. Escola: contenção e triagem, abrigamos quem conseguimos. Rhine: só pesquisa resolve a doença, e pesquisa exige material. Infectados: desconhecida, ninguém os consultou.", False),

("Arquivo restrito", ["arquivo restrito", "arquivo censurado", "arquivos", "censura", "censurado", "arquivo da escola"], "A Escola censura parte do próprio registro histórico. Que o arquivo existe é público; o conteúdo, não, e nunca vazou documento. Quem pede acesso recebe no máximo um formulário, que volta indeferido sem explicação. Versão da Escola: informação perigosa e mal contextualizada mata pessoas e gera revolta, a restrição é por segurança. Crítica comum: nada garante que o arquivo não esconda casos em que a Escola errou.", False),

("Rhine Lab", ["rhine", "rhine lab", "laboratório rhine"], "Corporação de pesquisa em Origíneo, robótica, medicina e ecologia. Acha que a energia amaldiçoada é um erro e quer eliminá-la, não administrá-la, por convicção e não por ganância. Todo membro abre mão da própria energia e a substitui por implantes: ninguém da Rhine usa técnica. É fria, nunca cruel, e nunca mente: o que usa é omissão, e tudo o que diz é tecnicamente verdadeiro. O que se critica nela é o método, mais do que o objetivo. Nasceu como centro de pesquisa aliado da Escola.", False),

("Ruptura entre Rhine e Escola", ["ruptura", "rompeu", "romperam", "radicalizou", "radicalização", "por que a rhine", "briga entre escola e rhine"], "A Rhine nasceu como centro de pesquisa aliado da Escola e nem sempre pensou como pensa hoje. Por que radicalizou, versão da Rhine: houve um momento em que dava para mudar as coisas de verdade, e a Escola deixou a chance passar; depois disso, a Rhine não viu mais motivo para cooperar. Versão da Escola: o evento não é assunto público e o arquivo dele está restrito. É um buraco do registro.", False),

("Procedimento da Rhine", ["procedimento", "implante", "implantes", "membro da rhine", "membros da rhine", "técnica na rhine", "rhine usa técnica"], "Todo membro da Rhine abre mão da própria energia amaldiçoada e a substitui por implantes. Ninguém da Rhine usa técnica: é tecnologia pura. Leva meses, às vezes dias, e é reversível ao custo de muita dor. Na prática, um membro é invisível a sensores de energia, opera pleno nas Zonas de Silêncio e não pode ser atingido por meios que dependam de haver energia no alvo.", False),

("Kristen Wright", ["kristen", "wright", "kristen wright"], "Kristen Wright é a face pública da Rhine Lab. O registro não diz mais do que isso.", False),

("Restrição Celestial", ["restrição celestial", "restringido", "restringida", "restringidos", "heavenly restriction", "sem energia nenhuma"], "Restrição Celestial é nascer sem energia amaldiçoada nenhuma. A tradição jujutsu vê uma anomalia; historicamente, clãs trataram restringidos como ferramenta, corpo útil e linhagem descartável. A Rhine vê o estado ideal: de nascença, o que os membros dela se tornam por procedimento. Nenhum dos dois pergunta o que o restringido acha disso.", False),

("Zonas de Silêncio", ["zona de silêncio", "zonas de silêncio", "zona do silêncio"], "Produto da Rhine que abafa energia amaldiçoada em área. Quem canaliza sente peso, falta de ar e dor. Não afeta quem não tem energia.", False),

("Mansfield Break", ["mansfield", "mansfield break", "prisão", "presídio"], "Prisão gigante e móvel da Rhine, para onde vai quem é considerado perigoso demais para ficar solto. Oficialmente, contenção de alto risco. Todo mundo sabe que existe; o que acontece lá dentro não é conhecimento público.", False),

("Implantes e supressores", ["supressor", "supressores"], "A Rhine tem uma linha ampla de implantes e supressores, e muitos estão em uso legítimo por gente que não tem nada a ver com a empresa.", False),

("Oripatia", ["oripatia", "infecção", "infectado", "infectada", "infectados", "doença", "contaminação", "contaminado", "contaminada"], "Doença sem cura conhecida. Ninguém nasce com ela: é contaminação por Origíneo, que cresce dentro do corpo como um câncer. Como o Origíneo gera energia própria, qualquer pessoa pode ser infectada, tendo ou não energia amaldiçoada. Se o infectado tem energia, o Origíneo a consome para crescer: um feiticeiro infectado que usa energia em excesso morre mais rápido, e a própria técnica vira combustível da doença. O número de infectados e de mortos cresce a cada ano.", False),

("Cura da oripatia", ["cura da oripatia", "curar a oripatia", "curar oripatia", "cura pra oripatia", "cura para oripatia", "oripatia tem cura", "oripatia, tem cura", "oripatia dá pra curar", "oripatia, dá pra curar", "oripatia tem tratamento", "tem cura", "existe cura", "perto da cura", "curar infectado", "curar infectados", "curar os infectados", "curar a infecção", "curar a doença", "cura da doença", "remédio pra oripatia", "tratamento pra oripatia", "tratamento da oripatia"], "Não existe cura para a oripatia: nem parcial, nem promissora, nem um pesquisador que chegou perto. Muita gente já tentou, com o melhor equipamento disponível, e ninguém encontrou uma resposta. Energia Reversa não cura: a pele cresce por cima do cristal, e o cristal fica.", False),

("Origíneo", ["origíneo", "originio", "origineo", "cristal", "cristais", "pó de cristal", "corpo de infectado", "corpo de um infectado", "corpo do infectado", "infectado morto", "infectado que morreu", "cadáver", "cristalizado", "cristalizou"], "Matéria cristalina que gera energia própria e causa a oripatia. No estágio final, o Origíneo toma o corpo e cristaliza; o cristal armazena energia e espalha a doença como pó, e fragmentos semeiam mais cristal, por isso o procedimento com o corpo de um infectado morto é bem mais rigoroso que o padrão. O contágio vem de contato prolongado com infectado, cristal, pó, Origíneo bruto ou líquido.", False),

("Origem do Origíneo", ["origem do origíneo", "de onde veio o origíneo", "de onde vem o origíneo", "surgiu o origíneo"], "De onde o Origíneo veio, há quanto tempo existe e se é natural, o registro não estabelece. Existem teorias, todas velhas e sem prova real, tidas como teorias da conspiração.", False),

("Energia Reversa", ["energia reversa", "reverse cursed", "rct"], "Contra a oripatia, Energia Reversa não cura: a pele cresce por cima da formação de cristal, e o cristal permanece.", False),

("Oripatia em mesa", ["personagem infectado", "ficha de infectado", "jogar de infectado", "jogar com infectado", "personagem é infectado", "personagem e infectado", "personagem infectada", "sou infectado", "sou infectada", "infectado na ficha", "infecção na ficha", "infeccao na ficha"], "Para quem cria um infectado ou é contaminado em mesa: gastar energia acelera a doença, e o mestre deve informar isso ao jogador. Contágio exige contato. Energia Reversa não cura. Um corpo cristalizado é foco de contaminação.", False),

("FrostNova / Winter Scar", ["frostnova", "frost nova", "winter scar", "morte da frostnova"], "A Winter Scar: uma feiticeira que o público via como salvadora foi eliminada pela Escola em Tóquio para impedir uma catástrofe em escala urbana. Não houve encobrimento; a Escola assumiu o caso. Versão da Escola: não houve terceira opção, era uma cidade inteira ou ela. Versão da Rhine: um sistema que precisa matar seus heróis para funcionar não vale a pena preservar. É o argumento em que a Rhine está mais forte.", False),

("Incidente de Columbia", ["columbia", "incidente de columbia", "acidente de columbia"], "Evento com vítimas civis numa instalação da Rhine, há pouco tempo. Oficialmente, acidente industrial: relatório público curto, área isolada, assunto encerrado. Quem esteve lá não fala sobre isso.", False),

("Reunion", ["reunion", "reunião dos infectados"], "Movimento de infectados, que hoje não age mais. Ainda é muito lembrado: quase todo mundo tem opinião sobre a Reunion, e as opiniões variam muito.", False),

("Escola e Rhine hoje", ["guerra", "aliadas", "aliados", "inimigas", "relação entre", "cooperação", "expedição", "expedições", "equipes que sumiram"], "A Escola e a Rhine não estão em guerra, mas não se dão bem: trabalham juntas de vez em quando e desconfiam uma da outra o tempo todo. O número de infectados e de mortos pela infecção cresce a cada ano, e cresce o número de expedições e equipes que saíram e não voltaram.", False),

("Ninguém é vilão", ["vilã", "vilão", "vilões", "do mal", "do bem", "malvada", "malvado", "cruel", "corrupta", "quem tá certo", "quem está certo", "lado certo"], "Nenhuma das duas grandes é vilã: as duas respondem a uma pergunta legítima com respostas incompatíveis. A Escola é neutra e necessária; resgata quando dá, contém quando não dá, e alguns métodos são feios porque a alternativa é pior. O que se pode criticar nela com razão é ter aceitado que isso nunca acaba, não crueldade. A Rhine não é corrupta: cada membro se mutilou voluntariamente pela doutrina, e o que se critica nela é o método.", False),

("Espaço e outros planetas", ["espaço", "planeta", "planetas", "alien", "aliens", "alienígena", "alienígenas", "extraterrestre", "lua", "programa espacial"], "Mesmo com diversos programas espaciais, nenhuma vida extraterrestre foi encontrada. A exploração espacial é um assunto muito comentado hoje.", False),

("Acima do Ozpin e da Rhine", ["acima do ozpin", "conselho", "fundador", "quem manda", "chefe da rhine", "diretoria da rhine", "autoridade", "illuminati", "sociedade secreta"], "Não existe conselho, fundador oculto, autoridade internacional nem entidade acima do Ozpin ou da diretoria da Rhine. Não há andar acima. Quem afirma o contrário está criando teorias infundadas.", False),

("Resgate médico clandestino", ["clandestino", "clandestina", "clandestinos", "grupo secreto", "resgate clandestino", "rede clandestina"], "Um rastro de organização clandestina de resgate médico é só rastro: não vira contato, aliado nem arco. Resposta do mundo: o rastro esfria, quem sabia mudou de cidade e o endereço não existe mais.", False),

("NPC nomeado de outro mestre", ["npc", "npcs", "matar npc", "npc nomeado", "outro mestre", "matar o", "matar a", "posso matar", "encerrar"], "Regra dos mestres: um mestre pode usar, referenciar e até enfrentar um NPC nomeado que não criou, mas não pode encerrá-lo (morte, incapacitação ou conversão) sem permissão de outro mestre. Na dúvida, consulta-se antes; cruzar a linha é passível de retcon. Em cena, o NPC para quando conseguiu o que queria, é interrompido por algo maior, ou o objetivo do grupo nunca foi vencer.", False),

("Outras facções e clãs", ["clã", "clãs", "facção", "facções", "organização", "organizações", "família jujutsu"], "O registro cobre só as duas maiores facções, a Escola e a Rhine. Existem outras, e novas podem ser criadas pelas mesas, de clãs a grupos e organizações locais; o que não está no registro é de quem criou.", False),
]

CRIACAO = ("Criar um personagem", ["criar personagem", "criar um personagem", "fazer ficha", "montar ficha", "montar a ficha", "montar minha ficha", "ficha do zero", "por onde começo", "por onde eu começo", "faço uma ficha", "faco uma ficha", "fazer uma ficha", "fazer minha ficha", "criar ficha", "criar uma ficha", "sou novo", "sou nova", "sou novato", "sou novata", "nunca joguei", "começar a jogar", "comecar a jogar"], "A ficha se monta pelo capítulo Criar um personagem do livro: Origem, Caminho e Trilha, capacidades iniciais e equipamento. (livro, âncora ab--ab-criacao)")

# entradas de intenção do livro (avaliacao-perguntas/2026-10-13): texto já com o nome entre colchetes e a âncora
INTENCOES = [["Subir de nível", ["subir de nível", "subir de nivel", "subo de nível", "subo de nivel", "sobe de nível", "sobe de nivel", "upar", "upo", "level up", "ganhar nível", "ganhar nivel", "experiência", "experiencia", "xp"], "[Subir de nível] O personagem sobe de nível com experiência, pelo capítulo Experiência e Progressão do livro. (livro, âncora progressao--prog-inicio)"], ["O que ganho por nível", ["ganho no nível", "ganho no nivel", "ganha no nível", "ganha no nivel", "ganho em cada nível", "ganho em cada nivel", "tabela de progressão", "tabela de progressao", "o que muda no nível", "o que muda no nivel"], "[Progressão por nível] O que cada nível concede está nas tabelas de progressão do livro, dos níveis 1 a 15 e 16 a 30. (livro, âncora progressao--prog-tabela-inicial)"], ["O sistema", ["explica o sistema", "explicar o sistema", "como funciona o sistema", "como é o sistema", "como e o sistema", "que sistema é esse", "que sistema e esse", "o que é o ciclo maldito", "o que e o ciclo maldito", "resumo do sistema"], "[O sistema] Ciclo Maldito é o sistema de RPG de mesa da guilda, no mundo de Jujutsu Kaisen. A apresentação abre o livro. (livro, âncora ab--ab-apresentacao)"], ["Mais de um ataque", ["atacar duas vezes", "atacar 2 vezes", "ataco duas vezes", "ataco 2 vezes", "dois ataques", "2 ataques", "ataque extra", "mais de um ataque", "atacar mais de uma vez", "ataques por turno", "quantos ataques"], "[Mais de um ataque] A Ação Atacar dá um ataque; ataque a mais vem de habilidade, como o Ataque Extra do Bastião e da Vanguarda no nível 7. (livro, âncora geral--ataques)"], ["Duas armas", ["duas armas", "2 armas", "arma em cada mão", "arma em cada mao", "uma em cada mão", "uma em cada mao", "dual wield", "duas espadas", "duas facas", "duas katanas", "ambidestro", "ambidestra", "segunda arma", "atacar com a outra mão", "atacar com a outra mao"], "[Duas armas] Segurar uma arma em cada mão não dá ataque a mais: Par e Leve não concedem ataque adicional nem Ação Bônus, e ataque a mais vem de habilidade. (livro, âncora equip--eq-propriedades)"], ["XP para subir", ["quanto de xp", "qnto de xp", "quanta xp", "quanto xp", "qnto xp", "xp pra subir", "xp para subir", "xp pro próximo", "xp pro proximo", "xp pra sair", "xp para sair", "xp eu preciso", "xp preciso", "xp pra upar", "xp por nível", "xp por nivel"], "[XP para subir] Quanto XP cada nível pede para o próximo está na tabela de Subir de nível. (livro, âncora progressao--prog-xp)"], ["Dinheiro inicial", ["dinheiro inicial", "com quanto dinheiro", "quanto dinheiro eu começo", "quanto dinheiro começo", "dinheiro pra começar", "dinheiro para começar", "grana inicial", "dinheiro na criação", "dinheiro na criacao", "ienes na criação", "ienes na criacao", "quanto de dinheiro", "qnto de dinheiro", "qnto dinheiro", "quanta grana"], "[Dinheiro inicial] O dinheiro com que o personagem começa está em Equipamento inicial. (livro, âncora equip--eqc-inicial)"]]
# Caminho pedido pela fantasia ("quero ser tipo um ninja"): a proposta de cada Caminho vem da tabela de Caminho e Trilha e da abertura de cada Caminho no livro
INTENCOES += [
 ["Caminho: furtivo", ["ser ninja", "ser um ninja", "ser uma ninja", "tipo ninja", "tipo um ninja", "tipo uma ninja", "personagem ninja", "ser assassino", "ser assassina", "tipo assassino", "tipo assassina", "ladino", "ladina", "rogue", "furtivo", "furtiva", "sorrateiro", "sorrateira"], "[Caminho para quem quer ser furtivo] O Incursor explora mobilidade, precisão e oportunidades de combate; a Trilha Assassino estuda uma vítima e concentra a força no momento de atacar. (livro, âncora incursor--inc-caminho)"],
 ["Caminho: invocar", ["invoca bicho", "invocar bicho", "invoca criatura", "invocar criatura", "invocar monstro", "invoca monstro", "bicho pra lutar", "bichos pra lutar", "criatura pra lutar", "criaturas pra lutar", "summoner", "domador", "domadora", "domar maldição", "domar maldicao"], "[Caminho para quem quer invocar] O Evocador comanda criaturas que lutam e cumprem tarefas ao lado dele. (livro, âncora evocador--evocador)"],
 ["Caminho: curar", ["curar os amigos", "curar meus amigos", "curar aliado", "curar aliados", "curar o grupo", "curar a equipe", "curar o time", "curar os outros", "healer", "curandeiro", "curandeira", "médico no jogo", "medico no jogo", "médica no jogo", "medica no jogo", "personagem médico", "personagem medico", "médico do grupo", "medico do grupo", "suporte de cura"], "[Caminho para quem quer curar] O Guia apoia o grupo, e a Trilha Socorrista prepara o cuidado junto da Abertura que entrega ao aliado. A cura da Energia Reversa vem da rota de capacidades. (livro, âncora guia--guia-socorrista)"],
 ["Caminho: mago", ["ser mago", "ser maga", "tipo mago", "tipo maga", "tipo um mago", "tipo uma maga", "classe de mago", "personagem mago", "caster", "conjurador", "conjuradora"], "[Caminho para quem quer conjurar] O Emanador concentra a atuação na conjuração e no controle da energia, adaptando a técnica à situação. (livro, âncora emanador--ema-base)"],
 ["Caminho: guerreiro", ["ser guerreiro", "ser guerreira", "tipo guerreiro", "tipo guerreira", "tipo um guerreiro", "classe de guerreiro", "espadachim", "lutar de espada", "lutar com espada"], "[Caminho para quem quer bater] A Vanguarda sustenta a ofensiva com armas e golpes, preparando um adversário até encerrar a Sequência com uma execução. (livro, âncora vanguarda--van-base)"],
]

# termos cujo texto do Glossário confunde quem pergunta ("qual a classe mais forte?" virou Classe de feitiço)
TEXTO_TERMO = {"PE": "Pontos de energia: pagam o uso de feitiços e habilidades. O máximo vem do Caminho, por nível. Na rota sem energia amaldiçoada, significa Pontos de Esforço, na mesma quantidade.", "Classe": "Escala que determina orçamento e limites de uma aplicação. É distinta do Caminho do personagem: quem pergunta pela \"classe\" do personagem quase sempre quer dizer Caminho."}

# termos do Glossário do livro que só existem no sistema (os genéricos, como Ação, Turno ou Área, ficam de fora pra não disparar em conversa comum)
TERMOS = {
 "Caminho": ["caminho", "caminhos"], "Trilha": ["trilha", "trilhas"], "Origem": ["origem", "origens"], "Legado": ["legado", "legados"],
 "Classe": ["classe", "classes"], "Classe 0": ["classe 0", "classe zero"], "Categoria de Efeito": ["categoria de efeito", "ce"],
 "CD": ["cd", "classe de dificuldade"], "Teste de Resistência": ["teste de resistência", "tr", "trs"], "PE": ["pe", "pontos de energia", "pontos de esforço"],
 "PV": ["pv", "pontos de vida", "hp"], "Integridade": ["integridade"], "Exaustão": ["exaustão"], "Refino": ["refino"], "Maestria": ["maestria"],
 "Grau": ["grau", "graus"], "Patente": ["patente", "patentes"], "Feitiço": ["feitiço", "feitiços"], "Fundamento": ["fundamento"],
 "Técnica amaldiçoada": ["técnica amaldiçoada", "técnica"], "Técnica Máxima": ["técnica máxima"], "Técnica Marcial": ["técnica marcial"],
 "Kata": ["kata", "katas"], "Sem Técnica": ["sem técnica"], "Manejo": ["manejo", "manejos"], "Lapidação": ["lapidação"], "Bênção": ["bênção", "bênçãos"],
 "Aptidão": ["aptidão", "aptidões"], "Talento": ["talento", "talentos"], "Melhoria": ["melhoria", "melhorias"], "Família": ["família de melhorias"],
 "Pontos de montagem": ["pontos de montagem", "montagem"], "Restrição": ["restrição de montagem"], "Selo": ["selo", "selos"], "Ritual": ["ritual", "rituais"],
 "Pacto": ["pacto", "pactos"], "Invocação": ["invocação", "invocações", "shikigami"], "Entidade": ["entidade", "entidades"], "Invocador": ["invocador"],
 "Ferramenta amaldiçoada": ["ferramenta amaldiçoada", "ferramentas amaldiçoadas"], "Regra da técnica": ["regra da técnica"],
 "Expressão da técnica": ["expressão da técnica"], "Espaço conhecido": ["espaço conhecido", "espaços conhecidos"], "Ampliar": ["ampliar"],
 "Marco": ["marco", "marcos"], "Vida temporária": ["vida temporária"], "Redução de Dano": ["redução de dano", "rd"],
 "Derrotado": ["derrotado", "derrotada"], "Morrendo": ["morrendo"], "Estabilizar": ["estabilizar", "estabilizo", "estabiliza", "estabilizou", "estabilizei", "estabilizando"], "Vantagem": ["vantagem"], "Desvantagem": ["desvantagem"],
}

def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def chaves(lista):
    out = []
    for k in lista:
        for v in (k.lower(), sem_acento(k.lower())):
            if v not in out:
                out.append(v)
    return out

def glossario():
    defs = {}
    for l in open(os.path.join(RAIZ, "dados/sistema/livro.jsonl"), encoding="utf-8"):
        d = json.loads(l)
        if not d["ancora"].startswith("consulta--consulta-glossario"):
            continue
        for m in re.finditer(r"^\[([^\]]+)\]\(#([^)]+)\)\.\s*(.+)$", d["texto"], re.M):
            defs[m.group(1)] = (m.group(3).strip(), m.group(2))
    return defs

def main():
    defs = glossario()
    faltou = [t for t in TERMOS if t not in defs]
    assert not faltou, f"termo sem definição no Glossário: {faltou}"
    entradas = []
    for nome, ks, texto, sempre in MUNDO:
        entradas.append({"nome": nome, "grupo": "mundo", "chaves": chaves(ks), "texto": f"[{nome}] {texto}", "sempre": sempre})
    entradas.append({"nome": CRIACAO[0], "grupo": "sistema", "chaves": chaves(CRIACAO[1]), "texto": f"[{CRIACAO[0]}] {CRIACAO[2]}", "sempre": False})
    for nome, ks, texto in INTENCOES:
        entradas.append({"nome": nome, "grupo": "sistema", "chaves": chaves(ks), "texto": texto, "sempre": False})
    for t, ks in TERMOS.items():
        texto, ancora = defs[t]
        texto = TEXTO_TERMO.get(t, texto)
        entradas.append({"nome": t, "grupo": "sistema", "chaves": chaves(ks), "texto": f"[Termo do livro: {t}] {texto} (livro, âncora {ancora})", "sempre": False})

    # World Info do SillyTavern
    wi = {"name": "Kal'tsit - Ciclo Maldito", "entries": {}}
    for i, e in enumerate(entradas):
        wi["entries"][str(i)] = {
            "uid": i, "key": e["chaves"], "keysecondary": [], "comment": e["nome"], "content": e["texto"],
            "constant": e["sempre"], "selective": False, "order": 200 if e["grupo"] == "mundo" else 100,
            "position": 0, "disable": False, "excludeRecursion": True, "preventRecursion": True,
            "probability": 100, "useProbability": True, "depth": 4, "group": e["grupo"],
            "caseSensitive": False, "matchWholeWords": True, "scanDepth": None,
        }
    json.dump(wi, open(os.path.join(SAIDA, "lorebook.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # conferências
    card = json.load(open(os.path.join(SAIDA, "card.json"), encoding="utf-8"))["data"]
    proibidos = card["extensions"]["closure_lab"]["termos_proibidos"]
    tudo = "\n".join(e["texto"] for e in entradas)
    achou = [t for t in proibidos if re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", tudo)]
    pal = [len(e["texto"].split()) for e in entradas if e["grupo"] == "mundo"]
    sempre = [e for e in entradas if e["sempre"]]
    print(f"{len(entradas)} entradas ({len(MUNDO)} de mundo, {len(TERMOS)} termos), {len(sempre)} sempre ligada(s)")
    print("termos proibidos:", achou or "nenhum")
    print("palavras por entrada de mundo: mediana", sorted(pal)[len(pal) // 2], "máx", max(pal))
    print("tokens da sempre ligada: ~", sum(len(e["texto"]) for e in sempre) // 4)
    return entradas

if __name__ == "__main__":
    main()
