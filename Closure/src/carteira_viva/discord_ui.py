"""Cartões e controles Discord. Ações de acesso voltam sempre ao serviço."""
from datetime import datetime,timezone
import io
import re
from types import SimpleNamespace
import discord
from .cliente_discord import FalhaCarteira

TEXTOS={
 'vazio':('Nenhum personagem cadastrado para este jogador. Use /personagem cadastrar para conectar uma ficha.','This player has no registered characters. Use /character register to connect a sheet.'),
 'escolher':('Escolha um personagem','Choose a character'), 'anterior':('Anterior','Previous'), 'proxima':('Próxima','Next'),
 'detalhes':('Detalhes · privado','Details · private'),'analisar':('Analisar · privado','Analyse · private'),
 'atualizar':('Atualizar dados','Refresh data'),'editar':('Editar cartão','Edit card'),'imagem':('Imagem do cartão','Card image'),
 'trocar':('Trocar arquivo','Replace sheet'),'salvar':('Salvar cartão','Save card'),'cancelar':('Cancelar','Cancel'),
 'preview':('Prévia · nada foi salvo ainda','Preview · nothing has been saved yet'),
 'salvo':('Cartão salvo. Abra a galeria novamente para ver a apresentação atual.','Card saved. Reopen the gallery to see its current presentation.'),
 'cancelado':('Prévia cancelada. O cartão continua igual.','Preview cancelled. The card is unchanged.'),
 'dono':('Jogador responsável','Player'), 'idade':('Idade','Age'),'cla':('Clã','Clan'),'origem':('Origem','Origin'),'caminho':('Caminho','Path'),
 'leitura':('Última leitura da ficha','Sheet last read'),'nunca':('Ainda não consultada','Not read yet'),
 'antigo':('Dados salvos · precisam de atualização','Saved data · refresh needed'),'recente':('Leitura recente','Recently read'),
 'aviso':('Não foi possível atualizar agora. Este cartão mostra os últimos dados salvos.','Could not refresh right now. This card shows the last saved data.'),
 'somente':('Abra /personagens para usar seus próprios controles.','Open /characters to use your own controls.'),
 'expirou':('Estes controles expiraram. Abra /personagens novamente.','These controls expired. Open /characters again.'),
 'sem_arquivo':('Abra este comando no servidor do personagem.','Use this command in the character’s server.'),
 'foto_ajuda':('Use /personagem imagem e anexe PNG, JPEG ou WebP de até 1 MiB, sem animação. A prévia precisa ser confirmada e não altera a planilha.','Use /character image and attach a PNG, JPEG or WebP up to 1 MiB, without animation. Confirm the preview to save; the sheet is not edited.'),
 'continuar_edicao':('Abra o formulário para editar título, frase, cor e o que aparece no cartão. A planilha não será alterada.','Open the form to edit the title, quote, colour and visible card fields. The sheet will not be edited.'),
 'abrir_formulario':('Abrir formulário','Open form'),'formulario':('Apresentação do personagem','Character presentation'),
 'titulo':('Título (opcional)','Title (optional)'),'frase':('Frase (opcional)','Quote (optional)'),
 'cor':('Cor (#RRGGBB; vazio usa o padrão)','Colour (#RRGGBB; empty uses default)'),
 'extras':('Extras visíveis (lista abaixo)','Visible extras (list below)'),
 'exemplos':('idade, clã, origem, caminho, imagem','age, clan, origin, path, image'),
 'limparfoto':('Para remover a imagem, apague “imagem” da lista de extras visíveis.','To hide the image, remove “image” from the visible extras list.'),
 'ficha':('Abrir planilha · Google verifica seu acesso','Open sheet · Google checks access'),
 'privado':('Somente você pode ver esta consulta. Cadastro e análise não aprovam a ficha.','Only you can see this view. Registration and analysis do not approve the sheet.'),
 'revisao':('Revisão do arquivo vinculado','Linked file revision'),'fonte':('Fonte e horário da análise','Analysis source and time'),
 'cargo':('Configuração de revisores atualizada. Dono do servidor e administradores já têm acesso; cargos de idioma/lore não são usados aqui.','Reviewer role settings updated. Server owner and administrators already have access; language/lore roles do not grant it.'),
 'nenhuma':('Nenhuma leitura atual disponível. Atualize ou reconecte sua ficha.','No current reading available. Refresh or reconnect your sheet.'),
}
ERROS={
 'imagem':('Use PNG, JPEG ou WebP sem animação, até 1 MiB. A imagem enviada não pôde ser preparada.','Use a PNG, JPEG or WebP without animation, up to 1 MiB. The image could not be prepared.'),
 'armazenamento':('O espaço de imagens está cheio. Peça ao operador do bot para conferir o armazenamento.','Image storage is full. Ask the bot operator to check the available space.'),
 'acesso':('Você não tem acesso a esta ação ou o personagem não está disponível neste servidor.','You cannot use this action, or the character is unavailable in this server.'),
 'conflito':('A fonte, campanha ou apresentação mudou. Abra a consulta ou prévia novamente.','The source, campaign or presentation changed. Open a new view or preview.'),
 'limite':('Há consultas demais em andamento. Tente novamente em instantes.','Too many requests are in progress. Please try again shortly.'),
 'tamanho':('O arquivo ou resultado excedeu o limite. Para imagem, use até 1 MiB.','The file or result exceeded the limit. Images must be up to 1 MiB.'),
 'leitura':('A ficha está incompleta ou recalculando. Confira a planilha e tente novamente.','The sheet is incomplete or recalculating. Check it and try again.'),
 'solicitacao':('Confira o código do personagem e os campos informados.','Check the character code and the supplied fields.'),
 'temporario':('Não consegui consultar a Carteira agora. Tente novamente ou reconecte a ficha se perdeu a autorização Google.','Could not reach the Character Wallet. Try again, or reconnect if Google access was revoked.'),
}


def txt(chave,lang):return TEXTOS[chave][lang=='en']
def erro(exc,lang):return ERROS.get(getattr(exc,'codigo','temporario'),ERROS['temporario'])[lang=='en']
def seguro(v,limite=1000):
    s=re.sub('[\x00-\x08\x0b-\x1f\u202a-\u202e\u2066-\u2069]','',str(v))
    s=re.sub(r'<([@#][!&]?)(\d+)>',lambda m:'<'+m[1]+'\u200b'+m[2]+'>',s)
    return discord.utils.escape_mentions(discord.utils.escape_markdown(s))[:limite]


def cartao_embed(card,lang):
    p=card['perfil'];e=discord.Embed(title=seguro(p.get('nome','Personagem'),100),colour=p.get('cor',0x397B77))
    e.description='\n\n'.join(x for x in (('**'+seguro(p['titulo'],200)+'**') if p.get('titulo') else '',seguro(p['frase'],500) if p.get('frase') else '') if x)
    e.add_field(name=txt('dono',lang),value='<@'+card['responsavel']+'>',inline=False)
    for campo in ('idade','cla','origem','caminho'):
        if campo in p and p[campo]!='':e.add_field(name=txt(campo,lang),value=seguro(p[campo],200),inline=True)
    hora=card.get('lido_em')
    e.add_field(name=txt('leitura',lang),value=f'<t:{int(hora)}:f>' if hora is not None else txt('nunca',lang),inline=False)
    estado=txt('antigo' if card.get('precisa_atualizar',True) else 'recente',lang)
    if card.get('aviso'):estado+=' · '+txt('aviso',lang)
    e.set_footer(text=estado)
    return e


class Controles(discord.ui.View):
    def __init__(self,cog,servidor,usuario,*,privado=False):
        super().__init__(timeout=600);self.cog,self.servidor,self.usuario,self.privado=cog,str(servidor),str(usuario),privado
        self.mensagem=None
    def lang(self):return self.cog.idioma_guild(self.servidor)
    async def interaction_check(self,i):
        if str(i.user.id)!=self.usuario or str(i.guild_id)!=self.servidor:
            await i.response.send_message(txt('somente',self.lang()),ephemeral=True,allowed_mentions=discord.AllowedMentions.none());return False
        return True
    async def pedir(self,acao,pid=None,**dados):
        return await self.cog.api.pedir(self.servidor,self.usuario,acao,personagem=pid,**dados)
    async def falhou(self,i,exc):
        await i.followup.send(erro(exc,self.lang()),ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
    async def on_timeout(self):
        for c in self.children:
            if hasattr(c,'disabled'):c.disabled=True
        if self.mensagem:
            try:await self.mensagem.edit(view=self)
            except discord.HTTPException:pass


class GaleriaView(Controles):
    def __init__(self,cog,s,u,dono,dados,*,single=False):
        super().__init__(cog,s,u);self.single=single;self.dono=str(dono);self.dados=dados;self.cursores=[''];self.pagina=0;self.card=dados['cartoes'][0] if dados['cartoes'] else None
        self.montar()
    def montar(self):
        self.clear_items();lang=self.lang()
        if self.dados['cartoes'] and not self.single:
            sel=discord.ui.Select(placeholder=txt('escolher',lang),options=[discord.SelectOption(label=seguro(c['perfil'].get('nome','Personagem'),85),value=c['id'],default=bool(self.card and self.card['id']==c['id'])) for c in self.dados['cartoes']],row=0)
            async def escolher(i):
                await i.response.defer()
                try:self.card=await self.pedir('cartao',sel.values[0]);await self.exibir(i)
                except FalhaCarteira as exc:await self.falhou(i,exc)
            sel.callback=escolher;self.add_item(sel)
        for delta,chave in ((-1,'anterior'),(1,'proxima')):
            if self.single:continue
            b=discord.ui.Button(label=txt(chave,lang),disabled=self.pagina==0 if delta<0 else not self.dados['proximo'],row=1)
            async def mover(i,delta=delta):
                await i.response.defer()
                try:
                    dest=self.pagina+delta
                    cursor=self.cursores[dest] if dest<len(self.cursores) else self.dados['proximo']
                    d=await self.pedir('listar',dono=self.dono,depois=cursor)
                    if dest==len(self.cursores):self.cursores.append(cursor)
                    self.pagina=dest;self.dados=d;self.card=d['cartoes'][0] if d['cartoes'] else None
                    await self.exibir(i)
                except FalhaCarteira as exc:await self.falhou(i,exc)
            b.callback=mover;self.add_item(b)
        if not self.card:return
        capacidades=self.card.get('capacidades',{})
        for chave,acao in (('detalhes','detalhes'),('analisar','analisar')):
            if not capacidades.get('ver_detalhes' if chave=='detalhes' else 'analisar'):continue
            b=discord.ui.Button(label=txt(chave,lang),row=2)
            async def privado(i,acao=acao):
                await i.response.defer(ephemeral=True,thinking=True)
                await self.cog.consulta_privada(i,self.card['id'],acao)
            b.callback=privado;self.add_item(b)
        if capacidades.get('ver_detalhes'):
            b=discord.ui.Button(label=txt('atualizar',lang),row=2)
            async def atualizar(i):
                await i.response.defer()
                try:self.card=await self.pedir('cartao',self.card['id']);await self.exibir(i)
                except FalhaCarteira as exc:await self.falhou(i,exc)
            b.callback=atualizar;self.add_item(b)
        if capacidades.get('personalizar'):
            b=discord.ui.Button(label=txt('editar',lang),row=3)
            async def editar(i):
                await i.response.defer(ephemeral=True,thinking=True);await self.cog.editar_privado(i,self.card['id'])
            b.callback=editar;self.add_item(b)
            b=discord.ui.Button(label=txt('imagem',lang),row=3)
            async def imagem(i):await i.response.send_message(txt('foto_ajuda',self.lang()),ephemeral=True)
            b.callback=imagem;self.add_item(b)
        if capacidades.get('trocar_arquivo'):
            b=discord.ui.Button(label=txt('trocar',lang),row=3)
            async def trocar(i):await self.cog.iniciar(i,'troca',self.card['id'])
            b.callback=trocar;self.add_item(b)
    async def conteudo(self):
        if not self.card:return {'content':txt('vazio',self.lang()),'embeds':[],'attachments':[]}
        e=cartao_embed(self.card,self.lang());arquivos=[]
        if self.card['perfil'].get('imagem_id'):
            try:
                dados=await self.pedir('imagem',self.card['id']);arquivos=[discord.File(io.BytesIO(dados),filename='cartao.webp')];e.set_image(url='attachment://cartao.webp')
            except FalhaCarteira:pass # cartão textual continua legível
        return {'content':None,'embeds':[e],'attachments':arquivos}
    async def exibir(self,i):
        # Recarrega a lista e a projeção para não republicar um campo ocultado
        # enquanto o menu estava aberto. Nenhuma planilha é lida aqui.
        if self.single:
            self.card=await self.pedir('cartao_salvo',self.card['id'])
        else:self.dados=await self.pedir('listar',dono=self.dono,depois=self.cursores[self.pagina])
        if self.card and not self.single:
            atual=next((c for c in self.dados['cartoes'] if c['id']==self.card['id']),None)
            self.card=atual or (self.dados['cartoes'][0] if self.dados['cartoes'] else None)
        if not self.single:self.cog.lembrar_nomes(self.servidor,self.usuario,self.dono,self.dados)
        self.montar();kw=await self.conteudo()
        self.mensagem=await i.edit_original_response(**kw,view=self,allowed_mentions=discord.AllowedMentions.none())


class PreviaView(Controles):
    def __init__(self,cog,s,u,pid,previa):
        super().__init__(cog,s,u,privado=True);self.pid=pid;self.previa=previa
        for chave in ('salvar','cancelar'):
            b=discord.ui.Button(label=txt(chave,self.lang()),style=discord.ButtonStyle.success if chave=='salvar' else discord.ButtonStyle.secondary)
            async def agir(i,chave=chave):
                await i.response.defer(ephemeral=True)
                try:
                    await self.pedir('confirmar' if chave=='salvar' else 'cancelar',self.pid,previa=self.previa['previa'])
                    self.stop();await i.edit_original_response(content=txt('salvo' if chave=='salvar' else 'cancelado',self.lang()),embeds=[],attachments=[],view=None,allowed_mentions=discord.AllowedMentions.none())
                except FalhaCarteira as exc:
                    await i.edit_original_response(content=erro(exc,self.lang()),embeds=[],attachments=[],view=None)
            b.callback=agir;self.add_item(b)
    async def conteudo(self):
        e=cartao_embed(self.previa['cartao'],self.lang());arquivos=[]
        e.set_author(name=txt('preview',self.lang()))
        if self.previa['cartao']['perfil'].get('imagem_id'):
            try:
                b=await self.pedir('imagem',self.pid,previa=self.previa['previa']);arquivos=[discord.File(io.BytesIO(b),filename='cartao.webp')];e.set_image(url='attachment://cartao.webp')
            except FalhaCarteira:pass
        return e,arquivos


class EditarModal(discord.ui.Modal):
    def __init__(self,cog,s,u,pid,atual):
        self.cog,self.s,self.u,self.pid,self.atual=cog,s,u,pid,atual
        lang=cog.idioma_guild(s);super().__init__(title=txt('formulario',lang),timeout=600)
        p=atual['perfil']
        self.titulo=discord.ui.TextInput(label=txt('titulo',lang),required=False,max_length=200,default=p.get('titulo',''))
        self.frase=discord.ui.TextInput(label=txt('frase',lang),required=False,max_length=500,style=discord.TextStyle.paragraph,default=p.get('frase',''))
        self.cor=discord.ui.TextInput(label=txt('cor',lang),required=False,max_length=7,default=f"#{p['cor']:06X}" if 'cor' in p else '')
        nomes={'idade':('idade','age'),'cla':('clã','clan'),'origem':('origem','origin'),'caminho':('caminho','path'),'imagem_id':('imagem','image')}
        visiveis=', '.join(nomes[x][lang=='en'] for x in nomes if x in atual['campos_publicos'])
        self.extras=discord.ui.TextInput(label=txt('extras',lang),placeholder=txt('exemplos',lang),required=False,max_length=100,default=visiveis)
        for x in (self.titulo,self.frase,self.cor,self.extras):self.add_item(x)
    async def on_submit(self,i):
        lang=self.cog.idioma_guild(self.s)
        if str(i.user.id)!=str(self.u) or str(i.guild_id)!=str(self.s):
            await i.response.send_message(txt('somente',lang),ephemeral=True);return
        await i.response.defer(ephemeral=True,thinking=True)
        try:
            cor=self.cor.value.strip()
            if cor and not re.fullmatch('#?[0-9a-fA-F]{6}',cor):raise FalhaCarteira('solicitacao')
            mapa={'idade':'idade','age':'idade','clã':'cla','cla':'cla','clan':'cla','origem':'origem','origin':'origem','caminho':'caminho','path':'caminho','imagem':'imagem_id','image':'imagem_id'}
            extras={x.strip().lower() for x in self.extras.value.split(',') if x.strip()}
            if extras-set(mapa):raise FalhaCarteira('solicitacao')
            d=await self.cog.api.pedir(self.s,self.u,'preparar',personagem=self.pid,
                alteracoes={'titulo':self.titulo.value or None,'frase':self.frase.value or None,'cor':int(cor.lstrip('#'),16) if cor else None},
                campos_publicos=sorted({'nome','titulo','frase','cor'}|{mapa[x] for x in extras}),base_esperada=self.atual['base'])
            await self.cog.mostrar_previa(i,self.pid,d)
        except FalhaCarteira as exc:await i.followup.send(erro(exc,lang),ephemeral=True)


class AbrirEditor(Controles):
    def __init__(self,cog,s,u,pid,atual):
        super().__init__(cog,s,u,privado=True)
        b=discord.ui.Button(label=txt('abrir_formulario',self.lang()))
        async def abrir(i):
            # Só reabre os valores já recebidos pelo dono. Submissão e salvar
            # consultam novamente membro/capacidade e a revisão da prévia.
            await i.response.send_modal(EditarModal(cog,s,u,pid,atual))
        b.callback=abrir;self.add_item(b)


def paginas_privadas(bundle,lang,analisar):
    if analisar:
        from closure_bot.ficha_leitor import Campo
        from closure_bot.ficha_corretor import Problema,Resultado
        from closure_bot.cogs.ficha import paginas
        from closure_bot.idiomas import usar
        r=bundle['analise']['resultado']
        args={k:v for k,v in r.items() if k not in ('problemas','pendencias','notas')}
        for k in ('problemas','pendencias','notas'):
            args[k]=[Problema(**p) for p in r[k]]
        # O apresentador também decodifica JSON dos cartões. Escapar esse JSON
        # antes de decodificar alteraria os dados; menções são neutralizadas no
        # texto final e nomes simples recebem escape de Markdown.
        ficha={k:Campo(v['valor'],v['celula'],v['parte']) for k,v in bundle['leitura']['campos']['ficha'].items()}
        with usar(lang):ps=paginas(Resultado(**args),ficha,SimpleNamespace(chave='closure',nome='Guias do Ciclo',avatar_url=None))
        for p in ps:
            p.title=seguro(p.title or '',256)
            for indice,campo in enumerate(p.fields):
                p.set_field_at(indice,name=discord.utils.escape_mentions(campo.name),value=discord.utils.escape_mentions(campo.value),inline=campo.inline)
            p.set_footer(text=(p.footer.text or '')[:1700]+' · '+txt('privado',lang))
        a=bundle['analise'];ps[0].add_field(name=txt('fonte',lang),value=f"<t:{int(a['origem']['lido_em'])}:f> · {txt('revisao',lang)} {a['origem']['revisao']} · {seguro(a['campanha']['nome'],100)}",inline=False)
        return ps
    e=cartao_embed(bundle['cartao'],lang);e.set_footer(text=txt('privado',lang))
    f=bundle['leitura']['campos']['ficha']
    for k,pt,en in (('nivel','Nível','Level'),('vida_max','Vida máxima','Max HP'),('energia_max','Energia máxima','Max energy'),('integridade_max','Integridade máxima','Max Integrity'),('defesa','Defesa','Defence'),('protecao','Proteção','Protection')):
        c=f.get(k)
        if c and c['valor']!='':e.add_field(name=en if lang=='en' else pt,value=seguro(c['valor'],100),inline=True)
    return [e]


class ConsultaView(Controles):
    def __init__(self,cog,s,u,pid,*,analise=False):
        super().__init__(cog,s,u,privado=True);self.pid,self.analise,self.pagina=pid,analise,0
    async def montar(self,bundle):
        self.clear_items();ps=paginas_privadas(bundle,self.lang(),self.analise)
        for delta,chave in ((-1,'anterior'),(1,'proxima')):
            b=discord.ui.Button(label=txt(chave,self.lang()),disabled=self.pagina==0 if delta<0 else self.pagina>=len(ps)-1)
            async def mover(i,delta=delta):
                await i.response.defer(ephemeral=True)
                try:
                    d=await self.pedir('analise_salva' if self.analise else 'detalhes',self.pid)
                    self.pagina=max(0,self.pagina+delta);emb=await self.montar(d)
                    await i.edit_original_response(embed=emb,view=self,allowed_mentions=discord.AllowedMentions.none())
                except FalhaCarteira as exc:
                    self.stop();await i.edit_original_response(content=erro(exc,self.lang()),embeds=[],view=None)
            b.callback=mover;self.add_item(b)
        self.add_item(discord.ui.Button(label=txt('ficha',self.lang()),url='https://docs.google.com/spreadsheets/d/'+bundle['arquivo']+'/edit'))
        return ps[min(self.pagina,len(ps)-1)]
