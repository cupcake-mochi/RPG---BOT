# Etapa 2 — banco e cadastro

26/10/2026 · branch `codex/carteira-viva-etapa-2`, sobre `daa5627` da etapa 1.
Main remota conferida: `de42447`. PRs 77 e 78 continuam abertas; CI da etapa 1
concluída com sucesso. A PR desta etapa depende da 78, sem merge ou publicação.

**Etapa 2 implementada localmente.** O módulo não está conectado ao Discord
nem ao Google. A [prova nativa de acesso](ACESSO-GOOGLE.md) continua pendente.

## Entregue

- Pacote independente `src/carteira_viva`, com cadastro e SQLite próprios.
- Vários personagens por jogador/servidor; conexão Google normalizada e
  reaproveitada entre vínculos do mesmo usuário.
- Cadastro livre dos próprios personagens, confirmação de responsabilidade,
  proteção contra tomada de posse e galeria paginada por servidor/jogador.
- Perfis e campos públicos por lista positiva; detalhes privados para dono,
  admin/dono do servidor ou cargos explicitamente configurados de revisão.
  `Manage Guild`, cargos de lore e cargos de edição não ganham leitura privada.
- Troca de fonte com revisão esperada, repetição segura de pedido e preservação
  do perfil. Fonte antiga não sobrescreve uma nova; análise antiga é identificada
  por leitura/revisão. A aprovação mecânica continua no motor existente.
- Cache com fonte, geração, horário e retenção. Uma leitura reserva um ticket;
  reserva posterior, troca de arquivo ou mudança de autorização invalida o anterior.
- Cifra obrigatória, contextos separados, rotação transacional e leitura de
  backup com chaves antigas. Sem segredos no retorno dos cartões/detalhes.
- Migrações v1→v2, recusa de banco alheio/versão futura e verificação de integridade.
- Exclusão imediata, remoção global por usuário autenticado, saída/retorno,
  retenção e registro externo de exclusões/bloqueios de autorização.
- Backup cifrado em blocos, restauração para destino novo, reaplicação do
  registro atual de remoções e limpeza de backups próprios após a retenção.

[Banco e interface interna](BANCO.md) descrevem os arquivos, métodos e limites.

## Falhas encontradas durante a implementação

1. Um backup anterior à desconexão recuperava a conexão como ativa. A regressão
   reproduziu as duas variantes, desconexão e revogação. O registro externo
   passou a incluir a versão de autorização bloqueada; o restore reaplica o bloqueio.
2. Uma falha tardia de renovação poderia revogar uma autorização nova. O
   adaptador agora precisa informar qual autorização falhou; resposta obsoleta
   é ignorada. Leituras anteriores à reconexão também ficam inválidas.
3. O nome do laboratório da etapa 1 colidia com o pacote definitivo na importação
   dos testes. O teste passou a usar `pesquisa.carteira_viva`; ambos exercitam
   o mesmo módulo de permissões, sem duplicar regras.

Nenhuma expectativa existente foi alterada para esconder esses problemas.
As expectativas da etapa 1 continuam passando contra o contrato promovido.

## Validação

- 61 testes novos da etapa 2 e 39 da etapa 1: **100 testes direcionados passaram**.
- Casos incluem permissões, isolamento, token ausente/conta diferente, leitura
  atrasada, revogação, troca, idempotência, saída, exclusão, retenção e rotação.
- Migração com falha injetada reverte schema; falha de exclusão reverte também
  o registro de remoção. Bancos e chaves são descartáveis.
- Backup testado com múltiplos blocos, arquivo alterado, truncado, reordenado,
  chave errada, dados extras, prazo expirado e ledger de outro banco.
- Recuperação preservou dados válidos e não reabriu personagem excluído ou
  autorização revogada/desconectada depois do backup.
- O caso de limpeza só remove backup próprio com metadados autenticados;
  arquivos de outro banco e metadados inválidos foram preservados.
- Manifesto de produção conferido: **90 arquivos**, sem `src/carteira_viva`
  nem testes. Nenhum fonte carregado pelas Guias foi alterado; sem ZIP novo.

Suíte completa com núcleo presente, sem alterar expectativas antigas:

```bash
cd Closure/src
../.venv/bin/python -m unittest discover -s testes
```

**1.076 executados em 409,329 s: 1.075 aprovados, zero falhas e um online
opcional pulado.** O aviso de ausência de chave nas fixtures antigas não é
diagnóstico do ambiente de produção; o novo módulo exige cifra e usa chaves
descartáveis nos testes. A suíte completa não foi repetida após os ajustes
exclusivamente documentais.

## Limites e próximo passo

Sem ensaio nativo Google/Discord, carga com mil personagens ou queda real de
energia. O teste de rollback é uma falha SQL controlada. A recuperação exige
o registro de remoções atual e as chaves; perda simultânea desses materiais
não pode ser compensada adivinhando exclusões que deixaram de existir.

O módulo não valida OAuth ou seleção real do Picker: recebe dados já
verificados de adaptadores de servidor. A etapa 3 deve implementar essa
fronteira, revalidar participação/cargos, ligar manutenção e integrar o
serviço web. Não converter DTOs do navegador diretamente em identidades.

Nenhuma ficha oficial/jogador, banco de produção, credencial externa, plano
ou permissão foi alterado. Sem chamadas pagas e sem merge/deploy.

Próxima: **etapa 3, GPT-6.1 Sol · Alto**. Pode continuar na mesma configuração.
OAuth Google/Discord e origem web continuam exigindo configuração própria;
não usar credenciais da Arquivista nem token de produção num bot de teste.
