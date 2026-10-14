# Contrato da aba oculta `ANALISE`

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
