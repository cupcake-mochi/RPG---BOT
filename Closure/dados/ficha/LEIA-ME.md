# dados/ficha

- `CONTRATO-ABA-BOT.md`: o contrato da aba oculta `ANALISE` que o bot lê (documento 5, 15/10/2026; formatos 1/2/4).
- `TESTES-FICHAS-14-10.md`: resultado das fichas de teste no Google e a fila de consertos.
- `DIVERGENCIAS-FICHA.md`: onde a ficha diverge do livro (pente fino de 14/10) e o que o bot faz até ela mudar.
- `analise-chaves.tsv`: as 5.381 chaves da aba, geradas da ficha por `ferramentas/ficha_analise.py chaves`. Não edite
  à mão.
- As fichas de teste da fase 3 ficam em `src/testes/dados/ficha_analise_*.xlsx` (só a aba ANALISE, com os valores
  que a própria ficha calculou no LibreOffice; `ferramentas/ficha_analise.py amostra` gera de novo).

- `analise-chaves-v1.tsv` e `analise-chaves-v2.tsv`: contratos antigos preservados para regressão.
- Formato 3: reservado ao trabalho paralelo de CONFIGURAÇÃO, ainda sem integração no bot.
