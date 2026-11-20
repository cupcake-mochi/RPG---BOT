# Por que a versão do Drive muda sozinha

29–30/10/2026 · PR 84 · **experimento nativo, sem escrita de células; encerrado**.
Explica as recusas do ensaio financeiro de 28/10 (cópia 9→10, fonte 12→13).

## Desenho

Fonte descartável nova, cópia da oficial Ciclo pelo "Fazer uma cópia" do Sheets, na conta
do consentimento. O editor foi fechado logo após criar e **nenhum dos arquivos foi aberto
durante as medições**. Piloto loopback novo; Discord `identify` e Google `drive.file`; o
aviso de app não verificado foi aceito pela pessoa; só a fonte escolhida no Picker.

1. Linha de base: versão da fonte a cada 10 s por 180 s.
2. Uma chamada `files.copy` com o mesmo corpo do bot (nome, `parents=root`, `appProperties`).
3. Versão e `modifiedTime` da fonte e da cópia a cada 10 s por 600 s.

## Resultado

- **A chamada de cópia não respondeu em 15 s** (`ReadTimeout`), mas o Google criou o arquivo.
  A cópia foi encontrada pelo nome e pelo marcador `cv_origem`, entre os arquivos visíveis
  ao app, **sem repetir o POST**. É o mesmo "POST Drive sem resposta" das duas cópias de 28/10.
- **Cópia:** versão 8 na criação, **9 em menos de 30 s**, depois estável por ~9,5 min.
- **Fonte:** versão 13 estável por ~6 min (linha de base e começo da observação); depois
  **subiu sozinha para 14**, uns 5–7 min após a cópia.
- **Nas duas mudanças o `modifiedTime` ficou igual** (o da cópia continuou igual ao
  `createdTime`). Não foi edição visível; é o que a referência do campo `version` descreve
  como mudança no servidor.

Não dá para separar, com este experimento, se a mudança da fonte foi efeito tardio da cópia
ou processamento independente do Google. As duas hipóteses levam à mesma conclusão abaixo.

## O que isso significa para o protocolo

A guarda "versão diferente ⇒ recusa" vai recusar sem motivo real em fluxos normais de cópia,
como aconteceu em 28/10. Nenhuma guarda foi alterada nesta rodada. Propostas para decisão:

1. **Versão mudou e `modifiedTime` não:** reler as células do contrato e seguir só se o conteúdo
   for idêntico ao do plano cifrado; qualquer diferença continua recusando. Não é adotar versão:
   é provar pelo conteúdo. `modifiedTime` diferente continua recusa imediata.
2. **Tempo da cópia:** aumentar o teto do `files.copy` de 15 s (a recuperação pelo marcador já
   existe e funcionou) para reduzir o caso "cópia incerta" em toda criação.
3. Esperar a versão "estabilizar" **não resolve**: a fonte mudou minutos depois.

## Encerramento

- Fonte e cópia na lixeira **recuperável** (conferidas abrindo cada uma pelo ID: aviso
  "O arquivo está na lixeira"; nada restaurado nem excluído em definitivo).
- A primeira rodada de limpeza mandou os dois arquivos à lixeira e revogou a autorização pela
  API; parou depois, com `Conflito`, na verificação pós-revogação (tentativa de nova intenção
  com o mesmo identificador de pedido). A renovação seguinte recebeu `invalid_grant` e o
  serviço marcou a conexão como revogada.
- Base do piloto limpa por script só de banco: zero personagens, fontes, cópias, financeiro,
  modelos, fluxos, sessões, conexões ativas e segredos; banco e ledger `ok`. Porta 8876 livre.
- Falha do script registrada: o marcador aleatório não foi gravado antes do POST; a cópia foi
  achada pelo nome e pelo hash da origem. Corrigir em ensaios futuros.

Sem escrita de células, oficial/produtor/jogadores intactos, sem modelo pago, Gateway, merge
ou Discloud. Criação bloqueada; escrita financeira nativa ainda pendente.
