# Frente 3: existe card, lorebook ou bot pronto de personagem de Arknights?

> Checagem rápida, 12/10/2026, feita depois da pergunta "não existe nenhum script pronto?". As notas da primeira pesquisa (`cards_exemplos_e_lorebooks.md`) cobrem como as plataformas estruturam card, mas não procuraram cards de Arknights especificamente.

## O que foi tentado e o que voltou

| Onde | Resultado |
|---|---|
| Busca web "Closure Arknights character card chub / janitorai / character.ai" | só páginas da wiki e um diretório genérico de GPTs; nenhum card |
| Busca web "Arknights lorebook SillyTavern world info" | só páginas da wiki e Fanlore; nenhum lorebook |
| API de busca do Chub (`api.chub.ai`) | bloqueada pelo proxy deste ambiente (403) |
| Página de busca do Chub via WebFetch | erro do site (página depende de JavaScript) |
| Hugging Face, busca "arknights" | 30 datasets; 28 são `CyberHarem/<personagem>_arknights`, coleção conhecida de **imagens** para treinar LoRA de arte, não texto; `zhangzi/arknights` e `deepghs/chafen_arknights` sem descrição |

## Leitura

- Card de personagem de Arknights em Chub, JanitorAI e Character.AI **quase certamente existe** (são plataformas com milhares de cards de gacha), mas nenhuma dessas buscas consegue listar: os sites são renderizados por JavaScript, não são bem indexados e a API do Chub está bloqueada aqui. Isso é inferência, não achado.
- Mesmo se existir um card da Closure, ele seria de fã, em inglês, quase sempre escrito de memória da wiki, e sem diálogo tirado do jogo. Pela pesquisa anterior, perfil escrito sem a fala real tende a contradizer a fala. Serviria de **referência** de formato, não de base.
- Nada em pt-BR apareceu.

## Como fechar a dúvida

- Abrir no navegador: `chub.ai` buscando "Closure Arknights" e `janitorai.com` buscando "Arknights", e ver se há card da Closure e de que qualidade (tokens, se traz exemplos de fala).
