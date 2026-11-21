"""Carteira viva: serviço e ponte Discord opcionais, separados da produção.

O serviço roda separado das Guias, com armazenamento próprio; as Guias só
carregam a ponte (ponte_discord) quando o site está configurado. Somente
adaptadores de servidor autenticados podem construir as identidades recebidas.
"""
