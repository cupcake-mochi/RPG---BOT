# Continuação em 20/10/2026

**Atualização posterior:** os dois ajustes foram publicados em 20/10, 09h49,
com autorização explícita. Bot online e mensagem nova confirmados no Discord.
[Publicação e pendências](../../pesquisa/validacao/2026-10-20-r53-pendentes/PUBLICACAO.md).

Os resultados abaixo desta seção são históricos, da bateria de 19/10.
A nova rodada executou ampliação, entidade completa/excesso, Liberações,
Máximas e Forma custom em cartão. Ampliação e custom passaram; cartões dos
trunfos e negativos de acesso foram conferidos, mas a entidade válida revelou
dois defeitos do bot que produzem seis falsos erros (Famílias da versão 12 e
resultados de perícia com sinal `+`). Troca rápida ficou parcial, sem captura
da janela; segunda pessoa não foi executada. Dois ajustes de exibição foram
implementados e testados no commit `939d2ed`, sem publicação na Discloud.

[Relatório de 20/10 com evidências e mensagens Discord](../../pesquisa/validacao/2026-10-20-r53-pendentes/RELATORIO.md).
[Status atualizado da retomada](../../docs/RETOMADA-R53.md).

# Bateria R53 · Sheets, XLSX e Discord · 19/10/2026

Código conferido: `c1724f0effad9d14fd4bd02525fcf93395e1d93f`, branch
`claude/project-thread-zzfh12`, [PR 67](https://github.com/cupcake-mochi/RPG---BOT/pull/67).
Referência do produtor: `Ficha---RPG-JJK@4b22da5420263a8885e28a508cbc39938dd9d9da`
(`codex/publicacao-r53`, PR 4); o `main` da ficha ainda é B47. O `main` do bot
está em `93271b7`, com as PRs 65/66 mescladas. Não confundir esses estados.

## Ambiente e limites desta rodada

Mizuki confirmou que já atualizou a Discloud e autorizou os testes no tópico
`1561410667108368575`, servidor `1357866906341736488`. Foram feitas **13 análises
reais**, entre 23:26 e 23:39, pela sessão do Discord no navegador interno do
app. As respostas R53 foram verificadas; não houve nova implantação nem
comparação byte a byte dos arquivos instalados nesta rodada.

Google Drive/Sheets conectado, navegador interno, Python, Git e GitHub estavam
disponíveis. A suíte foi executada em cópia temporária do código do Git, com
as dependências locais. Sem chamadas pagas a modelos. Não foram alterados
campanha, aprovações, variáveis, bancos ou recursos da hospedagem.

A oficial foi somente lida. As três fichas abaixo são **cópias sintéticas**,
com leitura pública por link autorizada pelo usuário. Não houve construção,
migração, Apps Script publicado, importação de XLSX ou alteração da oficial.
Os cartões foram salvos por edições nativas na interface do Sheets; não se
forjaram os JSONs de MONTAGENS para substituir esse teste.

## Fichas reutilizáveis

| Cópia | Conteúdo e resultado esperado no estado final |
|---|---|
| [01 · Base simples](https://docs.google.com/spreadsheets/d/13eWPuFzudrZ8obONgF1bvBl8EiG_aR0o83PkVLtCAaw/edit) | Nível 2, Bastião/Muro/Latente, 9 pontos de atributo, 10 perícias, 2 TR, capacidades de Origem e Famílias escolhidas; Projétil de Classe 1, 3 pontos em Dano. **0 erros e 0 pendências**, com os limites humanos ainda explícitos. |
| [02 · Avançada e erro proposital](https://docs.google.com/spreadsheets/d/1k47ugyDaY_GvZz5ErpwGA0MbPMmRY_1DlsV8QEcVXBY/edit) | Projétil válido, mescla Dano/Cura válida, Classe 0 válida e um feitiço chamado **Excesso proposital R53**, com 4 pontos para saldo 3. **1 erro esperado**, somente no Feitiço 3. |
| [03 · Custom mestre](https://docs.google.com/spreadsheets/d/14Y1xqOruOz6Wb_TI0I2WZj6HZdW9dVl08yyGDCXU3Co/edit) | Perícia **Runologia Coruja B47**, Inteligência, descrição `Ler inscrições; não concede bônus numérico extra.`. Usa a aprovação sintética exata já existente neste servidor. **0 erros e 0 pendências** com essa aprovação; sem ela, exige aprovação. |

O uso de `B47` no nome da perícia é intencional: testa a preservação da
aprovação anterior na exportação R53. Não cria uma autorização nova de jogo.

## Contas e respostas observadas

As contas abaixo foram confrontadas com os valores nativos e o painel:

- Classe 1: orçamento 3; uma função e Projétil sem custo adicional deixam
  saldo 3; 3 pontos em Dano produzem **3d8, 3 PE**.
- Mescla Dano/Cura: orçamento 3, custo-base 1, saldo 2; distribuição 1/1
  produz **1d8 de Dano e 1d8 de Cura, 3 PE**. A primeira versão com três
  funções e distribuição 1/1/1 excedeu o saldo e foi corretamente apontada.
- Excesso proposital: 4 pontos de Dano contra saldo 3; a ficha mostra
  REVISAR e o bot informa **Distribuição excede o saldo**.
- Classe 0: **2d8, 0 PE, saldo 2**, sem aviso mecânico.
- A análise da avançada registrou **duas leituras do link**, com a segunda
  estável após o salvamento nativo. Isso exercitou a releitura real, além
  das simulações da suíte.

| Ensaio | Retorno confirmado no Discord |
|---|---|
| Base incompleta, antes de preencher | 4 erros e 6 pendências, correspondentes às escolhas omitidas |
| Base completa por link | 0 erros / 0 pendências |
| Base completa por XLSX nativo | Mesmo resultado; **18.393 valores de chaves idênticos** ao CSV do link |
| Avançada com dois excessos | 2 erros, nos Feitiços 2/3 |
| Avançada após corrigir a mescla e incluir Classe 0 | 1 erro, apenas no Feitiço 3 proposital |
| Custom com MESTRE VIU e definição ainda diferente | 1 pendência de aprovação exata |
| Custom idêntico à aprovação anterior | 0 erros / 0 pendências; bônus da perícia conferido |
| Custom com atributo alterado para Essência | Nova pendência; aprovação anterior não foi reaproveitada. Inteligência foi restaurada ao final |
| XLSX técnico com dano exportado adulterado para 99 | Erro: **está 99, o certo é 3** |
| XLSX técnico com `dano` JSON como texto `"true"` | Erro de formato: precisa ser booleano |
| XLSX técnico sem a versão salva da Classe ativa | Pendência informativa; nenhum parecer mecânico daquele cartão |
| XLSX técnico com chave `nome` duplicada | Arquivo recusado, chave duplicada |
| XLSX técnico com fórmula sem cache em ANALISE!B6 | Arquivo recusado, célula identificada |

Os cinco últimos arquivos são **fixtures técnicas** com somente ANALISE,
derivadas dos valores da cópia nativa. Não são exportações integrais da ficha
nem prova de recálculo nativo de uma fórmula adulterada.

Respostas de referência no tópico:
[base por link](https://discord.com/channels/1357866906341736488/1561410667108368575/1561929378034880743),
[XLSX](https://discord.com/channels/1357866906341736488/1561410667108368575/1561929805765673032),
[avançada](https://discord.com/channels/1357866906341736488/1561410667108368575/1561931342659195003),
[custom aprovado](https://discord.com/channels/1357866906341736488/1561410667108368575/1561930737182183505),
[custom alterado](https://discord.com/channels/1357866906341736488/1561410667108368575/1561931482212343921).

## Verificações offline

- 33 testes específicos R53 passaram, incluindo os 89 casos do autor
  comparados pelo núcleo vendorizado. Isso não equivale a 89 testes nativos
  executados nesta rodada.
- Suíte completa: **882 executados, 881 aprovados, 1 online opcional pulado**,
  em 249,838 s.
- Cinco fixtures técnicas: expectativas verificadas localmente antes de
  enviar ao Discord; todas tiveram o retorno externo correspondente.
- Cópia custom recalculada offline com as quatro aprovações sintéticas
  anteriores: 0 erros / 0 pendências. Sem o cadastro, a pendência é esperada.
- Paridade dos valores da base por CSV/XLSX: 18.393 chaves, zero diferenças.

Evidência resumida versionada: `pesquisa/validacao/2026-10-19-r53-bateria/`.
Exportações, snapshots sintéticos, scripts de ensaio e capturas de tela ficam
localmente no diretório ignorado `src/var/testes-r53-2026-10-19/`. Não se
incluíram credenciais, bancos ou conteúdo de fichas reais no Git.

## Painel

O seletor e as quatro setas foram exercitados na análise avançada. A página
Personagem ficou verde (`rgb(46,139,86)`), a revisão do excesso ficou vermelha
(`rgb(204,1,1)`) e Limites ficou amarela (`rgb(212,159,23)`). O rodapé conservou
o veredito geral reprovado nas três páginas. A página de feitiços mostrou os
quatro cartões, com VÁLIDO/REVISAR por cartão e os dados/PE esperados.

## O que esta bateria não certifica

- A integração entregue recalcula **cartões R53**. O corpus geral/índice ainda
  é R51/R52 e o rodapé informa R52; não apresentar o resultado como auditoria
  completa de todas as alterações do livro R53.
- Ampliação em nível alto e recuperação entre duas Classes efetivamente
  disponíveis, Liberações, Técnica Máxima e entidades completas continuam
  sem novo ensaio nativo nesta rodada. Existem regressões offline, mas isso
  não substitui um caso preenchido no Sheets e enviado ao Discord.
- Aprendizado, histórico de marcos/treinos, autorização real, requisitos
  livres, alvos, COMO É, efeitos narrativos e interações de Alma permanecem
  com o mestre. Zero erros/pendências não elimina `nao_conferido`.
- A peça/Forma custom aprovada continua **sem recálculo independente do bot**,
  conforme INTEGRACAO-R53.md. O ensaio nativo de custom aqui foi uma perícia.
- A redação “pendências abertas” mesmo com contador zero pode ser polida:
  nessa situação o impedimento são partes não conferidas, não uma pendência
  detectada. Não se alterou o comportamento para esconder esse limite.

Não houve defeito funcional novo comprovado nos casos executados. Não mudar
expectativas nem repetir implantação apenas para registrar a bateria.

Próximos casos, critérios esperados e separação entre bot, produtor e mestre:
[RETOMADA-R53.md](../../docs/RETOMADA-R53.md). Os itens desse roteiro permanecem
pendentes; não foram contabilizados nas 13 análises desta rodada.
