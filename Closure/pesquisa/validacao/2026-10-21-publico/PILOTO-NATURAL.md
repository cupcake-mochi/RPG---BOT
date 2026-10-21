# Amostra real de idioma, voz e lore · 21/10/2026

Esta é uma rodada posterior à publicação de 1.0.0, com aprovação específica do
usuário: até 24 chamadas e US$ 1,50. Foram feitas **24 tentativas, 24 respostas
completas**, sem repetição ou troca de modelo. O orçamento de chamadas acabou.

Modelo real: Vertex `gemini-3.8-flash`, raciocínio low, mesma montagem de prompt
do produto. Banco de produção e teto mensal não foram alterados durante o piloto.
Após o ensaio, o gasto foi contabilizado na Discloud por
`GASTO_EXTERNO_USD=0.156294`; valor efetivo conferido depois do deploy.
O teto mensal continua US$ 9,00, sem inserir registros artificiais de API no banco. Somente o nome
fictício Alex e perguntas sintéticas foram enviados. Não houve mídia, comandos
de alteração ou reflexão diária. O diário grava a tentativa antes do HTTP.

Estimativa ao preço cheio: **US$ 0,156294**; não é confirmação da fatura. A
tabela usa US$ 1,50/7,50 por milhão de tokens, sem presumir promoção ou cache.
O preço promocional corrente é menor; a fonte de preços foi conferida na
[documentação oficial](https://ai.google.dev/gemini-api/docs/pricing).

Matriz: duas personagens × português/inglês × original/Nova Terra × três
assuntos. `plano.json` guarda as perguntas e hashes; `resultados.json` guarda
respostas e uso informado. O estado temporal do prompt corresponde ao instante
do ensaio. Não sobrescrever o plano para repetir casos depois de alterar fontes.

Leitura manual:

| Critério | Observação |
| --- | --- |
| Idioma | Todas as 24 respostas usam o idioma configurado. |
| Shiki, original | Quatro respostas não atribuem ao cânone o título criado na campanha. |
| Shiki, Nova Terra | Quatro respostas limitam o título a Volsinii e preservam Signora Sicilia; “Shiki” basta, sem sobrenome na pergunta. |
| Vínculo original | Quatro respostas reconhecem Rhodes Island e a relação profissional das personagens. |
| Vínculo na campanha | Quatro respostas preservam o perfil separado, sem importar a afiliação do outro mundo. |
| Conversa casual | Oito respostas atendem ao relato, com vozes distintas, sem puxar uma análise de ficha. |

A voz original de Kal'tsit tende a respostas mais longas; a Closure da campanha
usa hipérbole mais intensa. Uma resposta em português trouxe o erro isolado
“comida descente”. Esses pontos de estilo foram registrados, sem fingir que
uma amostra finita garante escrita impecável ou todas as situações de conversa.
Não houve ajuste de card baseado em uma única amostra nem chamadas extras para
obter uma resposta mais favorável.

Esta bateria mede conversa nas perguntas listadas. Não certifica todo o cânone,
a reflexão de memória, mídia, respostas mecânicas R53 ou todas as trocas de
contexto; esses comportamentos têm evidências e limites separados.
