# Bateria nativa R53 · 20/10/2026

**Atualização posterior ao encerramento:** o usuário autorizou a publicação,
concluída às 09h49 de 20/10. [Registro da publicação](PUBLICACAO.md).
O estado “não publicado” deste relatório é histórico, anterior a esse pedido.

## Código, escopo e origem

Branch `claude/project-thread-zzfh12`, PR 67. Base lida `9f52a57`.
Código local testado: `939d2ed747f9ff1fc0fa3533c4a618fb9405a118`.
Produtor de referência: `Ficha---RPG-JJK`, `codex/publicacao-r53`,
`4b22da5420263a8885e28a508cbc39938dd9d9da`.
Referência publicada fornecida pelo usuário: `c1724f0`; o hash instalado
não foi auditado. **Não houve publicação ou reinício na Discloud.**
As respostas externas abaixo exercitam o runtime publicado, que ainda tem
a redação antiga. Elas não validam a publicação dos dois ajustes locais.

Só cópias sintéticas, criadas por cópia integral nativa do Google Sheets:

- [04 · casos de nível alto](https://docs.google.com/spreadsheets/d/1lujjGigxC8bvYJ3DLRziIeUvLU_AeqjiCmcnt6iyqcE/edit).
- [05 · negativos e troca rápida](https://docs.google.com/spreadsheets/d/1VjBPOoDwrlODzAPoSINOjtLv7AOmdWXUiWHBBk4M1Es/edit).
- [06 · Forma custom em cartão](https://docs.google.com/spreadsheets/d/1GfxTJcN3G8SrEwA8KTqIKzafAGhfaeFtV3IjmlTeBWY/edit).

Nenhuma importação de XLSX, escrita em MONTAGENS/ANALISE, edição da ficha
oficial, configuração de campanha, banco ou aprovação real. Inputs gerais
foram preparados via Sheets; cartões e troca de Classes passaram pela edição
nativa e pelo onEdit. Exportações CSV/XLSX são reais, sem adulteração.
As três cópias contêm exclusivamente dados inventados e têm link de leitura.

`expectativas-antes.json` foi registrado antes dos respectivos envios e recebeu
adendos antes dos novos casos. A fonte independente das contas foi o livro
do produtor em `referencias-r53/LIVRO-COMPLETO.md`, não o resultado da ficha.
Histórico de XP inventado só para ensaio: nível 5/800 XP/4 missões longas;
nível 17/10.400 XP/52 longas; negativo nível 9/3.000 XP/15 longas. Uma missão
por semana, 200 XP por missão; nível inicial 2 preservado. A origem desses
ganhos, marcos, treinos e aquisições continua exigindo decisão do mestre.

## Resultado por caso

| Caso | Expectativa independente | Evidência e resultado |
|---|---|---|
| Ampliação, nível 5 | C1: Projétil, Dano 3, 3d8/3 PE. C2: Dano 6, 6d8/6 PE. Voltar e recuperar ambas as versões | Passou: C1 preservou 3, C2 preservou 6; link e XLSX C2 com ambas as versões concordaram. [Link](https://discord.com/channels/1357866906341736488/1561410667108368575/1562070976844402800), [XLSX](https://discord.com/channels/1357866906341736488/1561410667108368575/1562071699514593342), [retorno C1](https://discord.com/channels/1357866906341736488/1561410667108368575/1562071806825734248). |
| Ampliação proibida | Precisão acrescentada somente na C2 deve acusar mudança de peça | Passou: erro de ampliação e erro adicional esperado de Família Fechada. Remoção da peça e restauração do Dano retiraram os erros; export voltou ao estado anterior. [Discord](https://discord.com/channels/1357866906341736488/1561410667108368575/1562072346158833766). |
| Entidade completa, nível fixo 17 | Domada com técnica própria sintética, atributos 3/3/3/2/1, Vida 104, Defesa 13, ataque +5, CD 13, deslocamento 9. Básica C0: 3d6/0 PE. Especial 1: Precisão da Mira Livre, preço 1, saldo 1, Dano 1d8/3 PE. Especial 2: 2d8/3 PE | **Falhou a conferência integral**: seis falsos erros (Famílias e cinco perícias). Cartões e números preparados são compatíveis; não se declara a entidade aprovada. [XLSX nativo](https://discord.com/channels/1357866906341736488/1561410667108368575/1562075837195358309). |
| Entidade com excesso | Especial 1 com Dano 2 excede saldo 1 | Passou a detecção do excesso: sete erros, sendo seis falsos já conhecidos e um `Distribuição excede o saldo`. [Link](https://discord.com/channels/1357866906341736488/1561410667108368575/1562082259140354072), [XLSX](https://discord.com/channels/1357866906341736488/1561410667108368575/1562082742315782158). Restaurado Dano 1 ao fim. |
| Liberações válidas | Nível 17, Classe 3. Pessoal: 9 pontos + 3d8 = 12d8/14 PE. Entidade: 6 pontos + 3d8 = 9d8/14 PE | Cartões passaram, zero diagnósticos próprios; veredito global ainda tem seis falsos erros da entidade. [Link](https://discord.com/channels/1357866906341736488/1561410667108368575/1562077743133368322), [XLSX](https://discord.com/channels/1357866906341736488/1561410667108368575/1562077853955137577). |
| Máximas válidas | Nível 17, Classe fixa 5, orçamento 8, Dano fixo: pessoal 24d8, entidade 19d8; 25 PE cada | Cartões passaram, zero diagnósticos próprios, no mesmo link/XLSX dos trunfos. Não certifica aquisição, trunfo narrativo nem COMO É. |
| Liberações e Máximas sem acesso | Nível 9 para personagem e entidade; Liberação exige 10 e Máxima 17 | Passou a rejeição de acesso. Doze erros: seis de acesso/contagem dos trunfos, mais os seis falsos da entidade. [Link](https://discord.com/channels/1357866906341736488/1561410667108368575/1562078393095168125), [XLSX](https://discord.com/channels/1357866906341736488/1561410667108368575/1562079292265865357). |
| Forma custom pendente | Nome novo, baseada em Projétil, MESTRE VIU marcado; definição e cartão pedem aprovação exata | Passou: 0 erros/2 pendências por link e XLSX. [Link](https://discord.com/channels/1357866906341736488/1561410667108368575/1562080514251423838), [XLSX](https://discord.com/channels/1357866906341736488/1561410667108368575/1562081743564177552). Página Limites mostrou explicitamente `usa cadastro próprio; contas mostradas pela ficha, sem recálculo do bot`. |
| Forma custom aprovada | Definição literal anterior `Agulha Coruja B47`, tipo Forma, base Projétil, demais campos vazios | Passou reconhecimento da aprovação **sintética anterior**, sem gravar aprovação: 0 erros/0 pendências. [Link](https://discord.com/channels/1357866906341736488/1561410667108368575/1562081955032465450), [XLSX](https://discord.com/channels/1357866906341736488/1561410667108368575/1562082366640361612). O bot não recalcula o cartão custom; o livro/base prevê 3d8/3 PE. |
| Forma custom alterada | Mudar texto do efeito invalida correspondência com aprovação exata | Passou: retornaram as duas pendências. [Discord](https://discord.com/channels/1357866906341736488/1561410667108368575/1562082633477791825). Efeito restaurado vazio; voltou a 0/0 e a exportação ficou idêntica ao XLSX aprovado. |
| Troca rápida 2→1→2 | Preservar versões e capturar eventual transição para provar releitura | **Parcial**: oito capturas reais preservaram C1 Dano 3 e C2 Dano 6, sem mistura, mas todas já estavam estáveis. Não capturaram a janela nem provaram retry/releitura durante ela. [Discord do estado final](https://discord.com/channels/1357866906341736488/1561410667108368575/1562080421628346478); CSV final igual ao XLSX estável anterior. |
| Segunda pessoa no painel | Outro participante real autorizado | Não executado: nenhuma segunda sessão/pessoa disponível. Não se simulou multiusuário com a conta atual. |

## Dois defeitos funcionais encontrados, ainda sem correção

1. `ficha_magia.escolhas_familias` usa o validador posicional novo somente
   quando `formato.versao == 11`. R53 exporta 12 e cai na lógica antiga, que
   exige vagas 1/3/4. O produtor atual usa 1/2/3 (Livre + duas abertas).
   `Mira · Amparo · Área · vazio · vazio` é rejeitado indevidamente.
2. `ficha_b47` compara os resultados `invocacao.1.buff.pericia.N` diretamente
   com números. A exportação nativa usa textos `+3/+4/+5/+3/+4`, que o leitor
   conserva; gera cinco erros como `está +3, o certo é 3`.

As duas reproduções aparecem no XLSX nativo da entidade e nos trunfos, tanto
localmente quanto no Discord. Não se deslocaram Famílias para vagas erradas
nem se removeram sinais da exportação para obter verde. Corrigir esses
defeitos exige trabalho funcional posterior, fora dos dois ajustes de exibição.

## Preparação, descartes e limites de observação

- Família Amparo precisou ser selecionada nativamente para sincronizar as
  validações dos cartões. Antes disso, uma célula de Cura ainda continha
  `—` e impedia o salvamento da Máxima. É preparação incompleta do ensaio,
  não defeito funcional novo comprovado. A primeira análise de entidade
  com quatro pendências transitórias não é a prova de paridade; valem os
  snapshots estáveis 09 e 15.
- Primeiro ensaio rápido descartado: o helper conservava o handle da cópia
  04 enquanto o leitor acompanhava a 05. O helper foi corrigido para receber
  explicitamente a aba; a repetição e as oito capturas versionadas são da 05.
- Tentativa de referência de aba abreviada `FA!E69` foi recusada pelo Sheets
  antes de edição; a seleção correta foi refeita na aba FICHA AMALDIÇOADA.
  A primeira tentativa de alteração de efeito usava EZ49; a origem da chave
  no CSV mostrou **EZ45**. Aquela tentativa não foi enviada nem contada.
- Clicar setas de alguns painéis não produziu avanço confirmado. Não usar
  essas tentativas como prova de navegação. O limite do custom foi observado
  na página 5 da resposta pendente e também consta da análise local aprovada.
- As cópias 04 e 06 foram restauradas aos estados válidos preparados (a 04
  continua com os seis falsos erros do bot). A 05 fica no negativo nível 9.
- O corpus/rodapé do bot continua R51/R52; isto valida a integração dos
  cartões R53, não toda mudança do livro R53. Aprendizado, histórico, autorização,
  alvos, COMO É, narrativa e Alma continuam com o mestre, inclusive com 0/0.

## Código e verificação

Somente os dois ajustes pedidos, com regressões, no commit `939d2ed`:

- Contagem zero com apenas partes não conferidas passa a dizer
  `Conferência parcial; há partes não conferidas`. Pendências e ajustes reais
  conservam textos próprios. Veredito, cor, rodapé e limites não mudaram.
- Valor inválido na mensagem R53 fica com no máximo 120 caracteres e `…`
  quando truncado. Casos 119/120/121/300 caracteres exercitados.
- Ajuste opcional da redação B47 não realizado.

Windows, Python 3.12.14: 34 testes R53 OK; 246 testes `test_ficha*.py` OK,
um online opcional pulado; os 19 do painel estão incluídos nesses 246.
Também foram 174 B47, com um erro de caminho Linux; esse caso passou
isoladamente após disponibilizar launcher local em `.venv/bin/python.exe`.

Suíte completa solicitada: **874 executados, 29 erros, 1 falha, 65 pulados**.
Não ficou verde neste Windows: há uso de `os.killpg`, módulo `resource`, caminho
Linux do Python e falha de GIF dependente da execução de mídia. WSL indisponível.
Não substituir esse resultado pelos 882 testes verdes da rodada Linux nem
alterar runtime de mídia fora do escopo. Logs completos ficam no diretório
local ignorado; `testes-e-pacote.json` resume os resultados.

Pacote regenerado e auditado: 75 arquivos, sem segredos, bancos, campanha ou
ensaios; fontes alteradas iguais às testadas. SHA256
`31b39b284b140b4db70b2eaf09428745441fcdfe8bf8dfc595a323e46e76a2ed`.
**Preparado, não publicado.**

## Evidência e próxima retomada

Os JSONs desta pasta contêm expectativas, resultados, cartões exportados,
paridades e links das mensagens. Nos estados com XLSX comparado, as 18.393
chaves tiveram zero divergências. A aprovação sintética local foi lida do
registro anterior, sem alteração, apenas para reproduzir a comparação offline.
Nenhum cadastro de aprovação foi versionado.

Artefatos integrais e capturas ficam em `Closure/src/var/testes-r53-2026-10-20/`
(ignorado): CSVs, XLSX nativos, resultados, scripts e logs. Imagem dos cartões
da entidade: `trunfos-entidade.jpg`. A tentativa `custom-sem-recalculo.jpg`
capturou uma tela de carregamento e **não serve como evidência visual**.

Faltam: corrigir os dois defeitos da entidade com regressões e repetir os
casos afetados; capturar a transição real na troca rápida; segunda pessoa;
verificar a suíte completa em ambiente Linux compatível; revisão/merge da
PR 67. Qualquer implantação continua separada e depende de pedido do usuário.
