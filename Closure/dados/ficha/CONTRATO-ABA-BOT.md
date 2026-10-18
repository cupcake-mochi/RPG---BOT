# Contrato vigente · B47 formato 11 · 18/10/2026

Requisição CSV informa `headers=1`: a ANALISE tem uma linha de cabeçalho e
colunas de texto. Inferência automática pode absorver registros como rótulos;
o limite do parser continua preservado. CSV/XLSX atuais foram relidos com
8.190 chaves e zero diferenças, sem escrever na oficial. Trilha custom usa a
BASE DO LIVRO válida/aprovada nas contas de Famílias e extras; Nenhuma não
herda. Troca fixa preserva o valor mesmo com conta-base incompleta, sem apagar
pendências; especialização inválida não certifica bônus/treinos dependentes.
O parâmetro e o risco de inferência em colunas textuais estão descritos na
[documentação do Google](https://developers.google.com/chart/interactive/docs/spreadsheets).

Contas derivadas, efeitos e herança foram ampliados na continuação da integração.
Não há novos campos exigidos além do contrato entregue. Seletores pessoais,
inventário e resultados de TR ausentes estão discriminados em
[LACUNAS-PRODUTOR-B47.md](LACUNAS-PRODUTOR-B47.md); resultados agregados não
substituem essas entradas. Formas apenas renomeadas conservam as regras da base;
alterações estruturadas usam o motor custom e mantêm explícitas suas limitações.

Restrição custom embutida é dependência da Forma: precisa de definição válida e
aprovação própria, e sua assinatura entra na aprovação da Forma. A Família
custom usada pela Forma também exige aprovação própria. Frequência,
repetição e limite de Condições Pesadas não dependem de avisos exportados.
Distribuição incompleta/incompatível da entidade bloqueia suas contas
dependentes. CD de Controle usa saldo independente quando disponível;
descartar dano não compra bônus. As reproduções do produtor permanecem no
documento de lacunas, sem alteração da ficha oficial.

Menores publicadas usam também o requisito estruturado `exige` do catálogo:
Receptáculo respeita Coexistência/Conflito e Descendente respeita o clã escolhido.
Isso vale nas duas vagas, na rota Sem Técnica e em Origem custom com base.
Marcante vazia é informação insuficiente; uma marcante incompatível é divergência.
Descrições editadas pelo jogador não substituem esses requisitos. Efeitos inválidos
ou duplicados bloqueiam a conta dependente de CD/ataque sem interromper a análise.
CSV truncado ou com campo além do limite recebe erro de leitura; aspas e quebras
de linha válidas continuam preservadas literalmente.

O bot integra a ANALISE 11 entregue em `ccbd053c8f7e68f8b4ac223f721b309111d2dcc0`.
Contrato, mapa de campos, colisão do formato 4, cobertura, limites e cadastro de
aprovações estão em [INTEGRACAO-B47.md](INTEGRACAO-B47.md). O manifesto completo
por chave/parte/origem fica em `src/closure_bot/recursos/b47-campos.tsv`.

- Leitura por chave, sem depender de ordem, contagem exata ou endereço antigo.
- Nomes/textos literais são preservados; números e caixas usam tipos semânticos.
- Duplicatas, erro de fórmula B47 e fórmulas XLSX sem cache são diagnosticados.
- Regras e aprovações vêm do cadastro confiável do servidor no bot.
- Ausência, vazio, zero e falso são distintos. Exportação incompleta não certifica contas.
- Formatos 1/2 e variante TR-v4 comprovada permanecem compatíveis; 4 de campanha
  não é equivalente ao TR-v4. A B47 não contém as 485 adições exclusivas dele.
- Aprovação integral nunca é mostrada com partes relevantes não conferidas.

As seções seguintes são **histórico do contrato**, preservado para explicar
fixtures e compatibilidade. Suas contagens/estados não substituem a versão vigente.

# Contrato da aba oculta `ANALISE`

> **Versão documental 5, 15/10/2026.** O formato 4 amplia para **5.381 chaves**:
> 4 cabeçalhos, 3.398 entradas, 1.563 resultados e 416 avisos. Preserva as 4.896 chaves do
> formato 2, com a mesma célula, parte e fórmula; só `formato.versao` muda no prefixo antigo.
> O bot aceita 1, 2 e 4. **O formato 3 está reservado à implementação paralela de CONFIGURAÇÃO**;
> esta exportação 4 deriva do formato 2 e não incorpora CONFIGURAÇÃO/Bônus. A numeração não
> significa que o bot já interprete aquela aba. Não aceitar 3 silenciosamente nem substituir a
> exportação do outro trabalho por esta. A integração deve unir chaves e regras, escolher uma versão
> final única e regenerar os testes/contratos antes de liberar a ficha consolidada.

## Ampliação do formato 4

- `pericia.<nome>.atributo/ajuste/bonus`, `oficio.<nome>.atributo/ajuste/bonus`,
  `tr.<nome>.atributo/ajuste/bonus`: escolha e Buff/Debuff separados do resultado.
- `invocacao.N.tr.<nome>.bonus` e `invocacao.N.pericia.K.bonus`: resultados.
  As antigas `invocacao.N.buff.pericia.K` apontam para os mesmos resultados: ficam preservadas,
  mas **não são ajustes independentes e nunca devem ser somadas como Buff**.
- `equipavel.N.nome/quantidade/grau/volume` e `item.N.nome/quantidade/volume`: posições completas.
  Nos seis equipáveis de menu, Volume é resultado; nas linhas livres, entrada declarada.
- `carga.ajuste_limite`, `carga.total/limite`: ajuste separado dos resultados.
- `invocacao.N.carga.item.K.nome/volume` e `carga.total/limite`: Volume de cada linha armazenada
  é o total declarado; não há quantidade exportada para multiplicar de novo.
- Lista atual gerada em `analise-chaves.tsv`; arquivos `analise-chaves-v1.tsv` e
  `analise-chaves-v2.tsv` conservam os contratos antigos. Nenhuma das nove abas anteriores
  mudou neste incremento de exportação; XLSX e Apps Script foram regenerados pelo gerador.

> **Versão documental 4, 14/10/2026.** O formato 2 amplia a exportação para **4.896 chaves**:
> quatro de cabeçalho, 3.115 entradas, 1.361 resultados e 416 avisos. Preserva todas as 2.650 chaves
> anteriores, com a mesma parte e célula. O bot aceita os formatos 1 e 2; uma ficha antiga continua
> recebendo conferência parcial nas contas que dependem das entradas novas. O histórico da versão 3 segue abaixo.

## Ampliação do formato 2

- `tecnica.familia.*`: estado de cada uma das nove Famílias; também Regra, Descrição, Selo textual, atributo
  escolhido, rota e Regra Própria. Texto livre de Selo não é um requisito mecanicamente certificado.
- `zero.N.*`, `maxima.*`, `dominio.*`: entradas e resultados antes ausentes. Carta de Classe 0 sem nome ou peças
  não conta como preenchida só porque mostra os dados-base da progressão.
- `invocacao.N.atributo.<nome>.base/buff/total`: entradas separadas dos atributos, sem perder posições vazias.
- `invocacao.N.buff.*`, `atributo_acerto`, `atributo_fisico`, `tr_treinado`, `equipamento.N`, `pericia.N`,
  `talento.N`, `talento_extra.N`: escolhas e ajustes que o cálculo independente precisa ler.
- `invocacao.N.familia.1/2/3/4/5`: Livre; Livre da Principal; aberta; aberta; aberta da Trilha, respectivamente.
  A lista antiga `familias` permanece compactada e não serve para reconstruir essas posições.
- Textos, resolução escolhida e tipo de dano das cartas de entidades; registro dos trunfos da domada.
  Exportar um campo não significa que o bot já confira todo o seu efeito: cobertura em `ENTRADAS-FALTANTES-ANALISE.txt`.
- Naquela etapa a lista era `analise-chaves.tsv`; hoje está arquivada em `analise-chaves-v2.tsv`.
  Para gerar a lista atual, use `ficha_analise.py chaves` com o XLSX ou o JSON de `monta.py --exportar-analise`.
  O XLSX e `apps-script/Analise.gs` foram regerados na branch `codex/analise-completa-v2` do gerador.

### Aquisições no formato atual

As posições `passiva.1` a `passiva.5` são os cinco lugares pagos do gerador; `passiva.6` a
`passiva.12` são os sete lugares de Leque. O bot usa essa organização para a conta e lê Categoria/nível
pelo catálogo, sem confiar no custo exibido. Categoria declarada diferente da entrada conhecida é correção.

Talentos gratuitos da Origem ainda não têm posição/vinculação própria. O bot não escolhe quem foi
recebido assim: admite as possibilidades elegíveis de CE1 sem duplicação, verifica apenas excessos
inevitáveis e declara a aquisição/total não certificados. `origem.ce4` é separado dos cinco pagos.
A Regra Própria e `dominio.degrau` também são separados e consomem seus custos totais atuais.

Leque e Coexistência concedem aplicações, não vagas livres para Talento pago, Domínio ou invocação.
As posições ausentes numa exportação parcial não são convertidas silenciosamente em escolhas vazias;
nesse caso o bot não certifica a ocupação completa. Nenhuma chave ou versão foi alterada nesta leitura.

> **Versão 3, de 14/10/2026.** A ficha ganhou a aba de verdade (B47, fase 1, commit `dbdf1d4` do gerador da ficha),
> testada no Google Sheets, e o desenho é dela. **O que mudou da versão 2:**
> - **o nome da aba:** `ANALISE`, sem acento (decisão do Mizuki), no lugar de `BOT`;
> - **quatro colunas** (chave · valor · célula · parte) no lugar de campo · valor · observação;
> - **as chaves:** 2.650, geradas da própria ficha, no lugar da lista escrita à mão. Os nomes mudaram (`vida_max`,
>   `atributo.forca.base`, `origem.menor_1`...), e não existe mais `versao_ficha`: a versão do formato é `formato.versao`;
> - **sim/não virou 1/0**, e a coluna de valores sai toda como texto;
> - **a leitura também pelo link** da planilha aberta (CSV da aba), além do `.xlsx` baixado.

## A fonte

- **A aba ANALISE da ficha é o contrato.** Quem a monta é `ficha-v01/analise.py`, no gerador da ficha; o desenho e o
  sentido das chaves estão no `ESQUEMA-ANALISE.md` (`Planejamento-ficha/B47-analise-e-configuracao/`), e o plano
  inteiro, com "A rota da validação", no `PLANO.md` da mesma pasta.
- **A lista de chaves que o bot conhece** está em [`analise-chaves.tsv`](analise-chaves.tsv) (chave, parte, célula),
  gerada por `ferramentas/ficha_analise.py chaves FICHA.xlsx|LINK`. Não edite à mão: se a ficha mudar, gere de novo.
  O teste `test_contrato_tem_as_mesmas_chaves_da_ficha` compara essa lista com a ficha de teste.
- **Os nomes dos campos são os da ficha.** Os da versão 2 (`origem.ramo`, `origem.rota`...) não existem: o ramo e o
  Sem Técnica vêm junto da Origem ("Restrição Celestial · Sem Energia", "Latente · Sem Técnica"), e a ficha não tem
  campo de rota.

## Formato

- Aba `ANALISE`, oculta. Linha 1: `chave · valor · célula · parte`. Linha 2 em diante: os dados.
- **Partes:** `cabeçalho` (4 chaves), `entrada` (1.629: o que o jogador escolheu), `resultado` (601: o que a ficha
  calculou) e `aviso` (416: o que a ficha já marca).
- **Valores:** saem como texto, porque o CSV do Google escolhe um tipo por coluna e misturar número com texto apagava os
  textos. O bot converte (`ficha_leitor.normaliza`): número com vírgula ou ponto decimal, caixa de marcar como `1`/`0`,
  e vazio como "não preenchido". O texto de escolha ainda não feita ("Escolha seu Caminho") vale como vazio.
- **Célula:** de onde o valor saiu na ficha (`FICHA!D59`, `'FICHA PESSOAL'!AH64`), pra o mestre achar.
- **Lista:** feitiço, invocação, item e afins levam o número do item na chave (`feitico.7.pecas`), e as partes de um
  mesmo campo vêm juntas por ` · `.
- Chave não é reaproveitada com outro sentido: se a regra mudar, entra chave nova e `formato.versao` sobe.

## Cabeçalho

| chave | o que é | hoje |
| ----- | ------- | ---- |
| `formato.versao` | a versão deste formato | `1` |
| `ficha.versao` | a versão da ficha (`DADOS!B1`) | `1.0` |
| `ficha.sistema` | o sistema (`DADOS!F1`) | `Ciclo Maldito` |
| `ficha.livro` | o livro de onde a ficha saiu | `Ciclo Maldito R51` |

## Como o bot lê

1. **Entrada:** o `.xlsx` baixado do Google (Arquivo > Fazer download > .xlsx), lido com openpyxl e `data_only` (o
   Google grava o resultado das fórmulas), ou o link da planilha aberta pra leitura (CSV da aba pelo gviz, sem conta).
   A ficha que sai do gerador sem passar por uma planilha não tem os valores e é recusada com aviso.
2. **Versão:** `formato.versao` que o bot não conhece recebe aviso, sem correção.
3. **O bot nunca acredita na ficha.** O jogador é dono da cópia e pode mexer em tudo, inclusive nesta aba. Então:
   - as **regras da campanha** vêm do cadastro do bot, nunca da ficha (hoje só o padrão: o livro);
   - o **conteúdo custom** é conferido contra o registro dos aprovados, por impressão digital do texto (estrutura pronta;
     a aba CONFIGURAÇÃO é a fase 2 do B47);
   - as **contas** são refeitas a partir das entradas e comparadas com os resultados;
   - os **avisos** da ficha entram só como primeiro filtro.
4. **Resposta:** só no chat. O bot não escreve na ficha.

O código: `src/closure_bot/ficha_leitor.py` (leitura), `src/closure_bot/ficha_corretor.py` (conferência, sem IA) e
`src/closure_bot/cogs/ficha.py` (o comando está ligado).
