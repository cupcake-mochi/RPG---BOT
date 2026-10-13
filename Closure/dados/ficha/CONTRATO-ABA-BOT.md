# Contrato da aba oculta `BOT`

> **Rascunho de 12/10/2026, para o Mizuki ajustar.** Os campos foram tirados dos
> catálogos do sistema (`dados/sistema/catalogos.json`), não da ficha: a ficha
> "Ficha - Era da Revolução" ainda vai mudar (faltam as Origens). Quando ela fechar,
> confira esta lista contra ela e suba `versao_ficha`.

## Por que existe

A aba visível (CARTEIRA) é toda de célula mesclada. O bot antigo lia a planilha por
coordenada (`K5`, `T2`, `L12`…) e quebrava toda vez que o layout mudava. A aba `BOT`
é a única coisa que o bot lê: o visual pode mudar à vontade, desde que as fórmulas
daqui continuem apontando para as células certas.

## Formato

- Aba chamada **`BOT`**, oculta.
- Coluna A: `campo`. Coluna B: `valor`. Coluna C (opcional): observação. Linha 1 é cabeçalho.
- `valor` é **só fórmula** apontando para a aba visível (`=CARTEIRA!O9`), nunca valor digitado.
- Nome de campo em minúsculo, sem acento, com ponto para agrupar. Listas viram linhas
  numeradas a partir de 1 (`tecnica.1.nome`, `tecnica.2.nome`…).
- Campo vazio na ficha = célula vazia em `valor`. O bot trata vazio como "não preenchido".
- O jogador manda o `.xlsx` exportado (Arquivo > Fazer download > .xlsx). O Google grava o
  resultado das fórmulas e o bot lê a aba mesmo oculta.

## Campos

| campo | o que é | exemplo de valor |
| ----- | ------- | ---------------- |
| `versao_ficha` | número do layout; sobe quando a ficha mudar | `1` |
| `nome` | nome do personagem | `Kaori` |
| `nivel` | nível total | `2` |
| `caminho` | um dos Caminhos do catálogo | `Bastião` |
| `trilha` | Trilha do Caminho (vazio antes de ter) | `Muro` |
| `origem` | uma das Origens do catálogo | `Latente` |
| `atributo.forca` | valor do atributo | `2` |
| `atributo.destreza` | | |
| `atributo.constituicao` | | |
| `atributo.inteligencia` | | |
| `atributo.essencia` | | |
| `tr.fisico.atributo` | `Força` ou `Destreza` (travado na criação) | `Força` |
| `tr.<nome>.treinado` | `sim`/`não` para fisico, vigor, intelecto, espirito | `sim` |
| `pericia.<nome>.treinada` | `sim`/`não`, uma linha por perícia do catálogo (23) | `sim` |
| `oficio.<nome>.treinado` | `sim`/`não`, uma linha por ofício do catálogo (11) | `não` |
| `vida.max` | vida máxima | |
| `pe.max` | PE máximo | |
| `defesa` | Defesa | |
| `integridade.max` | Integridade | |
| `maestria` | | `1` |
| `refino` | | `1` |
| `xp.atual` | | |
| `tecnica.nome` | nome da técnica | |
| `feitico.<n>.nome` | feitiços conhecidos | |
| `feitico.<n>.pontos` | pontos gastos no feitiço | |
| `aptidao.<n>.nome` | aptidões | |
| `equipamento.<n>.nome` | itens | |

Nome de perícia/ofício/TR no campo: o nome do catálogo em minúsculo, sem acento, com
espaço virando `_` (`lidar_com_animais`, `sentir_energia`).

## O que o bot faz com isso

1. Lê `versao_ficha`. Se for diferente da que ele conhece, avisa e não corrige.
2. Confere os nomes (`caminho`, `trilha`, `origem`, perícias) contra `catalogos.json`.
3. Recalcula o que é derivado (vida, PE, Defesa, Integridade, contagem de perícias
   treinadas) e compara com o que a ficha diz.
4. Devolve a lista de diferenças com a âncora do livro de cada regra.
