# Escrita financeira com versões equivalentes

30/10/2026 · PR84 · **escrita e recuperação validadas no caminho observado; não publicado**.
Código `583a95b25167584dc175681a911e407799108a20`; HEAD documental inicial `cf7433c`.

## Código e preparação conferidos

Árvore limpa e branch/remoto iguais antes do ensaio. PR84 aberta em rascunho,
base `codex/carteira-viva-etapa-6`; main `de424478a7a120ecb43bd0c79eb93774d446fae6`.
[CI completo 41055294614](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/41055294614)
aprovado em 30/10 às 09:31:16 Brasília: 1.639 executados/1.638 aprovados/um
opcional pulado, zero falhas, 293,752 s. Logs completos conferidos; nenhuma
bateria completa repetida por este registro documental.

O Sheets fez uma fonte privada nova na mesma conta do consentimento. Uma entrada
fictícia em `FICHA PESSOAL!AW15` diferencia o estado inicial do alvo limpo; não há
alteração de ficha oficial ou de jogador. Não houve chamada ao Apps Script pelo piloto nem execução manual do inicializador.

Ambiente loopback isolado, banco/chave/token de serviço novos, credenciais do app
reutilizadas fora do Git. Logs de acesso desabilitados; PID/batimento e contadores
persistidos por chamada. A intenção da fonte foi gravada antes da cópia pela UI.
O piloto registra de forma durável o consumo antes de cada POST de negócio.
Só permite o `files.copy` da fonte exata com os marcadores esperados e um
`spreadsheets.batchUpdate` de 21 pedidos na cópia identificada. Restante das
escritas bloqueado; OAuth normal e GETs continuam permitidos. Sem aumento de cotas.

Seis provas offline do piloto passaram em 0,433 s: marcador anterior à rede,
cópia única mesmo após reinício, falha de transporte sem reenvio, recusa de escrita
na fonte, resposta financeira HTTP200 descartada com reenvio bloqueado e recusa de
outros métodos. São provas do kit privado, separadas da suíte do produto.

## Execução

Cadastro fictício confirmado por OAuth/Picker próprios, na conta principal do
mantenedor. O usuário concluiu login e o aviso de app não verificado. Nenhum
servidor novo ou mensagem de Discord foi necessário; identidade/cargos foram
consultados no servidor autorizado, sem iniciar Gateway.

1. `copiar_modelo`: **um POST Drive HTTP200, 23,674 s**, com o marcador gravado
   antes da rede. Primeira passagem recusou `VersaoAlterada` em 221,084 s durante
   a coleta, já com a cópia existente. Reinício e retomada da mesma operação
   recusaram outra leitura em 50,751 s. Nenhum segundo POST Drive.
2. A retomada instrumentada registrou apenas observações já feitas, sem GET
   adicional, alteração de cota ou mudança de guarda. Concluiu em 186,581 s:
   cópia identificada, `ref_origem` e `ref_destino` presentes e versões originais
   gravadas. A coleta final observou origem 14 e cópia 10; os números identificam
   só versões desta descartável, não conteúdo ou revisão do sistema.
3. `inicializar_financeiro_celulas`: medição e 21 pedidos do contrato; **um POST
   Sheets HTTP200, 4,737 s**. A resposta foi lida/validada e descartada de propósito
   pelo transporte do piloto. O serviço recusou com `escrita_incerta` em 169,487 s.
   Diário persistido em `enviada`, sem tentativa automática de repetição.
4. Encerramento normal e **processo novo** com a mesma base/chave/operação.
   O mesmo adaptador reconciliou por leitura em 161,725 s, **zero POST Drive/Sheets**.
   Estado final do diário `conferida`, retorno `celulas_conferidas` e
   `financeiro_celulas_conferidas=True`. Recibos originais comparados e intactos.
5. A leitura independente de `FICHA PESSOAL!AW15` confirmou a entrada fictícia
   intacta na fonte e ausente na cópia, sem nota na cópia e com o mesmo formato
   numérico nesse ponto. Duas leituras Sheets HTTP200. Não é prova visual/global
   de todas as abas, nem teste de conteúdo narrativo.

Resultado permanece corretamente limitado: `financeiro_concluido=False`,
`propriedades_apps_script_pendentes=True` e os quatro indicadores gerais falsos
(criação, conferência conjunta, consistência temporal e imagens atuais).

**Limite da equivalência:** nenhuma equivalência adicional ficou registrada na
origem ou no destino desta operação (contadores 0/0). O ensaio valida a escrita
financeira e sua recuperação com o código `583a95b` e a identificação da candidata;
não acrescenta uma prova nativa de registro de equivalência por impressão.
Os testes offline continuam sendo a evidência desse caminho específico. Mudança
no meio da leitura continuou sendo recusada, sem afrouxar G5 para passar o ensaio.

Contagem por fase do piloto, incluindo retomadas, separada da preparação e limpeza:

| Fase | HTTP200 | Drive GET | Sheets GET | Drive POST | Sheets POST |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cópia (três passagens, mesma operação) | 1.193 | 79 | 30 | 1 | 0 |
| Financeiro, resposta descartada | 461 | 29 | 12 | 0 | 1 |
| Reconciliação após reinício | 467 | 30 | 12 | 0 | 0 |

Sem HTTP429 nessas fases. O custo inclui consultas atuais de membro/servidor/cargos
em cada guarda e não é benchmark de desempenho. As durações são de cada passagem,
não uma soma que inclua a espera do usuário. Não repetir um ensaio inteiro só para
produzir outras contagens; investigar um problema por hipótese delimitada.

## Limpeza concluída

**30/10/2026 às 09:55:09 de Brasília.** Processo parado antes da limpeza; porta 8876
livre. Cópia identificada e fonte exatas, privadas/propriedade conferidas e marcadores
da cópia validados, enviadas à lixeira recuperável com GET confirmatório HTTP200
para cada uma. Nenhum arquivo oficial ou de jogador alterado/apagado.

Revogação Google HTTP200. O próprio adaptador financeiro passou a recusar `revogada`;
seis GETs Discord e um POST OAuth na tentativa, **zero Drive/Sheets**. Dados fictícios
removidos: zero personagens, fontes, cópias, diários financeiros, modelos, fluxos,
sessões, conexões ativas e segredos de jogador retidos. Banco e ledger íntegros (`ok`).
Abas próprias fechadas; abas do usuário preservadas. Sem grant ou recurso de teste
ativo para retomar: não restaurar a fonte/cópia nem reutilizar a autorização revogada.

Relatórios/contadores e o kit privado permanecem fora do Git em
`~/.local/share/guias-ciclo/carteira-piloto/etapa7-escrita-equivalente-20261030`.
Arquivos de configuração contêm credenciais do aplicativo e não devem ser
impressos ou copiados para commits, relatórios ou pacotes. Diretório 700/arquivos 600.
Nenhum fonte de produção precisou de correção nesta rodada; registro só documental,
sem nova suíte extensa, pacote, merge ou publicação.

## Limites que permanecem

Mesmo células conferidas não concluem as cinco propriedades Apps Script, os
outros domínios, preservação global, automações ou a proteção contra edição
concorrente do dono. Criar personagem continua bloqueado; etapa 7 parcial e
etapas 8–10 pendentes. Sem merge/deploy, modelo pago, ampliação de escopos ou
alteração do produtor. Esta rodada não publica a Carteira na Discloud.


## Próximo marco

Fechar a etapa 7C por domínios verificáveis, começando pela decisão técnica das cinco
propriedades Apps Script e concorrência do dono. O contrato já distingue essas
pendências: não marcar financeiro completo ou liberar criação só porque as células
passaram. Se a solução exigir produtor, escopo Google ou ativação manual, delimitar
isso separadamente antes de implementar; não ampliar acesso neste piloto encerrado.

Também continuam pendentes `preparada × versão configurada` e `validar_modelo` com
versões equivalentes, os demais domínios, preservação/automações/novo responsável e
prova integral. Etapa 8: operações de edição autorizadas; 9: revisão/carga/integrado;
10: clareza e preparação da publicação. Não tratar o número de etapas como percentual
ou prometer prazo curto enquanto esses contratos não estiverem fechados.
