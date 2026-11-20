# Publicação do Acerto da Expansão nas fichas R53

O app Guias do Ciclo (`1773761486581`) voltou ao ar em **19/11/2026 às
20:51:00**, horário de Brasília. O runtime é o merge
`921e7c805e8ab1964c02abae298f9ee1c529e840` da
[PR #110](https://github.com/cupcake-mochi/RPG---BOT/pull/110).

A consulta continua na R68/v0.379, e a Técnica Máxima continua conferida pela
R67. O que muda: a análise da ficha aceita as 12 chaves
`invocacao.N.exp.acerto` como `resultado`, que é como a ficha exporta desde
07/11. Antes disso, toda ficha formato 13 dava 12 erros de formato, e o
`conferir_b47` parava antes das contas. Por isso nenhum cartão R53 era
conferido no Discord. O que mudou e por quê está em
[Acerto da Expansão das invocações no formato R53](EXP-ACERTO-R53-2026-11-19.md).

## Git e testes

- O CI da PR passou no commit `c27ed0d`, com 1.032 testes, OK e um pulado. O
  merge saiu com a árvore idêntica a esse commit.
- No Windows, rodando como o CI (`unittest discover -s testes`, com
  `PYTHONUTF8=1`), `test_r53` deu 37 de 39. Os 2 que falharam só importam o
  `discord.py`, que não estava instalado nesse computador.

## Discloud

| Arquivo | Arquivos | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Backup antes do envio (20:48) | 188 | 3446604 | `48b03c3beeed0964fe7caaac9551181cff38e7d944c56a4594c1e9c49480b195` |
| Pacote (`ferramentas/empacotar.py`, commit `921e7c8`) | 93 | 1866387 | `897eea755f08f3b511398d7c7d4cf5f75759bbae7005139edf3bbfa63871e96a` |
| Backup depois do envio (20:51) | 188 | 3447556 | `187d9cc6d2bdbfd7316944e416d2cb45373fd477d15010f333a1c70efc989d37` |

- **Montagem do pacote.** Foi feita num clone novo com `core.autocrlf=false`.
  Como nas outras vezes, o empacotador regerou `src/var/site/nucleo.js` com
  CRLF no Windows, e essa entrada foi normalizada para LF. Os 92 arquivos
  versionados são iguais byte a byte ao commit. O `nucleo.js` é gerado e ficou
  igual ao instalado. Nenhum arquivo de texto tem CRLF. O único arquivo com a
  sequência CRLF é o `painel_clima.webp`, que é imagem binária.
- **O que estava instalado.** O backup de antes confirmou o runtime `8fff6ac`.
  Contra ele, o pacote trocava só dois arquivos: `ficha_b47.py` e
  `ficha_esquema.py`.
- **Envio.** Foi pelo Commit do app existente, com o build automático. O ZIP foi
  anexado pela extensão do Claude no navegador do Mizuki.
  - A área de envio (`/dashboard/app/1773761486581/deploy`) só cria o
    `input type=file` na hora do clique, e não deixa ele na página.
  - Para anexar sem abrir o seletor nativo, o `click()` dos inputs de arquivo
    foi interceptado na própria aba. O input passou a ficar na página, a
    extensão anexou o ZIP nele e o clique original foi restaurado logo depois.
- **Conferência no backup de depois.**
  - Os 93 arquivos do pacote estão instalados iguais.
  - O `.env` e a campanha têm o mesmo hash do backup de antes.
  - Os dois bancos deram `integrity_check` `ok`. As 18 tabelas (2 + 16) têm o
    mesmo dump e as mesmas contagens.
  - A comparação foi feita por contagens e hashes, sem expor valores.
- **Guarda.** Os backups e o pacote ficam fora do Git, em armazenamento local
  privado.

## Conferência em produção

- **Logs:** online em **7 servidores** às 20:51:00, com zero erros. Só
  aparecem os avisos de voz já conhecidos (PyNaCl/davey).
- **Discord, 20:54–20:55, tópico Testes.** Rodei o `GC:ficha` com o link da
  oficial do Ciclo Maldito, a mesma das publicações anteriores.
  [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1573124313723306075)
  - Painel normal, reprovada, **5 erros, 9 pendências e 0 observações**, em
    **5 páginas**. Antes eram 12 erros, 0 pendências e 3 páginas.
  - Nenhum erro de `exp.acerto`: a palavra "acerto" não aparece no painel.
  - Os 5 erros são do personagem em branco: Caminho, Trilha, perícias e
    ofícios, famílias livres (2) e famílias fechadas (3).
  - As 9 pendências também são da ficha vazia: capacidades da Origem, nome,
    pontos de atributo, TR e escolhas de treino.
  - Agora a parte R53 roda. A página Personagem mostra o Repertório (0 de 3
    espaços), maestria, Classe Máxima, refino de graça e Classe 0 grátis. A
    página Limites lista os campos `r53.classe0.*` que ainda não são
    conferidos.

## Conferências depois do registro (19/11, 21:52–21:57)

- **Era da Revolução.** O `GC:ficha` com o link da oficial deu o mesmo
  resultado da Ciclo: reprovada, 5 erros, 9 pendências e 0 observações, sem
  nenhum "acerto".
  [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1573138912149508237)
- **Cartão preenchido, por `.xlsx` anexo.**
  - A ficha foi uma cópia da descartável do ensaio pós-R67 (`1KCEtB…`, na
    lixeira desde o ensaio). Ela está no nível 17, com a Máxima "Teste R67
    Explosão" e a ANALISE exportada às 12:40.
  - A cópia (`15h6JR…`) foi baixada como `.xlsx` e mandada pra lixeira em
    seguida. Não precisou mexer em compartilhamento.
  - O painel ganhou a página **Feitiços e técnicas**: "Técnica Máxima — Teste
    R67 Explosão · Classe 5 · Dano 19d8; Saldo sem uso 8 pontos · 25 PE ·
    saldo 8 · ficha VÁLIDO". É a mesma conta do ensaio e da análise local.
  - A página Personagem mostra Repertório com 13 espaços, maestria 2, Classe
    Máxima 5, refino de graça 4 e Classe 0 grátis 5.
  - O resultado foi reprovada, com 7 erros, 9 pendências e 6 páginas.
  [Resposta](https://discord.com/channels/1357866906341736488/1561410667108368575/1573139714696028294)
- **Defeito visto.** Nesse painel, os erros "famílias livres" e "famílias
  fechadas" aparecem duas vezes na página Correções e revisão. Por isso o total
  é 7: são 5 erros diferentes. Na oficial em branco, cada um aparece uma vez só.
  Fica para uma correção separada.
- Isso também fecha a pendência "`.xlsx` de ficha 13 não testado com arquivo
  real" do [registro do formato 13](PUBLICACAO-FORMATO13-2026-11-19.md).

## Pendências reais

- Os cartões de feitiço e de Liberação preenchidos ainda não passaram pelo
  Discord. Só a Máxima passou.
- ~~A duplicação das famílias descrita acima.~~ Corrigida na PR #113 e publicada em 20/11. Veja o [registro](PUBLICACAO-FAMILIAS-2026-11-20.md).
- Não houve pergunta à Kal'tsit ou à Closure, porque essas chamam o modelo pago.
