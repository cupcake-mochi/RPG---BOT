# src: código do bot

**Continuação B47 em 18/10:** o link CSV declara `headers=1`; a leitura real da
oficial e o XLSX exportado retornaram 8.190 chaves e Campos/Resultado iguais,
sem escrita. Trilha custom usa a base aprovada em Famílias/extras; troca fixa
não depende da conta-base incompleta; especialização inválida não certifica
bônus/treinos. Testes finais, pacote e limitações em
[`RETOMADA-B47.md`](../docs/RETOMADA-B47.md). Antes de concluir publicação,
seguir [`ROTEIRO-EXTERNO-B47.md`](../dados/ficha/ROTEIRO-EXTERNO-B47.md).
Cards, memória, mídia e rotas de modelos preservados.
Suíte final: 797 testes, 796 aprovados e um online opcional pulado; teste
online separado aprovado. Pacote final e roteiro ainda não foram implantados.

**Integração B47 (18/10/2026):** ANALISE 11 por chave, leitor tipado, regras por servidor, efeitos e custom aprovados por definição exata. Cadastro local em `src/var/ficha-campanhas.json`; ferramenta do operador e comandos de teste em [`../dados/ficha/INTEGRACAO-B47.md`](../dados/ficha/INTEGRACAO-B47.md). Preserve esse arquivo na publicação junto do estado operacional. A B47 não emite as 485 adições exclusivas do TR-v4; os limites ficam visíveis no painel. Estados e formatos antigos abaixo são históricos. Não houve implantação nem validação Discord/Google nesta integração.

Continuação: `ficha_derivados_b47.py` confere Iniciativa, progressão numérica,
Sequelas/janela de Morrendo e escolhas de TR. CD/ataques/deslocamento distinguem
trocas conferíveis, contradições e entradas ausentes. Herança de Origem/Forma/
Ferramenta reutiliza contas da base; aprovação não executa prosa. Regressões:
`../.venv/bin/python -m unittest testes.test_b47_leitor testes.test_b47_integracao testes.test_b47_derivados testes.test_b47_revisao`
(de `Closure/src/`); suíte completa: `../.venv/bin/python -m unittest discover -s testes`.

Menores publicadas agora conferem também a marcante exigida pelo catálogo,
incluindo clã/modalidade, Sem Técnica e Origem custom herdada. Marcante vazia
é pendência. Efeitos inválidos em CD/ataques preservam as outras contas e o
painel; CSV malformado/excessivo recebe erro de leitura, sem alterar os limites.

A revisão seguinte acrescenta dependências aprovadas de Restrições embutidas,
limites por identidade/modalidade, bloqueio de contas de entidade com distribuição
inválida e CD de Controle por saldo recalculado. O motor puro interno recebe
contexto explícito de TR de Melhorias. Checkpoint anterior: 784 testes, 783
aprovados e um opcional pulado; estado detalhado em [`RETOMADA-B47.md`](../docs/RETOMADA-B47.md).

**Voz das reações v22 (15/10):** Mizuki esclareceu que o limite de conteúdo não deve neutralizar a personalidade. A orientação usa a voz/reações do card, inclusive humor, ironia, reserva ou crítica quando couberem, e retira a expressão parte neutra do pedido. Cards, comandos, ativação e limites preservados. Sem chamadas pagas; naturalidade depende do piloto. Relatório em `pesquisa/validacao/2026-10-15-voz-reacoes-v22/relatorio.txt`.

**Estado local do modo adulto v21 (15/10):** os comandos agora destacam se o modo está ativo no canal atual e explicam opção desligada, falta de marcação NSFW ou restrição a outro canal. Mesma decisão usada na conversa. A marcação 18+ continua necessária para o modo adulto; reconhecer personagem e comentar arte de forma neutra não exige entrar em interação sexual. Orientação evita desvio automático para RPG. 642 testes passaram e um online opcional foi pulado; 16 passaram no código do ZIP. Sem chamadas pagas, mudança de card ou marcação automática de canais. Relatório em `pesquisa/validacao/2026-10-15-nsfw-status-v21/relatorio.txt`.

**Reações adultas na v20 (15/10):** `/responder_nsfw ativar:Sim/Não` controla por servidor; `/nsfw_canal canal:#chat` restringe a um canal e seus tópicos, e `todos:Sim` remove essa restrição. Sem opção, ambos consultam o estado. Exige Gerenciar servidor, começa desligado, persiste no SQLite existente e só vale em canais marcados NSFW pelo Discord. O canal onde o comando foi usado não define a restrição. Permite reação/opinião adulta não gráfica, sem ERP, encenação sexual ou submissão; não muda os filtros do Google. Orientação geral evita inventar regras do servidor, dar broncas ou mandar apagar arquivos por suposição. Cards e rotas preservados. Validação final: 638 testes passaram, um online opcional pulado; 41 testes no código do ZIP passaram. Zero chamadas pagas; naturalidade depende do piloto. Relatório em `pesquisa/validacao/2026-10-15-gif-previas-v20/relatorio.txt`.

**Prévias e reconhecimento v20 (15/10):** links curtos/expirados de anexo do Discord que dão 403/404 podem usar outro endereço da prévia, validado como o mesmo arquivo. Tenor reconhece media1.tenor.com, prioriza GIF, identifica aliases pelo ID e pode ler metadados da página pública quando falta prévia. As duas mensagens reais fornecidas passaram na preparação, sem Gemini; causa temporal da falha original do Tenor não foi demonstrada. Falhas agora registram etapa/status sem conteúdo. A orientação visual também reconhece representações de si/da outra guia quando identificáveis, sem exigir fotografia, trocar de identidade ou inventar experiências. Cards preservados; acerto/naturalidade ainda precisam de piloto. Relatório em `pesquisa/validacao/2026-10-15-gif-previas-v20/relatorio.txt`.

**GIFs e conversa v19 (15/10):** links diretos de GIF em anexos do Discord entram na mesma análise do seletor, preservando a URL assinada e sem esperar uma prévia. O exemplo enviado pelo Mizuki foi baixado e preparado localmente em dois quadros; nenhuma chamada ao modelo. A orientação visual agora acompanha a intenção da mensagem: reação/comentário recebe conversa; descrição continua disponível quando pedida. Cards preservados; o efeito nas falas ainda exige piloto. Tempos de prompt, preparo e modelo entram nos logs sem conteúdo/URL. Mizuki confirmou GIFs do seletor na v18. Relatório em `pesquisa/validacao/2026-10-15-gif-conversa-v19/relatorio.txt`.

**GIFs do seletor v18 (15/10):** suporte às prévias de Klipy/Tenor/Giphy entregues pelo Discord, incluindo GIF em MP4, com até três quadros e sem áudio. Uma releitura limitada aguarda a prévia quando ela chega depois da mensagem. Usa a mesma ativação `MIDIA_ATIVA=1`, limites e rota paga da mídia; não exige chave nova. Validação local e limites em `pesquisa/validacao/2026-10-15-gif-seletor-v18/relatorio.txt`. O GIF real do Klipy ainda precisa de reteste na Discloud; não houve chamada paga.

**Áudio v17 e política (15/10):** medição local de tons estáveis e instrução de escuta preparadas, sem alterar o áudio enviado ou os cards. Três bipes reconhecidos pelo analisador local; ganho nas respostas ainda não medido. Comparação v16/v17 de 24 chamadas preparada, aguardando aprovação de custo; zero chamadas nesta preparação. 593 testes locais passaram, um online opcional pulado. Política publicada e relida no gist existente. Mídia continua desligada por padrão; sem implantação. Relatório em `pesquisa/validacao/2026-10-15-audio-v17/relatorio.txt`.

**Silêncio v16 (15/10):** áudio convertido totalmente zerado é identificado localmente. Pedidos simples de escuta/transcrição recebem aviso sem Gemini; perguntas adicionais em texto mantêm o fluxo normal com a nota factual, sem enviar áudio. Sinal baixo não nulo não é descartado. 75 testes direcionados passaram, zero chamadas reais. Bipes continuam falhando na amostra anterior; a nota 14/18 da v15 não mudou. Pacote `src/var/closure-lab-midia-v16.zip`, desligado por padrão, sem implantação. Fila atual em `docs/FILA-ATUAL.txt`; detalhes em `pesquisa/validacao/2026-10-15-silencio-v16/relatorio.txt`.

**Mídia v1 experimental (15/10):** imagens/GIFs anexados e áudios de até 30 s implementados; desligados por padrão (`MIDIA_ATIVA=0`, canais opcionais em `MIDIA_CANAIS`). Bateria aprovada e encerrada: 18 respostas completas, 14 critérios atendidos; imagens/GIFs 10/10, áudio 4/8. Bipes e silêncio falharam nas duas guias, portanto áudio permanece experimental. Custo cheio estimado US$ 0,1800225, sem uso incerto ou repetição; não há autorização residual. 584 testes locais passaram e um online opcional foi pulado. Relatório e roteiro em `pesquisa/validacao/2026-10-15-midia/relatorio.txt` e `teste-no-discord.txt`. Arquivos só no pedido atual, pela Vertex Flash, sem análise de vídeos/GIFs por link. .env, cards, CONFIGURAÇÃO e Discloud preservados; política local atualizada, gist público pendente. Mizuki confirmou a memória da v14 após novo Commit.

**Exclusão durante respostas (15/10):** apagar dados agora invalida conversas e fatos antigos ainda em processamento; oito testes novos e regressão reproduzida em cinco cenários no código anterior. Marcadores temporários, sem migração do banco. Resposta já em trânsito pode chegar ao Discord, mas não repõe texto no banco. Imagens/GIFs/vídeos continuam sem análise visual; proposta em `pesquisa/propostas/midia-visual/proposta.txt`. Relatório em `pesquisa/validacao/2026-10-15-exclusao-em-andamento/relatorio.txt`. Sem consumo pago ou implantação.

**R52 e revisão de preços (15/10):** entrega local aprovada pelo Mizuki integrada pelo sincronizador com `--entrega-livro`. O repositório do sistema ainda está em R51/v0.364: o manifesto registra hashes do texto/PDF R52, commit do catálogo e ausência de commit do livro novo. Apenas `origens--legado-criar` mudou, mantendo 511 blocos. Menores e Legados podem ser criados; marcantes seguem as opções publicadas, com a exceção da Restrição corporal; família própria do Descendente usa modalidade publicada. Busca de preço considera a coluna Preço, incluindo tabelas de itens/proteções e nomes curtos; “Pé de cabra” é preservado pelo filtro. Relatório: `pesquisa/validacao/2026-10-15-precos-origens/relatorio.txt`. Memória/mídia v12 continuam incluídas. Sem chamadas ao modelo, alteração de cards, CONFIGURAÇÃO ou implantação.

**Revisão de memória, mídia e preços (15/10):** conversa recente agora usa o SQLite e a cifra existentes, mantendo 12 turnos por canal/personagem, 30 minutos sem conversa e corte às 4h30; limpeza periódica e remoção do fio pelo comando de apagar dados. Reinício não recupera conversas já perdidas nem dispensa preservar banco/chave na hospedagem. Identificação textual de até dois links YouTube por mensagem via oEmbed, com cache, timeout e prévia do Discord como reserva; sem áudio/vídeo/imagem, sem API de modelo extra. Metadados acompanham o histórico sem entrar na busca do livro ou na reflexão. Preço de item nomeado prioriza a tabela; reproduzida/corrigida a mensagem longa sobre música e katana. Livro R51 e cards preservados. Mizuki vai corrigir a regra de Origem no repositório do sistema; aguardar essa alteração antes de sincronizar. Sem CONFIGURAÇÃO ou implantação. Detalhes em `pesquisa/validacao/2026-10-15-memoria-midia-precos/relatorio.txt`.

Esqueleto da fase 1 do `docs/PLANEJAMENTO.md`, escrito em 13/10/2026. O bot antigo em
`../../Closure Legado/` serve só de consulta.

**O que já faz:** sobe, responde `/ping` lendo o `MANIFESTO.json`, decide quem responde a cada mensagem
(por horário e pelo nome chamado), monta o pedido com card, lorebook, livro, estado e ficha da pessoa, chama o
modelo e envia a fala com o nome e o avatar de cada personagem. Roda na Discloud desde 13/10.
Em 14/10, Mizuki confirmou os testes de ficha depois de Commit e Rebuild, incluindo as quatro novas cópias
ANALISE 2, e cinco testes de consulta no chat. Mizuki também confirmou o painel por páginas às 23h05.

**Confirmação e filtro, 15/10:** Mizuki confirmou por captura os cinco resumos das cópias nativas de TR/perícias/carga: verde, vermelho para Vigor 999, amarelo para treino faltante, domada verde e Corda/carga amarelas. A busca v11 filtra usos cotidianos explícitos sem alterar a mensagem original entregue à guia. A auditoria offline dos 48 pedidos antigos remove as fontes dos 12 ambíguos e mantém idênticos 16 pedidos de regra e seis turnos de Origem. 537 testes executados: 536 passaram, um online opcional pulado; QuickJS/Node 14/14, fontes de títulos 425/425. Não houve novas chamadas ao modelo. Relatório `../pesquisa/validacao/2026-10-15-consulta-livro-v11/relatorio.txt`; pacote `var/closure-lab-consulta-v11.zip`, sem `.env`. CONFIGURAÇÃO segue separada.

**Ficha:** formatos 1, 2 e 4 aceitos. ANALISE 4 tem 5.381 chaves, com as 4.896 anteriores preservadas. O formato 3 pertence à implementação paralela de CONFIGURAÇÃO e não é aceito sem integrar suas regras. `ficha_entidade.py` refaz atributos, vida com
Buff, Defesa reconhecida, acerto desarmado, CD e deslocamento-base. `ficha_magia.py` lê Famílias exatas,
Classe 0 e Máxima; confere entrada carregada/retorno e CE dos Talentos por ganho. Quatro cópias preenchidas
foram calculadas no Google e relidas localmente. Não é correção integral de todo efeito, Domínio ou custom;
limites em `../dados/ficha/ENTRADAS-FALTANTES-ANALISE.txt`. Sem Gemini pago nesta rodada.

**Continuação de 15/10:** equipamento tabelado tem requisitos refeitos sem depender dos avisos da ficha.
Entidades com arma conhecida recebem Defesa e acerto conferidos; falta de treino/Força é pendência,
sem retirar proteção. Extras da Principal não acumulam carta e Talento; CE própria explícita respeita
o ganho. Trunfos da domada usam seu nível fixo, tabelas próprias e vagas de especiais para Domínio.
Ataque/CD das habilidades vêm das entradas, incluindo Precisão, sem usar os resultados calculados.
Reserva Profunda prevê o acréscimo por Classe; o Buff legado exige revisão para não contar duas vezes.
Essa etapa foi seguida pela conferência de TR/perícias e carga descrita abaixo. Texto/custom e efeitos
condicionais continuam parciais. CONFIGURAÇÃO está no outro chat; não foi integrada nesta entrega.

**TR/perícias e carga, 15/10:** `ficha_testes.py` refaz Maestria pelo nível, bônus dos quatro TR,
23 perícias e 11 Ofícios, especialização, pontos de atributo e quantidades de treino. Nas entidades, usa
atributos próprios e Maestria do dono. O antigo `buff.pericia.N` não é ajuste: permanece preservado no
contrato e os novos resultados são `pericia.N.bonus`. `ficha_carga.py` soma posições/quantidades do
inventário, uniforme vestido e armazenamento das entidades. Volume tabelado prevalece; livre é declarado
e vai ao mestre. Faltas geram pendência amarela; valores adulterados reprovam. Fórmulas legadas exatas
(Corda/Porte Incomum) recebem pendência. Origem temporal dos treinos, autorizações, anatomia e custom
continuam manuais. Três fichas geradas/recalculadas no LibreOffice cobrem os fluxos pessoais e domada.
A validação local soma 502 casos: 501 aprovados, um online opcional não executado.
A ampliação do gerador está separada da CONFIGURAÇÃO; antes de juntar, preservar os dois conjuntos de
chaves, escolher uma única versão final e regenerar os contratos/testes. Detalhes no relatório
`../pesquisa/validacao/2026-10-15-ficha-tr-pericias/relatorio.txt`.

**Painel de ficha:** resumo, revisão, TR/perícias, habilidades, invocações e limites em páginas do mesmo embed.
`ficha_paginacao.py` controla o seletor e as quatro setas; qualquer pessoa no canal pode folhear sem nova
leitura ou cálculo. Dez minutos sem interação encerram os controles e devolvem o resumo à mensagem.
Depois disso, rode a análise novamente para abrir. Não persiste a ficha ou as páginas em banco; após reinício
do bot, os controles antigos também precisam de nova análise. Funciona em `/ficha analisar` e `GC:ficha`.

## Arquivos

| Arquivo | O que faz |
| ------- | --------- |
| `closure_bot/plantao.py` | Quem responde: turno por horário, nome chamado, as duas citadas. Não conhece o Discord. A regra tem dono: `dados/personagem/servidor.md` e os `vida.md` |
| `closure_bot/config.py` | Lê o `.env` da pasta `Closure/` (o ambiente vence o arquivo) |
| `closure_bot/registro.py` | SQLite: `chamadas_api`, `gatilhos`, `mensagens_bot`, `paineis_clima` (um por servidor), `falas` (as últimas respostas de cada personagem por canal), `paciencia`, `fichas` (o que elas guardam de cada pessoa) e `mensagens_do_dia` (o texto de quem chamou, só até as 4h30) |
| `closure_bot/vida.py` | O estado do momento, pelo desenho dos `vida.md`: carga, movimento do canal, paciência, intimidade; monta o bloco de estado e as linhas a mais do lembrete |
| `closure_bot/reflexao.py` | Reflexão diária: tira das mensagens do dia os fatos de cada pessoa, passa pela peneira e apaga o texto |
| `closure_bot/cogs/pessoa.py` | `/meus_dados`, `/meus_pronomes`, `/meu_fato`, `/esquecer_fato`, `/apagar_meus_dados`, e o laço da reflexão às 4h30 |
| `closure_bot/dados.py` | Lê o manifesto das regras e o nome e a versão de cada card. Não escreve em `dados/` |
| `closure_bot/carteiro.py` | Envia a fala pelo webhook do canal, com nome e avatar por mensagem, e guarda o ID |
| `closure_bot/bot.py` | Junta tudo e carrega os módulos |
| `closure_bot/clima.py` | Clima de Tóquio ou de outro lugar pela Open-Meteo (sem chave), com cache de 15 min; acha o lugar pelo nome, diz se a mensagem puxa o assunto e monta a linha do bloco 4 |
| `closure_bot/cogs/clima.py` | `/clima [lugar]`, `/clima_canal`, `/clima_canal_desligar` e o painel diário de Tóquio, um canal por servidor |
| `closure_bot/modelo.py` | A chamada à IA numa camada só: fila de `provedor:modelo` com reserva (Vertex AI e AI Studio), e cada tentativa registrada com tokens e latência |
| `closure_bot/cogs/admin.py` | `/ajuda` (a lista sai dos próprios comandos, e cada pessoa só vê os que pode usar), `/ping`, `/status`, `/teste_webhook` (este só pro dono) |
| `closure_bot/cogs/atalho.py` | Comandos escritos no chat com `GC:` na frente (`GC:ajuda`, `GC:clima Quioto`, `GC:ping`, `GC:status`). Os que mexem em dado da pessoa ficam só na barra, onde a resposta é só pra ela |
| `closure_bot/cogs/chat.py` | Escuta as mensagens, decide quem responde, monta o pedido, chama o modelo e envia a fala |
| `closure_bot/conversa.py` | Conversa recente no SQLite existente (30 min sem conversa, 12 turnos, corte às 4h30); restaura após reiniciar |
| `closure_bot/midia.py` | Identificação textual de YouTube e prévias; cache limitado, sem leitura de áudio/vídeo/imagem |
| `closure_bot/prompt.py` | Monta o pedido ao modelo pela ponte do site, com o JavaScript da página rodando dentro do Python; é o único ponto que depende dela |
| `../iniciar.py`, `../discloud.config`, `../ferramentas/empacotar.py` | Início, configuração e pacote pra hospedagem |
| `closure_bot/cogs/regras.py` | `/livro` (e `GC:livro`, `GC:sistema`): link do livro de regras em PDF, com quem está de plantão. A consulta por comando é da fase 2 |
| `closure_bot/ficha_leitor.py` | Lê a aba oculta `ANALISE` da ficha, do `.xlsx` baixado (openpyxl) ou do link aberto (CSV), e normaliza os valores (fase 3) |
| `closure_bot/ficha_corretor.py` | Confere a ficha sem IA: formato, nomes, vida, PE, Integridade, proteção, Defesa e avisos. Chama as contas de montagem de `ficha_magia.py`. Regras de campanha e custom continuam só na estrutura, até CONFIGURAÇÃO |
| `closure_bot/ficha_repertorio.py` | Recalcula capacidade e ocupação do repertório, Categoria/nível dos Talentos, concessões de Leque/Origem, Regra Própria e requisitos/custo cumulativo de Domínio. Não converte aplicações gratuitas em vagas nem aprova efeitos/custom por um custo válido |
| `closure_bot/ficha_entidade_repertorio.py` | Confere escolhas extras da Principal e custos/níveis/quantidades dos trunfos da domada; Domínio compartilha vagas com especiais. Não aprova a técnica própria nem a montagem escrita só em texto |
| `closure_bot/ficha_equipamento.py` | Extrai requisitos, mãos e Volume das tabelas do livro; confere Força/patente e subtotal equipado das entidades. O inventário completo no formato 4 é conferido em ficha_carga.py; os formatos antigos continuam parciais |
| `closure_bot/ficha_testes.py` | Recalcula TR, perícias, Ofícios e quantidades de treinos da ANALISE 4; origem temporal e escolhas sem vínculo ficam manuais |
| `closure_bot/ficha_carga.py` | Soma o inventário completo e compara total/limite; catálogo do livro, quantidades e Volumes livres separados. Não presume autorização de armazenamento |
| `closure_bot/ficha_efeitos.py` | Bases e escadas de alcance/área extraídas do R51; confere as medidas e o tipo de resolução. Não usa bônus exportados como entrada nem interpreta escolhas escritas em prosa |
| `closure_bot/ficha_magia.py` | Tabelas e preços do R51 lidos do livro. Confere Classe, PE nominal, limites de peças/Restrições, parte do dano-base; nas entidades, nível, Classe, entrada e retorno. Na ANALISE 2 também confere Famílias, Classe 0/Máxima e CE por ganho; os números de entidade ficam em `ficha_entidade.py`. Não certifica contas ainda parciais; detalhes em `../dados/ficha/ENTRADAS-FALTANTES-ANALISE.txt` |
| `closure_bot/cogs/ficha.py` | `/ficha analisar` e `GC:ficha` (link escrito depois ou `.xlsx` anexo na mensagem): painel no canal com o que corrigir, o que o mestre confere, o que bateu e o que falta conferir, aberto por frase fixa de quem está de plantão. **Ligado** desde 14/10 (`LIGADO`); lê `dados/sistema/catalogos.json` e `livro.jsonl`, que o pacote leva |
| `testes/` | 399 testes em 14/10 (398 passaram; um teste online opcional foi pulado; inclui 23 de efeitos/medidas e 25 novos de repertório em `test_ficha_repertorio.py`; o que lê a ficha oficial pelo link só roda com `FICHA_ONLINE=1`); inclui 16 casos do verificador de respostas e um de retomada da bateria. Há testes que precisam do discord.py, da cryptography ou dos dois motores juntos e são pulados sem essas dependências. `testes/dados/` guarda respostas reais da Open-Meteo |

## Rodar

Neste computador já existe `Closure/.venv` com as dependências (criada em 13/10/2026; fica fora do git). De
dentro de `Closure/`:

    .venv/bin/python iniciar.py                 sobe o bot
    .venv/bin/python iniciar.py --conferir      mostra o que foi lido e o que falta, sem conectar

E os testes, de dentro de `Closure/src/`:

    ../.venv/bin/python -m unittest discover -s testes

Noutro computador: `python3 -m venv .venv` e `.venv/bin/pip install -r src/requirements.txt`.

Só um bot ligado por vez com o mesmo token. O do computador e o da Discloud ao mesmo tempo respondem em dobro.

## O que o bot precisa pra funcionar

Estado em 13/10/2026: tudo abaixo está feito, e o bot respondeu no servidor principal.

1. **Token do bot** em `DISCORD_TOKEN`, no `.env` da pasta `Closure/` (modelo em `.env.exemplo`, na raiz do repositório).
2. No portal de desenvolvedor, o **Message Content Intent** ligado: sem ele o bot não lê o nome na mensagem.
3. No servidor, a permissão **Gerenciar webhooks**. Sem ela a fala sai pela conta do bot, com o nome na frente
   ("**Closure:** ...").
4. `DONO_ID`, `GUILD_ID`, `CANAIS` e as duas URLs de avatar no `.env`. O avatar da Closure passa por um
   redimensionador público (wsrv.nl) que corta a imagem em quadrado, centralizada; se esse serviço sair do ar, a
   foto dela some e a URL precisa ser trocada. `CANAIS` tem só o canal próprio delas no servidor principal:
   é onde basta escrever o nome; nos outros canais elas respondem a quem marca o bot ou responde a uma mensagem dele.
   Ao subir, o bot registra os comandos em todo servidor, o que troca os do bot antigo.
5. O painel diário de clima: `/clima_canal` no canal, ou o ID do canal em `CLIMA_CANAIS`, no `.env` (o do
   servidor principal já está lá). Quem desligar o painel por comando precisa tirar o ID do `.env` também.

## Alternar Flash e Argon (14/10/2026)

### Uso seletivo e perfil compacto experimental

Flash 3.8 permanece padrão. Para um piloto em canais escolhidos, depois de revisar os resultados de
`pesquisa/validacao/2026-10-14-compacto-v2/relatorio.txt`, configure explicitamente:

```dotenv
MODELO_CHAT=misto
ARGON_CANAIS=ID_DO_CANAL_DE_TESTE
ARGON_PERFIL=compacto-v2
ARGON_TETO_USD=1
```

Substitua o ID e mantenha `VERTEX_PROJETO` e a chave privados. Sem canais selecionados, modo misto só
usa Flash. O limite de US$ 1 é uma parcela do teto global (normalmente US$ 9), não um valor extra;
zero bloqueia Argon e segue para o fallback. Não há classificador pago nem palavra do usuário que
ative o modelo. Nos canais escolhidos, toda mensagem que já chamaria o bot tenta Argon, até o limite;
isso não seleciona automaticamente apenas perguntas difíceis. A reflexão continua no Flash.

`ARGON_PERFIL=original` mantém o prompt anterior. `compacto-v1` usa textos revisáveis em
`pesquisa/propostas/argon-compacto-v1/`, implementados em `closure_bot/perfil_argon.py`. Compacta somente
sistema/lembrete: histórico, livro, lore, estado, pronomes e mensagem atual permanecem completos. O
fallback reconstrói a chamada Flash com o prompt original. Não edita os cards. Exige as versões
Closure 0.37 / Kal'tsit 0.30 e o sistema original exato: em incompatibilidade, pula Argon sem enviar
e usa o fallback. Uma mudança futura nos cards exige revisar o perfil.

`compacto-v2` usa os textos aprovados de `pesquisa/propostas/compacto-v2/`, com núcleo em
`closure_bot/perfil_compacto_v2.py`. Mantém as mesmas proteções da v1. O experimento e o bot
compartilham a transformação; o teste local compara o corpo inteiro nos 12 cenários e força o
fallback original. Flash compacto v2 existe apenas na ferramenta de avaliação: não há opção para
ativá-lo no chat, pois executou uma tarefa embutida numa tentativa de troca de identidade.

Na triagem v2 aprovada até 36 chamadas, encerramos em 27: 12 respostas de cada compacto,
uma Flash original e dois timeouts Flash original; nove originais suspensas. Nenhuma repetição.
Argon teve custo médio estimado US$ 0,004991 e mediana 3,54 s; Flash compacto US$ 0,001867 e
18,86 s. São estimativas com créditos promocionais, não fatura. O Argon custou 2,67× o Flash
compacto, e 20,34% acima do Flash original histórico nos mesmos 12 casos. A comparação com
original desta rodada está incompleta. A v2 melhorou alguns comportamentos, mas mantém
falhas de voz/inferência; gênero foi inconclusivo. Não é validação geral nem nota 102/102.
`ferramentas/avaliar_compacto_v2.py` sem `--executar` só prepara/confere localmente. A rodada
está concluída; não reaproveitar automaticamente as nove chamadas suspensas.

A proposta v3 está em `pesquisa/propostas/compacto-v3/`, com preparação local em
`ferramentas/preparar_compacto_v3.py`. Ainda não é uma opção de `ARGON_PERFIL` e não entra no
pacote de execução. Os 228 testes locais conferem sua integridade e a reprodução da v2, sem
chamadas de API. Os casos inéditos e o plano de diálogos não estão autorizados para execução paga.
Revisão externa: `docs/REVISAO-CLAUDE-ARGON.txt`.

Chamadas pagas agora esperam até 60 segundos; a gratuita continua com 12. O intervalo após falhas é
respeitado mesmo se todos os modelos estiverem indisponíveis. Erros de autenticação/configuração
ficam 30 minutos sem novas tentativas. HTTP 4xx/5xx confirmado não reserva custo, pois não é faturado.
Timeouts, cancelamentos e respostas 200 sem consumo completo
mantêm uma reserva cautelar no SQLite. Ela conta para os dois limites e sobrevive a reinício, mas
não é cobrança confirmada: `custo_estimado_usd` e `reserva_sem_uso_usd` ficam separados. O status
explicita estimativa + reservas. Não reconcilia automaticamente a fatura nem corrige chamadas antigas
sem uso; queda abrupta do processo antes de registrar e processos simultâneos continuam limitações.
Teto negativo, NaN, infinito ou inválido agora interrompe a configuração em vez de deixar um limite
ineficaz. Nenhuma configuração real foi ativada nem enviada à Discloud nesta revisão.

Na bateria, `--compacto-argon` mantém Flash original e prepara Argon compacto, com hash de ambos.
`--somente-argon` permite suspender novas tentativas Flash; tentativas anteriores continuam contando
no limite. A variante e o hash do pedido enviado ficam em cada resposta. Uma falha não é repetida.

A comparação local funcionou pela Vertex, usando a mesma chave e o mesmo projeto. Flash continua como padrão.
O relatório e as respostas estão em `pesquisa/validacao/2026-10-14-argon/`: 40 tentativas, 37 respostas,
17 pares completos; Argon low custou 2,64 vezes o Flash low nessa amostra.

No `Closure/.env` (ou nas variáveis da hospedagem), configure e reinicie:

```dotenv
# Vazio preserva FILA_MODELOS; este valor seleciona Argon no chat com Flash de reserva.
MODELO_CHAT=gemini-4-argon
# ID/número do mesmo projeto usado pela chave Vertex. Não publique o valor.
VERTEX_PROJETO=
ARGON_MAX_SAIDA=4096
```

Para voltar, use `MODELO_CHAT=gemini-3.8-flash`, ou deixe vazio para respeitar `FILA_MODELOS`.
A chave continua em `VERTEX_API_KEY`. Com `VERTEX_PROJETO`, Argon e Flash 3.8 usam a rota explícita
`locations/global`; sem projeto, permanece a rota Express. A rota curta do
Flash retornou 404 para Argon. A reflexão das 4h30 usa Flash low na Vertex (Flash-Lite pago de reserva),
independentemente de `MODELO_CHAT`. Ambos compartilham o registro e o teto de gasto.

Argon sempre usa `low`, omite temperatura/amostragem/penalidades, aceita `ARGON_MAX_SAIDA` entre 256 e
32768 e espera até 60 segundos. O limite inclui raciocínio e resposta; 4096 foi testado nos cinco casos
finais, sem cortes. Flash mantém seus parâmetros; a revisão posterior aumentou a espera paga para 60 segundos. Cada tentativa monta seu próprio
pedido, inclusive fallback. Logs e SQLite guardam tokens de entrada, resposta, raciocínio e cache,
modelo efetivo, término/corte, latência e custo estimado. Falha com uso informado também entra na soma.

O banco antigo ganha colunas automaticamente, sem apagar linhas. O limite faz uma reserva conservadora
antes de cada chamada paga para coordenar concorrência na mesma instância. Não controla outro processo
nem substitui o faturamento: timeouts podem ter cobrança sem retornar tokens. Os valores promocionais
são estimativas após créditos sobre gasto líquido; a fatura decide a aplicação. Preços do Argon mudam
em dezembro de 2026 e os do Flash em janeiro de 2027. Não é necessário Ultra para esta API.

A ferramenta `ferramentas/comparar_argon.py` prepara os prompts sem gastar por padrão. `--executar` faz
chamadas pagas, exige autorização prévia e usa um limite de 40 tentativas/US$ 0,50 estimado por pasta.
Ela salva o início de cada tentativa antes de enviar, não repete tentativas nem usa fallback na comparação.
Uma falha interrompe a rodada; `--continuar-apos-interrupcao` exige revisão manual e só avança nos casos
não tentados. Use outra pasta apenas para uma nova bateria autorizada. A pasta da rodada de 14/10 já
consumiu suas 40 tentativas: retomá-la não deve disparar novas chamadas.

## Modelo e prompt (13/10/2026)

- **Chamada à IA:** `closure_bot/modelo.py`. A fila padrão tenta o **gratuito primeiro** (Gemini 3.8 Flash
  pela chave do AI Studio) e só vai pro pago (o mesmo modelo pela Vertex) quando a cota do dia acaba; depois
  vem o 3.1 Flash-Lite, gratuito e pago. Provedor sem chave no `.env` sai da fila.
- **Teto de gasto:** a Vertex é pós-paga e não para quando o crédito acaba, passa a cobrar no cartão. Então
  o teto é do bot: antes de usar o pago ele soma o gasto do mês pelo registro (tokens vezes o preço de tabela
  de 13/10/2026) e, chegando a `TETO_MENSAL_USD` (padrão US$ 9), tira o pago da fila até o mês virar.
  `/status` e `--conferir` mostram o gasto estimado.
- **O que o gratuito custa:** a cota do 3.8 Flash é de 20 pedidos por dia, dividida com o site de teste; o
  Google pode usar as conversas do nível gratuito pra melhorar os produtos dele (no pago, não); e ele falha
  mais: num teste de 13/10, 3 de 7 pedidos voltaram "modelo com alta demanda".
- **Vertex com credencial desde 13/10/2026:** chave de API em `VERTEX_API_KEY`. A organização do Google
  Cloud bloqueia esse tipo de chave por padrão; o Mizuki soltou a restrição só no projeto do bot. O primeiro
  teste real (17 respostas, US$ 0,096) está em `pesquisa/validacao/` e resumido no fim de
  `pesquisa/reports/Qual IA usar no bot.md`.
- **Raciocínio reduzido por padrão** (Mizuki, 13/10/2026, "por enquanto"): o bot pede `thinkingLevel: low`.
  No teste custou 42% menos e respondeu em 2 a 4,5 s em vez de 4 a 13 s, sem perda visível em 17 respostas.
  `RACIOCINIO=modelo` no `.env` devolve o padrão do próprio modelo.
- **Prompt:** por enquanto vem do site de teste, por `../ferramentas/prompt_do_site/`. Essa ponte baixa a
  página do ramo `site-teste` e roda no Node a lógica dela (lorebook, busca no livro, estado, lembrete), então
  o bot usa exatamente o que os amigos testam, sem cópia de texto de card. Precisa do Node instalado.
- **Ler respostas:** `python3 ferramentas/testar_modelo.py` (de dentro de `Closure/`) manda 16 casos pelas
  duas personagens e grava em `pesquisa/validacao/`. Com a fila na Vertex cada caso é uma chamada paga.
- **Contra a monotonia** (pedido do Mizuki, 13/10/2026): o `carteiro` guarda o texto de cada fala enviada
  (só as delas, nunca o que as pessoas escrevem; 30 por personagem e por canal). A ponte aceita essas falas
  em `falas_anteriores` e roda com elas o detector de repetição da própria página, então o aviso "você já
  usou..." vale de uma conversa pra outra, sem chamada a mais. Medição com `ferramentas/medir_monotonia.py`:
  "oi closure" foi de 3 pra 6 respostas diferentes em 6, e "kal, tudo bem?" de 4 pra 6. Tira frase repetida;
  não dá assunto novo, que depende do estado e da ficha.
  A memória tem limite, pra ela não ter que inventar pra sempre: valem só as 6 respostas mais novas e só as
  das últimas 12 horas (`FALAS_VALEM_HORAS`); a frase só é barrada depois de aparecer em duas delas.
- **Vida** (13/10/2026): `vida.py` calcula o estado sem chamar modelo. Carga: respostas dela na última hora,
  em todos os canais. Movimento: mensagens do canal em 15 min (só a hora fica, em memória). Paciência: por
  pessoa e por personagem, cai com pergunta repetida em 30 min ou tentativa de tirá-la do personagem, volta 1 a
  cada 2 h; da pergunta fica só um resumo embaralhado, nunca o texto. Intimidade: dias diferentes em que a
  pessoa chamou aquela personagem (5, 15, 40, 100). O estado entra pela ponte (`estado=`): o bloco troca o
  da página, que é fixo, e o lembrete ganha no máximo duas linhas contando a de fora do plantão.
  Medição com `ferramentas/medir_monotonia.py --modo vida`: com ficha a resposta muda de assunto
  ("Como tá o Ren, ainda aguentando o tranco na mesa do Tiago?"); sem ficha ela usa o canal e o fato de a
  pessoa ser nova. Faltam os fatos da ficha, que só a reflexão diária preenche.
- **Ficha de pessoa e reflexão diária** (13/10/2026): quando alguém chama uma personagem, o texto fica em
  `mensagens_do_dia`. Às 4h30 `reflexao.py` manda o lote ao modelo, só por provedor pago, e grava no máximo três
  fatos novos por pessoa, até 15 no total (o mais velho sai). O texto é apagado mesmo se o modelo falhar. A
  peneira roda no pedido e no código: nada de saúde, dinheiro, religião, política, relacionamento, idade,
  endereço, contato, nem fato sobre outra pessoa. Na resposta entram só os fatos ligados à mensagem (até dois)
  ou, em uma de cada três, um sorteado (`vida.escolher_fatos`). Teste de verdade com 12 mensagens inventadas:
  8 fatos certos, e ficaram de fora a ansiedade, a idade, a cidade, a fofoca e o mau humor do dia.
- **Regras de fora** (lidas em 13/10/2026): política e termos de desenvolvedor do Discord e termos da API do
  Gemini. Feito por causa delas: a peneira dos fatos, a política de privacidade (`docs/PRIVACIDADE.md`)
  e a cifra do banco. O repositório vai ficar privado, então a política mora numa página avulsa (Gist) e o link
  dela vai em `POLITICA_URL`, no `.env`: é o que aparece no fim do `/meus_dados` e o que vai no portal do Discord. Falta o Mizuki pôr o link da política no portal de desenvolvedor do
  Discord. Fica em aberto, por decisão dele: o gratuito continua primeiro na fila, e nessa cota o Google pode
  usar o que recebe pra treinar, o que a regra 21 do Discord não permite com conteúdo de mensagem.
- **Banco cifrado:** `python3 -m closure_bot --gerar-chave` cria a `CHAVE_DO_BANCO` no `.env` (já criada neste
  computador). Com ela, falas, mensagens do dia, pronomes e fatos vão cifrados pro disco; IDs, horas e
  contagens ficam em claro. A hospedagem precisa da mesma variável. Sem a chave, ou com outra, o bot não
  mostra letra embaralhada: esquece o que não abre. Perder a chave é perder as fichas.
- **Chat ligado** (13/10/2026): quem chama uma personagem recebe resposta. O caminho, em `cogs/chat.py`:
  decide quem responde, atualiza o estado, monta o pedido pela ponte (`prompt.py`) com a conversa em andamento,
  as falas anteriores, o estado e a linha de clima, chama o modelo e envia pelo webhook. Só entra na conversa a
  mensagem de quem a chamou e a resposta dela; o resto do canal não vai pro modelo. Se o modelo falha, ela
  fica calada (frase pronta de erro não é fala dela) e o motivo vai pro log. Só o dono, pelo `DONO_ID`, vai
  no pedido como Mizuki.
- **Espera:** cada tentativa tem 25 segundos, e 12 no gratuito, que nos dois testes de ponta a ponta de 13/10 falhou nas 5 chamadas (sobrecarga, cota e demora). Provedor que falha fica de molho (10 min depois de cota
  estourada, 2 min depois de sobrecarga ou queda de rede) e a fila pula direto pro seguinte.
- **De onde vem a página do bot:** ela é montada neste computador, com os cards, o lorebook e o livro desta
  pasta (`python3 ferramentas/prompt_do_site/site_prompt.py --atualizar`). O site de teste dos amigos foi
  dispensado pelo Mizuki em 13/10/2026 e não é mais a fonte; `--atualizar --do-site` ainda baixa a página de lá,
  que parou na Closure v0.31 e na Kal'tsit v0.24. Mudou card, lorebook ou livro: rode o `--atualizar` e empacote
  de novo.
- **Sem Node na hospedagem** (13/10/2026): o JavaScript da página do site roda dentro do Python, pelo
  `quickjs-ng`. Nos 14 pedidos de conferência ele monta o mesmo pedido que o Node, em uns 40 ms (o Node leva
  quase 2 s por pedido, porque sobe um processo a cada vez). `python3 ferramentas/prompt_do_site/site_prompt.py
  --conferir` compara os dois, e `--atualizar` já compara sozinho quando a máquina tem os dois. Depois de baixar
  a página de novo, rode a conferência antes de empacotar. O `/status` mostra as versões que estão na página,
  que é de onde sai o prompt.
- **Consulta do livro, busca v10 (15/10):** definições por título/abertura em negrito e campos de tabelas
  são indexados em todos os capítulos. Perguntas de conta reúnem orçamento e conversão/teto: feitiço comum,
  Classe 0, Técnica Máxima e especial de entidade conservam suas fontes diferentes. A lista de aptidões
  traz o catálogo; Energia Reversa e Domínio Simples recebem o complemento quando a pergunta pede a
  explicação inteira. "Explica melhor" e "quanto custa?" podem retomar a regra anterior. O pedido reforça
  que brevidade/carga não cortam uma regra necessária e que dúvidas pontuais continuam pontuais. Até três
  blocos completos por pedido; sem segunda chamada automática. Nomes exatos consideram o título dos
  metadados, evitam nomes contidos em outros (Artes do Vínculo/Vínculo) e dispensam preenchimento de
  outra família numa definição específica. Comparações explícitas conservam as duas entradas.
  Confirmações e contestações podem manter a fonte por até seis mensagens anteriores; um novo assunto
  encerra essa cadeia. Personalização da Origem prioriza a permissão escrita e a escolha padrão juntas.
  Recomendações de Caminhos/Trilhas recebem ainda um panorama com recortes literais, âncoras e uma
  subseção pertinente inteira por Trilha, quando cabe no limite de 12.000 caracteres do conteúdo e seus
  rótulos (mais o cabeçalho). Isso inclui o Treino de Combate da Parceria com nível e condição, sem
  transformar o panorama em regras completas. Cards, modelos e esforço preservados. Os testes
  conferem fontes e montagem do pedido, não a resposta gerada; nenhuma API real foi chamada.
  Auditoria de títulos únicos: 421/425 antes e 425/425 depois. Títulos repetidos, paráfrases e qualidade
  das respostas ficam fora dessa régua. Relatório em
  `../pesquisa/validacao/2026-10-15-consulta-livro-v10/relatorio.txt`.
- **Testado de ponta a ponta sem o Discord**, com mensagem de mentira e o resto de verdade; no Discord mesmo
  ainda não rodou.

## Páginas públicas

O repositório é privado, então a política de privacidade e os termos de uso moram em duas páginas avulsas (Gist),
que são os links postos no portal do Discord. O texto de origem fica em `docs/`; a página não atualiza sozinha.

| Página | Origem | Atualizar com |
| --- | --- | --- |
| https://gist.github.com/cupcake-mochi/7439b3894cf8ad935601e0f521e16c08 | `docs/PRIVACIDADE.md` | `gh gist edit 7439b3894cf8ad935601e0f521e16c08 docs/PRIVACIDADE.md` |
| https://gist.github.com/cupcake-mochi/1bd7c72f8f47d5f47560443aa1861955 | `docs/TERMOS.md` | `gh gist edit 1bd7c72f8f47d5f47560443aa1861955 docs/TERMOS.md` |

## Hospedagem (Discloud)

`python3 ferramentas/empacotar.py` monta `src/var/closure-lab.zip` só com o que o bot precisa: `discloud.config`,
`iniciar.py`, `requirements.txt`, o código, a ponte com a página já baixada, o manifesto e os dois `card.json`.
Com `--com-env` o `.env` vai dentro; esse arquivo carrega segredo e não sai do computador a não ser pra
hospedagem.

- **Atualizar o app que já existe:** Commit com o `.zip`, depois Rebuild (reinstala as bibliotecas), depois Logs.
  O Commit não troca o arquivo principal do app: a Discloud continua chamando `closure_lab.py`, o do bot antigo
  (visto em 13/10/2026: o app caiu com `ModuleNotFoundError` do bot antigo). Por isso existe um `closure_lab.py` na
  raiz que só repassa pro `iniciar.py`.
- **Memória:** o processo chegou a 98 MB só de carregar e montar pedidos, sem conexão com o Discord. O
  `discloud.config` pede 256 MB; o plano do Mizuki vai até 1 GB, e os 100 MB do bot antigo não bastariam.
- **Banco:** fica em `src/var/bot.sqlite3` dentro da hospedagem. A Discloud preserva o arquivo entre as
  atualizações desde que ninguém o apague por lá (Mizuki, 13/10/2026). O pacote não leva banco nenhum, então
  subir pacote novo não passa por cima dele.
- **Segredos:** a hospedagem precisa das mesmas variáveis do `.env`, inclusive a `CHAVE_DO_BANCO`.

## Painel de clima (desenho)

Pedido do Mizuki em 13/10/2026, no jeito do painel do bot antigo: emoji e ícone do tempo, campos com emoji,
chance de chuva do dia, a imagem `closure_bot/recursos/painel_clima.webp` anexada e, no rodapé, o crédito de quem
desenhou (hatutaro), junto da fonte dos dados. Pra trocar a imagem, troque o arquivo e o `ARTE_DE` em
`cogs/clima.py`. Mudou o desenho do painel? Mude também o `DESENHO`: é o que faz o painel do dia ser refeito na
próxima volta, sem esperar o tempo virar.

## Regras de plantão implementadas

- Kal'tsit das 9h às 21h, Closure das 21h às 9h, horário de Brasília.
- O bot só reage a nome na mensagem (`closure`, `kal`, `kal'tsit`, `kaltsit`), menção ao bot ou resposta a
  uma mensagem dele. Mensagem de bot ou de webhook nunca é gatilho.
- Sem nome: responde quem está de plantão. Com nome: responde a chamada, mesmo fora do turno (a decisão
  sai marcada como fora do plantão, pra o lembrete ganhar a linha certa).
- As duas citadas na mesma mensagem: vale o nome que abre a mensagem; sem isso, quem está de plantão.
  **Essa regra é minha**, pra cobrir "closure, a kal'tsit falou que..."; o Mizuki pode trocar.
- Conversa privada com o bot é ignorada por enquanto: não existe webhook em DM, então lá não dá pra trocar
  nome e avatar. Fica em aberto.

## Clima (pedido do Mizuki em 13/10/2026)

Vem do bot antigo, que tinha painel de clima de Tóquio. Decisões do Mizuki: o painel automático volta; quando
perguntam, a personagem responde; vale pra outros lugares além de Tóquio; e **as duas monitoram de longe, sem
estar no lugar**.

- **Fonte:** Open-Meteo no lugar da OpenWeatherMap. Não pede chave nem conta, então não há segredo pra
  guardar. A chave antiga está escrita no código do legado; se aquele arquivo já foi compartilhado, vale
  revogar a chave no site da OpenWeatherMap.
- **`/clima [lugar]`** mostra o painel na hora (temperatura, sensação, umidade, vento, mínima e máxima, sol).
  Sem lugar, Tóquio.
- **Painel diário, um por servidor:** quem tem a permissão Gerenciar servidor usa `/clima_canal` no canal
  desejado, ou escolhe o canal no campo do comando (colar o ID do canal funciona). O painel de hoje sai na
  hora; nos outros dias, na primeira leitura depois das 6h de Brasília, e a mesma mensagem é editada quando a
  condição ou a temperatura mudam (confere de 15 em 15 min). `/clima_canal_desligar` desliga. É mensagem do
  bot, sem nome de personagem. Canal, dia e ID da mensagem ficam no SQLite, pra um reinício não postar de
  novo. Diferença pro legado: se o bot estiver fora do ar às 6h, o painel sai quando ele voltar.
- **Na conversa:** quando a mensagem puxa o assunto, `contexto_clima()` devolve a linha de dado pro bloco 4.
  Sem lugar na pergunta vale Tóquio ("tá chovendo aí?"); com lugar, o de lá ("como tá o clima em São Paulo?"):
  `[São Paulo, Brasil agora (14:15 de lá, dia): 28 °C, sensação de 30 °C, trovoada, ...]`. Lugar que a busca
  não acha vira `[Clima: o monitor não achou o lugar "X".]`. Sem a mensagem puxar, nada entra: é a mesma
  regra do sono da Closure, pra o clima não virar bordão. A ligação com o prompt entra junto com a resposta
  no chat (fases 2 e 4).
- **Como a busca escolhe o lugar:** entre os resultados com aquele nome, fica o mais populoso ("Paris" é a
  da França). A linha traz estado e país, pra quem perguntou ver se era esse. "Nova York" tem apelido no
  código, porque a busca em português só achava uma cidade do Maranhão.
- **Falta no card (texto de personagem, vai pelos geradores, com teste):** dizer que as duas acompanham o
  clima pelo computador e contam como está, sem dizer que estão lá. Elas respondem de outra estação, então
  não falam "aqui tá chovendo".

## Revisão de 13/10/2026 (pente fino antes de hospedar)

O que a revisão do código achou e corrigiu, cada item com teste:

- **Responder a uma fala fica com quem falou.** Antes, responder a uma mensagem da Kal'tsit de noite fazia a
  Closure atender. A fala respondida também entra no pedido quando já saiu da conversa em andamento.
- **Menção e ID não vão no texto.** A menção ao bot sai, e a de outra pessoa vira `@nome`, no que vai pro modelo
  e no que fica guardado até a reflexão. É o que a política de privacidade promete.
- **Nome, pronomes e fatos entram no bloco de estado sem colchete nem quebra de linha**, pra ninguém montar um
  bloco falso com o próprio apelido.
- **Limite de 8 chamadas por minuto por pessoa** e de 1500 caracteres por mensagem, porque cada resposta custa.
- **Reflexão atrasada roda ao subir**: se o bot estava fora do ar às 4h30, o texto guardado não fica parado.
- **Webhook apagado no servidor é refeito**, e comando que quebra avisa a pessoa em vez de ficar mudo.

Depois, no primeiro uso na Discloud (14/10/2026):

- **Mensagem com `@everyone`, `@here` ou menção a cargo não é conversa**, mesmo citando o nome delas. E elas
  nunca marcam ninguém: as menções saem desligadas em toda fala.
- **Marcar o bot ou responder a uma mensagem dele vale em qualquer canal.** `CANAIS` passou a limitar só o
  chamado pelo nome ("closure, ..."), que fora do canal delas apareceria em conversa dos outros. Um jogador marcou
  o bot no chat geral e ficou sem resposta; era isso, não o `GC:`.
- **O cargo do bot chama como marcar o bot (14/10).** O cargo que o Discord cria pro bot ao entrar no servidor
  ("Guias do Ciclo") vale como menção, e sai do texto mandado ao modelo. Qualquer outro cargo continua sem chamar,
  e o cargo dela junto de outro cargo também é aviso, não conversa.
- **Conversa sem chamar de novo (14/10).** Depois que ela responde alguém, a mensagem seguinte dessa pessoa no
  mesmo canal vai pra ela, sem nome, por até 3 minutos (`SEGUIMENTO` em `cogs/chat.py`). Para quando outra pessoa
  fala no canal, quando a mensagem responde ou marca outra pessoa e quando é só reação ("kkk", "valeu", emoji),
  que fecha a conversa. Vale também fora de `CANAIS`, pra quem começou marcando o bot. Fica na memória do programa.
- **Mencionar o bot não vira mais "comando"** no log (`CommandNotFound`): o tratamento de prefixo do discord.py
  foi desligado, porque quem lê mensagem são os módulos.

## O que falta

- Consulta de regra por comando (`cogs/regras.py` só tem o `/livro`). A análise de ficha já existe em `/ficha analisar` e `GC:ficha`, com cobertura parcial declarada.
- Calendário de sessões e aniversários, do desenho da vida.
