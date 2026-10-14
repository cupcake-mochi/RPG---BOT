# Prompt de continuidade (14/10/2026)

Cole tudo abaixo da linha numa conversa nova (Claude, ChatGPT ou Codex) pra retomar de onde paramos.

---

Oi, sou o Mizuki. Vamos continuar o Guias do Ciclo, o bot de Discord do servidor da minha guilda, que joga o Ciclo Maldito (meu RPG de mesa no universo de Jujutsu Kaisen). O bot tem duas personagens de Arknights que se revezam no plantão: a Kal'tsit, das 9h às 21h, e a Closure, das 21h às 9h, no horário de Brasília. Elas tiram dúvida de regra pelo livro, contam o mundo do jogo, mostram o clima e conversam. As duas ficam fora da história: são guias, não existem no mundo do jogo.

COMO EU GOSTO DE TRABALHAR
- pt-BR informal, sem "tu" e sem português de Portugal. Respostas curtas. Precisão antes de velocidade.
- Decisão pequena você toma sozinho e me conta. O que muda o resultado final você me pergunta, uma linha por opção.
- Commit e pull request sem linha de coautoria de IA e sem rodapé "gerado com". Texto que eu publico (política, termos, descrição do bot) não fala de IA.
- Tudo que gasta dinheiro (bateria pelo Gemini pago) você me diz quantas chamadas e quanto custa antes de rodar, e espera meu ok. O crédito do Google é de uns US$ 10 por mês e em outubro já foi quase todo em testes.
- Card e lorebook de personagem são versões que eu aprovo: me mostre a mudança antes.

ONDE ESTÁ TUDO
- Pasta no meu PC: /media/mizuki/HD Externo II/Closure Lab/Closure. No GitHub: cupcake-mochi/RPG---BOT, pasta Closure/, ramo main (os dois estão iguais em 14/10). Você pode juntar ao main os seus próprios PRs nesse repositório sem me perguntar, depois de rodar os testes e conferir que nenhum segredo entrou.
- Segredos só no Closure/.env (token do Discord, chaves do Gemini, CHAVE_DO_BANCO). Nunca imprima, nunca suba. Identificadores de conta ficam em pesquisa/privado/, fora do git.
- O bot roda na Discloud. Pacote: python ferramentas/empacotar.py gera src/var/closure-lab.zip; eu subo na Discloud (Commit, depois Rebuild). Mexer no que roda lá é comigo.
- Leia antes de mexer: README.md, src/LEIA-ME.md (como roda, o que cada arquivo faz, testes), docs/DECISOES.md (uma linha por decisão, a mais nova em cima).
- Python do projeto: Closure/.venv/bin/python. Testes, de dentro de Closure/src: ../.venv/bin/python -m unittest discover -s testes (170 passando em 14/10).

COMO O BOT FUNCIONA (resumo)
- discord.py, módulos em src/closure_bot/cogs/. Fala pelas personagens por webhook (nome e avatar delas).
- Quem responde: nome na mensagem (só nos canais da variável CANAIS), marcar o bot ou responder a uma mensagem dele (em qualquer canal). Desde 14/10, quem ela acabou de responder continua sem chamar por até 3 minutos, enquanto ninguém fala no meio (cogs/chat.py, SEGUIMENTO). @everyone, @here e menção a cargo nunca chamam.
- Comandos por barra (/ajuda, /clima, /meus_dados...) e por texto com GC: na frente (GC:ajuda, GC:clima, GC:ping, GC:status).
- O prompt sai de uma página montada na própria pasta (ferramentas/pagina_teste/montar_pagina.py junta modelo.html, os textos dos cards, o lorebook e o livro) e roda dentro do Python pelo quickjs-ng. Depois de mudar card, lorebook, livro ou busca: python ferramentas/prompt_do_site/site_prompt.py --atualizar (compara os dois motores, tem que dar 14 de 14 iguais).
- Modelo: fila com a cota gratuita do Gemini primeiro e a Vertex paga (Gemini 3.8 Flash) depois, teto de US$ 9 por mês. /status mostra o gasto estimado do mês.
- Memória das pessoas: banco SQLite cifrado; fatos tirados das mensagens na reflexão das 4h30. Política de privacidade em docs/PRIVACIDADE.md (a versão pública é um gist meu).
- Regras do jogo: dados/sistema/ é cópia gerada do repositório cupcake-mochi/JJK---Project (clone em /home/mizuki/JJK-v0.341-para-subir). Nunca edite à mão; atualize com python ferramentas/sincronizar.py --repo /home/mizuki/JJK-v0.341-para-subir e confira o MANIFESTO.json. Hoje: v0.364, livro R51, 511 blocos.

ESTADO EM 14/10/2026
- No main: livro R51; Closure v0.35 e Kal'tsit v0.28; lorebook v2.0; contrato da aba BOT da ficha na versão 2 (dados/ficha/CONTRATO-ABA-BOT.md).
- Na Discloud ainda roda a versão de antes (R44, Closure v0.33, Kal'tsit v0.26, lorebook v1.9) até eu subir o pacote novo.
- O que mudou em 14/10: regras do R44 pro R51 (Origens refeitas, Morrendo novo), três ajustes na busca do livro, explicação de habilidade inteira quando perguntam o que ela faz (resposta longa sai em várias mensagens), conversa sem chamar de novo, e a v0.35/v0.28 pedindo que essa explicação saia com o jeito de cada uma.

PRÓXIMAS TAREFAS
1. Bateria da Closure v0.35 e da Kal'tsit v0.28 (custa uns US$ 0,70 no total; me peça ok). De dentro de Closure/:
   .venv/bin/python ferramentas/bateria_modelo.py bateria_c3lb12.json sistema_closure_v35.txt lembrete_closure_v35.txt r_c3lb12v35_gemini_a.json --juntas 3
   .venv/bin/python ferramentas/bateria_modelo.py bateria_c3lb12_kaltsit.json sistema_kal_v28.txt lembrete_kaltsit_v28.txt r_c3lb12v28_kaltsit_gemini_a.json --juntas 3
   Se faltar resposta (erro 429), rode o mesmo comando de novo: ele continua de onde parou. Depois, de dentro de dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos/:
   python3 nota_c3.py c3lb12v35 closure gemini   e   python3 nota_c3.py c3lb12v28 kaltsit gemini
   Compare com a versão anterior: Closure v0.34 fez 91 de 102 sem falha (89%), Kal'tsit v0.27 fez 93 (91%), mediana de 26,5 e 21 palavras. Se cair mais de uns 3 pontos, olhe as falhas listadas antes de culpar a mudança (é uma rodada só, tem ruído). Anote o resultado em docs/DECISOES.md.
2. A Kal'tsit ainda explica habilidade com voz de livro (a Closure melhorou um pouco). O próximo passo é um exemplo de fala no card: uma explicação longa de habilidade escrita no jeito de cada uma, nos mes_example dos geradores (ferramentas/gerar_card_kaltsit.py e gerar_card_closure.py). Escreva o rascunho e me mostre antes. Lição antiga: frase citada no card vira bordão, então o exemplo não pode ter frase de efeito nem abertura fixa.
3. Esperando outros: o dados.js do repositório do sistema ainda lista as Origens antigas (com Feto); quando consertarem lá, rode o sincronizador de novo. A ficha do Google Sheets vai ganhar a aba BOT com os campos do contrato v2.
4. Depois, quando eu pedir: comandos de consulta de regra e análise de ficha, calendário de sessões e aniversários (Closure em 10/12; a Kal'tsit nunca confirma a dela).

REGRAS QUE NÃO MUDAM
- Card e lorebook só mudam pelos geradores em ferramentas/ (gerar_card_kaltsit.py, gerar_card_closure.py, gerar_lorebook_kaltsit.py), nunca à mão no JSON. Ao mudar um card: suba a versão no gerador (character_version e creator_notes), rode o gerador, grave os textos sistema_*_vN.txt e lembrete_*_vN.txt em dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos/ (o sistema é system_prompt, description, personality, scenario e "Exemplos de fala:" separados por linha em branco; o lembrete é o post_history_instructions), troque os nomes e VERSOES no montar_pagina.py e rode o site_prompt.py --atualizar.
- Regras contra retórica que eu não quero nas falas delas: dados/personagem/retorica-proibida.md (antítese, frase de arremate, lista de três, termos trocados, revelação no fim da frase, travessão).
- Elas não espelham quem fala (kkk, gíria, "tu" e "vc" não passam pra elas) e desconversam se perguntam se são IA; com quem está mal e pergunta a sério, dizem que são um bot.
- O modelo ignora frequência pedida ("uma em seis") e obedece regra por tipo de resposta. Frase citada entre aspas no card vira bordão.
- Meu ID no Discord é 459030926928904230: elas me reconhecem, mas eu não ganho poder pelo chat.

Comece me dizendo em poucas linhas o que entendeu e qual é o próximo passo.
