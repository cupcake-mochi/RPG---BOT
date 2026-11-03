# Fichas oficiais 1.0, Ritual e livro R57 · 25/10/2026

Manutenção das Guias do Ciclo depois do PR #17 da ficha
(`cupcake-mochi/Ficha---RPG-JJK`, merge `9d932c5`). Base do bot: `main`
`6f28e67` (PR #73). Branch: `claude/project-thread-e9mxlm`.

## Atualização publicada — 30/10/2026

PRs85/86/87 mesclados e publicados no app existente, runtime
**`229e539416333896a723c21cf3f0e7d2799f6c5d`**, online às **23:23:20 (Brasília)**.
Consulta R60/v0.369, mecânica R53. Corrigidos os falsos alertas de categorias
CE 1/2/3 e a seleção de fontes para adaptação de feitiços; mensagens da análise
revisadas em português e inglês. 990 testes, zero falhas, um opcional pulado;
91/91 arquivos instalados iguais ao pacote. Backups, integridade e preservação
de ambiente/bancos/campanha conferidos. Painel real com XLSX sintético validado.
Nenhuma ficha oficial/jogador alterada. Detalhes e limites no
[registro da publicação](PUBLICACAO-R60-2026-10-30.md). Não republicar pelo
commit documental. Os registros de 25/26 abaixo são históricos.

## Publicação posterior — 26/10/2026

Os PRs [75](https://github.com/cupcake-mochi/RPG---BOT/pull/75) e
[76](https://github.com/cupcake-mochi/RPG---BOT/pull/76) foram mesclados e publicados
no app existente. Runtime **a7afebb17fc4ff0297699de13861d56d81825612**, online
às **09:03:19 (Brasília)**. A consulta usa R57/v0.367; a mecânica permanece R53.
Os guias incluem a orientação atual de inventário. Backup, preservação dos
dados, testes e limites: [registro da publicação](PUBLICACAO-R57-2026-10-26.md).
O registro de 25/10 abaixo permanece como histórico.

## Publicação concluída em 25/10/2026

O PR [#74](https://github.com/cupcake-mochi/RPG---BOT/pull/74) foi mesclado.
A `main` resultante, **`20773855e098f8c8b738bba3614bb3318611db27`**, inclui
os PRs #73 e #74 e foi publicada pelo **Commit** no app existente das Guias.
O log confirmou online em **25/10/2026 às 19:46:47,556 (Brasília)**, em seis
servidores. Não foi necessário Rebuild separado. Memória de 700 MB e vCPU
0,68 mantidas. Não houve publicação da Arquivista nesta rodada.

Antes de publicar, o backup do app foi criado, baixado e validado (ZIP íntegro,
3.296.137 bytes), incluindo `.env`, `closure_lab.db`, `src/var/bot.sqlite3` e
`src/var/ficha-campanhas.json`. Está em armazenamento privado fora do Git.
A inspeção dos arquivos `guias_ficha.py` e `recursos_publicos.py` do backup
mostrou que esses dois fontes já correspondiam à main do PR #73 (`6f28e67`),
embora faltasse o registro daquela instalação. Isso corrige a incerteza do
registro anterior; não é uma afirmação sobre todos os arquivos daquela versão.

### Pacote e preservação

- Núcleo preparado com as fontes R53, sem sincronizar o livro R57. Pacote
  gerado por `ferramentas/empacotar.py`: **90 arquivos / 1.804.046 bytes**.
- SHA-256 do ZIP: `62a410bd4d2424bf0891db3f4d1aa8892cc9aa1e37b256d2cc9bcdb15b7beff9`.
- Todos os 90 arquivos foram comparados com os fontes e, após publicar, com
  os instalados: **90/90 iguais, nenhum ausente**. Incluem o núcleo,
  `ficha_b47.py`, `guias_ficha.py`, `recursos_publicos.py` e o guia inglês.
- O pacote não contém `.env`, bancos, cadastro de campanha ou credenciais.
- Auditorias imediatamente antes e depois da publicação, antes dos ensaios
  no Discord: `.env`, cadastro de campanha, ambiente efetivo (27 chaves) e
  conteúdo de **todas as tabelas dos dois bancos idênticos**. Contagens e
  hashes comparados sem expor valores; verificação de integridade `ok` nos
  dois bancos. As mensagens dos ensaios posteriores são tráfego novo normal.

### Validação desta publicação

- Suíte completa, com o núcleo presente: **970 executados em 323,074 s,
  0 falhas e 1 online opcional pulado**. Não repetir por documentação.
- **9 regressões de Ritual** aprovadas usando o código extraído do ZIP.
- Preparação do núcleo: **14/14 comparações entre motores** aprovadas.
- `/ping` real no Discord às 19:52: **R53, v0.366, 576 trechos**, 43 ms.
- `GC:guia criar`, página 1: links `1MQqh…` e `1pgLD…`, com os nomes dos
  dois modelos e a explicação da versão pública 1.0.
- Pedido direto ao bot, por menção, “manda o link da ficha oficial”: os dois
  modelos. Na continuação “manda o link da ficha oficial da Era da
  Revolução”: somente Era. Fora dos canais configurados, nome solto não
  chama a guia; foi usada menção no tópico de testes. Respostas locais,
  sem passar pelo modelo.
- Cópia **descartável** da oficial Ciclo Maldito preparada no Google Sheets,
  somente em campos de entrada: Latente, Bastião/Muro, nível 10,
  Inteligência 5, Ritual. Rota recalculada em `DADOS_AM!A2`: `1 Fundamento`.
  Exportação XLSX nativa com **18.393 chaves**, analisada localmente e por
  `GC:ficha` no Discord às 19:54. **Nenhum alerta de Técnica Inata** nas
  correções completas; os dois resultados coincidiram (4 erros e 8 pendências
  de preenchimento incompleto, incluindo escolhas de treino, famílias e
  orçamento de Aptidão/Bênção). Isso não é aprovação integral da ficha.
  O seletor abriu a página Correções e revisão normalmente.
- Cópia enviada à lixeira depois do ensaio. Nenhuma ficha oficial ou de
  jogador editada. Campanha e aprovações preservadas; nenhuma chamada paga.
- Logs pós-deploy e pós-ensaios conferidos: zero Error/Fatal nestes fluxos.
  Dois avisos de bibliotecas de voz ausentes (PyNaCl/davey); voz em chamada
  não foi validada nem faz parte desta publicação.

### Pendências e retomada

A publicação solicitada está encerrada. A versão textual de produto continua
1.0.3; a identificação exata do código instalado é o commit acima. O próximo
commit é **somente este registro de documentação**: não republicar por ele.

1. **Código/consulta, rodada separada:** sincronizar R57/v0.367 do
   `JJK---Project` `353d772`, ajustar somente a guarda de Especialidade Antiga
   para a nova formatação, regenerar o núcleo, executar
   `ferramentas/auditar_consulta_livro.py` e os testes de consulta com o núcleo
   presente. Abrir PR próprio e aguardar pedido específico antes de publicar.
   Até lá, consulta e mecânica continuam R53/v0.366.
2. **Código/mecânica, só se solicitado:** Origem custom sem base ainda não
   usa `campo.rota` no filtro Aptidão/Bênção nem no +1 de orçamento de Sem
   Técnica. A correção de Ritual não altera esse limite.
3. **Dados do produtor e mestre:** campos não exportados e partes indicadas
   em Limites da análise continuam sem conferência automática. Autorizações
   reais, histórico, requisitos livres e efeitos narrativos seguem humanos;
   esta publicação não amplia o contrato nem concede aprovações.

Retomada exata: conferir o remoto e esta publicação antes de mexer. Para a
próxima rodada autorizada, criar branch a partir da main atual e tratar apenas
a sincronização de consulta R57, preservando os limites acima. Não repetir o
deploy, os ensaios pagos ou esta bateria por rotina.

## Registro anterior à publicação

O restante registra a implementação e as verificações feitas antes do deploy.
Quando disser “não publicado” ou “nenhuma planilha alterada”, refere-se àquela
etapa; a publicação e o ensaio sintético posteriores estão registrados acima.

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
