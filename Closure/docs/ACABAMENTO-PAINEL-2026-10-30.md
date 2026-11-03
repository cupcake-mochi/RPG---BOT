# Acabamento após conferir o painel no Discord

> Fechamento posterior: integrado e publicado em 30/10/2026. Consulte [publicação R60](PUBLICACAO-R60-2026-10-30.md) para o runtime, testes finais e limites. As etapas de preparação abaixo permanecem como histórico.

A publicação dos PRs85/86 em `2ff90a1` foi validada com uma ficha XLSX totalmente sintética: três erros e 17 pendências, os mesmos do ensaio local. O teste visual mostrou dois problemas de apresentação restantes: rótulos como `custom · 1 · campo · origem` e repetição da instrução completa de recálculo em vários resultados vazios.

Esta revisão só muda apresentação em português e inglês:

- Cadastros numerados mostram “Cadastro próprio N” e o nome do campo; a Origem associada aparece como “Origem vinculada”.
- Refino, Classe 0 gratuita, Iniciativa, ataques, conjuração, deslocamento e prazo Morrendo têm rótulos legíveis e acentuados.
- O item sem resultado informa a ausência, o valor calculado pelo bot e a espera do recálculo. A orientação geral sobre novo XLSX, nova análise e preservação de fórmulas fica no resumo, sem repetir o parágrafo inteiro em cada item.

35 testes de mensagens, inglês e painel passaram, incluindo cores, limites e preservação dos resultados. As contas, severidades, registros e aprovações não mudaram. Nenhuma ficha real foi alterada. A publicação definitiva e seus resultados ficam no registro de publicação e no topo da fila.
