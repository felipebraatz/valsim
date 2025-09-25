# simulation.py

import json
import random
from data_structures import Team, Player, TeamData, PlayerStatsData # Importe suas "receitas"

# --- Funções de Carregamento de Dados ---
# É bom ter funções que carregam e preparam os dados.
def load_all_data():
    """Carrega os dados de times e stats dos arquivos JSON."""
    with open('data/teams.json', 'r', encoding='utf-8') as f:
        teams_base_data = json.load(f)
    with open('data/player_stats.json', 'r', encoding='utf-8') as f:
        player_stats_data = json.load(f)
    return teams_base_data, player_stats_data

# --- Lógica Principal da Simulação ---
def simulate_a_simple_match(team_a_id: str, team_b_id: str) -> dict:
    """
    Função principal que simula uma partida.
    Recebe os IDs das equipes e retorna um dicionário com o resultado.
    """
    teams_base, player_stats = load_all_data()

    if team_a_id not in teams_base or team_b_id not in teams_base:
        return {"error": "Um ou ambos os times não foram encontrados."}

    # LÓGICA DA SIMULAÇÃO AQUI (exemplo super simples)
    # No futuro, aqui você usaria as classes Pydantic para montar os objetos Team, Player, etc.
    # e rodaria a simulação de rounds.
    
    score_a = random.randint(5, 13)
    score_b = 13 if score_a < 13 else random.randint(5, 12)

    winner = team_a_id if score_a > score_b else team_b_id

    result = {
        "teamA": {"id": team_a_id, "score": score_a},
        "teamB": {"id": team_b_id, "score": score_b},
        "winner": winner
    }
    
    return result