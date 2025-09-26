# Simulador de Partidas de E-sports

Este é um aplicativo web construído com Python e Flask, projetado para simular partidas de e-sports de forma detalhada e em tempo real. O sistema utiliza dados de equipes e jogadores para gerar um log de eventos lance a lance, permitindo a visualização de confrontos hipotéticos.

## ✨ Features

- **Simulação em Tempo Real:** Acompanhe o desenrolar da partida evento por evento, desde a fase de compra até a conclusão de cada round.
- **Flexibilidade de Formato:** Suporte para séries Melhor de 1 (MD1), Melhor de 3 (MD3) e Melhor de 5 (MD5).
- **API de Dados:** Endpoints para servir estatísticas de jogadores e logos de equipes.
- **Geração Dinâmica de Stats:** As estatísticas dos jogadores são geradas dinamicamente com base em um sistema de tiers (S, A, B, C, D), introduzindo variabilidade e realismo.
- **Interface Web Interativa:** Configure as partidas e acompanhe os resultados diretamente no seu navegador.
- **Streaming de Eventos:** Utiliza Server-Sent Events (SSE) para enviar os eventos da simulação para o cliente de forma eficiente.

## 🛠️ Tech Stack

- **Back-end:** Python, Flask
- **Validação de Dados:** Pydantic
- **Front-end:** HTML, JavaScript
- **Ambiente de Desenvolvimento:** Nix, Firebase Studio

## 🚀 Getting Started

O projeto é configurado para ser executado em um ambiente Nix, que gerencia as dependências e a configuração do servidor.

1.  **Inicie o Workspace:** Ao abrir o projeto no ambiente de desenvolvimento, as dependências listadas em `requirements.txt` serão instaladas automaticamente em um ambiente virtual (`.venv`).

2.  **Execute o Servidor:** O servidor de desenvolvimento Flask pode ser iniciado de duas maneiras:
    - Automaticamente através da tarefa de preview `web`.
    - Manualmente, executando o script no terminal:
      ```bash
      ./devserver.sh
      ```

3.  **Acesse a Aplicação:** A aplicação estará disponível no painel de preview do seu IDE ou no endereço fornecido pelo servidor.

Para executar comandos `python` ou `pip` manualmente, lembre-se de ativar o ambiente virtual primeiro:
```bash
source .venv/bin/activate
```

## 📁 Estrutura do Projeto

```
.
├── main.py                   # Arquivo principal da aplicação Flask, define as rotas da API.
├── requirements.txt          # Lista de dependências Python.
├── devserver.sh              # Script para iniciar o servidor de desenvolvimento.
├── data/
│   ├── player_stats.json     # Dados base dos jogadores.
│   └── teams.json            # Dados das equipes.
├── src/
│   ├── *.html                # Templates HTML para a interface.
│   ├── data_structures.py    # Modelos Pydantic para validação e estruturação dos dados.
│   └── simulation/           # Módulos contendo a lógica principal da simulação.
└── static/
    └── images/
        └── logos/            # Logos das equipes.
```

## 🔌 API Endpoints

A aplicação fornece os seguintes endpoints:

- **`GET /api/player_stats`**
  - Retorna um arquivo JSON com as estatísticas de todos os jogadores.

- **`GET /api/simulate_series`**
  - Inicia uma nova simulação de série. Os eventos são retornados via streaming em formato `application/x-ndjson`.
  - **Query Params:**
    - `teamA` (string): ID da primeira equipe.
    - `teamB` (string): ID da segunda equipe.
    - `format` (string): Formato da série (`bo1`, `bo3`, `bo5`).
    - `maps` (string): String JSON de uma lista de mapas a serem jogados.

- **`GET /static/images/logos/<filename>`**
  - Serve os arquivos de imagem dos logos das equipes.

## ⚙️ Como Funciona

A simulação é iniciada por uma chamada de API do frontend para o endpoint `/api/simulate_series`. O backend então utiliza uma função geradora (`simulate_series`) que calcula cada evento da partida sequencialmente. Cada evento gerado é enviado de volta ao cliente como uma linha de JSON (Newline Delimited JSON), permitindo que a interface do usuário renderize o progresso da simulação em tempo real. As estatísticas e o desempenho dos jogadores são calculados dinamicamente para cada partida com base em um sistema de tiers de potencial, garantindo que não haja duas partidas exatamente iguais.
