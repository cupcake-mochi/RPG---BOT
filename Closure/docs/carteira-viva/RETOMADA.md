# Continuar a Carteira viva

Atualizado em 28/10/2026. **Etapas 1–6 implementadas; etapa 7 parcial; 8–10 pendentes.**
Carteira não publicada. Não confundir configuração de modelo com criação funcional.

## Inventário e equipamento · continuação de 28/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`86410bee3fc70fa81f124a695253e032688c3ebe`. Main `ef361cc` reconferida,
sem alteração desde o checkpoint anterior; bot main `de42447` também igual.

Três perfis novos: equipados (cinco campos), equipáveis guardados (88) e itens
(36). Restauram fórmulas/notas, limpam estoque e valores pessoais, preservando
configurações e catálogos. Quatro notas vivas antigas são limpas sem escrever
nas suas fórmulas protegidas. Soco, mão livre e Traje 1 são defaults da ficha;
não concede dinheiro, estoque ou treino. Fórmulas desconhecidas recusadas.
A variante decimal 0,1 observada nas oficiais é aceita somente nas fórmulas
inteiras conhecidas de Volume; mudança de número/referência continua recusada.
Contratos anteriores e assinatura financeira v1 mantidos.

417 cenários direcionados de formação/inventário e 101 financeiros passaram;
a coleção de inicialização soma 921 (101/82/78/243/417), confirmados pelo
[CI 40683614201](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40683614201),
aprovado em 28/10 às 08:56:07 Brasília no código `86410be`, junto ao pacote,
regressões, catálogo/progressão/Kaori e sintaxe 277 Python/220 JS-GS.
Duplicado 40683604255 cancelado. Fechamento produtor `edea21b` só documental,
`[skip ci]`. Leitura de 161 entradas/
guardas por oficial, zero diferenças e nenhuma escrita.

Projeção Sheets API em cópia privada do Ciclo: 129 campos/notas e quatro notas
isoladas restaurados; 2.678 posições, 10.450 comparações preservadas sem diferença.
Carga 0,3 de 5 igual ao modelo, por causa do Traje 1; nenhum erro nas faixas.
Cópia na lixeira, aba fechada. **Não executou os novos diários Apps Script,
OAuth das Guias ou automações.** Relatório do produtor:
`r53/inicializacao/INVENTARIO-2026-10-28.md`.

Próximo: campos pessoais restantes da CARTEIRA e propriedades de recuperação;
depois entidades/cartões/MONTAGENS. Ainda faltam arte/caches/recuperações,
orquestração/conferência conjunta, automações/notas vivas/treinos iniciais,
novo responsável, integração executável drive.file e prova nativa completa.
**Criação incondicionalmente bloqueada.** Avisos vazios não são aprovação;
notas vivas serão regeneradas na fase final. Não apagar diários para reiniciar.

Bot runtime `26ec106`, CI 40496955301 (1.314/1.313/um opcional), PR 84 base 83.
Consumidor só docs, sem repetir suíte ou gerar ZIP. Protótipos fora do pacote/bot.
Sem merge em main, deploy, Gateway, modelo pago, novos escopos ou escrita em
oficial/jogador. Próxima implementação GPT-6 Astra / Alto; revisão focal Médio.

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
