# Etapa 1 — contratos e prova local

26/10/2026 · branch `codex/carteira-viva-etapa-1`, sobre o plano `3ac230b`.
Main remota conferida explicitamente: `de42447`, que agora inclui o registro
da publicação R57. A PR 77 do planejamento continua aberta. Esta etapa tem
PR dependente dela, sem merge ou publicação.

**Estado: parte local concluída; prova OAuth nativa pendente.** Não declarar
que jogadores já conseguem conectar suas fichas nem que a etapa inteira foi
validada de ponta a ponta.

## Entregue

- [Contrato de dados e acesso](CONTRATO.md): identidades, campos públicos,
  revisão/edição separadas, múltiplos personagens, troca de fonte, retenção,
  exclusão e rotas propostas.
- [Configuração externa](ACESSO-GOOGLE.md): estado observado na conta Google e
  na Discloud, requisitos concretos e roteiro da prova nativa.
- Laboratório executável em `pesquisa/carteira_viva/`, separado do runtime.
  Testa sessão/identidade, expiração, retorno repetido, conta diferente,
  arquivo não autorizado, confirmação, conflito e revogação simulados.
- Persistência de conexão cifrada após reinício simulada com refresh token
  fictício. Nenhum segredo real foi usado, lido ou copiado.
- Regra de projeção pública por lista positiva: snapshot, URL Google e token
  não aparecem no cartão mesmo se enviados indevidamente no perfil de entrada.

## Verificação no navegador

Consultas somente de leitura, sem alterar configurações:

1. Console Google autenticado na conta pessoal: Rhodes Bot e os dois outros
   projetos visíveis mostram a autenticação ainda não configurada.
2. Discloud: conta Gold; Guias e Arquivista online; 700 MB e 256 MB alocados,
   respectivamente. Nenhum site aparece na lista observada de dois apps.
3. Discord está disponível na aba de Testes. Não enviamos comandos de uma
   funcionalidade que ainda não foi integrada ao bot.

Não habilitamos APIs, criamos clientes, ampliamos escopos, contratamos planos
ou alteramos planilhas. Não foi feito novo exame dos arquivos de produção;
a lista do painel não comprova SHA instalado.

## Testes realizados

```bash
cd Closure/src
../.venv/bin/python -m unittest testes.test_carteira_contrato
../.venv/bin/python -m unittest testes.test_carteira_contrato testes.test_servidor_publico
```

- **39 testes novos passaram**, sem rede, todos com dados fictícios.
- **67 testes passaram no conjunto direcionado**: os 39 novos mais 28
  existentes de isolamento, permissões, idioma e recursos públicos.
- Nenhuma falha ou teste pulado nesse conjunto; nenhuma expectativa antiga
  foi alterada. Avisos de ausência de chave em fixtures antigas não são
  diagnóstico do ambiente de produção; o laboratório usa cifra e chave de teste.
- Manifesto de empacotamento conferido: **90 arquivos**, sem laboratório ou
  testes. Nenhum fonte do runtime foi alterado; ZIP não regenerado/deploy não
  realizado. Não repetir a suíte extensa somente por esses documentos.

Os testes de retorno, renovação, revogação e leitura simulam o resultado de
adaptadores Google/Discord. Eles comprovam regras locais, **não** login OAuth,
segurança HTTP, Google Picker real, quota, latência externa ou servidor web.
O protótipo é síncrono e de processo único; não comprova concorrência entre
workers. Os testes de conflito exercitam operações intercaladas por revisão.

## O que falta para o ensaio real

1. Escolher origem/hospedagem HTTPS e orçamento. Gold não satisfaz o requisito
   documentado de sites Discloud; não foi cotado nem autorizado um upgrade.
2. Configurar OAuth Google exclusivo das Guias, APIs, Picker e conta de teste.
   Configurar callbacks Discord e um ambiente separado para iniciar o fluxo.
3. Implementar adaptadores OAuth/HTTP com biblioteca mantida, proteção de
   sessão/estado e validações de provedor. Não expor o laboratório como API.
4. Executar a leitura de uma ficha descartável, reiniciar, renovar, revogar e
   reconectar, com as duas identidades Discord quando disponíveis.

Não resolver essa dependência reutilizando credenciais da Arquivista ou
iniciando outro bot com o token de produção.

## Próximo passo

A etapa 2 pode avançar offline: banco definitivo, migrações, retenção e
permissões usando o contrato. **GPT-6.1 Sol · Alto** é a recomendação para
essa tarefa. A prova nativa da etapa 1 permanece uma pendência de liberação
e deve ser retomada junto da etapa 3, quando houver configuração externa.

Não há campo da planilha aprovado para escrita nesta rodada. Atualizações
da ficha, modelos por servidor, edição, revisão do mestre e publicação
continuam nas etapas previstas, sem ampliar autorização por consequência.
