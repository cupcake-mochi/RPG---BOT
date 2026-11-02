# Candidatas e mudanças de versão

28/10/2026 · PR 84 · implementação offline, não publicada.

## O que o ensaio demonstrou

O ensaio anterior observou mudanças no alvo e na fonte, mas não demonstrou suas
causas. A documentação do [campo version do Google Drive](https://developers.google.com/workspace/drive/api/reference/rest/v3/files)
informa que ele acompanha mudanças no servidor, inclusive não visíveis ao usuário.
`headRevisionId` só existe para conteúdo binário; não é substituto disponível nas
planilhas nativas. Isso não autoriza tratar a mudança observada como inofensiva,
recálculo ou cache. O bot continua recusando versões divergentes.

## Etapa de candidata

Novas intenções usam **protocolo interno de cópia 2**, dentro do envelope cifrado
existente. Schema 9, ledger 2, marcador Drive `cv_protocolo=1` e contrato financeiro
v1 permanecem iguais. Não há migração de banco nem alteração do produtor.

| Estado persistido | Significado |
| --- | --- |
| preparada | Intenção ainda não enviada; o envio exige a versão da origem registrada |
| enviada, sem candidata | Resultado incerto: só buscar o marcador privado |
| enviada, com candidata | Arquivo e versão da primeira observação fixados; não é inicialização |
| identificada | Fonte reconferida e candidata reobservada sem mudança; recibo imutável |

A origem é conferida antes da busca em retomadas, evitando ler um destino quando
o modelo já mudou. A candidata precisa ser própria, privada, com o marcador
esperado, distinta da fonte e ainda não cadastrada em qualquer servidor. A primeira
observação fixa arquivo/versão. Depois da conferência da origem, há outra observação
do destino antes de registrar o recibo. Mudança nesse intervalo mantém a operação
pendente; a retomada não adota outro arquivo ou versão e nunca repete o POST.

Intenções históricas sem campo de protocolo continuam compatíveis. Recibos já
identificados conservam a versão original. Protocolos desconhecidos são recusados.
O cadastro de personagem e `criar_por_modelo` não foram liberados.

## Diagnóstico privado

Até 12 observações cifradas por operação: etapa, versão de referência, observada,
primeiro/último horário e contagem de repetições. Não armazena conteúdo de células,
notas, nomes de arquivos, URLs, tokens ou mensagens arbitrárias. Campos aceitam
somente tipos internos, etapas fechadas e versões decimais como texto, sem converter
contadores grandes para float. Não há endpoint novo ou exposição desses dados no painel.

Observações repetidas são agrupadas. Gravar diagnóstico não renova a retenção da
cópia. Rotação/backup e exclusão usam o envelope e o tombstone existentes; não
ressuscitam candidatas excluídas nem autorizam replay ao restaurar.

Esse histórico **não é um veredito**. Uma versão posterior à escrita pode ser
esperada; autorização e conferência continuam nos controles anteriores. Só esse
campo técnico fica fora do hash de contexto financeiro. Candidata, versões,
origem, destino, modelo, autorização e demais campos continuam vinculados.

O leitor agora distingue uma mudança numérica de versão de outros erros de grade,
sem incluir os valores na mensagem pública. O serviço registra a divergência exata.
Uma cópia já alterada antes da preparação financeira é recusada antes de ler células.
Após envio, a reconciliação continua permitindo apenas leitura; sua versão pode ser
posterior, mas as entradas precisam corresponder ao plano cifrado original.

## Validação

100 testes direcionados distintos aprovados: lote inicial 97 em 56,582 s,
dois adicionais em 0,143 s e regressão nova de restauração, incluída na
bateria final de 32 cópias em 6,489 s (31 casos sobrepostos). São 19 casos novos, com cópia, financeiro,
grade, isolamento, valores acima de 2^53, histórico limitado, retenção, rotação,
backup/restore e exclusão global. Duas reproduções contra 701af66 falharam como
esperado antes da correção: candidata alterada durante a conferência da origem era
identificada; cópia já alterada consumia toda a leitura de células antes da recusa.
Uma revisão adicional confirmou que uma candidata já observada também não
pode ser trocada em intenção legada: falhou antes do ajuste e passou depois
em 0,091 s. Expectativas não foram relaxadas. As fixtures válidas passaram a executar a etapa
obrigatória de candidata. Pacote ignorado regenerado e
comparado: 90 arquivos, CRC/fontes iguais, sem Carteira/env/bancos/campanha;
SHA256 `27e0f7c28fcf8077ee53a5c22ba4a93e44562112f000c9681d12e7ad42471352`. Não publicado.

Uma revisão posterior reproduziu mais um caso no código 253bfe0: restauração de
um backup sem versão observada da origem podia identificar uma cópia tardia
usando a versão configurada como substituta. Agora serviço e banco exigem a
versão originalmente registrada antes da localização/identificação. Falhou antes
da correção e os 32 testes de cópia passaram depois; não houve expectativa relaxada.
O [CI 40797575755](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40797575755)
passou em 253bfe0 (1.532 executados, um opcional pulado, 353,420 s), antes dessa
correção. Por isso foi necessária outra suíte no código final.

Código final `eeb78f98a63f355e16c8b06dde24c80e4108ca80`: o
[CI 40798497466](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40798497466)
passou em 28/10 às 22:13:05 Brasília. Foram **1.533 executados, 1.532 aprovados,
um opcional pulado, zero falhas**, em 297,175 s. O fechamento posterior é só
documental (`[skip ci]`), sem nova suíte, pacote ou publicação.

## Próximo diagnóstico implementado offline

[Comparação de leituras](DIAGNOSTICO-GRADE-2026-10-28.md): ferramenta transitória
separa diferenças de literais/fórmulas/resultados/notas/formatos numéricos nas
páginas aceitas pelo leitor estrito. Não integra inicialização, não adota versões
e ainda não foi composta/executada no piloto real. Não é fingerprint global.

## O que ainda falta

Este bloco fecha o registro e a ordem das verificações. **Não resolve a causa das
mudanças nativas nem oferece prova de conteúdo estável.** Não renovar versões ou
apagar diários para prosseguir. Uma candidata recusada não é descartada ou cancelada
automaticamente; encerramento e revisão da fonte mutável precisam de protocolo próprio.

Antes de novo OAuth/ensaio, fechar o diagnóstico controlado da origem/cópia e o
contrato de preparação de conteúdo. Qualquer fingerprint proposto precisa declarar
cobertura de entradas/fórmulas/notas/formatos e limites de imagens/propriedades;
resultado calculado ou versão Drive não substituem essa prova. Nada disso foi
implementado ou presumido aqui. Cinco propriedades Apps Script e demais domínios,
CAS contra edição simultânea, preservação global, automações/responsável e prova
integral continuam pendentes. Criação bloqueada e quatro indicadores falsos.

Nenhuma chamada Google/Discord, ficha oficial/jogador alterada, scope novo, Apps
Script, modelo pago, Gateway, merge ou deploy nesta rodada. Sol Alto; revisão Médio.
