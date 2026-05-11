import argparse

from .cli import mainfunc
from .construtor import criar_projeto

def main():
    p = argparse.ArgumentParser(
    description="Executor de Otimização e Gerenciador de professores\n",
    
    )
        
    p.add_argument('--init', '-i', action='store_true', help="Inicializa local do projeto")
    
    args = p.parse_args()

    if args.init:
        criar_projeto()
    else:
        mainfunc()
    
if __name__ == "__main__":
    main()