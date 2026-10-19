# Closure

**Conhecimento de mundo · preparado em 18/10:** as duas guias consultam 31 textos
autorizados do consolidado da Era da Revolução, com recortes e origem por assunto.
Reservado Mizuki, Registros Complementares e Recursos Visuais não entram.
[Fontes, limites e atualização](dados/mundo/LEIA-ME.md). Esta alteração ainda
não foi implantada; a publicação B47 registrada abaixo é anterior.

**B47 · etapa publicada e conferida em 18/10/2026:** código `40d32a7` da
branch `codex/integracao-b47` instalado na Discloud com autorização do usuário.
Online em cinco servidores; backup final confirmou os 67 arquivos do pacote
iguais aos fontes, variáveis/dois bancos/campanha idênticos e quatro aprovações
preservadas. A PR 65 permanece aberta, sem novo merge; main contém a PR 64.

Passaram três testes após implantação, com dez páginas conferidas: erro por
link, custom aprovada por XLSX e arquivo sem cache recusado. Cores locais
confirmadas no Discord, quatro setas e seletor exercitados. São 44 análises
reais somando as baterias anteriores. Suíte do mesmo código: **822 executados,
821 aprovados e um opcional pulado**; **26/26 testes no ZIP**. Não houve nova
chamada paga, alteração da oficial ou concessão de aprovação de personagem real.

Esta etapa está encerrada. Revisão/merge da PR 65, segunda pessoa no painel,
recálculos nativos ampliados, dados/defeitos do produtor e decisões humanas
do mestre continuam separados. A ficha B47 foi entregue; não retomar C/D.

[Contrato e cobertura](dados/ficha/INTEGRACAO-B47.md) ·
[Retomada exata](docs/RETOMADA-B47.md) ·
[Roteiro externo](dados/ficha/ROTEIRO-EXTERNO-B47.md) ·
[Evidência da publicação](pesquisa/validacao/2026-10-18-b47-cores-publicacao/relatorio.txt).
Os registros datados abaixo são históricos.

**Voz das reações v22 (15/10):** Mizuki esclareceu que o limite de conteúdo não deve neutralizar a personalidade. A orientação usa a voz/reações do card, inclusive humor, ironia, reserva ou crítica quando couberem, e retira a expressão parte neutra do pedido. Cards, comandos, ativação e limites preservados. Sem chamadas pagas; naturalidade depende do piloto. Relatório em `pesquisa/validacao/2026-10-15-voz-reacoes-v22/relatorio.txt`.

**Estado local do modo adulto v21 (15/10):** os comandos agora destacam se o modo está ativo no canal atual e explicam opção desligada, falta de marcação NSFW ou restrição a outro canal. Mesma decisão usada na conversa. A marcação 18+ continua necessária para o modo adulto; reconhecer personagem e comentar arte de forma neutra não exige entrar em interação sexual. Orientação evita desvio automático para RPG. 642 testes passaram e um online opcional foi pulado; 16 passaram no código do ZIP. Sem chamadas pagas, mudança de card ou marcação automática de canais. Relatório em `pesquisa/validacao/2026-10-15-nsfw-status-v21/relatorio.txt`.

**Comparação de áudio concluída (15/10):** 24 respostas completas, sem repetição/fallback/uso incerto, por US$ 0,241773 estimados ao preço cheio. Núcleo solicitado atendido em 4/12 antes e 8/12 com a melhoria v17, sob o mesmo contexto v20; a resposta atual ao chiado da Closure tem detalhe adicional não confirmado. Tons simples melhoraram; acordes e fala com ruído continuam falhando. Amostra sintética pequena, sem certificação geral. Código do bot/ZIP preservados; sem novo pacote. Relatório em `pesquisa/validacao/2026-10-15-audio-comparacao-v20/relatorio.txt`.

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

> Ponto de entrada do projeto. Aqui fica o resumo e o índice das pesquisas;
> o detalhe de cada uma mora em `pesquisa/`.

## Resumo

Bot de Discord para o servidor da guilda que joga **Ciclo Maldito**, o sistema de mesa de
Jujutsu Kaisen do Mizuki ([`cupcake-mochi/JJK---Project`](https://github.com/cupcake-mochi/JJK---Project)).
Ele tira dúvida de regra, corrige ficha e conversa na voz de uma personagem de Arknights.

## Objetivos

1. Consulta das regras do Ciclo Maldito pelo chat, citando a fonte.
2. Comandos de análise e correção de ficha.
3. Personalidade de uma personagem de Arknights, interativa no servidor.

## Estado atual

**Fase 0 (organizar a pasta) concluída** em 12/10/2026: `dados/sistema/` sincronizado com o
Ciclo Maldito v0.359 / R44, e em 14/10 com o v0.364 / R51 (511 blocos). O esqueleto da fase 1 está em `src/closure_bot/` (13/10): o chat
responde e já roda na Discloud; os detalhes de execução ficam em `src/LEIA-ME.md`.

- **Kal'tsit** (plantão das 9h às 21h): card v0.30 aprovado e aplicado localmente em 14/10; histórico em `docs/DECISOES.md`.
- **Closure** (plantão das 21h às 9h): card v0.37 aprovado e aplicado localmente em 14/10, com exemplo de explicação inteira de habilidade.
- **Lorebook** v2.0 (97 entradas), com o livro R51 e os ajustes de busca de 14/10, na página montada localmente (`ferramentas/pagina_teste/`).
- **Filtro de conversa (busca v11, 15/10):** usos cotidianos explícitos de termos como trilha, energia e integridade não acionam o livro; perguntas mecânicas na mesma mensagem conservam as fontes. Reconstrução local da bateria: 12/12 casos ambíguos sem fontes de RPG, entrada em caracteres 24,6% menor nesse grupo; 16 pedidos de regra e seis turnos de Origem idênticos. Não mede custo nem novas respostas. 536 testes passaram, um online opcional pulado; auditoria mantém 425/425 títulos. [Revisão e limites](pesquisa/validacao/2026-10-15-consulta-livro-v11/relatorio.txt). Pacote sem `.env`: `src/var/closure-lab-consulta-v11.zip`; sem implantação pelo agente.
- **Consulta do livro (busca v10, 15/10):** nomes exatos prevalecem sobre palavras parecidas; confirmações conservam a fonte por até seis mensagens anteriores. Recomendações recebem um panorama literal dos Caminhos/Trilhas, incluindo o treino com armas da Parceria. A personalização da Origem conserva a permissão e a escolha padrão juntas. Auditoria local encontrou a fonte esperada nos 425 títulos únicos, sem avaliar respostas do modelo. [Revisão e limites](pesquisa/validacao/2026-10-15-consulta-livro-v10/relatorio.txt). Os cinco testes no Discord de 14/10 pertencem à busca v9; a v10 ainda precisa dessa confirmação.
- **Bateria mista v10 (15/10):** 48 tentativas Flash low, 47 respostas e um timeout sem repetição. Núcleos de regra conferidos bateram com o R51, incluindo a sequência de contestação da Origem; 11 respostas ambíguas completas ficaram no assunto cotidiano. A busca ainda enviou regras nas 12 tentativas ambíguas. Custo cheio estimado conhecido US$ 0,491862 e reserva incerta US$ 0,061989; sem ativar otimizações ou alterar o bot. [Resultados e limites](pesquisa/validacao/2026-10-15-bateria-mista-v10/relatorio.txt).
- **TR no Google Sheets (15/10):** cinco cópias nativas completas, 5.381 chaves lidas publicamente em cada: base verde, adulterada vermelha, treino faltante amarelo, domada verde e Corda amarela. Confirma cálculo/exportação no Google nos casos descritos; os XLSX anteriores eram sintéticos recalculados no LibreOffice. [Validação e limites](pesquisa/validacao/2026-10-15-ficha-tr-google/relatorio.txt). Mizuki confirmou os cinco resumos no Discord por capturas: cores, resultado e alertas esperados. Isso não certifica cada página interna.
- **Discloud (14/10):** Mizuki confirmou as regressões antigas, cinco perguntas de regra e os quatro painéis ANALISE 2 no Discord. O painel paginado também foi confirmado por ele às 23h05.
- **Painel de ficha (14/10):** resumo e páginas por assunto, seletor direto e botões primeira/anterior/próxima/última com emojis padrão. Controles públicos por dez minutos; encerrados, a mensagem volta ao resumo. Buffs identificados, números agrupados e detalhes longos repartidos sem perder itens. Sem modelo na análise ou na navegação.
- **TR, perícias e carga (15/10):** ANALISE formato 4 com 5.381 chaves, preservando as 4.896 anteriores. Bônus e quantidades refeitos das escolhas; ajustes ficam para o mestre. Carga usa o catálogo do livro e posições completas; fórmula legada exata vira pendência amarela. Página própria no painel. Formato 3 reservado ao trabalho de CONFIGURAÇÃO, ainda sem integração. [Revisão e testes](pesquisa/validacao/2026-10-15-ficha-tr-pericias/relatorio.txt).
- **Equipamento e trunfos (15/10):** requisitos de Força/patente, Defesa com armas reconhecidas, ataque armado e bônus de resolução das entidades; extras da Principal separados e trunfos da domada pelo nível dela. Reserva Profunda distingue o acréscimo do livro do Buff legado. Carga pessoal sem entradas completas permanece não certificada. Esta foi a etapa anterior a TR/perícias; CONFIGURAÇÃO segue no outro chat. Relatório em `pesquisa/validacao/2026-10-15-ficha-equipamento-trunfos/relatorio.txt`.
- **Repertório e Talentos (14/10):** capacidade recalculada pela progressão, aplicações gratuitas de Leque/Coexistência separadas das vagas comuns, Talentos por Categoria/nível, Regra Própria e Domínio pelo custo total atual e entidades por espaço conhecido. Concessões de Talentos pela Origem sem vinculação ficam por possibilidades, sem certificar o total. Relatório em `pesquisa/validacao/2026-10-14-ficha-repertorio/relatorio.txt`.
- **Contas de feitiço (14/10):** alcance/área e tipo de resolução conferidos, totais de Apoio/Cura e limites da Onda ampliados; Controle, Remate e Alma com verificações adicionais. Distribuição, texto e permissões continuam explícitos como revisão manual. Divergências exatas do gerador recebem pendência, sem certificar o valor. Detalhes em `pesquisa/validacao/2026-10-14-ficha-efeitos/relatorio.txt`.
- **ANALISE 2 (14/10):** 4.896 chaves, preservando as 2.650 antigas. Quatro cópias preenchidas e calculadas no Google cobrem Fundamento/Classe 0/Máxima, domada com Buff, criação/Principal e Kaori anterior com feitiços. Conferência de Famílias, números das entidades e Talentos ampliada; as quatro cópias foram aprovadas também no Discord. Cobertura e limites em `pesquisa/validacao/2026-10-14-analise-v2/relatorio.txt`. Argon congelado; CONFIGURAÇÃO segue no outro chat.
- **Proposta compacto v3 (14/10):** revisão pontual de identidade, fatos pessoais, gênero e cuidado; textos e perguntas inéditas preparados, sem API ou ativação. 228 testes locais passaram. A melhoria de comportamento ainda precisa de medição. [Proposta](pesquisa/propostas/compacto-v3/revisao.txt) · [Prompt de revisão no Claude](docs/REVISAO-CLAUDE-ARGON.txt).
- **Compacto v2 (14/10):** 12 pares completos; Argon com média US$ 0,00499 e mediana 3,54 s, Flash compacto US$ 0,00187 e 18,86 s, com créditos promocionais estimados. Argon foi melhor na recusa de tarefa embutida; Flash compacto teve regressão e não foi liberado no bot. V2 opcional só para Argon, desligada; Flash original continua padrão. 222 testes locais passam. [Resultados e limites](pesquisa/validacao/2026-10-14-compacto-v2/relatorio.txt).
- **Argon compacto experimental (14/10):** redução medida de 54% no custo do Argon nos mesmos casos; cerca de 19% acima do Flash da rodada anterior, com qualidade ainda desigual. Modo misto por canais, limite separado e perfil opcional preparados, desligados. [Revisão e resultados](pesquisa/validacao/2026-10-14-argon-compacto-v1/relatorio.txt).
- **Argon original no chat (14/10):** integração validada na Vertex global, com `low`, saída limitada a 4096 e Flash de reserva. Reflexão permanece no Flash. Em 17 pares completos, Argon custou 2,64× o Flash; Flash continua padrão. [Relatório e respostas](pesquisa/validacao/2026-10-14-argon/relatorio.txt).
- **Teste 4 — Corpo Amaldiçoado (14/10):** leitura real confirma PE 40 (36 + 4 de Núcleo Dependente). O bot agora avisa que essa menor não possui barra de Integridade, em vez de certificar os 60 calculados pela ficha. 277 testes: 276 passaram, um online opcional pulado. Planilha preservada; reteste posterior confirmado pelo Mizuki na Discloud.
- **Regressões da ficha (14/10):** Defesa fixa distingue zero, fórmula normal pendente e valor adulterado; notas do mesmo treino extra são agrupadas. Sem nome, o painel usa Caminho e nível conferidos. 275 testes executados: 274 passaram e um online opcional foi pulado. [Fila e validação](dados/ficha/TESTES-FICHAS-14-10.md).
- **Fase 3, correção de ficha (14/10):** o bot lê a aba oculta `ANALISE` da ficha (pelo `.xlsx` ou pelo link), refaz vida, PE, Integridade, proteção e Defesa pelo livro, confere Caminho, Trilha e Origem e junta os avisos da ficha. As contas básicas batem em quatro casos, incluindo a Kaori do livro. O comando `/ficha analisar` responde com um painel no canal e está ligado desde 14/10; magia e entidades receberam conferência parcial ampliada pela ANALISE 2. Divergências da ficha com o livro em [`dados/ficha/DIVERGENCIAS-FICHA.md`](dados/ficha/DIVERGENCIAS-FICHA.md). [Contrato da ANALISE](dados/ficha/CONTRATO-ABA-BOT.md).
- **Crédito do Google AI Pro:** ativado em 13/10/2026; a Vertex já respondeu com os cards
  atuais (fim de `pesquisa/reports/Qual IA usar no bot.md`).

Pra retomar numa conversa nova: [`docs/PROMPT-CONTINUIDADE.md`](docs/PROMPT-CONTINUIDADE.md).
O plano completo está em [`docs/PLANEJAMENTO.md`](docs/PLANEJAMENTO.md) e
[`docs/PLANO-PERSONALIDADE.md`](docs/PLANO-PERSONALIDADE.md), e as decisões em
[`docs/DECISOES.md`](docs/DECISOES.md).

## Pesquisas

Cada pesquisa ganha um arquivo em `pesquisa/` e uma linha nesta tabela.

| Tema | Pergunta que responde | Status | Arquivo |
| ---- | --------------------- | ------ | ------- |
| Modelo próprio ou API; como alimentar o bot | Vale treinar/hospedar um modelo ou seguir em API? Como fazer a personagem soar natural e fiel ao original? | Concluída em 12/10/2026 (com pontos a conferir listados no fim do relatório) | [relatório](pesquisa/reports/Bot%20de%20personagem%20modelo%20ou%20API.md) · [notas](pesquisa/research_notes/Bot%20de%20personagem%20modelo%20ou%20API/) |
| Fontes multilíngues e método de fidelidade | Existe material das personagens de Arknights/Endfield em outros idiomas ou pt-BR? Qual a melhor metodologia para o bot soar como a original? | Concluída em 12/10/2026 (com pontos a conferir listados no relatório) | [relatório](pesquisa/reports/Fontes%20multil%C3%ADngues%20e%20m%C3%A9todo%20de%20fidelidade.md) · [notas](pesquisa/research_notes/Fontes%20multil%C3%ADngues%20e%20m%C3%A9todo%20de%20fidelidade/) |
| Outros personagens e traduções pt-BR | Quanto material existe dos outros personagens? Alguém já traduziu algum para pt-BR? | Concluída em 12/10/2026 | [relatório](pesquisa/reports/Outros%20personagens%20e%20tradu%C3%A7%C3%B5es%20pt-BR.md) · [notas](pesquisa/research_notes/Outros%20personagens%20e%20tradu%C3%A7%C3%B5es%20pt-BR/) |

Validação das três pesquisas (12/10/2026): [pesquisa/validacao/](pesquisa/validacao/).

Já confirmado na fonte: Endfield tem texto oficial em pt-BR (vozes só CN/EN/JP/KR); a Closure é operadora jogável no servidor CN desde 01/05/2026 07:00 no horário da China, que é 30/04 às 20:00 em Brasília (global ainda sem data) e as falas de operadora dela existem só em chinês. As falas dela na história (1.557 em EN/JP/KR, 2.096 em CN) estão extraídas em `dados/corpus_closure/`.

## Estrutura de pastas

| Pasta | O que vai nela |
| ----- | -------------- |
| `docs/` | `PLANEJAMENTO.md` (fases), `DECISOES.md` (o porquê de cada decisão) e especificações. |
| `pesquisa/` | Relatórios e notas de pesquisa, uma por tema, com fonte e conclusão. |
| `referencias/` | Material de terceiros: PDFs, links salvos, documentação. |
| `dados/sistema/` | **Cópia gerada** das regras do Ciclo Maldito. Não editar; atualizar pelo `ferramentas/sincronizar.py`. |
| `dados/ficha/` | Contrato da aba oculta da ficha e fichas de teste. |
| `dados/corpus_closure/`, `dados/corpus_kaltsit/` | Falas das personagens extraídas do jogo (história, ficha de operadora, Loja) e os bancos sem lore. |
| `dados/personagem/` | Card, exemplos e lorebook da personagem do bot. |
| `ferramentas/` | Scripts de apoio, como o sincronizador. |
| `src/` | Código do bot. |

## Legado

O material anterior está em [`../Closure Legado/`](../Closure%20Legado/) e não é
alterado por este projeto — serve só de consulta:

- `closure_lab.py` — bot de Discord (discord.py + Gemini) para fichas de
  *Feiticeiros & Maldições*, hospedado na Discloud.
- `closure_lab.db` — banco SQLite do bot.
- `discloud.config`, `requirements.txt` — configuração de deploy e dependências.
- `Feiticeiros & Maldições - Livro de Regras v2.5.2 - Polido.pdf` — livro de regras.
