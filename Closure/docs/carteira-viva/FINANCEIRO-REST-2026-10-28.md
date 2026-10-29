# Células financeiras por REST

28/10/2026 · PR 84 · etapa 7C parcial · não publicado.

## Ensaio real

[Encerrado em 28/10 com recusas seguras](NATIVO-FINANCEIRO-2026-10-28.md):
primeiro destino mudou de versão durante a leitura; na segunda candidata,
a fonte mudou antes da identificação. **Zero POST Sheets financeiro**, sem
injeção HTTP200 ou prova de reconciliação após escrita. Três descartáveis na
lixeira, concessão revogada e base fictícia limpa. Causa das mudanças ainda
não demonstrada; não tratar como cache ou relaxar as guardas. Antes de novo
ensaio, fechar diagnóstico e fase de candidata. Descrição do código abaixo.

## O que mudou

`Consultas.inicializar_financeiro_celulas` é interno, sem rota web ou comando.
Recebe a referência tipada de uma cópia identificada pelo próprio serviço.
Recusa originais, destino compartilhado, concessão alheia, configuração alterada
ou arquivo já cadastrado como personagem em qualquer servidor.

O leitor completo delimita as faixas do contrato financeiro v1, conserva apenas
hashes de entradas/notas/formato numérico e monta 21 pedidos fixos. As 13 guardas
de fórmula são verificadas independentemente do limite de achados do painel.
Não interpreta fórmulas. Não aceita arquivo, faixa ou pedidos JSON do navegador.

O único batchUpdate limpa as entradas/notas previstas e repõe três constantes,
com field masks `userEnteredValue` ou `note`. Nunca usa máscara `*`, fórmula
nova ou chamada Apps Script. Caches podem recalcular; não são hash de preservação.
O teste compara os valores/formato/formulas delimitados, sem prometer preservação
global de imagens, mesclas, regras de validação ou todas as demais abas.

## Interrupções e segurança

- Schema 9/ledger 2: diário cifrado ligado à cópia, com prazo original de 30 minutos.
- `enviada` é persistido antes da rede, transacionalmente entre trabalhadores.
- A capacidade de envio só pode ser consumida uma vez. Timeout, 429 e cancelamento
  deixam resultado incerto: retomada só lê, mesmo se a grade ainda estiver antiga.
- Backup converte `preparada` em `enviada` apenas no backup. Não autoriza replay.
- Rotação preserva o diário; exclusão global/restore respeitam a remoção da cópia.
- O recibo da cópia não pode adotar uma versão editada depois da identificação.
- O fechamento reobserva a versão após a medição, antes de registrar conferência.
- Fila/cotas compartilhadas; limites maiores apenas neste adaptador interno.

A [API documenta a atomicidade dos pedidos e ressalva edições concorrentes](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/batchUpdate).
**Atomicidade não é comparação transacional de versão.** A observação antes do
POST não impede edição do dono nesse intervalo. O protocolo só admite uma cópia
privada ainda não cadastrada; a lacuna continua bloqueando a criação pública.
Ver [campos do RepeatCellRequest](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/request#RepeatCellRequest).

## O que falta

As cinco propriedades financeiras document/script do contrato não são células e
não são acessíveis por esta rota. Por isso `financeiro_concluido` permanece falso,
`propriedades_apps_script_pendentes` verdadeiro e os quatro indicadores gerais
continuam falsos. `celulas_conferidas` não certifica todo o financeiro.

Faltam ensaio nativo deste POST em nova cópia descartável (a prova anterior da
7B só criou/recuperou arquivo), solução das propriedades e edição simultânea,
demais domínios, automações/notas vivas/treinos/responsável e preservação integral.
Não restaurar as descartáveis antigas nem reutilizar sua concessão revogada.
Produtor PR 31 intacto; nenhuma ficha oficial/jogador alterada, merge, deploy,
Gateway, modelo pago, escopo ou endpoint novo nesta rodada.

## Próximo ensaio descartável

1. Criar fonte privada fictícia nova e usar OAuth/Picker próprios em base isolada.
   As descartáveis e concessões antigas já foram encerradas; não restaurá-las.
2. Criar a cópia pelo diário da 7B e identificá-la sem editar suas células ou
   cadastrá-la como personagem. Guardar a prova da versão original.
3. Chamar somente o adaptador interno financeiro. Conferir o único POST, entradas,
   notas e fórmulas delimitadas; não registrar conteúdo privado no relatório.
4. Ensaiar resposta perdida/reinício e confirmar retomada sem segundo POST.
   Se a grade não corresponder ao plano, manter pendente e não refazer o reset.
5. Conferir que propriedades continuam pendentes e criação continua bloqueada.
   Este ensaio não valida os outros domínios nem preservação global.
6. Revogar a concessão, comprovar recusa antes dos arquivos, remover dados
   fictícios, enviar ambas as descartáveis à lixeira e encerrar piloto/abas próprias.

## Validação

**214 testes direcionados aprovados em 101,771 s**, incluindo os 28 casos novos
do financeiro e regressões de cópia, banco, cartões, conferência, modelos e sessões.
ZIP regenerado: 90 arquivos, CRC e fontes iguais, sem Carteira, env, bancos ou
campanha; não publicado. SHA256
`b306c6132e8536645805a8a42a150a040334f33a654bb9f13850e71739ecfc71`.

Código `7491d811ee0d3ab7f3455fddc736ee4430d4bb2e`:
[CI completo 40788244056](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40788244056)
aprovado em 28/10 às **20:39:53 Brasília**: **1.514 executados, 1.513 aprovados,
um opcional pulado**, zero falhas, 331,040 s. Fechamento só documental [skip ci],
sem repetir bateria, pacote ou publicação.

As duas regressões foram reproduzidas antes da correção: adoção de versão editada no método anterior
e mudança entre a medição e o fechamento aceitas indevidamente. Nenhuma expectativa
foi relaxada. Fixtures de schemas históricos agora removem tabelas posteriores
por inventário independente, conservando as verificações de dados e migração.

Próxima implementação: Sol Alto; revisão focal: Médio. Não declarar a etapa 7
inteira concluída nem publicar este protótipo junto às Guias.
