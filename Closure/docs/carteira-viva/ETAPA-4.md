# Leitura e análise privadas

26/10/2026 · branch `codex/carteira-viva-etapa-4`, sobre `c44e9e5`/PR 80.
Implementação local, separada do bot publicado. PR 81 dependente da 80. Sem merge nem deploy.

## O que mudou

O serviço lê a aba `ANALISE` do arquivo escolhido no Picker. Usa a autorização
Google do responsável, sem tornar a ficha pública, copiar o livro inteiro ou
consultar outros arquivos da conta. A prova curta do cadastro continua sendo
só identificação de formato; a análise exige a leitura completa.

A grade passa pelo mesmo `de_linhas` do leitor atual. Zero, vazio e ausência
continuam diferentes. Texto literal não vira número por parecer numérico.
Fórmula sem resultado, erro efetivo do Google, duplicata e cabeçalho inválido
interrompem a leitura. Um campo que o produtor não exporta continua ausente.
Exportações incompletas chegam às guardas do motor, sem ganhar aprovação.

O adaptador busca apenas `ANALISE!A1:D20002`, com campos selecionados da API:
valor calculado e valor/fórmula de entrada. A última linha protege contra
corte silencioso. A resposta tem limite de 16 MiB descomprimidos; o snapshot
cifrado conserva o limite anterior de 8 MiB. Linhas vazias com formatação não
são registros. A versão Drive é conferida antes/depois; mudança durante o
pedido exige tentar novamente. Não há promessa de transação do Google entre
abas ou de detectar toda recalculação por essa versão.

Cartões em transição seguem a seleção de leitura existente: no máximo três
leituras, esperas de 3 e 6 segundos, sem misturar campos de respostas distintas.
Se ainda houver cartão salvando, o resultado informa isso e não fica aprovado.
Revogação conhecida bloqueia a conexão; erro de atualização invalida o snapshot
anterior daquela fonte, em vez de devolvê-lo como se fosse a consulta nova.

## Campanha e resultado

O serviço carrega o cadastro local confiável de campanhas pelo mesmo formato
usado no bot. O servidor da interação define qual entrada usar. O navegador
não fornece regras, aprovações, arquivo arbitrário ou identidade comprovada.
Cadastro ausente para um servidor dentro de um arquivo válido significa livro,
como no motor atual. Arquivo configurado perdido, ilegível ou inválido é falha;
não cai silenciosamente no padrão. A operação não concede aprovação.

A conferência chama `ficha_corretor.conferir`, com as referências existentes.
Cada resultado informa arquivo, revisão do vínculo, ID/horário da leitura,
versão Google, campanha/servidor/revisão, horário da análise e revisão do motor.
A mecânica continua R53. O hash do motor inclui fontes, catálogos e livro,
impedindo reutilizar uma análise salva depois de mudar o motor instalado.

Abrir a análise salva confere de novo membro/cargos atuais, fonte, autorização,
leitura e campanha. Uma revisão velha é recusada; não vira aprovação corrente.
Dono, administrador/dono do servidor e revisor configurado podem consultar.
Cargo de idioma/lore e `Manage Guild` sozinho continuam sem esse acesso.

O cartão público não recebe snapshot, achados, credencial ou link privado.
O endpoint de atualização devolve só metadados. O resultado completo fica na
rota privada, com limite de 2 MiB e sem truncar achados para caber. As respostas
HTTP usam `private, no-store`. Imagens e apresentação da galeria são etapa 5.

## Fila e limites

- Duas operações de leitura/análise por vez, uma por servidor/ator.
- Até 32 pedidos distintos em andamento/espera e quatro por servidor/ator.
- Até 64 interessados no mesmo pedido; eles compartilham o trabalho.
- Rodízio entre grupos. A reserva do banco só acontece depois da deduplicação.
- Prazo de 60 segundos por trabalho e 90 segundos incluindo a espera.
- Atualização comum reutiliza snapshot fresco por até 60 segundos. Análise
  explícita exige leitura nova; consultas simultâneas podem compartilhar essa leitura.
- Guarda local de 45 leituras Sheets/minuto por conta e 240 por projeto,
  conservadora, sem provocar quota real. Esperar cota também consome o prazo.
- Cada tentativa completa faz três GETs: metadados Drive, grade Sheets e
  metadados Drive. Há ainda uma renovação OAuth por trabalho e as verificações
  atuais de membro/cargos no Discord. Cache fresco evita Google, não permissões.
- Renovação serializada por conexão; refresh rotacionado é salvo cifrado antes
  da próxima renovação. Tokens não entram na resposta, no LLM ou nos logs.
- Cancelar um interessado preserva os demais. O último cancela o trabalho;
  encerramento cancela pendentes. O servidor CLI liga cancelamento por desconexão.
  Uma operação SQL já enviada ao worker ou conta já executando numa thread pode
  terminar: há transações e guardas de versão, sem prometer interromper CPU/SQL no meio.
- Saúde do serviço não espera vaga ocupada por consulta. JSON e normalização
  pesados rodam fora do loop HTTP; SQLite permanece na sua thread própria.

Os limites não são benchmark de capacidade. Carga, memória, latência, cotas
configuradas e convivência com as conversas ainda entram na etapa 9.

## Conferido nesta rodada

**49 testes novos aprovados**, em 28,916 s na bateria final. Incluem banco
cifrado real, motor real e HTTP em loopback com provedores fictícios. A comparação
cobre simples, avançada, custom com/sem aprovação, exportação incompleta e total
adulterado. CSV e XLSX coincidem com a grade nos campos da fixture de leitura.
O teste de rotação usa dois personagens e confirma renovação serializada.

Suíte completa local: **1.176 executados, 1.175 aprovados e um opcional pulado**,
zero falhas, em 369,082 s. Ela começou antes da última regressão: falha ao abrir
a credencial foi reproduzida, corrigida e incluída nos 49 testes finais acima.
Conferir o CI da PR para a suíte completa do SHA final (1.177 testes esperados).
Não há chamada paga ou uso de dados de jogadores. Mensagens de modelo/custo
na suíte vêm de simulações. Manifesto do bot conferido: 90 arquivos, sem Carteira,
ambiente ou bancos. Sem novo ZIP; a alteração está fora do pacote publicado.

Revisão achou e corrigiu o caso em que a abertura de credencial falhava antes
da guarda de invalidação: a atualização recusava, mas ainda deixava o snapshot
velho. A regressão falhou antes da correção e passou depois. Nenhuma expectativa
existente foi alterada para ocultar falha. O ensaio nativo da etapa 3 não passa
a ser prova de leitura completa por causa desta implementação.

## Ainda falta

1. Preparação em [NATIVO-ETAPA-4.md](NATIVO-ETAPA-4.md): nova cópia privada
   criada; usuário precisa passar pelo aviso Google e confirmar autorização.
   A leitura completa ainda não ocorreu. Provar no Google real a grade completa em novas cópias descartáveis: simples,
   avançada, Ritual, entidades e custom com/sem aprovação. Comparar com CSV/XLSX
   calculado e conferir os campos vazios efetivos retornados pelo Google.
2. Integrar comandos, botões privados e galeria na etapa 5; conferir cargo
   removido e conta sem privilégios nativamente. As rotas internas são a base,
   não comandos já instalados no Discord.
3. Definir a distribuição confiável da campanha quando bot e serviço rodarem
   em hosts separados. Não compartilhar SQLite pela rede nem copiar um cadastro
   uma vez e prometer que estará sempre atualizado. Até lá, piloto local usa
   arquivo confiável fornecido pelo operador; publicação depende dessa integração.
4. Hospedagem HTTPS persistente, consentimento público, termos/privacidade,
   backup operacional e ensaios de carga continuam pendentes nas etapas próprias.
5. Limites mecânicos do produtor e decisões do mestre permanecem: dados ausentes,
   aprendizado/histórico, autorizações reais, narrativa, alvos e Alma. Cadastro,
   MESTRE VIU e prosa não substituem essas entradas ou decisões.

Nenhuma ficha oficial/jogador foi alterada. Nenhum banco, segredo ou cadastro
real entra no Git. Produção continua no estado documentado antes da Carteira.

Próxima implementação: **etapa 5 — galeria e cartões**, com **GPT-6.1 Sol · Alto**.
A bateria nativa pendente pode acompanhar essa integração, sem chamar a etapa
4 de validada em produção antes dela.

## Referências da API

- [Grade limitada por ranges e fields](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/get).
- [Valor calculado e fórmula de entrada](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/cells#CellData).
