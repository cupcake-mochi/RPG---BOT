# Frente 4: como avaliar se o bot soa como a Closure

> Nota de pesquisa, 12/10/2026. Pergunta: como medir fidelidade de forma barata e confiável, para um personagem só, em pt-BR? Complementa o passo 7 (bateria fixa) do relatório anterior.

## Achados com fonte

- **LLM como juiz de fidelidade não é confiável sozinho.** PersonaEval ([arXiv 2508.10014](https://arxiv.org/abs/2508.10014v1), 2025): numa tarefa de identificar qual personagem está falando, "even the best-performing LLMs reach only around 69% accuracy", contra "90.8%" de humanos. Os autores dizem que o paradigma de LLM-juiz em roleplay costuma ser "unvalidated".
- **O que medir já tem lista pronta.** CharacterEval ([arXiv 2401.01275](https://arxiv.org/html/2401.01275v1), 2024) usa 13 métricas em 4 dimensões. As que importam para a Closure:
  - conversa: Fluency, Coherency, Consistency;
  - consistência de personagem: Knowledge-Accuracy, Knowledge-Hallucination, Persona-Behavior, Persona-Utterance (tom e jeito de falar batendo com o perfil);
  - atratividade: Human-Likeness, Expression Diversity.
  Eles treinaram um modelo de recompensa (CharacterRM) com notas de 12 anotadores humanos em escala de 1 a 5 e relatam que ele concorda mais com humanos que o GPT-4. O benchmark é em chinês.
- Nenhum benchmark achado avalia roleplay em português (mesma lacuna da primeira pesquisa).

## Protocolo proposto (inferência)

1. **Teste de quem falou (o mais forte).** Separar ~20 falas reais da Closure do corpus EN, transcriar para pt-BR com o mesmo cuidado do card (frente 3). Gerar ~20 respostas do bot para as mesmas falas anteriores (o campo `antes` do JSONL já dá o gatilho). Embaralhar e pedir para 3 a 5 pessoas que conhecem a Closure apontarem qual é do jogo. Taxa de acerto perto de 50% significa que o bot não se distingue da original. É a versão caseira do teste do PersonaEval, com humanos, que é onde ele é confiável.
2. **Planilha de nota com 6 critérios**, tirados do CharacterEval, de 1 a 5: soa natural em português; jeito de falar dela; atitude dela; acerta fato de lore; não inventa lore; variedade (não repete bordão). Mesmas pessoas, mesmas falas.
3. **LLM-juiz só para triagem automática**, nunca como nota final: checar respostas longas demais, bordão repetido, fato errado contra o lorebook. Validar o juiz contra as notas humanas do passo 2 antes de confiar nele.
4. **Repetir a mesma bateria a cada mudança** de card, de modelo ou de parâmetro, e guardar o resultado em `dados/` para comparar versões.

## Lacunas

- Não li o PDF do PersonaEval inteiro; os números são do resumo.
- Tamanho mínimo de bateria e de avaliadores para resultado estável não foi pesquisado; 20 falas e 3 a 5 pessoas é chute razoável para hobby, não número validado.
