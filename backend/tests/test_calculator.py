import pytest
from decimal import Decimal
from backend.services.calculator import Calculator
from backend.models.bill import Bill, BillItem, Member, Assignment


@pytest.fixture
def calculator():
    return Calculator()


@pytest.fixture
def sample_bill():
    return Bill(
        restaurant_name="Test Restaurant",
        date="2024-01-15",
        bill_number="INV-001",
        items=[
            BillItem(
                id="item-1",
                name="Biryani",
                quantity=2,
                unit_price=Decimal("300"),
                total=Decimal("600"),
                confidence=0.95
            ),
            BillItem(
                id="item-2",
                name="Coke",
                quantity=2,
                unit_price=Decimal("60"),
                total=Decimal("120"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("720"),
        tax=Decimal("65"),
        service_charge=Decimal("72"),
        discount=Decimal("0"),
        printed_total=Decimal("857")
    )


@pytest.fixture
def sample_members():
    return [
        Member(id="member-1", name="Rahul"),
        Member(id="member-2", name="Priya"),
        Member(id="member-3", name="Aman")
    ]


def test_one_person_consuming_item(calculator, sample_bill, sample_members):
    """Test when one person consumes an item entirely."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    # Rahul should pay full amount of item-1
    rahul_breakdown = next(m for m in result.members if m.member_id == "member-1")
    assert rahul_breakdown.food_subtotal == Decimal("600")


def test_two_people_sharing_item(calculator, sample_bill, sample_members):
    """Test when two people share an item equally."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    # Both should pay half of item-1
    rahul_breakdown = next(m for m in result.members if m.member_id == "member-1")
    priya_breakdown = next(m for m in result.members if m.member_id == "member-2")
    
    assert rahul_breakdown.food_subtotal == Decimal("300")
    assert priya_breakdown.food_subtotal == Decimal("300")


def test_three_people_sharing_item(calculator, sample_bill, sample_members):
    """Test when three people share an item equally."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2", "member-3"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    # Each should pay 1/3 of item-1
    for member in result.members:
        assert member.food_subtotal == Decimal("200")


def test_everyone_sharing_item(calculator, sample_bill, sample_members):
    """Test when everyone shares an item."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2", "member-3"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    # Each should pay equal share
    for member in result.members:
        assert member.food_subtotal == Decimal("200")


def test_different_consumption_levels(calculator, sample_bill, sample_members):
    """Test different consumption patterns."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2"]),
        Assignment(item_id="item-2", member_ids=["member-2", "member-3"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    rahul_breakdown = next(m for m in result.members if m.member_id == "member-1")
    priya_breakdown = next(m for m in result.members if m.member_id == "member-2")
    aman_breakdown = next(m for m in result.members if m.member_id == "member-3")
    
    # Rahul: half of item-1 = 300
    assert rahul_breakdown.food_subtotal == Decimal("300")
    # Priya: half of item-1 + half of item-2 = 300 + 60 = 360
    assert priya_breakdown.food_subtotal == Decimal("360")
    # Aman: half of item-2 = 60
    assert aman_breakdown.food_subtotal == Decimal("60")


def test_proportional_tax_allocation(calculator, sample_bill, sample_members):
    """Test tax is allocated proportionally to food consumption."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1"]),
        Assignment(item_id="item-2", member_ids=["member-2"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    rahul_breakdown = next(m for m in result.members if m.member_id == "member-1")
    priya_breakdown = next(m for m in result.members if m.member_id == "member-2")
    
    # Rahul's food share: 600/720 = 5/6 of subtotal
    # Rahul's tax share: 5/6 * 65 = 54.17
    expected_rahul_tax = (Decimal("600") / Decimal("720")) * Decimal("65")
    assert rahul_breakdown.tax_share == expected_rahul_tax.quantize(Decimal("0.01"))
    
    # Priya's food share: 120/720 = 1/6 of subtotal
    # Priya's tax share: 1/6 * 65 = 10.83
    expected_priya_tax = (Decimal("120") / Decimal("720")) * Decimal("65")
    assert priya_breakdown.tax_share == expected_priya_tax.quantize(Decimal("0.01"))


def test_proportional_service_charge(calculator, sample_bill, sample_members):
    """Test service charge is allocated proportionally."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1"]),
        Assignment(item_id="item-2", member_ids=["member-2"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    rahul_breakdown = next(m for m in result.members if m.member_id == "member-1")
    
    # Rahul's service charge share: 5/6 * 72 = 60
    expected_sc = (Decimal("600") / Decimal("720")) * Decimal("72")
    assert rahul_breakdown.service_charge_share == expected_sc.quantize(Decimal("0.01"))


def test_discount_allocation(calculator, sample_bill, sample_members):
    """Test discount is allocated proportionally."""
    bill_with_discount = Bill(
        restaurant_name="Test Restaurant",
        date="2024-01-15",
        bill_number="INV-001",
        items=[
            BillItem(
                id="item-1",
                name="Biryani",
                quantity=2,
                unit_price=Decimal("300"),
                total=Decimal("600"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("600"),
        tax=Decimal("54"),
        service_charge=Decimal("60"),
        discount=Decimal("50"),
        printed_total=Decimal("664")
    )
    
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2"])
    ]
    
    result = calculator.calculate(bill_with_discount, sample_members[:2], assignments)
    
    # Each should get half of discount
    for member in result.members:
        assert member.discount_share == Decimal("25")


def test_decimal_rounding(calculator, sample_bill, sample_members):
    """Test that amounts are properly rounded to 2 decimal places."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2", "member-3"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    # Check that all monetary values are rounded to 2 decimal places
    for member in result.members:
        assert member.food_subtotal == member.food_subtotal.quantize(Decimal("0.01"))
        assert member.tax_share == member.tax_share.quantize(Decimal("0.01"))
        assert member.service_charge_share == member.service_charge_share.quantize(Decimal("0.01"))
        assert member.total == member.total.quantize(Decimal("0.01"))


def test_final_total_reconciliation(calculator, sample_bill, sample_members):
    """Test that sum of member totals equals bill total."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2"]),
        Assignment(item_id="item-2", member_ids=["member-2", "member-3"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    # Sum of all member totals should equal bill total
    shares_total = sum(m.total for m in result.members)
    assert shares_total == result.bill_total
    assert result.difference == Decimal("0")


def test_missing_assignment_error(calculator, sample_bill, sample_members):
    """Test error when no assignments provided."""
    with pytest.raises(ValueError, match="At least one assignment is required"):
        calculator.calculate(sample_bill, sample_members, [])


def test_invalid_price_in_item(calculator):
    """Test that invalid prices are caught by model validation."""
    with pytest.raises(ValueError):
        BillItem(
            id="item-1",
            name="Test",
            quantity=1,
            unit_price=Decimal("-10"),
            total=Decimal("-10"),
            confidence=0.95
        )


def test_invalid_quantity_in_item(calculator):
    """Test that invalid quantities are caught by model validation."""
    with pytest.raises(ValueError):
        BillItem(
            id="item-1",
            name="Test",
            quantity=0,
            unit_price=Decimal("10"),
            total=Decimal("0"),
            confidence=0.95
        )


def test_printed_total_mismatch_warning(calculator, sample_bill, sample_members):
    """Test that printed total mismatch is handled."""
    # Create bill with mismatched total
    mismatched_bill = Bill(
        restaurant_name="Test Restaurant",
        date="2024-01-15",
        bill_number="INV-001",
        items=sample_bill.items,
        subtotal=sample_bill.subtotal,
        tax=sample_bill.tax,
        service_charge=sample_bill.service_charge,
        discount=sample_bill.discount,
        printed_total=Decimal("1000")  # Wrong total
    )
    
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1"]),
        Assignment(item_id="item-2", member_ids=["member-2"])
    ]
    
    result = calculator.calculate(mismatched_bill, sample_members, assignments)
    
    # Calculator should still work, using calculated total
    assert result.bill_total == Decimal("857")
    assert result.verification == "✓ Shares match bill total"


def test_multiple_quantities(calculator, sample_bill, sample_members):
    """Test items with multiple quantities."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1"]),
        Assignment(item_id="item-2", member_ids=["member-2"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    rahul_breakdown = next(m for m in result.members if m.member_id == "member-1")
    
    # Rahul should get full amount of item-1 (2 × 300 = 600)
    assert rahul_breakdown.food_subtotal == Decimal("600")


def test_no_members_error(calculator, sample_bill):
    """Test error when no members provided."""
    with pytest.raises(ValueError, match="At least one member is required"):
        calculator.calculate(sample_bill, [], [])
