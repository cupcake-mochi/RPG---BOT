# Financeiro: leitura individual × agrupada no Google

29/10/2026 · PR 84 · **mesma leitura nos dois modos, no domínio financeiro; ensaio encerrado**.
Código testado `49783ce0495b4ac6a7c9d1e8ba7b61cc100ffdb1`, sem alterações locais em `Closure/src`.
Limpeza concluída às 09:45 de Brasília, sem recursos ativos do piloto.

## Desenho

Diagnóstico da origem, intenção preparada, domínio **financeiro**, duas coletas sob a
mesma chave HMAC: **a primeira página por página e a segunda em lotes**. A alternância
foi feita só no runner privado (troca do modo do leitor a cada chamada de `paginas`),
sem mudar o código do bot. Assim a comparação do diagnóstico vira uma prova direta de
que os dois modos devolvem o mesmo conteúdo no Google real.

Cópia nova da oficial Ciclo pelo "Fazer uma cópia" do Sheets, na conta do consentimento,
nome **QA Carteira — financeiro agrupado — DESCARTÁVEL — 29-10-2026**, privada.
Piloto loopback novo (banco/chave/token novos fora do Git), Discord `identify` e Google
`drive.file`; o aviso de app não verificado foi aceito pela própria pessoa. Só a
descartável escolhida no Picker; personagem fictício na base isolada; escrita
Drive/Sheets bloqueada no transporte.

## Primeira tentativa: recusa correta na conferência do modelo

Recusada em 10,7 s com `ErroProvedor('conflito')` em `validar_modelo`: os metadados do
Drive mudaram entre o início e o fim da conferência (cerca de 7 s), cerca de dois minutos
depois de criar e renomear a cópia no editor. Nenhuma página financeira lida; nada
gravado. A guarda funcionou. Causa exata não provada (hipótese: processamento da cópia
recém-aberta no editor). **Uma** nova tentativa manual, 75 s depois, sem nenhuma mudança.

## Resultado da segunda tentativa

- Duas amostras completas **25/25 páginas**, cobertura compatível, 25 páginas comparadas.
- **Zero páginas com mudança** em literais, fórmulas, resultados, notas e formatos
  numéricos entre a coleta individual e a agrupada.
- Versões iniciais iguais, nenhuma divergência durante nem antes/depois das coletas.
- Diário preparado intacto; quatro indicadores de liberação falsos; zero HTTP429 ou erro.
- Fluxo 245,476 s, incluindo a conferência do modelo do servidor.

Páginas do financeiro: 25 faixas = 18 pequenas das guardas + 7 dos livros.

| GETs Sheets das páginas | Individual | Agrupado |
|---|---|---|
| Chamadas | 25 (uma faixa cada) | **11** (4×4, 1×3, 6×1) |
| Soma do tempo dessas chamadas | 73,3 s | 29,6 s |
| Maior chamada | 3,5 s | 3,2 s |

Os seis lotes de uma faixa são os livros, que já enchem o teto de 4.096 células.
No total da fase de cada amostra (o corte de fase acontece quando a leitura das páginas
começa, então inclui um pouco da preparação vizinha): individual 325 HTTP200 (244 membro,
55 Drive, 26 Sheets) e agrupada 142 HTTP200 (107 membro, 24 Drive, 11 Sheets).
Tempos são de uma execução cada, não benchmark.

## Encerramento

Runner parado; porta 8876 livre. Descartável na lixeira **recuperável** (PATCH e GET
HTTP200, `trashed=true`). Revogação Google HTTP200; nova chamada recusada `revogada`
(OAuth HTTP400) com zero Drive/Sheets. Zero personagens, fontes, cópias, financeiro,
modelos, fluxos, sessões, conexões ativas e segredos; banco e ledger `ok`.

## O que conclui e o que não conclui

Conclui que, no caminho observado, a leitura agrupada do **domínio financeiro** devolve o
mesmo conteúdo que a individual, com menos da metade das chamadas ao Sheets. É a
evidência que faltava para ligar `agrupar=True` em `financeiro_servico` (a medição já
está pronta e testada em `49783ce`).

Não prova a escrita financeira, a reconciliação sem segundo POST, as propriedades Apps
Script, a concorrência com o dono nem os demais domínios. Auditoria segue individual.
Criação bloqueada; sem modelo pago, escopo novo, Gateway, merge ou Discloud; oficial,
produtor e fichas de jogadores intactos.
