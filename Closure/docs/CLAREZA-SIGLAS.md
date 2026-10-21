# Clareza de siglas · manutenção 1.0.3

Revisão editorial em 21/10/2026. Os guias orientam a consultar a **versão atual
do livro**, sem exigir que o jogador decifre códigos internos. O identificador
R53 fica no diagnóstico `ping`, com o rótulo “versão do livro”; corresponde à
revisão 53, não à versão do bot nem ao nível do personagem. O manifesto e a
compatibilidade mecânica continuam usando os identificadores originais.

O livro informa que o PDF pode ser mais recente que a base instalada; a mesa
continua responsável por combinar a edição. Não chamamos uma base antiga de
“atual” apenas por estar instalada. Rodapés de análise não repetem o código.

Termos úteis são explicados no contexto: Teste de Resistência (TR), Classe de
Dificuldade (CD), pontos de energia (PE), pontos de vida (PV), pontos de
experiência (XP), conteúdo adulto (NSFW) e interpretação de cenas sexuais (ERP).
O resumo da análise oferece uma legenda curta. Os guias explicam GC: e o
arquivo Excel (.xlsx); a exportação privada descreve o arquivo de dados (.json).
As versões inglesas seguem a mesma orientação. Nomes de comandos, campos e
chaves exportadas permanecem estáveis.

Validação preparada: 153 testes direcionados aprovados; 57 páginas em inglês
com até 1.052 caracteres de texto e 90 chamadas estáticas de tradução sem
entradas ausentes. Suíte completa final: 953 testes executados, 952 aprovados e um online opcional pulado (CI final do runtime 39663249101). Mais 50 regressões: 49 aprovadas e uma opcional pulada. O complemento dos cartões passou 63 testes direcionados. Publicação conferida abaixo.
Não houve chamadas a modelos nem alteração de ficha, regras ou aprovação.

A primeira suíte completa executou 953 testes e encontrou três expectativas de
texto antigas: a frase literal “sem ERP”, a orientação anterior de marcação
NSFW e a exigência do código R51 no rodapé. Foram atualizadas para a redação
aprovada pelo usuário e para a legenda da ficha; as verificações de permissões,
isolamento por servidor, restrições e cálculos permanecem intactas. A edição
continua conferida no diagnóstico pelo teste do manifesto. Não foi alterado
resultado mecânico para ocultar falha.

## Fechamento publicado

Guias 1.0.3 publicadas inicialmente às 16:30:48 de Brasília; pacote definitivo com os resumos simplificados online às **16:42:16**. O ensaio
no Discord confirmou `GC:guia livro`, `GC:livro` com os dois temas e `GC:ping`
com o identificador técnico rotulado. Guia aberto por membro; livro e ping
conferidos pela conta administrativa. A redação comum não exige decifrar R53. Os resumos de cartões também retiram esse prefixo; nomes de formatos e chaves técnicas de compatibilidade permanecem identificáveis.

Auditoria dos backups: 90/90 arquivos instalados iguais ao pacote e aos fontes.
Ambiente e cadastro de campanha iguais; os dois bancos estão íntegros, com
as mesmas tabelas e registros. Contagem de chamadas de modelo preservada.
Nenhuma planilha foi editada e nenhuma chamada paga foi feita nesta rodada.

Pacote identificado por MANIFESTO-PACOTE-1.0.3.json; SHA-256
`690efa5ee372670d94bb02cd454a47e9b0dbc35bf4d9922ba21ed9b7e8616757`.
Arquivista 1.1.2 também publicada, com auditoria e retomada no seu repositório.

## Retomada

Conferir o remoto e o manifesto do pacote antes de editar. Esta manutenção
está concluída; não repetir implantação por mudança exclusivamente documental.
A análise continua parcial: entradas ausentes do produtor e decisões humanas
seguem nos relatórios de contrato e na validação da integração. Não foi
concedida nova autorização para modelos pagos. As evidências históricas de
fichas, lore e idiomas permanecem válidas dentro do escopo que documentam.

A revisão dos resumos de cartões também atualiza a tradução inglesa e a expectativa de apresentação do Feitiço 1: o nome e as contas permanecem, mas o prefixo de revisão deixa de ser exigido. Identificadores de formato e chaves exportadas não mudam.

Auditoria definitiva repetida após o complemento: 90/90 arquivos conferidos contra o manifesto, ambiente/campanha e dois bancos preservados sem diferenças de estado. Runtime validado em `42f6392`; nova abertura do guia confirmada no Discord às 16:42. O pacote definitivo é o único anexado à release.
