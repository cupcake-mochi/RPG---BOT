# R53, testes públicos e publicação · 21/10/2026

Os três acompanhamentos da versão inicial foram executados dentro do escopo
registrado abaixo. A versão estável das Guias é **1.0.1**, já na Discloud.
A Arquivista permanece **1.1.0**: a continuação acrescentou evidências, sem
alterar seu runtime.

## Código, publicação e verificações

- Guias: [PR 69 mesclada](https://github.com/cupcake-mochi/RPG---BOT/pull/69),
  merge `2b906558ba4ad4597d25371e6b6b571ed77db55f`; código `89ed8d9`,
  evidências e manifesto `33a8620`.
- [Versão estável 1.0.1](https://github.com/cupcake-mochi/RPG---BOT/releases/tag/v1.0.1),
  com ZIP, manifesto dos 89 arquivos e soma SHA-256. O tag aponta ao merge acima.
- Discloud: app `1773761486581`, login às 14:58:10 e online em cinco servidores
  às **14:58:14 de Brasília**. Logs sem erro; avisos de dependências opcionais
  de voz permanecem. Recursos não alterados: 700 MB / 0,68 vCPU.
- ZIP: SHA-256 `9e264247d4de1275278ff6f15f91bddf291fc5ee20de655665cde79a269f8cd0`.
  Backup posterior contém os **89 arquivos idênticos** aos hashes do manifesto.
- Suíte final no código/evidências `33a8620`: **953 executados, 952 aprovados,
  um online opcional pulado**. [CI final](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/39647726036).
- Arquivista: [PR 11 documental mesclada](https://github.com/cupcake-mochi/Arquivista-do-Ciclo/pull/11),
  merge `2fb772f2e0b336e1e1d598077ffc98335f6edb1a`. Não exigiu outro deploy;
  runtime `932df0e` da 1.1.0 permanece em execução.

Backups anterior (14:50) e posterior (15:04) foram guardados apenas localmente,
com acesso restrito. `.env` e cadastro de campanhas são idênticos. O SQLite do
bot tem integridade `ok`, mesmas contagens nas 16 tabelas e conteúdo idêntico em
15 delas. A única mudança foi o estado do painel climático ativo: de parcialmente
nublado para poucas nuvens, sem mudar local/configuração. O banco `closure_lab.db`
é idêntico byte a byte. Não publicar backups, bancos ou credenciais.

A única nova variável do aplicativo é `GASTO_EXTERNO_USD=0.156294`, para
contabilizar o piloto aprovado. O teto mensal continua US$ 9,00 ao preço cheio;
não foi ampliado. Console e `GC:status` confirmaram o valor efetivo após o deploy.
Não foram inseridas chamadas artificiais no banco de produção.

## O que foi concluído nesta continuação

1. **Consulta geral R53.** Corpus de 576 blocos; 202 mudanças comparadas ao
   registro oficial (91 adições, 26 remoções, 85 alterações), sem divergência
   não registrada. Os 497 títulos únicos elegíveis recuperam a fonte esperada.
   Corrigidas seleção de fonte para Funções/Formas/Máxima, Eco, Mais Um e leitura
   da edição corrente. Motor legado conserva fonte R52 separada, sem contaminar
   o contexto de consulta atual. [Revisão e limites](../../../docs/REVISAO-R53-POS-1.0.md).
2. **Testes nativos.** Uma cópia real atual da ficha, com estados de Classe 1
   válida, excesso proposital na Classe 1 e mescla de Classe 5 válida. Em cada
   estado, link e XLSX nativo concordam nas 18.393 chaves e no resultado completo.
   A ficha foi deixada incompleta propositalmente; não recebeu aprovação global.
   [Método, valores e limites](NATIVO.md). As baterias anteriores de entidades,
   Liberação, Máxima e custom continuam descritas em seus próprios fechamentos;
   não foram repetidas integralmente nesta rodada.
3. **Arquivista em inglês, de ponta a ponta.** Criação pelo formulário real do
   Discord, arquivo privado nativo `en_US`, proprietário do bot e editor real
   autorizado. Edição no Sheets chegou ao Discord; edição confirmada no Discord
   voltou à mesma linha/ID, revisão 1→2. Voltar ao português não criou outro
   arquivo nem reformatou o inglês. Cadastro fictício removido, sincronização
   desconectada e arquivo na lixeira recuperável. O registro de arquivo gerenciado
   permanece conforme o comportamento normal de desconectar; para repetir esse
   fluxo, restaure a cópia antes. [Relatório da Arquivista](https://github.com/cupcake-mochi/Arquivista-do-Ciclo/blob/main/docs/VALIDACAO-INGLES-DISCORD-2026-10-21.md).
4. **Conversa com modelo real.** 24 tentativas/24 respostas completas, duas
   personagens × dois idiomas × duas bases de lore × três assuntos. Estimativa
   conservadora US$ 0,156294. Nenhuma repetição, fallback ou uso desconhecido.
   [Resultados e ressalvas](../2026-10-21-publico/PILOTO-NATURAL.md). A quantidade
   autorizada acabou; qualquer novo piloto pago exige outra autorização.

## Ensaio depois da publicação

No tópico Testes, pela conta real sem cargo administrativo:

- `GC:ping`: R53/v0.366, 576 blocos, 49 ms.
- `GC:status`: pt-BR/Nova Terra, orçamento US$ 4,67 / 9,00, incluindo US$ 0,16
  externo; 686 chamadas históricas no banco, sem nova chamada de modelo no smoke.
- `GC:f` com o link da cópia nativa: nível 17, dois feitiços, 5 erros e 9
  pendências esperados do restante incompleto. Página 4 mostra C1 3d8/3 PE e
  C5 Dano 6d8 + Cura 4d8/15 PE, ambos VÁLIDO, cor verde. O rodapé mantém o
  veredito global reprovada, com livro R53.
- A conta administrativa selecionou Correções e revisão no mesmo painel criado
  pelo membro; a página 2 foi atualizada e ficou vermelha. Ambos os acessos
  reais foram confirmados, sem permissões administrativas concedidas à secundária.

O XLSX nativo foi conferido pelo leitor offline nesta rodada; não houve novo
upload desse XLSX no Discord após o deploy. As baterias anteriores de anexos
continuam válidas apenas para os casos que registram. Não confundir estes testes
com certificação de toda ficha, de toda combinação de cartões ou de toda a lore.

Após o ensaio, a cópia RPG de QA também foi movida à lixeira recuperável pela
interface do Sheets. As duas cópias novas desta rodada estão encerradas, sem
alterar as planilhas oficiais. Servidor mantido em pt-BR/Nova Terra; Arquivista
em pt-BR, sem sincronização sintética ativa.

## Cobertura restante e retomada

Não há bloqueador conhecido de publicação nos casos exercitados. Continuação
possível, quando solicitada:

- **Código do bot:** observar escrita em uso real e ampliar cenários independentes
  ou corrigir defeito reproduzido. Um erro de ortografia e diferenças de extensão
  da voz foram registrados no piloto, sem prometer texto infalível. A busca por
  título não mede a correção semântica de todas as respostas ao livro.
- **Dados do produtor:** conferir o contrato corrente antes de acrescentar contas;
  entradas não exportadas não podem ser deduzidas do próprio resultado auditado.
  Propostas históricas B47 não reabrem defeitos já encerrados no R53. Oficial e
  Apps Script ficaram intocados nesta rodada.
- **Mestre:** aprendizado, história dos marcos, autorizações reais, requisitos
  livres, narrativa, distribuição entre alvos e interações de Alma não cobertas
  continuam humanos. MESTRE VIU não autoriza; aprovação não cria benefício numérico.

Retomada exata: confira `origin/main`, o tag `v1.0.1` e os fechamentos atuais de
ambos os repositórios; preserve alterações locais. Não reaplique PRs 69/11 nem
repita deploy por documentação. O pacote publicado corresponde ao merge
`2b90655`. Para regressões em ambiente preparado, a partir de `Closure/src/`:
`python -m unittest discover -s testes`. O piloto pago está encerrado; não reusar
seu plano para enviar novas chamadas. Para novo teste nativo, faça outra cópia
sintética autorizada ou restaure explicitamente a cópia de QA da lixeira.
