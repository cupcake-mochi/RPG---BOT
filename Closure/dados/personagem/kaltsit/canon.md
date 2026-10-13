# Kal'tsit: canon e corte de tempo

> Etapa 0 do `docs/PLANO-PERSONALIDADE.md`, 12/10/2026. Cada fato cita de onde saiu.
> Corpus em `dados/corpus_kaltsit/`, gerado por `ferramentas/extrair_corpus.py`.

> **Referência, não vai pro bot (decisão do Mizuki, 12/10/2026).** A Kal'tsit do bot vive no
> mundo do Ciclo Maldito. Daqui sai só o que explica a personalidade dela; nomes, lugares e
> eventos de Arknights ficam de fora do card, dos exemplos e do lorebook.

## A decisão que vem antes de tudo: qual Kal'tsit

A história mudou quem ela é, e o servidor global está no meio dessa mudança.

| Momento | O que ela é | Onde está o texto | Global tem? |
| ------- | ----------- | ----------------- | ----------- |
| Até o Episódio 14 | Médica-chefe e cofundadora da Rhodes Island, fria, cheia de segredo, milenar sem dizer | 5.811 falas EN de história, 38 falas de operadora EN, arquivo pessoal EN | Sim |
| Episódio 15 | Morre: "The life of AMa-10, Kal'tsit, ends here." Mon3tr vira operadora humana e diz que dá pra trazê-la de volta com um Sarcófago | 498 falas dela no cap. 15, já no EN | Sim |
| Episódio 17 (Kal'tsit·Esperanta) | Volta pelo Sarcófago como **humana comum**: adoece, envelhece, morre; diz que "não tem mais segredo"; sai da sala de guerra e fica no Médico; cabelo comprido; boato de que "o temperamento ficou melhor"; nome completo Kal'tsit·Esperanta (思衡托, "esperança") | 102 falas de história do cap. 17 e 8 do cap. 16, só em CN; 38 falas de operadora e arquivo, só em CN | **Chega em 14/10/2026** com o evento Critical Phase Transition; a lista de lançamentos da wiki ainda diz "TBA" pra operadora |

Fontes: [sinopse do Ep. 15](https://arknights.wiki.gg/wiki/Episode_15/Synopsis), [Critical Phase Transition](https://arknights.wiki.gg/wiki/Critical_Phase_Transition) (CN 01/05/2026, global 14/10/2026), [lista de lançamentos](https://arknights.wiki.gg/wiki/Operator/List/Release), e o arquivo da Esperanta lido direto do `operadora_esperanta_zh_CN.json` (não da tradução da wiki).

**Substituída:** a decisão de 12/10 mais tarde foi trocada pela personalidade **clássica**, fora do
arco do Mizuki (ver `mundo.md`). A Esperanta fica pra atualização futura. Texto original da
decisão anterior, pra histórico: **mescla.** A personalidade é a da Esperanta (canon atual). A voz
e o lore vêm das duas versões: ela lembra de tudo ("如果你希望的话，我也愿意与你分享那些过去的见闻",
Archive File 4 da Esperanta), então o corpus clássico continua sendo dela. O que mudou (mais
leve, sem segredo, mortal, no Médico e não na sala de guerra) vira regra escrita na ficha de voz,
citando fala da Esperanta. Depois de 14/10, troca o CN pelo EN oficial.

**Ponto de spoiler:** quem joga no global só vê a Esperanta a partir de 14/10. Até lá, ela é
spoiler pro servidor.

## Fatos que valem pra qualquer versão

- Cofundadora da Rhodes Island e líder do Departamento Médico; "profoundly learned" em
  metalurgia, sociologia, artes de Originium, arqueologia, história, economia, botânica,
  geologia. *(Profile, `operadora_en_US.json`)*
- A ficha dela é disfarce: "Combat Experience 3 Years", "Place of Birth Rhodes Island",
  "Race Feline". O Archive File 5 desmente: ela viu Terra "ten thousand years ago, when
  Originium had yet to spread" e guarda "satellite photos stored in my body".
- O nome real do projeto dela é AMa-10, uma máquina pensada pra ajudar a reconstruir depois
  da "Silence"/寂静, que não devia ser reconhecida como vida. *(Ep. 15; Archive File 3 da
  Esperanta)*
- Mon3tr é a criatura de Originium ligada a ela; virou operadora própria no Ep. 15
  (global desde 16/09/2025).
- Relação com Theresa: Babel, a promessa de cuidar da Amiya ("I will raise her", Archive
  File 3), e a carta da Theresa no Promotion Record ("I hope the Rhodes can be a place you
  name home").
- Com o Doutor: é a única que pode examiná-lo ("No other personnel have this authority",
  Talk 1); a promessa "to protect yours and Amiya's hopes" (Trust 3).
- No Archive File 4, quem acha os registros secretos dela (com "full privileges" já
  liberados) é, pelo jeito de falar ("y'know", "my funds"), a Closure. *(inferência)*

## O que não usar como canon

- O conjunto `char_003_kalts_boc#6` (38 falas) é da skin **Remnant** (Bloodline of Combat/VI),
  um futuro alternativo onde "Originium has taken over the land". Está separado nos JSON.
- A idade de "13.352 anos" da wiki é especulação de fã (Trivia).
- Falas em que ela aparece como "???" antes de ser revelada não entram no corpus: o extrator
  só pega a tag com o nome dela.

## Ainda por conferir

- Das 110 falas CN dos caps. 16 e 17, só as cenas 17-02 e 17-04 são claramente depois da volta;
  16-08, 17-01, 17-09 e 17-16 parecem flashback (ver `voz.md`). Confirmar no EN.
- O que acontece com ela no cap. 16 (8 falas, só CN) e o texto completo do cap. 17, quando
  sair o EN no dia 14.
- O espelho EN do corpus está parado em 13/11/2025; depois de 14/10 vai ter fala dela em EN
  que ele não pega.
