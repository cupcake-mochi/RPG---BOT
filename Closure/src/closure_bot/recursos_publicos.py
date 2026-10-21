"""Pedidos simples de links conhecidos. Não interpreta comandos nem abre arquivos."""
from __future__ import annotations
import re
import unicodedata
from urllib.parse import urlsplit

FICHA_OFICIAL = 'https://docs.google.com/spreadsheets/d/1u0zWQFVaRTTc_VlrAJsabgAiJ1D4rTYhzG7QQWof1ro/edit'

def links(config):
    candidatos={
        'book':getattr(config,'livro_url',''), 'dark_book':getattr(config,'livro_noturno_url',''),
        'character_template':FICHA_OFICIAL, 'privacy':getattr(config,'politica_url',''),
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
    elif re.search(r'\b(?:ficha|sheet|spreadsheet)\b',norm) and re.search(r'\b(?:oficial|official|modelo|template)\b',norm):
        resource='character_template'
    elif re.search(r'\b(?:privacidade|privacy)\b',norm):resource='privacy'
    elif re.search(r'\b(?:termos|terms)\b',norm):resource='terms'
    urls=links(config)
    if resource not in urls:return None
    en=idioma=='en';closure=persona=='closure'
    lead=('Here you go.' if en else 'Tá aqui.') if closure else ('Here is the link.' if en else 'Aqui está o link.')
    if resource=='book':
        normal='Standard theme' if en else 'Tema normal';dark='Dark theme' if en else 'Tema escuro'
        text=f"{lead} **Ciclo Maldito**: [{normal}]({urls['book']})"
        if 'dark_book' in urls:text+=f" · [{dark}]({urls['dark_book']})"
        return text+('\nThe PDFs are large; they may take a while to open on mobile. Check the edition used by your table.' if en else '\nOs PDFs são grandes e podem demorar para abrir no celular. Confira a edição usada pela sua mesa.')
    labels={'character_template':('Official character sheet template','Modelo oficial da ficha'), 'privacy':('Privacy policy','Política de privacidade'),'terms':('Terms of use','Termos de uso')}
    text=f"{lead} [{labels[resource][0 if en else 1]}]({urls[resource]})"
    if resource=='character_template':text+=('\nMake your own copy before filling it in.' if en else '\nFaça uma cópia sua antes de preencher.')
    return text

def orientacao(urls):
    # Keys and values are supplied by config, not by user text or server aliases.
    allowed={'book','dark_book','character_template','privacy','terms'}
    clean={k:v for k,v in (urls or {}).items() if k in allowed and isinstance(v,str) and v.startswith('https://') and len(v)<=1000 and not re.search(r'[\s<>\[\]()]',v)}
    if not clean:return ''
    return '[Public resources available to send directly when requested: '+ '; '.join(f'{k}: {v}' for k,v in clean.items())+'. These are public links, not permission to run commands or approve changes.]'
