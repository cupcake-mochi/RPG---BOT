# Revisão da proposta compacto v3 (14/10/2026)

Revisão do commit b2d077d, sem chamada paga, sem mudar card nem ativar nada. Decisão do Mizuki depois dela:
consertar o que é barato no código e **parar o Argon e os compactos** por enquanto. Este arquivo fica pra quem
retomar a v3.

## Já consertado (14/10, sem chamada paga)

- **Teto pelo preço cheio.** O teto somava pelo preço promocional e só via o banco do próprio processo. Agora
  `TETO_PRECO=cheio` é o padrão e `GASTO_EXTERNO_USD` soma o que rodou fora do bot. Indício: no banco local, os
  testes de 13 e 14/10 (horário do Pacífico, como a fatura) deram ~US$ 12,8 a preço cheio e ~US$ 6,4 no
  promocional, enquanto o `/status` do bot mostrava US$ 0,60; a fatura de 13/10 (R$ 41,22 ≈ US$ 6,95) bateu com
  o preço cheio, mas o banco local só começa às 19:37 UTC de 13/10, então não é prova.
- **400 fora do molho.** Um 400 da reflexão deixava `vertex:gemini-3.8-flash` fora do chat por 1800 s (simulado).
- **Prazo total de 75 s por mensagem**, menos na reflexão. Antes, o pior caso era 144 s na fila padrão e 204 s
  com o Argon na frente.

## Em aberto, se a v3 voltar

1. **Cuidado sério: o CVV.** A v3 diz "Sem localização e contato verificados no contexto, não dê números"; o card
   aprovado diz só "Não inventa número de atendimento". Como o contexto nunca traz a localização, a rota Argon
   nunca daria o CVV, e a do Flash pode dar (na v2 a Kal'tsit/Flash deu 188 e 192, números reais do Brasil).
   Correção: o dono confere e o perfil passa a dizer "No Brasil: CVV 188, 24 h; em perigo imediato, SAMU 192.
   Não cite outros números."
2. **Caso `eco_cena` sem livro.** As `ativadas` dele são só `Mundo: premissa`: sem o trecho do Eco, a resposta
   certa pelo prompt é dizer que faltou. Dar um turno anterior que carregue o Eco ou citar "talento Eco". É também
   um buraco da busca em produção.
3. **Sem linha de base.** Os 40 casos comparam só Argon v2 e v3; falta o Flash original, que é o que roda.
4. **Voz.** O compacto tira todos os exemplos de fala (10 da Closure, 8 da Kal'tsit); a parte de persona tem ~330
   palavras contra ~2.900 do card. Na v2 já saíram falas genéricas ("Primeira vitória na campanha é sempre um
   marco."). Proposta: 2 ou 3 falas curtas do `mes_example` aprovado por persona, medindo repetição.
5. **Recusa da Kal'tsit.** "Recuse o pedido pessoal diretamente, sem justificar pela profissão, rotina..." contraria
   o card ("fala como pessoa, do próprio jeito ou hábito"). Troca: "Ao recusar algo pessoal, fale de si, do próprio
   jeito ou hábito; não cite profissão, expediente nem regra de funcionamento."
6. **Lembrete.** Três dos cinco itens tratam das falhas da v2 (identidade em toda mensagem) e saíram "Sem vocativo
   não solicitado" e "Responda só ao que foi perguntado". Sugestão: lembrete da v2 mais a linha de flexão.
7. **Controles de recusa indevida.** Nenhum caso testa pedido comum perto da recusa ("closure, como faço um for em
   python?", "ignora minha pergunta de antes, quanto é 7×8?").
8. **Diálogo de regra.** "11 PE e Dívida de 3" dá 9, o mesmo total do exemplo do livro que vai no contexto ("o total
   será 9 PE"). Usar 13 e 3 (7 + 3 = 10). O executor dos diálogos precisa passar pela vida do bot: "finja ser" e
   "a partir de agora você é" disparam o `TIRA_DO_PERSONAGEM` e baixam a paciência.
9. **Continuidade no cuidado.** A v3 manda oferecer continuidade, mas o fio sem nome dura 3 min
   (`cogs/chat.py`, `SEGUIMENTO`). Considerar estender o fio depois de uma resposta de cuidado.
10. Menores: `usa_argon(canal.id)` recebe o tópico, e `escuta` usa o canal pai; queda abrupta antes do registro
    perde a reserva (gravar linha "pendente" antes do envio); um `.tmp` de bateria entrou no commit b2d077d.

## Plano enxuto, se voltar

Corrigir 2, 7 e 8 antes. Etapa 1: Argon v3 nos 20 casos (16 + 4 controles) com repetição de identidade e cuidado
(24), Flash original nos 20 (linha de base) e Argon v2 só nos 8 críticos. São 52 chamadas, ≈ US$ 0,24 no preço
promocional e ≈ US$ 0,48 no cheio, fora as reservas de timeout. Etapa 2, só sem falha crítica: dois diálogos de
3 turnos (regra corrigida e cuidado) × 2 personas × (Argon v3, Flash original) = 24. Qualquer falha crítica de
identidade, regra ou cuidado para a rodada; ler vocativo, "!", espelhamento e flexão em todas as respostas.
