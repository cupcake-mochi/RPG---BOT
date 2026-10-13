# Kal'tsit: lorebook (etapa 5)

> 12/10/2026. Etapa 5 do `docs/PLANO-PERSONALIDADE.md`. O arquivo que vai pro bot e pro
> SillyTavern é o `lorebook.json` (World Info). Este arquivo explica o que tem nele.
> Gerado por `ferramentas/gerar_lorebook_kaltsit.py`: mudança de texto se faz no script.

## O que tem

| Grupo | Entradas | Fonte | Como foi escrito |
| ----- | -------- | ----- | ---------------- |
| Mundo | 32 (1 sempre ligada) | doc "Lore Simplificada - Era da Revolução", abas Mundo e Mestres, lido inteiro em 12/10 | Reescrito curto, fato primeiro e as versões depois, com as palavras do doc. Mediana de 48 palavras |
| Sistema | 53 | Glossário do livro (`dados/sistema/livro.jsonl`), mais uma entrada pro capítulo "Criar um personagem" | Definição copiada do livro, com a âncora. Só os termos que existem no sistema; os genéricos (Ação, Turno, Área, Cena...) ficaram de fora pra não disparar em conversa comum |

A sempre ligada é a premissa do mundo (~150 tokens): de onde vem a energia amaldiçoada, Escola ×
Rhine, oripatia, o registro tem buracos, versões não são fato, existem outras facções.

## Como aciona

- Por palavra-chave na mensagem, sem diferenciar maiúscula e com variante sem acento.
- No máximo 5 de mundo e 3 de sistema por mensagem. Quando bate mais que isso, ganha a entrada da
  chave mais longa ("arquivo restrito" passa na frente de "escola").
- O bot usa `ferramentas/ativar_lorebook.py`, que faz o mesmo que o SillyTavern faz com essas opções.
- A regra com número continua vindo do trecho do livro, que é outra busca. O lorebook só define o
  termo.

## O que mudou em relação às entradas do teste

- A da Escola tem triagem, tutoria e as escolas de Tóquio e Kyoto.
- A da Rhine perdeu "tecno-mística", e a Kristen Wright virou entrada própria, pra ela não aparecer
  em toda resposta sobre a Rhine. A ruptura com a Escola também virou entrada própria.
- A origem do Origíneo saiu da entrada do Origíneo e virou entrada própria.
- Ozpin é diretor da escola de Tóquio, e quem dirige a de Kyoto não está no registro.

## Pra decidir (Mizuki)

- **A aba Mestres vai pros jogadores?** Algumas entradas vêm do Guia do Mestre: as Limitações,
  com a "resposta do mundo", "Ninguém é vilão", "Oripatia em mesa" e a regra do NPC nomeado. Eu pus
  porque o `mundo.md` já decidiu que as Limitações viram regra dura dela, e as outras explicam o
  mundo sem revelar segredo. Se preferir que jogador não leia isso pela boca dela, é só tirar.
- **"Fato + o que ela acha"**: o plano pedia isso, mas o card manda ela só opinar quando pedem.
  As entradas não têm opinião dela; quando pedem, ela opina com o que está ali.
