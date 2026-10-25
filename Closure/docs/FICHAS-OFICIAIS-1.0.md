# Fichas oficiais 1.0, Ritual e livro R57 · 25/10/2026

Manutenção das Guias do Ciclo depois do PR #17 da ficha
(`cupcake-mochi/Ficha---RPG-JJK`, merge `9d932c5`). Base do bot: `main`
`6f28e67` (PR #73). Branch: `claude/project-thread-e9mxlm`.

## Estado conferido antes de mexer

- **GitHub `main`**: PR #73 (24/10), que já apontava o guia para a `1pgLD…` e
  registrava a `1MQqh…` só como base do servidor.
- **Publicado na Discloud**: 1.0.3 (21/10), segundo `docs/FILA-ATUAL.txt`. O
  ZIP do PR #73 foi entregue para atualização manual; não há registro de que
  tenha sido aplicado. Esta rodada não publica nada.
- **Cópia local do Mizuki** (`RPG---BOT-b47`): branch `codex/clareza-siglas`,
  anterior ao PR #73. Por isso ela ainda mostrava a ficha histórica `1u0z…`.
- `AGENTS.md` fica no repositório da ficha, não no do bot. Lido no `main` após o PR #17.

## 1. Links e guias

As duas oficiais (`r53/OFICIAIS.md` da ficha) passam a ser oferecidas juntas,
com nome: **Ficha · Era da Revolução** (`1MQqh…`) e **Ficha · Ciclo Maldito**
(`1pgLD…`). Se a pessoa cita uma pelo nome ("da Era da Revolução", "for Ciclo
Maldito"), vai só aquela. "Era" sozinho não escolhe modelo, porque é verbo comum.

- `recursos_publicos.py`: `FICHA_ERA_REVOLUCAO`, `FICHA_CICLO_MALDITO`,
  `MODELOS_FICHA`; `FICHA_OFICIAL` continua como nome antigo (Ciclo Maldito).
  O contexto das personagens recebe as duas chaves
  `character_template_era_revolucao` e `character_template_ciclo_maldito`.
- `guias_ficha.py` e `recursos/guias-en.json`: etapa 1 do `GC:guia criar` em
  PT/EN com os dois links e a explicação do 1.0.
- A `1u0z…` sai de tudo que é apresentado como atual. Fica nos relatórios
  históricos e no teste de formato B47 (`FICHA_HISTORICA_B47` em `test_ficha.py`).
- Comandos existentes não mudaram.

**Versões diferentes**: 1.0 é a versão pública da ficha (cabeçalho e número da
carteira). O contrato técnico continua R53, ANALISE 12 / montagem esquema 2.
O bot continua 1.0.3 publicado. O livro tem revisão própria (abaixo). Nada foi
trocado em massa: "R53" continua onde é referência técnica ou histórica.

## 2. Ritual e Técnica Inata

**Fluxo antes**: `conferir_b47` → `conferir_aptidoes` cria `Contexto` sem
`tecnica_inata` (padrão `False`) → `aptidoes()` sempre emite "exige Técnica
Inata" para Ritual → `conferir_aptidoes` rebaixa isso a pendência informativa.
Resultado: toda ficha com Ritual ficava com pendência, mesmo com Técnica, e uma
ficha Sem Técnica ou Técnica Marcial também só ficava pendente, sem erro.

**Agora** a Técnica vem da rota estruturada da Origem, como a ficha faz em
`DADOS_AM!A2` (correção 737e3d5 da ficha):

| Origem | Rota | Ritual |
|---|---|---|
| Latente, Receptáculo, Descendente, Encarnado, Híbrido, Restrição corporal | 1 Fundamento | sem aviso de Técnica |
| Origem do livro com "· Sem Técnica" | 2 Manejos | erro (livro: Sem Técnica não adquire Ritual) |
| Corpo Amaldiçoado | 3 Técnica Marcial | erro |
| Restrição Celestial · Sem Energia | 4 sem energia | erro |
| Custom **aprovada e válida**, sem base | `campo.rota` do cadastro | conforme a rota |
| Custom com BASE DO LIVRO | a visão mecânica já troca pela base (+ Sem Técnica se Manejos) | conforme a base |
| Custom sem aprovação válida, ou nome desconhecido | não confirmada | **pendência informativa**, com o motivo |

Nível 10, Inteligência 5, consumo de escolha e as demais aptidões seguem iguais.
Nada é aprovado por padrão: sem cadastro aprovado, a pendência continua.

**Limite conhecido, não alterado nesta rodada**: para custom sem base, o
`Contexto.rota` usado no filtro de menu (Aptidão × Bênção) e o +1 de orçamento
do Sem Técnica continuam vindo só do nome da Origem, como antes. Só a Técnica
Inata do Ritual passou a usar `campo.rota`. Mudar o resto mexe em outras regras
e merece rodada própria.

## 3. Livro

O livro publicado é a **R57** (v0.367, 25/10/2026, 415 páginas), em
`cupcake-mochi/JJK---PDF---RPG` `d6f462c` e `cupcake-mochi/JJK---Project`
`353d772`. SHA-256 do PDF claro: `40a405e0…`.

Diferença em relação à R53, pelos registros do próprio repositório
(`revisao-de-regras/alteracoes/R53-para-R54` … `R56-para-R57`): 103 alterações,
**todas com `altera_regras: false`**. R54 contextualiza termos antes do uso
(40), R55 acerta remissões e índice (28), R56 ajusta a ordem do roteiro de
criação (1), R57 acrescenta contexto em 34 blocos. O `catalogos.json` gerado é
idêntico ao atual. Isso é o que o autor registrou; não foi feita releitura
humana das 103 mudanças.

**O bot ainda lê o texto R53 (v0.366).** Sincronizar o corpus foi testado e
revertido:

- `ferramentas/sincronizar.py` aceita a v0.367 (576 blocos, 89 com texto mudado).
- Uma guarda do corretor para: Especialidade Antiga (`origens--encarnado-beneficios`)
  trocou "escolher Corpo no Marco" por "escolher **Corpo** naquele **[Marco]…**".
  É só formatação, mas o corretor recusa carregar sem revisão.
- A consulta conversacional usa o núcleo gerado por `ferramentas/empacotar.py`,
  que embute o livro. Integrar a R57 pede regenerar o núcleo, rodar
  `auditar_consulta_livro.py` e conferir os testes de consulta, como nas rodadas
  anteriores.

Até isso ser feito, `/ping` e o README dizem a verdade: livro lido R53 (v0.366).
O guia já manda conferir a edição usada pela mesa.

## Testes

Suíte completa em `Closure/src`: 970 executados, 66 pulados (camada de
consulta sem núcleo local e testes online opcionais), 0 falhas.
Novos: `test_ritual_tecnica.py` (9 testes: livro com e sem Técnica,
Técnica Marcial, sem energia, custom aprovada Fundamento/Manejos, custom com
base, custom sem aprovação, Inteligência 4, nível 9). Com o código antigo, 23
subcasos falham. `test_r53_definitiva.py` ganhou os testes dos dois modelos, do
modelo pedido pelo nome e do contexto público. Nenhuma planilha foi lida ou
alterada; nenhuma chamada de modelo pago.
