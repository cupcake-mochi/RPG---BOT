# Etapa 7: escolha do modelo e barreira de criação

26/10/2026. **Entrega parcial, não publicada.** Configuração implementada;
criação de nova ficha bloqueada por reprovação nativa da inicialização.
PR [84](https://github.com/cupcake-mochi/RPG---BOT/pull/84) em rascunho;
código `479389bc803a18dd812f5394aa86ef3bdec1a672`.
Branch `codex/carteira-viva-etapa-7`, base `codex/carteira-viva-etapa-6`
(`c2ca07ef2349ca8be46e2671a51da805bf03e69a`, PR 83). Nenhum merge ou deploy.
O CI documental da base terminou verde, run
[40424104893](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40424104893).

## Implementação no Git

- Schema 6: escolha por servidor, revisão crescente e referência customizada
  cifrada; preservação de personagens, fontes, leituras e análises existentes.
  Modelo oficial duplo por padrão; seleção opcional Era, Ciclo ou servidor.
- `/personagem modelos` e `modelo_configurar`; `/character templates` e
  `set_template`. Só administrador/dono configura. Manage Guild e cargo
  revisor não concedem essa capacidade.
- Modelo personalizado pelo fluxo existente Discord → OAuth Google
  `drive.file` → Picker → sondagem → prévia → confirmação. Conferência de
  permissão antes/depois das esperas, versão Drive e revisão local esperada.
  Alteração concorrente exige nova solicitação.
- Sondagem limitada de ANALISE 12/R53, abas e fórmulas de referência, com
  sinais de histórico/estado anterior. Não certifica limpeza ou automação.
- Escolha salva sem cadastrar personagem ou persistir uma nova conexão do
  administrador. Dados transitórios são descartados ao concluir/cancelar;
  a rotação também descarta tentativas OAuth antigas.
- Carteira e tela de conexão em PT/EN informam a indisponibilidade. Nome/ID
  privado do modelo customizado não aparecem na projeção para membros.
- Barreira incondicional no serviço: `criar_por_modelo` retorna
  `modelo_bloqueado`, inclusive com parâmetros forjados. Sem endpoint que
  copie/escreva no Google e sem flag de ambiente para contornar o bloqueio.

Cadastro de ficha existente continua independente. Não há parâmetros de
criação liberados. Nível do personagem, XP calculado e regra de nível inicial
da campanha têm significados distintos; ver CONTRATO.md e ensaio nativo.

## Validação

**CI Linux aprovado no código `479389b`: 1.304 executados, 1.303 aprovados,
um online opcional pulado e zero falhas, em 207,765 s.**
[Run 40440981766](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40440981766),
Python 3.12 / Linux. São 22 testes novos distintos além da base de 1.282.
O registro posterior é somente documental; não exige repetir essa bateria
extensa nem publicar o serviço.

83 testes direcionados finais passaram em 30,282 s no Windows recuperado:
modelos, sessões, interface Discord e HTTP da Carteira. O primeiro lote
identificou erros nas fixtures de backup/migração e na contagem esperada de
comandos; foram corrigidos preservando as verificações.

A suíte completa no Windows executou **1.292 testes em 912,595 s**, com
3 falhas, 36 erros e 2 pulados. Não passou. Entre as ocorrências: módulos
POSIX `fcntl`/`resource` e `os.killpg` indisponíveis, caminho `/tmp`, executável
Linux esperado por teste CLI, CRLF divergindo do hash vendorizado, timeout de
Node e remoção de arquivos SQLite ainda abertos no Windows. A fixture v3 de
cartões também esquecia de remover a tabela do schema 6; foi corrigida e seu
reteste passou. As duas verificações de imagem continuaram falhando isoladas:
o worker existente exige `resource`, ausente no Windows. Não foram afrouxados
limites nem alterado o processamento de mídia. O CI Linux aprovado acima é
a validação da plataforma de execução; não apaga o resultado local negativo.

Manifesto de empacotamento conferido sem gerar ZIP: 90 arquivos, sem Carteira,
segredos ou bancos. Núcleo local preparado dos fontes; quickjs/Node iguais
em 14/14 pedidos. A preparação não publica o serviço.

Navegador real com provedores **fictícios**: prévia PT/EN, aviso de dados
herdados, bloqueio sem confirmação de responsabilidade, salvar PT e cancelar
EN passaram. Na Carteira, membro comum viu só “modelo personalizado”, PT/EN,
e o logout retirou a área autenticada. Nenhum erro JavaScript observado.
Nenhum login Google/Discord real foi feito nessa demonstração. Serviço
temporário encerrado, abas de teste fechadas. A revisão automática de
permissão bloqueou a exclusão local, tanto recursiva quanto de arquivos
individuais, sem motivo específico além da política da ferramenta. Restam
somente dados fictícios em
`C:\Users\Mizuki\AppData\Local\Temp\carteira-demo-xd9kcr1_`
(banco, ledger de remoções, configuração de campanha e pasta de imagens).
Não confundir essa pendência local com as três cópias Google, já na lixeira.

No Drive real, três cópias herdaram extrato e estado salarial. No modelo
sintético, F46=5 alterou a regra, mas não o nível nem a fórmula de XP.
As cópias estão na lixeira. Resultado completo e limites em
[NATIVO-ETAPA-7.md](NATIVO-ETAPA-7.md). Esses ensaios não usam o OAuth das Guias.

## Ambiente e retomada

O Windows registrou evento NTFS 55 de corrupção no volume E:; as entradas
consultadas apontam diretórios fora deste repositório. Leituras do checkout
também travaram. Não foi diagnosticada corrupção específica do código nem
executado reparo do disco. O trabalho foi recuperado a partir da base Git
exata e dos patches desta conversa, em `C:\Users\Mizuki\.codex\tmp\carteira-etapa7-recovery`.
Os patches de salvamento permanecem fora do Git. Continuar nesse checkout;
não sobrescrever nem limpar o original do E: por rotina.

Produção preservada: nenhuma chamada paga, Gateway, publicação na Discloud,
alteração de credenciais, escopos ou permissões. O serviço da demonstração
usa banco temporário e credenciais inteiramente fictícias.

**Ainda não concluir a etapa 7.** Próximo trabalho: contrato de inicialização
do produtor e prova nativa com OAuth próprio. Depois de cumprir isso, etapa 8
com **GPT-6 Astra · Alto**, conforme PLANO.md.
