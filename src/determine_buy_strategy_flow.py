
from src.data_structures import (
    DetermineBuyStrategyInput,
    DetermineBuyStrategyOutput,
)


def determine_buy_strategy(
    input_data: DetermineBuyStrategyInput,
) -> DetermineBuyStrategyOutput:
    """
    A flow to determine a team's buy strategy for a round.
    """
    team = input_data.team
    
    # Ensure players have credits, default to 0 if not present
    credits_list = [p.credits for p in team.players if p.credits is not None]
    if not credits_list:
        average_credits = 0
    else:
        average_credits = sum(credits_list) / len(credits_list)

    # Simplified logic based on the user's guide
    if input_data.isPistol:
        return DetermineBuyStrategyOutput(
            strategy="full-buy", reasoning="Pistol round, buying what is possible."
        )

    loss_bonus = (team.lossStreak or 0) * 500
    next_round_min_eco = 1900 + loss_bonus

    # High economy, always buy
    if average_credits > 5000:
        return DetermineBuyStrategyOutput(
            strategy="full-buy",
            reasoning="High economy, full buy to press advantage.",
        )

    # Force buy conditions
    if 3500 < average_credits < 4500:
        # Can afford a decent buy, but might want to save if loss streak is high
        if (team.lossStreak or 0) >= 2:
            return DetermineBuyStrategyOutput(
                strategy="eco",
                reasoning="On a loss streak, saving for a better buy next round.",
            )
        return DetermineBuyStrategyOutput(
            strategy="force-buy", reasoning="Decent economy, force buying to contest."
        )

    if average_credits < next_round_min_eco + 1500:
        return DetermineBuyStrategyOutput(
            strategy="eco", reasoning="Low on credits, saving for a full buy."
        )

    # Default to full buy if enough credits
    return DetermineBuyStrategyOutput(
        strategy="full-buy", reasoning="Sufficient credits for a full buy."
    )
