"""Cliente interno da ponte; não encaminha credenciais para mensagens."""
import json
import re
from urllib.parse import urlsplit
import aiohttp


class FalhaCarteira(Exception):
    def __init__(self,codigo='temporario'): self.codigo=codigo


def origem_valida(origem,desenvolvimento=False):
    u=urlsplit(origem)
    if (u.scheme!='https' and not (desenvolvimento and u.scheme=='http' and u.hostname in ('127.0.0.1','localhost','::1'))) or not u.hostname or u.path not in ('','/') or u.query or u.fragment or u.username or u.password:
        raise ValueError('Configure uma origem HTTPS; piloto HTTP só em loopback explícito.')
    return origem.rstrip('/')


class ClienteCarteira:
    def __init__(self,origem,token,*,desenvolvimento=False):
        self.origem=origem_valida(origem,desenvolvimento);self.token=token
        if len(token)<32:raise ValueError('Segredo de serviço ausente.')

    async def pedir(self,s,u,acao,*,personagem=None,imagem=None,**dados):
        globais={'listar','cargo_revisor','modelos','configurar_modelo','criar_por_modelo'}
        locais={'cartao','cartao_salvo','detalhes','analisar','analise_salva','editar','preparar','confirmar','cancelar','imagem','enviar_imagem'}
        if personagem is None and acao not in globais: raise FalhaCarteira('solicitacao')
        if personagem is not None and (acao not in locais or not re.fullmatch('[a-f0-9]{32}',personagem)): raise FalhaCarteira('solicitacao')
        path='/interno/galeria' if acao=='listar' else '/interno/galeria/acao/'+acao if personagem is None else '/interno/galeria/'+personagem+'/'+acao
        headers={'Authorization':'Bearer '+self.token}
        kwargs={'json':{'servidor':str(s),'usuario':str(u),**dados}}
        if imagem is not None:
            if acao!='enviar_imagem' or not 0<len(imagem)<=1024*1024: raise FalhaCarteira('tamanho')
            headers|={'X-Carteira-Servidor':str(s),'X-Carteira-Usuario':str(u),'Content-Type':'application/octet-stream'}
            kwargs={'data':imagem}
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as client:
                async with client.post(self.origem+path,allow_redirects=False,headers=headers,**kwargs) as resp:
                    b=bytearray()
                    async for bloco in resp.content.iter_chunked(65536):
                        b.extend(bloco)
                        if len(b)>8*1024*1024:raise FalhaCarteira('tamanho')
                    if resp.status!=200:
                        codigo={403:'acesso',404:'acesso',409:'conflito',413:'tamanho',422:'leitura',429:'limite'}.get(resp.status,'temporario')
                        try:
                            reportado=json.loads(b).get('erro')
                            if reportado in {'solicitacao','imagem','armazenamento','limite','leitura','conflito','acesso'}:codigo=reportado
                        except (ValueError,AttributeError):pass
                        raise FalhaCarteira(codigo)
                    if acao=='imagem':
                        if resp.content_type!='image/webp' or len(b)>1024*1024:raise FalhaCarteira('tamanho')
                        return bytes(b)
                    if resp.content_type!='application/json':raise FalhaCarteira()
                    obj=json.loads(b)
                    if not isinstance(obj,dict):raise FalhaCarteira()
                    return obj
        except (aiohttp.ClientError,TimeoutError,ValueError):raise FalhaCarteira() from None
