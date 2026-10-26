# Laboratório da Carteira viva

Prova local da etapa 1, sem chamadas de rede. Não é OAuth implementado,
não é servidor público e não deve ser importada pelo bot de produção.

- `contrato.py`: capacidades separadas e projeção dos campos públicos.
- `prova_local.py`: estados, confirmação, cifra e troca de fonte em SQLite
  temporário. Recebe identidades/metadados já verificados como entradas de
  adaptadores; nos testes esses adaptadores são fictícios.
- `../../src/testes/test_carteira_contrato.py`: cenários positivos e negativos.

Para executar, a partir de `Closure/src`:

```bash
../.venv/bin/python -m unittest testes.test_carteira_contrato
```

Os testes criam bancos e chaves descartáveis numa pasta temporária, removida
ao fim. Não usar caminho de banco de produção. Conexões de prova não são
migração de cadastro nem formato de armazenamento definitivo.

O [contrato](../../docs/carteira-viva/CONTRATO.md) define a implementação futura;
o [relatório](../../docs/carteira-viva/ETAPA-1.md) distingue testes locais de
configuração nativa pendente. Nada deste laboratório entra no ZIP Discloud.
