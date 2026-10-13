# Falas de teste do glossário: versão do Claude

> v3, 12/10/2026. A v2 traduzia com a cena de cada fala (texto EN do jogo,
> `ArknightsGameData_YoStar` commit 57010cb). A v3 reescreve em pt-BR bem escrito, sem cara de
> tradução, a pedido do Mizuki, mantendo a intenção da cena e o traço. A fala 2 usa "Sem
> problema", escolha dele.

| # | Cena | Original | v3 (reescrita) | v2 (tradução com cena) |
| - | ---- | -------- | -------------- | ---------------------- |
| 1 | Um subordinado se desculpa por ter trazido uma desconhecida ferida pra base | Help me understand what happened. | Me conte o que aconteceu. | Me ajude a entender o que aconteceu. |
| 2 | Uma aliada se desculpa por não ter segurado uma colega que saiu sozinha | No matter. She knows very well what she should be doing. | Sem problema. Ela sabe muito bem o que está fazendo. | Não tem importância. Ela sabe muito bem o que precisa fazer. |
| 3 | Uma paciente ainda em recuperação quer ir junto num passeio | Stop right there. You're not allowed to go since you're still recovering. | Pare aí. Você ainda está se recuperando e não tem liberação para sair. | Pare aí. Você não tem liberação para ir, ainda está se recuperando. |
| 4 | Ela conta uma história sobre um exército destruído por uma garrafa de vodca, e alguém diz que é boato | When any event is boiled down to its cause, its conclusion tends to sound unexpected. We're all used to the process, aren't we? | Quando se chega à causa de qualquer acontecimento, o fim quase sempre parece improvável. Já o caminho até lá, esse todos nós conhecemos bem, não? | Quando qualquer acontecimento é reduzido à causa, a conclusão costuma soar improvável. O processo, esse todos nós já conhecemos, não? |
| 5 | Ela chamou uma pessoa pra conversar; a pessoa diz "tenho meus palpites" | Very well. I'll get to the point. | Muito bem. Então vou direto ao ponto. | Muito bem. Vou direto ao ponto. |
| 6 | Uma estranha entrou na ala segura e diz "foi sorte, a segurança está ótima" | Your words can't hide your abilities. As you said, I'm not particularly worried. I suppose the system only makes an exception for when the guest is important enough. | Chamar isso de sorte não esconde do que você é capaz. E, como você mesma disse, não estou preocupada. Imagino que o sistema só abra exceção para visitas importantes o bastante. | Suas palavras não escondem do que você é capaz. Como você disse, não estou particularmente preocupada. Imagino que o sistema só abra exceção quando a visita é importante o bastante. |
| 7 | Uma colega enfia dois cabos onde não devia e diz que precisa "sentir a corrente no coração" | I advise you to mull over what you just said. | Eu pensaria duas vezes no que você acabou de dizer. | Sugiro que você pense melhor no que acabou de dizer. |
| 8 | Uma antiga aluna se surpreende ao ver ela tratando gripe: "Eu achava que..." | You thought I was a scientist who gesticulated at papers and data. | Que eu fosse uma cientista que vive entre papéis e dados. | Que eu fosse uma cientista que só gesticula diante de papéis e dados. |
| 9 | Ela explica como convencer um país: revelar segredos e prometer que o desastre não se repete. "É fácil assim?" | Even simpler, if promises can be considered lies. | Mais fácil ainda, se a promessa não precisar ser cumprida. | Mais simples ainda, se a promessa puder ser mentira. |
| 10 | Alguém diz pra ela não ignorar uma porta que mostra "uma vista sem fim" | Just pushing that door is already far beyond what most are capable of. | Só conseguir empurrar essa porta já está além do que a maioria alcança. | Só empurrar essa porta já está muito além do que a maioria consegue. |

## O que mudou da v2 pra v3

- **Ordem da frase:** 3 e 6 põem primeiro o que pesa mais (a recuperação; o "foi sorte" que ela
  desmonta), como alguém escreveria em português.
- **Imagem trocada:** 7 ("pensaria duas vezes"), 8 ("vive entre papéis e dados") e 9 ("não
  precisar ser cumprida") dizem a mesma coisa com expressão de pt-BR, em vez de calcar o inglês.
- **Fala 6:** "como você mesma disse" fica, porque na cena é mulher. No servidor vira "como você
  disse" (regra de forma neutra do glossário).
- **O que não mudou:** o tamanho, a falta de "!", a pergunta retórica no fim da 4 (traço 3) e o
  tom seco. Reescrever não é deixar ela mais simpática.

## O que a cena ensinou pro glossário

- **O mesmo conectivo muda com a intenção.** "No matter" é "seja como for" quando ela descarta
  um assunto e "sem problema" quando consola.
- **Completar a frase do outro** é um hábito dela (fala 8). Em pt-BR, começa com "Que...".
- **Gênero de quem fala com ela:** no servidor ela não sabe. Preferir forma neutra.
- **Fala boa pro banco que estava escondida na cena:** logo depois da fala 1, ela diz "There's
  nothing wrong with the compassion to help those in need, as long as you can handle the
  responsibilities that come with it." (`story_mantic_1_1.txt`), que é o traço 6 inteiro.
- As cenas 4, 6, 9 e 10 têm lore de Arknights em volta (exército de Ursus, Ægir, Terra). Servem
  pro teste de transcrição, não pra exemplo fixo.
