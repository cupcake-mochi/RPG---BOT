# Validação do voz.md da Kal'tsit

> 12/10/2026. Pedido do Mizuki: comparar o `voz.md` com exemplos elogiados de fora e com mais
> falas da própria obra, e responder se a quantidade e a qualidade estão boas. Resultado: v1
> tinha um furo grande (registro formal), corrigido na v2.

## Resposta curta

- **Quantidade: boa pra uma ficha-fonte, grande demais pra ir no prompt.** A ficha tem 11 traços,
  6 marcas da Esperanta e ~40 falas citadas. As referências que funcionam põem bem menos no
  prompt: RoleLLM usa descrição + bordões + 5 diálogos buscados; a Anthropic sugere 3 a 5
  exemplos; o guia Ali:Chat pede "minimal" exemplos. Então o `voz.md` não vai inteiro pro bot:
  o card (etapa 3) resume ele em um parágrafo de voz e os exemplos (etapa 4) ficam em 3 a 5.
  A única falta real de quantidade é a Esperanta: 98 falas, só em CN até 14/10.
- **Qualidade: a v1 acertava os números que tinha, mas faltava o traço que mais separa ela do
  elenco.** Faltavam também três coisas que as referências têm e ela não tinha. As quatro
  entraram na v2.

## Com o que comparei

| Referência | Por que vale | O que ela cobre que a v1 não cobria |
| ---------- | ------------ | ----------------------------------- |
| [RoleLLM](https://arxiv.org/html/2310.00746v3) (ACL Findings 2024) | O método de diálogo dele (RoleGPT) ganhou com taxa de vitória de 63,3, contra 29,8 do prompt com poucos exemplos e 9,3 do zero-shot; 84% das respostas da base mostraram o jeito de falar do papel | Campo de **bordões** explícito |
| [ChatHaruhi](https://arxiv.org/pdf/2308.09597) | Ganho em avaliação humana; usa falas reais buscadas | Fala real > descrição (a v1 já seguia) |
| [PersonaGym](https://arxiv.org/html/2407.18416v4) | Benchmark de persona | "Hábitos linguísticos" foi a dimensão mais fraca dos modelos, ou seja, **registro e vocabulário** precisam estar explícitos |
| [Ali:Chat](https://rentry.co/alichat) | Guia de comunidade de referência pra cards (usado na primeira pesquisa) | Poucos exemplos, cada um mostrando traço; **não repetir expressão** (risco de cópia) |
| [Docs do SillyTavern](https://docs.sillytavern.app/usage/core-concepts/characterdesign/) | Documentação oficial | Não define quantidade; exemplos caem quando o contexto enche |
| Os próprios personagens do jogo | Quem conhece a Kal melhor que ninguém | **O que dizem do jeito dela falar** |

Não consegui abrir cards prontos da Kal'tsit: o Chub e o Moegirl recusaram acesso a partir
daqui (bloqueio de rede e robots). Card de fã, além disso, quase sempre sai da wiki e não da
fala, então a comparação com as referências acima é mais forte do que seria com eles. Se você
quiser, abra o chub.ai buscando "Kal'tsit" e me mande o link do card mais favoritado, que eu
comparo também.

## Testes contra mais falas da obra

**1. Ela contra o elenco.** Mesmas medidas em EN pra Amiya, Closure, W, Warfarin, Theresa,
Silence e Ch'en.

| Medida | Kal'tsit | Faixa do resto |
| ------ | -------- | -------------- |
| Palavras de 10+ letras | **4,2%** | 1,5–3,8% |
| Forma sem contração ("I do not") | **5,4%** das falas | 0,9–4,0% |
| Conectivo de concessão e lógica | **3,6%** | 0,7–2,3% |
| Falas com "!" | 2,0% | 0,9 (Theresa) a 22,5% (Closure) |
| Falas com 3 palavras ou menos | 15,6% | 10,4–26,5% |

O registro formal é o que mais separa ela do resto, e a v1 não falava dele. O "fala pouco" da
v1 estava errado no geral: ela é curta pra reagir (26% das respostas), mas não é das mais
curtas do elenco.

**2. Em chinês, pra ver se não é coisa do tradutor.** Conectivos (即使, 无论, 至少, 然而, 因此,
如果, 并非…) aparecem em **8,6%** das falas dela, contra 2,7–5,6% de Theresa, Amiya, Closure,
W, Warfarin, Saria e Ch'en. Ela tem 1,9% de "！" e é a de fala média mais longa depois da
Warfarin. O traço é da personagem, não da Yostar.

**3. Por capítulo, pra ver se o traço é estável.** Dividi o corpus em caps. 0–7, 8–12, 13–15 e
eventos. As medidas ficam na mesma faixa em todos ("!" de 1,6 a 3,0%; palavras longas de 3,3 a
5,0%). A exceção é a pergunta, que cai de 11% pra 6% nos caps. 13–15, que são de crise.

**4. O que os outros dizem dela no jogo.** Procurei falas de outros personagens sobre ela:
- Specter: "Dr. Kal'tsit sure uses a lot of big words, doesn't she?" → confirma o traço 0.
- Priestess: "one of Kal'tsit's rhetorical traps" → confirma os traços 0 e 3.
- Amiya, no cap. 7: "(Dr. Kal'tsit... Show some tact!)" → traço novo, o 10 (franca sem tato).
- Closure: "She'd always work my ass off all day" → exigente.
- Warfarin, no cap. 15: "(Kal'tsit was never so cooperative with exams!)" → bate com o
  arquivo da Esperanta, em que ela "finalmente aceita" o exame.

## O que mudou na v2

1. **Traço 0, registro formal e raciocínio em condição**, com números e a orientação pro pt-BR
   ("português correto sem virar livro").
2. **Traço 1 corrigido**: curta pra reagir, longa pra explicar.
3. **Traço 10, franca sem tato.**
4. **Tabela por interlocutor** (Doutor, Amiya, Closure, Warfarin, Mon3tr, W): os guias de card
   tratam a relação como parte da voz.
5. **Bordão: não tem, e isso é regra.** Responde o campo do RoleLLM sem inventar marca.
6. **"O que os outros dizem dela"**, pra servir de conferência no teste.

## O que ainda falta

- **Sua leitura** dos traços 4, 7 e 10, que saíram de amostra pequena.
- **Faixa emocional**: como ela fala com raiva, medo e luto (cap. 15, Theresa). Hoje a ficha cobre
  o tom calmo; os exemplos da etapa 4 precisam de pelo menos um momento sério.
- **Separar ela da Theresa** no teste com nome trocado: as duas quase não exclamam. O que separa
  são os conectivos (3,6% contra 1,7%) e a pergunta (10% contra 18%).
- **Esperanta em EN**, a partir de 14/10.

## Comparação com o card do Chub (Goldenglow/Kaltsit)

> Mandado pelo Mizuki em 12/10/2026, salvo em `referencias/cards/chub_Goldenglow_Kaltsit.json`.
> Character Card V2, id 700 no Chub (dos primeiros do site). Número de favoritos não veio no arquivo.

| Ponto | Card do Chub | Nossa ficha |
| ----- | ------------ | ----------- |
| De onde sai a voz | Adjetivos ("calm, reserved, intelligent, calculating") | Contagem do corpus + fala real citada |
| Fala real do jogo | Nenhuma | ~40 citadas |
| Exemplos de diálogo | 1, inventado: 65 palavras de fala e 103 de ação entre asteriscos | 3 a 5 previstos, transcritos de fala real, no tamanho de Discord |
| Registro formal (traço 0) | Não aparece; o exemplo usa "Hmmm. Interesting." e "Is this okay with you?" | Traço principal |
| Bordão | Abre o exemplo com "Hmmm", que ela usa em 0,3% das falas | Regra: não tem bordão |
| Relações | Só Mon3tr, como "pet... totally tame" | Doutor, Amiya, Closure, Warfarin, Mon3tr, W |
| Aparência | ~metade da descrição (cabelo, roupa, "110 lbs", "5'8") | Fica de fora: não ajuda a voz num chat de texto |
| Lore | "tall human woman" (a ficha diz Feline, e ela é AMa-10); "over 10,000 years... may be immortal" (era verdade até o Ep. 15) | Canon com fonte e corte de tempo, até a Esperanta |
| Instrução de formato | "Describe Kal'tsit's actions in detail", "can talk a lot and be very verbose" | Uma ou duas frases no chat; longo só pra explicar |

**Leitura:** o card é exatamente o que as pesquisas previam pra card de fã. A voz vem de
adjetivo, o exemplo é narração inventada e o lore é de memória e está desatualizado. Com esse
card, o modelo ia escrever cenas longas de roleplay com ação entre asteriscos, o contrário do
que um bot de Discord precisa. A comparação reforça o método, e não muda a ficha.

**O que vale aproveitar:** a ideia do `scenario` no consultório médico (bate com a Esperanta,
que agora fica no Médico) e a frase "all decisions... whichever is the lesser evil", que tem
apoio no corpus ("Some countries don't even care about the truth...") e pode entrar no card
depois de conferida.
