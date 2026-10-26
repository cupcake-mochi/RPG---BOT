# Conexão da ficha

26/10/2026 · implementação local da etapa 3. Branch
`codex/carteira-viva-etapa-3`, baseada em `b491409` da etapa 2/PR 79.
Main remota conferida antes: `de42447`; PR 79 aberta, CI verde nesse SHA.
Sem merge ou publicação nesta rodada. Produção continua no último runtime
registrado, `a7afebb`; esta entrega não instala comandos no Discord.

## Implementado

- Serviço aiohttp separado, com dependências próprias em
  `Closure/carteira/requirements.txt`; instruções em [SERVICO.md](SERVICO.md).
- OAuth com Authlib 1.9.1, PKCE S256 e estado de uso único. Exige a mesma conta
  Discord que iniciou a solicitação; consulta membros/cargos atuais com a API.
- Escopos: Discord `identify`; Google `drive.file`. O escopo Google permite
  escrita, mas o serviço faz somente GET de metadados e valores da planilha.
- Cookie de sessão HttpOnly, SameSite=Lax e Secure em HTTPS; rotação após
  identificação, origem exata, proteção contra requisições forjadas e limites
  de corpo, resposta e concorrência. Sem URLs arbitrárias para provedores.
- Google Picker na tela, validação de arquivo autorizado, tipo, lixeira,
  formato e nome por `ANALISE!A1:D32`. Essa leitura pequena **não analisa a
  ficha inteira**, não confere todos os campos e não aprova personagem.
- Credenciais e tentativas cifradas no schema 3, worker SQLite separado da
  interface HTTP e limpeza local a cada minuto. Só confirma a autorização
  durável depois da escolha/responsabilidade do jogador.
- Reuso de conexão válida, reconexão e troca atômica de arquivo preservando
  personagem/perfil. Nenhuma alteração no arquivo Google anterior. Revisões
  e versões da autorização bloqueiam respostas antigas e repetições indevidas.
- Backup exclui tentativas OAuth abertas. Reiniciar/recuperar descarta sessões
  pendentes e mantém vínculos confirmados. Cancelar não desfaz cadastro pronto.
- Tela PT/EN, confirmação clara e demonstração fictícia restrita a loopback.
- Ponte Discord opcional com links privados, sem carregar no bot existente.
  Tradução dos nomes dos comandos e uso do idioma configurado do servidor
  ficam para a integração da etapa 5.

## Validação

Conjunto principal: **149 testes aprovados**, incluindo os 101 anteriores.
Depois, regressão de backup e quatro testes da ponte: **5 aprovados**. Há
**150 testes distintos** da Carteira ao final. Nenhuma expectativa antiga
foi alterada para esconder falhas; a fixture v1 agora remove a tabela da
migração 3 antes de testar a subida de versão.

OAuth usa a biblioteca real com transporte HTTP simulado. Testes do serviço
usam HTTP em loopback, banco e provedores fictícios. Cobrem identidade errada,
cookie antigo, estado repetido, origem/CSRF, cancelamento durante callback,
revogação, saída do membro, troca concorrente, rollback ao duplicar arquivo,
confirmação repetida e preservação após reinício. A regressão de backup abre
a cópia decifrada e confirma zero tentativas, mantendo a tentativa original
utilizável até a confirmação.

Demonstração no navegador lateral: cadastro completo até a confirmação com
contas/planilha fictícias; tela inicial conferida em 390 × 844, sem corte de
texto ou botões. Banner identifica a simulação. Screenshot local de conclusão
em `/tmp/carteira-etapa3-demo.png`; tela pequena em
`/tmp/carteira-etapa3-mobile.png` (arquivos temporários, fora do Git).

Suíte completa no código `6d2fdb2`: **1.126 executados, 1.125 aprovados e um
online opcional pulado**, zero falhas, 527,418 segundos. Comando em
`Closure/src`: `../.venv/bin/python -m unittest discover -s testes`.
Núcleo de consulta presente; sem chamada paga ou alteração de planilha real.
As saídas de custo/modelo da suíte são de cenários simulados.
O manifesto do bot continua excluindo a Carteira, com os mesmos 90 arquivos.
Smoke de isolamento também passou: importar/criar o serviço não carrega
`discord` nem `closure_bot`. A ponte só importa Discord quando for carregada.

PR: [80](https://github.com/cupcake-mochi/RPG---BOT/pull/80), em rascunho,
base `codex/carteira-viva-etapa-2`. Conferir a validação automática do SHA atual.
O formulário inicial Google foi aberto apenas para inspeção: Rhodes Bot ainda
sem Auth configurado. Depois, o usuário criou/escolheu uma conta dedicada
às Guias para suporte público; identidade conferida no navegador. O primeiro
acesso ao Cloud foi aceito diretamente pelo usuário. Com autorização
específica, foi criado o projeto próprio `guias-ciclo-fichas` (Guias do
Ciclo - Fichas), sem ativar faturamento. O usuário também concluiu o aceite
da política de dados das APIs. O cadastro OAuth básico foi criado em modo
Externo/Testando. Cliente web, Drive/Sheets/Picker, escopo único drive.file e chave Picker
restrita configurados. O usuário optou por usar o app Discord oficial;
retorno local salvo e segredo OAuth redefinido pelo próprio usuário, sem
trocar o token do bot ou reiniciar a Discloud. Nenhuma leitura de ficha
real executada até este checkpoint. O formulário do
projeto pessoal não foi salvo.

## Pendências reais

**Etapa 3 local implementada; prova nativa aberta.** O piloto começou pela entrada controlada, com participação real conferida
na API Discord. Clientes/callbacks locais, consentimento básico Google e
chave restrita do Picker estão preparados. Ainda falta confirmar os
consentimentos de conta, selecionar a cópia no Picker real, validar
renovação/revogação e integrar a entrada por comando. Origem pública continua
pendente para jogadores. A demonstração não comprova CSP/SDK do Picker, renovação nativa,
revogação real ou comportamento em celular real. Seguir o roteiro de
[ACESSO-GOOGLE.md](ACESSO-GOOGLE.md); não anunciar a etapa como validada em
produção antes desses ensaios.

Não há análise completa, galeria, operações de escrita ou novo sistema de
aprovação. Leitura sob demanda é a etapa 4. Eventos gerais de saída/retorno,
desconexão pelo usuário e integração de idioma/comandos entram na camada
Discord/Carteira; o banco já oferece as ações de desconexão/exclusão.
Capacidade e hospedagem não foram medidas/contratadas. Authlib avisa sobre
migração futura do adaptador httpx; dependência fixada e aviso documentado.

Próxima implementação: **etapa 4, GPT-6.1 Sol · Alto**. Pode manter a mesma
configuração. Retomada exata em [RETOMADA.md](RETOMADA.md).

## Ajuste encontrado no começo do piloto

A primeira URL nativa mostrou `client_id=None`: o construtor do núcleo
Authlib recebe `session` antes de `client_id`; o argumento posicional tinha
sido interpretado como sessão. Reproduzido com teste que confere o ID na URL
de cada provedor: falha antes, passa depois de usar `OAuth2Client(None,
client_id=...)`. 49 testes de provedores/web/ponte passaram depois da
correção. O piloto foi reiniciado e a tela Discord abriu o app oficial e
somente identify. Consentimentos/seleção ainda em andamento neste checkpoint.

Cópia nativa privada de teste criada via integração Drive, denominada
QA Carteira — OAuth e Picker — DESCARTÁVEL — 26-10-2026; oficial preservada.
Mover somente essa cópia para a lixeira ao encerrar, após desconectar o piloto.
Não salvar identificadores de conta, tokens ou conteúdos privados no relatório.
