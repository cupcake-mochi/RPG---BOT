# Conferência posterior à versão 1.0 · 21/10/2026

## Consulta geral do R53

Fonte corrente: `cupcake-mochi/JJK---Project@1432c477f812aaaf1e0e8fdff8ed54d1709a663d`,
v0.366. O produtor da ficha foi conferido em
`Ficha---RPG-JJK@fbd6d156602958dc0f9da467a4a80100ad7b913f`.
Nenhuma fonte, planilha oficial ou Apps Script oficial foi alterado.

O corpus passa de 511 para 576 blocos. As 202 alterações (91 adições,
26 remoções, 85 modificações) foram comparadas, por âncora, com o antes/depois
publicado pelo sistema. Foram normalizados somente comentários HTML,
hierarquia dos títulos e títulos de abertura que o importador guarda como
metadados. Números, requisitos, proibições e texto das regras não são relaxados.
Não há alteração fora do registro. O catálogo geral `dados.js` permaneceu igual.

`auditar_r53.py` reproduz essa conferência; `corpus.json` registra cada bloco.
A busca foi exercitada para os 497 títulos únicos elegíveis. Ela encontra a
fonte esperada em todos; títulos repetidos, continuações e exemplos exigem
outras verificações e não são certificados por essa contagem.

Correções comprovadas:

- O sincronizador respeita “Fonte corrente R53” antes do título histórico R52.
- Cura/vida temporária recebem Funções e saldo e Formas; Máxima usa a entrada
  integral atual, e Classe 0 conserva sua proibição atual.
- Eco conserva o cabeçalho de nível/espaços, agora no mesmo nível de título dos
  Talentos individuais. A consulta de Mais Um encontra sua Melhoria, apesar das
  palavras comuns no nome, sem transformar conversa casual em pergunta de regra.
- Duas instruções inglesas deixaram de misturar artigos portugueses com “choose”.

## Compatibilidade mecânica

Os formatos antigos não são reinterpretados silenciosamente como R53.
`dados/sistema/legado-r52.jsonl` preserva a fonte usada nas contas legadas de
montagem e trunfos. Seu hash fica no manifesto. Esse arquivo não entra no núcleo
de busca nem no contexto das guias. Os cartões ANALISE 12 continuam usando o
motor R53 separado; o restante reaproveitado passa pelas regressões existentes.

Atualizar o texto do livro não automatiza toda a conferência humana. Aprendizado,
histórico dos marcos, autorização efetiva, compatibilidade narrativa, distribuição
entre alvos e interações de Alma não cobertas continuam com o mestre.
MESTRE VIU não concede aprovação; prosa aprovada não vira benefício numérico.

## Evidências desta rodada

- `pesquisa/validacao/2026-10-21-r53/corpus.json`: comparação integral de fontes.
- `pesquisa/validacao/2026-10-21-r53/busca-titulos.json`: recuperação por título,
  sem modelo.
- `pesquisa/validacao/2026-10-21-publico/PILOTO-NATURAL.md`: amostra real de
  conversa, com orçamento próprio aprovado e encerrado.
- `src/var/testes-publico-21out/`: exportações nativas e snapshots descartáveis,
  ignorados pelo Git. Não confundir com as baterias de 19/20 de outubro.

Suíte completa inicial após migração: 945 executados, 944 aprovados, um online
opcional pulado. Novas regressões adicionais e CI final são registradas no
fechamento desta rodada. Não se contam chamadas simuladas da suíte como chamadas
reais ao modelo.

## Retomada

Confira `origin/main`, a PR desta rodada e o fechamento antes de repetir testes
ou publicar. Para conferir as fontes: `python3 ferramentas/auditar_r53.py --repo
CAMINHO_JJK --saida pesquisa/validacao/2026-10-21-r53/corpus.json`, a partir de
`Closure/`. Para regressões, prepare o núcleo com `ferramentas/empacotar.py` e
execute a descoberta em `Closure/src/`. Não retome o piloto pago: suas 24
tentativas já foram usadas, sem autorização residual.
