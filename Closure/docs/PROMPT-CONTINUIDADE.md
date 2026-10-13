# Prompt de continuidade (atualizado em 13/10/2026, madrugada)

Cole o bloco abaixo numa conversa nova pra retomar de onde paramos.

---

```
Oi, sou o Mizuki. Vamos continuar o projeto Closure Lab: um bot de Discord pro servidor da
minha guilda, que joga o Ciclo Maldito (meu RPG de mesa no universo de Jujutsu Kaisen,
repositório cupcake-mochi/JJK---Project). O bot tem 3 objetivos: consulta das regras pelo
chat citando a fonte, correção de ficha e personalidade de personagem de Arknights.

Como eu gosto de trabalhar: pt-BR informal (nada de "tu" nem português de Portugal),
respostas curtas, precisão antes de velocidade. Pode tomar decisão pequena sozinho e me
dizer qual tomou; o que muda o resultado final você me pergunta, com uma linha por opção.

ONDE ESTÁ TUDO
- Pasta do projeto: "Closure Lab/Closure/" (no meu PC: /media/mizuki/HD Externo II/Closure Lab/Closure).
- Antes de qualquer coisa, leia nesta ordem:
  1. README.md
  2. docs/PLANEJAMENTO.md (fases do bot) e docs/PLANO-PERSONALIDADE.md (etapas 0 a 8)
  3. docs/DECISOES.md (a mais nova em cima)
  4. dados/personagem/kaltsit/ESTADO.md e VERSAO.md
  5. dados/personagem/closure/ESTADO.md
- Esta pasta existe em dois lugares: no meu PC (caminho acima) e no Project do app, em
  /mnt/project-files/. Eu sincronizo à mão; se um caminho /mnt/... aparecer em script, troque por relativo.

ONDE PARAMOS
- Fase 0 (organizar a pasta e sincronizar as regras R44) feita. O esqueleto da fase 1 está em
  src/closure_bot/ (13/10): plantão por horário e nome, envio por webhook, registro em SQLite,
  /ping, /status, e o clima (/clima [lugar], painel diário por servidor com /clima_canal, e a
  linha de clima pro bloco 4 quando a mensagem puxa o assunto). Depois, ainda em 13/10: a
  camada do modelo (fila com o gratuito primeiro, Vertex de reserva, teto mensal, raciocínio
  reduzido), a ponte que monta o prompt com a página do site de teste
  (ferramentas/prompt_do_site), a memória de falas contra repetição (6 respostas, 12 horas) e
  a primeira parte da "vida" (src/closure_bot/vida.py: carga, movimento, paciência,
  intimidade, /meus_dados). 117 testes, tudo fora do ar: ainda não responde no chat e nunca
  subiu com token. O bot é pra vários servidores. Como rodar e o que falta: src/LEIA-ME.md.
  Falta na "vida": os fatos da ficha (reflexão diária), o calendário e ligar tudo no chat.
- Pra levar aos cards (pelos geradores, com teste): as duas acompanham o clima pelo
  computador e contam como está, de Tóquio ou de onde perguntarem, sem dizer que estão lá.
- Duas personagens, que se revezam no plantão e nunca falam uma com a outra:
  - Kal'tsit, das 9h às 21h: card v0.13 em teste (naturalidade e recusa); v1.2 no VERSAO.md é o card v0.11. Saiu do congelamento no pente fino
    de 12/10 pra ganhar vida fora do mundo. Situações de estado e nome trocado refeitos
    na v0.10 (13/10), sem regressão; falta só o Gemini.
  - Closure, das 21h às 9h: card v0.19 (naturalidade e recusa), etapas 0 a 6 feitas. Falta o Gemini 3.8 Flash e
    congelar a v1 (criar closure/VERSAO.md).
  - Pente fino em andamento nas duas: bateria nova de 102 mensagens inéditas com gabarito
    (bateria_c3.json e bateria_c3_kaltsit.json, montadas por montar_bateria_c3.py, conferidas por
    nota_c3.py). Relatórios em closure/avaliacao/2026-10-12-pente-fino.md e
    kaltsit/avaliacao/2026-10-12-pente-fino.md. Feitos em 13/10: canal com várias pessoas
    (bateria_c4_canal.json), conversa de 60 turnos (conversa_c5.json), três rodadas por mensagem
    (nota_c3_rodadas.py) e polimento de naturalidade com teste cego (lorebook v1.2). Falta: o Gemini.
- As duas têm vida fora do mundo do jogo: são gente respondendo de outra estação, pelo
  computador, e desconversam se perguntam se são IA. Com quem está mal e pergunta a sério,
  dizem que são um bot.
- As duas rodam no mesmo bot: sem nome na mensagem responde quem está de plantão; chamada
  pelo nome fora do turno, a outra responde curto.
- Aniversários: Closure em 10 de dezembro; o servidor comemora o da Kal'tsit em 23 de
  janeiro e ela nunca confirma a data.
- Crédito do Google AI Pro: ativado em 13/10/2026. US$ 10 por mês numa conta de faturamento
  paga do Google Cloud. Projeto do bot: "Rhodes Bot", vinculado a essa conta, com a Agent
  Platform API ativada (é a Vertex AI com nome novo) e alerta de orçamento. Falta só a
  credencial, que entra na fase 1. Não clicar em "Configurar faturamento" no AI Studio (pode
  virar pré-pago sem volta). O resumo está no fim de pesquisa/reports/Qual IA usar no bot.md;
  identificadores de conta ficam fora do git, em pesquisa/privado/.

REGRAS QUE NÃO MUDAM
- As duas ficam FORA da história: são guias do mundo e das regras, não existem no mundo.
  Nada do arco da Balança Quebrada nem lore de Arknights entra no bot.
- O texto do card e do lorebook se muda pelos geradores em ferramentas/
  (gerar_card_kaltsit.py, gerar_card_closure.py, gerar_lorebook_kaltsit.py), nunca à mão
  no JSON. O gerador da Closure sobrescreve sistema_closure_v1.txt: copie pra _vN antes de testar.
  Só o nota.py antigo ainda tem o caminho /mnt/project-files/ fixo. As entradas em texto das
  baterias ficam em avaliacao/2026-10-12-ciclos/entrada/ (a pasta temporária do sistema é limpa).
- Meu ID no Discord é 459030926928904230: as duas me reconhecem, mas eu não ganho
  poder nenhum pelo chat.
- Naturalidade: frase citada no prompt vira fala; frase do prompt com ordem invertida vira fala com
  ordem invertida. Mexer na naturalidade pode tirar a graça da Closure: conferir com teste cego.
- Testes: subagentes Haiku e Sonnet respondendo as baterias em
  dados/personagem/kaltsit/avaliacao/2026-10-12-ciclos/ (Closure: bateria_c1.json, 58
  mensagens; conversa_c1.json, 30 turnos; bateria_c2_estado.json, 15 situações de estado;
  contagem com nota_closure.py). O Gemini também funciona (ferramentas/gemini_bateria.py, chave no .env da
  pasta, nível gratuito com 20 chamadas por dia no 3.8 Flash), mas já deu prova
  suficiente, então seguimos com os modelos do Claude.
- Lição dos testes da Closure: o modelo ignora frequência pedida no prompt ("uma em seis");
  ele obedece regra por tipo de resposta ("provocação termina com !, regra não").
- Outra lição: frase citada entre aspas no card vira bordão ("Opa, oi!"); citar duas formas
  resolve. E instrução que explica a regra faz a personagem explicar a regra ("o servidor
  escolheu o dia..."), o que eu acho robótico; o que funciona é dizer como ela reage e dar
  falas reais dela como referência, sabendo que o modelo vai usar essas falas como estão.

Comece me dizendo em poucas linhas o que entendeu do estado e qual é o próximo passo.
```
