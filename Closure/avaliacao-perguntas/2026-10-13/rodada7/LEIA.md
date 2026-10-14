# Busca do livro, rodada 7 (seguimento curto)

`proposta/busca_v7.js` = a v6 que está no `modelo.html` + uma regra só. `proposta/aplicar7.py` faz a troca.

**A regra:** em seguimento curto (até 2 palavras próprias, como "e quanto custa?", "e sem correr
antes?", "e a derrubado?", "e no nível 9?"), as duas seções que a pergunta anterior trouxe ganham +10,
mas só as que também têm uma palavra da pergunta nova. Vale também quando a palavra nova é termo do
livro: "correr" depois de salto continua em Saltos, e "derrubado" depois de Lento continua em
Condições leves. "e o bloquear?" depois do Guia continua indo pra Bloquear, porque as páginas do Guia
não falam de bloquear.

| Bateria | Atual (v6 + lorebook de agora) | v7 |
| ------- | ------------------------------ | -- |
| holdout5 | 34/38, papo 0/12 | **38/38**, papo 0/12 |
| todas as outras (bateria, holdout, holdout2, holdout3, holdout4, buracos, rodada 10, conversas 11 a 13) | | iguais |
| conversas reais: papo com livro / regra com livro | 8/129, 52/52 | iguais |

Os 4 que a v7 corrige na holdout5 são seguimentos curtos (w31, w36, w37, w38). Seguimentos das outras
baterias conferidos de novo: "e o bloquear?", "e de 20?", "e no nivel 23?", "e se for 30m?", "e pra entidade?".

**Sobre a medida:** a holdout5 já não é cega (eu corrigi 6 erros dela, e o lorebook de vocês resolveu os
pedidos de Caminho por fantasia). Testei o bônus com +4, +6 e +10; o resultado só muda na holdout5.
Antes de a próxima rodada de conversas, vale outra bateria escrita às cegas pra conferir se a regra
generaliza.

```
cd "Closure Lab/Closure"
python3 ferramentas/pagina_teste/montar_pagina.py /tmp/pagina.html
bash avaliacao-perguntas/2026-10-13/rodada7/rodar.sh /tmp/pagina.html
```
