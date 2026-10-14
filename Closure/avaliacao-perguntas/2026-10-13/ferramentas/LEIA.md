# Ferramentas de depuração da busca

Rodam o JS da própria página no Node, sem navegador. Use de dentro de "Closure Lab/Closure".

- `node porque.js PAGINA.html "pergunta||mensagem anterior||mais antiga"`: mostra por que a busca abriu (filtros), as palavras usadas e as 6 seções com maior nota. Numa pergunta de seguimento, a linha de filtros pode vir da chamada interna da pergunta anterior.
- `node termos.js PAGINA.html "pergunta"`: quais termos do mapa do livro (índice, glossário, tabela, título) a pergunta cita.
- `node causa.js PAGINA.html avaliacao-perguntas/2026-10-13/rodada2/bateria/conversas.json`: por que cada fala de papo puxou livro.
