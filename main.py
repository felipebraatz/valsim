# main.py
import sys
import os
import json
import time

# --- Correção do PYTHONPATH ---
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
venv_path = os.path.join(project_root, '.venv', 'lib', 'python3.11', 'site-packages')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_path not in sys.path:
    sys.path.insert(0, src_path)
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)
# --- Fim da Correção ---

from flask import Flask, jsonify, request, send_file, send_from_directory, Response, stream_with_context
from simulate_series_flow import simulate_series # Importa a função correta

app = Flask(__name__, static_folder='static', static_url_path='')

# Rota para a página principal
@app.route("/")
def index():
    return send_file('src/index.html')

# Rota para a página de partida rápida
@app.route("/quick_match")
def quick_match():
    return send_file('src/quick_match.html')

# Rota para a página de simulação de partida
@app.route("/match_simulation")
def match_simulation():
    return send_file('src/match_simulation.html')

# Rota de API para obter todos os times
@app.route("/api/teams")
def get_teams():
    """Serve o arquivo JSON com os dados das equipes."""
    return send_from_directory('data', 'teams.json')

# Rota de API para obter todas as estatísticas dos jogadores
@app.route("/api/player_stats")
def get_player_stats():
    """Serve o arquivo JSON com as estatísticas dos jogadores."""
    return send_from_directory('data', 'player_stats.json')
    
# Rota para servir logos de times
@app.route('/static/images/logos/<path:filename>')
def serve_team_logo(filename):
    return send_from_directory('static/images/logos', filename)
# --- ROTA DE SIMULAÇÃO CORRIGIDA ---
@app.route("/api/simulate_series", methods=['GET'])
def handle_simulation_stream():
    """
    Esta rota aceita os parâmetros da partida via GET, chama a simulação em modo streaming
    e retorna os eventos um a um.
    """
    team_a_id = request.args.get('teamA')
    team_b_id = request.args.get('teamB')
    series_format = request.args.get('format')
    maps_json = request.args.get('maps')

    if not all([team_a_id, team_b_id, series_format, maps_json]):
        return jsonify({"error": "Parâmetros 'teamA', 'teamB', 'format' e 'maps' são obrigatórios."}), 400

    try:
        maps = json.loads(maps_json)
    except json.JSONDecodeError:
        return jsonify({"error": "Parâmetro 'maps' inválido. Deve ser um JSON array de strings."}), 400

    def event_stream():
        """Gera os eventos da simulação."""
        try:
            # A função simulate_series é um gerador que produz os eventos
            for event in simulate_series(team_a_id, team_b_id, series_format, maps):
                # Envia cada evento como uma linha de JSON (Server-Sent Events like format)
                yield json.dumps(event) + '\n'
                time.sleep(0.1) # Pequeno delay para a UI conseguir renderizar
        except Exception as e:
            # Log do erro no servidor
            print(f"Erro durante a simulação: {e}")
            # Opcional: envia um evento de erro para o cliente
            error_event = {"type": "error", "message": str(e)}
            yield json.dumps(error_event) + '\n'

    # Retorna uma resposta de streaming
    # O mimetype 'application/x-ndjson' (Newline Delimited JSON) é apropriado para este tipo de stream
    return Response(stream_with_context(event_stream()), mimetype='application/x-ndjson')


def main():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)

if __name__ == "__main__":
    main()
