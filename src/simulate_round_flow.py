
import random
from typing import List, Literal

from src.data_structures import (
    KillEvent,
    Player,
    SimulateRoundInput,
    SimulateRoundOutput,
    Team,
)


def get_duel_weight(role: str, side: Literal["attack", "defense"]) -> int:
    attack_probs = {
        "Duelist": 35,
        "Initiator": 25,
        "Flex": 20,
        "Controller": 12,
        "Sentinel": 8,
    }
    defense_probs = {
        "Duelist": 20,
        "Initiator": 22,
        "Flex": 20,
        "Controller": 18,
        "Sentinel": 20,
    }
    probs = attack_probs if side == "attack" else defense_probs
    return probs.get(role, 10)


def select_player_for_duel(
    players: List[Player], side: Literal["attack", "defense"]
) -> Player:
    total_weight = sum(get_duel_weight(p.role, side) for p in players)
    rand_val = random.uniform(0, total_weight)
    current_weight = 0
    for player in players:
        current_weight += get_duel_weight(player.role, side)
        if rand_val < current_weight:
            return player
    return players[-1]  # Fallback


def run_round_simulation(input_data: SimulateRoundInput) -> SimulateRoundOutput:
    """
    This is a helper function, not a flow. It contains the core simulation logic.
    """
    alive_a = list(input_data.teamA.players)
    alive_b = list(input_data.teamB.players)
    kill_feed: List[KillEvent] = []

    def calculate_duel_outcome(
        p1: Player, p2: Player, p1_team: List[Player], p2_team: List[Player]
    ):
        # For the very first duel, ignore stats and make it a 50/50 chance.
        if not kill_feed:
            return (p1, p2) if random.random() < 0.5 else (p2, p1)

        # Higher HS% gives a chance for an "instant" win
        if random.random() < p1.stats.hs / 200:
            return p1, p2
        if random.random() < p2.stats.hs / 200:
            return p2, p1

        p1_score = p1.stats.aim * random.random()
        p2_score = p2.stats.aim * random.random()

        # Support from a nearby teammate can influence the duel
        p1_supporters = [p for p in p1_team if p.name != p1.name]
        if p1_supporters and random.random() < p1_supporters[0].stats.support / 150:
            p1_score *= 1.15  # 15% bonus for having support

        p2_supporters = [p for p in p2_team if p.name != p2.name]
        if p2_supporters and random.random() < p2_supporters[0].stats.support / 150:
            p2_score *= 1.15  # 15% bonus for having support

        # Clutch factor is more important when in a numbers disadvantage
        if len(p1_team) < len(p2_team):
            p1_score *= 1 + (p1.stats.clutch / 100) * random.random()
        if len(p2_team) < len(p1_team):
            p2_score *= 1 + (p2.stats.clutch / 100) * random.random()

        return (p1, p2) if p1_score > p2_score else (p2, p1)

    while alive_a and alive_b:
        all_alive_players = alive_a + alive_b
        initiator = select_player_for_duel(all_alive_players, "attack")
        initiator_is_team_a = any(p.name == initiator.name for p in alive_a)
        opponents = alive_b if initiator_is_team_a else alive_a

        if not opponents:
            break

        opponent = random.choice(opponents)
        winner, loser = calculate_duel_outcome(
            initiator,
            opponent,
            alive_a if initiator_is_team_a else alive_b,
            alive_b if initiator_is_team_a else alive_a,
        )

        kill_feed.append(
            KillEvent(
                killer=winner.name,
                victim=loser.name,
                killerTeam=input_data.teamA.name
                if any(p.name == winner.name for p in alive_a)
                else input_data.teamB.name,
                victimTeam=input_data.teamA.name
                if any(p.name == loser.name for p in alive_a)
                else input_data.teamB.name,
            )
        )

        if any(p.name == loser.name for p in alive_a):
            alive_a = [p for p in alive_a if p.name != loser.name]
        else:
            alive_b = [p for p in alive_b if p.name != loser.name]

    return SimulateRoundOutput(
        winner="teamA" if alive_a else "teamB", killFeed=kill_feed
    )


def simulate_round(input_data: SimulateRoundInput) -> SimulateRoundOutput:
    return run_round_simulation(input_data)
