# dados/sistema: cópia gerada, não editar

Tudo aqui sai do repositório do sistema ([`cupcake-mochi/JJK---Project`](https://github.com/cupcake-mochi/JJK---Project))
pelo `ferramentas/sincronizar.py`. Editar à mão cria uma segunda fonte da regra, e a
próxima sincronização apaga a edição. Se uma regra está errada, o conserto é no repositório.

| Arquivo | O que é | Vem de |
| ------- | ------- | ------ |
| `livro.jsonl` | Um bloco do livro por linha: `ancora`, `capitulo`, `capitulo_titulo`, `titulo`, `titulos`, `acesso`, `texto` | `sistema/05-material/livro/ciclo-maldito-r41/LIVRO-COMPLETO.md` |
| `catalogos.json` | Perícias, ofícios, Caminhos, Trilhas, Origens, TRs, atributos, Famílias e constantes do nível 2 | `sistema/05-material/gerador-ficha/dados.js` (conferido pelo `conferir-ficha.py` do repo) |
| `MANIFESTO.json` | Versão do sistema, edição do livro, commit, data e contagem de blocos por capítulo | o próprio sincronizador |

## Atualizar

```bash
cd "Closure Lab/Closure"
python ferramentas/sincronizar.py --repo CAMINHO_DO_CLONE_DO_JJK---Project
```

Precisa de Python 3 e Node. O script recusa o clone velho (o que não tem
`## Nove lições` no README) e falha sem gravar nada se o livro mudar de forma.
Depois de rodar, confira se o `MANIFESTO.json` tem a versão que você esperava.
