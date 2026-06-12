from decimal import Decimal, ROUND_HALF_UP

from app.schemas.dss import DSSItemInput, DSSRankedItem

URGENCY_WEIGHT = Decimal("0.4")
IMPACT_WEIGHT = Decimal("0.3")
ASSET_IMPORTANCE_WEIGHT = Decimal("0.2")
COST_WEIGHT = Decimal("0.1")
MAX_COST_FACTOR = Decimal("10")
TWO_PLACES = Decimal("0.01")


def quantize_score(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def calculate_cost_factor(cost: Decimal, highest_cost: Decimal) -> Decimal:
    if highest_cost <= 0:
        return Decimal("0.00")
    return quantize_score((cost / highest_cost) * MAX_COST_FACTOR)


def calculate_priority_score(
    urgency: Decimal,
    impact: Decimal,
    asset_importance: Decimal,
    cost_factor: Decimal,
) -> Decimal:
    score = (
        (urgency * URGENCY_WEIGHT)
        + (impact * IMPACT_WEIGHT)
        + (asset_importance * ASSET_IMPORTANCE_WEIGHT)
        - (cost_factor * COST_WEIGHT)
    )
    return quantize_score(score)


def recommendation_for_score(priority_score: Decimal) -> str:
    if priority_score >= Decimal("7.00"):
        return "Fund immediately"
    if priority_score >= Decimal("5.00"):
        return "Schedule after critical items"
    return "Defer or review scope"


def rank_recommendations(items: list[DSSItemInput]) -> list[DSSRankedItem]:
    highest_cost = max((item.cost for item in items), default=Decimal("0.00"))
    scored_items: list[DSSRankedItem] = []

    for item in items:
        cost_factor = calculate_cost_factor(item.cost, highest_cost)
        priority_score = calculate_priority_score(
            urgency=item.urgency,
            impact=item.impact,
            asset_importance=item.asset_importance,
            cost_factor=cost_factor,
        )
        scored_items.append(
            DSSRankedItem(
                rank=0,
                item_id=item.item_id,
                title=item.title,
                urgency=item.urgency,
                impact=item.impact,
                asset_importance=item.asset_importance,
                cost=item.cost,
                cost_factor=cost_factor,
                priority_score=priority_score,
                recommendation=recommendation_for_score(priority_score),
            )
        )

    scored_items.sort(
        key=lambda item: (
            item.priority_score,
            item.urgency,
            item.impact,
            -item.cost,
        ),
        reverse=True,
    )

    for index, item in enumerate(scored_items, start=1):
        item.rank = index

    return scored_items
