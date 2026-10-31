# Modelos: ensaio nativo de 26/10/2026

**Atualização de 28/10:** a conferência pelo OAuth próprio das Guias foi
exercitada em uma descartável: leitura, reinício/retomada e recusa após revogação.
A criação permanece bloqueada. Ver [prova real e limites](NATIVO-CONFERENCIA-2026-10-28.md).
O relato abaixo conserva o escopo e a data do ensaio original.

**Reprovado para criação automática.** Três cópias descartáveis pelo Drive
conectado demonstraram herança de histórico financeiro e estado salarial.
Isso não é um teste do OAuth `drive.file` das Guias. A configuração privada
do piloto permanece no SSD Linux, indisponível nesta sessão Windows; nenhum
projeto, cliente, segredo ou escopo foi recriado.

## Fontes conferidas

- `cupcake-mochi/Ficha---RPG-JJK`, main `d0836390f90b435b4796313e898eaaa1a4a4da8b`:
  `AGENTS.md`, `r53/OFICIAIS.md`, módulos de configuração/progressão e salário.
- `cupcake-mochi/JJK---Project`, main `353d7728fa4f505f830dc6c0421929a0ab2668c1`:
  texto R57; a ficha e o contrato mecânico continuam R53/ANALISE 12.
- [Era da Revolução](https://docs.google.com/spreadsheets/d/1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k/edit)
  e [Ciclo Maldito](https://docs.google.com/spreadsheets/d/1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw/edit).
  São os IDs públicos já usados pelo bot. A oficial histórica não foi utilizada.

O código gerado completo do produtor não é prova de que todas as atualizações
incrementais estão instaladas. O registro de oficiais aponta módulos instalados
e backups próprios; nenhuma instalação ou alteração foi feita nas fontes.

## O que foi feito

Criadas três planilhas de ensaio na pasta ChatGPT da conta Drive conectada:
uma cópia da Era, uma do Ciclo e uma terceira derivada do Ciclo, transformada
em modelo sintético de servidor pela regra de nível inicial 5. Todas com
30 abas. Os IDs temporários e a conta pessoal não são necessários neste Git.

Leitura limitada: `ANALISE!A1:D12`, `EXTRATO!A1:C6`,
`DADOS_SALARIOS!L1:N3`, `SALÁRIOS!A1:L3`, `FICHA!AH11:AN11`,
`DADOS!CZ45:CZ48`, `CONFIGURAÇÃO!C46:G49`, `CARTEIRA!O9`.
Fórmulas e valores efetivos foram lidos como CellData; não houve exportação
Excel, reconstrução da ficha ou varredura integral certificando limpeza.

| Verificação | Era | Ciclo | Servidor sintético |
|---|---|---|---|
| ANALISE / revisão | 12 / R53 | 12 / R53 | 12 / R53 |
| Nível do personagem `FICHA!AH11` | 10 | 2 | 2 antes e depois |
| XP `FICHA!AN11` | Fórmula, resultado 0 | Fórmula, resultado 0 | Fórmula preservada, resultado 0 |
| Regra inicial `CONFIGURAÇÃO!G46` | 2 | 2 | 2 → 5 |
| Extrato amostrado | Três lançamentos herdados | Três lançamentos herdados | Três lançamentos herdados |
| Estado salarial `DADOS_SALARIOS!L2` | Conteúdo anterior presente | Conteúdo anterior presente | Conteúdo anterior presente |
| Data de emissão `DADOS_SALARIOS!N2` | Vazia | Vazia | Vazia |
| Primeiras linhas de SALÁRIOS | Vazias | Vazias | Vazias |

Nas três cópias, a amostra do extrato tinha saldo inicial, gasto e ganho, e
o estado salarial armazenava início, grau e última emissão. A apresentação
“Não emitida” e N2 vazia não garantem ausência de estado anterior.

Após reler o alvo e sua estrutura, houve **uma única escrita de célula**:
`CONFIGURAÇÃO!F46 = 5` na cópia sintética, preservando formato e validação.
`G46` recalculou para 5; `AH11` continuou 2; `AN11` continuou a fórmula
`=DADOS!$CZ$47`, com resultado 0. `CZ47` manteve a soma das colunas de XP
das missões em FICHA PESSOAL. Isso prova essa dependência de fórmula, não
execução de `onEdit`, sincronização de cartões ou inicialização de personagem.

As três cópias foram movidas para a lixeira pelo navegador. A interface da
lixeira exibiu os três títulos e propriedade da conta conectada. Não foi
esvaziada. Nenhuma ficha oficial ou de jogador foi escrita, nenhum
compartilhamento foi alterado e nenhum gatilho foi ativado.

## O que continua sem prova

- Inicialização limpa completa, inclusive extrato oculto, propriedades do
  Apps Script, histórico, salário, emissão e caches das automações.
- Funcionamento de todos os cartões, menus, gatilhos simples/instaláveis e
  manutenção salarial após a cópia. Não foram executados nem certificados.
- Cópia com OAuth das Guias na conta do novo responsável, acesso posterior,
  reconexão/revogação e duas identidades Google distintas.
- Preservação de todas as fórmulas/proteções, todas as 18.393 chaves e
  compatibilidade mecânica completa do modelo customizado.

Propriedade no Drive conectado não comprova acesso de um futuro jogador.
O sucesso de `files.copy` também não comprova inicialização. A documentação
do [Drive sobre cópias](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/copy)
descreve a cópia do arquivo, enquanto a documentação dos
[gatilhos instaláveis](https://developers.google.com/apps-script/guides/triggers/installable)
explica que requisições de API e execuções de script não disparam esses gatilhos.

## Contrato necessário para liberar

O produtor precisa definir uma inicialização versionada e idempotente de nova
ficha: quais dados limpar, quais preservar e como verificar o resultado sem
apagar fórmulas, configuração da campanha ou estrutura. Deve cobrir estado
salarial antigo e atual, extrato, emissão, histórico e propriedades de script.
É preciso definir os passos manuais indispensáveis, inclusive autorização e
ativação de automações pela conta do responsável, e testar falha/retomada.

Depois repetir a matriz com ambas as oficiais e um modelo de servidor,
usando o cliente OAuth existente das Guias e cópias descartáveis. Só então
implementar a cópia independente com confirmação, recuperação e parâmetros
provados. Até lá, não há criação automática nem limpeza por lista de células
adivinhada. Dados de jogo continuam reservados à etapa 8.
