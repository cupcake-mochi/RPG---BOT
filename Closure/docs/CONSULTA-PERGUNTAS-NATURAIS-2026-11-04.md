# Perguntas naturais na consulta do livro

Correção sobre a main `48f0f4c`, na branch
`codex/consulta-perguntas-naturais`. Consulta R63/v0.373 e análise mecânica
R53 preservadas. Commit, push e abertura de PR autorizados em 04/11/2026.
Não publicada. Carteira Viva e seus ensaios não foram alterados.

## Problemas reproduzidos

- “Como funciona empunhadura dupla?” selecionava invocações em dupla e
  habilidades do Executor. Não entregava as regras de armas.
- Perguntas sobre agir logo após invocar recuperavam aquisição e habilidades
  do Evocador, sem a entrada em campo e o ciclo da entidade.
- “Como funciona os Atributos?” entregava a seção completa em terceiro lugar,
  depois de técnica e Invocação Principal. Não foi reproduzida uma ausência
  total da fonte na R63. A resposta antiga do Discord não foi reexecutada.
- A continuação “então não existe nenhum benefício?” perdia o assunto das
  duas armas. “Qual a duração?” também perdia assuntos de outros capítulos.
- “Posso usar Destreza pra bater com uma faca?” não recebia fonte do livro.

A reprodução usa a montagem local do pedido, não uma resposta gerada por
modelo. As falhas de seleção eram iguais nas duas personagens e nas duas lores.

## Correção

A busca prioriza definições diretas mesmo quando o nome aparece em muitas
páginas. Expressões de mesa sobre duas armas, entrada, ação, tarefa e troca de
invocações selecionam os respectivos trechos completos. Comandos especiais,
preparação, retorno e regras específicas conservam suas fontes próprias.

Uma pergunta de seguimento sem assunto próprio retoma a regra anterior.
Esclarecimentos como “me refiro a usar duas armas” também contam. A conversa
casual interrompe a sequência. Uma pergunta nova por outra regra usa o assunto
novo. Sem histórico de regra, “e qual a vantagem?” não busca benefícios aleatórios.

Perguntas sobre o atributo de um golpe recebem fórmula, propriedades e a tabela
da arma encontrada no livro. A fórmula da entidade é distinta da do personagem.
Os dados e preços continuam extraídos do livro. “Punhais” também localiza Punhal.
Nenhuma regra numérica nem conclusão mecânica foi escrita no seletor.

A quantidade máxima permanece em três blocos completos. Não foram alterados
cards, personalidade, lore, corpus R63, catálogos, legado, motor de análise ou
configurações de produção.

## Validação

- 66 testes direcionados passaram na versão final, sem alteração das
  expectativas dos testes antigos. Os dez métodos novos cobrem perguntas de
  mesa, esclarecimentos, singulares/plurais, custo, duração, limites, troca de
  assunto, conversa casual e diferenças entre personagem e entidade.
- A mesma bateria cobre atributos, maestria, iniciativa, concentração, carga,
  descanso, manobras, vida a zero, Integridade, resistência, crítico, armas,
  Energia Reversa e invocações. Os casos relatados são conferidos nas duas
  personagens e nos dois modos de lore.
- Auditoria antes/depois com as mesmas 498 perguntas pelos títulos do livro
  preservou 498/498 fontes. Essa auditoria é complementar às perguntas naturais.
- QuickJS e Node produziram os mesmos contextos nos quatro casos novos de
  paridade, incluindo o seguimento de uma pergunta sobre duas armas.
- Suíte completa coberta em três blocos, sem omissões ou duplicação entre
  eles: 361 testes (um online opcional pulado), 337 e 314. Total de **1.012
  testes, 1.011 aprovados, um pulado, zero falhas**. Tempos dos blocos:
  135,808 s, 136,314 s e 141,765 s. As partes são as suites por módulo de
  `unittest.defaultTestLoader.discover('testes')`, particionadas por
  `[0::3]`, `[1::3]` e `[2::3]`, a partir de `Closure/src`.
- A primeira execução completa foi interrompida para incluir e corrigir a
  regressão adicional de mudança de assunto (“e como funcionam os atributos?”
  depois de invocações). A execução final em processo único recebeu término
  por sinal (saída 143) antes do resumo. Por isso a comprovação final usa os
  três blocos completos acima, todos com saída zero, e não aquele log parcial.
- Corpus R63, catálogos, legado, código de análise e ponte Python/JS continuam
  idênticos à main de base. A alteração de produção fica no seletor da página
  que gera o núcleo. A análise mecânica permanece R53.
- Pacote regenerado e verificado, com 92/92 arquivos iguais aos fontes, ZIP
  íntegro e sem ambiente, bancos ou cadastro real de campanha. São 1.855.867
  bytes, SHA-256 `25799ee41373597cf51f2bb2fcbbb7871ef1af62e0ae6e563ee87390d25aef9f`.
  O pacote está ignorado pelo Git e não foi enviado à hospedagem.

A primeira reprodução dos testes novos teve 38 falhas de asserção em nove
métodos. Na revisão dos testes, foi retirada uma proibição indevida da fonte
“Trocar de entidade” numa dúvida sobre retorno de entidade caída. Essa fonte
já aparecia antes e é pertinente ao retorno por substituição. Foi mantida a
exigência da fonte “Retorno e corpos caídos” e a proteção contra forçar a regra
genérica de entrada nessa pergunta. Nenhuma expectativa antiga foi alterada.

## Limites e publicação

Os testes comprovam a seleção e integridade das fontes entregues ao modelo,
não que toda resposta futura terá interpretação correta. Não houve chamadas
pagas, ensaio novo no Discord, merge ou deploy. A auditoria de títulos e as
variações de mesa se complementam, sem prometer cobertura de qualquer frase.

Antes de publicar, revisar o diff e o pacote e seguir a rotina de backup e
conferência da Discloud. Um teste de resposta com modelo exige autorização
própria de quantidade e custo. A análise da ficha deve continuar na R53.
