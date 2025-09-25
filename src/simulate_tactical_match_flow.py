
import random
from typing import List, Literal, Union

from pydantic import BaseModel, Field

from src.data_structures import Player, Team, SimulateMatchOutput, potential_tiers


class TacticalMatchInputSchema(BaseModel):
    teamA: Team
    teamB: Team
    map: str  # Although not used in this new logic, it's kept for API consistency
    offensivePlay: str  # Also kept for API consistency


class PlayerStats(BaseModel):
    name: str
    kills: int
    deaths: int


class TacticalMatchOutputSchema(SimulateMatchOutput):
    reasoning: str  # Will be a summary of the probabilistic outcome
    defensiveSetup: str  # Will be a placeholder
    teamAStats: List[PlayerStats]
    teamBStats: List[PlayerStats]


def get_player_strength(player: Player, side: Literal['attack', 'defense']) -> float:
    """
    Calculates a single player's strength based on their stats and role.
    """

    def get_stat_value(stat: Union[str, int]) -> int:
        if isinstance(stat, int):
            return stat
        if isinstance(stat, str) and stat in potential_tiers:
            min_val, max_val = potential_tiers[stat]
            return (min_val + max_val) / 2  # Use the average of the tier
        return 75  # Default fallback value

    aim = get_stat_value(player.stats.aim)
    clutch = get_stat_value(player.stats.clutch)
    support = get_stat_value(player.stats.support)

    # Average of key stats
    raw_strength = (aim + clutch + support) / 3

    # Apply positional buffs
    if side == 'attack' and player.role == 'Duelist':
        raw_strength *= 1.10
    if side == 'defense' and player.role == 'Sentinel':
        raw_strength *= 1.10

    return raw_strength


def get_team_strength(team: Team, side: Literal['attack', 'defense']) -> float:
    """
    Calculates the overall team strength for the match.
    """
    average_player_strength = sum(get_player_strength(p, side) for p in team.players) / len(team.players)

    def get_stat_value(stat: Union[str, int]) -> int:
        if isinstance(stat, int):
            return stat
        if isinstance(stat, str) and stat in potential_tiers:
            min_val, max_val = potential_tiers[stat]
            return (min_val + max_val) / 2
        return 75

    avg_support = sum(get_stat_value(p.stats.support) for p in team.players) / len(team.players)
    avg_clutch = sum(get_stat_value(p.stats.clutch) for p in team.players) / len(team.players)
    cohesion_modifier = (avg_support + avg_clutch) / 20  # Scale it down to be a smaller bonus

    # In the future, a map-specific bonus could be added here.
    map_bonus = 0

    return average_player_strength + cohesion_modifier + map_bonus


def run_probabilistic_map_sim(teamA: Team, teamB: Team) -> TacticalMatchOutputSchema:
    """
    Runs a probabilistic map simulation to determine the winner and score.
    """
    scoreA = 0
    scoreB = 0
    round_winners: List[Literal['A', 'B']] = []

    # Simulate regulation rounds
    for round_num in range(1, 25):
        if scoreA >= 13 or scoreB >= 13:
            break

        # Determine sides for the current round
        is_first_half = round_num <= 12
        team_a_side = 'attack' if is_first_half else 'defense'
        team_b_side = 'defense' if is_first_half else 'attack'

        strengthA = get_team_strength(teamA, team_a_side)
        strengthB = get_team_strength(teamB, team_b_side)
        probA_wins_round = strengthA / (strengthA + strengthB)

        # Apply bonus for winning the pistol round (rounds 2 and 14)
        if round_num == 2 and round_winners:
            if round_winners[0] == 'A':
                probA_wins_round = min(0.95, probA_wins_round + 0.25)
            else:
                probA_wins_round = max(0.05, probA_wins_round - 0.25)
        if round_num == 14 and len(round_winners) > 12 and round_winners[12]:
            if round_winners[12] == 'A':
                probA_wins_round = min(0.95, probA_wins_round + 0.25)
            else:
                probA_wins_round = max(0.05, probA_wins_round - 0.25)

        # Apply "bonus round" disadvantage (rounds 3 and 15)
        if round_num == 3 and len(round_winners) > 1 and round_winners[0] == round_winners[1]:
            probA_wins_round = 0.35 if round_winners[0] == 'A' else 0.65
        if round_num == 15 and len(round_winners) > 13 and round_winners[12] == round_winners[13]:
            probA_wins_round = 0.35 if round_winners[12] == 'A' else 0.65

        winner: Literal['A', 'B']
        if random.random() < probA_wins_round:
            scoreA += 1
            winner = 'A'
        else:
            scoreB += 1
            winner = 'B'
        round_winners.append(winner)

    # Handle Overtime
    if scoreA == 12 and scoreB == 12:
        ot_round = 0
        while abs(scoreA - scoreB) < 2:
            is_first_ot_pair_side = (ot_round // 2) % 2 == 0

            team_a_side_ot = 'attack' if is_first_ot_pair_side else 'defense'
            team_b_side_ot = 'defense' if is_first_ot_pair_side else 'attack'

            strengthA_OT = get_team_strength(teamA, team_a_side_ot)
            strengthB_OT = get_team_strength(teamB, team_b_side_ot)
            baseProbA_OT = strengthA_OT / (strengthA_OT + strengthB_OT)

            if random.random() < baseProbA_OT:
                scoreA += 1
            else:
                scoreB += 1
            ot_round += 1

    winner = 'A' if scoreA > scoreB else 'B'

    def generate_player_stats(team: Team, rounds_won: int, rounds_lost: int) -> List[PlayerStats]:
        total_rounds = rounds_won + rounds_lost
        did_win = rounds_won > rounds_lost

        BASE_KILLS_PER_ROUND = 0.75
        BASE_DEATHS_PER_ROUND = 0.70
        PERFORMANCE_MODIFIER = 1.1 if did_win else 0.9

        stats = []
        for p in team.players:
            player_strength = get_player_strength(p, 'attack')  # Use a neutral side for stat generation

            # --- Kill Calculation ---
            strength_kill_modifier = (player_strength - 80) / 100 + 1  # Mod around 1.0
            expected_kills = total_rounds * BASE_KILLS_PER_ROUND * strength_kill_modifier * PERFORMANCE_MODIFIER
            kills = round(expected_kills + (random.random() - 0.5) * 5)
            kills = max(0, kills)

            # --- Death Calculation ---
            strength_death_modifier = 1 - (player_strength - 80) / 100  # Inverse mod around 1.0
            expected_deaths = total_rounds * BASE_DEATHS_PER_ROUND * strength_death_modifier * (1 / PERFORMANCE_MODIFIER)
            deaths = round(expected_deaths + (random.random() - 0.5) * 5)
            deaths = max(0, deaths)
            deaths = min(total_rounds, deaths)
            
            stats.append(PlayerStats(name=p.name, kills=kills, deaths=deaths))
        return stats

    teamA_stats = generate_player_stats(teamA, scoreA, scoreB)
    teamB_stats = generate_player_stats(teamB, scoreB, scoreA)

    return TacticalMatchOutputSchema(
        winner=winner,
        scoreA=scoreA,
        scoreB=scoreB,
        reasoning="Probabilistic simulation based on Team Strengths.",
        defensiveSetup="N/A (Probabilistic Sim)",
        teamAStats=teamA_stats,
        teamBStats=teamB_stats,
    )


def simulate_tactical_match(input_data: TacticalMatchInputSchema) -> TacticalMatchOutputSchema:
    """
    Main function to simulate a tactical match.
    """
    return run_probabilistic_map_sim(input_data.teamA, input_data.teamB)
