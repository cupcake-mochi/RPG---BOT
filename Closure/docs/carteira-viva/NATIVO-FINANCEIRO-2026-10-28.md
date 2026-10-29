# Ensaio financeiro no Google

28/10/2026 · PR 84 · **preparado, aguardando autorização Google; não validado**.
Código do ensaio: `7491d811ee0d3ab7f3455fddc736ee4430d4bb2e`.
A suíte de 1.514 continua sendo a validação offline anterior, não um resultado nativo.

## Preparação feita

- Remoto e árvore local conferidos: main `de42447`, branch da etapa 7 limpa no início.
- Criada fonte DESCARTÁVEL por cópia nativa da oficial, sem editar a oficial.
- Metadados confirmam arquivo privado com uma única permissão de dono.
- Somente nessa descartável, `EXTRATO!A2:C2` recebeu data/valor/texto fictícios e
  uma nota de teste. Leitura posterior confirmou entradas/notas e formatos anteriores.
- Piloto loopback em base/chave/segredo de serviço novos, fora do Git. OAuth/Picker
  próprios, sem novos escopos e sem alterar configuração de servidor em produção.
- Runner privado prepara: cadastro da fonte exata → cópia pelo diário da 7B →
  único envio financeiro. A resposta HTTP200 do POST Sheets será descartada
  deliberadamente para testar reconciliação após reinício; **ainda não aconteceu**.
- Identidade Discord real confirmada. A primeira solicitação de dez minutos
  expirou antes de concluir a seleção. Não estender esse prazo ou recuperar token
  expirado para contornar a recusa. Nova solicitação aberta no aviso Google.

## Estado no checkpoint

Zero personagens, zero operações de cópia e zero diários financeiros na base nova.
Nenhum POST Drive/Sheets pelo bot nesta rodada. A escrita de preparação foi feita
pelo conector somente na fonte descartável; não valida o adaptador financeiro.
Nenhuma oficial/ficha de jogador, Apps Script, produção ou campanha real alterada.
Sem modelo pago, Gateway, merge ou deploy. Arquivos/tokens/IDs reais e logs privados
não entram no Git, em ZIP ou neste relatório.

## Retomar

1. Confirmar o aviso Google e a seleção da fonte fictícia na aba do piloto.
   Confirmar também a prévia/cadastro; não selecionar outro arquivo.
2. Aguardar a cópia identificada. Se incerta, recuperar pelo mesmo pedido/diário,
   sem iniciar outro POST ou adotar uma cópia por ID arbitrário.
3. Executar a escrita de células e comprovar o que realmente ocorreu; a injeção
   planejada só pode ser registrada como feita se houver evidência HTTP200.
4. Reiniciar, reconciliar sem segundo POST e conferir as faixas/guardas delimitadas.
5. Manter propriedades Apps Script pendentes e criação bloqueada. A concorrência
   de edição do dono e a preservação global continuam sem solução/prova.
6. Revogar o grant, comprovar recusa, apagar dados fictícios, mover fonte/destino
   descartáveis à lixeira e encerrar piloto/abas próprias. **Limpeza ainda pendente.**

A configuração e os runners privados estão em `etapa7-financeiro-rest-20261028`
na base local do piloto. Não reutilizar as descartáveis/concessões anteriores.
Se a solicitação expirar, criar uma nova pelo fluxo normal. Não contornar avisos
nem alargar escopos. Sol Alto para continuar; Médio para revisão.
