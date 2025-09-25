
from typing import Literal, Dict, Any

from src.data_structures import (
    BuyPhaseInput,
    BuyPhaseOutput,
    DetermineBuyStrategyInput,
    Player,
    Team,
    Loadout,
)
from src.determine_buy_strategy_flow import determine_buy_strategy

# Data from lib/economy in the original TypeScript code
weapon_data: Dict[str, Dict[str, Any]] = {
    "vandal": {"cost": 2900},
    "phantom": {"cost": 2900},
    "bulldog": {"cost": 2050},
    "spectre": {"cost": 1600},
    "sheriff": {"cost": 800},
    "ghost": {"cost": 500},
    "classic": {"cost": 0},
}

shield_data: Dict[str, Dict[str, Any]] = {
    "heavy": {"cost": 1000},
    "light": {"cost": 400},
    "none": {"cost": 0},
}

ability_data: Dict[str, Dict[str, Any]] = {
    "Duelist": {"cost": 600},
    "Initiator": {"cost": 700},
    "Controller": {"cost": 500},
    "Sentinel": {"cost": 400},
    "Flex": {"cost": 500}, # Generic fallback
}


def execute_buy(
    player: Player, strategy: Literal["full-buy", "force-buy", "eco"]
) -> Player:
    """
    Executes the buy logic for a single player based on the team's strategy.
    """
    credits = player.credits or 0
    
    # Initialize a new loadout, keeping the secondary as classic by default.
    new_loadout = Loadout(secondary='classic', shield='none', abilities=False)

    # Weapon carry-over logic
    if player.alive and player.loadout and player.loadout.primary:
        new_loadout.primary = player.loadout.primary
    else:
        new_loadout.primary = None

    if strategy == "full-buy":
        primary_weapon_cost = weapon_data["vandal"]["cost"]  # Assume Vandal/Phantom
        heavy_shield_cost = shield_data["heavy"]["cost"]
        abilities_cost = ability_data.get(player.role, ability_data["Flex"])["cost"]

        if credits >= primary_weapon_cost + heavy_shield_cost + abilities_cost:
            credits -= primary_weapon_cost + heavy_shield_cost + abilities_cost
            new_loadout.primary = "vandal"
            new_loadout.shield = "heavy"
            new_loadout.abilities = True
        # Fallback to a cheaper rifle
        elif credits >= weapon_data["bulldog"]["cost"] + heavy_shield_cost:
            credits -= weapon_data["bulldog"]["cost"] + heavy_shield_cost
            new_loadout.primary = "bulldog"
            new_loadout.shield = "heavy"

    elif strategy == "force-buy":
        spectre_cost = weapon_data["spectre"]["cost"]
        light_shield_cost = shield_data["light"]["cost"]
        if credits >= spectre_cost + light_shield_cost:
            credits -= spectre_cost + light_shield_cost
            new_loadout.primary = "spectre"
            new_loadout.shield = "light"
        elif credits >= weapon_data["sheriff"]["cost"]:
            credits -= weapon_data["sheriff"]["cost"]
            new_loadout.secondary = "sheriff"

    else:  # eco
        if credits >= weapon_data["ghost"]["cost"]:
            credits -= weapon_data["ghost"]["cost"]
            new_loadout.secondary = "ghost"

    player.credits = credits
    player.loadout = new_loadout
    return player


def buy_phase_flow(input_data: BuyPhaseInput) -> BuyPhaseOutput:
    """
    A flow to handle the buy phase of a Valorant round.
    """
    buy_strategy_input = DetermineBuyStrategyInput(
        team=input_data.team,
        roundNumber=input_data.roundNumber,
        isPistol=input_data.isPistol,
    )
    strategy_result = determine_buy_strategy(buy_strategy_input)

    updated_players = [
        execute_buy(player, strategy_result.strategy)
        for player in input_data.team.players
    ]

    updated_team = input_data.team.copy(update={"players": updated_players})

    return BuyPhaseOutput(updatedTeam=updated_team)


def simulate_buy_phase(input_data: BuyPhaseInput) -> Team:
    """
    High-level function to simulate the buy phase and return the updated team.
    """
    result = buy_phase_flow(input_data)
    return result.updatedTeam
