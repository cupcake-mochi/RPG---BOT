# Consulta do livro R57 · 25/10/2026

**Publicado em 26/10/2026**, runtime `a7afebb17fc4ff0297699de13861d56d81825612`, incluindo PRs 75 e 76. [Resultado e validações](PUBLICACAO-R57-2026-10-26.md). As referências a pendência de merge/publicação abaixo descrevem a preparação anterior.

## Estado

Atualização preparada na branch `codex/consulta-r57`, a partir da main
`07836153b017399a634586447f36b1664ae5d90a`. Esta rodada atualiza **a consulta**;
a mecânica dos cartões continua R53. Não houve merge nem publicação na
Discloud. O app continua no código `2077385`, publicado às 19:46:47 de 25/10,
com consulta R53/v0.366, conforme o registro de publicação anterior.

## Fonte

- `cupcake-mochi/JJK---Project`, main conferida em
  `353d7728fa4f505f830dc6c0421929a0ab2668c1` (R57/v0.367).
- Importação por `ferramentas/sincronizar.py`, sem editar o produtor:
  576 blocos, 21 capítulos, mesmas âncoras. Mudaram 89 blocos em relação ao
  corpus R53 do bot.
- Os registros R53→R54, R54→R55, R55→R56 e R56→R57 contêm, respectivamente,
  40, 28, 1 e 34 alterações: **103**, todas com `altera_regras: false`.
  É a classificação do autor; não equivale a uma nova aprovação mecânica
  independente de cada frase. Uma mesma âncora pode receber várias alterações.
- `catalogos.json` permaneceu idêntico byte a byte. O objeto completo de
  referências mecânicas carregado por `Referencias.do_livro` também ficou
  igual ao obtido da R53 antes da sincronização. Não houve alteração dos
  motores R53 nem da fonte histórica `legado-r52.jsonl`.

## Guarda de Especialidade Antiga

O carregamento da R57 foi testado **antes da correção** e recusou
`Especialidade Antiga`, em `origens--encarnado-beneficios`. A frase agora diz
`sem precisar escolher **Corpo** naquele **[Marco](#progressao--prog-marcos)**`.

Somente nessa capacidade, a guarda aceita `**Corpo**` como `Corpo`.
O link de Marco está depois do trecho que já era conferido. Não foi criada
uma limpeza genérica de Markdown: âncora, nome e frase obrigatória continuam
sendo exigidos, assim como todas as comparações literais das demais capacidades.
Mudanças em requisito ou nome continuam bloqueadas pelos testes de regressão.
O nível mínimo e o benefício não foram alterados.

## Validação

- Suíte completa com o núcleo presente: **975 executados em 330,929 s,
  974 aprovados, zero falhas e um online opcional pulado**. Os testes de
  consulta rodaram; não foram pulados por ausência do núcleo. Nenhuma
  expectativa existente precisou ser alterada.

- Núcleo regenerado com a R57: QuickJS e Node iguais nos **14/14 pedidos**
  da preparação local.
- `auditar_consulta_livro.py`, comparando com o núcleo R53 preservado antes
  da mudança: **497/497 fontes esperadas antes e depois**.
  A auditoria mede recuperação de fontes de títulos únicos; não mede respostas
  geradas por IA nem cobre títulos repetidos, continuações e exemplos.
- Quatro novos testes de guardas: texto R57 com negrito/link, compatibilidade
  sem negrito, recusa de requisito/nome alterados e preservação das demais
  guardas. Um teste de consulta exige o texto R57 completo de Especialidade
  Antiga no contexto, evitando aprovar um núcleo antigo por engano.
- ZIP regenerado por `ferramentas/empacotar.py`, sem `.env`: **90/90 arquivos
  iguais aos fontes**, 1.813.869 bytes. SHA-256:
  `0d6cdc940db92849bdd93d640b9b7ab749278257fc3456798e7ad33966c35462`.
  O núcleo empacotado contém o trecho R57 e o manifesto informa R57/v0.367.
  Nenhuma credencial, banco ou cadastro de campanha no pacote. Mais quatro
  pedidos locais no ZIP extraído (Kal/Closure × QuickJS/Node) trouxeram o
  texto R57 completo e tiveram paridade entre motores.
- Evidências locais reproduzíveis:
  [fontes](../pesquisa/validacao/2026-10-25-consulta-r57/fontes.json),
  [testes](../pesquisa/validacao/2026-10-25-consulta-r57/testes.json) e
  [pacote](../pesquisa/validacao/2026-10-25-consulta-r57/pacote.json).
- Nenhuma chamada paga, mensagem ao Discord ou alteração de ficha oficial,
  de jogador ou de campanha nesta rodada. Sem teste nativo de resposta de
  modelo ou validação pós-deploy: o pacote ainda não foi publicado.

Para repetir somente quando houver motivo, a partir de `Closure/`:

```sh
.venv/bin/python ferramentas/prompt_do_site/site_prompt.py --atualizar
.venv/bin/python ferramentas/auditar_consulta_livro.py --saida /tmp/fontes-r57.json
cd src
../.venv/bin/python -m unittest discover -s testes
```

## Retomada

Revisar e mesclar a PR desta branch; publicar somente após pedido específico.
Ao publicar, fazer e baixar backup do app existente, usar Commit, comparar
arquivos instalados e dados preservados. O diagnóstico deve então informar
**consulta R57/v0.367**. A mecânica continua R53; não renomear o contrato
ANALISE 12 nem seus campos por causa da revisão editorial do livro.

A rota de Origem custom sem base no filtro Aptidão/Bênção e no +1 de orçamento
Sem Técnica continua fora deste trabalho. Campos ausentes e decisões reais do
mestre conservam os limites já documentados. Não reabrir a bateria paga ou
republicar a versão anterior por rotina.
