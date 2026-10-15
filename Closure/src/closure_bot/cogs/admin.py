"""Comandos do bot e preferências administrativas do servidor."""
from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import discord
from discord import app_commands
from discord.ext import commands

from ..dados import resumo_manifesto
from ..conteudo_adulto import motivo_inativo
from ..plantao import FUSO, de_plantao
from ..prompt import versoes as versoes_do_site


COR = 0xCC0102
# Título de cada grupo no /ajuda, pelo módulo que tem o comando. A lista sai dos próprios comandos, então não envelhece.
GRUPOS = {"Regras": "Regras", "Ficha": "Ficha", "ComandoClima": "Clima", "Pessoa": "Seus dados", "Admin": "Do bot"}
SO_DO_DONO = {"teste_webhook"}


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def painel_de_ajuda(self, *, cuida_do_servidor: bool, dono: bool) -> discord.Embed:
        agora = datetime.now(FUSO)
        canais = " ou ".join(f"<#{c}>" for c in sorted(self.bot.config.canais))
        onde = f"em {canais}" if canais else "no canal"
        embed = discord.Embed(title="Guias do Ciclo", color=COR, description=(
            "**» Como falar com elas**\n"
            f"Chame pelo nome {onde}, como `kal, o que é Integridade?` ou `closure, tá chovendo aí?`. "
            "Responder a uma mensagem delas também vale, e logo depois de ela responder você pode continuar sem chamar de novo.\n"
            "A Kal'tsit atende das 9h às 21h e a Closure das 21h às 9h, no horário de Brasília. "
            f"Agora quem atende é a {self.bot.personas[de_plantao(agora)].nome}."))
        grupos: dict[str, list[str]] = {}
        for comando in sorted(self.bot.tree.get_commands(), key=lambda c: c.name):
            do_servidor = getattr(comando, "default_permissions", None) is not None
            if (do_servidor and not cuida_do_servidor) or (comando.name in SO_DO_DONO and not dono):
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
            embed.add_field(name=f"» {grupo}", value="\n".join(grupos[grupo]), inline=False)
        embed.add_field(name="» Sem a barra", inline=False,
                        value="`GC:ajuda`, `GC:livro`, `GC:ficha` (com o link ou o .xlsx anexo), `GC:clima` (ou `GC:clima Quioto`), "
                              "`GC:ping` e `GC:status` fazem o mesmo, escritos no chat.")
        links = [f"[{nome}]({url})" for nome, url in (("Privacidade", self.bot.config.politica_url), ("Termos de uso", self.bot.config.termos_url)) if url]
        if links:
            embed.add_field(name="» Links", value=" | ".join(links), inline=False)
        if self.bot.user and self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Bot de fã, sem ligação oficial com nenhum jogo")
        return embed

    @app_commands.command(name="ajuda", description="Como falar com as guias e a lista de comandos.")
    async def ajuda(self, interacao: discord.Interaction) -> None:
        permissoes = getattr(interacao, "permissions", None)
        dono = interacao.user.id == self.bot.config.dono_id
        await interacao.response.send_message(
            embed=self.painel_de_ajuda(cuida_do_servidor=dono or bool(permissoes and permissoes.manage_guild), dono=dono), ephemeral=True)

    def texto_ping(self) -> str:
        return f"No ar ({round(self.bot.latency * 1000)} ms). Regras: {resumo_manifesto(self.bot.manifesto)}."

    async def texto_status(self) -> str:
        agora = datetime.now(FUSO)
        plantao = self.bot.personas[de_plantao(agora)]
        try:  # o que vale é o que está na página de onde sai o prompt; os card.json da pasta podem estar atrás
            cards = ", ".join(f"{nome} {versao}" for nome, versao in (await versoes_do_site()).items())
        except Exception as erro:
            cards = f"não deu pra ler a página ({str(erro)[:80]})"
        contagens = self.bot.registro.contagens()
        return (f"Agora ({agora:%H:%M}, Brasília) o plantão é de {plantao.nome}.\n"
                f"Prompt: {cards}.\n"
                f"Registro: {contagens['gatilhos']} gatilhos, {contagens['chamadas_api']} chamadas de API, "
                f"{contagens['mensagens_bot']} mensagens enviadas.\n"
                f"Orçamento usado no mês: US$ {self.bot.modelos.gasto_do_mes():.2f} de US$ {self.bot.modelos.teto_usd:.2f} "
                f"(preço {self.bot.modelos.teto_preco}, com reservas por consumo incerto"
                + (f" e US$ {self.bot.modelos.gasto_externo_usd:.2f} gastos fora do bot" if self.bot.modelos.gasto_externo_usd else "")
                + f"; pelo preço promocional, US$ {self.bot.modelos.gasto_do_mes(preco='promocional', externo=False):.2f} do bot).")

    @app_commands.command(name="ping", description="Confere se o bot está no ar e qual versão das regras ele leu.")
    async def ping(self, interacao: discord.Interaction) -> None:
        await interacao.response.send_message(self.texto_ping(), ephemeral=True)

    @app_commands.command(name="status", description="Quem está de plantão, versões dos cards e contagens do registro.")
    async def status(self, interacao: discord.Interaction) -> None:
        await interacao.response.send_message(await self.texto_status(), ephemeral=True)

    async def _administrador(self, interacao: discord.Interaction) -> bool:
        if not interacao.guild_id:
            await interacao.response.send_message("Use este comando dentro de um servidor.", ephemeral=True)
            return False
        permissoes = interacao.permissions
        if not (permissoes.manage_guild or permissoes.administrator):
            await interacao.response.send_message("É preciso ter a permissão Gerenciar servidor.", ephemeral=True)
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
        estado = "ativadas" if p.responder_nsfw else "desativadas"
        onde = (f"somente em <#{p.canal_nsfw_id}> e seus tópicos" if p.canal_nsfw_id is not None
                else "em todos os canais marcados como NSFW onde o bot já atende")
        return (f"{local}\n\nRespostas adultas não gráficas **{estado}** neste servidor; {onde}. "
                "O canal precisa estar marcado como NSFW no Discord. "
                "Permite reação e opinião, sem ERP ou encenação sexual; os bloqueios do Google continuam.")

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
            await interacao.response.send_message("Escolha um canal ou `todos:Sim`, sem combinar os dois.", ephemeral=True)
            return
        if canal is not None:
            if not isinstance(canal, discord.TextChannel) or canal.guild.id != interacao.guild_id:
                await interacao.response.send_message("Escolha um canal de texto deste servidor.", ephemeral=True)
                return
            if not canal.is_nsfw():
                await interacao.response.send_message("Marque o canal como NSFW nas configurações do Discord antes de escolhê-lo.", ephemeral=True)
                return
            self.bot.registro.definir_canal_nsfw(interacao.guild_id, canal.id)
        elif todos:
            self.bot.registro.definir_canal_nsfw(interacao.guild_id, None)
        await interacao.response.send_message(self._status_nsfw(interacao.guild_id, interacao.channel), ephemeral=True)

    @app_commands.command(name="teste_webhook", description="Manda uma mensagem de teste com o nome e o avatar de quem está de plantão.")
    async def teste_webhook(self, interacao: discord.Interaction) -> None:
        if interacao.user.id != self.bot.config.dono_id:
            await interacao.response.send_message("Esse comando é só do dono do bot.", ephemeral=True)
            return
        persona = self.bot.personas[de_plantao(datetime.now(FUSO))]
        await interacao.response.defer(ephemeral=True)
        await self.bot.carteiro.enviar(interacao.channel, persona, "[teste de webhook]", lembrar=False)
        await interacao.followup.send(f"Enviado como {persona.nome}.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
