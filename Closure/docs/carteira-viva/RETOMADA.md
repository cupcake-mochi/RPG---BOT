# Continuar a Carteira viva

Atualizado em 27/10/2026. **Etapas 1–6 implementadas; etapa 7 parcial; 8–10 pendentes.**
Carteira não publicada. Não confundir configuração de modelo com criação funcional.

## Checkout e Git

- Usar `C:\Users\Mizuki\.codex\tmp\carteira-etapa7-recovery` neste Windows.
- Branch `codex/carteira-viva-etapa-7`, [PR 84 em rascunho](https://github.com/cupcake-mochi/RPG---BOT/pull/84),
  dependente de `codex/carteira-viva-etapa-6` / PR 83.
- Código salvo e enviado: `479389bc803a18dd812f5394aa86ef3bdec1a672`.
- CI desse código aprovado: [40440981766](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40440981766),
  1.304 executados, 1.303 aprovados, um opcional pulado, zero falhas; 207,765 s.
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
79 direcionados passaram. CI desta continuação consta no relatório.
Leia também INICIALIZACAO-PRODUTOR.md: proposta de contrato 1, ainda sem rotina
de limpeza ou certificação nativa. Nenhum piloto ou teste Google novo nesta rodada.

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
- Ficha---RPG-JJK main `d0836390f90b435b4796313e898eaaa1a4a4da8b`.
- JJK---Project main `353d7728fa4f505f830dc6c0421929a0ab2668c1`.
- Texto R57; contrato mecânico R53/ANALISE 12. Revalidar antes de mudar o produtor.

A configuração privada existente das Guias está no SSD Linux:
`/home/mizuki/.local/share/guias-ciclo/carteira-piloto`. O usuário confirmou
que não está disponível neste Windows. Ela só é necessária para a prova pelo
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

**Concluir a etapa 7**, implementando/validando no produtor a proposta de
INICIALIZACAO-PRODUTOR.md e depois provando a criação com
OAuth próprio das Guias quando o ambiente privado estiver disponível. Manter
a criação desligada até cumprir o critério do PLANO.md. Depois, etapa 8,
**GPT-6 Astra · Alto**; edições de jogo exigem contrato, prévia, confirmação e
recuperação próprios. Não iniciar a etapa 8 como se a 7 tivesse sido concluída.

Ao continuar: conferir árvore, remoto, PR e CI; usar checkout recuperado no C:.
Testar proporcionalmente; documentação isolada não exige nova bateria extensa.
Atualizar fila, contrato, relatório e retomada, salvar commit/push na pilha
correta e separar sempre implementação, simulações, ensaio nativo e produção.
