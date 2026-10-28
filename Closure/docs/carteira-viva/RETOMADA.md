# Continuar a Carteira viva

Atualizado em 28/10/2026. **Etapas 1–6 implementadas; etapa 7 parcial; 8–10 pendentes.**
Carteira não publicada. Não confundir configuração de modelo com criação funcional.

## Recibos e quota · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`af8e83f2869c01daa203fb5aa5c26c802c472850`. Main produtor `ef361cc` e bot
`de42447` reconferidas sem mudança. Cartões visíveis e MONTAGENS agora trocam
seus diários detalhados por recibos somente após a conferência final. Mesma
chave, sem exclusão; queda preserva diário ou recibo. Recibo terminal confere
operação/cópia/modelo/domínio, layout, guardas e resultados, sem nova limpeza.
Diários v1 desses perfis migram após conferência; demais formatos/assinaturas
preservados. Toda gravação de diário conta propriedades alheias e aplica teto
interno de 450.000 bytes, com 9.000 por valor e releitura de persistência.

44 cenários novos e seis focais de cartões passaram localmente. Coleção completa
**2.305**, zero falhas, confirmada no [CI 40697164990](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40697164990),
aprovado no código `af8e83f` em 28/10 às 10:34:44 Brasília. Pacote nove arquivos,
sintaxe 277 Python/234 JS-GS e demais regressões passaram. Duplicado 40697154581
cancelado; fechamento posterior só documental `[skip ci]`. As duas suítes de
249 cartões reais somam 125.247 bytes de recibos cada (maior 503).
Simulação conjunta: 498 recibos + reserva 100 KB = 372.263 bytes, pico 372.629.
As suítes reais também acumulam 249 recibos por domínio. Isso resolve a
retenção detalhada excessiva no protótipo, mas ainda não mede quota/latência
Google nem prova o orçamento de todas as etapas futuras. Relatório produtor:
`r53/inicializacao/RECIBOS-2026-10-28.md`.

Próximo: dados/recursos/equipamentos das entidades, arte, orquestração com
orçamento global e conferência combinada, automações/treinos/notas vivas,
responsável, integração drive.file e prova nativa completa. Criação bloqueada;
protótipos fora do pacote/bot. Nenhuma planilha foi editada nesta rodada.
Consumidor só documentação; runtime `26ec106`, CI histórico 40496955301.
Sem suíte/ZIP novo, merge/deploy, Gateway, modelo pago ou acesso novo.
GPT-6.1 Sol / Alto para implementação; Médio para revisão focal (AGENTS.md).
Entradas seguintes são históricas.

## Histórico: cartões visíveis · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`216e44c99c9aabc389f8f8811418dd538e6d5735`. Main produtor `ef361cc` e bot
`de42447` reconferidas sem mudança. Agora os 249 cartões têm protocolo para
3.863 entradas visíveis e 737 validações de função, além das versões guardadas
já tratadas. Restaura Classe/nome/COMO É e entradas/notas explícitas, protege
contas/rótulos/menus. Porta fechada recebe `—`, aberta zero ou caixa desmarcada;
regra antes do valor, com retomada separada. Amparo é relido e protegido por
fórmula; o destino usa a Classe de fábrica. Extras permitem Classe 0, mas o
modelo atual começa em 1. Não mudar defaults para satisfazer expectativas.

Executor ampliado só com operação de validação; contratos anteriores mantidos.
101 financeiros, 441 formação e sete focais passaram localmente. Coleção
completa no [CI 40694498546](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40694498546),
aprovado no código `216e44c` em 28/10 às 10:16:56 Brasília: **791 novos, 2.261
totais** (101/82/78/243/441/155/370/791), pacote nove arquivos e sintaxe
277 Python/233 JS-GS. Duplicado 40694490233 cancelado; fechamento produtor
`43c2f67` somente documental, `[skip ci]`. Leitura das duas
oficiais: nove contextos, 124 entradas, 210 guardas e 25 validações por arquivo,
sem diferença, escrita ou execução Apps Script. Relatório produtor
`r53/inicializacao/CARTOES-VISIVEIS-2026-10-28.md`.

**Quota conjunta é bloqueio real:** guardar todos os diários detalhados dos
cartões somou 1.396.929 bytes (maior 5.765), acima da capacidade conjunta de propriedades. Antes da integração, resolver
orçamento/compactação com recibos e proteção contra reinicialização; não apagar
diários para repetir. Também faltam dados/recursos/equipamentos das entidades,
arte, orquestração/conferência combinada, automações/treinos/notas vivas,
responsável, integração executável drive.file e prova nativa completa. Criação
segue bloqueada. Eventos/editor não podem rodar no meio da limpeza; MONTAGENS,
campos visíveis e memórias finais precisam ser conferidos juntos.

Consumidor só documentação; runtime `26ec106`, CI histórico 40496955301,
1.314 executados/1.313 aprovados/um opcional. Sem suíte/ZIP novo, merge, deploy,
Gateway, modelo pago, escopos novos ou escrita em oficial/jogador.
GPT-6 Astra / Alto para implementação integrada; revisão focal Médio.

## Histórico: MONTAGENS · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`5749b3af25f3b4082900a26685db655a696c4c26`. Main do produtor `ef361cc` e bot
`de42447` reconferidas sem mudanças. Implementado o protocolo das versões
salvas dos 249 cartões: 48.015 entradas, todas as Classes, um diário por cartão.
Defaults/notas de entrada restaurados; títulos, Classes máximas calculadas,
rótulos, instruções e demais domínios preservados. Validação/mescla inesperada,
fórmula desconhecida ou mudança concorrente causa recusa. Nenhuma alteração
no executor financeiro ou nos contratos anteriores.

370 cenários novos e 101 financeiros passaram localmente. Coleção completa
**1.470** confirmada no [CI 40690086385](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40690086385),
aprovado no código `5749b3a` em 28/10 às 09:45:06 Brasília. Sintaxe 277 Python/
228 JS-GS e demais verificações passaram. Duplicado 40690078538 cancelado.
Fechamento produtor `3cca7c5` apenas documental, `[skip ci]`. Os diários sintéticos dos 249 cartões somam 178.035 bytes;
isso não certifica a quota global da cópia. Leitura das duas oficiais: oito
modos em cada uma, 990 entradas e 310 guardas por arquivo, zero divergências,
sem escrita. Não criou cópia nem executou Apps Script/OAuth nesta rodada.
Relatório produtor: `r53/inicializacao/MONTAGENS-2026-10-28.md`.

**Os cartões visíveis ainda faltam.** Seus valores e validações dependem das
funções liberadas: não restaurar números/checkboxes por cima de listas `—`.
Também faltam dados/recursos das entidades, arte, orquestração/quota e conferência
global, automações/treinos/notas vivas, responsável, integração drive.file e
prova nativa completa. O leitor real comprovou que limpar MONTAGENS mantém o
cache persistente antigo; a limpeza do domínio de memórias precisa terminar
antes de religar o editor e conferir o conjunto. Criação continua bloqueada.

Consumidor só documentação; runtime `26ec106`, CI histórico 40496955301,
1.314 executados/1.313 aprovados/um opcional. Sem suíte ou ZIP novos, merge,
deploy, Gateway, modelo pago, escopos novos ou escrita em oficial/jogador.
Próxima implementação: GPT-6 Astra / Alto; revisão focal Médio.

## Histórico: CARTEIRA e memórias · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`8bb93355cb5d20d75ead1d8ba9a4b6d7c3ad88cc`. Main `ef361cc` e bot main
`de42447` reconferidas sem novidade; nenhum merge necessário.

Perfil CARTEIRA: O13, O27 e O30, conteúdo/notas de fábrica; preserva servidor,
espelhos, identidade, foto e emissão tratados separadamente. O27 é a técnica
declarada consumida por DADOS_AM; sentinela antigo D24 do teste foi corrigido
com prova da montagem completa. Nove contratos de formação anteriores iguais.

Protocolo separado de memórias: quatro caches e 249 marcadores de Classe em
11 grupos fixos de até 24 chaves; recuperações conhecidas por timestamp com
diário individual. Só document properties conhecidas, sem apagar células,
MONTAGENS, configurações, script/user properties ou diários alheios. Recusa
namespace/contrato desconhecido, preserva retomada/concorrência/limites e
invalida cache volátil do editor. A inspeção final deve ser repetida para
identificar recuperações novas; concluir um grupo não certifica o conjunto.

441 cenários de formação/CARTEIRA, 155 de memórias e 101 financeiros passaram
localmente; **1.100** (101/82/78/243/441/155) confirmados no
[CI 40686604745](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40686604745),
aprovado no código `8bb9335` em 28/10 às 09:19:25 Brasília, junto ao pacote
e demais regressões. Run duplicado de push 40686597423 cancelado. Fechamento
produtor `306b22ed008a18d04e40c8d437806cedc5003333` só documental, `[skip ci]`. Quinze entradas/guardas e três notas conferidas em cada
oficial, sem divergência, somente leitura. Sem nova cópia, projeção ou execução
Apps Script nesta rodada. Relatório do produtor:
`r53/inicializacao/CARTEIRA-MEMORIAS-2026-10-28.md`.

Próximo: entidades/cartões/MONTAGENS. Ainda faltam arte, orquestração e
conferência conjunta, ordem das memórias com automações/notas vivas/treinos,
novo responsável, integração executável drive.file e prova nativa completa.
**Criação incondicionalmente bloqueada.** Limpar caches não limpa os cartões
armazenados; não religar automações no meio da limpeza nem apagar diários
para forçar uma nova execução. Não confundir testes isolados com aceite final.

Runtime bot `26ec106`, CI histórico 40496955301 (1.314/1.313/um opcional), PR 84
base PR 83; consumidor só docs, sem suíte/ZIP novo. Protótipos fora do pacote.
Sem merge/deploy/Gateway/modelo pago/escopos novos ou escrita em oficial/jogador.
Próxima implementação GPT-6 Astra / Alto; revisão focal Médio.

## Checkout e Git

Continuação Linux de 27/10: usar explicitamente
`/home/mizuki/.codex/tmp/carteira-etapa7-linux` para o bot e
`/home/mizuki/.codex/tmp/ficha-carteira-inicializacao` para o produtor.
São clones no SSD, reconferidos com o remoto. O checkout antigo em
`/media/mizuki/HD Externo II/Closure Lab/RPG---BOT-b47` está no código da
etapa 6 com alterações locais de versões diferentes da etapa 7. Não foi
resetado, limpo ou sobrescrito. A comparação local identificou versões já
salvas no histórico remoto, sem mudança exclusiva nas 19 fontes alteradas;
isso não autoriza descartar a árvore. Os caminhos Windows abaixo são históricos.

- No Windows recuperado, usar `C:\Users\Mizuki\.codex\tmp\carteira-etapa7-recovery` neste Windows.
- Branch `codex/carteira-viva-etapa-7`, [PR 84 em rascunho](https://github.com/cupcake-mochi/RPG---BOT/pull/84),
  dependente de `codex/carteira-viva-etapa-6` / PR 83.
- Código atual salvo e enviado: `26ec1068131a8b71a9a04688bcf8676771fd736c`.
- CI desse código aprovado: [40496955301](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40496955301),
  1.314 executados, 1.313 aprovados, um opcional pulado, zero falhas; 278,076 s.
  O commit posterior só registra documentação e usa `[skip ci]` para não
  repetir a bateria extensa por esse registro. Conferir o código pelo SHA acima.
- Base exata `c2ca07ef2349ca8be46e2671a51da805bf03e69a`; CI documental 40424104893 verde.
- Pilha anterior 77–83 em rascunho, sem merge. Não mudar a base para main nem usar force-push.
- Main conferida `de424478a7a120ecb43bd0c79eb93774d446fae6`.
- O checkout anterior `E:\Closure Lab\RPG---BOT-b47` teve leituras travadas.
  Windows registrou corrupção NTFS no E: em diretórios fora deste repositório.
  Nenhum reparo executado, nem corrupção específica do código diagnosticada.
  Base e patches foram recuperados no C:. Não sobrescrever ou remover o original.

## O que já funciona no código

Continuação de 27/10: sondagem 2 lê até a última linha física dos três livros
financeiros (máximo de 5.000 linhas; recusa acima disso), entradas e notas de
missão, caixa de lançamento e caixas de correção. Só os sinais são guardados;
versão da sondagem entra na comparação da confirmação. Dez testes novos;
79 direcionados passaram e CI Linux completo aprovado no SHA indicado acima.
Registro do ensaio financeiro anterior (antes do avanço descrito no topo).
Leia também INICIALIZACAO-PRODUTOR.md: o primeiro domínio financeiro está
implementado separadamente na PR 31 do produtor, em rascunho, sem integração
no bot. 99 cenários novos e CI do produtor passaram. A regra confirmada pelo
usuário é preservar configurações extras da mesa e inicializar os dados
pessoais separadamente. Naquele código, o protótipo cobria só financeiro;
textos e nível/base receberam os protótipos descritos no topo. A inicialização
pessoal inteira, inventário, cartões/recuperações e automações seguem pendentes. Prévia nativa financeira em
cópia do Ciclo concluída em 115,013 s; a primeira aplicação atingiu 360,813 s
e retomou em 236,503 s. Código
corrigido `4f3555d`, documentação `352929a`, CI 40505846627 verde; no máximo quatro escritas/chamada,
orçamento e conferência sem duplicação. Na segunda cópia, aplicação 283,416 s
sem timeout; repetição 150,489 s, estado comparado igual. Duas cópias na lixeira,
abas de ensaio/servidor local encerrados. Zero acionadores para o executor;
automação salarial não está atestada. Custo ainda exige otimização e integração
assíncrona permitida. Ver ETAPA-7.md para o alcance das comparações. Não confundir com criação completa
ou OAuth das Guias.

Schema 6, modelos oficiais por padrão, seleção opcional Era/Ciclo/personalizado,
configuração por dono/Administrator e prévia/confirmar via OAuth/Picker existente.
Referência customizada cifrada, revisão local e versão Drive verificadas, perda de
cargo revalidada. Não cria conexão persistente do administrador nem personagem.
Trocar modelo não muda fichas cadastradas, campanha ou análise. Membros veem
somente a escolha genérica; nome/arquivo privado não aparecem na Carteira.

Comandos `/personagem modelos`, `/personagem modelo_configurar`,
`/character templates`, `/character set_template`. Interface PT/EN.
Cadastro existente segue por `/personagem cadastrar` ou `/character register`.
`criar_por_modelo` sempre retorna `modelo_bloqueado`, sem escrita Google ou
atalho de configuração. Nenhum parâmetro de criação está liberado.

## Bloqueio nativo da etapa 7

Três cópias descartáveis pelo Drive conectado (duas oficiais e uma sintética)
herdaram EXTRATO e estado salarial em DADOS_SALARIOS!L2, mesmo com N2 vazia.
No modelo sintético, CONFIGURAÇÃO!F46=5 mudou G46 de 2 para 5, mas o personagem
ficou no nível 2 e XP 0. XP permanece fórmula; regra de campanha não inicializa
nível do personagem. As três cópias estão na lixeira, sem mudança nas fontes.

Isso comprova o bloqueio, não inicialização funcional, Apps Script, acesso de
um novo jogador ou OAuth das Guias. Não presumir gatilhos após cópia/API.
O produtor precisa versionar a limpeza e inicialização idempotente, indicar
ativação manual indispensável e comprovar resultado nas três classes de modelo.
Não limpar células conhecidas de forma avulsa para declarar uma ficha nova limpa.

Produtores conferidos:
- Ficha---RPG-JJK main `57117fbe5c2361e6a09bfa00f037b4bcfaa8437f` (incorporada na PR 31).
- JJK---Project main `353d7728fa4f505f830dc6c0421929a0ab2668c1`.
- Texto R57; contrato mecânico R53/ANALISE 12. Revalidar antes de mudar o produtor.

A configuração privada existente das Guias está no SSD Linux:
`/home/mizuki/.local/share/guias-ciclo/carteira-piloto`. Ela foi localizada nesta continuação Linux; não foi aberta nova conexão
Google das Guias nem reutilizado grant antigo. No Windows anterior ela não estava disponível. Ela só é necessária para a prova pelo
OAuth próprio; não pedir segredos no chat, não recriar clientes/projetos,
não ampliar escopos e não usar credenciais da Arquivista.

## Provas e limites

Limpeza local pendente: a revisão automática bloqueou excluir os arquivos de
`C:\Users\Mizuki\AppData\Local\Temp\carteira-demo-xd9kcr1_`, inclusive
individualmente; sem motivo específico além da política da ferramenta.
Contém somente dados fictícios desta demonstração, cujo serviço já encerrou.
Não contornar a restrição por outra ferramenta. As cópias Google estão na lixeira.

Leia ETAPA-7.md, NATIVO-ETAPA-7.md, CONTRATO.md, BANCO.md, SERVICO.md e TESTES.md.
83 testes direcionados finais passaram. A suíte completa Windows não passou:
1.292 executados, 3 falhas/36 erros/2 pulados; causas e fixture v3 corrigida
constam no relatório. O CI Linux aprovado valida a plataforma de execução.
Navegador PT/EN com provedores fictícios; Drive real por conector.
Não misturar essas provas. Pilotos anteriores continuam encerrados e grants
antigos revogados; não reutilizar cópias da lixeira.

HTTPS persistente, campanha/idioma autoritativos entre bot/serviço,
capacidade/recuperação e bateria nativa combinada seguem pendentes. Ocorrência
anterior de imagem lenta deve ser medida na etapa 9 sem afrouxar os limites.
Serviço/ponte seguem fora do pacote público. Sem modelo pago, merge, deploy,
Gateway duplicado, escrita em oficiais/jogadores ou publicação da Carteira.

## Próximo passo

**Concluir a etapa 7**, continuando os domínios pessoais restantes e a
orquestração/conferência final no produtor, conforme a proposta de
INICIALIZACAO-PRODUTOR.md e depois provando a criação com
OAuth próprio das Guias quando o ambiente privado estiver disponível. Manter
a criação desligada até cumprir o critério do PLANO.md. Depois, etapa 8,
**GPT-6 Astra · Alto**; edições de jogo exigem contrato, prévia, confirmação e
recuperação próprios. Não iniciar a etapa 8 como se a 7 tivesse sido concluída.

Ao continuar: conferir árvore, remoto, PR e CI; usar o checkout SSD deste ambiente,
sem sobrescrever a árvore antiga do disco externo.
Testar proporcionalmente; documentação isolada não exige nova bateria extensa.
Atualizar fila, contrato, relatório e retomada, salvar commit/push na pilha
correta e separar sempre implementação, simulações, ensaio nativo e produção.
