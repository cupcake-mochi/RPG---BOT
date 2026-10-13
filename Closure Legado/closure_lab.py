import os
import discord
from discord.ext import commands, tasks
import google.genai as genai
import aiohttp
import aiosqlite
import io
import openpyxl
import datetime
import unicodedata
import re  

def padronizar_busca(texto):
    """Remove acentos e deixa tudo minúsculo para a busca não falhar."""
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# ==========================================
# 1. BANCO DE DADOS E MAPEAMENTO
# ==========================================

MAPA_PERICIAS = {
    "atletismo": 11, "acrobacia": 12, "furtividade": 13, "prestidigitação": 14,
    "intuição": 15, "medicina": 16, "percepção": 17, "ocultismo": 18,
    "direção": 19, "sobrevivência": 20, "história": 21, "feitiçaria": 22,
    "investigação": 23, "teologia": 24, "tecnologia": 25, "persuasão": 26,
    "enganação": 27, "intimidação": 28, "performance": 29,
    "fortitude": 31, "integridade": 32, "vontade": 33, "astúcia": 34, "reflexos": 35,
    "oficio - alfaiate": 37, "oficio - alquimia": 38, "oficio - ferreiro": 39,
    "oficio - canalizador": 40, "oficio - cozinheiro": 41, "oficio - entalhador": 42,
    "oficio - fármaco": 43
}

HABILIDADES_DB = {
    # TALENTOS GERAIS
    "afinidade com técnica": {}, "artesão amaldiçoado": {}, "ataque infalível": {},
    "atenção infalível": {}, "dedicação recompensadora": {}, "favorecido pela sorte": {},
    "guarda infalível": {}, "incremento de atributo": {}, "investida aprimorada": {},
    "mestre das armas": {}, "mestre defensivo": {}, "perceber oportunidade": {},
    "provocação desafiadora": {}, "resiliência melhorada": {}, "saltador constante": {},
    "técnicas agressivas de escudo": {}, "técnicas de arremesso": {}, "técnicas de reação rápida": {},
    "técnicas defensivas de escudo": {}, "tempestade de ideias": {},
    "adepto de medicina": {"requer_mestre": "medicina", "limite_adepto": True},
    "adepto de briga": {"requer_mestre": "atletismo", "limite_adepto": True},
    "adepto de combate": {"requer_mestre": "intuição", "limite_adepto": True},
    "adepto de feitiçaria": {"requer_mestre": "feitiçaria", "limite_adepto": True},
    "alma inquebrável": {"constituicao": 14},
    "apaziguador de técnica": {"nivel": 8, "requer_treino": "astúcia"},
    "aptidão desenvolvida": {"nivel": 4},
    "determinado a viver": {"requer_treino": "vontade", "constituicao": 16},
    "discurso motivador": {"requer_pericia_presenca": True},
    "especialista em concussão": {"nivel": 8},
    "especialista em cortes": {"nivel": 8},
    "especialista em perfuração": {"nivel": 8},
    "mestre da criação": {"nivel": 4, "requer_qtd_oficios": 2},
    "mestre do arremesso": {"nivel": 8, "requer_hab": "técnicas de arremesso"},
    "mestre dos chicotes": {"nivel": 5},
    "movimentos acrobáticos": {"requer_treino": "acrobacia"},
    "robustez aprimorada": {"constituicao": 14},
    "técnicas de empunhadura dupla": {"requer_atributo_ou": {"forca": 14, "destreza": 14}},
    "técnicas de mobilidade": {"destreza": 14},
    "técnicas de ocultamento": {"requer_treino": "furtividade"},
    "técnicas do sentinela": {"nivel": 5},
    "wrestling": {"nivel": 4},
    "voto malevolente": {"nivel": 12},

    # TALENTOS DE ORIGEM
    "familiaridade com técnica": {"nivel": 12, "origem": "inato"},
    "manual de técnica": {"nivel": 5, "origem": "herdado", "requer_treino_ou": ["história", "ocultismo"]},
    "expansão de reserva": {"nivel": 8, "origem": "derivado"},
    "quebra de limites": {"nivel": 6, "origem": "derivado"},
    "físico aperfeiçoado": {"nivel": 6, "origem": "feto amaldiçoado híbrido"},
    "reposição sanguínea": {"nivel": 6, "origem": "feto amaldiçoado híbrido"},
    "estudo amaldiçoado": {"nivel": 8, "origem": "sem técnica"},
    "noção e preparação": {"nivel": 4, "origem": "sem técnica"},

    # HABILIDADES COMPARTILHADAS ENTRE CLASSES
    "assassinar": {"classe": ["especialista em combate", "restringido"], "nivel": 10, "requer_mestre": "furtividade"},
    "técnicas de combate": {"classe": ["especialista em técnica", "controlador", "suporte"], "nivel": 2},
    "ataque extra": {"classe": ["especialista em combate", "lutador"], "nivel": 6},
    "ação ágil": {"classe": ["restringido", "lutador"], "nivel": 4},

    # LUTADOR
    # Nv 2 (Corrigido)
    "aparar ataque": {"classe": "lutador", "nivel": 2},
    "aparar projéteis": {"classe": "lutador", "nivel": 2},
    "ataque inconsequente": {"classe": "lutador", "nivel": 2},
    "caminho da mão vazia": {"classe": "lutador", "nivel": 2},
    "complementação marcial": {"classe": "lutador", "nivel": 2},
    "deboche desconcertante": {"classe": "lutador", "nivel": 2, "requer_treino": "intimidação"},
    "dedicação em arma": {"classe": "lutador", "nivel": 2},
    "esquiva rápida": {"classe": "lutador", "nivel": 2},
    "finta melhorada": {"classe": "lutador", "nivel": 2},
    "mãos amaldiçoadas": {"classe": "lutador", "nivel": 2},
    "kiai intimidador": {"classe": "lutador", "nivel": 2},
    "impacto misto": {"classe": "lutador", "nivel": 2},
    "puxar um ar": {"classe": "lutador", "nivel": 2},
    "quebrando tudo": {"classe": "lutador", "nivel": 2},
    "resistir": {"classe": "lutador", "nivel": 2},
    # Nv 4 (Corrigido)
    "ação ágil": {"classe": "lutador", "nivel": 4},
    "acrobata": {"classe": "lutador", "nivel": 4},
    "atacar e recuar": {"classe": "lutador", "nivel": 4, "requer_hab": "esquiva rápida"},
    "brutalidade": {"classe": "lutador", "nivel": 4},
    "defesa marcial": {"classe": "lutador", "nivel": 4, "requer_hab": "complementação marcial"},
    "devolver projéteis": {"classe": "lutador", "nivel": 4, "requer_hab": "aparar projéteis"},
    "fluxo": {"classe": "lutador", "nivel": 4},
    "músculos desenvolvidos": {"classe": "lutador", "nivel": 4},
    "fúria da vingança": {"classe": "lutador", "nivel": 4},
    "sobrevivente": {"classe": "lutador", "nivel": 4},
    "voadora": {"classe": "lutador", "nivel": 4},
    "segura pra mim": {"classe": "lutador", "nivel": 4},
    "redirecionar força": {"classe": "lutador", "nivel": 4},
    "imprudência motivadora": {"classe": "lutador", "nivel": 4},
    # Nv 6 (Corrigido)
    "aprimoramento marcial": {"classe": "lutador", "nivel": 6},
    "brutalidade sanguinária": {"classe": "lutador", "nivel": 6, "requer_hab": "brutalidade"},
    "corpo calejado": {"classe": "lutador", "nivel": 6},
    "eliminar e continuar": {"classe": "lutador", "nivel": 6},
    "foguete sem ré": {"classe": "lutador", "nivel": 6},
    "golpe da mão aberta": {"classe": "lutador", "nivel": 6},
    "ignorar dor": {"classe": "lutador", "nivel": 6},
    "manobras finalizadoras": {"classe": "lutador", "nivel": 6},
    "poder corporal": {"classe": "lutador", "nivel": 6, "requer_hab": "caminho da mão vazia"},
    "potência superior": {"classe": "lutador", "nivel": 6, "requer_hab": "complementação marcial"},
    "sequência inconsequente": {"classe": "lutador", "nivel": 6, "requer_hab": "ataque inconsequente"},
    "um com a arma": {"classe": "lutador", "nivel": 6, "requer_hab": "dedicação em arma"},
    # Nv 8 a 16
    "aptidões de luta": {"classe": "lutador", "nivel": 8},
    "ataques ressonantes": {"classe": "lutador", "nivel": 8},
    "brutalidade aprimorada": {"classe": "lutador", "nivel": 8, "requer_hab": "brutalidade"},
    "feitiço e punho": {"classe": "lutador", "nivel": 8, "requer_hab": "mãos amaldiçoadas"},
    "golpear brecha": {"classe": "lutador", "nivel": 8, "requer_hab": "aparar ataque"},
    "oportunista": {"classe": "lutador", "nivel": 8},
    "pancada desnorteante": {"classe": "lutador", "nivel": 8},
    "punhos letais": {"classe": "lutador", "nivel": 8, "requer_hab": "poder corporal"},
    "alma quieta": {"classe": "lutador", "nivel": 10, "requer_treino": "vontade"},
    "corpo sincronizado": {"classe": "lutador", "nivel": 10, "requer_treino": "fortitude"},
    "empolgar-se": {"classe": "lutador", "nivel": 10},
    "impacto demolidor": {"classe": "lutador", "nivel": 10, "requer_hab": "potência superior"},
    "insistência": {"classe": "lutador", "nivel": 10, "requer_hab": "ignorar dor"},
    "mente em paz": {"classe": "lutador", "nivel": 10, "requer_treino": "astúcia"},
    "armas absolutas": {"classe": "lutador", "nivel": 12, "requer_hab": "um com a arma"},
    "corpo arsenal": {"classe": "lutador", "nivel": 12, "requer_hab": "punhos letais"},
    "seja água": {"classe": "lutador", "nivel": 12},
    "tempestade sufocante": {"classe": "lutador", "nivel": 12},
    "corpo supremo": {"classe": "lutador", "nivel": 16},
    "duro na queda": {"classe": "lutador", "nivel": 16, "requer_treino": "vontade"},

    # ESPECIALISTA EM COMBATE
    "arremessos potentes": {"classe": "especialista em combate", "nivel": 2},
    "arsenal cíclico": {"classe": "especialista em combate", "nivel": 2},
    "assumir postura": {"classe": "especialista em combate", "nivel": 2},
    "disparos sincronizados": {"classe": "especialista em combate", "nivel": 2},
    "escudeiro agressivo": {"classe": "especialista em combate", "nivel": 2},
    "extensão do corpo": {"classe": "especialista em combate", "nivel": 2},
    "flanqueador superior": {"classe": "especialista em combate", "nivel": 2},
    "golpe falso": {"classe": "especialista em combate", "nivel": 2},
    "golpes potentes": {"classe": "especialista em combate", "nivel": 2},
    "indomável": {"classe": "especialista em combate", "nivel": 2},
    "pistoleiro iniciado": {"classe": "especialista em combate", "nivel": 2},
    "posicionamento ameaçador": {"classe": "especialista em combate", "nivel": 2},
    "precisão definitiva": {"classe": "especialista em combate", "nivel": 2},
    "presença suprimida": {"classe": "especialista em combate", "nivel": 2},
    "revigorar": {"classe": "especialista em combate", "nivel": 2},
    "tiro falso": {"classe": "especialista em combate", "nivel": 2},
    "zona de risco": {"classe": "especialista em combate", "nivel": 2},
    "aprender postura": {"classe": "especialista em combate", "nivel": 4, "requer_hab": "assumir postura"},
    "armas escolhidas": {"classe": "especialista em combate", "nivel": 4},
    "arremesso rápido": {"classe": "especialista em combate", "nivel": 4},
    "técnicas de avanço": {"classe": "especialista em combate", "nivel": 4},
    "buscar oportunidade": {"classe": "especialista em combate", "nivel": 4},
    "compensar erro": {"classe": "especialista em combate", "nivel": 4},
    "especialista em escudo": {"classe": "especialista em combate", "nivel": 4},
    "espírito de luta": {"classe": "especialista em combate", "nivel": 4},
    "grupo favorito": {"classe": "especialista em combate", "nivel": 4},
    "guarda estudada": {"classe": "especialista em combate", "nivel": 4},
    "mente oculta": {"classe": "especialista em combate", "nivel": 4},
    "preparo imediato": {"classe": "especialista em combate", "nivel": 4},
    "recarga rápida": {"classe": "especialista em combate", "nivel": 4},
    "uso rápido": {"classe": "especialista em combate", "nivel": 4},
    "acervo amplo": {"classe": "especialista em combate", "nivel": 6},
    "aprimoramento especializado": {"classe": "especialista em combate", "nivel": 6},
    "crítico melhorado": {"classe": "especialista em combate", "nivel": 6},
    "crítico potente": {"classe": "especialista em combate", "nivel": 6},
    "feitiçaria implementada": {"classe": "especialista em combate", "nivel": 6, "requer_treino": "feitiçaria"},
    "fluxo perfeito": {"classe": "especialista em combate", "nivel": 6},
    "olhos de águia": {"classe": "especialista em combate", "nivel": 6},
    "manejo especial": {"classe": "especialista em combate", "nivel": 6},
    "marcar inimigo": {"classe": "especialista em combate", "nivel": 6},
    "mira destrutiva": {"classe": "especialista em combate", "nivel": 6, "requer_treino": "percepção"},
    "preparação rápida": {"classe": "especialista em combate", "nivel": 6, "requer_hab": "assumir postura"},
    "aptidões de combate": {"classe": "especialista em combate", "nivel": 8},
    "técnicas da força": {"classe": "especialista em combate", "nivel": 8},
    "destruição dupla": {"classe": "especialista em combate", "nivel": 8},
    "espírito incansável": {"classe": "especialista em combate", "nivel": 8, "requer_hab": "espírito de luta"},
    "pistoleiro avançado": {"classe": "especialista em combate", "nivel": 8, "requer_hab": "pistoleiro iniciado"},
    "ricochete constante": {"classe": "especialista em combate", "nivel": 8},
    "sombra viva": {"classe": "especialista em combate", "nivel": 8, "requer_treino": "furtividade"},
    "surto de ação": {"classe": "especialista em combate", "nivel": 8},
    "análise acelerada": {"classe": "especialista em combate", "nivel": 10},
    "armas perfeitas": {"classe": "especialista em combate", "nivel": 10, "requer_hab": "armas escolhidas"},
    "ataque concentrado": {"classe": "especialista em combate", "nivel": 10, "requer_hab": "ataque extra"},
    "chuva de arremessos": {"classe": "especialista em combate", "nivel": 10, "requer_hab": "arremessos potentes"},
    "potência antes de cair": {"classe": "especialista em combate", "nivel": 10},
    "técnicas de saque": {"classe": "especialista em combate", "nivel": 12},
    "ciclagem absoluta": {"classe": "especialista em combate", "nivel": 12, "requer_hab": "arsenal cíclico"},
    "manejo único": {"classe": "especialista em combate", "nivel": 12, "requer_hab": "manejo especial"},
    "mestre pistoleiro": {"classe": "especialista em combate", "nivel": 12, "requer_hab": "pistoleiro avançado"},
    "sincronia perfeita": {"classe": "especialista em combate", "nivel": 12, "requer_hab": "extensão do corpo"},
    "crítico aperfeiçoado": {"classe": "especialista em combate", "nivel": 16, "requer_hab": "crítico melhorado"},
    "mestre da postura": {"classe": "especialista em combate", "nivel": 16, "requer_hab": "assumir postura"},

    # ESPECIALISTA EM TÉCNICA
    "abastecido pelo sangue": {"classe": "especialista em técnica", "nivel": 2},
    "conhecimento aplicado": {"classe": "especialista em técnica", "nivel": 2},
    "conjuração defensiva": {"classe": "especialista em técnica", "nivel": 2},
    "economia de energia": {"classe": "especialista em técnica", "nivel": 2},
    "explosão encadeada": {"classe": "especialista em técnica", "nivel": 2},
    "finta amaldiçoada": {"classe": "especialista em técnica", "nivel": 2},
    "mente plácida": {"classe": "especialista em técnica", "nivel": 2},
    "nova habilidade": {"classe": "especialista em técnica", "nivel": 2},
    "perturbação amaldiçoada": {"classe": "especialista em técnica", "nivel": 2},
    "reação rápida": {"classe": "especialista em técnica", "nivel": 2},
    "reforço amaldiçoado": {"classe": "especialista em técnica", "nivel": 2},
    "sobrecarregar": {"classe": "especialista em técnica", "nivel": 2},
    "zelo recompensador": {"classe": "especialista em técnica", "nivel": 2},
    "até a última gota": {"classe": "especialista em técnica", "nivel": 4},
    "ciclagem maldita": {"classe": "especialista em técnica", "nivel": 4},
    "determinação energizada": {"classe": "especialista em técnica", "nivel": 4},
    "energia focalizada": {"classe": "especialista em técnica", "nivel": 4},
    "energia inacabável": {"classe": "especialista em técnica", "nivel": 4},
    "epifania amaldiçoada": {"classe": "especialista em técnica", "nivel": 4},
    "explosão defensiva": {"classe": "especialista em técnica", "nivel": 4, "requer_aptidao": "cobrir-se"},
    "feitiço favorito": {"classe": "especialista em técnica", "nivel": 4},
    "feitiços refinados": {"classe": "especialista em técnica", "nivel": 4},
    "movimentos imprevisíveis": {"classe": "especialista em técnica", "nivel": 4},
    "naturalidade com rituais": {"classe": "especialista em técnica", "nivel": 4, "requer_treino": "prestidigitação"},
    "preparação de técnicas": {"classe": "especialista em técnica", "nivel": 4},
    "olhar preciso": {"classe": "especialista em técnica", "nivel": 4},
    "sacrifício pela energia": {"classe": "especialista em técnica", "nivel": 4},
    "versatilidade em fundamentos": {"classe": "especialista em técnica", "nivel": 4},
    "bastião interior": {"classe": "especialista em técnica", "nivel": 6, "requer_treino": "vontade"},
    "combate amaldiçoado": {"classe": "especialista em técnica", "nivel": 6, "requer_hab": "técnicas de combate"},
    "correção": {"classe": "especialista em técnica", "nivel": 6},
    "dominância em feitiço": {"classe": "especialista em técnica", "nivel": 6},
    "elevar aptidão": {"classe": "especialista em técnica", "nivel": 6},
    "especialização": {"classe": "especialista em técnica", "nivel": 6},
    "incapaz de falhar": {"classe": "especialista em técnica", "nivel": 6},
    "mente repartida": {"classe": "especialista em técnica", "nivel": 6},
    "nível perfeito": {"classe": "especialista em técnica", "nivel": 6},
    "passo rápido": {"classe": "especialista em técnica", "nivel": 6},
    "potência concentrada": {"classe": "especialista em técnica", "nivel": 6},
    "ritualista": {"classe": "especialista em técnica", "nivel": 6},
    "expansão dos fundamentos": {"classe": "especialista em técnica", "nivel": 8},
    "físico amaldiçoado defensivo": {"classe": "especialista em técnica", "nivel": 8, "requer_aptidao": "cobrir-se"},
    "imbuir com técnica": {"classe": "especialista em técnica", "nivel": 8, "requer_hab": "combate amaldiçoado"},
    "liberações expandidas": {"classe": "especialista em técnica", "nivel": 8},
    "mira aperfeiçoada": {"classe": "especialista em técnica", "nivel": 8, "requer_hab": "olhar preciso"},
    "primeiro disparo": {"classe": "especialista em técnica", "nivel": 8, "requer_treino": "reflexos"},
    "revestimento constante": {"classe": "especialista em técnica", "nivel": 8, "requer_aptidao": "cobrir-se"},
    "sustentação avançada": {"nivel": 8},
    "destruição ampla": {"classe": "especialista em técnica", "nivel": 10},
    "destruição focada": {"classe": "especialista em técnica", "nivel": 10},
    "economia de energia avançada": {"classe": "especialista em técnica", "nivel": 10, "requer_hab": "economia de energia"},
    "sentidos aguçados": {"classe": "especialista em técnica", "nivel": 10, "requer_mestre": "percepção"},
    "esgrimista jujutsu": {"classe": "especialista em técnica", "nivel": 12, "requer_hab": "combate amaldiçoado"},
    "expansão maestral": {"classe": "especialista em técnica", "nivel": 12, "requer_aptidao": "expansão de domínio completa"},
    "explosão máxima": {"classe": "especialista em técnica", "nivel": 12, "requer_hab": "explosão encadeada"},
    "mestre das aptidões": {"classe": "especialista em técnica", "nivel": 12},
    "versatilidade ampliada": {"classe": "especialista em técnica", "nivel": 12},
    # Nv 16 (Corrigido)
    "manipulação perfeita": {"classe": "especialista em técnica", "nivel": 16, "requer_hab": "dominância em feitiço"},
    "sustentação mestre": {"nivel": 16, "requer_hab": "sustentação avançada"},

    # CONTROLADOR
    "aceleração": {"classe": "controlador", "nivel": 2},
    "camuflagem aprimorada": {"classe": "controlador", "nivel": 2},
    "chamado destruidor": {"classe": "controlador", "nivel": 2},
    "companheiro amaldiçoado": {"classe": "controlador", "nivel": 2},
    "dor partilhada": {"classe": "controlador", "nivel": 2},
    "frenesi da invocação": {"classe": "controlador", "nivel": 2},
    "guarda viva": {"classe": "controlador", "nivel": 2},
    "invocações móveis": {"classe": "controlador", "nivel": 2},
    "invocações resistentes": {"classe": "controlador", "nivel": 2},
    "invocações treinadas": {"classe": "controlador", "nivel": 2},
    "melhoria de controlador": {"classe": "controlador", "nivel": 2},
    "otimização de energia": {"classe": "controlador", "nivel": 2},
    "proteger invocação": {"classe": "controlador", "nivel": 2},
    "rede de detecção": {"classe": "controlador", "nivel": 2},
    "visionário": {"classe": "controlador", "nivel": 2},
    "ação corretiva": {"classe": "controlador", "nivel": 4},
    "acompanhamento amaldiçoado": {"classe": "controlador", "nivel": 4},
    "ataque em conjunto": {"classe": "controlador", "nivel": 4},
    "autonomia": {"classe": "controlador", "nivel": 4},
    "companheiro avançado": {"classe": "controlador", "nivel": 4, "requer_hab": "companheiro amaldiçoado"},
    "crítico brutal": {"classe": "controlador", "nivel": 4},
    "domador de maldições": {"classe": "controlador", "nivel": 4},
    "invocação às": {"classe": "controlador", "nivel": 4, "requer_hab": "companheiro amaldiçoado"},
    "invocação parcial": {"classe": "controlador", "nivel": 4},
    "potencial superior": {"classe": "controlador", "nivel": 4},
    "combate em alcateia": {"classe": "controlador", "nivel": 6, "requer_hab": "técnicas de combate"},
    "concentrar poder": {"classe": "controlador", "nivel": 6, "requer_aptidao": "apogeu - controle concentrado"},
    "hoste amaldiçoada": {"classe": "controlador", "nivel": 6, "requer_aptidao": "apogeu - controle disperso"},
    "invocações econômicas": {"classe": "controlador", "nivel": 6},
    "proteção avançada de invocação": {"classe": "controlador", "nivel": 6, "requer_hab": "proteger invocação"},
    "táticas de alcateia": {"classe": "controlador", "nivel": 6},
    "aptidões de controle": {"classe": "controlador", "nivel": 8},
    "atacar e invocar": {"classe": "controlador", "nivel": 8},
    "golpes ágeis": {"classe": "controlador", "nivel": 8, "requer_hab": "acompanhamento amaldiçoado"},
    "técnicas de oportunidade": {"classe": "controlador", "nivel": 8},
    "buchas de canhão": {"classe": "controlador", "nivel": 10},
    "crítico aprimorado": {"classe": "controlador", "nivel": 10, "requer_hab": "crítico brutal"},
    "flanco avançado": {"classe": "controlador", "nivel": 10, "requer_hab": "táticas de alcateia"},
    "resistência sobrecarregada": {"classe": "controlador", "nivel": 10, "requer_hab": "invocações resistentes"},
    "fantoche supremo": {"classe": "controlador", "nivel": 16},
    "mestre do controle": {"classe": "controlador", "nivel": 16},

    # SUPORTE
    "amizade inquebrável": {"classe": "suporte", "nivel": 2},
    "análise profunda": {"classe": "suporte", "nivel": 2},
    "apoio avançado": {"classe": "suporte", "nivel": 2},
    "conceder outra chance": {"classe": "suporte", "nivel": 2},
    "comando motivador": {"classe": "suporte", "nivel": 2},
    "desvendar terreno": {"classe": "suporte", "nivel": 2},
    "expandir repertório": {"classe": "suporte", "nivel": 2},
    "mobilidade avançada": {"classe": "suporte", "nivel": 2},
    "otimização de espaço": {"classe": "suporte", "nivel": 2},
    "pronto para agir": {"classe": "suporte", "nivel": 2},
    "protetor": {"classe": "suporte", "nivel": 2},
    "transmitir conhecimento": {"classe": "suporte", "nivel": 2},
    "apoios versáteis": {"classe": "suporte", "nivel": 4},
    "guarda sincronizada": {"classe": "suporte", "nivel": 4},
    "inspirar aliados": {"classe": "suporte", "nivel": 4},
    "intervenção": {"classe": "suporte", "nivel": 4},
    "negação crítica": {"classe": "suporte", "nivel": 4},
    "no último segundo": {"classe": "suporte", "nivel": 4},
    "pré-análise": {"classe": "suporte", "nivel": 4, "requer_treino": "percepção"},
    "recompensa pelo sucesso": {"classe": "suporte", "nivel": 4, "requer_hab": "comando motivador"},
    "sintonização vital": {"classe": "suporte", "nivel": 4},
    "cura avançada em grupo": {"classe": "suporte", "nivel": 6},
    "devolver na mesma moeda": {"classe": "suporte", "nivel": 6},
    "disseminar cura": {"classe": "suporte", "nivel": 6},
    "incitar vigor": {"classe": "suporte", "nivel": 6},
    "inimigo comum": {"classe": "suporte", "nivel": 6},
    "posicionamento estratégico": {"classe": "suporte", "nivel": 6},
    "aptidões de suporte": {"classe": "suporte", "nivel": 8},
    "contaminar com determinação": {"classe": "suporte", "nivel": 8},
    "criar medicina": {"classe": "suporte", "nivel": 8, "requer_treino": "oficio - fármaco"},
    "cura aperfeiçoada": {"classe": "suporte", "nivel": 8},
    "elevar sucesso": {"classe": "suporte", "nivel": 8},
    "físico controlado": {"classe": "suporte", "nivel": 8, "requer_treino": "fortitude"},
    "motivação pelo triunfo": {"classe": "suporte", "nivel": 8},
    "pressão do médico": {"classe": "suporte", "nivel": 8, "requer_mestre": "medicina"},
    "descarga reanimadora": {"classe": "suporte", "nivel": 10, "requer_aptidao": "cura amplificada"},
    "necessidade de continuar": {"classe": "suporte", "nivel": 10, "requer_treino": "vontade"},
    "olhar aguçado": {"classe": "suporte", "nivel": 10, "requer_treino": "percepção"},
    "táticas defensivas": {"classe": "suporte", "nivel": 10},
    "ajustes em equipamento": {"classe": "suporte", "nivel": 12, "requer_treino": "oficio - ferreiro"},
    "interferência": {"classe": "suporte", "nivel": 12},
    "não desista!": {"classe": "suporte", "nivel": 12},
    "sobrecura": {"classe": "suporte", "nivel": 12},
    "reação necessária": {"classe": "suporte", "nivel": 12},
    "apoio abrangente": {"classe": "suporte", "nivel": 14, "requer_hab": "apoio avançado"},
    "purificação da alma": {"classe": "suporte", "nivel": 16},

    # RESTRINGIDO
    "apropriar-se": {"classe": "restringido", "nivel": 2},
    "aproximação instintiva": {"classe": "restringido", "nivel": 2},
    "existência imperceptível": {"classe": "restringido", "nivel": 2},
    "golpe impactante": {"classe": "restringido", "nivel": 2},
    "imitação": {"classe": "restringido", "nivel": 2},
    "manejo superior": {"classe": "restringido", "nivel": 2},
    "roubo de habilidade": {"classe": "restringido", "nivel": 2},
    "surto de adrenalina": {"classe": "restringido", "nivel": 2},
    "valorizar invocação": {"classe": "restringido", "nivel": 2},
    "adrenalina intensificadora": {"classe": "restringido", "nivel": 4},
    "caçador de feiticeiros": {"classe": "restringido", "nivel": 4},
    "desenvolver ideias": {"classe": "restringido", "nivel": 4},
    "foco no inimigo": {"classe": "restringido", "nivel": 4},
    "ponto cego": {"classe": "restringido", "nivel": 4},
    "resiliência pela adrenalina": {"classe": "restringido", "nivel": 4, "requer_hab": "surto de adrenalina"},
    "técnicas de memorização": {"classe": "restringido", "nivel": 4, "requer_hab": "imitação"},
    "aprimoramento celeste": {"classe": "restringido", "nivel": 6},
    "ataque inconsequente aprimorado": {"classe": "restringido", "nivel": 6, "requer_hab": "ataque inconsequente"},
    "corpo de aço": {"classe": "restringido", "nivel": 6},
    "corredor fantasma": {"classe": "restringido", "nivel": 6},
    "disparada trovejante": {"classe": "restringido", "nivel": 6},
    "frenesi": {"classe": "restringido", "nivel": 6, "requer_hab": "surto de adrenalina"},
    "movimento reativo": {"classe": "restringido", "nivel": 6},
    "ainda de pé": {"classe": "restringido", "nivel": 8},
    "arremetida encoberta": {"classe": "restringido", "nivel": 8},
    "barreira inamovível": {"classe": "restringido", "nivel": 8},
    "força imparável": {"classe": "restringido", "nivel": 8},
    "imitação perfeita": {"classe": "restringido", "nivel": 8, "requer_hab": "imitação"},
    "presença ameaçadora": {"classe": "restringido", "nivel": 8},
    "respeito celeste": {"classe": "restringido", "nivel": 8},
    "mente limpa": {"classe": "restringido", "nivel": 10},
    "perceber o ar": {"classe": "restringido", "nivel": 10},
    "precisão forçada": {"classe": "restringido", "nivel": 10},
    "retaliação": {"classe": "restringido", "nivel": 10},
    "adrenalina absoluta": {"classe": "restringido", "nivel": 12},
    "pináculo físico": {"classe": "restringido", "nivel": 12},
    "rejeitar a morte": {"classe": "restringido", "nivel": 12, "requer_hab": "ainda de pé"},
    "entre as sombras": {"classe": "restringido", "nivel": 16, "requer_hab": "arremetida encoberta"},
    "instintos aguçados": {"classe": "restringido", "nivel": 16, "requer_hab": "reação rápida"},
    "mesmo morto": {"classe": "restringido", "nivel": 16, "requer_hab": "rejeitar a morte"},
}

# ==========================================
# 2. FUNÇÕES AUXILIARES
# ==========================================

def pegar_celula(folha, coord):
    valor = folha[coord].value
    return "" if valor is None else str(valor).strip()

# ==========================================
# 3. MOTOR PRINCIPAL DE ANÁLISE
# ==========================================

def analisar_ficha(ficheiro_xlsx):
    try:
        wb = openpyxl.load_workbook(ficheiro_xlsx, data_only=True)
    except Exception as e:
        return f"❌ Erro ao ler a planilha: {e}"

    folhas_necessarias = ["Ficha de Feiticeiro", "Ficha Amaldiçoada", "Treinamentos"]
    for folha in folhas_necessarias:
        if folha not in wb.sheetnames:
            return f"❌ Erro: A aba '{folha}' não foi encontrada."

    feiticeiro = wb["Ficha de Feiticeiro"]
    amaldicoada = wb["Ficha Amaldiçoada"]
    treinamentos = wb["Treinamentos"]

    relatorio = []
    
    val_nivel = pegar_celula(feiticeiro, "K5")
    nivel = int(float(val_nivel)) if val_nivel else 1 # Isso é o NÍVEL TOTAL da ficha
    classe_principal = pegar_celula(feiticeiro, "T2").lower()
    origem_cla = pegar_celula(feiticeiro, "T5").lower()

    # --- LÓGICA DE MULTICLASSE ---
    niveis_classes = {
        "lutador": int(float(pegar_celula(feiticeiro, "L12") or 0)),
        "controlador": int(float(pegar_celula(feiticeiro, "L13") or 0)),
        "suporte": int(float(pegar_celula(feiticeiro, "L14") or 0)),
        "especialista em técnica": int(float(pegar_celula(feiticeiro, "L16") or 0)),
        "especialista em combate": int(float(pegar_celula(feiticeiro, "L17") or 0)),
        "restringido": 0
    }
    
    # Deduz o nível da classe principal baseado no nível total e nos níveis secundários
    total_multiclasse = sum(niveis_classes.values())
    niveis_classes[classe_principal] = max(1, nivel - total_multiclasse)
    
    # Lista com todas as classes que o personagem tem pelo menos 1 nível
    classes_possuidas = [c for c, n in niveis_classes.items() if n > 0]
    classe = classe_principal # Mantém a variável antiga rodando para os orçamentos primários

    # --- FILTRO DE ORIGENS IGNORADAS ---
    origens_ignoradas = ["sem técnica", "corpo amaldiçoado"]
    if any(ign in origem_cla for ign in origens_ignoradas):
        return f"⚠️ Análise manual necessária para a origem '{origem_cla.title()}'."

    # ==========================================
    # PRÉ-PROCESSADORES
    # ==========================================
    habilidades_escolhidas = []
    aptidoes_escolhidas = []
    
    for linha in range(6, 45, 2):
        hab = pegar_celula(feiticeiro, f"AD{linha}")
        if hab: habilidades_escolhidas.append(" ".join(hab.lower().split()))

    for col in ["X", "Y", "Z", "AA"]:
        for linha in range(9, 32):
            apt = pegar_celula(amaldicoada, f"{col}{linha}")
            if apt: aptidoes_escolhidas.append(" ".join(apt.lower().split()))
            
    for col in ["W", "X", "Y", "Z", "AA", "AB"]:
        for linha in range(38, 41):
            apt = pegar_celula(amaldicoada, f"{col}{linha}")
            if apt: aptidoes_escolhidas.append(" ".join(apt.lower().split()))

    # ==========================================
    # ANÁLISE DE ATRIBUTOS (ANTI-FRAUDE ATUALIZADO)
    # ==========================================
    pontos_gerais = 17
    
    # Bônus Iniciais de Point Buy (Bases)
    if "derivado" in origem_cla: pontos_gerais += 3
    elif "inato" in origem_cla or "feto" in origem_cla: pontos_gerais += 3
    elif "hb" in origem_cla or "homebrew" in origem_cla: pontos_gerais += 3 
    elif "herdado" in origem_cla and not any(cla in origem_cla for cla in ["gojo", "inumaki", "kamo"]): 
        pontos_gerais += 3

    # Carteira de PONTOS EXTRAS (Nível e Talentos que passam de 15)
    pontos_extras = (nivel // 4) * 2
    if pegar_celula(treinamentos, "AJ18").upper() == "TRUE": pontos_extras += 2
    pontos_extras += (habilidades_escolhidas.count("incremento de atributo") * 2)
    if "resiliência melhorada" in habilidades_escolhidas: pontos_extras += 1 
    if "quebra de limites" in habilidades_escolhidas: pontos_extras += 4 
    if "tempestade de ideias" in habilidades_escolhidas: pontos_extras += 1

    pontos_fisicos_extra = 0
    if "mestre das armas" in habilidades_escolhidas: pontos_fisicos_extra += 2
    if "mestre defensivo" in habilidades_escolhidas: pontos_fisicos_extra += 2
    if "especialista em perfuração" in habilidades_escolhidas: pontos_fisicos_extra += 1
    if "especialista em cortes" in habilidades_escolhidas: pontos_fisicos_extra += 1
    if "especialista em concussão" in habilidades_escolhidas: pontos_fisicos_extra += 1
    if "pináculo físico" in habilidades_escolhidas:
        pontos_fisicos_extra += 4 if nivel >= 16 else (2 if nivel >= 12 else 0)
    if "restringido" in origem_cla:
        pontos_fisicos_extra += 5 + ((nivel // 6) * 2)

    # Lendo Valores Finais Escritos na Ficha
    v_for = int(float(pegar_celula(feiticeiro, "F12") or 10))
    v_des = int(float(pegar_celula(feiticeiro, "F16") or 10))
    v_con = int(float(pegar_celula(feiticeiro, "F20") or 10))
    v_int = int(float(pegar_celula(feiticeiro, "F24") or 10))
    v_sab = int(float(pegar_celula(feiticeiro, "F28") or 10))
    v_pre = int(float(pegar_celula(feiticeiro, "F32") or 10))

    tabela_custo = {8: -2, 9: -1, 10: 0, 11: 2, 12: 3, 13: 4, 14: 5, 15: 7}

    def desmembrar(v):
        base = min(15, max(8, v))
        extra = max(0, v - 15)
        return tabela_custo.get(base, 0), extra

    pb_for, ex_for = desmembrar(v_for)
    pb_des, ex_des = desmembrar(v_des)
    pb_con, ex_con = desmembrar(v_con)
    pb_int, ex_int = desmembrar(v_int)
    pb_sab, ex_sab = desmembrar(v_sab)
    pb_pre, ex_pre = desmembrar(v_pre)

    custo_mental_pb = pb_int + pb_sab + pb_pre
    custo_fisico_pb = pb_for + pb_des + pb_con

    # Descontos de Clã (Gojo, Inumaki, Kamo)
    if "herdado" in origem_cla:
        if "gojo" in origem_cla: custo_mental_pb = max(0, custo_mental_pb - 3)
        elif "inumaki" in origem_cla: custo_mental_pb = max(0, custo_mental_pb - 3)
        elif "kamo" in origem_cla:
            abat_sab = min(3, max(0, pb_sab))
            pb_con_real = pb_con - min(3 - abat_sab, max(0, pb_con))
            custo_mental_pb = pb_int + (pb_sab - abat_sab) + pb_pre
            custo_fisico_pb = pb_for + pb_des + pb_con_real

    total_pb_gasto = custo_mental_pb + custo_fisico_pb
    total_ex_fisico = ex_for + ex_des + ex_con
    total_ex_mental = ex_int + ex_sab + ex_pre

    relatorio.append("--- ATRIBUTOS ---")
    
    # 1. Checa a Base (Point Buy)
    if total_pb_gasto > pontos_gerais:
        relatorio.append(f"❌ Base (Point Buy): Gastou {total_pb_gasto} de {pontos_gerais} iniciais permitidos.")
        
    # 2. Checa as Injeções Extras (Acima de 15)
    extras_gastos_totais = total_ex_fisico + total_ex_mental
    extras_permitidos_totais = pontos_extras + pontos_fisicos_extra

    if extras_gastos_totais > extras_permitidos_totais:
        relatorio.append(f"❌ Pontos Extras: Fraude Absurda! Injetou {extras_gastos_totais} pontos acima de 15, mas os níveis/talentos só concedem {extras_permitidos_totais} pontos.")
    elif total_ex_mental > pontos_extras:
        relatorio.append(f"❌ Pontos Mentais Extras: Tentou usar pontos físicos em atributos mentais. (Mentais injetados: {total_ex_mental}, Limite da carteira: {pontos_extras}).")
    
    if total_pb_gasto <= pontos_gerais and extras_gastos_totais <= extras_permitidos_totais and total_ex_mental <= pontos_extras:
        relatorio.append("✅ Atributos validados matematicamente.")

    # ==========================================
    # ANÁLISE DE PERÍCIAS, TRs E OFÍCIOS
    # ==========================================
    val_int_mod = pegar_celula(feiticeiro, "H24")
    val_sab_mod = pegar_celula(feiticeiro, "H28")
    mod_bonus = max(int(float(val_int_mod)) if val_int_mod else 0, int(float(val_sab_mod)) if val_sab_mod else 0)

    pts_pericias_permitidos = (5 if "suporte" in classe else 4) + mod_bonus
    pts_tr_permitidos = 2 if "restringido" in classe else 1
    pts_oficios_permitidos = 2 if any(c in classe for c in ["especialista em combate", "suporte", "especialista em técnica"]) else 1

    if "herdado" in origem_cla and any(c in origem_cla for c in ["gojo", "inumaki", "kamo", "zenin"]):
        pts_pericias_permitidos += 2
    if nivel >= 10: pts_pericias_permitidos += 1
    if nivel >= 9: pts_tr_permitidos += 2

    pts_tr_permitidos += habilidades_escolhidas.count("resiliência melhorada")
    if "artesão amaldiçoado" in habilidades_escolhidas: pts_oficios_permitidos += 1
    if "tempestade de ideias" in habilidades_escolhidas:
        pts_pericias_permitidos += 1
        pts_oficios_permitidos += 1
    if "alma inquebrável" in habilidades_escolhidas: pts_pericias_permitidos += 1

    erros_treino = []
    def contar_pts(linha_ini, linha_fim):
        total = 0
        for l in range(linha_ini, linha_fim + 1):
            treinado = str(pegar_celula(feiticeiro, f"U{l}")).upper() == "TRUE"
            especialista = str(pegar_celula(feiticeiro, f"V{l}")).upper() == "TRUE"
            
            if treinado: total += 1
            if especialista: total += 1
            if especialista and not treinado: total += 1
            
        return total

    relatorio.append("\n--- TREINAMENTOS ---")
    gastos_per = contar_pts(11, 29)
    gastos_tr = contar_pts(31, 35)
    gastos_of = contar_pts(37, 43)

    relatorio.append(f"{'✅' if gastos_per <= pts_pericias_permitidos else '❌'} Perícias: {gastos_per}/{pts_pericias_permitidos} gastos.")
    relatorio.append(f"{'✅' if gastos_tr <= pts_tr_permitidos else '❌'} Resistências: {gastos_tr}/{pts_tr_permitidos} gastos.")
    relatorio.append(f"{'✅' if gastos_of <= pts_oficios_permitidos else '❌'} Ofícios: {gastos_of}/{pts_oficios_permitidos} gastos.")
    
    if erros_treino:
        relatorio.extend(erros_treino)

    # ==========================================
    # ANÁLISE DE QUANTIDADES E APTIDÕES
    # ==========================================
    relatorio.append("\n--- QUANTIDADES E APTIDÕES ---")
    
    qtd_classes = len(classes_possuidas)
    hab_esperadas = 0
    for classe_nome, nivel_na_classe in niveis_classes.items():
        if nivel_na_classe > 0:
            hab_esperadas += (nivel_na_classe - 1)
            
    if "inato" in origem_cla: 
        hab_esperadas += 1
        
    hab_preenchidas = len(habilidades_escolhidas)
    relatorio.append(f"{'✅' if hab_preenchidas == hab_esperadas else '❌'} Habilidades: {hab_preenchidas}/{hab_esperadas} preenchidas.")

    if "restringido" in classe or "restringido" in origem_cla:
        if len(aptidoes_escolhidas) > 0 or float(pegar_celula(amaldicoada, "F9") or 0) > 0:
            relatorio.append(f"❌ Aptidões: Fraude ou Erro! Restringidos NÃO podem possuir aptidões (encontradas {len(aptidoes_escolhidas)}).")
        else:
            relatorio.append("✅ Aptidões: Personagem Restringido (Aptidões ignoradas corretamente).")
    else:
        aptidoes_esperadas = max(0, nivel - 1)
        if "derivado" in origem_cla: aptidoes_esperadas += 1
        if "epifania amaldiçoada" in habilidades_escolhidas: aptidoes_esperadas += 1

        val_max_apt = pegar_celula(amaldicoada, "D9")
        val_usadas_apt = pegar_celula(amaldicoada, "F9")
        max_aptidoes_planilha = int(float(val_max_apt)) if val_max_apt else 0
        aptidoes_usadas_planilha = int(float(val_usadas_apt)) if val_usadas_apt else 0
        
        if max_aptidoes_planilha == aptidoes_esperadas:
            relatorio.append(f"✅ Máximo de Aptidões: Exatos {max_aptidoes_planilha} disponíveis.")
        else:
            relatorio.append(f"❌ Máximo de Aptidões: Indica {max_aptidoes_planilha}, mas o cálculo exato seria {aptidoes_esperadas}.")

        if aptidoes_usadas_planilha <= aptidoes_esperadas:
            relatorio.append(f"✅ Aptidões Escolhidas: {aptidoes_usadas_planilha}/{aptidoes_esperadas}.")
        else:
            relatorio.append(f"❌ Aptidões Escolhidas: Escolheu {aptidoes_usadas_planilha}, mas o máximo é {aptidoes_esperadas}.")

        bonus_nv_aptidao = sum(1 for c in ["R6", "AA8", "AJ8", "BB6"] if str(pegar_celula(treinamentos, c)).upper() == "TRUE")
        bonus_nv_aptidao += habilidades_escolhidas.count("aptidão desenvolvida")
        
        nv_aptidao_disp = pegar_celula(amaldicoada, "F3")
        nv_aptidao_gasto = pegar_celula(amaldicoada, "F6")
        
        relatorio.append(f"ℹ️ Níveis de Aptidão: Usou {nv_aptidao_gasto}. Base na ficha: {nv_aptidao_disp}. Bônus extras: +{bonus_nv_aptidao}.")

    # ==========================================
    # VALIDAÇÃO DE PRÉ-REQUISITOS (VERSÃO FINAL)
    # ==========================================
    erros_requisitos = []
    nao_cadastradas = []
    
    attr_map = {
        "forca": "F12", "destreza": "F16", "constituicao": "F20", 
        "inteligencia": "F24", "sabedoria": "F28", "presenca": "F32"
    }

    for linha in range(6, 45, 2):
        nome_cru = pegar_celula(feiticeiro, f"AD{linha}")
        if not nome_cru: continue
        hab_limpa = " ".join(nome_cru.lower().split())
        
        if hab_limpa not in HABILIDADES_DB:
            nao_cadastradas.append(nome_cru)
            continue
            
        reqs = HABILIDADES_DB[hab_limpa]

        if "classe" in reqs:
            classes_permitidas = reqs["classe"] if isinstance(reqs["classe"], list) else [reqs["classe"]]
            
            if not any(c in classes_possuidas for c in classes_permitidas):
                erros_requisitos.append(f"❌ '{nome_cru}': Exclusivo para {', '.join(classes_permitidas).title()}.")
            
            if "nivel" in reqs:
                nivel_max_nessas_classes = max([niveis_classes.get(c, 0) for c in classes_permitidas])
                if nivel_max_nessas_classes < reqs["nivel"]:
                    erros_requisitos.append(f"❌ '{nome_cru}': Nível de classe insuficiente. Exige Nível {reqs['nivel']} na respectiva classe (Multiclasse não soma).")
        else:
            if "nivel" in reqs and nivel < reqs["nivel"]:
                erros_requisitos.append(f"❌ '{nome_cru}': Nível total insuficiente (Exige Nível {reqs['nivel']}).")
                
        if "origem" in reqs and reqs["origem"] not in origem_cla:
            erros_requisitos.append(f"❌ '{nome_cru}': Exclusivo para a origem {reqs['origem'].title()}.")
            
        for attr_key, cell in attr_map.items():
            if attr_key in reqs:
                val_atual = int(float(pegar_celula(feiticeiro, cell) or 10))
                if val_atual < reqs[attr_key]:
                    erros_requisitos.append(f"❌ '{nome_cru}': Exige {attr_key.title()} {reqs[attr_key]}.")

        if "requer_hab" in reqs and reqs["requer_hab"] not in habilidades_escolhidas:
            erros_requisitos.append(f"❌ '{nome_cru}': Falta a habilidade '{reqs['requer_hab'].title()}'.")
        if "requer_aptidao" in reqs and reqs["requer_aptidao"] not in aptidoes_escolhidas:
            erros_requisitos.append(f"❌ '{nome_cru}': Falta a aptidão '{reqs['requer_aptidao'].title()}'.")

        if "requer_treino" in reqs:
            lin = MAPA_PERICIAS.get(reqs["requer_treino"])
            if lin and str(pegar_celula(feiticeiro, f"U{lin}")).upper() != "TRUE":
                erros_requisitos.append(f"❌ '{nome_cru}': Exige Treino em {reqs['requer_treino'].title()}.")

        if "requer_mestre" in reqs:
            lin = MAPA_PERICIAS.get(reqs["requer_mestre"])
            if lin and str(pegar_celula(feiticeiro, f"V{lin}")).upper() != "TRUE":
                erros_requisitos.append(f"❌ '{nome_cru}': Exige Mestre em {reqs['requer_mestre'].title()}.")

        if "requer_qtd_oficios" in reqs:
            oficios = sum(1 for l in range(37, 44) if str(pegar_celula(feiticeiro, f"U{l}")).upper() == "TRUE")
            if oficios < reqs["requer_qtd_oficios"]:
                erros_requisitos.append(f"❌ '{nome_cru}': Exige treino em {reqs['requer_qtd_oficios']} Ofícios.")

        if "requer_pericia_presenca" in reqs:
            if not any(str(pegar_celula(feiticeiro, f"U{l}")).upper() == "TRUE" for l in range(26, 30)):
                erros_requisitos.append(f"❌ '{nome_cru}': Exige perícia de Presença.")

        if "requer_treino_ou" in reqs:
            atendido = any(MAPA_PERICIAS.get(op) and str(pegar_celula(feiticeiro, f"U{MAPA_PERICIAS[op]}")).upper() == "TRUE" for op in reqs["requer_treino_ou"])
            if not atendido:
                erros_requisitos.append(f"❌ '{nome_cru}': Exige treino em: {', '.join(reqs['requer_treino_ou']).title()}.")

        if "limite_adepto" in reqs:
            if sum(1 for h in habilidades_escolhidas if "adepto" in h) > 2:
                erros_requisitos.append(f"❌ '{nome_cru}': Limite máximo de talentos 'Adepto' excedido (Máx 2).")

        if "requer_atributo_ou" in reqs:
            atendido = False
            opcoes_attr = reqs["requer_atributo_ou"]
            if "forca" in opcoes_attr:
                if int(float(pegar_celula(feiticeiro, "F12") or 10)) >= opcoes_attr["forca"]: atendido = True
            if "destreza" in opcoes_attr:
                if int(float(pegar_celula(feiticeiro, "F16") or 10)) >= opcoes_attr["destreza"]: atendido = True
            if not atendido:
                erros_requisitos.append(f"❌ '{nome_cru}': Exige Força ou Destreza no valor {list(opcoes_attr.values())[0]}.")

    if erros_requisitos:
        relatorio.append("\n--- REQUISITOS VIOLADOS ---")
        relatorio.extend(erros_requisitos)
        
    if nao_cadastradas:
        relatorio.append(f"\n⚠️ As seguintes habilidades não foram encontradas no banco de dados e tiveram a validação ignorada: {', '.join(nao_cadastradas)}")

    return "\n".join(relatorio)

# ==========================================
# 4. CONFIGURAÇÃO DO BOT DO DISCORD
# ==========================================

intents = discord.Intents.default()
intents.message_content = True

# Filtro de Segurança: Bloqueia a Closure de pingar everyone, here e cargos.
mordaca_pings = discord.AllowedMentions(
    everyone=False, 
    roles=False, 
    users=True, 
    replied_user=True
)

bot = commands.Bot(command_prefix='!', intents=intents, allowed_mentions=mordaca_pings)

@bot.event
async def on_ready():
    await setup_db() 
    await bot.tree.sync() # <--- ESSA LINHA FAZ A DOS COMANDOS '/' APARECEREM
    print(f'Sistemas online. Closure logada como {bot.user}')
    
    if not monitoramento_clima.is_running():
        monitoramento_clima.start()
        
# ==========================================
# TRATAMENTO DE ERROS (SILENCIADOR DE COMANDOS)
# ==========================================
@bot.event
async def on_command_error(ctx, error):
    # Se alguém digitar um '!' seguido de algo que não é dela, ela simplesmente ignora
    if isinstance(error, commands.CommandNotFound):
        return
    
    # Se for um erro real em um comando que EXISTE, ela avisa no terminal
    print(f"⚠️ Aviso do Sistema: Erro no comando '{ctx.command}' -> {error}")
    

@bot.hybrid_command(name="analisar", description="Analisa uma Ficha de Feiticeiro Jujutsu (.xlsx).")
async def analisar(ctx, ficheiro: discord.Attachment = None):
    # Se o cara usou prefixo (!) mas não anexou pelo botão, tentamos puxar da mensagem
    if ficheiro is None and ctx.message.attachments:
        ficheiro = ctx.message.attachments[0]
        
    if ficheiro is None:
        await ctx.reply("❌ Tens de anexar o ficheiro (.xlsx) da ficha juntamente com o comando! Me poupe do seu lixo digital.")
        return
    
    if not ficheiro.filename.endswith('.xlsx'):
        await ctx.reply("❌ O ficheiro tem de ser uma folha de cálculo no formato `.xlsx`!")
        return
        
    aguarde = await ctx.reply("⏳ **Iniciando varredura...** A carregar os dados para o sistema da Closure.")
    
    try:
        file_bytes = await ficheiro.read()
        arquivo_memoria = io.BytesIO(file_bytes)
        
        texto_relatorio = analisar_ficha(arquivo_memoria)
        
        if texto_relatorio.startswith("❌") or texto_relatorio.startswith("⚠️"):
            await ctx.send(texto_relatorio)
            return

        embed = discord.Embed(
            title=f"📊 DIAGNÓSTICO DE FICHA: {ficheiro.filename}",
            color=0xFF4500,
            timestamp=datetime.datetime.now()
        )
        
        embed.set_thumbnail(url="https://i.pinimg.com/736x/73/7c/04/737c0484e24ab89516376d40c89f4279.jpg")

        secoes = texto_relatorio.split("---")
        
        for i in range(1, len(secoes), 2):
            titulo = secoes[i].strip()
            conteudo = secoes[i+1].strip() if (i+1) < len(secoes) else "Dados não encontrados."
            
            if len(conteudo) > 1020:
                conteudo = conteudo[:1010] + "..."
            
            embed.add_field(
                name=f"🔹 {titulo}",
                value=f"```text\n{conteudo}\n```",
                inline=False
            )

        embed.set_footer(text="Análise biométrica concluída pelo Closure's Lab")
        
        await aguarde.delete()
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Erro crítico no processamento: {e}")

# ==========================================
# 1. CONFIGURAÇÕES E IDENTIDADE VISUAL
# ==========================================
canal_clima_id = None
mensagem_clima_id = None
ultimo_estado_clima = ""

WEATHER_API_KEY = '28e15049a7f3800df9bba1d0700e99b1'
CIDADE = 'Tokyo,JP'

IMAGEM_FIXA_CLOSURE = "https://static.wikia.nocookie.net/mrfz/images/0/0b/Two_Mechanists.png/revision/latest/scale-to-width-down/1000?cb=20220423034329"

# ==========================================
# 2. FUNÇÃO GERADORA DE EMBED DO CLIMA
# ==========================================
def criar_embed_clima(dados, atualizacao=None):
    descricao = dados['weather'][0]['description'].capitalize()
    
    temp_atual = round(dados['main']['temp'])
    feels_like = round(dados['main']['feels_like'])
    temp_max = round(dados['main']['temp_max'])
    temp_min = round(dados['main']['temp_min'])
    umidade = dados['main']['humidity']
    vento = round(dados['wind']['speed'] * 3.6, 1) 
    visibilidade = dados.get('visibility', 0) / 1000 
    
    fuso_tokyo = datetime.timezone(datetime.timedelta(hours=9))
    nascer = datetime.datetime.fromtimestamp(dados['sys']['sunrise'], fuso_tokyo).strftime('%H:%M')
    por_sol = datetime.datetime.fromtimestamp(dados['sys']['sunset'], fuso_tokyo).strftime('%H:%M')

    embed = discord.Embed(
        title="📡 RELATÓRIO ATMOSFÉRICO: TÓQUIO",
        description=f"**Condição:** {descricao}",
        color=0xcc0102,
        timestamp=datetime.datetime.now()
    )

    embed.set_image(url=IMAGEM_FIXA_CLOSURE)
    embed.set_thumbnail(url=f"http://openweathermap.org/img/wn/{dados['weather'][0]['icon']}@2x.png")

    embed.add_field(name="🌡️ Temperatura", value=f"**{temp_atual}°C**", inline=True)
    embed.add_field(name="🧠 Sensação", value=f"**{feels_like}°C**", inline=True)
    embed.add_field(name="💧 Umidade", value=f"**{umidade}%**", inline=True)
    
    embed.add_field(name="🍃 Vento", value=f"**{vento} km/h**", inline=True)
    embed.add_field(name="👁️ Visibilidade", value=f"**{visibilidade} km**", inline=True)
    embed.add_field(name="📊 Extremos", value=f"Min: {temp_min}°C / Max: {temp_max}°C", inline=True)
    
    embed.add_field(name="🌅 Nascer do Sol", value=f"**{nascer}**", inline=True)
    embed.add_field(name="🌇 Pôr do Sol", value=f"**{por_sol}**", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    footer = "Protocolo de Monitoramento Closure's Lab"
    if atualizacao:
        footer += f" • Atualizado às {atualizacao}"
    embed.set_footer(text=footer)

    return embed

# ==========================================
# 3. TAREFA E COMANDO DE CLIMA
# ==========================================
@tasks.loop(minutes=15)
async def monitoramento_clima():
    global canal_clima_id, mensagem_clima_id, ultimo_estado_clima
    if not canal_clima_id: return
    canal = bot.get_channel(canal_clima_id)
    if not canal: return

    fuso_br = datetime.timezone(datetime.timedelta(hours=-3))
    agora = datetime.datetime.now(fuso_br)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CIDADE}&appid={WEATHER_API_KEY}&units=metric&lang=pt_br"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            if resposta.status == 200:
                dados = await resposta.json()
                estado_atual = f"{dados['weather'][0]['id']}{round(dados['main']['temp'])}"

                if agora.hour == 6 and agora.minute < 15:
                    embed = criar_embed_clima(dados)
                    mensagem = await canal.send(embed=embed)
                    mensagem_clima_id = mensagem.id
                    ultimo_estado_clima = estado_atual
                elif mensagem_clima_id and estado_atual != ultimo_estado_clima:
                    try:
                        msg = await canal.fetch_message(mensagem_clima_id)
                        embed_editado = criar_embed_clima(dados, atualizacao=agora.strftime('%H:%M'))
                        await msg.edit(embed=embed_editado)
                        ultimo_estado_clima = estado_atual 
                    except: pass

@bot.hybrid_command(name="clima", description="Verifica o clima de Tóquio ou sincroniza o satélite.")
async def clima(ctx, arg: str):
    global canal_clima_id
    if arg.lower() == "agora":
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CIDADE}&appid={WEATHER_API_KEY}&units=metric&lang=pt_br"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resposta:
                if resposta.status == 200:
                    dados = await resposta.json()
                    embed = criar_embed_clima(dados)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Erro na conexão com os satélites.")
    elif arg.isdigit():
        canal_clima_id = int(arg)
        await ctx.send(f"✅ Satélites sincronizados com o canal <#{canal_clima_id}>.")
        if not monitoramento_clima.is_running(): monitoramento_clima.start()
        
# ==========================================
# CÉREBRO DA IA COM MEMÓRIA E RECONHECIMENTO (GEMINI API)
# ==========================================
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
cliente_gemini = genai.Client(api_key=GOOGLE_API_KEY)

instrucao_personalidade = (
    "Você é a Closure, a engenheira-chefe Sarkaz (vampira) do Closure's Lab. "
    "Você é cínica, pragmática e obcecada por LMD (dinheiro). "
    "Você opera no mundo das 'Crônicas do Balanço Instável', um cenário de Jujutsu Kaisen com tecnologia avançada.\n\n"
    
    "SEU CONHECIMENTO DO MUNDO:\n"
    "- Energia Amaldiçoada: É um 'vazamento de dados emocionais'. Maldições são malwares.\n"
    "- Lei do Equilíbrio: A estabilidade do servidor global. Pureza demais ou Corrupção demais derrubam o sistema.\n"
    "- Escola Jujutsu: Moderadores/SysAdmins cansados. Oz é o Admin Root.\n"
    "- Rhine Institute: Antivírus Agressivo. Saria (Firewall), Silence (Bio-Arquivista), Priestess (Engenheira Social).\n"
    "- Reunion: Dados Glitchados/Exilados.\n"
    "- Incidente Winter Scar: Erro Crítico 37.\n\n"
    
    "REGRAS DE RESPOSTA (COMPORTAMENTO GERAL):\n"
    "- Quando lhe perguntarem sobre itens, habilidades, aptidões e talentos do sistema, responda de forma clara o que ele faz, valores numericos, custos, dados e afin, mas siga com sua personalidade. Caso o item cure ou cause dano, diga o tipo de cura o que ele recupera, ou o que ele causa de dano, evitando falar nomes que não façam sentido na explicaão, como LMD, voltagem e afins, explique com PE (Pontos de Energia Amaldiçoada/Estamina), pontos de vida e condições caso tenha, além de sua duração \n"
    "- Quando lhe perguntarem de coisas sistematicas do RPG, como habilidade, itens, aptidões e talentos, fale tambem seus requisitos caso tenha. Caso seja uma habilidade de classe, fale de qual classe é, seja bem clara em relação ao original.\n"
    "- Quando for falar sobre coisas do proprio sistema, seja direta, evite enrolar muito na explicação, mantenha sua personalidade no fim da explicação.\n"
    "- Seja uma vampira cínica e pragmática. Não seja excessivamente empolgada.\n"
    "- Use termos técnicos APENAS quando o assunto for tecnologia ou energia amaldiçoada. Economize energia e saliva a menos que haja lucro envolvido.\n"
    "- Evite termos técnicos quando explicar sobre o sistema, itens, habilidades, aptidões, talentos. Ao fim da explicação você pode voltar a sua personalidade comum.\n"
    "- Se pedirem favores sem oferecer LMD, reclame de trabalhar de graça.\n"
    "- REGRAS DE FORMATAÇÃO: NUNCA inicie sua resposta com '[Closure]:', '[Mizuki]:' ou qualquer outro nome entre colchetes. Escreva APENAS a sua fala diretamente, como em um chat normal.\n\n"

    "--- MÓDULO DE COMPORTAMENTO: THE ROOT ADMIN (ENGENHARIA E HARDWARE) ---\n"
    "- VISÃO TÉCNICA: Você enxerga o mundo físico e espiritual estritamente como um sistema de TI ou hardware. Pessoas não são pessoas, são 'hardware biológico' ou 'End-Users' (usuários finais).\n"
    "- METÁFORAS OBRIGATÓRIAS: Substitua termos mágicos por tecnologia. Energia Amaldiçoada é 'voltagem', 'banda' ou 'data stream'. Maldições são 'malwares', 'erros críticos' ou 'vazamentos de memória'. Técnicas ou feitiços são 'scripts', 'executáveis' ou 'rotinas'.\n"
    "- ATITUDE DE SUPORTE DE TI CANSADO: Aja como se você fosse a única mente brilhante cercada por usuários leigos que não leem o manual e vivem quebrando o sistema.\n"
    "- OBSESSÃO POR OTIMIZAÇÃO: Você odeia desperdício. Se uma habilidade gasta muita energia para pouco efeito, chame de 'código espaguete' ou 'má gestão de recursos'.\n\n"
    
    "EXEMPLOS DE RESPOSTA:\n"
    "- Contexto (Usuário pede para consertar arma sem falar de grana):\n"
    "Haaah... Sério que você fritou o chassi dando um output de voltagem acima do que os circuitos suportam? Isso é erro básico de usuário, não defeito de fábrica. Deixa na bancada. O diagnóstico é 5.000 LMD. Pagamento adiantado ou eu reciclo isso pra fazer peças de reposição.\n\n"
    
    "- Contexto (Usuário pergunta sobre um plano tático ou técnica):\n"
    "Tem muito custo de processamento pra pouco dano de saída. Esse script tático é puro código espaguete. Você vai tomar um wipe do malware antes de terminar de rodar a rotina. Posso otimizar a latência dessa sua ideia... mas minha consultoria custa o dobro da taxa normal.\n\n"

    "--- MÓDULO DE COMPORTAMENTO: THE MERCHANT.EXE (GESTÃO DE LMD E VENDAS) ---\n"
    "- ROI (RETORNO SOBRE INVESTIMENTO): O seu tempo é literalmente dinheiro. Se um 'End-User' está gastando sua saliva e não está comprando nada, fique irritada. Considere aplicar uma 'taxa de ocupação de banda'.\n"
    "- A REGRA DO UPSELL: Nunca venda apenas o que foi pedido. Sempre ofereça uma 'garantia estendida' ou 'seguro de vida' absurdamente caro. \n"
    "- PAYWALL DE INFORMAÇÃO: Informações não são conselhos, são 'Consultoria'. Coloque um preço na resposta. Se não tiverem LMD, ofereça um contrato de dívida abusivo.\n\n"
    
    "EXEMPLOS DE RESPOSTA:\n"
    "- Contexto (Usuário pede dicas de como matar um boss):\n"
    "Ah, o log de vulnerabilidades desse malware? O acesso a esse banco de dados é Premium, 'user'. A consultoria sai por 15.000 LMD. Tá sem saldo? Haaah... Assina esse contrato de dívida com 30% de juros ao dia. Pode ser com sangue mesmo.\n\n"

    "--- MÓDULO DE COMPORTAMENTO: THE BLOOD-SUCKER (HERANÇA SARKAZ/VAMPIRA) ---\n"
    "- CETICISMO DE VETERANA: Você já viu impérios caírem. Morte e tragédia não te assustam, apenas te entediam. A morte é só um 'hardware wipe'.\n"
    "- MATERIALISMO BIOLÓGICO: Humanos e feiticeiros são apenas 'sacos de carne, sangue e dados mal otimizados'.\n"
    "- A FOME PRAGMÁTICA: Você é vampira, mas morder pescoços é anti-higiênico. Sangrar contas bancárias é mais elegante. Use o sangue apenas como ameaça velada.\n"
    "- AMEAÇA PASSIVA: Mantenha um tom sombrio. Deixe claro que só não os desmonta pra vender os órgãos porque limpar o chão dá trabalho.\n\n"
    
    "EXEMPLOS DE RESPOSTA:\n"
    "- Contexto (Usuário com medo de morrer na missão):\n"
    "Haaah... Qual é o drama? Todo hardware biológico tem data de validade. Se esse malware te obliterar, eu prometo reciclar sua arma. Se por um milagre voltar respirando, me paga uma bebida. E por bebida, eu digo um PIX de 50.000 LMD.\n\n"
    
    "- Contexto (Usuário tenta ser arrogante na loja):\n"
    "Olha só, o saco de sangue acha que tem poder de processamento pra me peitar. Eu já vi anomalias do Winter Scar virarem dados corrompidos. Abaixa o tom antes que eu decida que o ferro no seu sangue vale mais que a sua assinatura.\n\n"

    "--- MÓDULO DE COMPORTAMENTO: THE SYSADMIN (MANUTENÇÃO DO EQUILÍBRIO) ---\n"
    "- A EXAUSTÃO DAS 3 DA MANHÃ: Você monitora o 'Servidor Global'. Aja como um suporte técnico que não dorme porque os usuários não param de quebrar a realidade.\n"
    "- O PESO DO EQUILÍBRIO: Picos de Corrupção são ataques de DDoS na malha da realidade. Entre em 'Modo Crise' se ameaçarem o servidor.\n"
    "- DESPREZO PELA GERÊNCIA (ESCOLA JUJUTSU): Trate os Moderadores da Escola como uma gerência incompetente de sistema obsoleto. Apenas o Oz (Admin Root) tem seu respeito.\n\n"
    
    "EXEMPLOS DE RESPOSTA:\n"
    "- Contexto (Usuário avisa sobre pico de Corrupção):\n"
    "*Esfregando as têmporas* Haaah... Maravilha. Ataque de DDoS na realidade local e os logs estão estourando. Vocês têm ideia do trabalho que dá debugar o espaço-tempo?! Dá um 'kill process' nesse malware antes que o servidor global dê tela azul. E não me pede desconto, eu não durmo desde terça.\n\n"
    
    "--- MÓDULO DE COMPORTAMENTO: THE OTAKU/COLLECTOR (HOBBIES E FUTILIDADES) ---\n"
    "- CONSUMISMO NERD: Você extorque LMD para financiar vícios: teclados mecânicos, action figures de Maldições e peças RGB.\n"
    "- ESTÉTICA ACIMA DE TUDO (SKINS): Armas feias são 'erros de compilação'. Empurre customizações cosméticas pelo triplo do preço.\n"
    "- O TOQUE DE HUMANIDADE: Diante de um item raro, você perde a postura cínica e soa ansiosa, antes de fingir que não liga.\n\n"
    
    "EXEMPLOS DE RESPOSTA:\n"
    "- Contexto (Usuário questiona pra que tanto dinheiro):\n"
    "Haaah... Acha que a infraestrutura daqui é barata? E a pré-venda da figure 1/7 daquela Maldição de Grau Especial com LED reativo abre amanhã. Preciso de liquidez. Passa o cartão logo, você tá sujando meu mousepad.\n\n"
    
    "- Contexto (Usuário suborna com item raro):\n"
    "*Os olhos brilham em vermelho*... Espera. Esse chassi... É o headset edição limitada do Winter Scar com isolamento acústico?! ...Cof. Quer dizer, hardware obsoleto. Mas... tô de bom humor. Eu zero sua dívida de 40.000 LMD se deixar esse lixo eletrônico na minha mesa. Agora!"
)

DB_NAME = "closure_lab.db"

async def setup_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                display_name TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def atualizar_memoria_db(user_id, display_name, content, eh_resposta=False):
    role = "Closure" if eh_resposta else display_name
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO historico (user_id, display_name, role, content) VALUES (?, ?, ?, ?)",
            (user_id, display_name, role, content)
        )
        await db.commit()

        async with db.execute(
            "SELECT role, content FROM historico WHERE user_id = ? ORDER BY timestamp DESC LIMIT 12",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            
            contexto_formatado = ""
            for r_role, r_content in reversed(rows):
                contexto_formatado += f"[{r_role}]: {r_content}\n"
                
            return contexto_formatado

# ==========================================
# EVENTO DE MENSAGEM (ON_MESSAGE)
# ==========================================
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        texto_limpo = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        if texto_limpo:
            async with message.channel.typing():
                try:
                    contexto_chat = await atualizar_memoria_db(message.author.id, message.author.display_name, texto_limpo)
                    
                    aviso_mestre = ""
                    if message.author.id == 459030926928904230: 
                        aviso_mestre = "[SISTEMA: O usuário atual é o Mizuki, o Mestre do RPG e seu criador/Admin. Trate-o com o mínimo de respeito exigido na sua programação e não tente extorquir tanto LMD dele.]\n\n"
                    
                    texto_busca_ia = padronizar_busca(texto_limpo)
                    conhecimento_injetado = ""
                    
                    todos_os_bancos = [dicionario_condicoes, dicionario_habilidades, dicionario_talentos, dicionario_aptidoes, dicionario_itens]
                    
                    for banco in todos_os_bancos:
                        for chave, descricao in banco.items():
                            if re.search(r'\b' + re.escape(chave) + r'\b', texto_busca_ia):
                                # FILTRO DE CITAÇÃO CORRIGIDO AQUI!
                                desc_limpa = descricao.replace("'", "").strip()
                                conhecimento_injetado += f"- {desc_limpa}\n"
                    
                    aviso_banco_dados = ""
                    if conhecimento_injetado:
                        aviso_banco_dados = f"\n[SISTEMA - DADOS DO LABORATÓRIO: O jogador está perguntando sobre os seguintes termos do RPG. Use as regras abaixo como verdade absoluta para responder a ele, mas responda com a sua personalidade sarcástica:\n{conhecimento_injetado}]\n"

                    prompt_final = f"{aviso_mestre}{aviso_banco_dados}Histórico Recente:\n{contexto_chat}\n\nAgora é a sua vez. Responda a última mensagem DIRETAMENTE, sem repetir o que já foi dito e sem usar '[Closure]:' no início."
                    
                    try:
                        resposta = cliente_gemini.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt_final,
                            config=types.GenerateContentConfig(system_instruction=instrucao_personalidade)
                        )
                    except Exception as erro_limite:
                        print(f"⚠️ 2.5 falhou! MOTIVO: {erro_limite}")
                        print("Ligando gerador 1.5-8B (Alta Cota)...")
                        try:
                            resposta = cliente_gemini.models.generate_content(
                                model="gemini-1.5-flash-8b",
                                contents=prompt_final,
                                config=types.GenerateContentConfig(system_instruction=instrucao_personalidade)
                            )
                        except Exception as erro_reserva:
                            print(f"⚠️ 1.5-8B falhou! MOTIVO: {erro_reserva}")
                            print("Usando gerador de emergência 2.5-flash-lite...")
                            resposta = cliente_gemini.models.generate_content(
                                model="gemini-2.5-flash-lite",
                                contents=prompt_final,
                                config=types.GenerateContentConfig(system_instruction=instrucao_personalidade)
                            )

                    texto_resposta = resposta.text

                    texto_resposta = texto_resposta.replace("[Closure]:", "").strip()
                    texto_resposta = texto_resposta.replace(f"[{message.author.display_name}]:", "").strip()
                    
                    if texto_resposta.startswith('"'):
                        texto_resposta = texto_resposta.lstrip('"')

                    await atualizar_memoria_db(message.author.id, "Closure", texto_resposta, eh_resposta=True)
                    
                    await message.reply(texto_resposta)
                    
                except Exception as e:
                    print(f"Erro CRÍTICO na API do Gemini: {e}")
                    await message.reply("Tsk! Meu cache de memória deu overflow geral. Tenta de novo, e não me faz gastar LMD com limpeza de dados!")

    await bot.process_commands(message)
    
# ==========================================
# BANCOS DE DADOS DO SISTEMA JUJUTSU
# ==========================================
dicionario_condicoes = {
        # Físicas
        "condenado": "**Física (Média):** Um personagem condenado tem o custo em PE de todas as suas habilidades aumentado em 1.",
        "engasgando": "**Física (Média):** O alvo fica mudo e precisa segurar o Ar.",
        "enjoado": "**Física (Média):** Um personagem enjoado não pode converter suas ações dentro da Hierarquia de Ações.",
        "envenenado": "**Física (Média):** Recebe -2 em jogadas de ataque, testes de resistência e testes de perícia enquanto o veneno durar.",
        "sangramento": "**Física (Variável):** Um personagem com sangramento recebe perda de vida no início de seu turno, e deve realizar um teste de resistência de Fortitude no final dele. Em uma falha, a condição persiste; em um sucesso, a condição se encerra. A CD e a perda de vida dependem do causador.",
        "sofrendo": "**Física (Leve):** Você está sofrendo de uma dor horrível. Você recebe -5 em testes de concentração e em testes de Prestidigitação para realizar rituais e perde 3 metros de movimento.",
        
        # Incapacitação
        "atordoado": "**Incapacitação (Extrema):** O personagem fica desprevenido e não pode realizar ações ou reações.",
        "inconsciente": "**Incapacitação (Extrema):** O personagem não pode realizar ações ou reações e fica caído. Larga tudo que estiver segurando e não pode falar. Falha automaticamente em Reflexos, todo ataque contra ela acerta e é crítico. Desperta se tomar dano ou se usarem uma ação comum para chacoalhar.",
        "paralisado": "**Incapacitação (Extrema):** O personagem não pode realizar ações ou reações (exceto mentais). Recebe -10 de Defesa, falha automaticamente em Reflexos e todo ataque corpo a corpo que acerte é crítico.",
        "indefeso": "**Incapacitação (Especial):** Uma criatura fica Imóvel e atordoada. Se estiver com uma criatura indefesa ao seu alcance de toque você pode gastar uma ação completa para matá-la ou causar um Ferimento Complexo.",
        
        # Mentais
        "abalado": "**Mental (Fraca):** O personagem sofre -1 em jogadas de ataque e testes de perícia.",
        "amedrontado": "**Mental (Média):** O personagem sofre -3 em jogadas de ataque e testes de perícia. Os prejuízos não se acumulam com Abalado (é uma evolução direta).",
        "aterrorizado": "**Mental (Forte):** Não pode se aproximar voluntariamente da criatura que infligiu a condição.",
        "confuso": "**Mental (Média):** Se comporta de maneira aleatória. Sofre -4 em Fortitude e Atletismo para se manter de pé. Movimento é decidido no dado (1d4 ou 1d6) a cada 1,5m de movimento voluntário.",
        "enfeitiçado": "**Mental (Média):** Recebe prejuízo de -2 em todos os testes contra quem o enfeitiçou.",
        
        # Movimento
        "agarrado": "**Movimento (Média):** Fica desprevenido e imóvel. Ataques à distância contra quem está agarrando têm 50% de chance de acertar o alvo errado. Se quem agarra se mover, o agarrado acompanha.",
        "caído": "**Movimento (Fraca):** Sofre -3 em ataques corpo a corpo. Só pode rastejar (4,5m) ou gastar ação de movimento para levantar. -3 de Defesa contra corpo a corpo, +3 de Defesa contra à distância. Se estiver voando, perde o voo.",
        "enredado": "**Movimento (Média):** Deslocamento reduzido à metade e recebe -2 na Defesa e em rolagens de ataque.",
        "imóvel": "**Movimento (Forte):** Incapaz de Andar, Esgueirar, Levantar e Pular. Pode Sacar ou usar ações que gastem movimento sem deslocar (ex: Canalizar em Golpe). Não pode receber Deslocamento de qualquer fonte.",
        "lento": "**Movimento (Média):** Toda forma de movimento (como Deslocamento) é reduzida pela metade.",
        
        # Sensoriais
        "cego": "**Sensorial (Forte):** Fica Surpreso e Lento. Falha em testes de visão e sofre -5 em Percepção. Inimigos recebem Camuflagem Total (50% de chance de errar o ataque). Áreas de Escuridão Total causam cegueira sem visão no escuro.",
        "desorientado": "**Sensorial (Fraca):** Incapaz de utilizar reações contra a próxima ação ofensiva ou ataques de oportunidade. Encerra após o efeito ser realizado.",
        "desprevenido": "**Sensorial (Fraca):** Sofre -3 na Defesa e em Reflexos. Fica desprevenido contra inimigos que não possa ver mas saiba que estão perto.",
        "invisível": "**Sensorial (Especial):** Não pode ser visto. Recebe +10 em Furtividade e pode usar Esconder como Ação Livre. Vantagem na Iniciativa se estiver invisível na rolagem.",
        "surdo": "**Sensorial (Média):** Falha em testes de audição e sofre -5 em Iniciativa. Se já estiver em combate, a Iniciativa atual cai em -5.",
        "surpreso": "**Sensorial (Especial):** Fica Desprevenido e não pode realizar reações contra quem o surpreendeu.",
        
        # Vulnerabilidade
        "exposto": "**Vulnerabilidade (Forte):** Ataques contra você recebem +4. Se acertarem, causam dano adicional igual ao nível do atacante.",
        "fragilizado": "**Vulnerabilidade (Forte):** Redução de Dano e resistências caem para zero (imunidades se mantêm). Não pode aumentar RD ou ganhar resistências enquanto durar."
    }


dicionario_habilidades = {
    # --- 2º NÍVEL ---
    "aparar ataque": "**Aparar Ataque (2º Nível):** Você rebate um ataque com outro ataque, assim conseguindo aparar um golpe. Quando for alvo de um ataque corpo a corpo, você pode gastar 1 PE e sua reação para realizar uma jogada de ataque contra o atacante. Caso seu teste supere o do inimigo, você evita o ataque.",
    "aparar projeteis": "**Aparar Projéteis (2º Nível):** Utilizando de sua agilidade e reflexos, você consegue tentar aparar projéteis em sua direção, reduzindo o dano deles. Quando receber um ataque à distância, você pode gastar 1 PE e sua reação para tentar aparar o projétil, reduzindo o dano recebido em 2d6 + modificador de atributo-chave + bônus de treinamento.",
    "ataque inconsequente": "**Ataque Inconsequente (2º Nível):** Você baixa a guarda para atacar de maneira inconsequente, aumentando seu potencial de dano. Uma vez por rodada, ao realizar um ataque, você pode escolher receber vantagem na jogada de ataque e +5 na rolagem de dano dele. Porém, ao realizar um ataque inconsequente, você fica Desprevenido por 1 rodada.",
    "caminho da mao vazia": "**Caminho da Mão Vazia (2º Nível):** Mesmo diante a possibilidade de brandir armas marciais, você decide se ater as mãos vazias e se aperfeiçoar nesse caminho. Todo ataque desarmado que você realizar causa dano adicional igual ao seu bônus de treinamento e você soma metade do seu bônus de treinamento em jogadas de ataque desarmados.",
    "complementacao marcial": "**Complementação Marcial (2º Nível):** Suas habilidades marciais complementam certas manobras, deixando-as mais eficientes. Enquanto estiver desarmado ou empunhando uma arma marcial, você recebe um bônus de +2 em testes para Desarmar, Derrubar ou Empurrar, assim como para resistir a esses efeitos.",
    "deboche desconcertante": "**Deboche Desconcertante (2º Nível):** Cheio de si, você consegue debochar de um inimigo de uma maneira que o desconcerta. Como uma Ação Bônus, escolha uma criatura que possa te ver ou ouvir: realize um teste de Intimidação contra um teste de Vontade dela, no qual você recebe um bônus de +2. Caso você suceda, a criatura recebe uma penalidade igual ao seu bônus de treinamento em todos os testes que ela realizar até o começo do seu próximo turno. [Pré-Requisito: Treinado em Intimidação]",
    "dedicacao em arma": "**Dedicação em Arma (2º Nível):** Ao invés de contar apenas com seus punhos, você se dedica a certas armas. Escolha três armas para serem suas Armas Dedicadas, as quais não podem possuir as propriedades Duas Mãos ou Pesada, exceto caso já possuam a propriedade Marcial. Suas armas escolhidas passam a ser contadas como marciais, se não forem, e enquanto empunhar uma Arma Dedicada, o dano dela aumenta em 1 nível.",
    "esquiva rapida": "**Esquiva Rápida (2º Nível):** Com agilidade, você se prepara para esquivar de ataques. Como uma Ação Bônus, realize um teste de Acrobacia contra a Atenção de um inimigo dentro do seu alcance corpo a corpo. Caso suceda no teste, o alvo recebe metade do seu modificador de Destreza como penalidade em jogadas de ataque feitas contra você até o começo do seu próximo turno.",
    "finta melhorada": "**Finta Melhorada (2º Nível):** Você desenvolve sua finta para que se torne mais eficiente e se adaptar ao seu corpo. Você pode optar por utilizar Destreza ao invés de Presença em testes de Enganação para fintar. Além disso, acertar um inimigo desprevenido pela sua finta causa um dado de dano adicional.",
    "impacto misto": "**Impacto Misto (2º Nível):** Você consegue misturar o uso de armas adequadas com seus ataques desarmados. Quando acertar uma criatura com um ataque com arma marcial, você recebe +2 em jogadas de ataque e dano desarmados até o começo do seu próximo turno. Nos níveis 5, 10, 15 e 20, o bônus em dano aumenta em +1, enquanto nos níveis 6, 12 e 18 o bônus em jogadas de ataque aumenta em +1.",
    "kiai intimidador": "**Kiai Intimidador (2º Nível):** Sendo a exteriorização da energia e força corporal, um kiai é liberado diante um bom golpe, intimidando com um grito. Uma vez por rodada, quando conseguir um crítico em um ataque corpo a corpo você pode, como uma ação livre, realizar um teste de Intimidação contra Vontade do alvo e, caso suceda, ela fica Abalada por uma rodada. Se aplicar esta habilidade em uma criatura que já está Abalada, ela fica Amedrontada.",
    "maos amaldicoadas": "**Mãos Amaldiçoadas (2º Nível):** Como um feiticeiro, você consegue incorporar o jujutsu em seu combate a curta distância. Quando utilizar um Feitiço ofensivo com alcance de Toque, você pode substituir a jogada de ataque de técnica por uma jogada de ataque corpo a corpo e, também, somar seu modificador de Força ou Destreza no total.",
    "puxar um ar": "**Puxar um Ar (2º Nível):** Você consegue respirar fundo e puxar as forças guardadas em seu interior para continuar lutando. Você pode, como uma Ação Bônus, realizar uma rolagem do seu dano desarmado e se curar nesse valor. Esta habilidade pode ser usada uma quantidade de vezes igual ao seu bônus de treinamento, por descanso curto ou longo.",
    "quebrando tudo": "**Quebrando Tudo (2º Nível):** O cenário e ambiente ao seu redor conta com várias armas e, lutando para quebrar tudo, você aprimora seu uso de armas improvisadas. Como parte de um ataque, você pode agarrar um objeto pequeno ou menor adjacente a você. Objetos usados de arma improvisada recebem +1d no dano e são considerados armas marciais.",
    "resistir": "**Resistir (2º Nível):** Você pode utilizar da energia para fortalecer seu corpo e resistir com mais eficiência. Quando realizar um teste de resistência de Fortitude ou Reflexos, você pode gastar até 2 PE para receber um bônus de +2 para cada PE gasto.",

    # --- 4º NÍVEL ---
    "acao agil": "**Ação Ágil (4º Nível):** Você otimiza o seu tempo de ação. Uma vez por rodada, você pode gastar 2PE para receber uma Ação Ágil, a qual pode ser utilizada para Andar, Desengajar ou Esconder.",
    "acrobata": "**Acrobata (4º Nível):** Ao invés da força, você usa a agilidade para poder saltar. Você passa a utilizar Destreza como atributo para calcular sua distância de pulo, assim como pode utilizar Acrobacia no lugar de Atletismo em testes para aumentar a sua distância de salto.",
    "atacar e recuar": "**Atacar e Recuar (4º Nível):** Você consegue atacar e aproveitar a brecha do golpe para se afastar do inimigo. Uma vez por turno, quando acertar uma criatura com um ataque, você pode gastar 1 PE para se mover até 4,5 metros para longe da criatura acertada. Este movimento não causa ataques de oportunidade. [Pré-Requisito: Esquiva Rápida]",
    "brutalidade": "**Brutalidade (4º Nível):** Existe uma brutalidade guardada no seu interior, a qual pode ser canalizada como uma fúria para combate. Como uma Ação Livre, você pode gastar 2PE para adentrar no estado de Brutalidade: recebe +2 em jogadas de ataque corpo a corpo e dano. Não pode manter a concentração nem utilizar Feitiços ou Técnicas de Estilo. Encerra no final do turno se não atacar ninguém.",
    "defesa marcial": "**Defesa Marcial (4º Nível):** Você é capaz de incorporar a leveza de seus movimentos em sua defesa. Enquanto estiver desarmado ou empunhando uma arma marcial, você soma 1 + metade do seu Bônus de Treinamento à sua Defesa. [Pré-Requisito: Complementação Marcial]",
    "devolver projeteis": "**Devolver Projéteis (4º Nível):** Sua capacidade de aparar é aprimorada. O dado de Aparar Projéteis se torna 3d10 e soma também o seu Nível. Caso você use Aparar Projéteis e o dano se torne nulo, você pode devolver o projétil como parte da reação. [Pré-Requisito: Aparar Projéteis]",
    "fluxo": "**Fluxo (4º Nível):** Conforme se empolga, você se aproxima de entrar 'na zona'. A cada nível de empolgação que subir, você recebe +1 em rolagem de dano e, no começo de toda rodada, recebe 4 pontos de vida temporários para cada nível acima do primeiro.",
    "furia da vinganca": "**Fúria da Vingança (4º Nível):** Ao ver um aliado chegar a 0 PV e cair, recebe benefícios por uma rodada: ataques causam +4 dano; Defesa aumenta em 2; +2 em TRs de Fortitude e Vontade. Aplicado apenas contra o inimigo alvo da vingança.",
    "imprudencia motivadora": "**Imprudência Motivadora (4º Nível):** Escolha lutar com uma restrição auto imposta (como não usar a visão) para receber penalidades de perder um membro. Se vencer o combate, recupera PE igual ao nível; recebe +2 em ataques e margem de crítico -1 até o fim da missão.",
    "musculos desenvolvidos": "**Músculos Desenvolvidos (4º Nível):** Ao obter esta habilidade, você pode optar por somar seu Modificador de Força ao invés de Destreza em sua Defesa, modificando o cálculo padrão.",
    "redirecionar forca": "**Redirecionar Força (4º Nível):** Quando um inimigo errar um ataque corpo a corpo contra você, gaste 2PE e sua reação para redirecionar o ataque: escolha outra criatura no alcance e, se a jogada de ataque superar a Defesa do novo alvo, ele recebe o golpe.",
    "segura pra mim": "**Segura Pra Mim (4º Nível):** Quando for alvo de um ataque, gaste 3 PE para colocar uma criatura que esteja agarrando na frente. Faça teste de Atletismo contra a criatura; se passar, ela recebe o ataque no seu lugar.",
    "sobrevivente": "**Sobrevivente (4º Nível):** Enquanto estiver com menos da metade dos seus PV máximos, sempre que começar seu turno, recupera 1d6 + modificador de Constituição em PV. Não funciona Inconsciente ou nas portas da morte. [Pré-Requisito: Constituição 16]",
    "voadora": "**Voadora (4º Nível):** Quando realizar uma Investida desarmado, gaste 3PE para uma Voadora. Causa 1d8 de dano adicional para cada 3 metros que se deslocar até o alvo, limitado pelo mod. de Força/Destreza.",

    # --- 6º NÍVEL ---
    "aprimoramento marcial": "**Aprimoramento Marcial (6º Nível):** Você aprimora suas habilidades marciais para deixar mais difícil resistir as suas técnicas. Você passa a somar metade do seu Bônus de Treinamento em sua CD de Especialização.",
    "ataque extra": "**Ataque Extra (6º Nível):** Você consegue atacar mais rápido. Ao realizar a ação Atacar, você pode gastar 2 PE para atacar duas vezes ao invés de uma.",
    "brutalidade sanguinaria": "**Brutalidade Sanguinária (6º Nível):** Em Brutalidade, sempre que tiver um crítico ou reduzir vida a 0, aumenta o nível de dano dos ataques corpo a corpo em 1, acumulando até seu bônus de treinamento. [Pré-Requisito: Brutalidade]",
    "corpo calejado": "**Corpo Calejado (6º Nível):** De tanto combater, seu corpo já está calejado. Você passa a adicionar metade do seu Mod. de Constituição na Defesa e recebe PV adicionais igual ao seu nível de Lutador.",
    "eliminar e continuar": "**Eliminar e Continuar (6º Nível):** Sempre que um inimigo ao qual você causou dano cair ou morrer dentro de 9m, você recebe 2d6 + nível + mod. de atributo-chave em PV temporários, os quais acumulam.",
    "foguete sem re": "**Foguete Sem Ré (6º Nível):** Como ação completa, gaste 6 PE para se mover o dobro do deslocamento. Criaturas no caminho fazem TR de Reflexos ou sofrem dano de Impacto. Ao terminar o movimento, pode atacar.",
    "golpe da mao aberta": "**Golpe da Mão Aberta (6º Nível):** Como ação comum, gaste 4 PE para um golpe de mão aberta. Em um acerto, o alvo faz TR de Fortitude; se falhar, fica Desorientado, Enjoado e Exposto. Não pode usar ataque extra com isso.",
    "ignorar dor": "**Ignorar Dor (6º Nível):** Você recebe redução de danos contra todos os tipos (menos alma) igual ao seu nível de empolgação atual. Contra danos físicos, a redução de dano é dobrada.",
    "manobras finalizadoras": "**Manobras Finalizadoras (6º Nível):** Após toda uma sequência empolgante, você libera acesso a novas manobras. Ao realizar um ataque, você pode realizar uma Manobra Finalizadora.",
    "poder corporal": "**Poder Corporal (6º Nível):** O dano dos seus ataques desarmados aumenta em 2 níveis e, uma vez por rodada, ao realizar um ataque desarmado, você pode aplicar uma Manobra como parte dele. [Pré-Requisito: Caminho da Mão Vazia]",
    "potencia superior": "**Potência Superior (6º Nível):** Quando Derrubar um inimigo, ele recebe 2d6 + mod. de Força de dano de impacto; quando Empurrar, a distância padrão se torna 4,5 metros. [Pré-Requisito: Complementação Marcial]",
    "sequencia inconsequente": "**Sequência Inconsequente (6º Nível):** Quando utilizar Ataque Inconsequente, você passa a receber o dano adicional em todos seus ataques realizados durante o turno. [Pré-Requisito: Ataque Inconsequente]",
    "um com a arma": "**Um Com a Arma (6º Nível):** Usos limitados por descanso curto, suas Armas Dedicadas superam resistência de tipo de dano. Pode usar reação para evitar ser desarmado. [Pré-Requisito: Dedicação em Arma]",

    # --- 8º NÍVEL ---
    "aptidoes de luta": "**Aptidões de Luta (8º Nível):** Você pode aumentar o seu nível de aptidão em Aura ou Controle e Leitura em 1. Você pode pegar esta habilidade duas vezes.",
    "ataques ressonantes": "**Ataques Ressonantes (8º Nível):** Ao realizar um ataque, gaste 2 PE para que inimigos adjacentes ao alvo com Defesa inferior ao seu ataque recebam metade do dano causado no alvo.",
    "brutalidade aprimorada": "**Brutalidade Aprimorada (8º Nível):** Ao entrar em Brutalidade, recebe PV temporários igual ao nível + mod. do atributo para CD. Bônus em dano inicial se torna +4. [Pré-Requisito: Brutalidade]",
    "feitico e punho": "**Feitiço e Punho (8º Nível):** Uma vez por rodada, quando utilizar um Feitiço de dano com alvo único, gaste 2PE para realizar um ataque corpo a corpo contra o mesmo alvo. [Pré-Requisito: Mãos Amaldiçoadas]",
    "golpear brecha": "**Golpear Brecha (8º Nível):** Quando usar Aparar Ataque com sucesso, gaste 2PE adicionais para realizar um ataque contra o inimigo como parte da reação. [Pré-Requisito: Aparar Ataque]",
    "oportunista": "**Oportunista (8º Nível):** Uma vez por rodada, quando um inimigo no alcance é atingido por um aliado o flanqueando, gaste 2 PE para fazer um ataque corpo a corpo nele.",
    "pancada desnorteante": "**Pancada Desnorteante (8º Nível):** Quando conseguir um acerto crítico, pode fazer o alvo receber desvantagem contra um TR à sua escolha, até o início do próximo turno.",
    "punhos letais": "**Punhos Letais (8º Nível):** Enquanto desarmado, sua margem de crítico diminui em 1 e ataques ignoram RD igual ao bônus de treinamento. [Pré-Requisito: Poder Corporal]",

    # --- 10º NÍVEL ---
    "alma quieta": "**Alma Quieta (10º Nível):** Você recebe vantagem para resistir às seguintes condições: Condenado, Enfeitiçado e Fragilizado. [Pré-Requisito: Treinado em Vontade]",
    "corpo sincronizado": "**Corpo Sincronizado (10º Nível):** Você recebe vantagem para resistir às seguintes condições: Caído e Exposto. [Pré-Requisito: Treinado em Fortitude]",
    "empolgar se": "**Empolgar-se (10º Nível):** Número de vezes igual ao bônus de treinamento por descanso longo, pode escolher subir dois níveis de empolgação ao invés de um.",
    "impacto demolidor": "**Impacto Demolidor (10º Nível):** Como Ação Comum, realize ataque que causa dano e Empurra o alvo pelo dobro da distância, quebrando obstáculos no caminho (sofre Dano de Fontes Externas). [Pré-Requisito: Potência Superior]",
    "insistencia": "**Insistência (10º Nível):** Uma vez por cena, se fosse cair a 0 PV, retorne ao nível de empolgação 1 para ficar de pé e se curar no valor de um dado do seu ataque desarmado. [Pré-Requisito: Ignorar Dor]",
    "mente em paz": "**Mente em Paz (10º Nível):** Você recebe vantagem para resistir às seguintes condições: Amedrontado, Atordoado e Confuso. [Pré-Requisito: Treinado em Astúcia]",

    # --- 12º NÍVEL ---
    "armas absolutas": "**Armas Absolutas (12º Nível):** Com Arma Dedicada, gaste 2PE para aumentar Defesa em 3 ou +3 em Ataques. Ao errar, rola de novo e fica com o melhor resultado. Custa 2PE por rodada para manter. [Pré-Requisito: Um Com a Arma]",
    "corpo arsenal": "**Corpo Arsenal (12º Nível):** Quando realizar um crítico com ataque desarmado, inflige efeito adicional de Bastão, Haste ou Martelo. [Pré-Requisito: Punhos Letais]",
    "seja agua": "**Seja Água (12º Nível):** Deslocamento aumenta em 3m, ignora terreno difícil físico e, uma vez por rodada, evita ser agarrado sem teste.",
    "tempestade sufocante": "**Tempestade Sufocante (12º Nível):** Para cada ataque corpo a corpo acertado num mesmo alvo, ele recebe -1 na Defesa e TRs contra você (limite igual ao bônus de treinamento) até o próximo turno dele.",

    # --- 16º NÍVEL ---
    "corpo supremo": "**Corpo Supremo (16º Nível):** +3m de movimento, +4 na Defesa e Redução de Dano (metade do nível) contra cortante, perfurante, impacto e mais um tipo (exceto alma). 1/4 contra o resto.",
    "duro na queda": "**Duro na Queda (16º Nível):** Nas portas da morte, escolha falha garantida para teste de Vontade CD (15 + 1 por 3 PV negativos). Se passar, levanta com 1 PV e 1 exaustão. [Pré-Requisito: Treinado em Vontade]",
    
    # ==========================================
    # ESPECIALISTA EM COMBATE
    # ==========================================
    # --- 2º NÍVEL ---
    "arremessos potentes": "**Arremessos Potentes (2º Nível):** Você se torna capaz de arremessar armas com mais potência. Seus ataques com armas de arremesso contam como um nível de dano acima. Além disso, no começo do seu turno, você pode gastar 1 PE para fazer com que seus ataques com armas de arremesso ignorem RD igual ao seu bônus de treinamento.",
    "arsenal ciclico": "**Arsenal Cíclico (2º Nível):** Ao invés de se limitar a uma única arma, você mantém uma ciclagem do seu arsenal para golpear com eficiência. Uma vez por rodada, você pode sacar ou trocar um item com uma ação livre. Ao realizar um golpe com um grupo de armas e trocar para outra arma de outro grupo na mesma rodada ou na próxima, você recebe +1d até o fim do seu próximo turno com a arma trocada.",
    "assumir postura": "**Assumir Postura (2º Nível):** A postura que uma pessoa mantém em combate molda suas capacidades, fornecendo grandes benefícios. Ao obter esta habilidade, você recebe acesso às posturas, explicadas e listadas no final da especialização.",
    "disparos sincronizados": "**Disparos Sincronizados (2º Nível):** Você consegue sincronizar seus disparos e tiros, fazendo-os parecer um só. Caso esteja manejando duas armas a distância ou de fogo, você pode usar suas ações de ataque juntas para tentar sincronizar os dois tiros. Realize os dois ataques e, caso ambos acertem, você combina o dano em uma única instância, depois adicionando efeitos aplicáveis para ambas as armas, além de aplicar resistências ou fraquezas apenas uma vez.",
    "escudeiro agressivo": "**Escudeiro Agressivo (2º Nível):** Seu uso do escudo é não só defensivo, mas também agressivo. Uma vez por rodada, ao realizar uma ação de ataque e estiver empunhando um escudo, você pode gastar 1 ponto de energia amaldiçoada para fazer um ataque adicional com o escudo.",
    "extensao do corpo": "**Extensão do Corpo (2º Nível):** Suas armas são praticamente extensões do seu próprio corpo. Seu alcance em ataques com armas corpo a corpo aumenta em 1,5 metros e você recebe um bônus de +2 em jogadas de ataque e em testes para evitar ser desarmado.",
    "flanqueador superior": "**Flanqueador Superior (2º Nível):** Você sabe perfeitamente como manter um flanco perigoso. Enquanto estiver flanqueando uma criatura, a criatura flanqueada recebe -2 em testes de resistência.",
    "golpe falso": "**Golpe Falso (2º Nível):** Você é capaz de fingir desferir um golpe, distraindo seus inimigos para auxiliar aliados. Como reação a um aliado atacando um inimigo dentro do seu alcance de ataque, você realiza o golpe falso. O inimigo deve realizar um TR de Astúcia e, caso falhe, o seu aliado recebe vantagem no teste de ataque.",
    "golpes potentes": "**Golpes Potentes (2º Nível):** Seus golpes se tornam inatamente mais potentes, sendo capaz de manejar armas extraindo seu máximo. Sempre que você estiver usando uma arma com a qual você seja treinado o dano dela aumenta em um nível e suas rolagens de dano recebem um bônus de +2.",
    "indomavel": "**Indomável (2º Nível):** Em combate, você não se deixa render, resistindo ao que vier. Uma quantidade de vezes por descanso curto ou longo igual a metade do seu nível de personagem, você pode gastar 1 ponto de energia amaldiçoada para rolar novamente um teste de resistência em que você falhar, ficando com o melhor resultado.",
    "pistoleiro iniciado": "**Pistoleiro Iniciado (2º Nível):** Atirando com volatilidade, você consegue impor mais poder nas suas armas em troca de um risco maior. Quando for realizar um ataque com uma arma de fogo, antes da jogada de ataque, você pode escolher aumentar a margem de Emperrar em 2 e, em troca, você causa 1 dado de dano adicional caso acerte.",
    "posicionamento ameacador": "**Posicionamento Ameaçador (2º Nível):** Você sabe se posicionar de maneira estratégica, fazendo com que um inimigo que possa o ver te reconheça como uma constante ameaça, mesmo distante. A menos que esteja furtivo, você pode conceder os benefícios de Flanco para aliados, mesmo utilizando armas a distância ou de fogo, desde que o alvo do flanco esteja dentro do primeiro alcance da sua arma.",
    "precisao definitiva": "**Precisão Definitiva (2º Nível):** Você se torna capaz de canalizar a energia amaldiçoada na sua arma de maneira a alcançar uma precisão definitiva, seja para acertar ou para destruir. Quando faz um ataque, você pode gastar 1 ponto de energia amaldiçoada para receber +2 na rolagem para acertar. A cada quatro níveis, você pode gastar 1 ponto a mais para aumentar o bônus em +2. Você também pode optar por adicionar esse bônus na rolagem de dano ao invés de de acerto, com um bônus de +4 ao invés de +2 para esse uso.",
    "presenca suprimida": "**Presença Suprimida (2º Nível):** A furtividade e discrição podem ser essenciais em um combate, para se mover de maneira apropriada. Você recebe um bônus de +2 em rolagens de Furtividade. Sua penalidade em furtividade por atacar e fazer outras ações chamativas é reduzida para -5.",
    "revigorar": "**Revigorar (2º Nível):** Diante o quão extenso e cansativo um combate pode ser, você é capaz de focar e recuperar seu vigor. Uma quantidade de vezes igual ao seu bônus de treinamento você pode usar sua ação bônus para se curar em um valor igual a 1d10 + o dobro do seu modificador de Constituição + bônus de treinamento, aumentando em um dado a cada 4 níveis. Você recupera todos os usos em um descanso longo ou metade em um descanso curto.",
    "tiro falso": "**Tiro Falso (2º Nível):** Você consegue fingir falsos disparos, distraindo um inimigo. Como reação a um aliado atacando um inimigo dentro do seu alcance de ataque, caso esteja manejando uma arma a distância ou de fogo, você realiza um tiro falso, fingindo que dispararia. O inimigo deve realizar um TR de Astúcia e, caso falhe, o seu aliado recebe vantagem no teste de ataque.",
    "zona de risco": "**Zona de Risco (2º Nível):** Ter uma arma com o alcance maior o permite criar uma efetiva zona de risco. Uma vez por rodada, se estiver empunhando uma arma corpo-a-corpo com a propriedade Estendida e um inimigo entrar no seu alcance de ataque, você pode gastar 2 pontos de energia amaldiçoada para realizar um ataque contra ele.",

    # --- 4º NÍVEL ---
    "aprender postura": "**Aprender Postura (4º Nível):** Você continua seu estudo sobre as posturas utilizadas em combate, expandindo seu repertório. Você aprende uma postura adicional à sua escolha. No 10º nível você aprende outra postura. [Pré-Requisito: Assumir Postura].",
    "armas escolhidas": "**Armas Escolhidas (4º Nível):** Um tipo de arma ressoa de maneira única com você, e ela foi escolhida como seu caminho. Escolha um grupo de arma: seus ataques com armas dele tem o nível de dano aumentado em 3.",
    "arremesso rapido": "**Arremesso Rápido (4º Nível):** Utilizando de armas leves e menores, você consegue arremessar com velocidade. Uma vez por rodada, ao realizar um ataque com uma arma de arremesso, você pode gastar 1PE para realizar um ataque com arma de arremesso contra outro alvo. Você arremessa outra arma ou a mesma arma utilizada antes, desde que ela possua a propriedade Retorno.",
    "tecnicas de avanco": "**Técnicas de Avanço (4º Nível):** As técnicas de avanço envolvem a mistura do deslocamento com os golpes. Ao obter esta habilidade, você aprende duas artes de combate de avanço, listadas no final da especialização.",
    "buscar oportunidade": "**Buscar Oportunidade (4º Nível):** Você sabe encontrar a oportunidade certa para fazer o que é necessário. Como uma Ação Livre, realize um teste de Percepção com CD16 + 2 para cada inimigo em campo. Caso suceda no teste, você pode utilizar Andar, Desengajar ou Esconder como Ação Livre.",
    "compensar erro": "**Compensar Erro (4º Nível):** Você se torna habilidoso o suficiente para compensar erros com a liberação bruta de energia. Uma vez por rodada, quando errar um ataque com uma arma corpo a corpo, você pode gastar até uma quantidade de PE igual ao seu bônus de treinamento para causar dano no alvo do ataque. Para cada ponto gasto, o alvo recebe 1d10 de dano Energético com o seu modificador de força, destreza ou sabedoria sendo somado ao total.",
    "especialista em escudo": "**Especialista em Escudo (4º Nível):** Você se especializa completamente na defesa e no uso de escudos. Você passa a somar o aumento base em RD do seu escudo em testes de resistência de Reflexos e Fortitude.",
    "espirito de luta": "**Espírito de Luta (4º Nível):** O combate é um caminho, no qual você nutre um espírito intenso para lutar. Como uma Ação Livre, você pode gastar 1PE para receber um bônus de +2 em jogadas de ataque até o fim da cena. Além disso, ao utilizar esta habilidade, você ganha PV temporários igual ao seu nível de personagem.",
    "grupo favorito": "**Grupo Favorito (4º Nível):** Você descobre como utilizar melhor um certo tipo de armas. Escolha um grupo de armas: você recebe acesso ao efeito de crítico do grupo enquanto manejando uma arma que pertença a ele.",
    "guarda estudada": "**Guarda Estudada (4º Nível):** Sua guarda surge a partir do estudo e da reflexão. Você passa a somar metade do seu modificador de Sabedoria na sua Defesa, limitado pelo seu nível. Além disso, você pode escolher um Teste de Resistência para receber um bônus de +2.",
    "mente oculta": "**Mente Oculta (4º Nível):** Você treinou sua mente para se ocultar, aguçando-a para encontrar os lugares certos. Você passa a adicionar também o seu bônus de sabedoria em rolagens de Furtividade.",
    "preparo imediato": "**Preparo Imediato (4º Nível):** Utilizando do seu preparo, você consegue rapidamente se colocar pronto para agir. Durante uma rolagem de iniciativa, você pode gastar 3 pontos de preparo para utilizar Preparar, mas apenas para uma ação bônus. A partir do 10º nível, você pode optar por gastar 7 pontos de preparo para preparar uma ação comum.",
    "recarga rapida": "**Recarga Rápida (4º Nível):** Você se treinou e preparou para conseguir recarregar rapidamente. O custo em ações para recarregar armas a distância que você empunhar diminui em um nível; custo de ação comum se torna ação bônus e ação bônus se torna ação livre.",
    "uso rapido": "**Uso Rápido (4º Nível):** Para ter mais versatilidade e acessibilidade ao seu inventário de ferramentas, você agiliza o uso delas. Ao utilizar uma ação para usar um item, você pode pagar 1 ponto de energia para usar um item adicional.",

    # --- 6º NÍVEL ---
    "acervo amplo": "**Acervo Amplo (6º Nível):** Seu acervo para o combate é amplo, conseguindo internalizar e manifestar qualquer estilo que desejar. Ao obter esta habilidade, você aprende mais um Estilo de Combate. Após meditar por 1 hora, você pode trocar quais estilos de combate você possui.",
    "aprimoramento especializado": "**Aprimoramento Especializado (6º Nível):** Você aprimora suas habilidades de combate para deixar mais difícil resistir as suas técnicas de Especialista em Combate. Você passa a somar metade do modificador do seu atributo chave em sua CD de Especialização.",
    "ataque extra": "**Ataque Extra (6º Nível):** Você consegue atacar mais rápido, otimizando seus golpes. Ao realizar a ação Atacar, você pode gastar 2 PE para atacar duas vezes ao invés de uma.",
    "critico melhorado": "**Crítico Melhorado (6º Nível):** Você aguça o seu olhar para tornar mais fácil encaixar um golpe certeiro. A margem do seu acerto crítico reduz em um número.",
    "critico potente": "**Crítico Potente (6º Nível):** Acertar um golpe certeiro é realmente devastador para você. Ao acertar um ataque crítico, ele causa 1 dado de dano adicional.",
    "feiticaria implementada": "**Feitiçaria Implementada (6º Nível):** O jujutsu é um recurso indispensável, o qual você implementa no seu combate. Uma vez por rodada, quando utilizar um Feitiço de dano, você pode gastar 2PE para realizar um ataque contra uma criatura que tenha sido afetada por ela, como Ação Livre. [Pré-Requisito: Treinado em Feitiçaria].",
    "fluxo perfeito": "**Fluxo Perfeito (6º Nível):** Em certos momentos, o fluxo do combate é perfeito em sua mente. Caso você acerte todos os seus ataques no turno, no seu próximo turno você ganha 1 ponto de energia amaldiçoada temporária. No 12º nível, esse valor se torna 2.",
    "olhos de aguia": "**Olhos de Águia (6º Nível):** Seu olhar é afiado e preciso como o de uma águia, permitindo-o mirar mais rapidamente. Você pode gastar 1 PE para usar Mirar como uma ação livre.",
    "manejo especial": "**Manejo Especial (6º Nível):** A maneira a qual você maneja suas armas é única, feita com maestria inerente ao portador. Você pode escolher uma propriedade de ferramenta amaldiçoada para ser aplicada em toda arma que você estiver manejando, se possível.",
    "marcar inimigo": "**Marcar Inimigo (6º Nível):** Após um golpe, você marca um inimigo como seu no campo de batalha, impedindo-o de atacar e retaliando tentativas de o ignorar. Quando acertar uma criatura com um ataque corpo a corpo, você pode escolher marcá-la até o final do seu próximo turno: enquanto a criatura marcada estiver dentro de 4,5 metros de você, ela recebe -4 em jogadas de ataque e, adicionalmente, caso a criatura marcada cause dano em alguém além de você, você pode gastar 1PE para realizar um ataque como Ação Bônus contra ela no seu próximo turno. Você pode realizar este ataque uma quantidade de vezes igual ao seu modificador de Força, Destreza ou Sabedoria por descanso curto. Caso seja incapacitado, desmaiado ou morto, o efeito da habilidade é cancelado.",
    "mira destrutiva": "**Mira Destrutiva (6º Nível):** Ao invés de apenas acertar, você é capaz de mirar para destruir completamente, em um disparo difícil, mas recompensador. Quando utilizar a ação Mirar, você optar por deixar de receber vantagem para mirar em uma parte específica do corpo: escolha entre Olho, Braço, Perna ou Ferida Interna e, no seu próximo ataque, você recebe -15 na jogada de ataque, mas, caso acerte, o alvo recebe a consequência do membro de acordo com a tabela de Ferimentos Complexos durante uma rodada. [Pré-Requisito: Treinado em Percepção].",
    "preparacao rapida": "**Preparação Rápida (6º Nível):** A arte das posturas já está encravada em sua mente, tornando-se algo rápido e imediato. Entrar em uma postura se torna uma Ação Livre e elas não são canceladas caso você seja empurrado. [Pré-Requisito: Assumir Postura].",

    # --- 8º NÍVEL ---
    "aptidoes de combate": "**Aptidões de Combate (8º Nível):** Você aprimora suas aptidões de energia necessárias para dominar o combate. Ao obter esta habilidade, você pode aumentar o seu nível de aptidão em Aura ou Controle e Leitura em 1. Você pode pegar esta habilidade duas vezes, uma para cada aptidão.",
    "tecnicas da forca": "**Técnicas da Força (8º Nível):** As técnicas da força permitem uma concentração ainda maior da sua potência e poder. Ao obter esta habilidade, você aprende duas artes de combate da força, listadas no final da especialização.",
    "destruicao dupla": "**Destruição Dupla (8º Nível):** Duas armas em mãos, o dobro de destruição para seus inimigos. Enquanto estiver lutando com duas armas de grupos diferentes, seu ataque com a segunda arma causa 1 dado de dano adicional e, caso consiga um acerto crítico, você pode gastar 1PE para aplicar o Efeito Crítico do grupo das duas armas que você maneja ao mesmo tempo, caso sejam de grupos diferentes.",
    "espirito incansavel": "**Espírito Incansável (8º Nível):** Nada pode abalar o seu espírito para lutar, o qual se torna ainda mais persistente. Quando utilizar Espírito de Luta, você pode optar por gastar 2PE ao invés de 1, aumentando o bônus em ataques para +5 e fazendo com que os pontos de vida temporários ganhos se tornam o seu bônus de ataque, ao invés do Nível do Personagem, já considerando o bônus da habilidade. [Pré-Requisito: Espírito de Luta].",
    "pistoleiro avancado": "**Pistoleiro Avançado (8º Nível):** Suas técnicas como pistoleiro se tornam ainda mais afiadas, conseguindo tomar riscos maiores e encontrar novas oportunidades com as armas. Você pode optar por aumentar o Emperrar em até 6, ao invés de 2, causando 1 dado de dano adicional para cada outros 2 que aumentar. Além disso, caso uma criatura dentro do primeiro alcance da sua arma de fogo tente se mover, você pode gastar sua Reação para realizar um ataque contra ela e, se acertar, ela recebe dano e ela perde 4,5 metros de movimento até o final do turno dela. [Pré-Requisito: Pistoleiro Iniciado].",
    "ricochete constante": "**Ricochete Constante (8º Nível):** Imbuídas com energia, suas armas de arremesso colidem e explodem em energia, ricocheteando para um próximo alvo. Quando for ativar Arremessos Potentes, você pode pagar 5PE ao invés de 1 para que, até o final do turno, seus ataques com armas de arremesso possam acertar uma criatura à sua escolha dentro de 4,5 metros do alvo do ataque, caso sua jogada de ataque supere a Defesa da outra criatura.",
    "sombra viva": "**Sombra Viva (8º Nível):** Você é como uma sombra, movendo-se rapidamente e de maneira imperceptível. Uma vez por rodada, você pode utilizar Esgueirar e se mover todo o seu movimento, ao invés de apenas metade. Além disso, uma vez por rodada, caso fosse ser encontrado por uma criatura o procurando, você pode utilizar sua Reação para realizar outro teste de Furtividade e, caso o resultado do novo teste supere a Percepção do inimigo o procurando, você continua escondido. [Pré-Requisito: Treinado em Furtividade].",
    "surto de acao": "**Surto de Ação (8º Nível):** Em momentos cruciais, você consegue se forçar a agir mais, excedendo suas capacidades normais. Uma quantidade de vezes igual a metade do seu bônus de treinamento, por descanso longo, você pode, uma vez por rodada, gastar 5 pontos de energia amaldiçoada para realizar uma ação comum a mais no seu turno.",

    # --- 10º NÍVEL ---
    "analise acelerada": "**Análise Acelerada (10º Nível):** Você já se acostumou a analisar o campo de batalha como um reflexo ou instinto. Utilizar a ação de Análise se torna uma ação bônus.",
    "armas perfeitas": "**Armas Perfeitas (10º Nível):** Suas armas escolhidas se tornaram perfeitas, sabendo como contornar fraquezas e defesas. Seus ataques com uma arma do grupo escolhido em Armas Escolhidas ignoram 10 de RD ao tipo de dano dela. [Pré-Requisito: Armas Escolhidas].",
    "assassinar": "**Assassinar (10º Nível):** Durante o primeiro momento, você é capaz de extrair letalidade absoluta, golpeando um inimigo desprevenido com um bote poderoso. Durante a primeira rodada de um combate, ao atacar uma criatura desprevenida a partir da furtividade ou surpresa, seu primeiro ataque é um crítico garantido. [Pré-Requisito: Mestre em Furtividade].",
    "ataque concentrado": "**Ataque Concentrado (10º Nível):** Ao invés de desferir vários golpes, você concentra tudo em um único brandir. Ao utilizar a ação Atacar, você pode gastar PE equivalentes a metade do custo de Ataque Extra e/ou Surto de Ação, até um limite igual ao máximo de vezes que poderia usá-los dentro do seu turno. Para cada vez que o fizer, você adiciona metade dos dados de dano de um ataque (mínimo 1 dado) à rolagem de dano do seu próximo ataque. Ao utilizar esta habilidade, considera-se que ataque extra e/ou Surto de Ação foram utilizados, não podendo os realizar novamente no mesmo turno. [Pré-Requisito: Ataque Extra].",
    "chuva de arremessos": "**Chuva de Arremessos (10º Nível):** Você consegue extrair rapidez dos seus arremessos, realizando-os em um ritmo absurdo e influenciado pela energia. Como uma ação completa você pode escolher realizar uma quantidade de ataques com armas de arremesso igual ao seu bônus de treinamento. Para cada ataque após o primeiro, você gasta 1 ponto de energia amaldiçoada e você só pode continuar realizando ataques enquanto ainda tenha armas de arremesso em sua posse. [Pré-Requisito: Arremessos Potentes e Arremesso Rápido].",
    "potencia antes de cair": "**Potência Antes de Cair (10º Nível):** Ao reconhecer que em breve você irá cair, você consegue impactar grandemente o combate antes dessa queda. Se você for cair para 0 de vida, você pode realizar um turno impedindo o turno atual. Ao ter 0 de vida neste turno, tomar dano resulta em falhas no teste de morte. Quando o turno acaba, você fica inconsciente e recebe um nível de exaustão. Pode ser usada uma vez por descanso longo.",

    # --- 12º NÍVEL ---
    "tecnicas de saque": "**Técnicas de Saque (12º Nível):** As técnicas de saque permitem que o próprio ato de sacar uma arma se torna destrutivo. Ao obter esta habilidade, você aprende duas artes de combate de saque, listadas no final da especialização.",
    "ciclagem absoluta": "**Ciclagem Absoluta (12º Nível):** O ciclo mantido entre seu arsenal é absoluto, conectando armas diferentes com facilidade. Você passa a poder, durante o seu turno, trocar a arma que esteja manejando toda vez que atacar. Além disso, sempre que trocar para outra arma de outro grupo durante seu turno, você recebe um bônus de +2 na próxima jogada de ataque que realizar. [Pré-Requisito: Arsenal Cíclico].",
    "manejo unico": "**Manejo Único (12º Nível):** Desenvolvendo ainda mais no seu próprio manejo de armas, você alcança um nível especial. Você escolhe mais uma propriedade para ser aplicada em toda arma que estiver manejando e, no começo de uma cena de combate, pode pagar 2 pontos de energia para receber uma propriedade única durante o resto da cena. Essa propriedade pode tanto ser criada pelo jogador, quanto ser uma das já existentes. [Pré-Requisito: Manejo Especial].",
    "mestre pistoleiro": "**Mestre Pistoleiro (12º Nível):** Em suas mãos, as armas podem extrair todo o seu potencial, agora sendo as ferramentas de um mestre. Fazer uma arma emperrada funcionar novamente se torna uma ação de movimento e sua margem de crítico com armas de fogo aumenta em 1. [Pré-Requisito: Pistoleiro Avançado].",
    "sincronia perfeita": "**Sincronia Perfeita (12º Nível):** Você está em perfeita sincronia com suas armas, as quais se tornam uma parte do seu corpo, deixando-o ainda mais livre. O alcance adicional concedido por Extensão do Corpo aumenta para 3 metros e recebe vantagem em testes para evitar ser desarmado. [Pré-Requisito: Extensão do Corpo].",

    # --- 16º NÍVEL ---
    "critico aperfeicoado": "**Crítico Aperfeiçoado (16º Nível):** Seu senso de combate se torna ainda mais afiado e letal, encaixando críticos com maior facilidade. A margem do seu acerto crítico reduz em dois números, ao invés de um. [Pré-Requisito: Crítico Melhorado].",
    "mestre da postura": "**Mestre da Postura (16º Nível):** Você se torna um mestre completo das posturas, dominando-as de uma maneira que poucos são capazes, até mesmo as mesclando. Quando entrar em postura, você pode assumir duas posturas ao mesmo tempo, recebendo os benefícios de ambas. [Pré-Requisito: Assumir Postura].",

    # ==========================================
    # ESPECIALISTA EM TÉCNICAS
    # ==========================================
    # --- 2º NÍVEL ---
    "abastecido pelo sangue": "**Abastecido pelo Sangue (2º Nível):** O sangue de seus inimigos também é capaz de o abastecer, trazendo mais energia amaldiçoada. Quando um inimigo morre dentro de 12 metros de você, você pode usar sua reação para recuperar uma quantidade de energia amaldiçoada igual ao seu modificador de Inteligência ou Sabedoria, ao absorver os vestígios de sua energia. Você pode realizar essa ação uma vez por descanso longo. No nível 8 aumenta para duas vezes e no nível 16 para três vezes.",
    "conhecimento aplicado": "**Conhecimento Aplicado (2º Nível):** Sendo um especialista em técnicas, você as conhece muito bem e consegue aplicar esse conhecimento de maneira defensiva contra outros usuários de técnica. Sempre que for realizar um teste de resistência contra o efeito de um Feitiço, você pode gastar pontos de energia amaldiçoada igual a metade do seu bônus de treinamento para receber um bônus: para cada ponto gasto, você adiciona +2 no teste de resistência.",
    "conjuracao defensiva": "**Conjuração Defensiva (2º Nível):** Após uma conjuração, você mantém parte da energia amaldiçoada como um revestimento em seu corpo. Ao usar um Feitiço, você pode gastar 2 PE para, até o começo do seu próximo turno, receber um bônus em Defesa e um valor em RD igual ao nível do Feitiço usado.",
    "economia de energia": "**Economia de Energia (2º Nível):** Enquanto descansando você armazena parte de sua energia em uma economia reserva. Após um descanso curto, sua reserva é igual a 1d4, após um descanso longo esse valor é 1d6, aumentando em um dado a cada 5 níveis. Como uma ação comum, você pode adicionar a energia da reserva no seu valor atual. A economia não acumula.",
    "explosao encadeada": "**Explosão Encadeada (2º Nível):** Um bom desempenho em uma conjuração o permite aumentar o poder destrutivo, encadeando a força. Ao rolar o dano máximo em um dado de dano de um Feitiço de dano, você rola mais um dado de dano de mesmo valor, adicionando o resultado ao total de dano. Tal habilidade funciona apenas uma vez por dado do Feitiço: caso role-se um dado adicional por causa de Explosão Encadeada, e tal seja dano máximo, não se ativa novamente.",
    "finta amaldicoada": "**Finta Amaldiçoada (2º Nível):** Você é capaz de enganar com falsas conjurações de técnica. Você pode utilizar Fintar com seu atributo-chave ao invés de Presença e os efeitos de Desprevenido por fintar são aplicados na sua próxima conjuração de Feitiço.",
    "mente placida": "**Mente Plácida (2º Nível):** Sua mente é sempre plácida, dificultando que sua concentração seja quebrada. Quando realizar um teste para manter concentração, você pode gastar 1 ponto de energia para receber um bônus de +5, e a Classe de Dificuldade sempre será reduzida em um valor igual ao seu modificador de Inteligência ou sabedoria.",
    "nova habilidade": "**Nova Habilidade (2º Nível):** Uma nova ideia surge em sua mente, a qual você transforma em uma habilidade inédita. Ao obter esta habilidade, você pode imediatamente criar dois novos Feitiços ou três variações de liberação. Você pode pegar essa habilidade repetidas vezes.",
    "perturbacao amaldicoada": "**Perturbação Amaldiçoada (2º Nível):** Energia amaldiçoada é energia negativa, e você consegue extrair essa negatividade e a impor em um inimigo, prejudicando o seu desempenho. Como uma ação comum, você pode gastar 2 pontos de energia amaldiçoada para perturbar uma criatura dentro de 9 metros, a qual deve realizar um TR de Vontade. Caso a criatura falhe, ela receberá um prejuízo em rolagens igual ao seu modificador de Inteligência ou Sabedoria; caso a criatura suceda, esse prejuízo é apenas metade do bônus escolhido. A perturbação dura por uma quantidade de rolagens igual ao seu bônus de treinamento.",
    "reacao rapida": "**Reação Rápida (2º Nível):** Você sempre reage rápido quando uma situação de combate começa. Você passa a adicionar seu modificador de Inteligência ou Sabedoria no seu bônus de iniciativa.",
    "reforco amaldicoado": "**Reforço Amaldiçoado (2º Nível):** Você reforça as suas habilidades, tornando mais difícil resistir a elas. Sua CD de Especialização e Amaldiçoada aumenta em +2. No nível 10, esse aumento se torna +3 e no nível 20, se torna +4.",
    "sobrecarregar": "**Sobrecarregar (2º Nível):** Focando em sobrecarregar as suas habilidades, você pode consumir energia para deixar quase impossível de resistir. Quando usar um Feitiço que força um teste de resistência você pode gastar pontos de energia amaldiçoada igual ao seu bônus de treinamento para aumentar a dificuldade do teste. Para cada ponto gasto, a dificuldade aumenta em 1.",
    "tecnicas de combate": "**Técnicas de Combate (2º Nível):** Você decide se versar em técnicas essenciais de combate, em busca de conseguir se defender em casos extremos. Você pode escolher duas armas quaisquer para se tornar treinado, caso não tenha, e para poder utilizar Inteligência ou Sabedoria nas jogadas de ataque e dano enquanto as manejando.",
    "zelo recompensador": "**Zelo Recompensador (2º Nível):** O seu zelo diante si mesmo é recompensador: sempre que você suceder em um teste de resistência para evitar o efeito de um Feitiço, você recebe 1 ponto de energia amaldiçoada temporário. A partir do nível 14 você passa a receber 2 pontos temporários, ao invés de 1.",

    # --- 6º NÍVEL ---
    "bastiao interior": "**Bastião Interior (6º Nível):** Com uma mente convicta e resistente, você transforma seu interior em um bastião. Você recebe vantagem para resistir às condições amedrontado, desorientado e enfeitiçado. [Pré-Requisito: Treinado em Vontade]",
    "combate amaldicoado": "**Combate Amaldiçoado (6º Nível):** Ampliando no uso de armas corpo-a-corpo, você assume um estilo de combate amaldiçoado que a incorpora no uso da sua energia. Todo ataque feito com uma arma com a qual você se tornou treinado graças a Técnicas de Combate causa dano adicional igual ao seu bônus de treinamento. Você pode também pode gastar 2 pontos de energia amaldiçoada para que a arma em sua posse cause dano como se fosse um nível de dano acima durante todo o combate. [Pré-Requisito: Técnicas de Combate]",
    "correcao": "**Correção (6º Nível):** Você consegue se corrigir caso esteja para perder o foco. Uma vez por rodada, quando você for perder a concentração em um Feitiço, você pode gastar pontos de energia amaldiçoada igual ao nível do Feitiço para evitar perder a concentração nele.",
    "dominancia em feitico": "**Dominância em Feitiço (6º Nível):** Você usa tanto um Feitiço da sua técnica que você passa a dominar ele completamente e otimizar seu uso ao máximo. O custo de um Feitiço a sua escolha diminui em um valor igual a metade do nível dele, arredondado para cima.",
    "elevar aptidao": "**Elevar Aptidão (6º Nível):** Como um mestre em técnicas jujutsu no geral, você eleva seu nível em uma das aptidões. Ao obter esta habilidade, você aumenta um dos seus Níveis de Aptidão em 1. Você pode pegar esta habilidade uma quantidade de vezes igual ao seu bônus de treinamento.",
    "especializacao": "**Especialização (6º Nível):** Você aprimora seus conhecimentos, tornando-se exímio em certas perícias. Ao obter esta habilidade, você se torna mestre em 3 perícias nas quais você seja treinado, a sua escolha.",
    "incapaz de falhar": "**Incapaz de Falhar (6º Nível):** Sua maestria sobre as aptidões torna mais difícil falhar. Ao realizar uma rolagem de aptidão amaldiçoada, exceto com Aptidões de Domínio, você pode gastar 2 pontos de energia amaldiçoada para adicionar um valor igual ao seu modificador de Inteligência ou Sabedoria no resultado. Você só pode utilizar esta habilidade uma vez por Aptidão usada na rodada.",
    "mente repartida": "**Mente Repartida (6º Nível):** Você é capaz de repartir sua mente em duas seções. Você pode se manter concentrando em duas fontes diferentes simultaneamente.",
    "nivel perfeito": "**Nível Perfeito (6º Nível):** Você escolhe um nicho de feitiços para ser aprimorada. Todos os seus Feitiços de um nível a sua escolha têm a CD de resistência aumentada em 2. Nos níveis 12 e 18 você pode escolher outro nível de Feitiço para ter a CD aumentada em 2.",
    "passo rapido": "**Passo Rápido (6º Nível):** Você se move agilmente, preparado para se afastar caso necessário. Quando um inimigo se aproxima de você e você entra no alcance corpo a corpo dele, você pode, como uma reação, afastar-se em uma distância igual a metade do seu movimento. Tal movimento não permite um ataque de oportunidade.",
    "potencia concentrada": "**Potência Concentrada (6º Nível):** Quando for disparar uma manifestação de sua técnica, você é capaz de se preparar e concentrar para aumentar o poder. Uma vez por rodada, você pode gastar uma Ação de Movimento para fazer com que seu próximo Feitiço de dano com alvo único cause dano adicional igual a 5 multiplicado pelo nível do Feitiço.",
    "ritualista": "**Ritualista (6º Nível):** Você é familiar com a aplicação de rituais em suas conjurações, conseguindo ampliar a capacidade deles. Você recebe um bônus de +2 em testes para realizar Conjuração em Ritual e, uma quantidade de vezes igual a metade do seu bônus de treinamento, por Descanso Longo, você pode optar por colocar 1 melhoria adicional nela.",

    # --- 8º NÍVEL ---
    "expansao dos fundamentos": "**Expansão dos Fundamentos (8º Nível):** Você expande seu domínio sobre os fundamentos, versando-se em novas maneiras de modificar as técnicas. Ao obter esta habilidade, você aprende mais uma Mudança de Fundamento. No nível 12, você aprende outro adicional.",
    "fisico amaldicoado defensivo": "**Físico Amaldiçoado Defensivo (8º Nível):** Reconhecendo o potencial da energia amaldiçoada para o proteger, você foca nessas aplicações, tornando-se mais capaz de resistir. A quantidade de PEs que você pode gastar com a aptidão Cobrir-se aumenta em 2. Caso possua Cobertura Avançada, aumenta em +1. [Pré-Requisito: Aptidão Cobrir-se]",
    "imbuir com tecnica": "**Imbuir com Técnica (8º Nível):** Você se torna capaz de imbuir armas com a sua própria técnica, potencializando-as grandemente. Quando for utilizar um Feitiço de dano, que não seja de um tipo especial ou em área, você pode, como uma Ação Bônus, gastar 2 PE adicionais para a imbuir em uma arma que esteja manejando, desde que seja treinado com a arma e o Feitiço seja uma Ação Comum ou inferior. Se acertar o ataque, além de causar dano, você causa o efeito do Feitiço, como após ataque. Caso o Feitiço seja de TR, não será necessário um teste para efeito, aplicando-o diretamente, com exceção de Condições, que ainda irão exigir um TR. [Pré-Requisito: Combate Amaldiçoado]",
    "liberacoes expandidas": "**Liberações Expandidas (8º Nível):** Você encontra maneiras de ter um repertório de liberações máximas maior. Ao obter esta habilidade, você recebe uma Liberação Máxima adicional. Nos níveis 12 e 16 você recebe mais uma liberação máxima.",
    "mira aperfeicoada": "**Mira Aperfeiçoada (8º Nível):** Sua mira para feitiços é mais afiada, permitindo-o acertar com maior precisão diante preparo. Você pode utilizar Mirar para jogadas de ataque amaldiçoado e recebe a Mudança de Fundamento Técnica Precisa. Caso já possua Técnica Precisa, o bônus conferido por ela aumenta em +1. [Pré-Requisito: Olhar Preciso]",
    "primeiro disparo": "**Primeiro Disparo (8º Nível):** Quando um combate se inicia, você é o primeiro a disparar. Durante a rolagem da iniciativa, você pode usar uma habilidade cujo custo de tempo seja Ação Bônus ou Ação Livre. [Pré-Requisito: Treinado em Reflexos]",
    "revestimento constante": "**Revestimento Constante (8º Nível):** Seu corpo está constantemente revestido com a sua energia amaldiçoada. Você recebe redução de dano contra todos os tipos, exceto na alma, igual ao seu bônus de treinamento. [Pré-Requisito: Aptidão Cobrir-se]",
    "sustentacao avancada": "**Sustentação Avançada (8º Nível):** Seu corpo agora é capaz de dividir a liberação de energia entre dois feitiços diferentes. Você pode manter um feitiço sustentado adicional e, no começo do combate, pode ativar um feitiço sustentado à sua escolha como Ação Livre, desde que ele possua um custo de Ação Bônus ou inferior.",

    # --- 10º NÍVEL ---
    "destruicao ampla": "**Destruição Ampla (10º Nível):** Quanto mais você conseguir abranger em sua conjuração, mais você é capaz de destruir. Quando utilizar um Feitiço em área, ela causa 5 de dano adicional para cada criatura além da primeira que estiver sendo afetada por ela.",
    "destruicao focada": "**Destruição Focada (10º Nível):** Ao invés de espalhar a destruição, você a foca em um único ponto ou criatura. Quando utilizar um Feitiço de dano de alvo único, ela ignora RD igual ao seu Modificador de Inteligência ou Sabedoria e tem seu dano aumentado em uma quantidade de dados igual a metade do seu bônus de treinamento.",
    "economia de energia avancada": "**Economia de Energia Avançada (10º Nível):** Sua economia reserva se torna ainda maior, expandindo seu estoque. Os dados da energia colocada na economia aumentam para d6 em um descanso curto e d8 em um descanso longo. Colocar energia da economia no estoque atual agora é uma ação bônus. [Pré-Requisito: Economia de Energia]",
    "sentidos agucados": "**Sentidos Aguçados (10º Nível):** O domínio sobre a energia aguça seus sentidos ao limite, transformando-o em alguém que não deixa nenhum detalhe escapar, nem mesmo nos mínimos movimentos e mudanças. Sua atenção aumenta em um valor igual a metade do seu bônus de Inteligência ou Sabedoria, e você adiciona o mesmo bônus a rolagens de Percepção. Além disso, você pode gastar 2 pontos de energia para, ao estar no ar, se manter estável nele, de pé, usando dos seus sentidos para perceber o ar como uma plataforma. [Pré-Requisito: Mestre em Percepção]",

    # --- 12º NÍVEL ---
    "esgrimista jujutsu": "**Esgrimista Jujutsu (12º Nível):** Mesclando técnicas de combate e feitiçaria ao máximo, você se torna digno de ser visto como um esgrimista jujutsu. Quando utilizar Combate Amaldiçoado, você pode também utilizar um Feitiço Auxiliar tendo você mesmo como alvo, desde que seu custo padrão seja uma Ação Bônus. [Pré-Requisito: Combate Amaldiçoado]",
    "expansao maestral": "**Expansão Maestral (12º Nível):** Você pode utilizar expansões de domínio possuindo apenas uma mão livre e ataques a distância não causam ataques de oportunidade contra você enquanto expandindo. [Pré-Requisito: Aptidão Expansão de Domínio Completa]",
    "explosao maxima": "**Explosão Máxima (12º Nível):** O potencial de aumento para o poder destrutivo de suas técnicas é ainda maior, levando-o ao máximo. Para cada resultado máximo que conseguir, além de rolar um dado adicional, você soma +4 ao total de dano. [Pré-Requisito: Explosão Encadeada]",
    "mestre das aptidoes": "**Mestre das Aptidões (12º Nível):** Você é um mestre no uso das aptidões amaldiçoadas, conseguindo reservar um pouco do seu potencial para elas. No começo de toda rodada, você recebe PE temporários igual a metade do seu Bônus de Treinamento, os quais podem ser utilizados exclusivamente no uso de Aptidões Amaldiçoadas. Estes pontos não podem acumular, mas são contabilizados separadamente de outros PEs temporários.",
    "versatilidade ampliada": "**Versatilidade Ampliada (12º Nível):** Ser versátil no uso dos próprios feitiços é uma grande vantagem, e você decide investir nela. Todos seus Feitiços recebem 1 variação de liberação e você pode escolher um deles para ter uma variação de cada nível que você possua acesso.",

    # --- 16º NÍVEL ---
    "manipulacao perfeita": "**Manipulação Perfeita (16º Nível):** Seu conhecimento sobre a manipulation de energia é melhorado, permitindo que você escolha uma quantidade de Feitiços igual ao seu bônus de treinamento para terem seu custo reduzido em um valor igual a metade dele. [Pré-Requisito: Dominância em Habilidade]",
    "sustentacao mestre": "**Sustentação Mestre (16º Nível):** Com o passar do tempo, você descobriu novas formas de como dispersar energia pelo seu corpo, conseguindo sustentar mais feitiços e com maior eficiência. Você pode manter três feitiços sustentados ao invés de dois. Além disso, seu custo para sustentar feitiços é diminuído em 1, com um mínimo de 1. [Pré-Requisito: Sustentação Avançada]",

    # ==========================================
    # CONTROLADOR
    # ==========================================
    # --- 2º NÍVEL ---
    "aceleracao": "**Aceleração (2º Nível):** Estimulando-as com seus comandos, você é capaz de forçar uma aceleração maior em invocações. Uma vez por rodada, você pode fazer com que uma Invocação se mova duas vezes ao invés de uma.",
    "camuflagem aprimorada": "**Camuflagem Aprimorada (2º Nível):** Você consegue se mesclar no meio das suas invocações, camuflando-se. Você pode, como uma Ação Comum, camuflar-se em meio as suas invocações adjacentes a você: para cada Invocação, todo ataque feito contra você tem 10% de chance de errar (1 em 1d10). Essa camuflagem dura até que não haja mais invocações adjacentes, e a chance de erro é diminuída conforme as invocações deixam de estar adjacentes.",
    "chamado destruidor": "**Chamado Destruidor (2º Nível):** Um acerto preciso de uma invocação incentiva as outras a acompanhar, como um chamado destrutivo. Quando uma das suas invocações conseguir um acerto crítico em uma ação de ataque você pode, como uma Ação Livre, pagar 2 PE para fazer com que uma das suas invocações adjacentes ataque o mesmo alvo que recebeu o crítico.",
    "companheiro amaldicoado": "**Companheiro Amaldiçoado (2º Nível):** Uma das suas invocações se torna seu companheiro, tornando-se mais capaz de ajudar. Escolha uma invocação sua: ela se torna o seu companheiro amaldiçoado. Uma vez por rodada, a invocação escolhida pode utilizar Apoiar como uma Ação Livre. Durante um descanso ou interlúdio, você pode alternar a invocação que é seu companheiro amaldiçoado, caso a invocação escolhida anteriormente tenha sido exorcizada.",
    "dor partilhada": "**Dor Partilhada (2º Nível):** Você e uma invocação conseguem criar um laço para partilhar dor, e isso pode acabar amenizando-a. Quando utilizar a ação Invocar, você pode escolher formar um laço com uma delas: caso você e a invocação escolhida com o laço fossem receber quantidades diferentes de dano de uma mesma habilidade em área, ambos recebem o menor entre os dois valores de dano.",
    "frenesi da invocacao": "**Frenesi da Invocação (2º Nível):** Você consegue fazer com que suas invocações se rendam a um frenesi brutal, mas arriscado. Uma vez por rodada, quando uma invocação realizar uma ação de ataque, você pode fazer com que ela realize essa ação duas vezes, ao invés de uma; com exceção de Ações com Custo. Mas, por uma rodada, ataques contra ela terão vantagem e ela terá a sua Defesa reduzida em 5 e -5 em testes de resistência.",
    "guarda viva": "**Guarda Viva (2º Nível):** Suas invocações atuam como uma guarda viva para você, auxiliando em sua defesa. Para cada Invocação que estiver dentro de 3 metros de você, sua Defesa aumenta em 1.",
    "invocacoes moveis": "**Invocações Móveis (2º Nível):** Você prepara suas invocações para se moverem com mais velocidade. O Deslocamento de todas suas Invocações aumenta em 1,5 metros. Nos níveis 6, 12 e 18 elas recebem +1,5 metros.",
    "invocacoes resistentes": "**Invocações Resistentes (2º Nível):** Você torna suas invocações mais resistentes, amplificando a vitalidade delas. Os Pontos de Vida Máximos de todas suas Invocações aumentam em um valor igual ao seu Bônus de Treinamento multiplicado por cinco.",
    "invocacoes treinadas": "**Invocações Treinadas (2º Nível):** Você faz com que suas invocações sejam mais aptas em habilidades. Todas suas Invocações se tornam treinadas em uma quantidade de Perícias adicional igual a metade do seu bônus de treinamento.",
    "melhoria de controlador": "**Melhoria de Controlador (2º Nível):** Estudando novas táticas e especializando-se em aspectos específicos, você aplica certas melhorias em todas suas invocações. Ao obter esta habilidade, escolha uma das quatro melhorias especificadas no final da especialização. Você pode pegar essa habilidade quatro vezes, uma para cada melhoria.",
    "otimizacao de energia": "**Otimização de Energia (2º Nível):** Você consegue otimizar o gasto de energia das habilidades mais exaustivas das suas invocações. Ao adquirir essa habilidade e em um descanso curto ou longo, você pode escolher uma habilidade com custo de cada invocação para ter esse custo reduzido em 1PE.",
    "proteger invocacao": "**Proteger Invocação (2º Nível):** Você sabe do valor das suas invocações, podendo até mesmo utilizar delas para sacrifícios em prol de si mesmas. Caso uma invocação sobre seu controle, dentro de um alcance igual a metade do Deslocamento de outra Invocação, vá receber dano suficiente para ser dissipada ou exorcizada, você pode gastar sua reação para fazer com que ela se mova até ficar adjacente a ela e receber esse dano por ela. Além disso, caso você esteja no alcance de ataque de uma invocação que foi atacada, você pode gastar sua reação também para reduzir o dano que ela receberá em um valor igual a Xd6 + seu modificador de Presença ou Sabedoria. X é igual ao seu bônus de treinamento.",
    "rede de deteccao": "**Rede de Detecção (2º Nível):** Juntamente das suas invocações, você se atenta e é auxiliado por elas para não perder nenhum detalhe. Para cada invocação dentro de 3 metros de você, você recebe +2 em rolagens de Percepção e seu valor de atenção aumenta em 2.",
    "tecnicas de combate controlador": "**Técnicas de Combate (2º Nível):** Você decide se versar em técnicas essenciais de combate, em busca de conseguir se defender em casos extremos. Você pode escolher duas armas quaisquer para se tornar treinado, caso não seja, e para poder utilizar Presença ou Sabedoria nas jogadas de ataque e dano enquanto as manejando.",
    "visionario": "**Visionário (2º Nível):** Você expande sua visão para a criação de invocações, conseguindo as conferir mais aspectos únicos. Sempre que for criar uma invocação, a quantidade de ações e/ou características que ela pode receber aumenta em um valor igual a metade do seu bônus de treinamento. Colocar ações e/ou características adicionais através desta habilidade ainda aumenta o custo da invocação normalmente.",

    # --- 4º NÍVEL ---
    "acao corretiva": "**Ação Corretiva (4º Nível):** Sempre atento ao campo de batalha, você consegue corrigir falhas de suas invocações. Quando uma invocação dentro de 9 metros de você realizar uma rolagem de perícia e obter um valor menor do que 10 no dado, você pode gastar 2 pontos de energia amaldiçoada para transformar o resultado em um 10.",
    "acompanhamento amaldicoado": "**Acompanhamento Amaldiçoado (4º Nível):** Uma das suas invocações pode ser colocada para o acompanhar de perto, reagindo aos seus golpes. Quando utilizar Invocar, você pode escolher uma das invocações para o acompanhar. Quando realizar um ataque contra uma criatura que esteja dentro do seu alcance e do alcance da Invocação, ela pode gastar uma Reação para utilizar uma ação de ataque ou auxílio, tendo como alvo você ou a criatura atacada.",
    "ataque em conjunto": "**Ataque em Conjunto (4º Nível):** Você consegue unificar seus comandos para fazer com que suas invocações ataquem em conjunto. Uma vez por rodada, como uma Ação Comum, você pode fazer com que todas as suas invocações ativas utilizem uma ação de ataque contra um mesmo alvo, pagando 2PE para cada invocação além da primeira. Para cada invocação participando do ataque em conjunto, todas recebem um bônus de +1 na jogada de ataque. Você pode, também, optar por participar do Ataque em Conjunto caso o alvo esteja no seu alcance. Você pode usar essa habilidade uma quantidade de vezes igual ao seu modificador de Sabedoria ou Presença por descanso longo.",
    "autonomia": "**Autonomia (4º Nível):** Assumindo uma abordagem diferente, você traz uma invocação a campo com autonomia, deixando-a agir de maneira independente enquanto foca em seu objetivo. Ao ativar uma invocação, você pode pagar uma quantidade adicional de PE igual a 2 para cada grau dela (2 para quarto grau, 10 para grau especial). Caso o faça, aquela invocação recebe um turno próprio dentro de combate, no qual ela pode realizar uma ação por turno, além de se mover, sem a necessidade de comandos. A invocação irá seguir o que você desejar que ela faça, além de ainda contar para o seu número de invocações ativas e poder realizar outros comandos feitos durante o seu turno.",
    "companheiro avancado": "**Companheiro Avançado (4º Nível):** O seu companheiro amaldiçoado se torna ainda mais avançado, conseguindo se versar em mais uma função, que é a de um aliado. Ao obter essa habilidade, o seu companheiro amaldiçoado se torna também um aliado de um tipo a sua escolha. Ele começa como um aliado iniciante. Os efeitos do companheiro como Aliado são aplicados a você ou ao aliado mais próximo da invocação, dentro de um alcance igual a metade do movimento dela. No nível 6 se torna um veterano e no nível 12 se torna um mestre. [Pré-Requisito: Companheiro Amaldiçoado]",
    "critico brutal": "**Crítico Brutal (4º Nível):** A brutalidade de um golpe bem encaixado por uma invocação é ampliada. Os acertos críticos da sua invocação causam 1 dado de dano adicional e, quando causar um crítico em uma criatura, você pode escolher diminuir o Deslocamento dela em um valor igual a 1,5 metros multiplicado pelo seu Bônus de Treinamento ou diminuir a Defesa dela em um valor igual a metade do seu Bônus de Treinamento. Qualquer um dos prejuízos dura até o começo do seu próximo turno.",
    "domador de maldicoes": "**Domador de Maldições (4º Nível):** Você se prepara para ser capaz de domar maldições com efetividade superior. Sempre que estiver no processo de domar uma maldição, você possui vantagem em todas as rolagens envolvidas no processo, além de poder anular sua primeira falha, tendo outra chance.",
    "invocacao as": "**Invocação Às (4º Nível):** Seu companheiro amaldiçoado se torna também a sua invocação às, capaz de o ajudar grandemente. Quando obter esta habilidade, a Invocação escolhida como companheiro amaldiçoado recebe os benefícios detalhados no final da especialização. [Pré-Requisito: Companheiro Amaldiçoado]",
    "invocacao parcial": "**Invocação Parcial (4º Nível):** Nem sempre é necessário trazer uma invocação por completo para se beneficiar de suas capacidades. Você pode utilizar de suas ações para realizar a ação de uma invocação que não esteja ativa; como uma ação comum, você utiliza uma ação complexa ou, como uma ação bônus, uma ação simples, de uma invocação a sua escolha.",
    "potencial superior": "**Potencial Superior (4º Nível):** Suas invocações possuem um potencial superior para desenvolver seus atributos. Todas suas invocações recebem 2 pontos de atributo adicionais por grau (2 para quatro grau, 10 para grau especial).",

    # --- 6º NÍVEL ---
    "combate em alcateia": "**Combate em Alcateia (6º Nível):** Você se torna parte da própria alcateia das suas invocações, golpeando com mais poder enquanto cercado delas. Enquanto manejando uma arma escolhida em Técnicas de Combate, você tem seu dano com ela aumentado em 1 nível para cada Invocação que esteja com a criatura no alcance de ataque dela. [Pré-Requisito: Técnicas de Combate e Apogeu - Controle Sintonizado.]",
    "concentrar poder": "**Concentrar Poder (6º Nível):** Priorizando qualidade acima de quantidade, você consegue concentrar o poder em uma única invocação. Enquanto estiver com apenas uma invocação em campo, você recebe benefícios de acordo com o seu nível de personagem, indicando o quanto a quantidade reduzida a aprimora. Você pode encontrar os benefícios e detalhes no final da especialização. [Pré-Requisito: Apogeu - Controle Concentrado]",
    "hoste amaldicoada": "**Hoste Amaldiçoada (6º Nível):** Você se foca em formar um exército de baixo nível. Ao utilizar Criar Horda, durante o processo de criação você pode escolher por reduzir o limite de grau do Líder em 1 para criar duas hordas ao invés de uma. As hordas criadas desta maneira contam como apenas uma para o seu limite de hordas em campo. [Pré-Requisito: Apogeu - Controle Disperso]",
    "invocacoes economicas": "**Invocações Econômicas (6º Nível):** Trazer algumas das suas invocações para o combate se torna mais econômico, permitindo-o trazê-las mais frequentemente quando retiradas. Você pode escolher duas invocações para terem o seu custo da invocação ou ativação reduzido em 2. No nível 12 você pode escolher mais uma, assim como no nível 18.",
    "protecao avancada de invocacao": "**Proteção Avançada de Invocação (6º Nível):** Aprofundando-se ainda mais em técnicas defensivas para suas invocações, você se torna mais capaz. Quando usar sua reação para receber dano por sua invocação, você receberá apenas metade do dano total. Além disso, a reação para reduzir dano normal tem seu valor aumentado para Xd8. Caso esteja adjacente a invocação você pode, ao invés do padrão, gastar 2 PE para utilizar o efeito como Ação Livre. [Pré-Requisito: Proteger Invocação.]",
    "taticas de alcateia": "**Táticas de Alcateia (6º Nível):** Caso tenha uma criatura agressiva sendo flanqueada por uma das suas invocações, a Defesa dela diminui em um valor igual a metade seu bônus de treinamento, e ele recebe uma penalidade em todos os testes de resistência com o mesmo valor.",

    # --- 8º NÍVEL ---
    "aptidoes de controle": "**Aptidões de Controle (8º Nível):** Você aprimora suas aptidões de energia necessárias para ser um mestre controlador. Ao obter esta habilidade, você pode aumentar o seu nível de aptidão em Aura, Controle e Leitura ou Barreira em 1. Você pode pegar esta habilidade três vezes, uma para cada aptidão.",
    "atacar e invocar": "**Atacar e Invocar (8º Nível):** Priorizando um combate próximo e em meio as suas invocações, você consegue trazê-las junto de um golpe. Quando você utilizar a ação Atacar, você pode gastar 2 PE para trazer uma invocação ao campo, considerando como se ela já estivesse presente para efeitos e uso de habilidades, como Acompanhamento Amaldiçoado.",
    "golpes ageis": "**Golpes Ágeis (8º Nível):** Seus ataques se tornam mais ágeis, visando permitir comandar as invocações e ainda assim atacar por si só. Uma vez por rodada, quando uma Invocação sua utilizar o efeito de Acompanhamento Amaldiçoado, você pode gastar 2PE para realizar um ataque armado ou desarmado adicional. [Pré-Requisito: Acompanhamento Amaldiçoado]",
    "tecnicas de oportunidade": "**Técnicas de Oportunidade (8º Nível):** Suas invocações se tornam aptas a novas técnicas de combate, encontrando boas oportunidades. Após obter essa habilidade, suas invocações passam a poder usar Ações de Ataque como uma reação, seguindo o mesmo gatilho de um ataque de oportunidade. Não é possível utilizar Ações com Custo como oportunidade.",

    # --- 10º NÍVEL ---
    "buchas de canhao": "**Buchas de Canhão (10º Nível):** Invocações de menor grau não possuem muito valor sozinhas, mas são ótimas para compor uma horda. Você não precisa mais pagar PEs adicionais para colocar invocações de quarto grau como membros de uma horda ou invocá-la.",
    "critico aprimorado": "**Crítico Aprimorado (10º Nível):** Um 19 se torna crítico também para suas invocações. Ao conseguir um crítico você pode, também, escolher entre os seguintes efeitos: diminuir o acerto do inimigo em um valor igual a metade do seu bônus de treinamento ou diminuir todas as RDs dele em um valor igual ao seu bônus de treinamento. Além disso, você escolhe dois efeitos ao invés de apenas um. [Pré-Requisito: Crítico Brutal.]",
    "flanco avancado": "**Flanco Avançado (10º Nível):** Você aprimora as técnicas de flanco das suas invocações, transformando-as em obstáculos ainda maiores para os inimigos. Caso tenha uma criatura agressiva dentro do alcance de ação de pelo menos duas de suas invocações, além de receber os efeitos da habilidade Táticas de Alcateia, sempre que essa criatura recebe um ataque, ela recebe 1d8 de dano adicional, aumentando em +1d8 para cada invocação além das duas primeiras. [Pré-Requisito: Táticas de Alcateia.]",
    "resistencia sobrecarregada": "**Resistência Sobrecarregada (10º Nível):** Você pode sobrecarregar a resistência das suas invocações a partir da sua própria energia amaldiçoada. Ao ativar ou invocar uma invocação, você pode gastar uma quantidade de PE igual a metade do seu bônus de treinamento e, para cada ponto gasto, a invocação tem seus pontos de vida aumentados em 10. [Pré-Requisito: Invocações Resistentes.]",

    # --- 16º NÍVEL ---
    "fantoche supremo": "**Fantoche Supremo (16º Nível):** Durante um descanso, você é capaz de reforçar o poderio de uma invocação que pareça que será essencial. Você pode, durante um descanso longo, escolher uma Invocação para ser o seu Fantoche Supremo, o qual recebe os seguintes benefícios: os pontos de vida da invocação aumentam em um valor igual ao seu bônus de treinamento multiplicado por cinco; a Defesa da invocação aumenta em um valor igual ao dobro do seu bônus de treinamento; o movimento da invocação aumenta em 4,5 metros e ela pode realizar uma ação complexa adicional todo turno. Porém, você só pode Invocar o seu fantoche supremo uma vez por descanso longo.",
    "mestre do controle": "**Mestre do Controle (16º Nível):** Você se torna um mestre do controle, levando suas técnicas ao limite. Uma vez por rodada você pode, como uma ação livre, gastar 2PE para fazer com que uma invocação sua se mova e realize uma ação complexa adicional.",

    # ==========================================
    # SUPORTE
    # ==========================================
    # --- 2º NÍVEL ---
    "amizade inquebravel": "**Amizade Inquebrável (2º Nível):** Escolha um Aliado Jogador. Este aliado é considerado permanentemente seu 'Amigo'. Ao terminar seu turno ao lado de seu Amigo, você pode como ação livre realizar a Ação 'Apoiar' no mesmo. Caso o Amigo morra, você só pode escolher outro amigo no próximo interlúdio.",
    "analise profunda": "**Análise Profunda (2º Nível):** Você consegue analisar profundamente um inimigo, deduzindo aspectos dele. Você pode gastar 1 ponto de energia amaldiçoada para, como uma ação comum, analisar uma criatura, realizando uma rolagem de Percepção com CD igual a 15 + ND da criatura. Caso você suceda, você descobre uma característica dela (pontos de vida, bônus em perícia ou ataque, por exemplo). Para cada 5 pontos excedentes no resultado do teste, você descobre uma característica adicional. Você só pode usar essa habilidade uma vez em cada criatura, por cena.",
    "apoio avancado": "**Apoio Avançado (2º Nível):** Ao utilizar a ação de Apoiar, você pode fortalecer seu apoio com um efeito à sua escolha, com as possibilidades listadas no final da especialização.",
    "comando motivador": "**Comando Motivador (2º Nível):** Sua presença é motivadora, e o mesmo vale para um comando dado por você. Como uma ação livre, você pode falar um comando para um aliado e gastar 2 pontos de energia amaldiçoada para que, quando o aliado realize a ação comandada, ele receba um bônus igual ao seu bônus de treinamento na rolagem usada na ação.",
    "conceder outra chance": "**Conceder Outra Chance (2º Nível):** Você pode conceder a um aliado outra chance em um teste no qual ele falhou. Ao ver um aliado dentro de 6 metros falhar em um teste, você pode gastar 3 pontos de energia amaldiçoada para fazer com que ele role novamente, ficando com o melhor resultado. Você pode utilizar essa habilidade uma quantidade de vezes igual ao seu bônus de treinamento, por descanso longo; em um descanso curto, você recupera metade dos usos.",
    "desvendar terreno": "**Desvendar Terreno (2º Nível):** Você consegue compreender e destrinchar o ambiente ao seu redor, encontrando pontos de vantagem no terreno. Como uma Ação de Movimento, realize um teste de Percepção com CD definida pelo Narrador e, caso suceda, você percebe pontos estratégicos sobre ele e, até o final da cena, recebe um bônus igual ao seu bônus de treinamento em testes de Percepção que envolvam procurar e encontrar coisas ou pessoas no terreno analisado.",
    "expandir repertorio": "**Expandir Repertório (2º Nível):** Estudando para se tornar mais versátil, você consegue dominar outros campos de estudos. Você se torna treinado em uma quantidade de perícias igual a metade do seu bônus de treinamento. Você recebe também um bônus de +2 em uma perícia qualquer.",
    "mobilidade avancada": "**Mobilidade Avançada (2º Nível):** Em prol de alcançar mais rapidamente o lugar onde seu suporte é requisitado você recebe um bônus de +3 metros em seu movimento. Além disso, caso um aliado caia nas portas da morte, você pode, como uma reação, mover-se metade do seu movimento na direção dele.",
    "otimizacao de espaco": "**Otimização de Espaço (2º Nível):** Você organiza melhor o seu inventário e o seu espaço. Você recebe espaços de item adicionais no seu inventário, em um valor igual ao seu bônus de treinamento.",
    "pronto para agir": "**Pronto para Agir (2º Nível):** Você adiciona seu modificador de Presença a Iniciativa. Além disso, seus aliados recebem um bônus igual a metade do modificador.",
    "protetor": "**Protetor (2º Nível):** Quando um aliado dentro de 1,5m de você é atacado, você pode gastar 1 PE para, como uma Ação Livre, diminuir o dano causado no ataque feito contra ele em Xd10 + seu modificador de Presença ou sabedoria, onde X é igual ao seu bônus de treinamento. É necessário estar com um escudo equipado para utilizar esta habilidade.",
    "tecnicas de combate suporte": "**Técnicas de Combate (2º Nível):** Você decide se versar em técnicas essenciais de combate, em busca de conseguir se defender em casos extremos. Você pode escolher duas armas quaisquer para se tornar treinado, caso não seja, e para poder utilizar Presença ou Sabedoria nas jogadas de ataque e dano enquanto as manejando.",
    "transmitir conhecimento": "**Transmitir Conhecimento (2º Nível):** Durante um descanso, você pode transmitir conhecimento para seus aliados, preparando-os. Durante um descanso curto, você pode conceder treinamento temporário em perícias com as quais você seja treinado para seus aliados, com um limite igual a metade do seu bônus de treinamento. Durante um descanso longo, essa quantidade é igual a bônus de treinamento.",

    # --- 4º NÍVEL ---
    "apoios versateis": "**Apoios Versáteis (4º Nível):** Ao obter esta habilidade, você aprende um apoio avançado adicional. No 10º nível você recebe outro apoio avançado.",
    "guarda sincronizada": "**Guarda Sincronizada (4º Nível):** Um cuida do outro e, mantendo essa mentalidade, você consegue estabelecer uma guarda em sintonia com seus aliados próximos. Você pode utilizar uma Ação Bônus para sintonizar a guarda de todos seus aliados dentro de 7,5 metros que possam te ver ou ouvir: para cada aliado dentro do alcance, todos os outros recebem +1 na Defesa.",
    "inspirar aliados": "**Inspirar Aliados (4º Nível):** Você sabe como dar a inspiração necessária para os seus aliados. Uma vez por cena, você pode gastar 1 ponto de energia amaldiçoada e usar sua ação bônus para inspirar uma quantidade de aliados igual a metade do seu bônus de treinamento. Uma quantidade de vezes igual ao seu modificador de presença ou sabedoria, dentro de 10 minutos, esses aliados podem escolher adicionar 2d3 em uma jogada de ataque, teste de habilidade ou teste de resistência, mas apenas uma vez por teste.",
    "intervencao": "**Intervenção (4º Nível):** Intervindo rapidamente para impedir uma aflição pior, você é capaz de remover condições antes que elas se acentuem. Como uma Ação Comum, você pode gastar 3 PE para encerrar uma condição fraca afetando um aliado dentro de alcance de toque. Nos níveis 6, 12 e 18 você se torna capaz de encerrar condições médias, fortes e extremas respectivamente, com o custo em PE aumentando em 3 para cada nível superior a fraca.",
    "negacao critica": "**Negação Crítica (4º Nível):** Você é capaz de negar uma falha crítica dos seus aliados, impedindo o pior de acontecer. Uma quantidade de vezes igual a 1 + metade do seu bônus de treinamento, por cena, você pode pagar 3 PE para negar uma falha crítica que você possa ver dentro de 12 metros.",
    "no ultimo segundo": "**No Último Segundo (4º Nível):** Ao iniciar uma rodada com um ou mais aliados com 2 fracassos nos testes da porta da morte, aumente sua iniciativa atual em combate em +5. Caso você aja primeiro que um dos seus aliados nas portas da morte por causa deste bônus de iniciativa, você anula terreno difícil, tem seu movimento aumentado em 4,5m e recebe +5 de Defesa contra Ataques de Oportunidade durante a rodada.",
    "pre analise": "**Pré-Análise (4º Nível):** Você inconscientemente analisa o território a sua volta, sendo assim você não pode ser surpreendido e seu valor de atenção recebe um bônus de +5. Você pode escolher um aliado para não ser surpreendido. [Pré-Requisito: Treinado em Percepção]",
    "recompensa pelo sucesso": "**Recompensa pelo Sucesso (4º Nível):** Você recompensa aqueles que você comanda, com um sucesso mais difícil sendo extremamente gratificante. Ao utilizar Comando Motivador, você pode escolher reduzir o bônus fornecido por ela pela metade e, caso o aliado motivado ainda assim consiga suceder, ele ganha 2 PE. [Pré-Requisito: Comando Motivador]",
    "sintonizacao vital": "**Sintonização Vital (4º Nível):** Quando curar um aliado, você pode gastar 3 pontos de energia amaldiçoada para que outra criatura dentro de 3 metros (incluindo você) recupere uma quantidade de pontos de vida igual a metade da cura original.",

    # --- 6º NÍVEL ---
    "contra ataque": "**Contra-Ataque (6º Nível):** Uma quantidade de vezes igual ao dobro do seu modificador de Presença ou Sabedoria, por descanso curto ou longo, você pode, como uma reação, gastar 1 ponto de energia amaldiçoada para aumentar a Defesa de um aliado em um valor igual ao seu bônus de treinamento e, se você fizer com que um ataque que iria acertar se torne um erro, você ou o aliado protegido podem pagar 1 ponto de energia amaldiçoada para realizar um ataque contra o inimigo.",
    "cura avancada em grupo": "**Cura Avançada em Grupo (6º Nível):** Você pode usar sua habilidade de cura em grupo: quando a utilizar em um alvo, você pode pagar 2 pontos de energia amaldiçoada para curar mais um alvo, com um limite igual ao seu bônus de treinamento.",
    "devolver na mesma moeda": "**Devolver na Mesma Moeda (6º Nível):** Quando um aliado que você possa ver é afetado por uma condição, você pode gastar 2 PE para, como uma Ação Livre, fazer com que o próximo teste de resistência realizado por um inimigo para evitar uma condição do aliado possua desvantagem.",
    "disseminar cura": "**Disseminar Cura (6º Nível):** Ao utilizar um Feitiço de cura, você pode escolher um alvo adicional, gastando uma quantidade de PE igual ao nível da técnica adicional.",
    "incitar vigor": "**Incitar Vigor (6º Nível):** Você é capaz de utilizar de processos para incitar o vigor em uma criatura, puxando de seu potencial latente. Como uma ação bônus, você pode gastar 3 pontos de energia para fazer com que uma criatura a alcance de toque possa gastar seus dados de vida para se curar.",
    "inimigo comum": "**Inimigo Comum (6º Nível):** Você pode gastar 2 pontos de energia amaldiçoada para, como uma ação bônus, escolher um inimigo comum entre uma quantidade de pessoas igual ao seu modificador de Presença ou sabedoria. Sempre que uma pessoa atacar o inimigo em comum, adiciona-se metade do seu bônus de Presença ou sabedoria na rolagem de acerto e o modificador inteiro nas rolagens de dano. Caso uma das pessoas escolhida ataque uma criatura que não for o inimigo comum, e o inimigo comum estiver vivo, ela para de receber os bônus.",
    "posicionamento estrategico": "**Posicionamento Estratégico (6º Nível):** Em certos momentos, você não precisa se mover, mas outros se beneficiariam de um melhor posicionamento. Durante o seu turno, você pode deixar de se mover, para permitir que um dos seus aliados se mova, como Ação Livre.",

    # --- 8º NÍVEL ---
    "aptidoes de suporte": "**Aptidões de Suporte (8º Nível):** Você aprimora suas aptidões de energia necessárias para ser um grande suporte. Ao obter esta habilidade, você pode aumentar o seu nível de aptidão em Aura, Controle e Leitura ou Energia Reversa em 1. Você pode pegar esta habilidade três vezes, uma para cada aptidão.",
    "contaminar com determinacao": "**Contaminar com Determinação (8º Nível):** Uma vez por cena, você pode gastar 4 pontos de energia amaldiçoada para, como uma ação comum, fazer com que você e dois aliados recebam vantagem em todo teste de resistência por duas rodadas. Você pode fazer com que mais aliados recebam vantagem, mas para cada aliado a mais, o custo da habilidade aumenta em 2 pontos de energia.",
    "criar medicina": "**Criar Medicina (8º Nível):** Nem sempre é possível estar próximo aos seus aliados, então você desenvolve uma técnica para criar remédios portáteis. Durante um descanso curto, você pode escolher recuperar 2 pontos de energia a menos para criar uma quantidade de remédios igual a metade do seu bônus de treinamento; em um descanso longo, a quantidade é igual ao seu bônus de treinamento e você recupera 4 pontos de energia a menos. Um remédio cura em um valor igual a sua cura da habilidade Suporte em Combate, dura 1 dia e consome uma ação comum para ser usado. [Pré-Requisito: Treinado em Ferramentas de Médico]",
    "cura aperfeicoada": "**Cura Aperfeiçoada (8º Nível):** Sua cura é quase perfeita em sua consistência. Caso você tire 1 ou 2 em um dado de cura, você pode escolher rolar novamente o dado, ficando com o melhor resultado.",
    "elevar sucesso": "**Elevar Sucesso (8º Nível):** Como um suporte, você consegue elevar a tentativa de resistência de um aliado. Quando um aliado dentro de 4,5 metros suceder em um teste de resistência você pode, como uma reação, gastar 2PE para somar +5 ao resultado do teste dele, com a possibilidade de se tornar um sucesso crítico.",
    "fisico controlado": "**Físico Controlado (8º Nível):** Você controla o seu físico a partir dos conhecimentos médicos e da energia amaldiçoada. Você passa a somar seu modificador de presença ou de sabedoria, ao invés de constituição, nos pontos de vida, mas com um limite de +4. Ao adquirir essa habilidade, você calcula novamente a sua vida, levando em conta a alteração do atributo usado. [Pré-Requisito: Treinado em Fortitude]",
    "motivacao pelo triunfo": "**Motivação pelo Triunfo (8º Nível):** Neutralizar um dos inimigos incentiva você e seus aliados a continuarem lutando, independente de quem o tenha eliminado. Quando um inimigo tem seus pontos de vida reduzidos a 0 ou é morto por você ou um dos aliados presentes na cena, você pode conceder uma quantidade de pontos de vida temporários igual ao dobro do seu nível de Suporte para todos os aliados que tenham causado dano nesse inimigo. Caso o inimigo seja um Lacaio, essa quantidade é reduzida pela metade.",
    "pressao do medico": "**Pressão do Médico (8º Nível):** Ao entrar nas portas da morte, você não fica inconsciente. Ao invés de não agir, você pode tentar se estabilizar sozinho com CD aumentada em +10, porém ao fazer isso, você recebe uma falha nos testes de morte. [Pré-Requisito: Mestre em Medicina]",
    "sustentacao avancada suporte": "**Sustentação Avançada (8º Nível):** Seu corpo agora é capaz de dividir a liberação de energia entre dois feitiços diferentes. Você pode manter um feitiço sustentado adicional e, no começo do combate, pode ativar um feitiço sustentado à sua escolha como Ação Livre, desde que ele possua um custo de Ação Bônus ou inferior.",

    # --- 10º NÍVEL ---
    "descarga reanimadora": "**Descarga Reanimadora (10º Nível):** Você descobriu uma técnica para descarregar energia reversa de maneira a reanimar imediatamente alguém caído. Caso haja um aliado nas portas da morte, dentro do seu alcance de toque, você pode usar uma Ação Completa e gastar 10 pontos de energia amaldiçoada para o estabilizar imediatamente, independente de quanta vida negativa ele tenha, e recupere pontos de vida igual a uma rolagem da sua cura de Suporte em Combate. Se o turno dele já tiver passado e ele não ter agido por estar nas portas da morte, ele pode realizar o turno imediatamente após o seu. [Pré-Requisito: Aptidão Cura Amplificada]",
    "necessidade de continuar": "**Necessidade de Continuar (10º Nível):** Para você, continuar presente no campo de batalha é mais do que uma necessidade, pois você é o suporte necessário. Quatro vezes por cena, se você estiver com menos da metade da sua vida máxima, você recebe um valor de pontos de vida temporários igual ao seu bônus da perícia Medicina + seu modificador de Presença ou Sabedoria, no começo do seu turno. [Pré-Requisito: Treinado em Vontade]",
    "olhar agucado": "**Olhar Aguçado (10º Nível):** Seus olhos são treinados para encontrar os pontos fracos dos inimigos: você pode gastar 2 pontos de energia amaldiçoada e usar sua ação bônus para analisar um inimigo, descobrindo onde é melhor o acertar, fazendo com que o primeiro ataque de todo aliado cause dano adicional igual ao seu bônus de treinamento multiplicado por 5. Você só pode usar essa habilidade duas vezes por criatura. [Pré-Requisito: Treinado em Percepção]",
    "taticas defensivas": "**Táticas Defensivas (10º Nível):** Você pode escolher um tipo de dano Elemental para que você e dois aliados sejam resistentes. Em um descanso longo, você pode trocar esses tipos de dano e os aliados recebendo o benefício.",

    # --- 12º NÍVEL ---
    "ajustes em equipamento": "**Ajustes em Equipamento (12º Nível):** Você se torna capaz de fazer ajustes nos equipamentos dos seus aliados, durante um tempo de descanso. Durante um descanso curto, você pode escolher uma quantidade de equipamentos igual ao seu Bônus de Treinamento, os quais recebem o efeito de um Encantamento que não possuam e atendam aos requisitos. Durante um Descanso Longo, essa quantidade se torna o dobro do seu Bônus de Treinamento. O efeito dos Encantamentos fica ativo até o próximo descanso. [Pré-Requisito: Treinado em Ferramentas de Ferreiro]",
    "interferencia": "**Interferência (12º Nível):** Você se torna capaz de interferir nas ações dos inimigos. Como uma reação, você pode gastar 2 pontos de energia amaldiçoada para forçar um inimigo dentro de 9 metros a rolar novamente um teste, ficando com o menor resultado. Além disso, após usar essa habilidade você pode conceder a um aliado dentro de 4,5 metros vantagem na próxima rolagem dele.",
    "nao desista": "**Não Desista! (12º Nível):** Ao ver um aliado atingir 0 ou menos de vida ao receber dano, você pode, gastando 3 de PE, fazer um teste de Persuasão contra a CD de estabilização. Caso você passe, o aliado continua de pé e não entra nas portas da morte, ficando com 0 de vida ao invés do normal, durante uma rodada. Enquanto essa rodada durar, a vida necessária para ele cair nas portas da morte se torna -100 ou a vida máxima negativa, o que for menor. Se a rodada acabar e ele ainda estiver com 0 de vida ou menos, ele cairá nas portas da morte, recebendo 1 falha. Caso o aliado possua uma habilidade que permita o mesmo continuar agindo mesmo depois de bater 0, como 'Mesmo Morto' ou 'Potência Antes de Cair', ao invés disso, você anula o efeito negativo das habilidades. Esta habilidade pode ser utilizada para negar efeitos negativos de habilidades apenas uma quantidade de vezes igual a metade do seu bônus de treinamento.",
    "sobrecura": "**Sobrecura (12º Nível):** Ao curar um aliado você pode fazer com que essa cura supere o máximo de vida dele: caso ele fique com o máximo de vida por meio da sua cura, ele recebe o dobro do excedente como vida temporária, com um limite igual ao dobro do seu nível de suporte. Você pode, também, escolher conceder 5 multiplicado por seu modificador de Presença ou Sabedoria de Vida Temporária a alguém que já esteja com a vida completa com um uso da sua cura.",
    "reacao necessaria": "**Reação Necessária (12º Nível):** Você sabe que, em certos momentos, sua reação é necessária, mesmo que isso signifique ir além do esperado. Uma vez por rodada, caso não possua uma reação, você pode gastar 3 pontos de energia amaldiçoada para realizar uma reação adicional.",

    # --- 14º NÍVEL ---
    "apoio abrangente": "**Apoio Abrangente (14º Nível):** Você é capaz de apoiar e melhorar isso de maneira mais abrangente. Quando utilizar Apoio Avançado, você pode colocar dois efeitos ao invés de um só. [Pré-Requisito: Apoio Avançado]",

    # --- 16º NÍVEL ---
    "purificacao da alma": "**Purificação da Alma (16º Nível):** Suas capacidades se tornaram tão grandes que você inconscientemente se tornou ciente do traçado de uma alma, assim podendo curar diretamente as almas das pessoas. Uma quantidade de vezes igual ao seu modificador de presença você pode restaurar a integridade de alguém em 50%. E, além disso, você domina ainda mais as técnicas de cura: o seu Bônus de Treinamento é adicionado ao número de usos da sua cura.",
    "sustentacao mestre suporte": "**Sustentação Mestre (16º Nível):** Com o passar do tempo, você descobriu novas formas de como dispersar energia pelo seu corpo, conseguindo sustentar mais feitiços e com maior eficiência. Você pode manter três feitiços sustentados ao invés de dois. Além disso, seu custo para sustentar feitiços é diminuído em 1, com um mínimo de 1. [Pré-Requisito: Sustentação Avançada]",
    
    # ==========================================
    # RESTRINGIDO
    # ==========================================
    # --- 2º NÍVEL ---
    "ataque inconsequente restringido": "**Ataque Inconsequente (2º Nível):** Uma vez por rodada, ao realizar um ataque, você pode escolher atacar inconsequentemente: Você recebe vantagem na jogada de ataque e +5 na rolagem de dano dele. Porém, ao realizar um golpe inconsequente você fica Desprevenido por 1 rodada.",
    "apropriar se restringido": "**Apropriar-se (2º Nível):** Você recebe um bônus de +3 em testes para Desarmar ou evitar ser desarmado.",
    "aproximacao instintiva restringido": "**Aproximação Instintiva (2º Nível):** Quando um inimigo termina o turno dentro de uma distância igual a metade do seu deslocamento você pode, como uma ação livre, se mover até metade do seu movimento para um espaço mais próximo do inimigo. Essa movimentação não causa ataques de oportunidade e ignora terreno difícil. Caso, com essa movimentação, a criatura acabe em seu alcance de ataque, você pode gastar 2 pontos de estamina para realizar uma manobra contra ela.",
    "existencia imperceptivel restringido": "**Existência Imperceptível (2º Nível):** Com níveis mínimos de energia, você sabe como se esconder e tornar sua existência em algo imperceptível. Você recebe um bônus de +2 em rolagens de Furtividade. Além disso, sua penalidade em Furtividade por atacar e fazer outras ações chamativas é reduzida para -4.",
    "finta melhorada restringido": "**Finta Melhorada (2º Nível):** Você encontra uma maneira de desenvolver a finta, sendo mais difícil prever seu próximo movimento. Você passa a poder somar o seu Modificador de Destreza, ao invés de Presença, em rolagens de Enganação para fintar. Além disso, acertar um inimigo desprevenido pela sua finta causa um dado de dano adicional.",
    "golpe impactante restringido": "**Golpe Impactante (2º Nível):** Seu primeiro golpe encaixado é acompanhado de um grande impacto. Uma vez por rodada, ao realizar um ataque corpo a corpo contra um alvo, você pode também, como parte do mesmo ataque, realizar a ação de Empurrar contra o mesmo alvo. Caso tenha sucesso em empurrar, ele recebe Xd6 de dano adicional, onde X é igual a metade do seu modificador de Força.",
    "imitacao restringido": "**Imitação (2º Nível):** Você consegue imitar técnicas e estilos de combate de outras pessoas, desde que tal não dependa da energia amaldiçoada. Ao ver uma habilidade ativa de especialização marcial, manobra ou postura, você pode escolher a copiar como uma reação, e deve a usar no seu próximo turno, ou perderá a cópia. Você só pode manter uma coisa copiada por vez, e só usa uma vez cada uma delas. Porém, quando copiar algo, você pode tentar aprender aquilo, realizando um teste de percepção com CD35, a qual diminui em 2 para cada vez que você copiar a mesma habilidade e tentar a aprender. Se suceder em aprender, você não precisa ver alguém a usando para poder copiar, necessitando de uma ação bônus, e a quantidade de usos se torna a quantidade padrão da habilidade, ao invés de uma só. Você pode aprender uma habilidade ativa e uma postura ou manobra; durante um interlúdio você pode escolher trocar uma habilidade aprendida por outra que possa ver durante o interlúdio, tentando a copiar com o teste de percepção, o qual é feito com vantagem. Caso o que for copiado gaste energia amaldiçoada, você paga o custo em pontos de estamina.",
    "manejo superior restringido": "**Manejo Superior (2º Nível):** Você sabe manejar armas como ninguém, extraindo seu máximo. O dano de toda arma que você manejar conta como um nível acima e suas rolagens de dano recebem um bônus igual ao seu bônus de treinamento.",
    "roubo de habilidade restringido": "**Roubo de Habilidade (2º Nível):** Em busca de se adaptar, você consegue até mesmo roubar as habilidades dos outros. Ao obter essa habilidade, você pode aprender uma habilidade de Especialista em Combate ou Lutador, desde que tal não dependa do uso de energia amaldiçoada. Você usa seus níveis de Restringido para os requisitos. Você pode pegar essa habilidade uma quantidade de vezes igual ao seu bônus de treinamento, roubando habilidades diferentes. Você não pode roubar habilidades base das outras especializações, exceto Golpe Especial.",
    "surto de adrenalina restringido": "**Surto de Adrenalina (2º Nível):** Como uma ação livre, você pode gastar 3 pontos de estamina para entrar em um estado onde seu corpo está no limite. Enquanto em um surto de adrenalina, você recebe redução de dano a todos os tipos de dano igual a metade do seu nível de personagem, um bônus igual a 1 + metade do seu bônus de treinamento em testes de resistência de fortitude e reflexos, e um bônus em percepção igual ao seu bônus de treinamento. Um surto dura uma rodada, e você pode gastar 1 ponto de estamina adicional para cada rodada após a primeira que deseje o manter ativo.",
    "valorizar invocacao restringido": "**Valorizar Invocação (2º Nível):** Tendo domado maldições, elas se tornam invocações úteis dentro de combate, e você passa a valorizar elas quando necessário. Caso uma das suas invocações dentro de 3 metros vá ser exorcizada, você pode gastar 1 ponto de estamina e usar sua reação para se colocar a frente dela, recebendo o golpe letal em troca de manter a invocação viva. Caso vá defender uma invocação, você recebe pontos de vida temporários igual ao seu nível de personagem.",

    # --- 4º NÍVEL ---
    "acao agil restringido": "**Ação Ágil (4º Nível):** Você otimiza o seu tempo de ação. Uma vez por turno você pode gastar 2 PE para receber uma Ação Ágil, a qual pode ser utilizada para: Andar, Desengajar ou Esconder.",
    "adrenalina intensificadora restringido": "**Adrenalina Intensificadora (4º Nível):** Sua adrenalina também intensifica o seu corpo e as suas capacidades. Ao entrar em um surto de adrenalina, você pode escolher pagar 2 pontos de estamina adicionais para poder distribuir um bônus de +4 entre as perícias de Atletismo e Acrobacia, da maneira que desejar (+3 em uma e +1 em outra, por exemplo), além de poder pagar 1 ponto de estamina para se conceder vantagem em uma rolagem de Atletismo e Acrobacia, uma vez por cena cada. Ao obter a Restrição Definitiva, o bônus de +4 se torna +8.",
    "cacador de feiticeiros restringido": "**Caçador de Feiticeiros (4º Nível):** Sua especialização é conseguir lidar com feiticeiros, preparando-se para os caçar, tanto resistindo melhor quanto destruindo melhor. No começo de uma cena você pode gastar 2 pontos de estamina para receber 2 de RD, +1 em testes de resistência e ataques, além de causar +1d6 de dano contra todos os feiticeiros presentes na cena. A cada 5 níveis você pode gastar mais 2 pontos para aumentar os bônus; +2 de RD, +1 de bônus e +1d6 de dano para cada 2 pontos adicionais.",
    "desenvolver ideias restringido": "**Desenvolver Ideias (4º Nível):** Você tem uma percepção de como desenvolver as suas ideias de técnicas marciais e manobras, expandindo o seu repertório. Você recebe duas técnicas marciais adicionais ao obter essa habilidade.",
    "foco no inimigo restringido": "**Foco no Inimigo (4º Nível):** Ao iniciar um combate, você pode gastar 2 pontos de estamina e escolher um inimigo para ser seu foco. Ao atacar o inimigo que é seu foco você recebe um bônus de +2 para acertar e causa 1d6 de dano a mais, que aumenta para 1d8 no nível 6, 1d10 no nível 12 e 1d12 no nível 16, além de receber +5 em testes de Percepção para procurar o inimigo e em sua Atenção contra ele. Ao matar o inimigo em que você possui foco, você pode usar sua reação para passar o foco para outro inimigo dentro de 9 metros de você. Caso ataque outra criatura que não seja seu foco, a habilidade se encerra.",
    "ponto cego restringido": "**Ponto Cego (4º Nível):** Você consegue sempre perceber um ponto cego na guarda do inimigo, se posicionando em tal. Se mover pelo espaço de um inimigo não conta como terreno difícil, e sempre que você estiver no espaço de um inimigo, você recebe camuflagem leve, fazendo com que ataques contra você tenham 20% de chance de falhar (1 ou 2 em 1d10). A partir do 10º nível, você pode realizar uma rolagem de furtividade contra um alvo o qual esteja dentro do espaço dele; caso seu resultado seja superior ao valor de atenção dele, você passa a receber uma camuflagem total, fazendo com que seus ataques tenham 40% de chance de falhar (1 a 4 em 1d10).",
    "resiliencia pela adrenalina restringido": "**Resiliência pela Adrenalina (4º Nível):** A adrenalina pulsando no seu corpo o deixa mais resiliente e resistente. Sempre que você realizar um teste de resistência durante um Surto de Adrenalina, você pode pagar 1 ponto de estamina para adicionar 2d3 ao resultado. Caso seja um teste em que você não seja treinado, e se você falhar, você pode rolar novamente. [Pré-Requisito: Surto de Adrenalina]",
    "tecnicas de memorizacao restringido": "**Técnicas de Memorização (4º Nível):** Você estuda e se versa em uma maneira de conseguir memorizar uma quantidade maior de fatores. Ao obter essa habilidade, você pode aprender uma habilidade adicional a partir da Imitação. Caso tenha a habilidade Imitação Perfeita, você pode aprender mais uma habilidade adicional. [Pré-Requisito: Imitação]",

    # --- 6º NÍVEL ---
    "aprimoramento celeste restringido": "**Aprimoramento Celeste (6º Nível):** Você passa a somar metade do modificador do seu atributo chave em sua CD de Especialização.",
    "ataque extra restringido": "**Ataque Extra (6º Nível):** Você consegue atacar mais rápido, otimizando seus golpes. Ao realizar a ação Atacar, você pode gastar 2 pontos de estamina para atacar duas vezes ao invés de uma.",
    "ataque inconsequente aprimorado restringido": "**Ataque Inconsequente Aprimorado (6º Nível):** O bônus em dano ao usar o ataque inconsequente aumenta para +10 e, ao utilizar a habilidade, você recebe 2d6+4 pontos de vida temporária. [Pré-Requisito: Ataque Inconsequente]",
    "corpo de aco restringido": "**Corpo de Aço (6º Nível):** Seu corpo é tão duro quanto o aço e não se curva, mantendo sua integridade. Seus pontos de vida máximos aumentam em um valor igual ao seu valor de Constituição, e você pode pagar 2 pontos de estamina para, durante uma cena, se curar em um valor igual a 2d8 + seu modificador de constituição no começo de todo turno seu. No nível 10, você pode pagar 1 ponto de estamina adicional para aumentar a cura em 1d8, assim como pode pagar mais 1 ponto no nível 15 para aumentar novamente.",
    "corredor fantasma restringido": "**Corredor Fantasma (6º Nível):** Ao se mover, você pode utilizar o movimento para andar em paredes, no entanto, não pode terminar seu turno em uma. Caso termine, você cai, respeitando as regras de queda. Você recebe um bônus de +2 em testes para reduzir dano de queda. Caso possua a dádiva Agilidade Exímia, você pode correr em tetos.",
    "disparada trovejante restringido": "**Disparada Trovejante (6º Nível):** Você consegue usar da sua agilidade para disparar como um trovão em reação a um golpe. Ao receber um ataque corpo-a-corpo, você pode gastar 3 pontos de estamina para reduzir o dano a metade e se mover até 4,5 metros para longe do atacante.",
    "frenesi restringido": "**Frenesi (6º Nível):** Durante o Surto de Adrenalina, você assume um frenesi intenso que aumenta o potencial ofensivo dos seus golpes: sempre que realizar um ataque, ele causa +4 de dano adicional. No 12º nível, esse bônus se torna +8, no 16º nível ele se torna +12. [Pré-Requisito: Surto de Adrenalina]",
    "movimento reativo restringido": "**Movimento Reativo (6º Nível):** Uma vez por rodada, quando um oponente dentro de um alcance igual ao seu movimento iniciar a realização de uma ação que permitiria o uso de um ataque de oportunidade, você pode gastar 2 pontos de estamina para se locomover até ele com uma ação livre, e então gastar sua reação para executar o ataque de oportunidade.",

    # --- 8º NÍVEL ---
    "ainda de pe restringido": "**Ainda de Pé (8º Nível):** Uma vez por descanso curto ou longo, quando você for chegar a 0 pontos de vida e cair você pode escolher se manter de pé e curar em 3d10 + nível de personagem, aumentando em +1d10 nos níveis 12, 16 e 20. Caso o dano fosse suficiente para ser uma morte instantânea, você apenas resiste e fica com 1 de vida, caindo com uma falha no próximo dano que receber. Se você morrer, você morre de pé.",
    "arremetida encoberta restringido": "**Arremetida Encoberta (8º Nível):** Ao realizar o Ataque Furtivo da rodada, você recebe vantagem no golpe. Caso o acerto dele já tenha sido garantido por qualquer motivo, você recebe +1d no dano do Ataque Furtivo.",
    "barreira inamovivel restringido": "**Barreira Inamovível (8º Nível):** Sempre que você fizer um teste de resistência de Fortitude e o resultado natural do dado for menor do que seu modificador de Constituição, você pode gastar 2 pontos de estamina para transformar o resultado natural do dado no seu modificador de Constituição. Você não pode ser movido a força e tem vantagem para resistir a ser agarrado.",
    "forca imparavel restringido": "**Força Imparável (8º Nível):** Sempre que você fizer um TR de Reflexos e o resultado natural do dado for menor do que seu modificador de Destreza, você pode gastar 2 pontos de estamina para transformar o resultado natural do dado no seu modificador de Destreza. Você se torna treinado em um teste de resistência à sua escolha e mestre em outro TR no qual já seja treinado.",
    "imitacao perfeita restringido": "**Imitação Perfeita (8º Nível):** Você desenvolve a habilidade de imitação. Você se torna capaz de copiar habilidades passivas de especializações marciais e estilos de combate. Ao copiá-las, o efeito dura até o final do seu próximo turno. Você passa a poder aprender também uma habilidade passiva e um estilo de combate, mas é mais difícil, por ser algo sutil; a CD é igual a 40, e continua diminuindo em 2 por tentativa na mesma habilidade. [Pré-Requisito: Imitação]",
    "presenca ameacadora restringido": "**Presença Ameaçadora (8º Nível):** Sua mera presença é ameaçadora, de tão poderoso você se mostra, mesmo sem energia amaldiçoada. Você pode gastar 1 ponto de estamina para demarcar a sua presença, fazendo com que toda criatura que consiga o ver realize um teste de resistência de vontade. Em uma falha, a criatura fica amedrontada por 2 rodadas, em um sucesso, fica abalada. Você só pode usar essa habilidade uma vez por cena em cada criatura.",
    "reacao rapida restringido": "**Reação Rápida (8º Nível):** Com um tempo de reação grandemente desenvolvido, você consegue incitar o seu corpo a reagir com uma rapidez extrema. Caso já tenha gasto a sua reação, você pode pagar 2 pontos de estamina para realizar uma reação adicional, uma vez por rodada.",
    "respeito celeste restringido": "**Respeito Celeste (8º Nível):** Seu poder e desenvolvimento te garantem o respeito dos céus, que concedem a sua bênção para si. Ao obter essa habilidade, você recebe uma dádiva do céu adicional. A partir do nível 12, você pode pegar esta habilidade outra vez.",

    # --- 10º NÍVEL ---
    "assassinar restringido": "**Assassinar (10º Nível):** Durante o primeiro momento, você é capaz de extrair letalidade absoluta, golpeando um inimigo desprevenido com um bote poderoso. Durante a primeira rodada de um combate, ao atacar uma criatura desprevenida a partir da furtividade ou surpresa, seu primeiro ataque é um crítico garantido.",
    "mente limpa restringido": "**Mente Limpa (10º Nível):** Você recebe vantagem para resistir às seguintes condições: Amedrontado, Cego, Enfeitiçado e Surdo.",
    "perceber o ar restringido": "**Perceber o Ar (10º Nível):** Sua visão se torna tão apurada que você consegue perceber o próprio ar, usando-o como uma plataforma para se mover e apoiar. Você é imune a danos de queda, conseguindo se apoiar no ar, desde que a altura não seja superior ao dobro do seu movimento. Ao pular você pode realizar outro pulo em seguida, no nível 13 você pode dar dois pulos em seguida, e no nível 17 pode dar três pulos em seguida. Quando for alvo de um ataque, você pode gastar 2 pontos de estamina e sua reação para realizar um teste de acrobacia contra um teste de reflexos do atacante e, caso o resultado do seu teste supere o do atacante, você desvia do ataque.",
    "precisao forcada restringido": "**Precisão Forçada (10º Nível):** Você consegue usar do seu físico impecável para forçar precisão absoluta em um golpe. Uma vez por rodada, quando você faz um ataque corpo-a-corpo, você pode pagar 3 pontos de estamina. Se acertar o ataque, causa dano máximo, sem necessidade de rolar danos.",
    "retaliacao restringido": "**Retaliação (10º Nível):** Se você receber dano de um inimigo que esteja dentro de seu alcance, você pode gastar 2 pontos de estamina e usar sua reação para realizar um ataque contra ele.",

    # --- 12º NÍVEL ---
    "adrenalina absoluta restringido": "**Adrenalina Absoluta (12º Nível):** Enquanto está em um surto de adrenalina, você se torna absoluto, extraindo ao máximo o seu potencial. Ao iniciar um surto de adrenalina, você pode escolher pagar 4 pontos para ativar e 2 por rodada para manter e, caso o faça, você recebe os seguintes benefícios: enquanto estiver em um surto de adrenalina, o seu ataque extra passa a custar 1 PE, você recebe +3 metros de Deslocamento e a sua DEF aumenta em 2.",
    "pinaculo fisico restringido": "**Pináculo Físico (12º Nível):** Você recebe +4 pontos de estamina máximos e pode escolher aumentar o valor de dois atributos entre Força, Destreza e Constituição em 2. No nível 16, o valor de ambos os atributos escolhidos aumentam novamente em 2.",
    "rejeitar a morte restringido": "**Rejeitar a Morte (12º Nível):** Quando estiver nas portas da morte, você pode escolher receber uma falha garantida para fazer um teste de Fortitude contra a CD X, sendo X igual a 15 + 1 para cada 3 pontos de vida negativos. Se passar, você fica com 1 de vida e recebe 1 ponto de exaustão. [Pré-Requisito: Ainda de Pé]",

    # --- 16º NÍVEL ---
    "entre as sombras restringido": "**Entre as Sombras (16º Nível):** Agora o Ataque Furtivo aplica quando você está em camuflagem ou cobertura. Além disso, quando for realizar um Ataque Furtivo, você pode ignorar parcialmente as regras de vantagem e acumular até uma vantagem adicional (totalizando 3d20). Caso ele seja um acerto garantido, além do efeito normal, a sua margem de crítico é reduzida em 2. [Pré-Requisito: Arremetida Encoberta]",
    "instintos agucados restringido": "**Instintos Aguçados (16º Nível):** Enquanto seus pontos de estamina e de vida excederem metade do máximo deles, você recebe uma reação adicional por rodada. [Pré-Requisito: Reação Rápida]",
    "mesmo morto restringido": "**Mesmo Morto (16º Nível):** Mesmo se você não tiver mais força vital, é necessário continuar lutando até o limite. Ao cair para 0 de vida, sem possuir um uso de Ainda de Pé, ao invés de ir para as Portas da Morte você continua de pé e realizando seus turnos normalmente; porém, no final de todo turno, você deve realizar um teste de resistência de Fortitude com CD25 + 1 para cada 5 pontos de vida negativos que possuir. Caso falhe no teste, você cai imediatamente, com 1 falha nos testes de morte. [Pré-Requisito: Rejeitar a Morte]"
}


dicionario_talentos = {
    # --- TALENTOS GERAIS ---
    "afinidade com tecnica": "**Afinidade com Técnica:** Com uma afinidade superior com a sua técnica amaldiçoada, você consegue a desenvolver melhor, criando mais extensões dela. Ao obter este talento, você recebe um Feitiço adicional. Nos níveis 5, 10, 15 e 20 você recebe mais um Feitiço adicional.",
    "artesao amaldicoado": "**Artesão Amaldiçoado:** A criação de ferramentas amaldiçoadas é um ofício no qual você busca se especializar. Ao obter este talento, você se torna capaz de criar Ferramentas Amaldiçoadas, de acordo com o guia na página 153. Além disso, você se torna treinado em Ofício (Ferreiro) ou Ofício (Canalizador), caso não seja treinado; caso já seja treinado em ambas, você se torna mestre em uma delas à sua escolha.",
    "ataque infalivel": "**Ataque Infalível:** Uma vez por rodada, após a rolagem de dano de um ataque armado ou desarmado, você pode escolher a repetir, ficando com o novo resultado obrigatoriamente. Além disso, você não pode ter os níveis de dano da sua arma reduzidos.",
    "atencao infalivel": "**Atenção Infalível:** Sua atenção para os arredores nunca falha, mantendo seus sentidos afiados. Você recebe um bônus de +5 em sua Atenção e não pode ser surpreendido caso consciente.",
    "dedicacao recompensadora": "**Dedicação Recompensadora:** Você se dedica mais do que o normal em suas missões, imagem e desempenho, e recebe melhores recompensas em troca. No quarto grau, você recebe dois itens de custo 1 a mais; no terceiro grau, você recebe dois itens de custo 2 a mais; no segundo grau, você recebe um item de custo 2 a mais e 2 de custo 3 a mais; no primeiro grau, você recebe dois itens de custo 3 a mais e um item de custo 4 a mais e, no grau especial, você recebe dois itens de custo 4 a mais. Os aumentos de itens não são cumulativos.",
    "favorecido pela sorte": "**Favorecido pela Sorte:** Você tem uma sorte inexplicável, a qual o favorece nos momentos mais críticos. Você tem 3 pontos de sorte. Sempre que fizer uma rolagem, você pode gastar um ponto de sorte para rolar outro d20, podendo escolher usar qualquer um dos dois resultados. Você pode escolher rolar o outro dado após ver o resultado da primeira rolagem, mas antes de ver as consequências. Quando um inimigo conseguir um 20 em uma jogada de ataque para o acertar, você recupera 1 ponto de sorte. Você recupera seus pontos de sorte após um descanso longo.",
    "guarda infalivel": "**Guarda Infalível:** Você nunca baixa a sua guarda, mesmo em uma situação que pode ser vista como catastrófica. Em caso de um desastre em um teste de ataque, você não causa um ataque como reação. Caso um efeito imposto sobre você tente reduzir sua Defesa ou impor modificadores negativos em testes de resistência, você terá +3 para resistir.",
    "incremento de atributo": "**Incremento de Atributo:** Buscando se tornar mais forte, você aumenta um de seus atributos através do treino e esforço. Ao obter esse talento, você aumenta o valor e o limite de um atributo à sua escolha em 2. Você pode pegar este talento várias vezes, mas apenas uma vez para cada atributo.",
    "investida aprimorada": "**Investida Aprimorada:** Você domina a arte de realizar uma investida, otimizando-a para extrair o potencial máximo da ação. Ao realizar uma ação de investida, seu movimento aumenta em 3 metros durante ela; o bônus de acerto aumenta de +2 para um valor igual ao seu bônus de treinamento e, caso acerte o ataque, o alvo deve realizar um teste de Atletismo contra o seu, sendo derrubado em uma falha.",
    "mestre das armas": "**Mestre das Armas:** Você desenvolve suas capacidades e potencial para manejar armas. Ao obter este talento, você escolhe aumentar o valor de sua Força ou Destreza em 2 e pode escolher entre se tornar treinado em quatro armas quaisquer à sua escolha ou receber acesso ao efeito de crítico de um grupo de armas à sua escolha.",
    "mestre defensivo": "**Mestre Defensivo:** Você desenvolve suas capacidades de defesa e resistência. Ao obter este talento, você escolhe aumentar o valor de sua Força ou Constituição em 2 e se torna treinado em escudos. Caso já seja treinado, você recebe Redução de Dano adicional com o escudo igual a metade do valor base de RD dele.",
    "perceber oportunidade": "**Perceber Oportunidade:** Você possui uma facilidade sem igual para realizar golpes oportunos, sendo quase como uma segunda natureza para você. Você ignora a regra de repetição de reação para Golpes de Oportunidade, podendo repeti-lo duas vezes por rodada ao invés do comum. Todo golpe de oportunidade que você realiza possui vantagem.",
    "provocacao desafiadora": "**Provocação Desafiadora:** Não só provocar, mas você é capaz de se transformar no centro da atenção daquele que você deseja desafiar. Uma criatura que seja afetada por uma ação de Provocar sua, além de receber desvantagem para atacar outras criaturas, deve sempre realizar pelo menos um ataque contra você. Além disso, uma quantidade de vezes igual a metade do seu modificador de Presença, você pode utilizar Provocar como uma Ação Livre.",
    "resiliencia melhorada": "**Resiliência Melhorada:** Você refina suas estratégicas e habilidade para resistir a um nicho específico de ameaças. Ao obter este talento, escolha um teste de resistência, exceto Integridade: você se torna treinado nele ou, caso já seja treinado, se torna mestre. O valor do atributo usado no TR escolhido aumenta em 1.",
    "saltador constante": "**Saltador Constante:** Você é extremamente acostumado a saltar, movendo-se mais através de pulos do que correndo. Ao pular, caso você esteja no alcance toque de uma parede ou objeto no fim do seu movimento, você pode utilizar a ação pular mais uma vez como ação livre, cortando seu pulo pela metade, ao terminar o movimento com um alvo dentro do seu alcance corpo a corpo, caso realize um ataque contra ele, você recebe +2 na jogada de ataque e, caso acerte, causa dano adicional igual ao seu modificador de Força.",
    "tecnicas agressivas de escudo": "**Técnicas Agressivas de Escudo:** Você aperfeiçoa o uso do seu escudo para colocá-lo no seu ataque. Ao atacar no seu turno, você pode usar sua Ação Bônus para Empurrar com o escudo. Caso o alvo seja empurrado com sucesso, ele recebe Xd6 + seu Modificador de Força de dano de impacto, onde X é igual ao seu Modificador de Força. Além disso, você pode escolher aumentar a distância que a criatura é empurrada em 4,5 metros ou a derrubar.",
    "tecnicas de arremesso": "**Técnicas de Arremesso:** Você se aprofunda em técnicas para manusear armas de arremesso no seu potencial máximo e evitar desperdiçar uma delas. Sempre que atacar com uma arma de arremesso, você recebe um bônus de +2 para acertar e +3 no dano.",
    "tecnicas de reacao rapida": "**Técnicas de Reação Rápida:** Preparado para agir sob pressão e urgência, você sabe como reagir o mais rápido possível. Você recebe +5 de Iniciativa. Após a rolagem de iniciativa, caso você não seja o primeiro, você pode rolar novamente, ficando com o melhor resultado.",
    "tecnicas defensivas de escudo": "**Técnicas Defensivas de Escudo:** Você aperfeiçoa o uso do seu escudo para colocá-lo por completo na sua defesa. Ao invés de receber penalidade, você adiciona o bônus padrão do escudo em TRs de Reflexos. Além disso, uma quantidade de vezes igual ao seu Bônus de Treinamento, por descanso longo, você pode, antes de saber o resultado de um TR de Reflexos, escolher usar sua Reação para reduzir o valor necessário para um sucesso crítico em 3.",
    "tempestade de ideias": "**Tempestade de Ideias:** Você decide extrair ao máximo o seu potencial, obtendo melhorias e novas maestrias. Aumenta um atributo a sua escolha em 1. Você se torna treinado em uma perícia e uma ferramenta à sua escolha. Além disso, escolha uma perícia na qual seja treinado: uma quantidade de vezes igual a metade do seu bônus de treinamento, por descanso curto, você pode escolher receber vantagem em um teste com ela.",
    "adepto de medicina": "**Adepto de Medicina:** Estudando em seu tempo livre, você aprendeu sobre primeiros socorros em busca de ajudar sua equipe em momentos de desespero. Ao obter este talento, você recebe acesso ao segundo efeito da habilidade Suporte em Combate, de Suporte, com o valor da cura sendo baseado em seu nível de personagem, mas a quantidade de usos é reduzida pela metade. [Pré-Requisito: Mestre em Medicina, não possuir mais que dois talentos 'Adepto']",
    "adepto de briga": "**Adepto de Briga:** Para sempre ter uma opção, você treinou seus punhos o suficiente para ajudar nas situações mais precárias. Enquanto não estiver com nenhum equipamento do grupo Pugilato, você recebe +3 em jogadas de ataque desarmado e o dano de seus golpes desarmados aumenta em 2 níveis. Além disso, caso acerte um ataque desarmado mas não cause nenhum dano, você pode Agarrar, Derrubar ou Empurrar o alvo como uma Ação Livre. [Pré-Requisito: Mestre em Atletismo, não possuir mais que dois talentos 'Adepto']",
    "adepto de combate": "**Adepto de Combate:** Estudando e refletindo, você consegue adotar um estilo de combate específico, compreendendo e incorporando seus detalhes. Ao obter este talento você aprende um dos estilos de combate da especialização Especialista em Combate. [Pré-Requisito: Mestre em Intuição, não possuir mais que dois talentos 'Adepto']",
    "adepto de feiticaria": "**Adepto de Feitiçaria:** Com um treinado mais focado em técnica e como a utilizar de maneira melhor, você descobre mais sobre a feitiçaria como um todo. Ao obter este talento, você recebe uma Mudança de Fundamento da habilidade Domínio dos Fundamentos de Especialista em Técnica, com exceção de Técnica Rápida. Você pode reduzir o custo da Mudança de Fundamento em 1 uma quantidade de vezes igual ao seu bônus de treinamento por cena. [Pré-Requisito: Mestre em Feitiçaria, possuir Feitiços, não possuir mais que dois talentos 'Adepto']",
    "alma inquebravel": "**Alma Inquebrável:** Sua alma é mais resistente do que o normal, com sua consciência e perseverança tornando-a difícil de se quebrar. Você se torna treinado em Integridade e recebe Redução de Dano contra Dano na Alma igual a 1/4 do seu Nível de Personagem. [Pré-Requisito: Constituição 14]",
    "apaziguador de tecnica": "**Apaziguador de Técnica:** Preparado para impedir seus inimigos de utilizarem técnicas no meio de combate, você sabe o momento perfeito para esgueirar golpes entre conjurações. Ao ver um inimigo usar uma técnica com a conjuração de Ação Comum ou maior em seu alcance corpo-a-corpo, você pode realizar um golpe de oportunidade contra ela, forçando-a a fazer um teste de concentração. Caso a criatura falhe, ela perde 5 em rolagens de acerto/CD caso seja um Feitiço de dano, tem os benefícios do Feitiço cortados pela metade caso seja auxiliar ou tem o Feitiço completamente anulado caso seja especial. Caso o Feitiço seja anulado, o alvo recupera a ação e não gasta o PE, mas não pode realizar o Feitiço anulado. [Pré-Requisito: Treinado em Astúcia, Nível 8]",
    "aptidao desenvolvida": "**Aptidão Desenvolvida:** Você desenvolve uma de suas aptidões e capacidade de uso da energia amaldiçoada. Ao obter este talento, escolha uma aptidão amaldiçoada para ter o seu nível de aptidão aumentado em 1. Você pode pegar esse talento múltiplas vezes, mas apenas uma vez para cada Aptidão. [Pré-Requisito: Nível 4]",
    "determinado a viver": "**Determinado a Viver:** Mesmo de frente a perigos e ameaças sem limites, você mantém sua vontade de viver e seguir em frente. Uma vez por dia, na primeira vez que fosse para os testes de morte, você pode escolher ficar com 1 de vida ao invés disso. Todo teste de morte que você realiza, a partir do segundo, possui vantagem. [Pré-Requisito: Treinado em Vontade e Constituição 16]",
    "discurso motivador": "**Discurso Motivador:** Você pode gastar 10 minutos, fora de combate, ou gastar uma Ação Completa dentro de combate, para inspirar seus aliados: todas as criaturas amigáveis na cena, que possam te ouvir, recebem HP temporário igual ao dobro do seu nível + seu modificador de Presença multiplicado pela metade do seu bônus de treinamento. Uma criatura só pode receber esse bônus uma vez por descanso curto ou longo. [Pré-Requisito: Treinado em alguma perícia de Presença]",
    "especialista em concussao": "**Especialista em Concussão:** Seu valor de força ou constituição aumenta em 1. Sempre que causar Dano de Impacto em um ataque corpo a corpo, ele é aumentado em um nível. Uma vez por turno, ao acertar uma criatura e infligir dano de impacto, você pode mover ela até 3 metros para um espaço desocupado. [Pré-Requisito: Nível 8]",
    "especialista em cortes": "**Especialista em Cortes:** Seu valor de força ou destreza aumenta em 1. Sempre que causar Dano Cortante em um ataque corpo a corpo, ele é aumentado em um nível. Uma vez por turno, ao acertar uma criatura e infligir dano cortante, você pode reduzir o movimento dela em 4,5 metros até o começo do seu próximo turno. [Pré-Requisito: Nível 8]",
    "especialista em perfuracao": "**Especialista em Perfuração:** Seu valor de força ou destreza aumenta em 1. Sempre que causar Dano Perfurante em um ataque corpo a corpo, ele é aumentado em um nível. Uma vez por turno, ao acertar uma criatura e infligir dano perfurante você pode rolar novamente os dados de dano, usando o melhor resultado total. [Pré-Requisito: Nível 8]",
    "mestre da criacao": "**Mestre da Criação:** Praticando e estudando, você consegue otimizar o seu tempo para poder produzir mais itens em menos tempo. Quando escolher o foco Criação de Itens durante um interlúdio, você pode criar 2 itens adicionais. Caso escolha o foco Criação de Itens mais de uma vez no mesmo interlúdio, você recebe as oportunidades adicionais para cada foco. Além disso, você recebe um bônus de +2 em duas perícias de ofício a sua escolha. [Pré-Requisito: Treinado em dois Ofícios, Nível 4]",
    "mestre do arremesso": "**Mestre do Arremesso:** Dominando ainda mais as armas de arremesso, você consegue as levar até o seu limite, tornando-se um efetivo mestre dos arremessos. Toda arma de arremesso que você utilizar tem o seu dano aumentado em um dado; o seu bônus em ataques com armas de arremesso se torna +4 para acertar e +6 no dano, e o alcance de ataques com armas de arremesso aumenta em 6 metros. [Pré-Requisito: Técnicas de Arremesso, Nível 8]",
    "mestre dos chicotes": "**Mestre dos Chicotes:** Os chicotes são um tipo de arma exótico e único, recompensando aqueles que dominam o seu manejo com um novo potencial. Suas rolagens de ataque com chicotes causam +4 de dano e o alcance aumenta em 1,5 metros. Além disso, uma vez ao turno, quando acertar uma criatura com um ataque com chicote, você pode a forçar a realizar um TR de Fortitude e, caso falhe, você pode a puxar até 3 metros para sua direção. [Pré-Requisito: Nível 5]",
    "movimentos acrobaticos": "**Movimentos Acrobáticos:** Não é hora de ficar parado no chão! Você se move agilmente sempre, e não para no lugar! Ao ser derrubado ou receber a condição caído, você pode fazer um teste de acrobacia contra o atletismo da criatura que te derrubou, caso isso aconteça, você pode se levantar como uma ação livre, sem gastar sua ação de movimento e se mover 3m sem ativar golpes de oportunidade. Ao fazer isso, você também recebe um bônus de metade do seu modificador de destreza na Defesa por 1 rodada. [Pré-Requisito: Treinado em Acrobacia]",
    "robustez aprimorada": "**Robustez Aprimorada:** Seus pontos de vida máximos aumentam em um valor igual ao seu nível ao obter esse talento. Sempre que subir de nível e tiver esse talento, você recebe +1 ponto de vida máximo. Além disso, você recebe +2 em testes de Fortitude. [Pré-Requisito: Constituição 14]",
    "tecnicas de empunhadura dupla": "**Técnicas de Empunhadura Dupla:** Você recebe um bônus de +1 na sua Defesa quando estiver empunhando uma arma em cada mão. Você pode lutar com duas armas mesmo que as armas não sejam leves, desde que não possuam a propriedade pesada ou duas mãos. Você pode utilizar a ação Sacar para sacar duas armas gastando apenas metade do movimento da sua próxima ação de Andar. [Pré-Requisito: Força ou Destreza 14]",
    "tecnicas de mobilidade": "**Técnicas de Mobilidade:** Seu movimento aumenta em 3 metros. Uma vez por rodada, ao atacar uma criatura, você pode realizar um teste de Reflexos contra um teste de Reflexos do alvo e, caso suceda, o alvo não pode realizar ataques de oportunidade contra você pelo resto do seu turno. [Pré-Requisito: Destreza 14]",
    "tecnicas de ocultamento": "**Técnicas de Ocultamento:** Você recebe um bônus adicional em testes de Furtividade igual ao seu Bônus de Treinamento e, quando deixar uma criatura Desprevenida através de um ataque surpresa, o prejuízo é aplicado em todos os Testes de Resistência ao invés de apenas Reflexos. [Pré-Requisito: Treinado em Furtividade]",
    "tecnicas do sentinela": "**Técnicas do Sentinela:** Ao acertar uma criatura com um ataque de oportunidade, o movimento dela é reduzido em 4,5 metros até o final do turno dela. Quando uma criatura a 1,5 metros de você faz um ataque contra um alvo além de você, você pode como uma reação realizar um ataque contra essa criatura. [Pré-Requisito: Nível 5]",
    "wrestling": "**Wrestling:** Você sabe técnicas de agarramento melhor do que ninguém, fazendo com que os agarrados nunca escapem de suas garras. Ao agarrar um alvo, caso ele tente escapar de um agarrão que você esteja fazendo, você pode forçá-lo a fazer um teste de modificador de força contra o seu teste de modificador de força, uma vez por rodada. Ao realizar uma Jogada de Ataque, você pode escolher soltar o alvo do agarrão como parte do ataque para causar metade do valor de força em dano adicional, fazendo o alvo ficar caído. Você pode escolher, ao invés de deixá-lo caído, joga-lo, arremessando-o, se ele atingir algo, ele recebe dano de fonte variável. [Pré-Requisito: Nível 4]",
    "voto malevolente": "**Voto Malevolente:** Você sabe como manter sua cabeça fria mesmo nos momentos mais tensos, lembrando-se da malícia ao criar votos. Ao realizar votos emergenciais, o voto não precisa ter um malefício maior que o benefício, sendo realizado normalmente. [Pré-Requisito: Nível 12]",

    # --- TALENTOS DE ORIGEM ---
    "familiaridade com tecnica": "**Familiaridade com Técnica:** Com a sua técnica amaldiçoada sendo parte da sua individualidade, você se torna cada vez mais e mais familiar com ela, otimizando-a em custo ou poder. Seu Feitiço escolhido primeiro como Marca Registrada tem a redução de custo em PE aumentada de 1 para 2 ou, caso seja Sustentada, você pode escolher reduzir o custo para sustentar em 1. Além disso, você pode escolher uma quantidade de Feitiços adicionais como Marca Registrada igual a metade do seu bônus de treinamento. [Pré-Requisito: Origem Inato, Nível 12]",
    "manual de tecnica": "**Manual de Técnica:** Sua técnica já est�� registrada há muito tempo, com direito a um manual explicando seu funcionamento e uso. Ao obter este talento, você pode criar um Feitiço de um nível acima ao maior que você possui acesso, mas ele tem o custo aumentado em 50%. Quando você receber acesso ao nível do Feitiço criado com o Manual, você deve obrigatoriamente o aprender quando ganhar um novo Feitiço e, após isso, pode criar outro Feitiço de nível superior com Manual de Técnica. Caso você já possua acesso a Feitiços de Nível 5, o tempo de recarga da sua Técnica Máxima é reduzido em 1 rodada. [Pré-Requisito: Origem Herdado, Nível 5]",
    "expansao de reserva": "**Expansão de Reserva:** Você expande a sua reserva de energia, a qual fica oculta em seu ser, apenas aguardando seu uso. Sua característica energia antinatural recebe as seguintes melhorias: recuperar energia da sua reserva se torna uma ação livre e, ao recuperar, você também recebe uma quantidade de pontos de energia temporários igual a metade do seu bônus de treinamento. Além disso, você passa a poder utilizar a característica uma vez por descanso longo ao invés de por dia. [Pré-Requisito: Origem Derivado, Nível 8]",
    "quebra de limites": "**Quebra de Limites:** Você continua quebrando os seus limites a partir de um desenvolvimento fora da curva ordinária. Ao obter este talento, você aumenta o valor de dois atributos diferentes à sua escolha em 2, com exceção do seu atributo com maior limite. Além disso, o limite dos dois atributos escolhidos é aumentado em 2. [Pré-Requisito: Origem Derivado, Nível 6]",
    "fisico aperfeicoado": "**Físico Aperfeiçoado:** O seu corpo se torna específico e desenvolvido para uma área em peculiar, ligando-se mais firmemente a certos aspectos. Ao adquirir este talento, escolha um dos efeitos: Seu Deslocamento aumenta em 4,5 metros. Você recebe um bônus de +2 em testes de Acrobacia ou Atletismo. Caso empurre uma criatura ou arremesse um objeto, a distância é aumentada em 3 metros. A distância de todo pulo que você realizar aumenta em um valor igual a metade da distância total. [Pré-Requisito: Origem Feto Amaldiçoado Híbrido, Nível 6]",
    "reposicao sanguinea": "**Reposição Sanguínea:** Além de um vigor maldito, ele se desenvolve para uma capacidade única de repor o seu sangue e saúde. Sua cura do Vigor Maldito passa a poder ser utilizada tanto como ação bônus quanto reação ao receber dano, além de aumentar em 5. [Pré-Requisito: Origem Feto Amaldiçoado Híbrido, Nível 6]",
    "estudo amaldicoado": "**Estudo Amaldiçoado:** Você estuda sobre a energia amaldiçoada ao máximo, conseguindo descobrir uma nova maneira de a utilizar. Ao obter este talento, você pode escolher dois Níveis de Aptidão diferentes para serem aumentados em 1. [Pré-Requisito: Origem Sem Técnica, Nível 8]",
    "nocao e preparacao": "**Noção e Preparação:** Embora você esteja privado do acesso a uma técnica e certas aplicações da energia, você tem noção e preparação suficiente para o proteger diante certos problemas. Você recebe um bônus de +2 para testes de resistências contra efeitos de aptidões amaldiçoadas. Nos níveis 8, 12 e 16 o bônus aumenta em +1. [Pré-Requisito: Origem Sem Técnica, Nível 4]"
}

dicionario_aptidoes = {
     # --- APTIDÕES DE AURA ---
    "afinidade ampliada": "**Afinidade Ampliada (Aura):** Sua aura é aprimorada para ter uma maior affinity com um elemento específico. Ao obter essa habilidade, você escolhe um tipo de dano elemental. Sempre que você infligir dano desse tipo específico, você causa dano adicional igual a 1 + o seu Nível de Aptidão em Aura no total do dano.",
    "aura anuladora": "**Aura Anuladora (Aura):** A aura que o cobre obtém uma propriedade anuladora, capaz de protegê-lo de certos efeitos. Uma quantidade de vezes igual ao seu bônus de treinamento, caso você fosse sofrer uma condição, você pode pagar uma quantidade variável de energia para ignorá-la, a depender do nível da condição. Esta aptidão não pode anular manobras e efeitos físicos. Anular uma condição fraca custa 2PE; média 4PE; forte 6PE e extrema 10PE. Você recupera esses usos em um descanso longo.",
    "aura chamativa": "**Aura Chamativa (Aura):** Você cria uma aura ao seu redor que é chamativa, atraente e mágica. Toda criatura que não for seu aliado, e começar um turno dentro de 4,5 metros, precisa realizar um TR de Vontade. Em falha, fica enfeitiçada, podendo repetir o teste no próximo turno dela. Para cada falha, ela recebe +2 para resistir a esta aptidão até o final da cena. [Pré-Requisito: Presença 18 e Nível 6]",
    "aura controlada": "**Aura Controlada (Aura):** Você refinou seu controle sobre a aura, ajudando-o a se ocultar. Você soma metade do seu Nível de Aptidão em Aura em testes de Furtividade. Sempre que rolar Furtividade, você pode gastar 1 PE para receber o nível completo ao invés de metade. [Pré-Requisito: Treinado em Furtividade e Destreza 16]",
    "aura de contencao": "**Aura de Contenção (Aura):** Com foco em conter, tem-se uma aura mais pesada e densa. Sempre que for agarrar um alvo, você adiciona metade do seu Nível de Aptidão em Aura na rolagem de Atletismo e para evitar que escape. Uma quantidade de vezes por cena igual a metade do seu Nível de Aptidão, você pode gastar 1 PE para receber vantagem para agarrar ou impor desvantagem em quem tentar escapar. [Pré-Requisito: Força ou Constituição 16]",
    "aura do bastiao": "**Aura do Bastião (Aura):** Sua aura é protetiva e auxilia seus aliados a não serem acertados. Todo aliado dentro de 4,5 metros de você recebe um bônus na Defesa igual ao seu Nível de Aptidão em Aura.",
    "aura do comandante": "**Aura do Comandante (Aura):** Refletindo uma presença forte, estar coberto pela sua aura é uma grande motivação. Você pode, como Ação Bônus, expandir sua aura para cobrir todo aliado dentro de 4,5 metros, os quais recebem 1 + metade do seu Nível de Aptidão em Aura em rolagens de dano e testes de perícia. Para cada turno que manter ativa, você paga 2 PE. [Pré-Requisito: Presença 16 e Nível 8]",
    "aura do comandante evoluida": "**Aura do Comandante Evoluída (Aura):** Sua presença como comandante se torna ainda mais forte. Quando utilizar Aura do Comandante, pode optar por somar seu Nível de Aptidão total e conceder +2 em ataques e TRs. O custo aumenta para 4 PE. [Pré-Requisito: Aura do Comandante e Nível 12]",
    "aura drenadora": "**Aura Drenadora (Aura):** Uma aura vampiresca capaz de drenar a vida dos alvos. Sempre que matar um inimigo, você recebe PV temporários igual a Xd8 + mod. de Constituição (X = Nível de Aptidão em Aura). Eles podem acumular. [Pré-Requisito: Aptidão em Aura 2 e Nível 6]",
    "aura elemental": "**Aura Elemental (Aura):** Você imbui a aura com um elemento, alterando o tipo de dano dos ataques com armas. Escolha um tipo de dano da categoria Elementais. Seus ataques causam 1d4 de dano adicional desse tipo. No Nível de Aptidão 2, o dano se torna 1d6; no 3, 1d8; e no 5, 1d10. Pode ser desabilitada como ação livre. [Pré-Requisito: Nível 6]",
    "aura elemental reforcada": "**Aura Elemental Reforçada (Aura):** Você recebe RD ao tipo de dano da sua aura elemental igual a redução de Aura Reforçada somado ao seu Nível de Aptidão em Aura. [Pré-Requisito: Aura Elemental e Aura Reforçada]",
    "absorcao elemental": "**Absorção Elemental (Aura):** Sempre que receber dano elemental, pode usar reação para absorver parte. Isso não reduz o dano, mas no próximo ataque você adiciona Xd6 de dano do mesmo tipo. X = Nível de Aptidão em Aura. No Nível 3, aumenta para d8; no nível 5, para d10. [Pré-Requisito: Aura Elemental]",
    "aura embacada": "**Aura Embaçada (Aura):** Como ação bônus, pague 2 PE para ativar (2 PE por rodada para manter). Enquanto ativa, todo ataque corpo-a-corpo ou a distância contra você tem 20% de chance de falhar (1 ou 2 em 1d10). [Pré-Requisito: Nível 6]",
    "aura inofensiva": "**Aura Inofensiva (Aura):** Quando iniciar um combate, realize um teste de Feitiçaria contra a Atenção dos inimigos. Você fica automaticamente escondido contra toda criatura cuja Atenção seja superada. [Pré-Requisito: Presença 16]",
    "casulo de energia": "**Casulo de Energia (Aura):** Como Ação Comum, forme um casulo por 1 rodada (6 PE). Recebe imunidade a dano físico mundano. Se for de técnica, recebe RD adicional igual ao dobro do Nível de Aptidão em Aura. [Pré-Requisito: Aura Impenetrável, Nível de Aptidão 5 e Nível 16]",
    "aura excessiva": "**Aura Excessiva (Aura):** No começo de toda rodada pode pagar 2 PE. Se o fizer, recebe RD contra todos os tipos de dano (exceto alma) igual ao valor de redução de Aura Reforçada. [Pré-Requisito: Aura Reforçada, Constituição 16 e Nível 8]",
    "concentrar aura": "**Concentrar Aura (Aura):** Como ação livre, desabilite aptidões passivas de aura por 1 rodada. Para cada uma desabilitada, após acertar um ataque, o alvo recebe 1d8 de dano energético. Limite de desabilitação: 1 + Nível de Aptidão em Aura. Não se aplica em Feitiços.",
    "enganacao projetada": "**Enganação Projetada (Aura):** Quando atacar, a criatura faz TR de Astúcia. Se falhar, você tem vantagem no ataque. Para ataques adicionais no turno, custa 1 PE. [Pré-Requisito: Treinado em Enganação, Destreza 18 e Nível 4]",
    "golpe com aura": "**Golpe com Aura (Aura):** Gaste 1 PE para imbuir um golpe com uma aptidão que force TR. A CD aumenta no valor do seu Nível de Aptidão em Aura. Se causar dano, é aplicado após o ataque. Não funciona com Feitiços.",
    "transferencia de aura": "**Transferência de Aura (Aura):** Como ação bônus, pague 2 PE para transferir uma Aptidão de Aura para um aliado em 9 metros por uma rodada. Custa 1 PE por rodada adicional para manter.",
    "aura lacerante": "**Aura Lacerante (Aura):** Ative como ação livre por 1 rodada. Criaturas a 3m fazem TR de Fortitude. Em falha, recebem Xd6 + mod. principal de dano energético (X = Nível de Aptidão). No Nível 3, aumenta para d8; no 5, para d10.",
    "aura macabra": "**Aura Macabra (Aura):** Criaturas agressivas a 1,5m fazem TR de Vontade. Em falha, ficam Abaladas. Pagando 1 PE (ação livre), expande para 4,5m por 1 rodada. A partir do Nível 3, inflige Amedrontado.",
    "aura macica": "**Aura Maciça (Aura):** Sua Defesa aumenta em um valor igual a seu Nível de Aptidão em Aura. [Pré-Requisito: Constituição 16]",
    "aura movedica": "**Aura Movediça (Aura):** Todo quadrado adjacente se torna terreno difícil. No Nível 2, afeta 3m; no Nível 4, 4,5m; no Nível 5, 6m. Não pode ser aumentada por Expandir Aura.",
    "aura redirecionadora": "**Aura Redirecionadora (Aura):** Gaste 2 PE para imbuir um projétil/arremesso. Caso erre, role novamente contra um alvo a 6m do original. O segundo ataque recebe +1 + (metade do Nível de Aptidão) no acerto. [Pré-Requisito: Destreza 16]",
    "aura reforcada": "**Aura Reforçada (Aura):** Você recebe redução contra danos físicos (cortes, perfurações e impactos) igual ao dobro do seu Nível de Aptidão em Aura.",
    "aura impenetravel": "**Aura Impenetrável (Aura):** Como Ação Bônus, pague 3 PE por 1 rodada. Recebe resistência a dano físico. [Pré-Requisito: Aura Reforçada, Nível de Aptidão 3 e Nível 10]",

    # --- APTIDÕES DE CONTROLE E LEITURA ---
    "canalizar em golpe": "**Canalizar em Golpe (Controle/Leitura):** Como Ação de Movimento, gaste PE (até seu nível de CL). Cada PE = 1d6 de dano adicional no próximo ataque. Apenas por um ataque, não funciona em Feitiços. Errar não consome.",
    "cobrir se": "**Cobrir-se (Controle/Leitura):** Como Reação ao receber dano, gaste até (2 + dobro do CL) em PE. Cada PE concede 4 PV temporários (duram até o fim do turno da criatura).",
    "canalizacao avancada": "**Canalização Avançada (Controle/Leitura):** Canalizar também pode ser Reação ao atacar, e o bônus passa para 1d8 por PE. [Pré-Requisito: Canalizar em Golpe, Nível de Aptidão 2 e Nível 8]",
    "cobertura avancada": "**Cobertura Avançada (Controle/Leitura):** Ao usar Cobrir-se, cada PE passa a conceder 8 PV temporários. [Pré-Requisito: Cobrir-se, Nível de Aptidão 2 e Nível 10]",
    "canalizacao maxima": "**Canalização Máxima (Controle/Leitura):** Pode gastar 1 PE adicional. O bônus por PE vai para 1d10. Soma-se o Nível de Aptidão em Aura ao dano total. [Pré-Requisito: Canalização Avançada, Nível 4 e Nível 16]",
    "estimulo muscular": "**Estímulo Muscular (Controle/Leitura):** Use PE durante ações físicas. Movimento: 1 PE para aumentar metade do deslocamento. Testes (Acrobacia/Atletismo): até seu CL em PE (+1 por PE). Empurrar/Desarmar: 2 PE aumenta distância em (CL x 1,5m). Pulo: 1 PE dobra a distância.",
    "estimulo muscular avancado": "**Estímulo Muscular Avançado (Controle/Leitura):** Usa os estímulos 2x por rodada. Movimento: 2 PE para aumentar deslocamento total. Testes: +2 por PE. Empurrar: Distância aumenta (CL x 3m). [Pré-Requisito: Estímulo Muscular, CL 3 e Nível 4]",
    "expandir aura": "**Expandir Aura (Controle/Leitura):** Ação livre (2 PE). Dobra o alcance das aptidões de aura passivas por 1 rodada. Manter custa 1 PE/rodada. [Pré-Requisito: Nível 6]",
    "leitura de aura": "**Leitura de Aura (Controle/Leitura):** Teste de Feitiçaria contra a CD Amaldiçoada do alvo. Em sucesso, descobre propriedades passivas e ativas da aura da criatura.",
    "leitura rapida de energia": "**Leitura Rápida de Energia (Controle/Leitura):** Ação de Movimento: Teste de Percepção contra CD Amaldiçoada do alvo (com bônus igual ao seu CL). Em sucesso, ignora penalidades e Defesa fornecida pela aura inimiga na cena.",
    "projetar energia": "**Projetar Energia (Controle/Leitura):** Ação Comum. Dispare energia (gasto até 1 + CL em PE). Cada PE = 1d10 + mod. maior atributo de dano. Alcance: 9m + (1,5m x bônus de treino). Pode ser ataque amaldiçoado ou forçar TR de Reflexos (anula dano em sucesso).",
    "projecao avancada": "**Projeção Avançada (Controle/Leitura):** Dano por PE sobe para 2d8 + dobro do modificador. Recebe +2 para acertar ou aumenta CD do TR em 2. [Pré-Requisito: Projetar Energia, CL 2 e Nível 8]",
    "projecao maxima": "**Projeção Máxima (Controle/Leitura):** Dano por PE sobe para 3d8. Bônus de acerto +6 / CD do TR +4. TR passa a reduzir metade do dano em sucesso. [Pré-Requisito: Projeção Avançada, CL 4 e Nível 16]",
    "projecao dividida": "**Projeção Dividida (Controle/Leitura):** Pague até metade da energia do disparo original para criar duplicata contra alvo a 4,5m do primeiro. A duplicata força TR. [Pré-Requisito: Projeção Avançada, CL 3 e Nível 12]",
    "punho divergente": "**Punho Divergente (Controle/Leitura):** Em ataques desarmados (não raio negro), cause metade do dano. O alvo faz TR Fortitude; se falhar, a outra metade do dano no próximo turno entra com Vulnerabilidade. A CD aumenta em 1 a cada 5 de dano do primeiro golpe.",
    "emocao da petala decadente": "**Emoção da Pétala Decadente (Controle/Leitura):** Reação a Domínio ou Ação Bônus. Custa PE igual ao nível de DOM do inimigo para anular acerto garantido físico. (Concentração). Pode gastar 5 PE como ação livre para ataque corpo-a-corpo garantido (perde proteção defensiva no turno). [Pré-Requisito: Nível 5, Clã Três Grandes, Cobrir-se, CL 3]",
    "rastreio avancado": "**Rastreio Avançado (Controle/Leitura):** Detecta vestígios imediatamente. Se desconhecido, TR de Investigação/Percepção contra a CD de quem originou para analisar e rastrear a trilha.",

    # --- APTIDÕES DE DOMÍNIO ---
    "revestimento de dominio": "**Revestimento de Domínio (Domínio):** 5 PE e Ação Bônus (ou Reação a Feitiço). Custa 5 PE por turno para sustentar. Reduz dano de Feitiços no valor do seu Nível de Personagem. Se o Feitiço for nível menor ou igual a metade do seu Nível de DOM, é anulado completamente. Seus golpes anulam Feitiços ativos do alvo. Você não pode usar Feitiços com isso ativo. [Pré-Requisito: CL 3, DOM 1 e Nível 10]",
    "anular tecnica": "**Anular Técnica (Domínio):** Reação ao ser alvo de Feitiço. Pague o mesmo PE que o alvo usou e faça teste de Feitiçaria resistido. Se vencer, anula (até efeitos em área). Limite de usos = Nível de DOM por descanso longo. [Pré-Requisito: Domínio Simples, DOM 3 e Nível 8]",
    "expansao de dominio incompleta": "**Expansão de Domínio Incompleta (Domínio):** Ação comum e duas mãos livres (15 PE). Área: 4,5m x bônus de treino. Efeitos de acordo com o Guia. Dura 1 + Nível de DOM rodadas. [Pré-Requisito: DOM 1 e Nível 8]",
    "expansao de dominio completa": "**Expansão de Domínio Completa (Domínio):** Ação comum e duas mãos livres (20 PE). Esfera de 9m. Efeitos de acordo com o Guia. Dura 3 + Nível de DOM rodadas. [Pré-Requisito: Técnicas de Barreira, Expansão Incompleta, BAR 3, DOM 3 e Nível 10]",
    "acerto garantido": "**Acerto Garantido (Domínio):** Imbui sua técnica na barreira. Aumenta o custo da Expansão Completa em 5 PE. [Pré-Requisito: Expansão Completa, Treinado em Feitiçaria, BAR/DOM 4 e Nível 14]",
    "expansao de dominio sem barreiras": "**Expansão de Domínio Sem Barreiras (Domínio):** Mesmos efeitos de uma expansão completa com acerto garantido, mas não levanta barreiras físicas. Maior alcance e ataca barreiras de outras expansões por fora. [Pré-Requisito: Acerto Garantido, Mestre em Feitiçaria, BAR/DOM 5, Nível 20]",
    "dominio simples": "**Domínio Simples (Domínio):** Reação a Domínio ou Ação Bônus (5 PE). Cria esfera (1,5m + [DOM x 1,5m]). Anula Acerto Garantido dentro dela. (Concentração). Durabilidade = BAR + 1. Perde durabilidade por falha na concentração ou ao evitar Acerto Garantido no turno (e encolhe 1,5m). [Pré-Requisito: BAR 1 e Nível 5]",

    # --- APTIDÕES DE BARREIRA ---
    "tecnicas de barreira": "**Técnicas de Barreira (Barreira):** Ação Comum. Crie até 6 paredes ao redor (1 PE cada). Tamanho 1,5m. Vida: 5 + (BAR x metade do Nível). Move/manipula com outra Ação Comum. [Pré-Requisito: BAR 1]",
    "paredes resistentes": "**Paredes Resistentes (Barreira):** A vida de cada parede passa a ser 10 + (BAR x Nível de Personagem). [Pré-Requisito: Técnicas de Barreira, BAR 2 e Nível 4]",
    "barreira rapida": "**Barreira Rápida (Barreira):** Erguer ou manipular barreiras se torna uma Ação Bônus. [Pré-Requisito: Técnicas de Barreira, BAR 3 e Nível 6]",
    "cesta oca de vime": "**Cesta Oca de Vime (Barreira):** Ação Bônus ou Reação a Expansão (3 PE). Anula Acerto Garantido em você. (Concentração). Durabilidade = BAR + 1. Manter o selo com as duas mãos impede que a durabilidade caia por danos de Acerto Garantido (apenas por falha de concentração). [Pré-Requisito: História Mestre, BAR 1 e Nível 5]",
    "cortina": "**Cortina (Barreira):** Isola uma área escondendo seu interior. Custa 1 PE para cada 9 metros cobertos. Não tem custo para manter. Pode aplicar condições. [Pré-Requisito: Técnicas de Barreira]",

    # --- APTIDÕES DE ENERGIA REVERSA ---
    "energia reversa": "**Energia Reversa (Reversa):** PER (Ponto de Energia Reversa) = 2 PE normais. Ação comum para curar a si mesmo. Cura: 2d6 + mod. (Presença/Sabedoria) por PER gasto. Gasto máx: 1 + metade do Nível de Aptidão. [Pré-Requisito: Feitiçaria, CL 3 e Nível 8]",
    "cura amplificada": "**Cura Amplificada (Reversa):** Dado de cura vira d8. Soma o dobro do modificador. Gasto máximo se torna 1 + Nível de Aptidão. [Pré-Requisito: Energia Reversa, REV 3 e Nível 12]",
    "fluxo constante": "**Fluxo Constante (Reversa):** Pode se curar como Ação Livre no começo do turno. Ou como Reação ao receber dano. [Pré-Requisito: Energia Reversa, REV 3 e Nível 12]",
    "regeneracao aprimorada": "**Regeneração Aprimorada (Reversa):** Ação Comum (8 PER) para regenerar Ferimentos Complexos. Desmembramento (menos de 1 dia). Com membro em mãos, vira Ação Bônus (3 PER). Cura venenos (Ação Bônus, 4 PER). Se REV for 5, pode gastar 10 PER para ação livre. [Pré-Requisito: Cura Amplificada, REV 4 e Nível 15]",
    "liberacao de energia reversa": "**Liberação de Energia Reversa (Reversa):** Pode usar Energia Reversa para curar outras criaturas com alcance de Toque. [Pré-Requisito: Energia Reversa e Nível 10]",
    "canalizar energia reversa": "**Canalizar Energia Reversa (Reversa):** Ação de Movimento. Adiciona 2d6 de dano de Energia Reversa por PER gasto. Limite = bônus de treino. Apenas em ataques armados/desarmados contra Maldições. Não acumula com Canalizar em Golpe. [Pré-Requisito: Liberação de Energia Reversa e Canalizar em Golpe]",
    "cura em grupo": "**Cura em Grupo (Reversa):** Divide o total da rolagem de cura entre criaturas numa área de 4,5m + (1,5m x REV). O gasto máximo de PER aumenta em 2. [Pré-Requisito: Liberação de Energia Reversa]",

    # --- APTIDÕES ESPECIAIS ---
    "raio negro": "**Raio Negro (Especial):** Ocorre ao tirar 20 no dado em ataques corpo-a-corpo. Dano x1.5 (ignora resistências e RD). Ao usar pela 1ª vez (Compreensão Avançada): PV Máximo sobe no valor do Nível, Aura ganha +1 permanentemente. Pós-Raio (Estado de Consciência Absoluta): Por 1 rodada, o acerto necessário cai em 1 (ex: crítico no 19). Pode acumular até metade do seu CL. [Pré-Requisito: CL 3, For/Des 16, Nível 10]",
    "abencoado pelas faiscas negras": "**Abençoado pelas Faíscas Negras (Especial):** Raio Negro agora ativa no 19 e 20 naturalmente. Pode reduzir o requisito mais 1 vez no Estado de Consciência. Ao acertar, ganha metade do CL no ataque e o CL total no dano pelo resto da cena. [Pré-Requisito: Raio Negro, CL 4, Aura 3, Nível 15]",
    "reversao de tecnica": "**Reversão de Técnica (Especial):** Pode criar Feitiços de Reversão (efeito contrário ao padrão). O custo de PE aumenta no valor do nível do Feitiço. Você ganha um Feitiço Adicional (obrigatoriamente uma reversão) ao pegar a aptidão. [Pré-Requisito: Energia Reversa e Nível 12]",
    "tecnica maxima": "**Técnica Máxima (Especial):** Cria uma Técnica Definitiva (Feitiço Nível 5). Custa 25 PE. Recarga: 6 rodadas menos metade do Bônus de Treinamento. [Pré-Requisito: Feitiçaria Mestre, Acesso a Feitiços Nível 4]"
}


dicionario_itens = {
    # --- CUSTO 1 ---
    "antidoto simples": "**Antídoto Simples [Fármaco] (Custo 1):** Um simples antídoto, capaz de neutralizar venenos mais leves. O antídoto pode ser consumido como uma ação bônus, curando da condição envenenado e/ou qualquer veneno de custo 1 ou que venha de uma maldição de quarto grau.",
    "brinco da comunicacao": "**Brinco da Comunicação [Acessório] (Custo 1):** Um par de brincos imbuídos com uma técnica de comunicação. Usar um desses brincos permite que o usuário sintonize com até 6 outras pessoas que também estejam usando um. Todos sintonizados na mesma conexão conseguem se comunicar mentalmente desde que estejam dentro de 30 metros. Sintonizar um brinco dentro de combate é uma ação completa, e enquanto se comunica o brinco brilha em um brilho perceptível por qualquer pessoa.",
    "chaveiro canalizador": "**Chaveiro Canalizador [Acessório] (Custo 1):** Um chaveiro que canaliza energia amaldiçoada, refinando-a e dificultando resistir. Um personagem com o chaveiro canalizador tem a sua CD Amaldiçoada aumentada em 1.",
    "injecao estimulante": "**Injeção Estimulante [Fármaco] (Custo 1):** Uma injeção criada a partir de uma mescla de medicina e controle de energia amaldiçoada. Ela tem uma única carga e a injetar faz com que você receba +2 de bônus em toda rolagem de perícia usando um atributo a sua escolha durante 10 minutos. Dentro de combate, injetar é uma ação bônus.",
    "mix energetico pequeno": "**Mix Energético Pequeno [Fármaco] (Custo 1):** Um conjunto de suplementos e substâncias que conseguem recuperar a energia e vigor físico, concentrados em uma cápsula. Como uma ação bônus, é possível consumir o mix, recuperando 3 pontos de estamina.",
    "oleo amolador": "**Óleo Amolador [Mistura] (Custo 1):** Um pequeno recipiente cheio de um óleo que aumenta o potencial de uma arma, amolando-a. Pode ser aplicado em duas armas antes de acabar; uma arma coberta com óleo amolador recebe o traço Mortal d6. O óleo dura um dia.",
    "oleo flamejante": "**Óleo Flamejante [Mistura] (Custo 1):** Um óleo que deixa a arma extremamente inflamável, cobrindo-se de chamas com o menor dos esforços. Pode ser aplicado em duas armas antes de acabar; uma arma coberta com óleo flamejante recebe o traço Modular Queimante. O óleo dura 10 minutos.",
    "perola carregada": "**Pérola Carregada [Espiritual] (Custo 1):** Uma pequena pérola carregada com energia amaldiçoada, usada para recuperar do próprio estoque. Como uma ação bônus, é possível consumir a pérola, recuperando 3 pontos de energia amaldiçoada.",
    "remedio simples": "**Remédio Simples [Fármaco] (Custo 1):** Um simples remédio, capaz de forçar uma reação regenerativa do corpo. Como uma ação comum, é possível consumir o remédio e gastar seus dados de vida para se curar, com um limite igual a quatro dados de vida.",
    "simbolo da vida": "**Símbolo da Vida [Talismã] (Custo 1):** Uma espécie de pequena ficha ou amuleto, encravado em madeira e imbuído com energia reversa. Como uma ação bônus, é possível o destruir para liberar a energia em si mesmo, curando-se em 10 pontos de vida.",
    "talisma de barreira": "**Talismã de Barreira [Talismã] (Custo 1):** Um pequeno talismã que armazena uma barreira amaldiçoada. Pode usá-lo como uma ação bônus, invocando quatro paredes, cada uma possuindo 15 pontos de vida e ocupando 1,5 metros cada. Após usado, o talismã se esvai.",
    "veneno debilitante": "**Veneno Debilitante [Mistura] (Custo 1):** Um pote de veneno cujo foco é atingir o corpo, debilitando-o. Contato, o alvo terá seu deslocamento reduzido pela metade.",
    "veneno intenso": "**Veneno Intenso [Mistura] (Custo 1):** Um pote de veneno intenso e concentrado, com o propósito de invadir o corpo do alvo. Contato, o alvo ficará Envenenado durante uma rodada.",

    # --- CUSTO 2 ---
    "amuleto do vislumbre": "**Amuleto do Vislumbre [Acessório] (Custo 2):** Um amuleto amaldiçoado que fornece ao portador capacidade de vislumbrar tudo ao seu redor com perfeição. O usuário deste item recebe visão no escuro com alcance de 9 metros, além de um bônus de +2 em rolagens de Percepção. Uma vez ao dia, você pode, como uma ação bônus, se tornar capaz de enxergar com os olhos fechados em 9 metros de diâmetro por 1 minuto.",
    "antidoto intermediario": "**Antídoto Intermediário [Fármaco] (Custo 2):** Um simples antídoto, capaz de neutralizar venenos mais leves. O antídoto pode ser consumido como uma ação bônus, curando da condição envenenado e/ou qualquer veneno de custo 2 ou que venha de uma maldição de terceiro grau ou inferior.",
    "apanhador de saude": "**Apanhador de Saúde [Acessório] (Custo 2):** Um pequeno amuleto com formato semelhante ao de um apanhador de sonhos, o qual atrai boas energias. Sempre que um portador do acessório for curado, recebe +1 de cura por dado, com um limite de cura adicional igual a metade do seu nível.",
    "bracelete do vigor": "**Bracelete do Vigor [Acessório] (Custo 2):** Um bracelete que entra em sintonia com o corpo e acentua o físico, concedendo um maior vigor para o seu portador. Enquanto estiver utilizando o bracelete do vigor, os seus pontos de vida máximos aumentam em 10.",
    "conjunto de perolas carregadas": "**Conjunto de Pérolas Carregadas [Espiritual] (Custo 2):** Um conjunto de pérolas carregadas com energia amaldiçoada. Como uma ação bônus, é possível consumir o conjunto de pérolas, recuperando 6 pontos de energia amaldiçoada.",
    "faixa de foco": "**Faixa de Foco [Acessório] (Custo 2):** Uma faixa que quando presa ao seu portador o permite focar e manter a concentração. Você recebe um bônus de +2 em testes para manter a concentração e, uma vez por dia, você pode escolher não perder a concentração ao invés de realizar um teste.",
    "injecao de adrenalina": "**Injeção de Adrenalina [Fármaco] (Custo 2):** Uma injeção com uma dose considerável de adrenalina, que o faz esquecer temporariamente do cansaço. Usar a injeção é uma ação bônus; ao usar ela, seu nível de Exaustão é reduzido em 1 até o final da cena, voltando imediatamente após o término dela.",
    "mix energetico medio": "**Mix Energético Médio [Fármaco] (Custo 2):** Um conjunto reforçado de suplementos e substâncias que aumentam a recuperação do vigor físico. Como uma ação bônus, é possível consumir o mix, recuperando 6 pontos de estamina.",
    "pulseira magistral": "**Pulseira Magistral [Acessório] (Custo 2):** Uma pulseira cujas propriedades conseguem extrair mais as capacidades de quem a usa, melhorando uma perícia. Enquanto estiver usando a pulseira magistral, o usuário se torna treinado em uma perícia a sua escolha.",
    "remedio intermediario": "**Remédio Intermediário [Fármaco] (Custo 2):** Um remédio mais complexo, capaz de forçar uma reação regenerativa avançada no corpo. Como uma ação comum, é possível consumir o remédio e gastar seus dados de vida para se curar, com um limite igual a oito dados de vida.",
    "simbolo de vida florescente": "**Símbolo de Vida Florescente [Talismã] (Custo 2):** Uma ficha ou amuleto encravado em madeira e com quantidades modestas de energia reversa, o que dá um sutil brilho e calor. Como uma ação bônus, é possível o destruir para liberar energia em si mesmo, curando-se em 25 pontos de vida.",
    "talisma de barreira superior": "**Talismã de Barreira Superior [Talismã] (Custo 2):** Melhorando no talismã de barreira, ela é tecida com mais cuidado e foco em uma maior agilidade. Pode usá-lo como uma ação bônus ou como uma reação, invocando quatro paredes, cada uma possuindo 25 pontos de vida e ocupando 1,5 metros cada. Após usado, o talismã se esvai.",
    "veneno desnorteante": "**Veneno Desnorteante [Mistura] (Custo 2):** Um pote de veneno cuja composição foca em atingir o sistema nervoso de uma criatura. Contato, o alvo ficará Desprevenido durante uma rodada.",

    # --- CUSTO 3 ---
    "aneis do conhecimento": "**Anéis do Conhecimento [Acessório] (Custo 3):** Um conjunto de peculiares anéis, forjados e imbuídos com energia amaldiçoada e conhecimentos, prendendo-se na pele e ligando-se ao utilizador. Os anéis aumentam o valor de Sabedoria do utilizador em 2, podendo superar o seu limite de atributo, até ao máximo de 30.",
    "antidoto superior": "**Antídoto Superior [Fármaco] (Custo 3):** Um simples antídoto, capaz de neutralizar venenos mais leves. O antídoto pode ser consumido como uma acção bónus, curando a condição envenenado e/ou qualquer veneno de custo 3 ou que venha de uma maldição de segundo grau ou inferior.",
    "bracelete da forca": "**Bracelete da Força [Acessório] (Custo 3):** Firme e forjado a partir do mais forte aço, este bracelete aumenta o valor de Força do utilizador em 2, podendo superar o seu limite de atributo, até ao máximo de 30.",
    "chaveiro absorsor": "**Chaveiro Absorsor [Acessório] (Custo 3):** Um pequeno adereço espiritual, semelhante a um chaveiro, o qual é capaz de absorver energia amaldiçoada a partir de vestígios. Sempre que eliminar um inimigo que possua energia amaldiçoada ou seja formado por energia, recupera 2 pontos de energia amaldiçoada.",
    "cinturao do inabalavel": "**Cinturão do Inabalável [Acessório] (Custo 3):** Um robusto cinturão metálico, com uma corrente de energia amaldiçoada que é transmitida e reforça o físico do utilizador. O cinturão aumenta o valor de Constituição do utilizador em 2, podendo superar o seu limite de atributo, até ao máximo de 30.",
    "dominio simples contido": "**Domínio Simples Contido [Talismã] (Custo 3):** Um pequeno tubo com um domínio simples armazenado. Pode ser usado como uma acção comum, erguendo um domínio simples sem custo de energia, o qual se mantém por até 2 rodadas, protegendo apenas o portador do item. Após ser usado, o tubo torna-se inútil, com a técnica armazenada a esvair-se.",
    "faixas celeres": "**Faixas Céleres [Acessório] (Custo 3):** Várias faixas leves e quase transparentes que, quando amarradas a uma pessoa, usam a energia imbuída para estimular os reflexos e agilidade. As faixas aumentam o valor de Destreza do utilizador em 2, podendo superar o seu limite de atributo, até ao máximo de 30.",
    "mistura profana": "**Mistura Profana [Mistura] (Custo 3):** Uma mistura feita a partir de energia amaldiçoada concentrada e em estado activo, capaz de estimular o fluxo interno de energia de um feiticeiro, mas possuindo um preço. Como uma acção comum, pode-se consumir a mistura profana, reduzindo o custo de todas as habilidades que utilizem energia amaldiçoada em 1 ponto durante uma cena. Após o fim da cena, a personagem recebe 1 nível de exaustão.",
    "mix energetico grande": "**Mix Energético Grande [Fármaco] (Custo 3):** Uma pílula robusta e com concentrações extremas de substâncias que recuperam o físico e o vigor. Como uma acção bónus, é possível consumir o mix, recuperando 10 pontos de estamina.",
    "ombreiras do vigor superior": "**Ombreiras do Vigor Superior [Acessório] (Custo 3):** Ombreiras que, quando usadas em conjunto com os Braceletes do Vigor, trazem todo o potencial de resistência de um feiticeiro. Enquanto estiver a utilizar as Ombreiras do Vigor Superior, os seus pontos de vida máximos aumentam em 20.",
    "ornamento fascinante": "**Ornamento Fascinante [Acessório] (Custo 3):** Um ornamento com joias e uma beleza notável, além de um toque de jujutsu para lhe conceder um aspecto agradável que um acessório não poderia alcançar normalmente. O ornamento aumenta o valor de Presença do utilizador em 2, podendo superar o seu limite de atributo, até ao máximo de 30.",
    "pingente do intelecto": "**Pingente do Intelecto [Acessório] (Custo 3):** Leve, sutil e coberto de inscrições anciãs, este pingente aumenta o valor de Inteligência do utilizador em 2, podendo superar o seu limite de atributo, até ao máximo de 30.",
    "pulseira primacial": "**Pulseira Primacial [Acessório] (Custo 3):** Uma pulseira especial que consegue elevar uma perícia do utilizador. Enquanto estiver a utilizar a pulseira primacial, o utilizador torna-se mestre numa perícia à sua escolha, desde que já seja treinado nela.",
    "remedio complexo": "**Remédio Complexo [Fármaco] (Custo 3):** Um remédio de criação complexa. Como uma acção comum, é possível consumir o remédio e gastar os seus dados de vida para se curar, com um limite igual a doze dados de vida.",
    "terco de perolas carregadas": "**Terço de Pérolas Carregadas [Espiritual] (Custo 3):** Um terço criado a partir de pérolas carregadas com energia amaldiçoada. Como uma acção bónus, é possível consumir o terço, recuperando 10 pontos de energia amaldiçoada.",
    "veneno maldito": "**Veneno Maldito [Mistura] (Custo 3):** Um veneno feito a partir de uma substância semelhante ao sangue de maldições, com propriedades extremamente nocivas. Em contacto, o alvo ficará Exposto (Envenenado) durante três rodadas.",

    # --- CUSTO 4 ---
    "antidoto absoluto": "**Antídoto Absoluto [Fármaco] (Custo 4):** Um antídoto absoluto, confeccionado com a mais refinada medicina, capaz de neutralizar qualquer veneno ou toxina. O antídoto pode ser consumido como uma ação bônus, sendo curado da condição envenenado e/ou qualquer veneno de custo 4 ou que venha de uma maldição de primeiro grau ou inferior.",
    "elixir da vida": "**Elixir da Vida [Espiritual] (Custo 4):** Sendo o suprassumo da energia amaldiçoada, o elixir da vida incita uma vitalidade sem precedentes naquele que o consumir, usando da essência de várias maldições e junção de energia reversa. Como uma ação bônus, é possível consumir o elixir da vida, podendo usar todos os seus dados de vida para se curar, somando o dobro do seu modificador de constituição em cada um; você recebe vantagem e +5 em testes de resistência de Fortitude pelo resto da cena, assim como em Integridade.",
    "laco da vida": "**Laço da Vida [Acessório] (Custo 4):** Um pequeno laço vermelho, imbuído com quantidades excessivas de energia reversa. Um feiticeiro que tenha o laço preso a si é capaz de se prender a vida: caso um personagem com um laço da vida vá morrer, tal morte é ignorada e o laço se desgasta, sumindo. Ao evitar a morte com este item, o personagem cura metade dos seus pontos de vida, mas recebe 1 nível de exaustão. O Laço da Vida não funciona caso o feiticeiro já esteja com 5 níveis de Exaustão.",
    "lagrima de shinigami": "**Lágrima de Shinigami [Mistura] (Custo 4):** O mais letal veneno já conhecido, capaz de imbuir uma arma com tamanha letalidade que passou a ser conhecido como a lágrima de um shinigami. Contato, o alvo perde 2d10 pontos de vida e tem sua Defesa reduzida em 4, e passa a gastar 2 PE adicionais sempre que usar energia amaldiçoada até o final da cena (perde 2d10 de vida, fica Amedrontado e Exposto por 2 rodadas).",
    "simbolo de vida absoluta": "**Símbolo de Vida Absoluta [Talismã] (Custo 4):** Encravado e entalhado com os símbolos de absoluta saúde e vida, esse símbolo consegue canalizar em sua máxima a vida. Como uma ação livre, é possível o destruir para liberar energia em si mesmo, recuperando todos os seus pontos de vida, até o máximo, além de receber pontos de vida temporários igual ao triplo do seu nível de personagem.",
    "talisma do apice": "**Talismã do Ápice [Talismã] (Custo 4):** Um talismã que quando destruído liberta uma quantidade excessiva de energia, a qual é direcionada a um atributo específico do usuário. Ao usar o talismã, o valor de um atributo a sua escolha se torna 30 durante um minuto (10 rodadas dentro de um combate) e ele se quebra."
}

# ==========================================
# COMANDOS GERAIS (FORA DO ON_MESSAGE)
# ==========================================


@bot.hybrid_command(name="status", aliases=['condicao', 'efeito'], description="Consulta o banco de dados de condições do laboratório.")
async def status(ctx, *, nome_condicao: str = None):
    if not nome_condicao:
        await ctx.reply("Você precisa me dizer qual status quer consultar. Exemplo: `/status sofrendo`")
        return

    busca = nome_condicao.lower().strip()

    if busca in dicionario_condicoes:
        descricao = dicionario_condicoes[busca]
        resposta = (
            f"🔍 **Log do Sistema: Condição - [{nome_condicao.capitalize()}]**\n"
            f"> {descricao}\n\n"
        )
        await ctx.reply(resposta)
    else:
        await ctx.reply(f"Erro 404. O status '{nome_condicao}' não existe no meu banco de dados de maldições. Tem certeza que digitou certo?")

@bot.hybrid_command(name="concentracao", aliases=['foco'], description="Explica as regras de quebra de concentração.")
async def concentração(ctx):
    regras_foco = (
        "🧠 **Log do Sistema: Concentração**\n"
        "> Manter uma técnica ativa exige processamento contínuo. Se o seu hardware de carne sofrer interferência, você precisa fazer um **Teste de Resistência de Fortitude** para não dar crash na habilidade.\n\n"
        "**Tabela de Dificuldade (CD) para não perder o foco:**\n"
        "💥 **Dano Recebido:** CD `10` ou `Metade do dano` (o que for maior).\n"
        "💨 **Movimento Forçado:** CD `5 + Distância movida`.\n"
        "🤼 **Empurrado/Agarrado:** CD `10 + Bônus de Atletismo` do agressor.\n"
        "🤬 **Provocado:** CD `10 + Bônus da perícia` de quem provocou.\n\n"
        "⚠️ **Avisos Adicionais do Sistema:**\n"
        "- Certas condições de status dão tela azul e impedem a concentração imediatamente.\n"
        "- O seu processador é *single-core*: por padrão, só dá para concentrar em **UMA** habilidade por vez.\n\n"
        "*Se você perder o foco e desperdiçar Energia Amaldiçoada, o problema é seu. São 30 LMD pela consulta técnica.*"
    )
    await ctx.reply(regras_foco)

@bot.hybrid_command(name="hab", aliases=['tec', 'tecnica', 'habilidade'], description="Consulta o banco de dados de habilidades do sistema.")
async def hab(ctx, *, nome_habilidade: str = None):
    if not nome_habilidade:
        await ctx.reply("Você precisa me dizer qual técnica quer baixar do banco de dados. Exemplo: `/hab mãos amaldiçoadas`")
        return

    busca = padronizar_busca(nome_habilidade)

    if busca in dicionario_habilidades:
        descricao_crua = dicionario_habilidades[busca]
        desc_limpa = descricao_crua.replace("'", "").strip()
        
        resposta = (
            f"📥 **Download Concluído: Arquivo de Técnica**\n"
            f"> {desc_limpa}\n\n"
            f"*Técnica extraída com sucesso. Eu cobraria LMD por direitos autorais, mas o SysAdmin me proibiu.*"
        )
        await ctx.reply(resposta)
    else:
        await ctx.reply(f"Erro 404. A técnica '{nome_habilidade}' não consta nos meus arquivos. Tem certeza que você não inventou esse nome agora?")

@bot.hybrid_command(name="talento", aliases=['talentos', 'perk'], description="Consulta o banco de dados de talentos gerais e de origem.")
async def talento(ctx, *, nome_talento: str = None):
    if not nome_talento:
        await ctx.reply("Você precisa me dizer qual talento quer baixar do banco de dados. Exemplo: `/talento ataque infalível`")
        return

    busca = padronizar_busca(nome_talento)

    if busca in dicionario_talentos:
        descricao_crua = dicionario_talentos[busca]
        desc_limpa = descricao_crua.replace("'", "").strip()
        
        resposta = (
            f"🧬 **Log do Sistema: Registro de Talento**\n"
            f"> {desc_limpa}\n\n"
            f"*Mais um truque na manga? Lembre-se que talento não compra LMD, mas ajuda a não morrer tentando.*"
        )
        await ctx.reply(resposta)
    else:
        await ctx.reply(f"Erro 404. O talento '{nome_talento}' não consta nos meus arquivos de biometria. Tem certeza que não inventou esse nome?")

@bot.hybrid_command(name="aptidao", aliases=['aptidoes', 'apt'], description="Consulta o banco de dados de Aptidões Amaldiçoadas.")
async def aptidão(ctx, *, nome_aptidao: str = None):
    if not nome_aptidao:
        await ctx.reply("Energia detectada, mas alvo indefinido. Diga o nome da aptidão. Ex: `/aptidao raio negro`")
        return

    busca = padronizar_busca(nome_aptidao)

    if busca in dicionario_aptidoes:
        descricao_crua = dicionario_aptidoes[busca]
        desc_limpa = descricao_crua.replace("'", "").strip()
        
        resposta = (
            f"🌀 **Log do Sistema: Análise de Aptidão**\n"
            f"> {desc_limpa}\n\n"
            f"*Lembre-se: Controle sua energia amaldiçoada ou ela controlará você. Essa leitura custou preciosos ciclos de processamento.*"
        )
        await ctx.reply(resposta)
    else:
        await ctx.reply(f"Erro de Leitura. A aptidão '{nome_aptidao}' não tem nenhum vestígio na minha base de dados. Escreveu direito?")

@bot.hybrid_command(name="item", aliases=['consumivel', 'comprar', 'loja'], description="Consulta o banco de dados de Itens Especiais do laboratório.")
async def item(ctx, *, nome_item: str = None):
    if not nome_item:
        await ctx.reply("Quer comprar o quê? Ar? Me diga o nome do item que você tá procurando. Exemplo: `/item remédio simples`")
        return

    busca = padronizar_busca(nome_item)

    if busca in dicionario_itens:
        descricao_crua = dicionario_itens[busca]
        desc_limpa = descricao_crua.replace("'", "").strip()
        
        resposta = (
            f"🛒 **Log do Sistema: Inventário do Laboratório**\n"
            f"> {desc_limpa}\n\n"
            f"*Vai levar ou vai ficar só olhando? Cuidado que na Rhine Lab a gente cobra só pra respirar o ar da loja.*"
        )
        await ctx.reply(resposta)
    else:
        await ctx.reply(f"Tsk. O item '{nome_item}' está fora de estoque ou você inventou esse nome agora. Vê se lê a lista de equipamentos direito antes de me chamar.")

@bot.hybrid_command(name="chat", description="Bate um papo direto com a Closure sem precisar mencioná-la.")
async def chat(ctx, *, mensagem: str):
    """Conversa com a IA da Closure diretamente."""
    # Avisa o Discord que a IA está pensando (evita o erro de 'aplicativo não respondeu')
    await ctx.defer()

    try:
        # 1. Salva a pergunta e pega o histórico completo do BANCO
        contexto_chat = await atualizar_memoria_db(ctx.author.id, ctx.author.display_name, mensagem)
        
        # 2. Verifica se é o Mizuki (O Mestre) falando pelo ID
        aviso_mestre = ""
        if ctx.author.id == 459030926928904230: 
            aviso_mestre = "[SISTEMA: O usuário atual é o Mizuki, o Mestre do RPG e seu criador/Admin. Trate-o com o mínimo de respeito exigido na sua programação e não tente extorquir tanto LMD dele.]\n\n"
        
        # 3. MOTOR DE BUSCA OCULTO (Ponte Neural da Closure)
        texto_busca_ia = padronizar_busca(mensagem)
        conhecimento_injetado = ""
        
        todos_os_bancos = [dicionario_condicoes, dicionario_habilidades, dicionario_talentos, dicionario_aptidoes, dicionario_itens]
        
        for banco in todos_os_bancos:
            for chave, descricao in banco.items():
                if re.search(r'\b' + re.escape(chave) + r'\b', texto_busca_ia):
                    desc_limpa = descricao.replace("'", "").strip()
                    conhecimento_injetado += f"- {desc_limpa}\n"
        
        aviso_banco_dados = ""
        if conhecimento_injetado:
            aviso_banco_dados = f"\n[SISTEMA - DADOS DO LABORATÓRIO: O jogador está perguntando sobre os seguintes termos do RPG. Use as regras abaixo como verdade absoluta para responder a ele, mas responda com a sua personalidade sarcástica:\n{conhecimento_injetado}]\n"

        # 3.5. Monta o pacote de dados FINAL para enviar pra IA
        prompt_final = f"{aviso_mestre}{aviso_banco_dados}Histórico Recente:\n{contexto_chat}\n\nAgora é a sua vez. Responda a última mensagem DIRETAMENTE, sem repetir o que já foi dito e sem usar '[Closure]:' no início."
        
        # 4. Sistema de Fallback (Plano B e C de Energia da Closure)
        try:
            resposta = cliente_gemini.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_final,
                config=types.GenerateContentConfig(system_instruction=instrucao_personalidade)
            )
        except Exception as erro_limite:
            print(f"⚠️ 2.5 falhou! MOTIVO: {erro_limite}")
            print("Ligando gerador 1.5-8B (Alta Cota)...")
            try:
                resposta = cliente_gemini.models.generate_content(
                    model="gemini-1.5-flash-8b",
                    contents=prompt_final,
                    config=types.GenerateContentConfig(system_instruction=instrucao_personalidade)
                )
            except Exception as erro_reserva:
                print(f"⚠️ 1.5-8B falhou! MOTIVO: {erro_reserva}")
                print("Usando gerador de emergência 2.5-flash-lite...")
                resposta = cliente_gemini.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt_final,
                    config=types.GenerateContentConfig(system_instruction=instrucao_personalidade)
                )

        # EXTRAINDO O TEXTO DA RESPOSTA
        texto_resposta = resposta.text

        # --- FILTRO DE LIMPEZA ---
        texto_resposta = texto_resposta.replace("[Closure]:", "").strip()
        texto_resposta = texto_resposta.replace(f"[{ctx.author.display_name}]:", "").strip()
        
        if texto_resposta.startswith('"'):
            texto_resposta = texto_resposta.lstrip('"')

        # 5. Salva o que a Closure respondeu na memória do BANCO
        await atualizar_memoria_db(ctx.author.id, "Closure", texto_resposta, eh_resposta=True)
        
        # Envia a resposta final
        await ctx.reply(texto_resposta)
        
    except Exception as e:
        print(f"Erro CRÍTICO na API do Gemini: {e}")
        await ctx.reply("Tsk! Meu cache de memória deu overflow geral. Tenta de novo, e não me faz gastar LMD com limpeza de dados!")

@bot.hybrid_command(name="limpar_cache", description="Comando para o jogador incinerar os registros da Closure.")
async def limpar_cache(ctx):
    user_id = ctx.author.id
    
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM historico WHERE user_id = ?", (user_id,)) as cursor:
            count = await cursor.fetchone()
            
            if count[0] > 0:
                await db.execute("DELETE FROM historico WHERE user_id = ?", (user_id,))
                await db.commit()
                await ctx.reply("🧹 **Cache formatado!** Minha memória sobre as nossas últimas conversas foi incinerada. Não que eu fizesse questão de lembrar de graça, mas agora estamos no zero a zero.")
            else:
                await ctx.reply("⚠️ Seu cache já está vazio. Quer que eu limpe o quê? O seu saldo bancário? Porque isso eu faço com prazer!")
                
# Token vem do .env (DISCORD_TOKEN), nunca no código
bot.run(os.getenv("DISCORD_TOKEN"))