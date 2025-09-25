# data_structures.py

"""
@fileOverview Este arquivo define todas as estruturas de dados principais e a lógica de apoio.
Inclui os modelos Pydantic para jogadores, equipes e simulações, que servem como
validadores e "plantas" para os dados carregados de arquivos JSON.
"""

import random
from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field, conlist

# --- Lógica de Apoio ---

potential_tiers = {
    'S': (90, 99),
    'A': (85, 89),
    'B': (80, 84),
    'C': (70, 79),
    'D': (60, 69)
}

def generate_stat(tier: Literal['S', 'A', 'B', 'C', 'D']) -> int:
    """
    Converte o tier de potencial de um jogador (por exemplo, "S") em uma estatística numérica aleatória
    dentro do intervalo definido para esse tier.
    """
    min_val, max_val = potential_tiers[tier]
    return random.randint(min_val, max_val)

# --- Modelos de Dados (Schemas Pydantic) ---

# Usado como placeholder
class Loadout(BaseModel):
    pass

class Titles(BaseModel):
    kickoff: int = 0
    league: int = 0
    masters: int = 0
    champions: int = 0

class SecondPlaces(BaseModel):
    masters: int = 0
    champions: int = 0

class Mvps(BaseModel):
    kickoff: int = 0
    league: int = 0
    masters: int = 0
    champions: int = 0

class PlayerAccolades(BaseModel):
    titles: Titles = Field(default_factory=Titles)
    secondPlaces: SecondPlaces = Field(default_factory=SecondPlaces)
    mvps: Mvps = Field(default_factory=Mvps)

class PlayerStats(BaseModel):
    aim: Union[str, int]
    hs: int
    support: Union[str, int]
    clutch: Union[str, int]

class Player(BaseModel):
    name: str
    role: str
    nationality: str
    age: int
    photo: Optional[str] = None
    accolades: Optional[PlayerAccolades] = None
    stats: PlayerStats
    credits: Optional[int] = None
    loadout: Optional[Loadout] = None
    alive: Optional[bool] = None

class Team(BaseModel):
    name: str
    players: conlist(Player, min_length=5, max_length=5)
    lossStreak: Optional[int] = None
    currentEcon: Optional[int] = None

class KillEvent(BaseModel):
    killer: str
    victim: str
    killerTeam: str
    victimTeam: str

class SimulateRoundInput(BaseModel):
    teamA: Team
    teamB: Team

class SimulateRoundOutput(BaseModel):
    winner: Literal['teamA', 'teamB']
    killFeed: List[KillEvent]

class PlayerMatchStats(PlayerStats):
    kills: int
    deaths: int

class PlayerWithMatchStats(Player):
    stats: PlayerMatchStats

class SimulateMatchInput(BaseModel):
    teamA: Team
    teamB: Team

class SimulateMatchOutput(BaseModel):
    winner: Literal['A', 'B']
    scoreA: int
    scoreB: int
    killFeed: Optional[List[KillEvent]] = None
    teamAPlayers: Optional[List[PlayerWithMatchStats]] = None
    teamBPlayers: Optional[List[PlayerWithMatchStats]] = None

class PlayerSeriesStats(PlayerStats):
    kills: int
    deaths: int

class PlayerWithSeriesStats(Player):
    stats: PlayerSeriesStats

class TeamWithSeriesStats(Team):
    players: conlist(PlayerWithSeriesStats, min_length=5, max_length=5)

class MapResult(BaseModel):
    winner: Literal['A', 'B']
    scoreA: int
    scoreB: int

class MapResultWithPlayerStats(MapResult):
    teamAPlayers: List[PlayerWithMatchStats]
    teamBPlayers: List[PlayerWithMatchStats]

class SimulateSeriesInput(BaseModel):
    teamA: Team
    teamB: Team
    gamesToWin: int
    roundName: Optional[str] = None

class SimulateSeriesOutput(BaseModel):
    winner: Literal['A', 'B']
    teamAScore: int
    teamBScore: int
    teamA: TeamWithSeriesStats
    teamB: TeamWithSeriesStats
    mapResults: List[MapResultWithPlayerStats]

class DetermineBuyStrategyInput(BaseModel):
    team: Team
    roundNumber: int
    isPistol: bool

class DetermineBuyStrategyOutput(BaseModel):
    strategy: Literal['full-buy', 'force-buy', 'eco']
    reasoning: str

class BuyPhaseInput(BaseModel):
    team: Team
    roundNumber: int
    isPistol: bool

class BuyPhaseOutput(BaseModel):
    updatedTeam: Team

class TeamDataPlayer(BaseModel):
    name: str
    role: str
    nationality: str
    age: int
    photo: Optional[str] = None

class TeamData(BaseModel):
    id: str
    name: str
    acronym: str
    region: Literal['Americas', 'EMEA', 'Pacific', 'China']
    players: conlist(TeamDataPlayer, min_length=5, max_length=5)
    logo: Optional[str] = None
    logoBg: Optional[Literal['blend', 'normal']] = None

class PlayerStatsData(BaseModel):
    aim: Literal['S', 'A', 'B', 'C', 'D']
    hs: int
    support: Literal['S', 'A', 'B', 'C', 'D']
    clutch: Literal['S', 'A', 'B', 'C', 'D']

# NOTA: O dicionário 'teams' com os dados brutos foi removido deste arquivo.
# Ele agora reside em 'data/teams.json' e deve ser carregado separadamente.