Cópia do modelo R53 de `cupcake-mochi/Ficha---RPG-JJK@76bc66788fb6f75faa3b778f03939017d9d65420` (Técnica Máxima R67, PR 136; antes `4b22da5`, PR 4).

A conta da Máxima segue a R67: a Forma sai dos dados, os pontos de 8/12/16 pagam só as Melhorias, há vida temporária e a aplicação sem dano vira Efeito Próprio pago pelos dados.
`contextos.json` não mudou: a R67 não alterou modalidade nem classes dos 249 cartões.

- `formulas.py` e `catalogo.json`: idênticos (sha256 conferido em `testes/test_r53.py`).
- `modelo.py`: só os imports viraram relativos ao pacote.
- `formas_custom.py`: só a constante `CAMPOS`.
- `contextos.json`: os 249 cartões (modalidade e classes) extraídos de `montagens_r53.py`/`cartoes_diretos.py`,
  mais `classe0.6` e `classe0.7` (Classe 0, classes `[0]`), que a Prática Cotidiana acrescentou no fim do registro
  (`ficha-v01/pratica_cotidiana.py`, Ficha---RPG-JJK@bc4bd46, 05/11/2026). Conferidos contra o `R53_EDITOR_.contextos`
  do `apps-script/EditorR53.gs` de Ficha---RPG-JJK@78fc37d: 251 ids, iguais a estes. As chaves deles na ANALISE estão em
  `recursos/pratica-cotidiana-campos.tsv`, como opcionais.

Não edite à mão: para uma nova publicação, copie de novo do commit da ficha e atualize os sha nos testes.
