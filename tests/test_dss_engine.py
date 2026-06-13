from decimal import Decimal

from app.services.dss_engine import (
    calculate_cost_factor,
    calculate_priority_score,
    recommendation_for_score,
    rank_recommendations,
)
from app.schemas.dss import DSSItemInput


def test_calculate_cost_factor_when_highest_cost_zero():
    assert calculate_cost_factor(Decimal("100"), Decimal("0")) == Decimal("0.00")


def test_calculate_priority_score_and_recommendation():
    cost_factor = Decimal("2.50")
    score = calculate_priority_score(
        urgency=Decimal("8.00"),
        impact=Decimal("7.00"),
        asset_importance=Decimal("6.00"),
        cost_factor=cost_factor,
    )
    assert score == Decimal("6.25")
    assert recommendation_for_score(score) == "Schedule after critical items"


def test_rank_recommendations_produces_ordered_ranks():
    items = [
        DSSItemInput(item_id=1, title="Item A", urgency=Decimal("9.00"), impact=Decimal("5.00"), asset_importance=Decimal("4.50"), cost=Decimal("2000")),
        DSSItemInput(item_id=2, title="Item B", urgency=Decimal("6.00"), impact=Decimal("6.00"), asset_importance=Decimal("6.00"), cost=Decimal("500")),
        DSSItemInput(item_id=3, title="Item C", urgency=Decimal("3.00"), impact=Decimal("3.00"), asset_importance=Decimal("3.00"), cost=Decimal("10000")),
    ]

    ranked = rank_recommendations(items)
    assert [item.item_id for item in ranked] == [1, 2, 3]
    assert [item.rank for item in ranked] == [1, 2, 3]
    assert ranked[0].recommendation in {"Fund immediately", "Schedule after critical items", "Defer or review scope"}
