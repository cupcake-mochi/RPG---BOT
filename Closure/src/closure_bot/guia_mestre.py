"""Roteiro humano de revisão, complementar à análise determinística."""

MESTRE = ("Revisar uma ficha como mestre", (
    ("1. Combine o que será revisado",
     "Este roteiro ajuda o mestre a revisar a ficha inteira, usando o painel do bot como apoio. "
     "Abra por **GC:guia mestre** ou **/ficha mestre**. Ele não analisa um arquivo nem concede aprovações.\n\n"
     "Peça ao jogador o link ou o arquivo Excel (.xlsx) da ficha atual. Confirme campanha, edição do livro, nível inicial, Grau, recursos e opções permitidas. "
     "Se houver regras próprias, compare **CONFIGURAÇÃO → REGRAS DE CAMPANHA** com o que a mesa autorizou.\n\n"
     "Use `GC:guia criar` para acompanhar o preenchimento e `GC:guia planilha` para localizar abas e configurações. "
     "Faça a revisão pela versão atual: um painel antigo não acompanha as edições do jogador."),
    ("2. Rode a análise e separe os resultados",
     "Use **/ficha analisar** com o link ou arquivo Excel (.xlsx). Pelo chat, escreva `GC:ficha LINK_DA_FICHA` "
     "ou anexe o XLSX à mensagem de `GC:ficha`. "
     "Envie uma fonte por análise. Por link, o bot precisa ter acesso de leitura; o painel aparece no canal.\n\n"
     "Leia **Resumo**, **Correções e revisão** e **Limites da análise**. Vermelho indica erro naquela página; "
     "amarelo indica pendência, revisão ou limite; verde vale apenas para as verificações mostradas. "
     "O rodapé informa o resultado geral.\n\n"
     "Separe o que exige corrigir uma entrada, completar informação, comprovar uma fonte ou decidir como mestre. "
     "Peça uma análise nova depois das correções. As setas só navegam pelo resultado já calculado.\n\n"
     "**Zero erros não é aprovação integral.** VÁLIDO no cartão descreve a conta da planilha; "
     "não comprova que o personagem adquiriu ou pode usar aquela capacidade."),
    ("3. Confira criação, treinos e progressão",
     "Compare os atributos base e seus limites com a criação acordada. Confira Origem, traço, marcante e menores elegíveis, "
     "Caminho e Trilha compatíveis. Legados de história não concedem bônus nem substituem capacidades.\n\n"
     "Confira de onde veio cada perícia, ofício, treino em arma e Teste de Resistência (TR). Verifique trocas, escolhas repetidas e o atributo fixo "
     "do TR Físico. Não cobre de novo uma escolha recebida gratuitamente, nem conte duas vezes o mesmo treino.\n\n"
     "Para progressão, peça os registros de missões, pontos de experiência (XP), marcos de Corpo/Refino/Leque, rolagens de vida autorizadas, "
     "trocas e aprendizados. Confira ordem de aquisição, requisitos de nível e eventuais feitos de Limiar.\n\n"
     "Um total que fecha hoje não comprova esse histórico. "
     "Se faltar evidência, registre a dúvida e combine como resolvê-la antes de liberar a parte afetada."),
    ("4. Leia cada habilidade junto da montagem",
     "Na **FICHA AMALDIÇOADA**, compare o Fundamento, Manejos ou Katas com a rota permitida pela Origem. "
     "Confira atributo, Famílias, tipos de dano, Selo, Expressão e requisitos das peças.\n\n"
     "Para cada cartão, leia **COMO É** ao lado da montagem. Defina alvo, forma de acertar ou resistir, alcance, duração, "
     "frequência, condição de encerramento e o que precisa continuar verdadeiro para o efeito funcionar. "
     "Uma Restrição precisa limitar o uso de verdade, na cena.\n\n"
     "Confira função, Classe, pontos, dados, PE, Melhorias e Restrições e suas dependências. "
     "Aprovar uma versão não libera automaticamente qualquer versão ampliada ou interpretação futura. "
     "Espere a troca de Classe terminar antes de avaliar os campos.\n\n"
     "Revise separadamente efeitos narrativos, distribuição entre alvos e interações de Alma que o bot não conferiu. "
     "Não deduza uma entrada ausente do resultado que deseja validar."),
    ("5. Confira espaços, entidades e efeitos ativos",
     "Revise o orçamento de espaços e a origem de cada aquisição: feitiços, Talentos pagos, benefícios gratuitos, "
     "Classe 0, Domínio e entidades usam contagens e posições próprias. "
     "Confira também acesso a Aptidões, Refino/Lapidação, Liberação e Técnica Máxima.\n\n"
     "Em **INVOCAÇÕES**, confira tipo, aquisição, nível, Classe, atributos, Famílias, treinos, Talentos e cartões próprios. "
     "O nível atual do personagem não substitui a progressão de uma domada.\n\n"
     "Combine quais entidades estão realmente ativas, limites simultâneos, comandos, manutenção e recursos compartilhados. "
     "A lista de entidades conhecidas não comprova esse estado de cena.\n\n"
     "Para pactos e efeitos temporários, verifique condição, custo, duração e fonte. "
     "Em BÔNUS E MUDANÇAS, confira Somar/Trocar por, conflitos e se a mesma fonte também entrou no Buff/Debuff."),
    ("6. Revise regras e opções próprias",
     "Peça a definição completa: nome, base do livro, campos alterados, requisitos, efeito, frequência e limites. "
     "Confira todas as dependências, incluindo Família e Restrição próprias usadas por uma Forma.\n\n"
     "**MESTRE VIU é um lembrete do jogador**, não uma aprovação registrada no bot. "
     "Hoje, o responsável pelo bot cadastra a decisão combinada com o mestre para a **definição exata e o servidor correto**. "
     "Não há comando de jogador para aprovar a própria criação.\n\n"
     "Se base, atributo, custo ou funcionamento mudarem, confira se a definição precisa de uma aprovação nova. "
     "Uma aprovação antiga com o mesmo nome não basta. `GC:guia custom` aprofunda esse processo.\n\n"
     "Aprovação não transforma prosa em bônus. Use campos estruturados para números e comprove sua fonte. "
     "Uma peça própria pode continuar **sem recálculo independente**, mesmo aprovada; "
     "nesse caso, a conta e o funcionamento ainda precisam da conferência humana indicada no painel."),
    ("7. Confira equipamento, recursos e registros",
     "Na **FICHA PESSOAL**, compare inventário, quantidades, munição, Volume e o que está em uso. Confira "
     "treino, Força, mãos, acesso e dinheiro das compras. Ter o item não dispensa seus requisitos.\n\n"
     "Na **FICHA**, confira recursos máximos e atuais, Defesa, Proteção, deslocamento e estados. Uma ficha que "
     "começa ferida ou com Sequelas precisa refletir a situação combinada. Evite substituir fórmulas por "
     "valores que só escondam o problema.\n\n"
     "Confira datas e participações das missões e os acordos salariais quando a mesa usar esse controle. "
     "Confira o saldo em **TOTAL DISPONÍVEL (W86)** e os lançamentos no EXTRATO. **O86 é ± GASTO / GANHO**, não "
     "saldo manual; não lance salários de novo. Os últimos 10 créditos estão em CONFIGURAÇÃO!K81:P90. A análise "
     "do bot não certifica datas de missão nem o histórico salarial.\n\n"
     "Use **Limites da análise** como lista adicional: o que está ausente ou não conferido não vira válido por "
     "suposição."),
    ("8. Registre a decisão e finalize a revisão",
     "Para cada dúvida, anote **o que foi conferido, a fonte ou decisão, a condição de uso e o que ainda "
     "falta**. Separe erro de conta, informação faltante e decisão de mesa. Não conceda um bônus só para fazer "
     "o painel ficar verde.\n\n"
     "Depois das correções, analise novamente a mesma versão e confira se a mudança resolveu o problema sem "
     "criar outro. As partes sem conferência automática continuam exigindo sua revisão, mesmo com zero erros e "
     "pendências.\n\n"
     "Diga ao jogador o que está liberado, o que depende de ajuste e quais limites valem durante a sessão. Se a "
     "ficha estiver pronta para a mesa, conclua a criação marcando **EMITIR**, ao lado de Não emitida, na "
     "CARTEIRA. O campo grava a data e se desmarca ao salvar; ele não registra sua decisão no bot.\n\n"
     "O salário só conta depois de emitir. Marcar EMITIR de novo não muda a data. A correção em "
     "CONFIGURAÇÃO!O38 só aceita da emissão atual até hoje (sem emissão, só hoje), preserva salários vencidos e "
     "reinicia o ciclo aberto. Guarde os acordos de mesa fora do painel temporário e reveja a autorização "
     "quando a definição mudar."),
))
