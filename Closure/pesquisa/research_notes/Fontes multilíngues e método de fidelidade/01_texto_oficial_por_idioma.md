# Frente 1: texto oficial da Closure por idioma (Arknights)

> Nota de pesquisa, coletada em 12/10/2026, refeita depois que a primeira tentativa (4 agentes) caiu sem gravar nada.
> Método: dados do cliente do jogo espelhados no GitHub, baixados e contados por script. Os números abaixo saíram de contagem direta, não de wiki.

## Fontes primárias usadas

| Repositório | Idiomas | Última atualização | Observação |
|---|---|---|---|
| `Kengxxiao/ArknightsGameData` | zh_CN | 09/10/2026 (dados de 08/10/2026, versão 78.0.0) | Atual. Global saiu deste repo. |
| `Kengxxiao/ArknightsGameData_YoStar` | en_US, ja_JP, ko_KR | 13/11/2025 (EN data 25-11-11) | **Parado há 11 meses.** Tudo do global depois de nov/2025 falta aqui. |

Acesso: `raw.githubusercontent.com` e `git clone --filter=blob:none` com sparse-checkout em `*/gamedata/story/` funcionam deste ambiente. A API do GitHub, prts.wiki e arknights.wiki.gg são bloqueados por curl aqui (via WebFetch é outra rota).

## A Closure como operadora

- ID interno: `char_4228_closur`. Nome CN 可露希尔, appellation "Closure". Raridade 6 estrelas (TIER_6), classe Vanguard (`PIONEER`), subclasse `tactician`.
- Frase de recrutamento (itemUsage): 罗德岛总工程师可露希尔，以先锋身份亲临前线！
- Dubladoras: CN 侯小菲, JP 沼仓爱美 (só essas duas vozes no `voiceLangDict`; sem EN/KR registradas no CN).
- Texto de operadora no CN: **38 falas** (charword: secretária, conversas, promoção etc.) e **9 blocos de arquivo pessoal** (handbook).
- No espelho global (parado em nov/2025) ela **não existe** como operadora: nem `character_table`, nem falas, nem arquivo em EN/JP/KR. Isso só prova que não existia até nov/2025; o status atual no global precisa de outra fonte (ver frente 1b abaixo).

## A Closure como NPC na história (o volume grande)

Contagem de linhas com `[name="<nome dela>"]` nos arquivos de história:

| Idioma | Nome na tag | Falas | Arquivos | Caracteres de fala |
|---|---|---|---|---|
| zh_CN (até 10/2026) | 可露希尔 | 2.096 | 120 | ~138 mil |
| en_US (até 11/2025) | Closure | 1.557 | 77 | ~111 mil |
| ja_JP (até 11/2025) | クロージャ | 1.557 | 77 | ~158 mil |
| ko_KR (até 11/2025) | 클로저 | 1.557 | 77 | ~128 mil |

- EN, JP e KR têm exatamente o mesmo número de falas e arquivos: o global traduz arquivo por arquivo, então dá para **alinhar fala a fala** entre os três (mesmo arquivo, mesma ordem). O CN é o original e alinha com eles nos 77 arquivos em comum.
- As 539 falas a mais do CN vêm sobretudo da história principal recente (62 arquivos em `obt/main`) e de 23 arquivos de `obt/sandboxperm` (Reclamation Algorithm), conteúdo que o global ainda não tinha em nov/2025.
- Onde ela mais fala em EN: `act8mini` st06 (138), Operator Record da Snowsant (111), `act4d0` st07 (81), records de Weedy, Thermal-EX e Ines/otter, capítulos 14, 15, 9 e 10 da principal.
- Apelidos que aparecem: "Clo" (Cliffheart chama assim). O Doutor aparece como placeholder `{@nickname}` em alguns textos.

## O que foi salvo

Extração pronta em `Closure/dados/corpus_closure/` (JSONL, uma fala por linha, com arquivo, número da linha e a fala anterior como contexto):

- `historia_zh_CN.jsonl`, `historia_en_US.jsonl`, `historia_ja_JP.jsonl`, `historia_ko_KR.jsonl`
- `operadora_zh_CN.json`: as 38 falas de operadora e os 9 blocos de arquivo, em chinês.

Script que gerou: tag `[name="..."]` exata, sem fuzzy. Falas com tag de nome variante (ex.: "Closure's Muffled Voice", 1 por idioma) ficaram de fora.

## Inferências

- O corpus em inglês já é grande o bastante para minerar a ficha de voz (passo 1 do relatório anterior): ~1.500 falas cobrem tom, bordões, como ela trata Doutor, Kal'tsit, Amiya e Warfarin.
- Para as falas de operadora (as mais "de personagem", feitas pra soar como ela), por enquanto só existe o chinês nos dados. Tradução de fã para EN deve existir na wiki em inglês; ver frente 1b.

## Lacunas

- Status atual da Closure jogável no global (EN) não confirmado pelos dados.
- Não conferi se há texto dela fora de `story/` (descrição de loja, e-mail, mensagens de evento), que deve ser pouco.

## Frente 1b: status atual pela wiki em inglês (arknights.wiki.gg, lida em 12/10/2026)

- [Lista de lançamentos](https://arknights.wiki.gg/wiki/Operator/List/Release): Closure lançada no CN em **30/04/2026**, global **"TBA"**. Últimos lançamentos do global: Zima the Raging Tide, Botani e Ukusik em 16/09/2026. Último do CN: Homebound, 08/10/2026.
  - O README dizia 01/05/2026 e a wiki diz 30/04. **Validação:** nos dados do jogo (`activity_table`, evento `act4mainss` 相变临界 = Critical Phase Transition) o início é 01/05/2026 07:00 UTC+8, ou seja 30/04 20:00 em Brasília. As duas datas estão certas, cada uma no seu fuso.
- [Página dela](https://arknights.wiki.gg/wiki/Closure): 6★ Tactician, introduzida no evento **Critical Phase Transition**, "[CN] Standard Headhunting". A wiki já lista dubladora em inglês (Carla Tassara), o que indica que o EN tem elenco definido, mas não há texto EN oficial ainda.
- [Dialogue](https://arknights.wiki.gg/wiki/Closure/Dialogue): as 38 falas estão **em chinês**, marcadas como "Untranslated". Não há tradução EN nem de fã ali.
- [File](https://arknights.wiki.gg/wiki/Closure/File): cabeçalho e introdução em inglês (tradução de fã creditada a "Shainel", a partir de post do Bilibili); Clinical Analysis e Archive Files ainda em chinês. O Archive File 1 é uma piada: "este documento é conteúdo pago, fale com a Closure para comprar acesso".

## Endfield

- Não achei nada que coloque a Closure como personagem do Endfield. A wiki do Endfield bloqueia leitura automática (robots), e a busca geral só trouxe a nave Rhodes Island no Talos-II. Fica como lacuna; o Endfield serve ao projeto como fonte de **texto oficial em pt-BR do universo** (vocabulário, termos traduzidos), não de fala dela.
