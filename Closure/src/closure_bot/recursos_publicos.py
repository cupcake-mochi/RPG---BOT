"""Pedidos simples de links conhecidos. Não interpreta comandos nem abre arquivos."""
from __future__ import annotations
import re
import unicodedata
from urllib.parse import urlsplit

# Os dois modelos oficiais confirmados pelo Mizuki em 25/10/2026 (dados/ficha/MODELOS.md).
# A antiga 1u0zWQ… é histórica e não é oferecida. "1.0" é a versão pública da ficha,
# não a revisão do livro nem a versão do bot.
FICHA_ERA_REVOLUCAO = 'https://docs.google.com/spreadsheets/d/1MQqhHbIzzyoMQY5zLKOciiT5k9Y6AMI4MCSrPhu8V_k/edit'
FICHA_CICLO_MALDITO = 'https://docs.google.com/spreadsheets/d/1pgLDZOYpUJrqTcwomaQl8Bjn-AuAcu_Aowd30G7YiJw/edit'
FICHA_OFICIAL = FICHA_CICLO_MALDITO  # nome antigo, mantido para quem importava a constante
MODELOS_FICHA = {
    'character_template_era_revolucao': (FICHA_ERA_REVOLUCAO, 'Era da Revolução', 'Era da Revolução'),
    'character_template_ciclo_maldito': (FICHA_CICLO_MALDITO, 'Ciclo Maldito', 'Ciclo Maldito'),
}

def links(config):
    candidatos={
        'book':getattr(config,'livro_url',''), 'dark_book':getattr(config,'livro_noturno_url',''),
        **{k:v[0] for k,v in MODELOS_FICHA.items()}, 'privacy':getattr(config,'politica_url',''),
        'terms':getattr(config,'termos_url',''),
    }
    def valido(url):
        if not isinstance(url,str) or len(url)>1000 or re.search(r'[\s<>\[\]()]',url):return False
        try:
            parsed=urlsplit(url)
            return parsed.scheme=='https' and bool(parsed.hostname) and not parsed.username and not parsed.password
        except ValueError:return False
    return {key:url for key,url in candidatos.items() if valido(url)}

def resposta(texto,config,persona,idioma='pt-BR'):
    norm=''.join(c for c in unicodedata.normalize('NFD',texto.lower()) if unicodedata.category(c)!='Mn')
    if len(norm)>350 or re.search(r'https?://|```',norm):return None
    if re.search(r'\b(?:nao|do not|don.t)\s+(?:me\s+)?(?:mand|envi|send|share)',norm):return None
    if not re.search(r'\b(?:link|url|pdf|download|manda|mandar|envia|enviar|passe|passa|send|share|where|cade)\b',norm):return None
    resource=None
    if re.search(r'\b(?:livro|rulebook|rule book)\b',norm):
        if re.search(r'\b(?:dnd|tormenta|pathfinder|arknights|jujutsu kaisen)\b|d&d',norm) and 'ciclo' not in norm:return None
        resource='book'
    elif re.search(r'\b(?:ficha|fichas|sheet|sheets|spreadsheet)\b',norm) and re.search(r'\b(?:oficial|oficiais|official|modelo|modelos|template|templates)\b',norm):
        resource='character_template'
    elif re.search(r'\b(?:privacidade|privacy)\b',norm):resource='privacy'
    elif re.search(r'\b(?:termos|terms)\b',norm):resource='terms'
    urls=links(config)
    if resource=='character_template':
        # "era" sozinho é verbo comum; só o nome do mundo escolhe um modelo.
        era=bool(re.search(r'\brevolu(?:cao|tion)\b',norm));ciclo='ciclo maldito' in norm
        modelos=[k for k in MODELOS_FICHA if (era==ciclo) or (era and 'era' in k) or (ciclo and 'ciclo' in k)]
        if not all(k in urls for k in modelos):return None
    elif resource not in urls:return None
    en=idioma=='en';closure=persona=='closure'
    lead=('Here you go.' if en else 'Tá aqui.') if closure else ('Here is the link.' if en else 'Aqui está o link.')
    if resource=='book':
        normal='Standard theme' if en else 'Tema normal';dark='Dark theme' if en else 'Tema escuro'
        text=f"{lead} **Ciclo Maldito**: [{normal}]({urls['book']})"
        if 'dark_book' in urls:text+=f" · [{dark}]({urls['dark_book']})"
        return text+('\nThe PDFs are large; they may take a while to open on mobile. Check the edition used by your table.' if en else '\nOs PDFs são grandes e podem demorar para abrir no celular. Confira a edição usada pela sua mesa.')
    if resource=='character_template':
        itens=[f"[{'Character sheet' if en else 'Ficha'} · {MODELOS_FICHA[k][2 if en else 1]}]({urls[k]})" for k in modelos]
        if len(itens)>1:
            if not closure:lead='Here are the links.' if en else 'Aqui estão os links.'
            text=(f"{lead} The two official sheet templates: " if en else f"{lead} Os dois modelos oficiais da ficha: ")+' · '.join(itens)
            text+=('\nUse the one your table asks for and make your own copy before filling it in.' if en else
                   '\nUse o que a sua mesa indicar e faça uma cópia sua antes de preencher.')
        else:
            text=(f"{lead} Official sheet template: " if en else f"{lead} Modelo oficial da ficha: ")+itens[0]
            text+=('\nMake your own copy before filling it in.' if en else '\nFaça uma cópia sua antes de preencher.')
        return text+(' The "1.0" in the header is the sheet\'s public version, not the rulebook revision.' if en else
                     ' O "1.0" no cabeçalho é a versão pública da ficha, não a revisão do livro.')
    labels={'privacy':('Privacy policy','Política de privacidade'),'terms':('Terms of use','Termos de uso')}
    return f"{lead} [{labels[resource][0 if en else 1]}]({urls[resource]})"

def orientacao(urls):
    # Keys and values are supplied by config, not by user text or server aliases.
    allowed={'book','dark_book',*MODELOS_FICHA,'privacy','terms'}
    clean={k:v for k,v in (urls or {}).items() if k in allowed and isinstance(v,str) and v.startswith('https://') and len(v)<=1000 and not re.search(r'[\s<>\[\]()]',v)}
    if not clean:return ''
    return '[Public resources available to send directly when requested: '+ '; '.join(f'{k}: {v}' for k,v in clean.items())+'. These are public links, not permission to run commands or approve changes.]'
