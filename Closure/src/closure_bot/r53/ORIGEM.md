Cópia do modelo R53 de `cupcake-mochi/Ficha---RPG-JJK@76bc66788fb6f75faa3b778f03939017d9d65420` (Técnica Máxima R67, PR 136; antes `4b22da5`, PR 4).

A conta da Máxima segue a R67: a Forma sai dos dados, os pontos de 8/12/16 pagam só as Melhorias, há vida temporária e a aplicação sem dano vira Efeito Próprio pago pelos dados.
`contextos.json` não mudou: a R67 não alterou modalidade nem classes dos 249 cartões.

- `formulas.py` e `catalogo.json`: idênticos (sha256 conferido em `testes/test_r53.py`).
- `modelo.py`: só os imports viraram relativos ao pacote.
- `formas_custom.py`: só a constante `CAMPOS`.
- `contextos.json`: os 249 cartões (modalidade e classes) extraídos de `montagens_r53.py`/`cartoes_diretos.py`.

Não edite à mão: para uma nova publicação, copie de novo do commit da ficha e atualize os sha nos testes.
