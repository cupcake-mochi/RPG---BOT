# Integração B47 no bot · 18/10/2026

**Bateria nativa preparada em 18/10:** seis cópias sintéticas calculadas no
Sheets, 8.190 chaves por XLSX e resultados locais conferidos. Roteiro em
`BATERIA-NATIVA-B47.md`. Inclui aprovação exata, MESTRE VIU sem autorização,
efeito alterado, resultado adulterado e campanha não autorizada. Encontrado
e corrigido no código o falso cadastro de Caminho/Trilha pelos menus default
de cartões vazios; **817 testes: 816 aprovados e um opcional pulado**. Esse
patch ainda não foi implantado. As cópias limpam esses menus não usados para
permitir o teste também no runtime anterior. Com autorização posterior do
Mizuki, seis cópias receberam leitura por link e quatro hashes sintéticos
foram instalados somente no servidor escolhido. Cadastro ativo relido e
conferido; sem mudar regras gerais, reiniciar ou implantar código. Os seis
links anônimos coincidem com os XLSX nas 8.190 chaves.

**Discord executado com autorização em 18/10:** 13 análises reais na versão
já publicada: seis links, seis XLSX e uma reanálise. Os seis pares devolveram
resumos idênticos: casos 01/02 sem divergências nem aprovação pendente; 03 com
quatro aprovações pendentes apesar de MESTRE VIU; 04 reabriu somente o efeito
alterado; 05 reprovou Vida 999/23; 06 reprovou a regra/total não autorizados.
As seis páginas da 02, quatro setas e seletor foram exercitados. Encerramento
após dez minutos e reabertura por nova análise foram observados. Sem chamadas
pagas, reinício, implantação do patch 65 ou alteração da oficial nesta rodada.
Evidências: `pesquisa/validacao/2026-10-18-b47-discord/`. Segunda pessoa no painel
e os demais casos ampliados do roteiro externo ainda não foram exercitados
no Discord; aprovação integral continua limitada pelo produtor e pelo mestre.

**Publicação autorizada em 18/10:** PR 64 mesclada em
`1997f25fe990eb307204365cda172aeec831969f` e ZIP implantado na Discloud.
Bot online em cinco servidores. Backup antes/depois: 67 arquivos instalados
idênticos ao ZIP; `.env` e dois bancos preservados byte a byte, integridade ok.
Memória de 1.000 MB mantida. Nessa publicação inicial o cadastro B47 de campanha
ainda não existia; posteriormente foram instaladas apenas as aprovações
sintéticas autorizadas. A bateria real por link/XLSX e navegação descrita
acima passou nessa versão; não publica o patch 65. Evidências da implantação em
`pesquisa/validacao/2026-10-18-b47-publicacao/`. A ficha oficial foi preservada.

**Checkpoint anterior de código em 18/10:** Máxima confere montagem, combinações e
herança/aprovação; montagem inválida não certifica dano. Toca a Alma simples
confere metade sem conceder permissão; a fórmula fixa do produtor fica pendente.
Quebra Coisa entra no teto, sem multiplicar dano secundário. **814 testes,
813 aprovados e um online opcional pulado**; 17 regressões passaram no ZIP.
[Retomada](../../docs/RETOMADA-B47.md). No checkpoint de testes, ainda sem merge/implantação; oficial preservada.

Implementação determinística no projeto `Closure/`. A ficha oficial não foi editada,
nenhum Apps Script foi publicado e nenhum XLSX foi importado no Google. Mensagens
sintéticas de teste foram enviadas somente após a autorização posterior registrada
acima. Não há chamadas reais a modelos nestes testes.

Checkpoint anterior de 18/10: leitura pública CSV/XLSX da B47 oficial, 8.190 chaves em
ambas e zero diferenças. Corrigido cabeçalho automático do gviz com `headers=1`;
Trilha custom herda a base aprovada para Famílias/extras; troca fixa independe
da conta-base; especialização inválida não certifica bônus. Evidências e limites
em `pesquisa/validacao/2026-10-18-b47-cobertura/`. Os remotos continuam nas três
bases abaixo. Nenhuma escrita nativa, mudança do produtor ou implantação.
Checkpoint anterior: **797 executados, 796 aprovados e um opcional pulado**, em
182,286 s; teste online de leitura executado separadamente e aprovado.

## Bases conferidas

| Projeto | SHA utilizado | Observação |
| --- | --- | --- |
| RPG---BOT | `7e4dc35209ea840549d5ccf5a0b49834da21d117` | `main` atual no início, árvore limpa |
| Ficha---RPG-JJK | `ccbd053c8f7e68f8b4ac223f721b309111d2dcc0` | `main` e `codex/configuracao-b47` iguais; fechamento prevalece sobre documentos históricos |
| JJK---Project | `e593ba8cf24ce6bbd2f517f5431a73a96610e02b` | v0.365/R52; examinado o diff desde `82878e6`, sem mudança no catálogo `dados.js` |

O bot já retinha o texto R52 de Origem, com proveniência própria no MANIFESTO.
Não se atribuiu retroativamente um commit ao texto dessa entrega anterior nem
se sincronizou o livro inteiro por conveniência. O novo código preserva cards,
personalidade, memória e mídia.

## Contrato e colisão histórica

Foram lidos os sete fragmentos JSON de ANALISE dos GS efetivamente entregues,
sem executar JavaScript nem o gerador. A extração verificou sobreposições e
encontrou **8.190 identidades únicas**: 4 cabeçalhos, 3.347 entradas,
2.642 campos de configuração, 1.419 resultados e 778 avisos.

O formato 4 consumido pelo bot vinha do rascunho de TR/perícias/carga:
5.381 chaves. O formato 4 da campanha B47 tinha 5.274 e incluía `regra.*`,
`efeito.*` e vida rolada. Não são equivalentes. Dos campos TR-v4, a B47
atual retém **4.896**, acrescenta **3.294** e não exporta as **485** adições
daquela variante paralela. A integração não inventa esses dados ausentes.

- [Manifesto B47 completo](../../src/closure_bot/recursos/b47-campos.tsv): chave, parte, origem e marcação lógica do produtor.
- [Delta por chave](MAPA-B47-DELTA.tsv): todas as 3.294 adições e 485 ausências.
- Os contratos `analise-chaves-v1.tsv`, `-v2.tsv` e `analise-chaves.tsv` continuam preservados.
- A coordenada da origem é apenas diagnóstico. Mudança física não muda identidade.
  Ordem de linhas e quantidade exata de registros não definem compatibilidade.
- Formatos 1/2 e TR-v4 comprovados continuam atendidos. O 4 de campanha e
  variantes desconhecidas recebem explicação; não são aceitos pelo número.

## Mapa de consumo e cobertura

| Campos/grupo | Tratamento no bot | Limite explícito |
| --- | --- | --- |
| Cabeçalho, identidade, campos presentes | Manifesto por chave/parte, sistema, duplicatas, erros e resultados calculados | Ficha branca/incompleta não aprova personagem; extensões desconhecidas não são certificadas |
| Textos, nomes, descrições, requisitos, escadas | Tipo semântico; preserva `007`, `1,5`, `VERDADEIRO`, `*?~`, `=` e espaços nos campos textuais | Texto não é fórmula nem concessão mecânica |
| `regra.*` e `.campanha` | Compara com cadastro **do servidor no bot**, incluindo valores efetivos e declaração; vazio difere de zero | XP manual/histórico de missões e Limiar não são comprovados pela ficha |
| Vida fixa/rolada, PE, Integridade, Proteção, Defesa | Recalcula de entradas, regras autorizadas e efeitos; dado do Caminho, rolagens ausentes/inválidas e exceções de Origem | Origem do Buff e duplicação com concessões requerem mestre; equipamento desconhecido não certifica Defesa |
| Iniciativa, Maestria, Classe, Refino gratuito, Classes 0 gratuitas e janela de Morrendo | Contas independentes; Sequelas extras, campanha, soma/troca e estados inválidos | Resultado vazio vira pendência. Quantidade de Classes 0 gratuitas não é quantidade de dados |
| CD/conjuração/ataques pessoais | Detecta totais fora de todas as possibilidades e confere trocas, inclusive zero | Seletores pessoais ausentes da exportação impedem certificar a escolha do atributo |
| Deslocamento pessoal | Confere Exaustão, possibilidades de meia marcha/parada e troca final; Buff e efeitos na ordem entregue | Carga incompleta impede certificar qual penalidade está ativa; casos invariáveis são conferidos |
| Origem publicada e capacidades | Confere vínculo de marcante/menores ao catálogo R52 e rejeita menores repetidas, sem depender dos avisos | Capacidade criada sem definição/aprovação permanece pendente; escolhas incompatíveis não certificam contas dependentes |
| Atributos/Corpo/marcos | Pontos e tetos da campanha; conserva cálculos de progressão existentes | Sequência histórica de escolhas não é inferida de totais |
| `efeito.1..30.*` | Valida ligado, alvo, modo, número, fonte, conflitos; `trocar por` vence soma/Buff, inclusive zero | Fonte digitada não é aprovação. Alvos sem conta integrada ficam explicitamente não conferidos |
| Efeitos de Vida/PE/Integridade/Proteção/Defesa/Iniciativa | Aplicados uma vez à conta independente; Proteção efetiva alimenta Defesa | Conflito, entrada inválida e linhas idênticas de mesma fonte impedem certificação do alvo |
| Custom em todos os namespaces atuais | Preserva registros crus, valida capacidade, nomes literais/colisões, base, campos e aprovação exata | Registro inválido/sem aprovação não autoriza benefício |
| `MESTRE VIU` | Só lembrete; excluído da assinatura de conteúdo | Não substitui autorização do mestre |
| Famílias da técnica | Nove do livro + dez cadastros compartilhados; estados e contagens pelas regras autorizadas | Descrição não acrescenta números |
| Famílias das entidades | Nove vagas de cada uma; perfil da Trilha, efeito de famílias da trilha antes da autonomia, limites próprios; Livre integra total aberto | Não herda estado Livre/Fechada da técnica nem de outra entidade; falta de escolhas é pendência; fração/conflito/teto acima de nove é erro |
| Trilha custom com base | Valida BASE DO LIVRO e vincula o registro publicado à aprovação; usa o perfil herdado em Famílias/extras da Principal | Sem aprovação/base válida, conta dependente não certificada; Nenhuma/vazio não herda. Texto por nível não vira concessão; teto/ativas não exportados continuam parciais |
| Perícia/Ofício custom | 10+10 cadastros; 23/11 posições de uso; atributo, treino, especialização, ajuste e resultado; efeitos por **nome** | Presença automática não concede treino. `bonus` é ajuste, `resultado` é o total. Tudo usa o orçamento anterior |
| Perícias de entidade | Recalcula bônus por atributo e maestria, duplicatas e quantidade de treino | `buff.pericia.N` é resultado histórico, nunca somado como ajuste; TR completo não está exportado |
| TR/perícias/Ofícios do livro | Mantém cálculos de TR-v4; B47 confere dois TR treinados e orçamentos compartilhados com custom; TR escolhido da entidade é independente | B47 não emite os ajustes/bônus pessoais nem os resultados de TR da entidade; não certifica resultados ausentes |
| Equipamento/carga | Reutiliza requisitos, catálogo e verificações antigas; estende equipamento estruturado aprovado | Carga integral B47 não é certificada: faltam quantidades, Volumes e ajuste da variante TR-v4 |
| Melhorias/Condições/Restrições | 30/30 compartilhadas, herança, peso/devolução, identidade, frequência, Família; Condição exige TR | Requisitos livres, aplicação contextual e interações não automatizadas ficam em revisão |
| Restrição custom embutida em Forma | Compila a dependência validada, exige aprovação própria e vincula a assinatura da Forma à definição da Restrição | Mudar a dependência invalida ambas as aprovações; MESTRE VIU continua irrelevante para autorização |
| Consistência da entidade | Distribuição completa por entradas individuais, resumo correspondente e marcos; entidade inválida não certifica números/testes/habilidades dependentes | Pendência/erro fica restrito à entidade afetada; resultados da outra entidade continuam independentes |
| Formas custom | 10; motor puro, escadas, custos, desconto da Forma Livre pessoal, Liberação/Remate, adicionais, total de Rajada/Mais Um/Junto, Alma simples e bônus de resolução da entidade; renomeação pura reaproveita a base e identidade conserva incompatibilidades | Alma combinada com adicionais/distribuição, distribuição e permissões de uso ainda exigem revisão; efeito narrativo permanece manual |
| Controle na entidade | CD por saldo recalculado nas Formas publicadas/custom, bônus apenas quando há Melhoria da Família Controle; Precisão herdada preservada | Saldo desconhecido ou uma única apresentação que não separe as CDs continua parcial. Fórmula atual sem o +2 devido recebe pendência precisa, nunca certificação |
| Aptidões/Bênçãos/Talentos | 10/10 cadastros; CE, rota, requisitos estruturados, bases/aliases e orçamentos existentes | Aprendizado/Origem não exportados são pendências; total no teto de Refino usa possibilidades, sem inventar ordem histórica |
| Tipo/Talento de entidade | 10/20 cadastros, bases, CE; modos Vida/Talismã/Reserva independentes | Aquisição, alma e resultado de reserva sem campo estruturado completo ficam não conferidos |
| Origem/Caminho/Trilha custom e 25 cartões 3a | Aprovação, campos, rota compatível e pacote da Origem herdada nas contas antigas; números de Caminho/equipamento; ligação da Trilha; menor exige marcante correspondente | Concessões novas de Origem sem base e habilidades livres não viram automação; não existe aprovação integral por cadastro |
| Ferramenta amaldiçoada e Reserva Profunda herdadas | Ferramenta vincula hash à base, herda Proteção/ocupação de mãos e aceita Volume zero; Reserva Profunda conserva ganho da base uma vez, inclusive via efeito identificado | Estigma/desgaste/efeitos livres e Buff de PE com origem ambígua exigem mestre; alias de arma de duas mãos não libera escudo |
| Magia, repertório, entidades e trunfos existentes | Reaproveita os módulos e regressões anteriores | Mantém limites já documentados de distribuição, texto, permissões e uso em campo |

O painel distingue divergência (vermelho), pendência de aprovação/informação,
parte não automatizada e valores conferidos. Qualquer limitação relevante torna
o resumo amarelo e parcial, inclusive para fixtures legadas. As páginas preservam
o campo relacionado e a âncora de regra quando disponível.

Lacunas do contrato e possível defeito de critério com curingas no produtor têm
reprodução e correção proposta em [LACUNAS-PRODUTOR-B47.md](LACUNAS-PRODUTOR-B47.md).
Ampliação concreta de campos/semântica/testes separada em
[PROPOSTA-CONTRATO-B47.md](PROPOSTA-CONTRATO-B47.md), ainda não implementada.
Não foram corrigidas por permissividade no bot nem por edição da oficial.

## Aprovação e campanha

O comando público e `GC:ficha` leem `src/var/ficha-campanhas.json` por ID do
servidor. Arquivo ausente usa livro e nenhum custom aprovado. Arquivo inválido
interrompe a análise, sem cair silenciosamente no padrão. Não se lê autorização
da ANALISE nem de um anexo enviado pelo jogador.

O mecanismo `Aprovados` existente foi reaproveitado; assinaturas B47 são
`b47-v2:SHA256` de tipo, nome, campos crus relevantes e definição da base.
Não se apagam acentos/pontuação ou se confundem falso/zero/vazio. Mudar conteúdo
ou base invalida a assinatura. O cadastro retém hash e identificação da
aprovação; não retém a ficha. Requer operação por alguém autorizado a manter
o bot, depois da decisão do mestre. Não é um comando público de jogador.

De dentro de `Closure/`:

```bash
.venv/bin/python ferramentas/ficha_campanha.py inspecionar --servidor ID --ficha ANALISE.csv
.venv/bin/python ferramentas/ficha_campanha.py aprovar --servidor ID --ficha ANALISE.csv --campo custom.melhoria.1 --por 'mestre/registro da decisão'
.venv/bin/python ferramentas/ficha_campanha.py aprovar --servidor ID --ficha ANALISE.csv --campo efeito.1 --por 'mestre/registro da decisão'
.venv/bin/python ferramentas/ficha_campanha.py regra --servidor ID --nome atributos_pontos --valor 10
.venv/bin/python ferramentas/ficha_campanha.py regra --servidor ID --nome vida_rolada --valor '"Sim"'
```

Também aceita XLSX calculado em `--ficha`. `ID` e caminho são substituídos pelo
operador; arquivos de jogadores permanecem fora do Git. Preserve esse cadastro
local junto do estado operacional ao publicar o bot. A ferramenta não conecta
ao Discord, não altera a planilha e não implanta nada.

## Validação e regressões

Comandos de dentro de `Closure/src/`:

```bash
../.venv/bin/python -m unittest testes.test_b47_leitor testes.test_b47_integracao testes.test_b47_derivados testes.test_b47_revisao
../.venv/bin/python -m unittest discover -s testes
```

O resultado vigente desta continuação fica no relatório de 18/10 indicado no
início; os números deste parágrafo são checkpoints anteriores.
**Primeiro fechamento na nuvem:** 694 testes, 693 aprovados e um online opcional
pulado. **Checkpoint 7015c80: 784 testes, 783 aprovados e um online opcional pulado**,
em 108,989 s. São 12 regressões adicionais nesta continuação; os casos anteriores
de dependências, distribuição, Controle e contas/herança continuam na suíte.
Estado de empacotamento em `docs/RETOMADA-B47.md`. Não houve recálculo Google/LibreOffice.

As fixtures B47 são sintéticas e montadas em memória pelo manifesto. Não há
cópia de ficha privada nem dependência do PC. Motor puro de personagem foi
internalizado da fonte indicada no cabeçalho, com catálogo estático da mesma
base; não importa o gerador no runtime. As demais contas são refeitas pelos
módulos do bot e confrontadas por casos válidos/adulterados/incompletos.

Falhas investigadas durante a implementação:

1. As fixtures XLSX históricas contêm `#NAME?` em inventário agregado. Os testes
   mecânicos continuam úteis, mas esses campos são declarados não conferidos.
   B47 rejeita erros de fórmula; não se passou a certificar os erros antigos.
2. Expectativa antiga de painel verde com partes não conferidas contrariava o
   requisito atual. A revisão exige que as mesmas limitações existam e que o
   painel seja amarelo/parcial; os números esperados foram preservados.
3. O dublê antigo de interação não tinha `guild_id`. Foi completado com um ID
   sintético para testar a seleção da campanha, como a interação real oferece.
4. A primeira fixture nova omitia `tecnica.rota.nome`. Corrigiu-se a fixture
   para emitir Fundamento, sem relaxar a conferência desse resultado.
5. A orientação legada de PE da Origem só conhecia Buff. A B47 confere o
   acréscimo uma única vez entre Buff e efeitos identificados; não recomenda
   duplicar um ganho já aplicado. Regressões cobrem vínculo de Origem e menores
   repetidas sem aviso, além do campo estruturado EXIGE TR da Melhoria.
6. Na continuação, a expectativa textual de uma Forma apenas renomeada mudou
   para a saída do verificador da base. O número permanece 3d8. Uma fixture nova
   de Explosão Classe 2 tinha orçamento errado: são seis pontos menos um da
   Forma Livre, portanto 5d8; o alcance publicado é 18 m. Corrigiu-se a fixture
   com essa derivação, preservando as contas do contrato.
7. Os novos testes reproduziram defeitos do consumidor: efeito de Famílias
   ignorado; falta de desconto da Forma Livre; hash de Ferramenta sem base
   porque um campo vazio mascarava o seletor correto; duas mãos/Proteção não
   propagadas ao alias; e certificação após erro na montagem custom. Foram
   corrigidos no código, sem relaxar as asserções de adulteração.
8. PE de Reserva Profunda agora considera a identidade herdada, evita somar
   novamente o ganho em efeito identificado e deixa Buff ambíguo pendente.
   Efeitos literalmente duplicados de uma fonte não são autorizados em dobro
   por compartilhar um único hash de aprovação.
9. A primeira fixture de resolução da entidade usava `FORÇA`; o seletor
   publicado usa `Força`, como o contrato antigo e a conta compartilhada.
   Corrigiu-se a entrada da fixture e completaram-se seu dano/alcance; o teste
   exige aprovação das contas e detecta `Ataque +999`, preservando a regra.
10. Revisão seguinte: a fixture da incompatibilidade de Inescapável usava
    Classe 2 no nível 2. Com a interrupção correta após Classe inválida, esse
    caso deixou de alcançar a regra que queria testar. Ajustou-se apenas o
    nível sintético para 6; a mesma asserção de incompatibilidade permanece.
11. As regressões novas reproduzem: frequência perdida ao herdar Condicional
    com sufixo de peso; Restrição embutida não compilada nem vinculada à
    aprovação; duas Condições Pesadas e Inescapável sem dano escapando do motor
    custom; e números dependentes conferidos após distribuição inválida.
    Corrigiu-se o código. Uma Melhoria pesada de Controle não é presumida
    Condição: o limite usa modalidade e identidade da base.
12. Tudo ou Nada agora considera TR acrescentado por Melhoria estruturada.
    Essa é uma adaptação explícita do motor puro internalizado, documentada
    no cabeçalho; o padrão do motor continua compatível e nenhuma prosa é
    interpretada. O seletor/número exportado não determina o saldo de Controle.
13. O helper `testar` da bateria nova foi renomeado para `analisar`, pois o
    unittest coleta qualquer método iniciado por `test`. Não se alterou
    nenhuma expectativa mecânica para corrigir esse erro de coleta.
14. A continuação reproduziu uma interrupção real: efeito com número inválido
    ou duplicado na CD/ataque levava `None` ao formatador de possibilidades.
    Agora a caixa inválida bloqueia somente a conta dependente, mantendo o
    diagnóstico da linha do efeito e as outras contas independentes. Troca
    válida não encobre uma segunda linha inválida na mesma caixa.
15. Menores publicadas só tinham o vínculo com a Origem conferido, sem seu
    requisito estruturado `exige`. Conselho Interior com Conflito e as
    menores exclusivas de outro clã eram aceitos. As seis exigências atuais
    são verificadas nas duas vagas, em Sem Técnica e em Origem custom com
    base. Marcante vazia é pendência de informação; incompatível é erro,
    impedindo certificação das contas dependentes da Origem. Prosa editada
    pelo jogador não altera o requisito. Os testes novos falharam no código
    anterior e passaram com a correção, sem mudar expectativas para verde.
16. CSV com campo acima do limite do parser lançava `csv.Error` fora do
    tratamento de leitura. O leitor devolve `FichaIlegivel` para esse caso e
    CSV truncado, conservando aspas/quebras/literais de CSV válido. Não se
    aumentou o limite global para aceitar a entrada excessiva.

## Validação externa e publicação

Na primeira continuação, Google foi usado somente para leitura pública de
CSV/XLSX. Depois, com autorização, seis cópias foram preenchidas e calculadas no
Sheets, exportadas e exercitadas no Discord: os 13 comandos descritos acima.
Git, Python, Node, Sheets e navegador autenticado estavam disponíveis; não foi
necessário LibreOffice. Acesso Git/push conferido. A evidência agregada fica em
`pesquisa/validacao/2026-10-18-b47-discord/`; capturas e links das respostas ficam
na entrega local, sem cadastro operacional ou IDs de Discord publicados no Git.

Roteiro detalhado: [ROTEIRO-EXTERNO-B47.md](ROTEIRO-EXTERNO-B47.md).
Os itens abaixo são o roteiro ampliado. A bateria de seis casos cobriu base,
custom/aprovação exata, efeito alterado, resultado adulterado, campanha e painel;
os demais cenários não passam a ser nativamente comprovados por essa rodada.
Usar a versão já publicada, sem repetir implantação:

1. Preservar banco/chave/cadastro de campanha e garantir uma única instância.
2. `/ficha analisar` e `GC:ficha` com uma cópia sintética B47 calculada, primeiro
   por link público e depois por XLSX baixado. Conferir o mesmo resumo/páginas.
3. Alterar um resultado e comprovar vermelho; retirar uma chave e comprovar
   exportação incompleta. Ficha branca nunca deve obter aprovação integral.
4. Conferir custom sem aprovação, aprovar a definição pelo cadastro do bot e
   conferir novamente; mudar um campo deve reabrir a pendência.
5. Exercitar efeitos somar/trocar zero/conflito, regra divergente, autonomia e
   Famílias diferentes em duas entidades, treino e Ofício custom nos limites.
6. Conferir seletor/setas, páginas de pendências e limites. Não interpretar
   conferência parcial como autorização para jogo.
7. Escolher Conselho Interior com Conflito e uma menor exclusiva de outro clã;
   conferir campo/requisito no painel. Deixar a marcante vazia deve mostrar
   pendência. Um efeito com valor não numérico em CD/ataque deve gerar um
   diagnóstico e preservar as demais páginas, sem falha do comando.

Não executar `construir()`/`continuar()`, editar a oficial, importar XLSX no Google,
alterar acessos, chamar modelos pagos ou reiniciar produção para esse roteiro.
