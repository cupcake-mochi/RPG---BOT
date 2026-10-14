# Gostos e hábitos fora do trabalho: Kal'tsit e Closure (canon)

> Pesquisa de 13/10/2026. **Referência, não vai direto pro bot**: as duas vivem no mundo do Ciclo
> Maldito, então nome próprio de Arknights (Theresa, Robin, Rhodes Island etc.) fica de fora do card;
> o que interessa é o gosto em si.
>
> **Formato de cada item:** gosto/hábito — citação curta original — fonte exata — status — muda depois?
>
> **Status:** **fato** = texto oficial do jogo que afirma isso; **fato (piada)** = oficial, mas de evento de
> 1º de abril ou fala de vendedora; **inferência** = minha leitura de um texto oficial que não afirma
> diretamente; **fã** = especulação de fã/wiki.
>
> **Fontes:**
> - Local: `dados/corpus_kaltsit/`, `dados/corpus_closure/` (arquivo:linha = roteiro de história).
> - Baixado em 13/10/2026 (só leitura, nada salvo no projeto): `ArknightsGameData` zh_CN, master
>   (`building_data.json` = mobília, `uniequip_table.json` = módulos, `skin_table.json` = roupas,
>   `handbook_info_table.json` = arquivos), e o mesmo do `ArknightsGameData_YoStar` en_US, que é o
>   espelho de 13/11/2025. **"Só CN"** quer dizer que o id não existe no en_US desse espelho.
> - Web: arknights.wiki.gg (Trivia, Gallery e a página do evento web Footprints).
> - Traduções do chinês são minhas.

---

## Kal'tsit

O material oficial quase não fala da vida privada dela. O que existe é pouco e indireto, e a maior
parte é do arco de 2025-2026 (morte no Ep. 15 e volta como Esperanta).

| # | Gosto/hábito | Citação original | Fonte exata | Status | Muda depois? |
|---|---|---|---|---|---|
| K1 | **Botânica**: conhece as plantas pelo nome, origem e uso | "Star Valerians. First discovered by the Gallic scholar Jacques in 817... the primary ingredient in many hypnotics." / Closure: "I forgot you had botanist listed on your resume." | `corpus_kaltsit/historia_en_US.jsonl`, `story_kalts_1_1.txt:274-276` e fala da Closure antes de `:280`; Profile: "Profoundly learned in... botany, geology" (`operadora_en_US.json`, Profile) | fato (o saber). Que seja um **hobby**, e não só formação: inferência | não |
| K2 | **Chá**: aceita, mas só quando insistem, e não costuma tomar chá com amigos | "Just this cup of tea, then." / Closure: "in these twelve years, you haven't had tea with me even once!" | `story_kalts_1_1.txt:286` e `:304` (corpus da Kal'tsit e da Closure) | fato (a cena). "Não gosta de chá": **não dá pra afirmar**; o que a cena mostra é que ela não para pra socializar | não |
| K3 | **Café**: nenhum gosto oficial. "Sir, your coffee" é ela disfarçada de criada servindo outra pessoa | "Sir, your coffee." | `level_act18d0_02_end.txt:18`; o disfarce é a roupa "The Remains of Time" ([Trivia](https://arknights.wiki.gg/wiki/Kal%27tsit/Trivia)) | fato de que **não** é gosto dela. No cap. 17 (só CN), "café" aparece só como metáfora: "你不能像索要一杯咖啡一样要求别人交还你的记忆" | — |
| K4 | **Trabalha até cair; não dorme**. Só "descansa" quando a enganam | Closure: "a herbal tea that Lena formulated. Really calms your mind, especially so for someone who hasn't had any shut-eye for three days straight." / "Sleep well in the garden, Kal'tsit." | `corpus_closure/historia_en_US.jsonl`, `story_kalts_1_1.txt:375`, `:383` | fato | sim: a Esperanta (só CN) passa mais tempo no Médico e menos em reuniões (Arquivo 1 da Esperanta) |
| K5 | **Dorme/descansa no sofá do escritório** | "Guest sofa... The master of the office rests here as well." (CN: "也是办公室主人休憩的地方") | mobília `furni_kaltsroom_sofa_01` "'Command: Rest'" (`building_data.json`, CN e EN) | fato | é da época depois da morte (conjunto refeito "pela memória da Mon3tr"); o hábito é de antes |
| K6 | **Ouvia música enquanto trabalhava** (aparelho no canto da mesa) | "凭Mon3tr的回忆复原的音乐播放器，曾放置在凯尔希办公桌的一角。纵使时光匆匆流逝，她在桌前忙碌的身影，依然会在旋律响起时浮现于眼前。" | mobília `furni_act72d6_audioPlayer_01` "追想回声" (`building_data.json` zh_CN; **só CN**) | fato (o aparelho estava na mesa e tocava enquanto ela trabalhava). **Que tipo de música: não diz** | — |
| K7 | **Toca piano** (passado de séculos atrás, em Leithanien) | Savage: "Doctor, Amiya, did you know Dr. Kal'tsit can play the piano?" / Amiya: "I never would have thought Dr. Kal'tsit had such a profound mastery of music." | evento web oficial **Footprints** (7º aniversário global, 08/10–07/11/2026), parada Concert Hall ([wiki](https://arknights.wiki.gg/wiki/Footprints)) | fato que ela **sabe** tocar. Que toque **hoje** ou por prazer: inferência. A ligação com a artista felina do registro é implícita na própria página | novo (out/2026) |
| K8 | **Proibiu bebida alcoólica no refeitório** | a regra "No Alcohol" que "Kal'tsit personally established... out of concern for the health of patients and certain Operators", e ela deu bronca em quem levou bebida escondida | Footprints, paradas Cafeteria (Past/Present) ([wiki](https://arknights.wiki.gg/wiki/Footprints), offset ~100000) | fato (a regra). Que ela mesma não beba: **inferência fraca**, o motivo dado é a saúde dos outros | — |
| K9 | **Não usa vestido de gala; é sempre igual no vestir** | Heidi: "have you ever seen Kal'tsit in a gown?... you should suggest that Kal'tsit try out a few different styles of dress." | Footprints, Banquet of Nobles | fato (pela fala de outra personagem) | — |
| K10 | **Não deixava ninguém fazer exame nela** | "Also, yeah, Kal'tsit really doesn't let people give her physical exams." | `operadora_en_US.json`, Clinical Analysis | fato | **sim**: Esperanta (só CN), "是的，凯尔希终于愿意配合接受体检了" (Warfarin, 临床诊断分析 em `operadora_esperanta_zh_CN.json`) |
| K11 | **Assistia filmes quando a arrastavam** | "she would even drag Kal'tsit to their Glasgow Gang dormitory to watch movies." | Arquivo 2 da Siege (Vina) `char_1019_siege2` (`handbook_info_table.json` en_US) | fato que **foi**, e arrastada. Gosto de cinema: não | não |
| K12 | **Quer saber das notícias do mundo** (jornais) | Closure: "各种报纸合订本... 凯尔希没说，但这段时间泰拉发生了什么，她肯定想知道。扫描仪和阅读器就当我送她的了。" | módulo da Closure `uniequip_002_closur` "给自己的小奖杯" (TAC-X, `uniequip_table.json` zh_CN; **só CN**, global previsto 14/10/2026) | **inferência da Closure** dentro do texto oficial ("ela não disse, mas com certeza quer saber") | é da Esperanta (depois da volta) |
| K13 | **Gosta de contar histórias do passado, se pedirem** (só depois da volta) | "如果你希望的话，我也愿意与你分享那些过去的见闻，尽管我绝不保证它们听起来一定有趣。" | `operadora_esperanta_zh_CN.json`, 档案资料四; e 信赖提升后交谈2 ("我乐意与你分享过往万年的见闻") | fato | **sim**: só a Esperanta (CN). A clássica guarda segredo |
| K14 | **Ri sem perceber** | "Amiya... did I smile?" / Esperanta: "……我在笑？" | `level_main_07-04_end.txt:63`; `operadora_esperanta_zh_CN.json`, 档案资料四 | fato | nas duas versões |
| K15 | **Gosta dos momentos de pausa, que ficaram mais frequentes por causa dos amigos** | "I occasionally needed to pause for a short rest, and I have realized that these temporary breaks have increased in frequency... companions... who allowed me to relax in an almost lazy manner" | `operadora_en_US.json`, Archive File 5 | fato | — |
| K16 | **Cabelo comprido, "parece mais gentil"** (boato entre funcionários) | "我真的觉得留长发的凯尔希老师更好看，看起来好像温柔了一点。" | `operadora_esperanta_zh_CN.json`, 档案资料一 | fato (fofoca dentro do texto) | **sim**, só Esperanta |
| K17 | **Roupa casual** existe só como disfarce | "凯尔希的私服之一" / "凯尔希隐藏身份时穿过的服装" | roupa `char_003_kalts@sale#14` "时遗" / The Remains of Time (`skin_table.json`) | fato | — |
| K18 | **Nada sobre gato, comida favorita, livro favorito, hobby declarado** | — | a página de [Trivia](https://arknights.wiki.gg/wiki/Kal%27tsit/Trivia) não tem nada disso; TV Tropes também não | — | — |

**Especulação de fã ou só da wiki, não usar como gosto:**
- A Trivia diz que ela foi inspirada em John Oldman, de *The Man from Earth* (fonte: o ilustrador 唯@W, GCORES CLIPS VOL.12). É do autor, não um gosto dela.
- Na Gallery da wiki, os desenhos "musicista de Leithanien" e "professora da Ludwigs-Universität" são de @Kaifei_29 para o Footprints. O texto do evento não diz que a professora "séria e erudita" é ela; isso é inferência da página.
- A "idade de 13.352 anos" é especulação da Trivia (já marcada no `kaltsit/canon.md`).

---

## Closure

Ao contrário da Kal'tsit, a Closure tem muito material de vida privada. Quase tudo que é mais
específico é **só CN** (ela virou operadora em 01/05/2026, e o conjunto de mobília dela também é CN).
O global deve receber isso a partir de 14/10/2026, **não confirmado** (ver `closure/canon.md`).

### Comida e bebida

| # | Gosto/hábito | Citação original | Fonte exata | Status | Muda depois? |
|---|---|---|---|---|---|
| C1 | **Café, muito** | "他们就算吸我的血也只能吸到咖啡" ("se me chupassem o sangue, só ia sair café") / "给，咖啡。看你那黑眼圈，昨晚又熬夜了吧？" | `operadora_zh_CN.json`, 交谈2 e 问候 | fato (só CN) | — |
| C2 | Derrama café na bancada de trabalho (o tapete teve que ser trocado) | "自从可露希尔不小心在之前的普通地毯上打翻了润滑油和咖啡..." | `furni_closureRoom_carpet_02` "显像重组" (**só CN**) | fato | — |
| C3 | **Bebida energética cheia de açúcar** | "放满了可露希尔爱喝的高糖功能饮料，能有效恢复理智。放心，血魔可不怕胖！" | `furni_closureRoom_shelf_01` "时钟小柜" (**só CN**) | fato (é o gosto mais explícito que existe: "爱喝", "adora beber") | — |
| C4 | **Chocolate** (o doce dela, até em combate) | "一直盯着屏幕头都晕了……巧克力巧克力……" | `operadora_zh_CN.json`, 作战中4 | fato (só CN) | — |
| C5 | **Salgadinho de batata (chips)**, comendo enquanto trabalha | "可露希尔在旁边嚼着薯片说：'就该给每个人都配一把。'" / "she threw the bag of chips in her hands" | `furni_closureRoom_chair_01` (só CN); Arquivo 2 da Eunectes `char_416_zumama` (EN) | fato | — |
| C6 | **Biscoito sabor churrasco**, que oferece pros outros | "烧烤味饼干，来一片？" | `operadora_zh_CN.json`, 信赖触摸 | fato (só CN) | — |
| C7 | **Lista de lanches favoritos**: chocolate, chips, fruta seca, biscoito | o "sonho" com a rainha oferece "坐在这把宝座上……吃巧克力... 如果巧克力不合你的心意，这里还有薯片、果脯、饼干……"; no fim ela dá de presente "下个月的巧克力、薯片、果脯和饼干都免单了" | `corpus_closure/historia_zh_CN.jsonl`, `story_closur_1_1.txt:836-840` e `:940` (só CN) | fato que esses são os lanches dela; "favoritos" é **inferência** (o sonho oferece exatamente o que ela gosta, e é a mesma lista que ela dá de presente) | — |
| C8 | Esquece de comer quando trabalha de fone, e depois come por três | "I'm so hungry I could swallow a meatbeast whole!" / "I was wearing my headphones so I couldn't hear the door" / "I'm not here to listen to a sermon during mealtime!" | `level_act7mini_st06.txt:494`, `:499`, `:504` | fato | — |
| C9 | **Não gosta de comida "saudável"** | "Wanna finish this health food for me? I mean it. This stuff's got a real funny taste." | `level_st_09-04.txt:40` (em seguida: "Just kidding.") | fato, mas meio piada | — |
| C10 | **Chá da tarde com amigos**: ela que convida | "can't you at least finish your tea first? Think of this as having afternoon tea with your buddy." | `story_kalts_1_1.txt:284` (a Closure usou o chá pra fazer a Kal'tsit dormir) | fato que ela convida; "gosta de chá": inferência | — |
| C11 | Biscoito e chá de flor | "who could refuse flower cookies AND flower tea that good, you know? Plus, I got a double portion!" | `story_podego_1_1.txt:463` | fato | — |
| C12 | Bebida alcoólica: sem gosto declarado; numa fala de vitrine aparece "*hic*" | "the food and drinks here are must-try. Good enough to convince me to leave this sunless den, *hic*..." | `corpus_closure/loja_en_US.json`, `vitrine` | fato (piada): é fala de vendedora pra vender um pacote | — |
| C13 | Mantém a "rede de lanches" da nave (vende lanche pro pessoal) | "——零食网络的渠道被芙蓉发现了？！" / "采购部这么多种类的零食，当然是有特殊渠道才能买到啦！" | `story_closur_1_1.txt:250`; `operadora_zh_CN.json`, 交谈1 | fato (só CN) | — |

### Tempo livre: jogos, filmes, música, leitura

| # | Gosto/hábito | Citação original | Fonte exata | Status | Muda depois? |
|---|---|---|---|---|---|
| C14 | **Filme ruim e "estranho"**, assistido com amigos: clube de cinema | "We put on four movie clubs together, plus we watched a dozen shit flicks together... we're shit flick buddies." / "If you ever find some who's willing to watch shitty movies with you, that's a true friend" | `story_robin_1_1.txt:628`, `:634` | fato | — |
| C15 | Procura **filmes cult, de nicho**, e arrasta gente pra assistir | "可露希尔时常能在罗德岛的媒体库中找到一些风格小众的怪奇电影，然后她会四处拐来其他干员坐上凳子陪她一起观看。" | `furni_closureRoom_ledchair_01` "流光坐凳" (**só CN**) | fato | — |
| C16 | **Filmes e novelas/séries** ("soaps"), e reclama de não achar companhia | "she's been frustrated at not finding someone of like mind to have fun watching movies and soaps together." | Arquivo 3 da Robin `char_451_robin` (`handbook_info_table.json` en_US) | fato | — |
| C17 | Reconhece clichê de filme B | "There's way too much exposition in the script? And it's full of B-movie garbage?" | `level_act6d5_st03.txt:1001` | fato | — |
| C18 | **Gamer e criadora de jogo**: fez um jogo com o Conviction, que foi mal avaliado | "the all new joint Closure and Conviction-developed game—Soldiers Assemble: Barrage Fortress!" / pôster: "因为游戏差评率太高，视频已经不再公开了" | `level_act3fun_entry.txt:227` (evento de 1º de abril); `furni_closureRoom_poster_02` "《狂弹要塞》海报" (só CN) | fato (piada no evento, fato na mobília) | — |
| C19 | **Ganha torneio de jogo e de game jam** e guarda os troféus. Parou de ganhar por falta de tempo | "存放着各类游戏比赛和游戏开发比赛的奖杯... 自从她身上的担子加重之后，奖杯已经很久没有增加过了。" | `furni_closureRoom_cabinet_01` "成就展柜" (só CN) | fato | **sim**: piorou depois do Ep. 15 (mais trabalho) |
| C20 | **Estuda speedrun com glitch** | "学习邪道速通手法" | `furni_closureRoom_computerdesk_01` "第一控制台" (só CN) | fato | — |
| C21 | Faz os próprios controles e acha qualquer modelo de 2 meses atrás velho | "那不都是两个月前的过时款式了，我已经在开发新的了。" | `furni_closureRoom_equipmentdesk_01` (só CN) | fato | — |
| C22 | Faz programa de **aposta** e é banida | "'争锋频道自动评估投注'程序，然而测试阶段使用的账号就分别惨遭凯尔希和主办方封禁" | `furni_closureRoom_officedesk_01` (só CN) | fato | — |
| C23 | Ganhou um torneio "porque sentou mais perto do servidor" | "最后她靠着坐得离服务器最近，在分数达成时间的判定上获胜" | `furni_closureRoom_poster_01` "《心连心》海报" (só CN) | fato | — |
| C24 | Fliperama | EN: "Closure's favorite brand new gaming machine." / CN: "可露希尔大力引进的最新款街头游戏机" | `furni_act14d0_arcadegame_01` | fato. **Diferença de tradução:** o EN diz "favorite"; o CN só diz que ela "trouxe com empenho" | — |
| C25 | Software de criar jogo de console portátil, provavelmente o presente que deu a si mesma | "掌机游戏开发大师V10.0——东国（南院）... 售价：-" (o nome do módulo é "给自己的小奖杯", "um troféuzinho pra mim mesma") | `uniequip_002_closur` (só CN) | fato que comprou; "é pra ela mesma": **inferência** (o texto é cortado em "……") | — |
| C26 | **RPG de mesa** (chama pra montar grupo) | "Dominions & Dogma is already on 10th Edition... wanna get a group together?... we'll letcha be Dominion Master!" | `loja_en_US.json`, `vitrine` | fato (piada): fala de vendedora. É a ponte mais natural com o servidor de RPG, mas não passa de uma linha de venda | — |
| C27 | **Música o tempo todo**: não trabalha sem música e usa fone | "Can't even do this job anymore without listening to some music." | `level_act7mini_st06.txt:500` | fato | — |
| C28 | **Gosta de D.D.D.** (Destructive Dragon Demon, DJ de EDM do mundo do jogo) | "现在它已经可以基于可露希尔的实时精神状况自动播放D.D.D.的不同专辑了。" | `furni_closureRoom_collectioncabinet_01` "多用途音乐机" (só CN); quem é D.D.D.: [wiki](https://arknights.wiki.gg/wiki/Destructive_Dragon_Demon) | fato (tem os álbuns e o player toca D.D.D. conforme o humor dela). Gênero: **EDM** | — |
| C29 | "Quem não gosta de música não sabe viver" | "There are two kinds of people: music lovers, and people who don't know how to live. So which kind are you, Doc?" | `loja_en_US.json`, `vitrine` | fato (piada): fala de vendedora | — |
| C30 | **Exercício só com jogo de dança**, e o tapete está empoeirado | "'华法琳建议我多运动，我觉得音乐跳舞游戏就够了'... 上面浅浅地积着一层灰" | `furni_closureRoom_carpet_01` "感应式地毯" (só CN) | fato | — |
| C31 | **Lê muito**: periódicos, revistas, livros técnicos de várias áreas, e paga por eles | "一份长长的书单，横跨从药品制造到精密工业到土木工程再到装潢设计的广阔领域... 这都是她看过的东西... 为这些期刊、杂志、著作... 花了不少钱" | `operadora_zh_CN.json`, 晋升记录 | fato (só CN). É leitura técnica; romance não aparece | — |
| C32 | Coloca livro técnico na lista de leitura dos outros (piada) | "'Today's booklist... *Originium and Art of Drone Maintenance*—Closure, did you put this on here?'" | `furni_magicAcademy_wallpaper_01` (EN e CN) | fato | — |
| C33 | Gosta de modificar robô e de robô "com problemas próprios" | "不觉得有自己苦恼的机器才更像人吗？" / Friston-3: "Closure takes great joy in" as modificações | `operadora_zh_CN.json`, 交谈3; Arquivo 1 do Friston-3 `char_4093_frston` (EN) | fato | — |
| C34 | Quer que o Lancet-2 a chame de "irmãzona fofa" | "让Lancet-2叫我'可爱的可露希尔姐姐'更有趣" | `operadora_zh_CN.json`, 交谈3 | fato | — |

### Sono, rotina, manias

| # | Gosto/hábito | Citação original | Fonte exata | Status | Muda depois? |
|---|---|---|---|---|---|
| C35 | **Coruja: dorme tarde porque gosta** | CN: "'可露希尔确实昼伏夜出，但那是因为她喜欢熬夜，对吧？'隐德来希笑道。" / EN: "'Closure's sleep schedule is rather atypical for our kind,' Entelechia says with a grin." | `furni_villagemanor_arch_01` "Nightwalker Arch" | fato. **Diferença de tradução:** o CN diz "porque gosta de virar a noite"; o EN só diz "horário atípico" | — |
| C36 | O cômodo dela é feito pra virar a noite | "想想罗德岛的总工程师为什么经常熬夜不休息，就能明白这并不奇怪。" | tema `furni_set_closureRoom` "可露希尔的万能空间" (só CN) | fato | — |
| C37 | **Cochilo em qualquer lugar**, e pede cinco minutinhos | "能不能麻烦你把办公室灯光调暗点，我补五分钟觉再去……" / "我看看能不能补个觉……" | `operadora_zh_CN.json`, 任命助理 e 编入队伍 | fato (só CN) | — |
| C38 | Dorme em cima da mesa | "可露希尔正趴在桌子上呼呼大睡，身旁还放了个很有她个人风格的小奖杯" | `uniequip_002_closur` (só CN) | fato | — |
| C39 | **Sono picado** (4 h em 4 pedaços; já fazia isso na juventude) | "不就一天睡四个小时还拆成四份睡嘛，这种事我在卡兹戴尔的时候又没少做……" | `story_closur_1_1.txt:338` (só CN) | fato | **sim**: é da fase sem a Kal'tsit (pós-Ep. 15). Num momento chega a "一个半小时" (`:469`) |
| C40 | Hoje a luz do quarto fica mais no modo "trabalho" e no modo "dormir" do que nos modos de jogo | "近些日子她用得最多的样式除了'办公'就是'睡眠'了" | `furni_closureRoom_ceilingLight_01` (só CN) | fato | **sim**: menos lazer depois que o trabalho aumentou |
| C41 | **Foge de trabalho; quer folga**, mas não consegue largar a responsabilidade | "能不工作我当然不想工作啊！可，就只是坐在这里吃巧克力，我会觉得……" / "借着出外勤的机会逃避工作啦" | `story_closur_1_1.txt:846`; `operadora_zh_CN.json`, 干员报到 | fato | a reclamação aumenta depois do Ep. 15 |
| C42 | Conserta o bule elétrico do Doutor, de novo e de novo (piada que se repete) | "绝大多数时间仅用于修理博士的热水壶" / "我都会在工程部等着修你的热水壶的" | `furni_closureRoom_table_01`; `operadora_zh_CN.json`, 信赖提升后交谈3; `story_snsant_1_1.txt:769` (EN) | fato | — |
| C43 | Cobra por tudo (piada de dinheiro) | "该文档为付费内容" / "ZOOT快捷支付消费：180000龙门币" | `operadora_zh_CN.json`, 档案资料一 e 晋升记录 | fato (piada) | — |
| C44 | Quer um quarto **cheio de flor** | "I heard Lena moved her dorm into the Convalescent Garden. Now that makes me jealous! I wanna sleep with flowers and stuff too!" | `loja_en_US.json`, `vitrine` | fato (piada): fala de vendedora | — |
| C45 | Gosta de roupa, ou pelo menos de vender e provar | "Can someone get the lights for me? I'm gonna get changed too." | `loja_en_US.json`, `vitrine` (várias falas) | fato (piada): fala de vendedora; não dá pra separar gosto de propaganda | — |
| C46 | Mania de limpeza: modo de faxina "nível Kal'tsit" | "快速、普通、深度以及名为'凯尔希级'的第四等级，她对此没有进行过说明" | `furni_closureRoom_floor_01` (só CN) | fato | — |

### O que ela não gosta

| # | Não gosta de | Citação original | Fonte exata | Status | Muda depois? |
|---|---|---|---|---|---|
| C47 | A palavra "responsabilidade" (quando brigava com a família) | "和家里人吵架的时候，我其实最讨厌'责任'这种字眼了。" | `story_closur_1_1.txt:808` (só CN) | fato | **sim**: hoje carrega a responsabilidade mesmo assim |
| C48 | Tradição de vampiro e "pureza" | "光是在聊天时回想起血魔那套东西都让她牙酸" | `operadora_zh_CN.json`, 档案资料四 | fato | — |
| C49 | Os próprios pais ("não quer ver nem morta") e o Duq'arael | "死都不要见面的血魔（自己的父母）" | `operadora_zh_CN.json`, 档案资料四 | fato | — |
| C50 | Hora extra sem fim e ter que mandar em tudo | "我真的不想当罗德岛的负责人啊！" | `operadora_zh_CN.json`, 晋升后交谈1 | fato | só depois do Ep. 15 |
| C51 | Sermão na hora da comida | "I'm not here to listen to a sermon during mealtime!" | `level_act7mini_st06.txt:504` | fato | — |
| C52 | Comida natureba (ver C9) | — | — | fato (piada) | — |

**Especulação ou só da wiki:** a Trivia diz que o nome vem da Ada Lovelace (mesmo aniversário, 10/12)
e que o drone se chama Lambda; o drone é "possivelmente" referência ao cálculo lambda. As camisetas
com logo parecido com o do GitHub e o dinossauro do Chrome são observação de fã sobre a arte, e
servem só como pista de estilo (ela gosta de cultura de programador): **inferência**.
([Trivia](https://arknights.wiki.gg/wiki/Closure/Trivia)). Gostos de comida, filme ou música não aparecem na Trivia.

---

## Lacunas: temas comuns de conversa sem resposta oficial

Se alguém perguntar sobre esses temas, o card não deve inventar; a interpretação fica pra depois.

| Tema | Kal'tsit | Closure |
|---|---|---|
| **Anime/desenho** | Nada. O mundo do jogo não tem "anime". | Nada sobre anime. Tem filme ruim/cult, filme B e "soaps"/novelas (C14–C17). Que tipo de série: não diz. |
| **Série/TV** | Nada. | "movies and soaps" (C16). Nenhum título real. |
| **Música** | Tinha um aparelho de música na mesa (K6) e sabe tocar piano (K7). **Que gênero ouve: não diz**. | EDM (D.D.D., C28), sempre de fone (C27), jogo de dança (C30). Banda real: nenhuma. |
| **Comida favorita** | **Nada**. Nenhum prato, doce ou comida. | Lanches: chocolate, chips, fruta seca, biscoito (C4–C7). **Comida de verdade (prato): nada**. |
| **Bebida** | Toma chá quando insistem (K2). Café: nada (K3). Álcool: proibiu no refeitório pelos outros (K8); se ela bebe: nada. | Café (C1) e energético com açúcar (C3). Álcool: nada além de piada de vendedora (C12). Sangue: o canon nega o estereótipo ("só ia sair café"). |
| **Tempo livre** | Quase nada: trabalha, descansa no sofá, pausas com os amigos (K5, K15). Hobby declarado: **nenhum**. Botânica e piano são saber, não hobby confirmado. | Muito: jogar, criar jogo, filme ruim com amigos, speedrun, modificar robô, RPG de mesa (só em fala de venda). |
| **Leitura** | Lê relatório; quer notícias (K12, inferência da Closure). Livro favorito: nada. | Técnica, de várias áreas (C31). Ficção: nada. |
| **Animal de estimação / gato** | Nada (a Mon3tr é parceira, não bicho de estimação). | Nada (os robôs fazem esse papel, C33–C34). |
| **Esporte/exercício** | Nada. | Só o jogo de dança empoeirado (C30). |
| **Clima/estação, cor favorita, cheiro** | Nada. | Nada. |
| **Sono** | Não dorme quando trabalha (K4). Hábito normal de sono: nada. | Coruja e cochilos (C35–C40). |
| **Aniversário** | Clássica: "Undisclosed". Esperanta (só CN): 23/01, data nova. O que ela acha de aniversário: nada além da fala pro Doutor. | 10/12 (arquivo CN). O que ela acha: nada. |

**Para conferir depois de 14/10/2026:** o texto EN oficial das falas de operadora da Closure, do
arquivo dela, do módulo TAC-X e do conjunto de mobília "可露希尔的万能空间", se e quando chegarem
ao global. O EN costuma suavizar (ver C24 e C35).
