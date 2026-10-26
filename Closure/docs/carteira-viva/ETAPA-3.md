# Conexão da ficha

26/10/2026 · etapa 3 · branch `codex/carteira-viva-etapa-3`, sobre `b491409`
da etapa 2/PR 79. PR 80 em rascunho, sem merge ou publicação. O serviço é
separado do bot; não há comando novo instalado na Discloud.

## Entrega

- OAuth com Authlib/PKCE e estado de uso único, vinculado à conta Discord que
  iniciou o pedido. Membro e cargos atuais conferidos pela API.
- Google por arquivo com Picker; apenas leitura de metadados e
  `ANALISE!A1:D32` para identificar formato/nome. Não confere a ficha inteira.
- Cadastro, reuso da autorização, reconexão e troca atômica de fonte; conta,
  versões e revisões bloqueiam respostas antigas e transferências indevidas.
- Tentativas cifradas com validade de dez minutos, cookies/CSRF/origem,
  limites, worker SQLite e limpeza local. Backup sem tentativas pendentes.
- Tela PT/EN, demonstração fictícia em loopback e ponte Discord opcional.
  Tradução dos comandos/integração do idioma do servidor entra na etapa 5.

Execução/configuração: [SERVICO.md](SERVICO.md) e
[ACESSO-GOOGLE.md](ACESSO-GOOGLE.md). Banco: [BANCO.md](BANCO.md).

## Conferido

**152 testes distintos da Carteira aprovados.** Suíte completa posterior às
correções nativas: **1.128 executados, 1.127 aprovados, um online opcional
pulado e zero falhas**, em 722,911 segundos. Comando em `Closure/src`:
`../.venv/bin/python -m unittest discover -s testes`.

Núcleo de consulta presente. Sem modelo pago: mensagens de custo/modelo na
suíte são simuladas. Smoke de isolamento passou: criar o serviço não importa
`discord` ou `closure_bot`. Manifesto do bot permanece em 90 arquivos, sem
Carteira, bancos ou ambiente; não foi preparado outro ZIP do bot.

A demonstração fictícia passou, inclusive tela pequena. Depois, o
[piloto com provedores reais](NATIVO-ETAPA-3.md) passou em cadastro, Picker,
reinício, refresh sem novo consentimento Google, revogação com bloqueio e
reconexão do mesmo personagem/arquivo. Os defeitos encontrados no piloto
foram corrigidos com regressões: client_id da URL, escopo de comandos herdado
do Discord, origem para validar chave restrita e layout do Picker sob CSP.

Google dedicado configurado em teste; Discord usa o aplicativo oficial por
escolha do usuário. O próprio usuário preparou o segredo OAuth, sem mudar o
token do bot. Credenciais privadas fora do Git. A cópia foi para a lixeira,
o cadastro fictício foi removido e o grant Google de teste foi revogado.
Nenhuma ficha oficial ou de jogador foi editada; nenhum app Discord extra
foi criado, nem a Discloud foi reiniciada/publicada nesta rodada.

## O que permanece

- Próxima implementação: **etapa 4**, leitura completa sob demanda e análise
  privada determinística, incluindo campanha e aprovações exatas do servidor.
- Troca entre dois arquivos distintos, conta errada, callbacks atrasados e
  rollback estão cobertos offline; não foram todos repetidos no provedor real.
- Comandos, cargos reais e galeria ainda não estão integrados ao Discord;
  celular físico e origem HTTPS pública não foram validados/contratados.
- Antes de público geral: completar divulgação de privacidade/termos Google,
  verificação/publicação do consentimento e hospedagem. O teste não prova
  capacidade, análise completa ou autorização permanente.
- CI do checkpoint `88751e1` passou. Conferir o SHA posterior com as demais
  correções nativas na PR 80 antes de integrar. Não dar merge nas PRs dependentes
  nem publicar por causa deste relatório.

Modelo recomendado para continuar: **GPT-6.1 Sol · Alto**. Pode manter a
configuração. Prompt completo em [RETOMADA.md](RETOMADA.md).
