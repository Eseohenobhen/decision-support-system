from decimal import Decimal

from app.services.property_service import create_property, list_properties, get_property
from app.services.fund_service import create_fund, list_funds
from app.schemas.property import PropertyCreate
from app.schemas.fund import PropertyFundCreate


def test_create_and_get_property(db_session, manager_user):
    property_in = PropertyCreate(
        code="TEST-PROP",
        name="Test Property",
        address="100 Test St",
        city="Lagos",
        state="Lagos",
        country="Nigeria",
        total_units=20,
        manager_id=manager_user.id,
    )
    property_ = create_property(db_session, property_in)
    assert property_.code == "TEST-PROP"
    assert property_.name == "Test Property"

    fetched = get_property(db_session, property_.id)
    assert fetched is not None
    assert fetched.code == "TEST-PROP"


def test_list_properties_respects_manager_filter(db_session, manager_user, admin_user):
    property_in = PropertyCreate(
        code="FILTER-TEST",
        name="Filter Test",
        address="200 Filter St",
        city="Lagos",
        state="Lagos",
        country="Nigeria",
        total_units=10,
        manager_id=manager_user.id,
    )
    create_property(db_session, property_in)

    manager_props = list_properties(db_session, manager_user)
    assert len(manager_props) == 1

    admin_props = list_properties(db_session, admin_user)
    assert len(admin_props) >= 1


def test_create_and_list_funds(db_session, manager_user, property_with_fund):
    property_, existing_fund = property_with_fund

    fund_in = PropertyFundCreate(
        property_id=property_.id,
        fiscal_year=2027,
        annual_budget=Decimal("150000"),
        current_balance=Decimal("140000"),
        reserved_balance=Decimal("10000"),
        currency="NGN",
    )
    fund = create_fund(db_session, fund_in)
    assert fund.fiscal_year == 2027
    assert fund.annual_budget == Decimal("150000")

    funds = list_funds(db_session, manager_user)
    assert len(funds) >= 1
