# Divergências entre a ficha e o livro (pente fino de 14/10/2026)

Pente fino do corretor da fase 3 contra o livro R51 e as fórmulas da ficha gerada (B47, fase 1, commit `dbdf1d4`). O
conserto destas é no gerador da ficha, não no bot. Até lá, o bot sabe de cada uma e **não reprova** por elas: avisa
o que falta ou manda pro mestre conferir.

| # | O que o livro diz | O que a ficha faz | O que o bot faz até a ficha mudar |
| - | ----------------- | ----------------- | --------------------------------- |
| 1 | **Especialidade Antiga** (Encarnado): no nível 10, especialista na competência do Conhecimento Reavivado, "sem precisar escolher Corpo no Marco" (`origens--encarnado-beneficios`) | conta toda especialização como uma escolha de Corpo gasta (`DADOS!AK15`, `AK16`) e mostra "1 a mais" | não reprova o "a mais" que ela explica; manda pro mestre conferir |
| 2 | Treino além dos 9 ou 10 da criação: **Duas Vidas** (Encarnado, 1), **Aprendizado Complementar** (Restrição corporal, 1 perícia ou 2 ofícios), **Arquivo de Procedimentos** (Corpo Amaldiçoado, 1 ativo) | conta só 9 perícias e 2 ofícios, ou 10 e nenhum (`DADOS!AK19`, `AK20`), e mostra "a mais" | idem: até o número que a capacidade dá, vira nota pro mestre |
| 3 | PE a mais: **Núcleo Dependente** (Essência + marcos × metade da Essência) e **Reserva Excedente** (2 × Essência) | o PE máximo (`FICHA!J30`) não soma | avisa que falta pôr o valor no Buff de PE e confere se o Buff tem esse valor |
| 4 | **Corpo Debilitado, Quebradiço e Exaurido** (Restrição corporal): Defesa fixada em 0, sem bônus; o Quebradiço tem metade da vida máxima | a Defesa (`FICHA!D59`) e a vida (`FICHA!J26`) saem normais | aceita Defesa 0; só a Defesa normal calculada recebe pendência de ajuste, qualquer outro valor reprova. Vida pela metade continua pendência quando a ficha não aplica |
| 5 | O `ESQUEMA-ANALISE.md` chama os resultados de `vida.max`, `energia.max`... e a Origem de `origem.menor.1` | a aba usa `vida_max`, `energia_max`, `origem.menor_1` | o bot segue a aba (é ela o contrato); o esquema precisa ser atualizado |
| 6 | Um treino extra da Origem deve ter uma conferência pelo mestre | o mesmo contador de excesso pode acender em Perícias, Ofícios (mesmo com dois marcados) e no resumo | junta avisos do mesmo excesso justificado em uma nota, preferindo o resumo; valores diferentes e excessos sem permissão continuam visíveis |
| 7 | **Núcleo Dependente**: não possui barra de Integridade (`origens--corpo-inteiro-manutencao`) | a Teste 4 mantém a fórmula normal de Integridade 60 | fórmula normal recebe pendência para desconsiderar a reserva, sem certificar o número; zero/vazio reconhecem ausência de barra; outros valores reprovam |
| 8 | Um escudo só impede o Selo se ocupar a mão exigida pelo Selo da técnica | `marca_selo` mostra "Trava Selo de gesto" sempre que há escudo, sem ler o Selo escolhido; a ANALISE não exporta essa escolha | omite esse aviso genérico por falta de impacto confirmado. Avisos específicos continuam classificados; retomar a conferência quando o contrato trouxer o requisito do Selo |
| 9 | Linha cresce em comprimento até 60 m e depois em largura para 3 m e 4,5 m (`fundamento--alcance`) | o gerador publicado com ANALISE 2 conserva largura 1,5 m mesmo nesses aumentos | só a largura antiga exata gera pendência com a medida correta; medida do livro é conferida, outros valores reprovam |
| 10 | Toca a Alma reduz os dados pela metade, para baixo (`catalogo--cat-defesas`) | fórmula comum do gerador mantém os dados anteriores à redução | só os dados e a média exatos da fórmula antiga recebem pendência; resultado correto é conferido numericamente, permissão da Regra continua manual. Interação com adicionais/distribuição continua não certificada |
| 11 | Ataque armado da entidade usa o atributo da arma, mantendo a CD pelo atributo escolhido (`construcao--entidades-atributos`) | `DADOS_INVOC.atq` usa sempre o atributo de acerto escolhido; o gerador não troca pelo atributo da arma | só esse bônus antigo exato recebe pendência quando não coincide com um atributo permitido pela arma. Outros valores incompatíveis reprovam. Falta de treino continua desvantagem; modalidade/Fineza exige registro |
| 12 | Precisão dá +2 no ataque **ou na CD**, conforme a resolução (`catalogo--cat-mira`) | a resolução da carta da entidade acrescenta +2 ao ataque, mas mantém a CD original | na resolução por TR, só a CD antiga exata recebe pendência; a CD correta é recalculada das entradas. Separação da CD de Controle e bônus de saldo zero continua manual |
| 13 | Reserva Profunda aumenta PE máximo em 3 × maior Classe (`catalogo--cat-passivas-3`) | fórmula pessoal soma Caminho e Buff, sem identificar esse Talento | aceita o total do livro com o acréscimo; o total legado exato recebe pendência para conferir se o Buff já o inclui. Não certifica a origem do Buff nem soma o acréscimo duas vezes por Talento repetido |

## O que bate (conferido)

- Vida, PE, Integridade, proteção e Defesa, pelas fórmulas das peças 1, 11, 14 e 24: iguais às da ficha em quatro
  fichas recalculadas (em branco, Kaori, Revestimento 2 com Broquel e Buff, Refino 6 por marcos com escudo Médio).
- Proteção da rota sem energia: a Defesa sem Armadura usa a Lapidação com a mesma conta e a mesma progressão do
  Refino, e a ficha usa a mesma célula. Igual ao livro.
- Escudo com arma de duas mãos não conta; as 21 armas de duas mãos do livro são as mesmas da ficha.
- Maestria sobe nos níveis 10, 18 e 26; marcos nos níveis 6, 10, 14, 18, 22, 26 e 30; Refino até 10.
- Especialização só a partir do nível 10, sem exceção de Origem antes disso.
- Revestimento 2 pede Grau 3, Revestimento 3 pede Grau 2 (`equip--eqc-dinheiro`): o "Pede Grau" da ficha reprova.
- Falta de Força pro equipamento: o livro deixa usar com penalidade; o bot avisa sem reprovar.
