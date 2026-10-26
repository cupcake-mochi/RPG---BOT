# Continuar a Carteira viva

Atualizado em 26/10/2026. Etapas 1–4 implementadas e piloto básico de leitura
Google concluído. **Etapa 5 implementada: galeria, apresentação e consultas no
Discord. Etapas 6–10 pendentes.** Nenhuma Carteira publicada na Discloud.

## Estado salvo

- Main conferida: `de42447`. PRs 77–81 são dependentes e continuam sem merge.
- Base da etapa 5: `df703ec`, PR 81, CI verde. Branch atual:
  `codex/carteira-viva-etapa-5`; PR nova deve ter base etapa 4, nunca main.
- Galeria `/personagens [jogador]`, comandos PT/EN, consultas privadas,
  apresentação com prévia e imagem cifrada. Detalhes: ETAPA-5.md.
- Suíte local 1.237, zero falhas, um opcional; 19 testes finais da interface
  passaram. Coleta final esperada: 1.238. Registrar CI do head final.
- Piloto Discord com duas contas reais e Google fictício passou na galeria,
  apresentação e análise privada; falta fechar o registro da limpeza/retorno
  da instância hospedada. Não declarar nova publicação do bot.
- Credenciais em pasta privada fora do Git. Não reutilizar grants revogados
  nem cópias na lixeira dos pilotos anteriores; não redefinir tokens.
- Nova ponte continua opcional e excluída do ZIP do bot. Produção exige host
  HTTPS persistente e campanha sincronizada de forma autoritativa.

## Próxima etapa

**Etapa 6, Carteira web responsiva. Modelo: GPT-6.1 Sol · Alto (`high`).**
Manter a mesma API e capacidades. Não abrir o serviço em produção para adiantar
uma etapa, nem criar URL pública de imagem ou link de Carteira inexistente.

```text
Continue a Carteira viva das Guias do Ciclo, em português informal.
Leia o topo de Closure/docs/FILA-ATUAL.txt e carteira-viva/RETOMADA.md,
PLANO.md, CONTRATO.md, BANCO.md, SERVICO.md, TESTES.md e ETAPA-5.md.
Confira AGENTS, remoto, branch, árvore, PRs e CI. PRs 77–81 e a PR da etapa 5
são dependentes; não mesclar nem publicar esta pilha automaticamente.

Implemente a etapa 6: Carteira web responsiva, usando o mesmo serviço,
cadastro e verificações atuais. Só projeção básica pública; fonte, campos
completos e análise exigem identidade Discord comprovada e capacidade atual.
Compartilhar o link não transfere acesso. Revalidar servidor, saída, cargos,
fonte/autorização, leitura/campanha/motor e estado das prévias em cada ação.
A imagem permanece cifrada fora do SQL e não ganha URL pública sem contrato.

Não repetir o piloto básico Google da etapa 4 por rotina: 18.393 chaves e
paridade XLSX já passaram, grant revogado e cópia na lixeira. Etapa 5 tem
Discord real com duas contas, mas Google fictício; não converter isso em
validação nativa de fichas avançadas. Leia as pendências de ETAPA-5.md.
Nenhuma escrita Google antes da etapa 8; sem modelo pago. Preservar banco,
registro atual de remoções, mídia cifrada e chaves anteriores nos backups.

Não editar fichas oficiais/jogadores. Sem Gateway duplicado. Não substituir o
app da Discloud pelo serviço incompleto. Atualize fila, docs e retomada com
resultado real; faça commit/push/PR dependente, sem force-push. No fim separe
Git, ensaios e produção e recomende modelo/esforço para a etapa 7. Use Sol Alto.
```
