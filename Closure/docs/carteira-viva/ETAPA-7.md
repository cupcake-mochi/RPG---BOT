# Etapa 7: escolha do modelo e barreira de criação

## Escolhas, recursos e condições · continuação de 27/10

Produtor [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), código
`a55517deb9b77c43b796c80ac41f1029c0fdebd7`, sobre main `57117fbe5c2361e6a09bfa00f037b4bcfaa8437f`
(merge `6d4ddf1`; PR 38 só registra backup 11/instalação salarial por outro trabalho).
Não reaplicar essa instalação. Inicializadores continuam fora do pacote e do bot.

- 19 escolhas básicas: Caminho/Trilha/Origem, atributos base/distribuição de
  Corpo, contadores de marcos e seletores pessoais de atributo.
- 20 recursos/bônus: atuais voltam às fórmulas dos máximos, bônus/temporários
  ficam zerados e caixas ± vazias; não copia resultado numérico antigo.
- Nove condições/descanso: Sequelas, extras, Exaustão, resistências/imunidades,
  convite de descanso e registro anterior. Notas voltam à fábrica, incluindo
  a instrução de Sequelas extras. Formatos, validações e catálogos preservados.

Um diário de cena com 29 entradas excedia o tamanho permitido: domínios foram
separados e o executor recusa acima de 9.000 bytes UTF-8 antes de gravar.
Assinatura financeira v1 mantida. Contrato gerado de fonte pública e conferido
sem regeneração; variantes Google restritas de separador/aspas, sem mudar texto
literal ou aceitar outra conta. Guardas desses perfis usam leitura em bloco.

**502 cenários locais passaram** (101/80/78 + 243 novos), com todas as falhas
antes/depois das escritas. Leitura nativa das duas oficiais: 112 conferências
por documento, zero divergências finais, sem escrita. Projeção Sheets API numa
cópia privada nova do Ciclo: 48 campos/notas e 11.634 comparações delimitadas
preservadas sem diferença; atuais acompanharam máximos após escolhas fictícias
(23/23, 8/8, 26/26). Cópia na lixeira, aba fechada. **Não executou os novos
perfis/diários Apps Script nem OAuth próprio das Guias.** [Prova e limites](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/a55517deb9b77c43b796c80ac41f1029c0fdebd7/r53/inicializacao/ESCOLHAS-RECURSOS-2026-10-27.md).

CI Linux aprovado no código `a55517d`: [40540295538](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40540295538),
27/10 às 13:24:13 Brasília. Confirmados 502 cenários, pacote de nove arquivos,
regressões, sintaxe de 277 fontes Python/212 JS-GS, catálogo/progressão/Kaori.
O duplicado do push já havia terminado aprovado quando se tentou cancelá-lo;
não somar execuções. Registro posterior só documental com `[skip ci]`.

Criação permanece bloqueada. Faltam Grau, treinos, capacidades de Origem,
técnica/Famílias, inventário, entidades/cartões/MONTAGENS, fotos/arte e caches/
recuperações, além de orquestração/conferência conjunta, latência, ativação,
novo responsável e teste completo dos executores. Não repetir fases antigas
nem apagar diários. As pendências nos registros abaixo são históricas do código
indicado em cada entrada; não reimplementar os domínios já cobertos aqui.

Bot runtime continua `26ec106`, CI 40496955301, PR 84 dependente da 83. Só docs
mudaram no consumidor; sem suíte extensa ou ZIP novo, merge em main, deploy,
Gateway, modelo pago, novo OAuth ou escrita em oficial/jogador. Próxima
implementação: GPT-6 Astra / Alto; revisão focal: Médio.

## Registro anterior: nível/base de XP e textos pessoais · 27/10

O produtor incorporou a main `9536746405f12a9e159e9173b54a2a861c0a871a`
(merge `8cb12ac`), incluindo XP base e fechamento da otimização Android.
Não reabrir desempenho. Código novo `280a7dcd0b3fb56b0a43dd6e0d88aaadcb08d634`
na [PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31), em rascunho.

- Executor privado por perfis fixos; diário/assinatura financeira v1 preservados.
- Nível inicial/base XP: escreve AH11/CZ54 pela regra e curva atuais da mesa,
  sem copiar XP antigo nem alterar fórmulas. Não distribui atributos/marcos.
- Identidade textual: 14 entradas/notas pessoais, com rótulos e espelhos
  conferidos. Fotos/arte, escolhas, recursos e inventário continuam pendentes.
- **259 cenários offline**: 101 financeiros, 80 nível/base, 78 textos.
  XP independente: 20.643 verificações/9.900 combinações sem exportação opcional.
  Essas contagens são do produtor, não da suíte de 1.314 do bot.

No fechamento, main avançou para `b0dc6aacef08b2c01a7f8a3519bbcc9bff9546ed`
(PR 37 salarial) e foi incorporada no merge `84bcd56` do produtor. Fórmulas
protegidas/alvos dos inicializadores não mudaram. 15 verificações de abertura,
95 salariais e 101 financeiras passaram após o merge. O ensaio nativo descrito
é anterior; não valida execução desse código Apps Script. Nada foi instalado.

CI final do integrado `84bcd566ae74d73bd8fdaf3889aa1ab5d7c68722`
aprovado: [40535287570](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40535287570), 27/10 às 12:53:51 Brasília.
Os 259 cenários, pacote de nove arquivos e regressões passaram; 277 fontes
Python/208 JS-GS com sintaxe válida. Run duplicado cancelado. Registro final
posterior só documental. Prova do OAuth/Apps Script completo continua pendente.

CI anterior, antes da PR 37, aprovado no código `280a7dc`:

[40534237271](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40534237271), 27/10 às 12:47:26 Brasília.
Confirmados os 259 cenários, pacote de nove arquivos sem inicializadores,
sintaxe e regressões. Run duplicado do push cancelado; registro posterior
só documental, sem repetir a bateria do bot.

A leitura Google encontrou separador `;` em G46; corrigida a guarda para
aceitar somente essa variante da fórmula conhecida. Alterar a regra continua
recusado, com regressão. Em nova cópia privada da Era, projeção dos efeitos
via Sheets API: 14 textos/notas limpos, nível 10/base 3.700, XP 3.700→3.750
com missão de 50→3.700 após retirar. 8.998 comparações de campos preservados
nos intervalos lidos sem diferença. Cópia na lixeira e aba fechada.

**Essa projeção não executou os novos perfis Apps Script**, nem seus diários,
travas ou retomadas. O ensaio financeiro anterior é do código `4f3555d`, antes
da extração e da main atual. Nenhum desses resultados atesta criação inteira,
OAuth próprio das Guias ou automações. Relatório e alvos:
[NIVEL-TEXTOS-2026-10-27.md](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/280a7dcd0b3fb56b0a43dd6e0d88aaadcb08d634/r53/inicializacao/NIVEL-TEXTOS-2026-10-27.md).

Os perfis não entram no pacote e não são chamados pelo bot. Cada domínio
retorna `criacaoDisponivel=false`; `criar_por_modelo` continua bloqueado sem
exceção. Falta orquestração e conferência final conjunta: depois de mudar o
nível, repetir o financeiro antigo deve recusar por mudança de campo protegido.
Não reiniciar fases nem apagar diários para contornar. Recuperações/editor
(inclusive caches novos `r53_versoes`/`r53_marcas_custom`), fotos, escolhas,
atributos, treinos, marcos, recursos, inventário, entidades/cartões, automações
e novo responsável ainda precisam de implementação/aceite.

Bot continua no runtime `26ec106`, CI 40496955301, PR 84 dependente da etapa 6.
Só documentação mudou no consumidor; sem nova suíte extensa ou ZIP. Não houve
merge em main, deploy, Gateway, chamada paga, novo OAuth ou escrita em
oficial/jogador. Próxima implementação: GPT-6 Astra / Alto; revisão focal: Médio.

## Registro anterior: modelo e ensaio financeiro

O modelo do servidor é a ficha do sistema com configurações extras da mesa,
conforme esclarecimento do usuário. Preservar essas regras/catálogos, sem
herdar o personagem. Não há parâmetros de criação liberados no bot.

O primeiro domínio de inicialização foi implementado em PR separada no
produtor: [Ficha PR 31](https://github.com/cupcake-mochi/Ficha---RPG-JJK/pull/31),
`codex/inicializacao-financeira-carteira`, código `4f3555d`, base `d0836390`.
É um protótipo financeiro com prévia/diário, passos separados de conteúdo,
notas e propriedades, retomada após interrupções e conferência de fórmulas.
Não integra o pacote, não é endpoint e não inicializa o personagem inteiro.
Flags do navegador não são prova de origem ou responsabilidade.

**99 cenários offline novos passaram**, mais regressões focais de salário e
missões (95 e 64 cenários/611 verificações, respectivamente). O smoke Linux
do produtor passou no mesmo SHA: run
[40505846627](https://github.com/cupcake-mochi/Ficha---RPG-JJK/actions/runs/40505846627).
A execução duplicada do push foi cancelada; a da PR passou no mesmo SHA. Não
houve falha no código por esse cancelamento. Suíte do bot não repetida: a
mudança nesta continuação do consumidor é documental; código continua `26ec106`.

Metadados/âncoras das duas oficiais relidos somente para leitura. Uma nova
cópia descartável do Ciclo foi criada pelo Drive conectado; apenas nela foi
adicionado um arquivo de ensaio, sem substituir os módulos instalados.
Código colado foi conferido integralmente contra o protótipo e o wrapper
restringe planilha/projeto ao alvo descartável. A prévia nativa concluiu em
115,013 s. Este tempo não é adequado a um comando Discord: medir e reduzir
antes de oferecer a criação. A primeira aplicação atingiu 360,813 s; a mesma operação retomou e concluiu
em 236,503 s. Leitura externa de sete intervalos completos (26.143 posições)
confirmou zero entradas/notas/erros, saldo/períodos/crédito zero e emissão
vazia. 22 campos de fórmulas/regras/nível, 16 fórmulas de XP e formato/validação
em 183 posições permaneceram iguais. Isso não prova a inicialização pessoal
inteira. Primeira cópia na lixeira e abas do ensaio fechadas.

O defeito de tempo motivou quatro passos por execução, orçamento de 210 s,
retorno incompleto retomável e eliminação de duas leituras redundantes, com
três regressões. Nenhuma conferência de conclusão foi retirada. Orçamento
não cancela chamada Google nem garante latência máxima. Segunda cópia nova com a correção: prévia 113,524 s, aplicação 283,416 s sem
timeout, repetição 150,489 s. As 17 faixas da conferência ficaram iguais depois
da repetição; sete intervalos completos sem entradas/notas/erros, totais zero,
22 campos de fórmulas/regras/nível, 16 fórmulas de XP e 183 formatos/validações
preservados. O limite de quatro escritas e o retorno por orçamento são provas
da VM; este caso nativo tinha só três diferenças e concluiu numa chamada.
Painel Google mostrou zero acionadores para a conta conectada; onOpen simples
20,962 s. Isso não certifica salário diário ou automações de novo responsável.
As duas cópias estão na lixeira, abas de ensaio e servidor loopback encerrados.
O custo de 4 min 43 s ainda exige redução e integração assíncrona permitida
antes de oferecer a criação ao jogador; não elevar o prazo do bot por rotina.
Registro detalhado: [produtor](https://github.com/cupcake-mochi/Ficha---RPG-JJK/blob/codex/inicializacao-financeira-carteira/r53/inicializacao/NATIVO-2026-10-27.md).

O protótipo conserva `criacaoDisponivel=false`, nível/XP e regra inicial da
campanha. Identidade, escolhas, progressão, inventário, cartões/MONTAGENS,
propriedades de recuperação, automações e responsabilidade ainda precisam
de implementação/aceite próprios. Não chamar a etapa 7 de concluída nem
iniciar a 8 como se a criação estivesse liberada.

Checkouts Linux no SSD registrados em RETOMADA.md; árvore do disco externo
preservada. Não houve novo OAuth das Guias, modelo pago, merge, deploy,
Gateway ou escrita em ficha oficial/de jogador nesta continuação.

## Continuação de 27/10/2026 — inventário e sondagem 2

PR 84 preservada na base da etapa 6. As duas mains do produtor foram
reconferidas e continuam nos SHAs registrados abaixo. Foi preparada a
[proposta de contrato de inicialização 1](INICIALIZACAO-PRODUTOR.md), com
registros de missão, trocas de regra, notas de identidade salarial, caixas
pendentes, propriedades/cache, preservação de fórmulas e protocolo de
falha/retomada. Preparadores existentes não são inicializadores de personagem.
Não houve edição do repositório produtor ou aplicação em planilha.

O consumidor agora consulta os metadados de grade e depois intervalos
explícitos até a última linha física dos três históricos financeiros, até
5.000 linhas por livro. Grade maior é recusada, sem voltar a uma amostra.
Também verifica entradas/notas das quatro listas de missão, O86 e as caixas
de correção. Limites de resposta/prazo preservados; chamadas somente GET.
Valores e notas não são salvos na referência: apenas sinais constantes.
Sondagem 2 é registrada e comparada na confirmação; referências anteriores
continuam identificadas como 1, sem migração de schema ou personagens.

Dez regressões novas, incluindo linhas tardias, notas sem valor, privacidade
e mudança de sinais/versão durante a confirmação. **79 testes direcionados
passaram em 15,857 s**, modelos + provedores + fluxo HTTP. **CI Linux aprovado
no código `26ec1068131a8b71a9a04688bcf8676771fd736c`: 1.314 executados,
1.313 aprovados, um opcional pulado, zero falhas, em 278,076 s**;
[run 40496955301](https://github.com/cupcake-mochi/RPG---BOT/actions/runs/40496955301).
São 32 testes novos desde a base da etapa 6. O registro posterior é apenas
documental e usa `[skip ci]` para não repetir a bateria extensa.
Não foi repetida a bateria
completa Windows, cujas limitações já estão documentadas abaixo.

Esta continuação não abriu novo piloto, não reutilizou grants/cópias descartados
e não produziu prova nativa adicional. A configuração privada das Guias segue
indisponível neste Windows; nenhuma credencial ou escopo foi recriado. A
proposta não implementa limpeza nem atesta automações/propriedades: **etapa 7
continua parcial e criação permanece bloqueada, inclusive sem sinais**.

## Entrega e validação de 26/10/2026

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
