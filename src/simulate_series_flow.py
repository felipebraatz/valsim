
from typing import List
from src.data_structures import (
    SimulateSeriesInput,
    SimulateSeriesOutput,
    MapResultWithPlayerStats,
    TeamWithSeriesStats,
    PlayerWithSeriesStats,
    PlayerWithMatchStats,
    Team,
    Player,
    PlayerSeriesStats
)
from src.simulate_tactical_match_flow import simulate_tactical_match, TacticalMatchInputSchema


def simulate_series(input_data: SimulateSeriesInput) -> SimulateSeriesOutput:
    """
    Handles the series simulation process.
    """
    team_a_wins = 0
    team_b_wins = 0
    map_results: List[MapResultWithPlayerStats] = []

    round_name = input_data.roundName or ""
    is_lower_final = 'lower final' in round_name.lower()
    is_grand_final = 'grand final' in round_name.lower()
    games_to_win = 3 if is_lower_final or is_grand_final else input_data.gamesToWin
    max_games = (games_to_win * 2) - 1

    # Initialize players with series stats
    team_a_players_series: List[PlayerWithSeriesStats] = [
        PlayerWithSeriesStats(
            **p.model_dump(),
            stats=PlayerSeriesStats(**p.stats.model_dump(), kills=0, deaths=0)
        ) for p in input_data.teamA.players
    ]
    team_b_players_series: List[PlayerWithSeriesStats] = [
        PlayerWithSeriesStats(
            **p.model_dump(),
            stats=PlayerSeriesStats(**p.stats.model_dump(), kills=0, deaths=0)
        ) for p in input_data.teamB.players
    ]

    for _ in range(max_games):
        tactical_input = TacticalMatchInputSchema(
            teamA=input_data.teamA,
            teamB=input_data.teamB,
            map='ascent', # Placeholder
            offensivePlay='Default' # Placeholder
        )
        match_result = simulate_tactical_match(tactical_input)

        # Map tactical match stats back to full player objects for the map result
        team_a_players_map = [
            PlayerWithMatchStats(
                **base_player.model_dump(),
                stats={
                    **base_player.stats.model_dump(),
                    'kills': p_map.kills,
                    'deaths': p_map.deaths,
                }
            )
            for base_player in input_data.teamA.players
            for p_map in match_result.teamAStats if p_map.name == base_player.name
        ]
        
        team_b_players_map = [
            PlayerWithMatchStats(
                **base_player.model_dump(),
                stats={
                    **base_player.stats.model_dump(),
                    'kills': p_map.kills,
                    'deaths': p_map.deaths,
                }
            )
            for base_player in input_data.teamB.players
            for p_map in match_result.teamBStats if p_map.name == base_player.name
        ]

        map_results.append(
            MapResultWithPlayerStats(
                winner=match_result.winner,
                scoreA=match_result.scoreA,
                scoreB=match_result.scoreB,
                teamAPlayers=team_a_players_map,
                teamBPlayers=team_b_players_map,
            )
        )

        # Aggregate series stats
        for p_map in team_a_players_map:
            player_to_update = next((p for p in team_a_players_series if p.name == p_map.name), None)
            if player_to_update:
                player_to_update.stats.kills += p_map.stats.kills
                player_to_update.stats.deaths += p_map.stats.deaths

        for p_map in team_b_players_map:
            player_to_update = next((p for p in team_b_players_series if p.name == p_map.name), None)
            if player_to_update:
                player_to_update.stats.kills += p_map.stats.kills
                player_to_update.stats.deaths += p_map.stats.deaths

        if match_result.winner == 'A':
            team_a_wins += 1
        else:
            team_b_wins += 1

        if team_a_wins >= games_to_win or team_b_wins >= games_to_win:
            break

    # Construct final team objects with aggregated series stats
    final_team_a = TeamWithSeriesStats(**input_data.teamA.model_dump(), players=team_a_players_series)
    final_team_b = TeamWithSeriesStats(**input_data.teamB.model_dump(), players=team_b_players_series)

    return SimulateSeriesOutput(
        winner='A' if team_a_wins > team_b_wins else 'B',
        teamAScore=team_a_wins,
        teamBScore=team_b_wins,
        teamA=final_team_a,
        teamB=final_team_b,
        mapResults=map_results,
    )
