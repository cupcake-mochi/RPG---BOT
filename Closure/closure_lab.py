"""Só existe por causa da hospedagem: o app na Discloud foi criado com o bot antigo, cujo arquivo principal era
closure_lab.py, e enviar arquivos novos por Commit não troca o arquivo principal. Este repassa pro início de verdade."""
import sys

from iniciar import main

if __name__ == "__main__":
    sys.exit(main())
