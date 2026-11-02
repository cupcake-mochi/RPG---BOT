# Concorrência com a edição do dono · 02/11

Decisão de contrato, sem mudança de comportamento. Fecha o item de concorrência
do critério da etapa 7; não libera a criação, porque os demais itens continuam
pendentes (eventos reais, atestado de ativação, demais domínios, tempo de
preparo e prova integral).

## Fato externo

O [`spreadsheets.batchUpdate`](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/batchUpdate)
é atômico, mas o corpo do pedido não tem campo de precondição (versão, revisão
ou etag) e a página avisa que as mudanças podem ser alteradas por mudanças de
colaboradores. Não existe compare-and-swap nesta rota. O `LockService` do Apps
Script só trava outros scripts, não a edição manual. A fila local (`fila.py`)
ordena só o trabalho do próprio bot.

## Decisões do mantenedor

1. As cópias normalmente são feitas pelo jogador, sem o bot, e compartilhadas
   com ele depois. O dono tem acesso o tempo todo, então a corrida não é
   fechada por controle de acesso.
2. O bot só escreve numa ficha com permissão ou quando solicitado. O comando
   do jogador no Discord basta como solicitação, sem confirmação extra.
3. Separar áreas de escrita (bot só lançando numa aba própria) foi considerado
   e recusado, porque muda o contrato do produtor.
4. **O risco residual da janela entre a última conferência e o POST é aceito.**
   Ele precisa aparecer no guia do recurso e na resposta ao jogador quando o
   bot escrever.

## Regras de toda escrita

| Regra | Conteúdo |
|---|---|
| A · Permissão | Nenhuma escrita sem solicitação identificada (quem, qual ficha, o quê), válida só para aquela operação. |
| B · Escopo mínimo | Células nomeadas, máscaras `userEnteredValue`/`note`; sem `*`, intervalo largo ou fórmula nova. |
| C · Antes | Reobservar logo antes do POST; se mudou, recusar sem enviar e sem repetir sozinho. |
| D · Depois | Reler e comparar; divergência é informada, nunca "corrigida" pelo bot. |
| E · Incerto só lê | Timeout, 429 ou cancelamento depois de `enviada` nunca reenviam. |
| F · Fora de células | Missão, gasto e edição do dia a dia ficam com as rotinas da planilha; não simular `onEdit`. Propriedades Apps Script têm contrato próprio. |

## Cobertura atual

O único caminho de escrita existente, a inicialização financeira
(`financeiro_servico.py`), já segue B–E. Os testes de
`testes/test_carteira_financeiro_rest.py` cobrem, entre outros:

- C: `test_destino_sobe_versao_com_conteudo_diferente_recusa_sem_post`,
  `test_guarda_de_versao_reobservada_depois_da_cota_de_escrita`,
  `test_mudanca_interna_durante_leitura_de_pagina_recusa`;
- D: `test_alteracao_externa_depois_do_envio_recusa_sem_repetir`,
  `test_mudanca_apos_leitura_final_nao_recebe_selo_conferida`;
- E: `test_429_de_escrita_nao_e_repetido`,
  `test_cancelamento_durante_post_retomada_nao_repete`,
  `test_resposta_perdida_retomada_so_le_sem_segundo_post`;
- A (contexto): `test_outro_usuario_e_json_de_referencia_nao_acessam_google`,
  `test_ficha_cadastrada_em_qualquer_servidor_impede_mutacao`.

A escrita sob pedido em ficha já entregue ainda não existe; ela pertence à
etapa 8 e deve herdar A–F, incluindo o aviso do risco aceito ao jogador.
Nenhum teste novo foi necessário nesta rodada.
