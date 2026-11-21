# Publicação dos cartões 6 e 7 de Classe 0 (Prática Cotidiana)

O app Guias do Ciclo (`1773761486581`) voltou ao ar em **20/11/2026 às
22:27:17**, horário de Brasília. O runtime é o merge
`c0004f438030d39352d281b9fbff39d3953c5c77` da
[PR #118](https://github.com/cupcake-mochi/RPG---BOT/pull/118).

A consulta continua na R68/v0.379, e a análise continua no R53.

**O que muda.** Desde 05/11 (Ficha---RPG-JJK@`bc4bd46`), a ficha tem 251
cartões R53. A Prática Cotidiana somou `classe0.6` e `classe0.7`, de Classe 0,
e 91 chaves no fim da ANALISE. O bot conhecia só 249 cartões. Com isso, quem
preenchia o cartão 6 ou 7 recebia um erro de formato ("um dos 249 cartões
publicados") e 55 chaves não reconhecidas. Com os cartões vazios, a página
Limites da análise listava as chaves cruas (`r53.classe0.6.*`, `zero.6.*`…).

- O `r53/contextos.json` ganhou os dois cartões, iguais aos do EditorR53 de
  Ficha---RPG-JJK@`78fc37d`.
- As 91 chaves entram como opcionais, no arquivo
  `recursos/pratica-cotidiana-campos.tsv`, lido das oficiais exportadas em
  19/11. Elas são reconhecidas quando vêm, e a falta delas não gera pendência.
  Uma cópia anterior a 05/11 dá o mesmo veredito.
- Nenhuma regra ou número de mecânica mudou.

## Git e testes

- O CI da PR passou no commit `f9b3a52`, com 1.741 testes, OK e um pulado. O
  primeiro CI falhou num único teste, `test_r53_definitiva`, que contava 18.393
  chaves na ficha sintética. Agora a conta é 18.393 + 91.
- Os testes novos estão em `test_r53.py`:
  - os cartões 6 e 7 gravados, com o aviso do cartão 7;
  - as partes iguais às dos cartões 1;
  - os tipos;
  - a cópia sem as chaves dá o mesmo veredito, os mesmos problemas e as mesmas
    pendências.
- Teste com a Ciclo oficial exportada e o cartão 6 preenchido:
  - código antigo: 6 erros, sendo o novo o `formato r53.classe0.6.entrada`, e
    55 chaves não reconhecidas;
  - código novo: 5 erros e 9 pendências, os mesmos da ficha em branco,
    "Classe 0 6: … ficha VÁLIDO" e 0 chaves adicionais.

## Discloud

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio (22:25) | 188 | 3453587 | `7ba510a2081b30859e201b6a9f541ec60ae69e0a98c96a1eac6dc68af9a68a64` |
| Pacote (`ferramentas/empacotar.py`, commit `c0004f4`) | 94 | 1867918 | `9f1c23dfb69efb1c1067478b5a486346bcd49fb544b5d0b9cd49a55a6d716598` |
| Backup depois do envio (22:28) | 189 | 3455367 | `ab61498cb3be7940ddf1d5d99cd30f2e46c2714592311531c7d5b15bcefc7d4e` |

- **Montagem do pacote.** Foi feita num clone novo com `core.autocrlf=false`.
  - O `nucleo.js` veio com CRLF e foi normalizado para LF, como nas outras
    vezes.
  - Os 93 arquivos versionados são iguais ao commit, e nenhum arquivo de texto
    tem CRLF.
  - O pacote tem um arquivo a mais, o TSV novo.
- **O que estava instalado.** O backup de antes confirmou o runtime `56b02cf`.
  - Contra ele, o pacote trocava `ficha_esquema.py`, `ficha_r53.py` e
    `r53/contextos.json`, e acrescentava `recursos/pratica-cotidiana-campos.tsv`.
  - Em relação ao backup das 00:03, o `.env`, a campanha e o `closure_lab.db`
    estavam iguais. O `bot.sqlite3` só mudou com o uso: cresceu, e as tabelas
    do dia recomeçaram.
- **Envio.** Foi pelo Commit do app existente, com o build automático. O ZIP
  foi anexado do mesmo jeito do registro
  [das Famílias](PUBLICACAO-FAMILIAS-2026-11-20.md).
- **Conferência no backup de depois.**
  - Os 94 arquivos do pacote estão instalados iguais.
  - O `.env` e a campanha têm o mesmo hash do backup de antes.
  - Os dois bancos deram `integrity_check` `ok`, e as 18 tabelas estão iguais.
- **Guarda.** Os backups ficam fora do Git, em `D:\Downloads`, com o nome
  `backup-guias-2026-11-20-HHMM-…-pratica-cotidiana.zip`.
  - O Chrome deixou o download de antes como `.tmp` por alguns segundos, então
    o ZIP (íntegro) foi copiado antes de o navegador terminar.
  - A cópia ficou igual byte a byte ao download final. O arquivo
    `cd355fa8-….tmp` não ficou em `D:\Downloads`.

## Conferência em produção

- **Logs:** online em **7 servidores** às 22:27:17, com zero erros. Só aparecem
  os avisos de voz já conhecidos.
- **Discord, 22:32, tópico Testes.** Mandei o `GC:ficha` com uma cópia
  descartável da Ciclo oficial (exportada às 21:13 de 20/11), com o cartão 6 de
  Classe 0 preenchido. Só as 16 células B da ANALISE do cartão foram trocadas
  no XML; o resto do arquivo é o original.
  [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1573511435324235910)
  - **5 erros, 9 pendências e 6 páginas**, os mesmos da ficha em branco.
  - Em Feitiços e técnicas aparece "Classe 0 6 · Classe 0 · Utilidade definida
    na Regra; sem resultado variável; Saldo sem uso 2 pontos · 0 PE · saldo 2 ·
    ficha VÁLIDO".
  - Nenhuma das 6 páginas mostra chave crua (`r53.`, `zero.N`, `classe0.`). A
    observação de apresentação do
    [registro de 19/11](PUBLICACAO-EXP-ACERTO-R53-2026-11-19.md) está resolvida.
  - O log registrou "ficha analisada: reprovada, 5 problema(s)".
  - Não houve chamada paga.

## Limitação conhecida

A regra `zeros_adicionais`, em `ficha_repertorio.py`, dá +2 Classe 0 com a
Prática Cotidiana na Restrição corporal. Ela não cobre a Prática Cotidiana
herdada por Restrição custom, que a ficha aceita. Ficou de fora para não mexer
em mecânica.

## Pendências reais

- A divergência de RAM (`RAM=256` no `discloud.config`, 512 MB no painel)
  continua em aberto.
