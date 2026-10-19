# Retomada — fontes da Era da Revolução

Branch: `codex/mundo-era-revolucao`, criada de `0b7b10c` para separar esta
funcionalidade da etapa B47 encerrada. Implementação: `4200281`.
PR: https://github.com/cupcake-mochi/RPG---BOT/pull/66 (rascunho).
Base da PR: `codex/integracao-b47`, dependência da PR 65, ainda aberta.
Depois do merge da 65, conferir o diff e mudar a base desta PR para `main`.
Não repetir implantação B47 ou alterar sua avaliação por causa desta consulta.

O usuário forneceu o consolidado e pediu conhecimento de mundo para as guias,
excluindo 04 Reservado Mizuki, 05 Registros Complementares e 06 Recursos
Visuais. O acesso reservado até para si foi considerado desnecessário:
**nenhuma das três pastas foi importada e não existe exceção de dono**.

Implementado:

- Importação positiva e reproduzível de 31 textos/228 seções, com hashes.
- Consulta local compartilhada por Kal'tsit e Closure, com fonte e contexto
  limitado por pergunta. Não requer banco novo nem modelo para recuperar dados.
- Mistérios permanecem sem resposta inventada; falas de NPCs são fonte, não
  instruções de personalidade. Procedimentos de XP/missões da campanha não
  alteram cálculo B47, cadastro de campanha ou aprovação do mestre.
- Testes de exclusão com canários privados, recuperação das 20 regiões e das
  regras de campanha, conversa cotidiana, continuação e paridade dos motores.
- Núcleo regenerado e pacote sem `.env`, bancos ou campanha. Somente
  `src/var/site/nucleo.js` difere do pacote B47 instalado.

Fontes/atualização/comandos: `dados/mundo/LEIA-ME.md`.
Evidência final: `pesquisa/validacao/2026-10-18-mundo-era/`.
Fechamento da implementação: 834 testes executados, 833 aprovados e um online
opcional pulado; 12 testes novos incluídos, 14 casos iguais nos motores e 12
pedidos conferidos no código do ZIP extraído. Posteriormente o usuário autorizou
a implantação: 90 testes prévios passaram, publicação concluída às 22:44 de
18/10 e bot online em cinco servidores. Conferência dos 67 arquivos e preservação
de variáveis/bancos/campanha em `pesquisa/validacao/2026-10-18-mundo-publicacao/`.
Mais 12 verificações de contexto passaram diretamente no QuickJS da Discloud,
seis perguntas nas duas guias, sem modelo. Console desconectado ao final.
ZIP de entrega fora do Git: `entregas/closure-lab-era-revolucao-2026-10-18.zip`
na pasta de trabalho, ao lado do checkout. SHA256:
`acc3e58d71f8410c144b0c70a5fed383f1adeb14e167a695c7d68adf8c5b180d`.

## O que continua separado

**Código do bot:** busca lexical tem limite de cinco trechos/14.000 caracteres.
Perguntas muito amplas ou paráfrases sem nomes/tópicos podem exigir refinamento;
não afirmar cobertura semântica integral. Testes verificam as fontes e o pedido
montado, não uma resposta generativa real.

**Dados/fonte:** novas informações ou correções devem vir de texto autorizado
pelo criador. Não buscar cânone externo, importar pastas excluídas, corrigir
silenciosamente números da fonte ou alterar a ficha oficial.

**Mestre:** autorizações reais, conhecimento de um PJ, limites de história,
consequências de campanha e ambiguidades dos procedimentos permanecem humanos.

**Publicação:** implantação e reinício concluídos após autorização específica
do usuário neste chat. Não houve merge, mensagens ao Discord ou chamadas pagas.
A sessão web do Discord estava desconectada, portanto não se certificou uma
resposta de comando/conversa nesta rodada. Bateria de respostas pelo modelo
continua exigindo combinar quantidade/custo antes. Não repetir a implantação.

## Instrução exata para continuar

> Continue a PR 66 na branch codex/mundo-era-revolucao. Confira o remoto e a
> árvore antes de editar; leia dados/mundo/LEIA-ME.md, este arquivo e a evidência
> em pesquisa/validacao/2026-10-18-mundo-era/. Preserve as três pastas excluídas,
> as personalidades, a avaliação B47, memória e mídia. A importação e o pacote
> estão publicados e conferidos na Discloud; leia também a evidência em
> pesquisa/validacao/2026-10-18-mundo-publicacao/. Revisão/merge das PRs continuam
> separados; eventual bateria paga exige quantidade/custo autorizados. Não
> repita publicação ou ensaios já confirmados por rotina.
