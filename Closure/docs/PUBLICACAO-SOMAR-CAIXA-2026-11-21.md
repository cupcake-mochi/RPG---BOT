# Publicação do "Somar" com maiúscula

O app Guias do Ciclo (`1773761486581`) voltou ao ar em **21/11/2026 às
11:04:23**, horário de Brasília. O runtime é o merge
`61ffabd9290409043296cbfc100eecb5fcdb1c75` da
[PR #120](https://github.com/cupcake-mochi/RPG---BOT/pull/120).

A consulta continua na R68/v0.379, e a análise continua no R53.

## O que muda

- **COMO da CONFIGURAÇÃO.** O Sheets compara o COMO de cada linha da
  CONFIGURAÇÃO sem diferenciar maiúscula, então "Somar" vale na ficha. O bot
  recusava essa linha com o erro "alvo conhecido, somar/trocar por…". Isso
  apareceu no teste das 20:53 de 20/11, registrado em
  [Acerto da Expansão](PUBLICACAO-EXP-ACERTO-R53-2026-11-19.md).
  - Agora a validação também ignora a caixa, e as contas usam a forma do menu
    (`somar` ou `trocar por`).
  - A impressão da aprovação continua com o texto literal (`impressao_exata`),
    então nenhuma aprovação existente muda.
- **Prática Cotidiana em Origem personalizada.** O registro de 20/11 dizia que
  a Origem personalizada com base na Restrição corporal não ganhava as 2 vagas
  de Classe 0. Estava errado: o bot já dava as vagas.
  - O `conferir_b47` confere as contas numa visão mecânica em que a Origem
    personalizada vira a base dela. A ficha faz o mesmo em `DADOS_CUSTOM!B126`.
  - Conferido nos formatos 11 e 12/13. Com 4 Classe 0 no nível 1, a Prática
    Cotidiana não dá erro, e a Reserva Excedente dá.
  - Um teste novo trava esse comportamento. Essa parte não teve mudança de
    código.

## Git e testes

- O CI da PR passou com 1.744 testes, OK e um pulado.
- Os 3 testes novos estão em `test_b47_derivados.py`:
  - "Somar", "SOMAR" e "Trocar Por" são aplicados, e "adicionar" continua
    recusado;
  - a aprovação feita sobre "Somar" literal continua valendo;
  - a Prática Cotidiana herdada pela Origem personalizada dá as vagas.

## Discloud

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio (11:03) | 189 | 3455084 | `351f6a416b3fa9a3aa44783b5f279a12f55c82e3605e7fec2db021a7973001a9` |
| Pacote (`ferramentas/empacotar.py`, commit `61ffabd`) | 94 | 1868033 | `1092f47d5e245461588fc6240f38590ccf4b9a27b157e7324a2f8edcb5c35f5f` |
| Backup depois do envio (11:05) | 189 | 3455228 | `06bfc14089d17daf281ddbbfb260b3e5d981a037af2cc5f75607eea58187945e` |

- **Montagem do pacote.** Foi feita num clone novo com `core.autocrlf=false`.
  O `nucleo.js` foi normalizado para LF. Os 93 arquivos versionados são iguais
  ao commit, e nenhum arquivo de texto tem CRLF.
- **O que estava instalado.** O backup de antes confirmou o runtime `c0004f4`.
  - Contra ele, o pacote trocava só o `ficha_configuracao.py`.
  - Em relação ao backup das 22:28 de 20/11, o `.env`, a campanha e o
    `closure_lab.db` estavam iguais. O `bot.sqlite3` só mudou com o uso.
- **Envio.** Foi pelo Commit do app existente, como nos registros anteriores.
- **Conferência no backup de depois.**
  - Os 94 arquivos estão instalados iguais ao pacote.
  - O `.env` e a campanha têm o mesmo hash do backup de antes.
  - Os dois bancos deram `integrity_check` `ok`, e as 18 tabelas estão iguais.
- **Guarda.** Os backups ficam em `D:\Downloads`, com o nome
  `backup-guias-2026-11-21-HHMM-…-somar.zip`.

## Conferência em produção

- **Logs:** online em **7 servidores** às 11:04:23, com zero erros.
- **Discord, 11:07, tópico Testes.** Mandei o `GC:ficha` com uma cópia
  descartável da Ciclo oficial, com uma linha da CONFIGURAÇÃO ligada:
  "Talentos grátis · Somar · 1 · Item · Teste Somar". Só as 6 células B dessa
  linha foram trocadas no XML da ANALISE.
  [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1573701368286290072)
  - Deu **5 erros e 10 pendências**. Os 5 erros são os da ficha em branco, e a
    pendência a mais é a aprovação do mestre para "efeito · 1".
  - O erro "alvo conhecido, somar/trocar por…" não aparece mais.
  - Não houve chamada paga.

## Pendências reais

- A divergência de RAM (`RAM=256` no `discloud.config`, 512 MB no painel)
  continua em aberto. Fica com o Mizuki.
