#!/bin/sh

# Ativa o ambiente virtual
source .venv/bin/activate

# Adiciona o diretório do projeto ao PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Executa o Flask com o caminho completo para o executável do venv
# Isso garante que estamos usando as dependências corretas.
.venv/bin/python -u -m flask --app main --debug run --port $PORT
