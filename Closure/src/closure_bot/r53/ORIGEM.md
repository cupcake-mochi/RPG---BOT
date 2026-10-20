Cópia do modelo R53 de `cupcake-mochi/Ficha---RPG-JJK@4b22da5420263a8885e28a508cbc39938dd9d9da` (PR 4).

- `formulas.py` e `catalogo.json`: idênticos (sha256 conferido em `testes/test_r53.py`).
- `modelo.py`: só os imports viraram relativos ao pacote.
- `formas_custom.py`: só a constante `CAMPOS`.
- `contextos.json`: os 249 cartões (modalidade e classes) extraídos de `montagens_r53.py`/`cartoes_diretos.py`.

Não edite à mão: para uma nova publicação, copie de novo do commit da ficha e atualize os sha nos testes.
