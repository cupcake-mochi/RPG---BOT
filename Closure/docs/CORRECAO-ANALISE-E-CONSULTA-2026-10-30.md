# Análise de ficha e consulta de montagem — 30/10/2026

## Escopo

Correção independente da Carteira viva, sobre main de42447, na branch
`codex/correcao-analise-clareza`, [PR85](https://github.com/cupcake-mochi/RPG---BOT/pull/85).
Código `e110b4c0fb60a816b75b8dea374497ac82557033`. Sem merge ou publicação nesta rodada.
A etapa 7 e o PR84 permanecem separados e parciais.
Nenhuma ficha oficial ou de jogador foi alterada. Não houve chamada paga.
Dados da ficha investigada não foram adicionados ao Git ou às fixtures.

## Correções

- Talentos: aceita o rótulo `CE 1`, `CE 2` e `CE 3` emitido pelas fórmulas,
  além dos inteiros já aceitos. A conversão ocorre apenas na conferência da
  categoria; nomes, definições e impressões de aprovação continuam literais.
  Categoria diferente do catálogo, categoria fora do limite e nível insuficiente
  continuam sendo erros. Categoria válida não aprova efeitos próprios.
- Cadastros: nome vazio, espaços no início/fim e separador de lista recebem
  explicações distintas. Não remove espaços automaticamente nem reutiliza
  aprovações depois de mudar a identidade.
- Painel em português e inglês: avisos mecânicos mostram o nome do cartão;
  Ampliação explica os campos de Melhorias/Funções/Restrições, Classe 0 explica
  categoria versus desconto, e orçamento mostra a decomposição exportada quando
  os valores finitos e não negativos de custo reconciliam com o saldo negativo.
  Essa conta é identificada como informação da ficha, não uma nova validação.
  Dados ausentes/incoerentes usam mensagem geral. Divergência entre aviso do
  motor e aviso exportado conserva os dois lados, sem mascarar o defeito.
- Lore: remove referência antiga a R52 no aviso da Era. Limita a ressalva sobre
  fatos não registrados à lore; a consulta mecânica continua usando o livro.
- Consulta: pedidos narrativos de adaptar/criar feitiços sem palavras como
  custo/pontos passam a receber fontes de montagem. Continuação mecânica com
  “Compreendo, porém…” preserva o pedido anterior. Não herda essa orientação
  após troca para assunto casual. Tabelas e limites vêm do livro, sem números
  fixos acrescentados ao seletor ou autorização automática de custom.

## Reprodução e limites

O caso relatado sobre adaptar um feitiço para bônus de dano corpo a corpo
selecionava alcance, espaços e concentração. O seguimento isolado selecionava
alcance, Estímulo Muscular e tipos de dano. Nenhum trazia a montagem solicitada.
A seleção era igual com Nova Terra ligada/desligada. Agora a pergunta e seu
seguimento recebem Formas, Pontos e preços e Efeito Próprio nos dois modos e nas
duas personagens; o teste também cobre uma pergunta equivalente em inglês.
Isso comprova as fontes fornecidas, não a qualidade de uma resposta de modelo.
Não houve validação nova no Discord ou inspeção de arquivos instalados.

A leitura privada anteriormente obtida foi reprocessada localmente: oito erros
antes, quatro depois. Sumiram apenas os quatro alertas de categoria textual.
Continuaram o nome com espaço e três avisos mecânicos (Ampliação, Classe 0 e
orçamento). Aprovações reais de servidor não foram carregadas nessa reprodução;
suas pendências não permitem concluir que um mestre nunca aprovou um cadastro.

## Encaminhamento ao produtor

Há referências de origem desatualizadas na coluna C de ANALISE. Exemplo técnico:
a chave `passiva.1.categoria`, na linha 2809, tem fórmula em B que lê
`FICHA AMALDIÇOADA!F392`, enquanto C descreve `FICHA AMALDIÇOADA!F379`.
É uma indicação de localização desatualizada; não é a fórmula lendo F379.
O consumidor calcula por chave/valor, então essa divergência não altera por si
só a categoria, os cálculos ou a autorização. Pode orientar alguém à célula errada.
O limite já possui regressão em `test_r53_definitiva`: mudar C não deve mudar
valores, impressões ou o resultado. A correção do produtor deve revisar a geração
dos metadados após deslocamentos de layout, sem substituir coordenadas no escuro
ou alterar IDs e tipos do contrato. Não corrigir manualmente a ficha do jogador.

O falso positivo `CE 3` versus `3` é resolvido no consumidor; não exige retirar
os rótulos de categoria dos menus da ficha. Os avisos mecânicos restantes são
conferências preservadas, não defeitos comprovados das fórmulas do produtor.

## Validação

- Dez regressões novas passaram (18,359 s na execução final direcionada).
- Seleção de fontes: 497/497 antes e depois, nenhuma regressão.
- Caso de adaptação/seguimento: QuickJS e Node produziram entradas idênticas
  nas duas personagens e nos dois modos de lore (quatro comparações).
- Núcleo e ZIP regenerados; 91/91 arquivos iguais aos fontes. ZIP ignorado pelo
  Git, sem ambiente, bancos ou dados de jogador: 1.817.216 bytes,
  SHA-256 `a7d89feb72cf53cb500aee86c6c6aca4c4e661e3733d58fad241a8ba358aed81`.
- Primeira suíte completa: 986 testes, um opcional pulado; 29 falhas de
  asserção investigadas. Vinte e oito eram subcasos do teste que ainda exigia
  literalmente R52; a expectativa foi atualizada para o livro do contexto,
  preservando a separação entre lore e mecânica. A outra revelou que o novo
  formato alcançava avisos de cadastro fora do escopo; o formatador foi
  restringido aos três problemas de nome, sem alterar aquele teste.
- Após os ajustes, 34 testes direcionados de clareza, inglês e lore passaram
  em 35,231 s. A suíte completa final passou no
  [CI41156361663](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/41156361663),
  código `e110b4c`, em 30/10 às 22:43:13 (Brasília): 986 executados,
  985 aprovados e um opcional pulado, sem falhas, em 227,759 s.
  O fechamento posterior altera somente documentação, sem repetir suíte/pacote.

## Continuidade

Revisar a PR desta branch e integrar separadamente da Carteira viva. Não há
publicação autorizada nesta rodada. Antes de publicar: backup do app existente,
verificação do conjunto integrado, Commit sem sobrescrever ambiente/bancos,
conferência dos arquivos instalados e teste de painel/consulta no Discord.
Respostas reais de modelo só com autorização de quantidade/custo aplicável.
