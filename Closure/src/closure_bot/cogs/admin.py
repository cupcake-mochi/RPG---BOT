"""Comandos do bot e preferências administrativas do servidor."""
from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import discord
from discord import app_commands
from discord.ext import commands

from ..dados import resumo_manifesto
from ..idiomas import atual, tr, catalogo
from ..conteudo_adulto import motivo_inativo
from ..plantao import FUSO, de_plantao
from ..prompt import versoes as versoes_do_site
from ..ficha_paginacao import PaginasFicha
from ..atalhos import CURTOS, OUTROS_NOMES


COR = 0xCC0102
# Título de cada grupo no /ajuda, pelo módulo que tem o comando. A lista sai dos próprios comandos, então não envelhece.
GRUPOS = {"Guias": "Guias de uso", "Regras": "Regras", "Ficha": "Ficha", "ComandoClima": "Clima", "Pessoa": "Seus dados", "Admin": "Do bot"}
SO_DO_DONO = {"teste_webhook"}
SO_DA_GERENCIA = {"idioma", "language", "lnt", "cargo_admin"}


def _campos_grupo(embed, grupo, linhas):
    partes=[]
    for linha in linhas:
        if partes and len(partes[-1])+len(linha)+1 <= 1024:
            partes[-1]+="\n"+linha
        else:
            partes.append(linha)
    for i,parte in enumerate(partes):
        nome="» "+grupo+(" · continued" if atual()=="en" else " · continuação")*(i>0)
        embed.add_field(name=nome,value=parte,inline=False)


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def painel_de_ajuda(self, *, cuida_do_servidor: bool, dono: bool, configura_mundo: bool = False) -> discord.Embed:
        if atual() == "en":
            return self._ajuda_ingles(cuida_do_servidor=cuida_do_servidor,dono=dono,configura_mundo=configura_mundo)
        agora = datetime.now(FUSO)
        embed = discord.Embed(title="Guias do Ciclo", color=COR, description=(
            "**» Como falar com elas**\n"
            "Nos canais onde o bot atende, chame pelo nome: `kal, o que é Integridade?` ou `closure, tá chovendo aí?`. "
            "Em outro canal, mencione o bot diretamente, se você puder usá-lo ali. "
            "Responder a uma mensagem delas também vale, e logo depois de ela responder você pode continuar sem chamar de novo.\n"
            "A Kal'tsit atende das 9h às 21h e a Closure das 21h às 9h, no horário de Brasília. "
            f"Agora quem atende é a {self.bot.personas[de_plantao(agora)].nome}."))
        grupos: dict[str, list[str]] = {}
        for comando in sorted(self.bot.tree.get_commands(), key=lambda c: c.name):
            do_servidor = getattr(comando, "default_permissions", None) is not None or comando.name in SO_DA_GERENCIA
            delegado = configura_mundo and comando.name in {"idioma", "language", "lnt"}
            if (do_servidor and not (cuida_do_servidor or delegado)) or (comando.name in SO_DO_DONO and not dono):
                continue
            # grupo de comandos (/ficha analisar): cada subcomando numa linha, com a menção clicável dele
            itens = list(comando.commands) if isinstance(comando, app_commands.Group) else [comando]
            for item in itens:
                nome = comando.name if item is comando else f"{comando.name} {item.name}"
                mencao = self.bot.mencoes.get(comando.name, "/" + comando.name)
                if item is not comando:
                    mencao = mencao.replace(f"</{comando.name}:", f"</{nome}:") if mencao.startswith("</") else "/" + nome
                grupo = "Para quem cuida do servidor" if do_servidor or comando.name in SO_DO_DONO else \
                    GRUPOS.get(type(getattr(item, "binding", None)).__name__, "Outros")
                grupos.setdefault(grupo, []).append(f"{mencao} · {item.description}")
        ordem = [*GRUPOS.values(), "Outros", "Para quem cuida do servidor"]
        for grupo in sorted(grupos, key=ordem.index):
            _campos_grupo(embed,grupo,grupos[grupo])
        embed.add_field(name="» Sem a barra", inline=False,
                        value="`GC:guia criar` ensina a montar a ficha; `GC:guia planilha` explica abas e configurações.\n"
                              "`GC:guia ficha` explica a análise; `GC:guia` abre todos os assuntos.\n"
                              "`GC:ajuda`, `GC:livro`, `GC:ficha` (com o link ou o .xlsx anexo), `GC:clima` (ou `GC:clima Quioto`), "
                              "`GC:ping` e `GC:status` fazem o mesmo, escritos no chat.\n"
                              "Escolha **Abreviações** no menu abaixo para ver só os atalhos.")
        links = [f"[{nome}]({url})" for nome, url in (("Privacidade", self.bot.config.politica_url), ("Termos de uso", self.bot.config.termos_url)) if url]
        if links:
            embed.add_field(name="» Links", value=" | ".join(links), inline=False)
        if self.bot.user and self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Página 1 de 2 · Comandos disponíveis · Bot de fã, sem ligação oficial com nenhum jogo")
        return embed

    def _ajuda_ingles(self, *, cuida_do_servidor, dono, configura_mundo=False):
        agora = datetime.now(FUSO)
        e = discord.Embed(title="Guides of the Cycle",color=COR,description=(
            "**» Talk to the guides**\n"
            "In channels where the bot listens, call a guide by name: `kal, how does Integridade work?` or "
            "`closure, what is the weather in Tokyo?`. In another channel, mention the bot directly if you can use it there. "
            "You can also reply to a guide's message or continue shortly after her reply without repeating the name.\n"
            "Kal'tsit covers 09:00–21:00 and Closure 21:00–09:00, Brasília time. "
            f"Currently on duty: {self.bot.personas[de_plantao(agora)].nome}."))
        grupos = {}
        nomes = {"Guias":"Usage guides","Regras":"Rulebook","Ficha":"Character sheets","ComandoClima":"Weather","Pessoa":"Your data","Admin":"Bot information"}
        for comando in sorted(self.bot.tree.get_commands(),key=lambda c:c.name):
            admin = getattr(comando,"default_permissions",None) is not None or comando.name in SO_DA_GERENCIA
            delegado = configura_mundo and comando.name in {"idioma", "language", "lnt"}
            if (admin and not (cuida_do_servidor or delegado)) or (comando.name in SO_DO_DONO and not dono):
                continue
            for item in (list(comando.commands) if isinstance(comando,app_commands.Group) else [comando]):
                nome = comando.name if item is comando else f"{comando.name} {item.name}"
                mencao = self.bot.mencoes.get(comando.name,"/"+comando.name)
                if item is not comando:
                    mencao = mencao.replace(f"</{comando.name}:",f"</{nome}:") if mencao.startswith("</") else "/"+nome
                grupo = "Server administration" if admin or comando.name in SO_DO_DONO else nomes.get(type(getattr(item,"binding",None)).__name__,"Other commands")
                grupos.setdefault(grupo,[]).append(f"{mencao} · {tr(item.description,'en')}")
        for grupo,linhas in grupos.items():
            _campos_grupo(e,grupo,linhas)
        e.add_field(name="» Type commands in chat",inline=False,value=(
            "`GC:guide create` walks through character creation; `GC:guide spreadsheet` explains tabs and settings.\n"
            "`GC:guide sheet` explains analysis; `GC:guide gm` covers the GM review. `GC:guide` opens all topics.\n"
            "`GC:help`, `GC:book`, `GC:sheet LINK` (or attach XLSX), `GC:weather CITY`, `GC:ping` and `GC:status` also work in chat.\n"
            "Choose **Abbreviations** below for short names. Native slash-menu names follow your Discord client's language; "
            "Portuguese commands and English prefix aliases remain accepted."))
        links=[f"[{nome}]({url})" for nome,url in (("Privacy",self.bot.config.politica_url),("Terms of use",self.bot.config.termos_url)) if url]
        if links:e.add_field(name="» Links",value=" | ".join(links),inline=False)
        if self.bot.user and self.bot.user.display_avatar:e.set_thumbnail(url=self.bot.user.display_avatar.url)
        e.set_footer(text="Page 1 of 2 · Available commands · Fan-made bot; not affiliated with any game")
        return e

    def painel_abreviacoes(self, servidor: int | None) -> discord.Embed:
        if atual() == "en":
            e = discord.Embed(title="Abbreviations",color=COR,description=(
                "Short forms of the same commands. **Full names still work.**\n\n"+
                "\n".join(f"`GC:{n}` → `GC:{d}`" for n,d in CURTOS.items())+
                "\n\nArguments still apply: `GC:f SHEET_LINK`, `GC:c BH` or `GC:g gm`. Attach XLSX to the same `GC:f` message."))
            e.add_field(name="Other accepted names",value="\n".join(f"`GC:{n}` → `GC:{d}`" for n,d in OUTROS_NOMES.items()),inline=False)
            extras=self.bot.registro.atalhos_servidor(servidor) if servidor else {}
            linhas=[f"`GC:{n}` → `GC:{d}`" for n,d in extras.items()]
            for i in range(0,len(linhas),10):
                e.add_field(name="Server shortcuts" if i==0 else "Server shortcuts · continued",value="\n".join(linhas[i:i+10]),inline=False)
            if not extras:e.add_field(name="Server shortcuts",value="None configured." if servidor else "Open help in a server to see its shortcuts.",inline=False)
            e.add_field(name="Configure a shortcut",inline=False,value=(
                "With **Manage Server**, use `/atalho definir` to choose a name and allowed destination. "
                "Example: name `review`, destination **Guia: Revisar uma ficha como mestre**. Then `GC:review` opens that guide. "
                "`/atalho remover` removes one; `/atalho listar` lists them. Up to 20 per server; reserved commands and shortcuts cannot be replaced.\n"
                "This is a snapshot. Reopen help after changing a shortcut."))
            e.set_footer(text="Page 2 of 2 · Abbreviations · GC:help abbreviations opens this page directly")
            return e
        e = discord.Embed(title="Abreviações", color=COR, description=(
            "São formas curtas dos mesmos comandos. **Os nomes completos continuam funcionando.**\n\n"
            + "\n".join(f"`GC:{nome}` → `GC:{alvo}`" for nome, alvo in CURTOS.items())
            + "\n\nO que você escreve depois continua valendo: `GC:f LINK_DA_FICHA`, `GC:c BH` ou `GC:g mestre`. "
            "O XLSX também pode ser anexado à mensagem de `GC:f`."))
        e.add_field(name="Outros nomes aceitos", value="\n".join(f"`GC:{n}` → `GC:{d}`" for n, d in OUTROS_NOMES.items()), inline=False)
        extras = self.bot.registro.atalhos_servidor(servidor) if servidor else {}
        linhas = [f"`GC:{n}` → `GC:{d}`" for n, d in extras.items()]
        for i in range(0, len(linhas), 10):
            e.add_field(name="Atalhos deste servidor" if i == 0 else "Atalhos deste servidor · continuação",
                        value="\n".join(linhas[i:i+10]), inline=False)
        if not extras:
            e.add_field(name="Atalhos deste servidor", value="Nenhum cadastrado." if servidor else "Abra a ajuda dentro de um servidor para consultar seus atalhos.", inline=False)
        e.add_field(name="Criar um atalho para o servidor", value=(
            "Quem tem **Gerenciar servidor** usa `/atalho definir`, escolhe um nome e o destino. "
            "Exemplo: nome `revisar`, destino **Guia: Revisar uma ficha como mestre**. "
            "Depois, `GC:revisar` abre esse guia. `/atalho remover` retira; `/atalho listar` consulta. "
            "Até 20 por servidor; comandos e atalhos padrão não podem ser substituídos.\n"
            "Esta lista é uma foto do momento. Reabra `/ajuda` depois de mudar um atalho."), inline=False)
        e.set_footer(text="Página 2 de 2 · Abreviações · GC:ajuda abreviações abre esta página diretamente")
        return e

    async def enviar_ajuda(self, enviar, *, usuario, servidor: int | None, permissoes=None, abreviacoes=False):
        dono = usuario.id == self.bot.config.dono_id
        permissoes = permissoes if permissoes is not None else getattr(usuario, "guild_permissions", None)
        from ..servidor import autorizado, administrador
        pode = bool(servidor and autorizado(usuario, self.bot.registro.opcoes_servidor(servidor), permissoes))
        paginas = [self.painel_de_ajuda(cuida_do_servidor=dono or administrador(usuario, permissoes), dono=dono, configura_mundo=pode),
                   self.painel_abreviacoes(servidor)]
        v = PaginasFicha(paginas, aviso_encerrado=tr('Abra /ajuda ou GC:ajuda novamente para continuar'))
        if abreviacoes:
            v.indice = 1
            v._atualizar()
        v.mensagem = await enviar(embed=paginas[v.indice], view=v)

    @app_commands.command(name="ajuda", description="Como falar com as guias e a lista de comandos.")
    @app_commands.choices(pagina=[app_commands.Choice(name="Comandos disponíveis", value="comandos"),
                                app_commands.Choice(name="Abreviações", value="abreviacoes")])
    async def ajuda(self, interacao: discord.Interaction, pagina: str = "comandos") -> None:
        async def enviar(**extras):
            await interacao.response.send_message(**extras, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())
            return await interacao.original_response()
        await self.enviar_ajuda(enviar, usuario=interacao.user, servidor=interacao.guild_id,
                               permissoes=interacao.permissions, abreviacoes=pagina == "abreviacoes")

    def texto_ping(self) -> str:
        return tr('No ar ({0} ms). Regras: {1}.').format(round(self.bot.latency * 1000), resumo_manifesto(self.bot.manifesto))

    async def texto_status(self, servidor: int | None = None) -> str:
        agora = datetime.now(FUSO)
        plantao = self.bot.personas[de_plantao(agora)]
        try:  # o que vale é o que está na página de onde sai o prompt; os card.json da pasta podem estar atrás
            cards = ", ".join(f"{nome} {versao}" for nome, versao in (await versoes_do_site()).items())
        except Exception as erro:
            cards = tr('não deu pra ler a página ({0})').format(str(erro)[:80])
        contagens = self.bot.registro.contagens()
        configuracao = ""
        if servidor:
            opcoes = self.bot.registro.opcoes_servidor(servidor)
            mundo = "Nova Terra" if opcoes.nova_terra else "Arknights"
            configuracao = tr("Neste servidor: idioma {0}; mundo {1}.\n").format(opcoes.idioma, mundo)
        return configuracao + (tr('Agora ({0:%H:%M}, Brasília) o plantão é de {1}.\nPrompt: {2}.\nRegistro: {3} gatilhos, {4} chamadas de API, {5} mensagens enviadas.\nOrçamento usado no mês: US$ {6:.2f} de US$ {7:.2f} (preço {8}, com reservas por consumo incerto').format(agora, plantao.nome, cards, contagens['gatilhos'], contagens['chamadas_api'], contagens['mensagens_bot'], self.bot.modelos.gasto_do_mes(), self.bot.modelos.teto_usd, self.bot.modelos.teto_preco)
                + (tr(' e US$ {0:.2f} gastos fora do bot').format(self.bot.modelos.gasto_externo_usd) if self.bot.modelos.gasto_externo_usd else "")
                + tr('; pelo preço promocional, US$ {0:.2f} do bot).').format(self.bot.modelos.gasto_do_mes(preco='promocional', externo=False)))

    @app_commands.command(name="ping", description="Confere se o bot está no ar e qual versão das regras ele leu.")
    async def ping(self, interacao: discord.Interaction) -> None:
        await interacao.response.send_message(self.texto_ping(), ephemeral=True)

    @app_commands.command(name="status", description="Quem está de plantão, versões dos cards e contagens do registro.")
    async def status(self, interacao: discord.Interaction) -> None:
        await interacao.response.send_message(await self.texto_status(interacao.guild_id), ephemeral=True)

    async def _administrador(self, interacao: discord.Interaction) -> bool:
        if not interacao.guild_id:
            await interacao.response.send_message(tr('Use este comando dentro de um servidor.'), ephemeral=True)
            return False
        permissoes = interacao.permissions
        if not (permissoes.manage_guild or permissoes.administrator):
            await interacao.response.send_message(tr('É preciso ter a permissão Gerenciar servidor.'), ephemeral=True)
            return False
        return True

    def _status_nsfw(self, guild_id: int, canal) -> str:
        p = self.bot.registro.preferencias_servidor(guild_id)
        motivo = motivo_inativo(SimpleNamespace(guild=SimpleNamespace(id=guild_id), channel=canal), self.bot.registro)
        local = {
            None: '**Neste canal: ativo.**',
            'desativado': '**Neste canal: inativo — a opção está desligada no servidor.**',
            'sem_marcacao': '**Neste canal: inativo — falta marcar o canal como NSFW no Discord.**',
            'outro_canal': '**Neste canal: inativo — este canal não é o escolhido em /nsfw_canal.**',
        }.get(motivo, '**Neste canal: não foi possível conferir o canal atual.**')
        local = tr(local)
        estado = tr('ativadas') if p.responder_nsfw else tr('desativadas')
        onde = (tr('somente em <#{0}> e seus tópicos').format(p.canal_nsfw_id) if p.canal_nsfw_id is not None
                else tr('em todos os canais marcados como NSFW onde o bot já atende'))
        return (tr('{0}\n\nRespostas adultas não gráficas **{1}** neste servidor; {2}. O canal precisa estar marcado como NSFW no Discord. Permite reação e opinião, sem ERP ou encenação sexual; os bloqueios do Google continuam.').format(local, estado, onde))

    @app_commands.command(name="responder_nsfw", description="Ativa ou desativa reações adultas não gráficas neste servidor.")
    @app_commands.describe(ativar="Sim para ativar, Não para desativar. Em branco, consulta a configuração.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def responder_nsfw(self, interacao: discord.Interaction, ativar: bool | None = None) -> None:
        if not await self._administrador(interacao):
            return
        if ativar is not None:
            self.bot.registro.definir_responder_nsfw(interacao.guild_id, ativar)
        await interacao.response.send_message(self._status_nsfw(interacao.guild_id, interacao.channel), ephemeral=True)

    @app_commands.command(name="nsfw_canal", description="Limita as reações adultas a um canal ou remove essa restrição.")
    @app_commands.describe(canal="Canal de texto marcado como NSFW; inclui seus tópicos.",
                           todos="Sim para remover a restrição de canal. Sem opções, consulta a configuração.")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def nsfw_canal(self, interacao: discord.Interaction, canal: discord.TextChannel | None = None,
                         todos: bool = False) -> None:
        if not await self._administrador(interacao):
            return
        if canal is not None and todos:
            await interacao.response.send_message(tr('Escolha um canal ou `todos:Sim`, sem combinar os dois.'), ephemeral=True)
            return
        if canal is not None:
            if not isinstance(canal, discord.TextChannel) or canal.guild.id != interacao.guild_id:
                await interacao.response.send_message(tr('Escolha um canal de texto deste servidor.'), ephemeral=True)
                return
            if not canal.is_nsfw():
                await interacao.response.send_message(tr('Marque o canal como NSFW nas configurações do Discord antes de escolhê-lo.'), ephemeral=True)
                return
            self.bot.registro.definir_canal_nsfw(interacao.guild_id, canal.id)
        elif todos:
            self.bot.registro.definir_canal_nsfw(interacao.guild_id, None)
        await interacao.response.send_message(self._status_nsfw(interacao.guild_id, interacao.channel), ephemeral=True)

    @app_commands.command(name="teste_webhook", description="Manda uma mensagem de teste com o nome e o avatar de quem está de plantão.")
    async def teste_webhook(self, interacao: discord.Interaction) -> None:
        if interacao.user.id != self.bot.config.dono_id:
            await interacao.response.send_message(tr('Esse comando é só do dono do bot.'), ephemeral=True)
            return
        persona = self.bot.personas[de_plantao(datetime.now(FUSO))]
        await interacao.response.defer(ephemeral=True)
        await self.bot.carteiro.enviar(interacao.channel, persona, "[teste de webhook]", lembrar=False)
        await interacao.followup.send(tr('Enviado como {0}.').format(persona.nome), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
