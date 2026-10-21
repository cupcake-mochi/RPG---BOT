"""English display of deterministic results. Canonical keys and user text are unchanged."""
from __future__ import annotations
import json
import re
from functools import lru_cache
from pathlib import Path
from collections import OrderedDict
import discord

LABELS = {
    'Perícias e ofícios':'Skills and trades','Pontos de atributo':'Attribute points','Perícias':'Skills','Ofícios':'Trades',
    'Testes de Resistência':'Saving throws','Grau do uniforme':'Uniform Grade','Força da mão principal':'Main-hand Strength',
    'Força da mão secundária':'Off-hand Strength','Força do uniforme':'Uniform Strength','Requisito de Força':'Strength requirement',
    'Treino da arma':'Weapon training','Selo':'Seal','Vagas de pacto':'Vow slots','Caminho':'Path','Trilha':'Branch','Origem':'Origin',
    'Vida':'HP','PE':'EP','Integridade':'Integrity','Proteção':'Protection','Defesa':'Defense','Formato da ficha':'Sheet format',
    'Repertório':'Repertoire','Espaços de repertório':'Repertoire slots','Marcos de Leque':'Leque milestones',
    'Marcos de Corpo':'Corpo milestones','Marcos de Refino':'Refino milestones','Rota de criação':'Creation route',
    'Categoria da Regra Própria':'Custom Rule category','Espaços da Regra Própria':'Custom Rule slots','Degrau do Domínio':'Domain tier',
    'Espaços do Domínio':'Domain slots','Talento CE4 da Origem':'Origin EC4 Talent','Arma principal':'Main-hand weapon',
    'Mão secundária':'Off hand','Uniforme':'Uniform','Carga':'Load','Carga total':'Total load','Limite de carga':'Load limit',
    'Buff/Debuff do limite de carga':'Load-limit adjustment','Escolhas de treino':'Training choices',
    'Pontos de atributo por criação e marcos':'Attribute points from creation and milestones','Pontos de Corpo':'Corpo points',
    'Força':'Strength','Destreza':'Dexterity','Constituição':'Constitution','Inteligência':'Intelligence','Essência':'Essence',
    'Classe':'Class','nível':'level','retorno':'return cost','entrada':'entry cost','CD':'DC','acerto':'attack bonus',
    'deslocamento':'movement','Melhorias':'Improvements','Restrições':'Restrictions','atributos':'attributes','nome':'name',
    'Forma':'Form','nível de aquisição':'acquisition level','Famílias':'Families','montagem':'build','resolução':'resolution','alcance':'range','Dano':'Damage','dano-base':'base damage','bônus':'bonus',
    'especialização':'specialization','quantidade':'quantity','atributo':'attribute','Perícia própria':'Custom skill',
    'Ofício próprio':'Custom trade','Origem própria':'Custom Origin','Melhoria própria':'Custom Improvement',
    'Restrição própria':'Custom Restriction','Forma própria':'Custom Form','Perícia':'Skill','Ofício':'Trade','Equipável':'Equipment',
    'Item':'Item','TR':'Saving throw','Físico':'Physical','Vigor':'Vigor','Intelecto':'Intellect','Espírito':'Spirit',
    'básica':'basic ability','especial':'special ability','habilidade da Trilha':'Branch ability','Técnica Máxima':'Maximum Technique',
    'Feitiço':'Spell','Liberação':'Release','Invocação':'Summon','Talento':'Talent','Classe 0':'Class 0',
    'orçamento':'budget','base das funções':'function base','custo da Forma':'Form cost','Melhorias pagas':'paid Improvements',
    'devolução':'refund','dano (d8)':'damage (d8)','cura (d8)':'healing (d8)','PV temporários':'temporary HP',
    'saldo sem uso':'unused balance','CD de Controle':'Control DC','resumo da função':'function summary',
    'avisos do cartão':'card warnings','registro ativo':'active record','Classe máxima':'maximum Class',
}
# Only UI labels enter this function; user/card names are appended afterwards.
def label(text):
    if text in LABELS:return LABELS[text]
    out=[]
    for part in text.split(' · '):
        if part.startswith('Buff/Debuff de '):
            out.append('Adjustment to '+label(part[15:]));continue
        found=False
        for a,b in sorted(LABELS.items(),key=lambda p:-len(p[0])):
            if re.fullmatch(re.escape(a)+r' \d+',part):
                out.append(b+part[len(a):]);found=True;break
        if not found:out.append(LABELS.get(part,part))
    return ' · '.join(out)

@lru_cache(maxsize=1)
def patterns():
    data=json.loads((Path(__file__).parent/'recursos/ficha-en.json').read_text())
    result=[]
    for pt,en in data.items():
        if not re.search(r'\{\d+(?::[^}]+)?\}',pt):continue
        chunks=re.split(r'(\{\d+(?::[^}]+)?\})',pt)
        regex='';seen=set()
        for p in chunks:
            m=re.fullmatch(r'\{(\d+)(?::[^}]+)?\}',p)
            if m:
                n=m[1];regex+=f'(?P<x{n}>.*?)' if n not in seen else f'(?P=x{n})';seen.add(n)
            else:regex+=re.escape(p)
        result.append((len(re.sub(r'\{[^}]+\}','',pt)),re.compile(regex,re.S),en))
    return data,sorted(result,key=lambda t:-t[0])


def detail(text):
    """Translate known engine messages only. Captures keep their original spelling and value."""
    text=str(text)
    data,templates=patterns()
    if text in data:return data[text]
    for _,regex,en in templates:
        m=regex.fullmatch(text)
        if m:
            # Values are already formatted by the engine: no second numeric conversion.
            values={int(k[1:]):v for k,v in m.groupdict().items()}
            return re.sub(r'\{(\d+)(?::[^}]+)?\}',lambda n:values[int(n[1])],en)
    return text


def line(p):
    from .cogs.ficha import _rotulo
    name=label(_rotulo(p.campo));found=p.encontrado;expected=detail(p.esperado)
    if p.regra=='buff':
        if re.fullmatch(r'\d+(?:[.,]\d+)?',found):found='+'+found
        return f'**{name}**: {found}'
    if p.regra in ('conta','formato'):
        return f'**{name}**: reported {found}; expected {expected}'
    anchor=f' · rule `{p.ancora}`' if p.ancora else ''
    return f'**{name}** (`{p.campo}`): {expected} (reported: {found})'+anchor


def checked(text):
    """The engine prefixes are known; the remainder may contain user names and stays literal."""
    translated=detail(text)
    if translated!=text:return translated
    for a,b in sorted(LABELS.items(),key=lambda p:-len(p[0])):
        if text.startswith(a+' '):return b+text[len(a):]
    return text


def paginas(result,sheet,persona,manifest=None):
    from .cogs.ficha import COR,_campos,_rotulo,GRUPO,_nome_grupo,_valor_legivel
    from .ficha_leitor import Campo
    name=str(sheet.get('nome',Campo('','','')).valor).strip()
    title=('Character sheet · '+name if name else 'Unnamed character sheet')[:256]
    pending=bool(result.pendencias or result.notas or result.nao_conferido)
    visual='pendente' if result.veredito=='aprovada' and pending else result.veredito
    verdict={'aprovada':'passed within the checked scope','pendente':'partial review','reprovada':'corrections required','formato desconhecido':'unknown format'}[visual]
    description={'aprovada':'I checked the sheet. The values I can verify match the rules.',
        'pendente':'This is a partial review. The panel separates corrections, pending checks and the GM’s decisions.',
        'reprovada':'I checked the sheet and found corrections to make before play.',
        'formato desconhecido':'I do not recognize this sheet format. Download the current sheet version.'}[visual]
    if persona.chave=='closure':
        description={'aprovada':'I went through the sheet, and everything I can check lines up.',
          'pendente':'The check is only partial. I separated what needs attention and what the GM still needs to review.',
          'reprovada':'I went through the sheet and found a few things to fix.',
          'formato desconhecido':'I don’t recognize this sheet format. Could you get the current version?'}[visual]
    def base(state='aprovada'):
        e=discord.Embed(title=title,color=COR[state]);e.set_author(name=persona.nome,icon_url=persona.avatar_url or None);return e
    pages=[]
    def add(category,fields,state='aprovada',states=None):
        current=None;rank={'aprovada':0,'pendente':1,'reprovada':2};curstate=state
        for n,v in fields:
            if current is None or len(current)+len(n)+len(v)>3800 or len(current.fields)>=8:
                current=base(state);current.description='**'+category+'**';curstate=state;pages.append((category,current))
            target=(states or {}).get(n,state)
            if rank[target]>rank[curstate]:curstate=target;current.color=COR[target]
            current.add_field(name=n[:256],value=v,inline=False)
    summary=base(visual if visual in COR else 'pendente');summary.description=description
    summary.add_field(name='Result',value=f'**{verdict.capitalize()}**\n{len(result.problemas)} error(s) · {len(result.pendencias)} pending check(s) · {len(result.notas)} GM adjustment(s)',inline=False)
    reviews=[('❌ Corrections required',result.problemas),('⚠️ Missing or needs attention',result.pendencias),('👀 GM review',result.notas)]
    for heading,items in reviews:
        if items:
            lines=[];size=0
            for p in items[:3]:
                value=line(p)
                if size+len(value)>600:break
                lines.append(value);size+=len(value)+3
            value='\n'.join('• '+v for v in lines)
            if len(lines)<len(items):value+=f'\n• {len(items)-len(lines)} more on the Corrections and review pages.'
            summary.add_field(name=heading,value=value,inline=False)
    personal=[];groups=OrderedDict();tests=OrderedDict()
    for value in result.conferidos:
        m=re.fullmatch(r'(.+): bônus ([+-]\d+(?:\.\d+)?)',value)
        if m:
            test,bonus=m.groups();entity=re.match(r'^(Invocação \d+) · (.+)$',test)
            category,test=entity.groups() if entity else ('Saving throws' if test.startswith('TR ') else 'Skills and trades',test)
            tests.setdefault(label(category),[]).append(f'**{checked(test)}**: {bonus}');continue
        m=GRUPO.match(value)
        if m:groups.setdefault(m[1],[]).append(checked(_valor_legivel(m[2])))
        else:personal.append(value)
    basics=[]
    prefixes=('Caminho ','Trilha ','Origem ','Vida ','PE ','Integridade ','Proteção ','Defesa ')
    for group in (prefixes[:3],prefixes[3:6],prefixes[6:]):
        values=[checked(v) for v in personal if v.startswith(group)]
        if values:basics.append(' · '.join(values))
    if basics:summary.add_field(name='✅ Checked and correct',value='\n'.join(basics)[:1000],inline=False)
    if groups:
        summons={re.match(r'Invocação \d+',g)[0] for g in groups if g.startswith('Invocação ')}
        abilities=sum(not re.fullmatch(r'Invocação \d+',g) for g in groups)
        summary.add_field(name='Checked details',value=f'{abilities} '+('ability' if abilities==1 else 'abilities')+f' · {len(summons)} '+('summon' if len(summons)==1 else 'summons')+'. Use the menu or arrows to browse.',inline=False)
    if tests:summary.add_field(name='Saving throws and skills',value=f'{sum(map(len,tests.values()))} checked bonuses. See the Saving throws and skills pages.',inline=False)
    if result.nao_conferido:summary.add_field(name='⏳ Still unchecked',value='Some items need manual review. See the Analysis limits pages.',inline=False)
    summary.add_field(name='GM review',value='Use `GC:guide gm` or `/ficha mestre` to review the whole sheet alongside this panel. The guide explains the process; the GM makes the decision.',inline=False)
    summary.add_field(name='Sheet and rule names',value='Official sheet labels, option names, exported keys and player-written text keep their original spelling so you can find them in the sheet.',inline=False)
    pages.append(('Summary',summary))
    fields=[]
    for heading,items in reviews:fields+=_campos(heading,[line(p) for p in items])
    add('Corrections and review',fields,'pendente',{'❌ Corrections required':'reprovada'})
    add('Character',_campos('Other checked values',[checked(t) for t in personal if not t.startswith(prefixes)]))
    fields=[]
    for category,values in tests.items():fields+=_campos(category,values)
    add('Saving throws and skills',fields)
    spells=[];entities=OrderedDict()
    for group,values in groups.items():
        raw=_nome_grupo(group,sheet);prefix,sep,suffix=raw.partition(' — ')
        heading=label(prefix)+(sep+suffix if sep else '')
        fields=_campos(heading,values)
        if group.startswith('Invocação '):entities.setdefault(label(re.match(r'Invocação \d+',group)[0]),[]).extend(fields)
        else:spells+=fields
    add('Spells and techniques',spells)
    for category,fields in entities.items():add(category,fields)
    add('Analysis limits',_campos('Manual review and missing inputs',[detail(t) for t in result.nao_conferido]),'pendente')
    book=(manifest or {}).get('edicao_livro','')
    for i,(category,e) in enumerate(pages):
        e.set_footer(text=f'Page {i+1} of {len(pages)} · {category} · Overall result: {verdict} · rules {book}'+(' · controls for 10 min' if len(pages)>1 else '')+' · the GM can decline even when all checked values match')
    return [e for _,e in pages]
