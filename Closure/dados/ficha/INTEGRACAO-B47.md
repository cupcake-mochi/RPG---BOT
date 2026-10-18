# Integração B47 no bot · 18/10/2026

Implementação offline no projeto `Closure/`. A ficha oficial não foi editada,
nenhum Apps Script foi publicado, nenhum XLSX foi importado no Google e nenhuma
mensagem foi enviada ao Discord. Não há chamadas reais a modelos nestes testes.

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
| Atributos/Corpo/marcos | Pontos e tetos da campanha; conserva cálculos de progressão existentes | Sequência histórica de escolhas não é inferida de totais |
| `efeito.1..30.*` | Valida ligado, alvo, modo, número, fonte, conflitos; `trocar por` vence soma/Buff, inclusive zero | Fonte digitada não é aprovação. Alvos sem conta integrada ficam explicitamente não conferidos |
| Efeitos de Vida/PE/Integridade/Proteção/Defesa | Aplicados uma vez à conta independente; Proteção efetiva alimenta Defesa | Conflito impede certificação do alvo |
| Custom em todos os namespaces atuais | Preserva registros crus, valida capacidade, nomes literais/colisões, base, campos e aprovação exata | Registro inválido/sem aprovação não autoriza benefício |
| `MESTRE VIU` | Só lembrete; excluído da assinatura de conteúdo | Não substitui autorização do mestre |
| Famílias da técnica | Nove do livro + dez cadastros compartilhados; estados e contagens pelas regras autorizadas | Descrição não acrescenta números |
| Famílias das entidades | Nove vagas de cada uma; perfil da Trilha, autonomia e limites próprios; Livre integra total aberto | Não herda estado Livre/Fechada da técnica nem de outra entidade; falta de escolhas é pendência |
| Perícia/Ofício custom | 10+10 cadastros; 23/11 posições de uso; atributo, treino, especialização, ajuste e resultado; efeitos por **nome** | Presença automática não concede treino. `bonus` é ajuste, `resultado` é o total. Tudo usa o orçamento anterior |
| Perícias de entidade | Recalcula bônus por atributo e maestria, duplicatas e quantidade de treino | `buff.pericia.N` é resultado histórico, nunca somado como ajuste; TR completo não está exportado |
| TR/perícias/Ofícios do livro | Mantém cálculos de TR-v4; B47 lê seus treinos e os conta junto de custom | B47 não emite os ajustes/bônus daquela variante; não certifica resultados ausentes |
| Equipamento/carga | Reutiliza requisitos, catálogo e verificações antigas; estende equipamento estruturado aprovado | Carga integral B47 não é certificada: faltam quantidades, Volumes e ajuste da variante TR-v4 |
| Melhorias/Condições/Restrições | 30/30 compartilhadas, herança, peso/devolução, identidade, frequência, Família; Condição exige TR | Requisitos livres, aplicação contextual e interações não automatizadas ficam em revisão |
| Formas custom | 10; motor puro da entrega, campos estruturados e escadas por contexto/faixa, custo/orçamento e benefício básico | Liberação e interações especiais não cobertas não certificam dano; efeito narrativo permanece manual |
| Aptidões/Bênçãos/Talentos | 10/10 cadastros; CE, rota, requisitos estruturados, bases/aliases e orçamentos existentes | Aprendizado/Origem não exportados são pendências; total no teto de Refino usa possibilidades, sem inventar ordem histórica |
| Tipo/Talento de entidade | 10/20 cadastros, bases, CE; modos Vida/Talismã/Reserva independentes | Aquisição, alma e resultado de reserva sem campo estruturado completo ficam não conferidos |
| Origem/Caminho/Trilha custom e 25 cartões 3a | Aprovação, campos, herança declarada, números de Caminho e equipamento, ligação da Trilha | Concessões de Origem e habilidades livres não viram automação; não existe aprovação integral por cadastro |
| Magia, repertório, entidades e trunfos existentes | Reaproveita os módulos e regressões anteriores | Mantém limites já documentados de distribuição, texto, permissões e uso em campo |

O painel distingue divergência (vermelho), pendência de aprovação/informação,
parte não automatizada e valores conferidos. Qualquer limitação relevante torna
o resumo amarelo e parcial, inclusive para fixtures legadas. As páginas preservam
o campo relacionado e a âncora de regra quando disponível.

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
../.venv/bin/python -m unittest testes.test_b47_leitor testes.test_b47_integracao
../.venv/bin/python -m unittest discover -s testes
```

**Resultado na nuvem:** suíte completa com 690 testes, 689 aprovados e um online opcional pulado. Verificação focal posterior da Forma e cadastro: quatro testes aprovados. Pacote gerado sem `.env`/banco, com módulos e todos os recursos B47 presentes. Não houve recálculo Google/LibreOffice.

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

## Validação externa e publicação

Google, Discord e LibreOffice não foram usados. Git/Python/Node/testes estavam
disponíveis; acesso Git foi verificado. A conta colaboradora passou a permitir
push durante esta tarefa. A API GitHub depende da política de rede da nuvem.

Em servidor de teste, após revisão da PR e implantação **pelo operador**:

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

Não executar `construir()`/`continuar()`, editar a oficial, importar XLSX no Google,
alterar acessos, chamar modelos pagos ou reiniciar produção para esse roteiro.
