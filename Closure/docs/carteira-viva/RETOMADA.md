# Continuar a Carteira viva

Atualizado em 26/10/2026. **Etapas 1–6 implementadas; restam 7–10.**
Carteira ainda não publicada na Discloud. Não confundir o piloto local com a
versão pública dos bots.

## Estado salvo

- Main remota conferida: `de424478a7a120ecb43bd0c79eb93774d446fae6`.
- Branch `codex/carteira-viva-etapa-6`, PR 83 em rascunho, base etapa 5/PR 82
  (`52ca144`). Pilha 77–83 dependente, sem merge. Não trocar a base para main
  para ocultar a dependência e não usar force-push.
- Código final da Carteira web: `0c9a15f760bc3d3d437e2fa85b231223306a7576`.
  Última guarda: exclusão global de dados encerra as sessões do próprio usuário.
  Regressão reproduzida antes/depois, 18 testes de sessão passaram. CI completo:
  **1.282 executados, 1.281 aprovados, um online opcional pulado e zero falhas**,
  261,589 s; run 40423286577. O commit posterior só de documentação não muda
  esse código nem exige publicação. ETAPA-6.md detalha os ensaios do navegador.
- Login Discord, galeria/cartão, detalhes/análise privados e interface PT/EN.
  Schema 5 com sessões transitórias cifradas; cookie/CSRF rotacionados, logout
  no servidor e revalidação de cargos/fonte/campanha. Sessões não vão ao backup.
- Suíte direcionada: 60/60, mais a regressão final de exclusão (18/18 sessões).
  Não repetir a bateria extensa por alteração exclusivamente documental. O CI executa a suíte normal, sem desativar debug.
- Piloto web com uma conta Discord real: login, galeria, análise e página 2
  passaram, com Google fictício. Logout invalidou outra aba. Três cadastros e
  conexão removidos, zero sessões/leituras/análises, banco íntegro e serviço
  parado. Produção preservada. Não afirmar duas identidades OAuth nesta rodada.
- Google básico da etapa 4 foi real: 18.393 campos, paridade XLSX, renovação e
  leitura sob demanda. Grant revogado e cópia na lixeira. A demonstração web
  usa ficha fictícia e não substitui a bateria nativa avançada.
- Ponte opcional segue fora do runtime/ZIP das Guias, 90 arquivos. Nesta rodada
  não houve deploy, parada de produção, Gateway duplicado ou chamada paga.
- Segredos fora do Git, em armazenamento privado. Não usar credenciais da
  Arquivista, redefinir tokens ou reutilizar grants/cópias descartados.

Ocorrência da etapa 5: upload isolado levou 19,153 s perto do teto de 20 s.
I/O é hipótese, não causa comprovada da falha anterior. Limite/expectativa
foram preservados; medir host e concorrência na etapa 9. A máquina local também
apresenta inicializações lentas: isso não mede a futura hospedagem.

## Próxima etapa

**Etapa 7: modelo de ficha do servidor. GPT-6 Astra · Alto (`high`).**
Primeiro revisar o contrato das cópias e suas automações; depois implementar
somente o que puder ser comprovado. Modelos oficiais são o padrão, configuração
administrativa é opcional e cadastro de ficha existente continua independente.
Não copiar emissão, histórico ou salário para um personagem novo.

```text
Continue a Carteira viva das Guias do Ciclo, em português informal.
Leia o topo de Closure/docs/FILA-ATUAL.txt e carteira-viva/RETOMADA.md,
PLANO.md, CONTRATO.md, BANCO.md, SERVICO.md, TESTES.md e ETAPA-6.md.
Confira AGENTS, remoto, árvore, branch, PRs e CI. Base da etapa 7: branch
codex/carteira-viva-etapa-6, PR 83. Pilha 77–83 em rascunho e dependente;
não mesclar nem publicar automaticamente. Commits documentais não pedem deploy.

Implemente a etapa 7 após validar o contrato do produtor: modelo oficial por
padrão e modelo compatível configurável pelo admin, cópia independente,
acesso do responsável, fórmulas, automações e inicialização. Distinga nível,
XP e regra de nível inicial da campanha. Não suponha que copiar ou escrever
pela API ativa gatilhos Google. Teste somente cópias descartáveis dos modelos
oficiais e um modelo sintético; nunca altere a oficial ou fichas de jogadores.
Trocar modelo não pode migrar personagens antigos silenciosamente.

Reutilize cadastro, sessões e capacidades atuais. Não ampliar escopos ou
permissões, contratar hospedagem nem redefinir credenciais por conveniência.
Edições de jogo só na etapa 8, com contrato próprio e prévia/confirmação.
Preserve autorização atual de responsável/revisor/admin e separação de lore.
Sem modelo pago, Gateway duplicado, escrita em fichas reais ou publicação do
serviço incompleto. Registre bloqueios reais do produtor e pendências nativas.

Ao fechar: testes proporcionais, commit/push/PR dependente, fila e retomada,
limpeza dos dados fictícios e distinção entre Git, piloto e produção.
Recomende etapa 8, GPT-6 Astra Alto, conforme PLANO.md.
```
