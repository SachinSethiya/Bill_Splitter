import pytest
from decimal import Decimal
from backend.services.validator import Validator, ValidationError
from backend.models.bill import Bill, BillItem, Member, Assignment


@pytest.fixture
def validator():
    return Validator()


@pytest.fixture
def valid_bill():
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
            )
        ],
        subtotal=Decimal("600"),
        tax=Decimal("54"),
        service_charge=Decimal("60"),
        discount=Decimal("0"),
        printed_total=Decimal("714")
    )


@pytest.fixture
def valid_members():
    return [
        Member(id="member-1", name="Rahul"),
        Member(id="member-2", name="Priya")
    ]


def test_validate_valid_bill(validator, valid_bill):
    """Test validation of a valid bill."""
    errors = validator.validate_bill(valid_bill)
    assert len(errors) == 0


def test_validate_empty_restaurant_name(validator):
    """Test validation of empty restaurant name."""
    bill = Bill(
        restaurant_name="",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("100"),
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("100")
    )
    
    errors = validator.validate_bill(bill)
    assert any(e.field == "restaurant_name" for e in errors)


def test_validate_no_items(validator):
    """Test validation of bill with no items."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[],
        subtotal=Decimal("0"),
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("0")
    )
    
    errors = validator.validate_bill(bill)
    assert any(e.field == "items" for e in errors)


def test_validate_duplicate_item_ids(validator):
    """Test validation of duplicate item IDs."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test 1",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            ),
            BillItem(
                id="item-1",
                name="Test 2",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("200"),
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("200")
    )
    
    errors = validator.validate_bill(bill)
    assert any("duplicate" in e.message.lower() for e in errors)


def test_validate_item_empty_name(validator):
    """Test validation of item with empty name."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("100"),
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("100")
    )
    
    errors = validator.validate_bill(bill)
    assert any("name" in e.message.lower() for e in errors)


def test_validate_invalid_quantity(validator):
    """Test validation of invalid quantity."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=0,
                unit_price=Decimal("100"),
                total=Decimal("0"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("0"),
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("0")
    )
    
    errors = validator.validate_bill(bill)
    assert any("quantity" in e.message.lower() for e in errors)


def test_validate_invalid_unit_price(validator):
    """Test validation of invalid unit price."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=1,
                unit_price=Decimal("-10"),
                total=Decimal("-10"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("-10"),
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("-10")
    )
    
    errors = validator.validate_bill(bill)
    assert any("price" in e.message.lower() for e in errors)


def test_validate_item_total_mismatch(validator):
    """Test validation of item total mismatch."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=2,
                unit_price=Decimal("100"),
                total=Decimal("250"),  # Should be 200
                confidence=0.95
            )
        ],
        subtotal=Decimal("250"),
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("250")
    )
    
    errors = validator.validate_bill(bill)
    assert any("total" in e.message.lower() for e in errors)


def test_validate_subtotal_mismatch(validator):
    """Test validation of subtotal mismatch."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("150"),  # Mismatch
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("150")
    )
    
    errors = validator.validate_bill(bill)
    assert any(e.field == "subtotal" and e.severity == "warning" for e in errors)


def test_validate_total_mismatch(validator):
    """Test validation of printed total mismatch."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("100"),
        tax=Decimal("10"),
        service_charge=Decimal("10"),
        discount=Decimal("0"),
        printed_total=Decimal("150")  # Should be 120
    )
    
    errors = validator.validate_bill(bill)
    assert any(e.field == "printed_total" and e.severity == "warning" for e in errors)


def test_validate_negative_tax(validator):
    """Test validation of negative tax."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("100"),
        tax=Decimal("-10"),
        service_charge=Decimal("0"),
        discount=Decimal("0"),
        printed_total=Decimal("90")
    )
    
    errors = validator.validate_bill(bill)
    assert any(e.field == "tax" for e in errors)


def test_validate_negative_service_charge(validator):
    """Test validation of negative service charge."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("100"),
        tax=Decimal("0"),
        service_charge=Decimal("-10"),
        discount=Decimal("0"),
        printed_total=Decimal("90")
    )
    
    errors = validator.validate_bill(bill)
    assert any(e.field == "service_charge" for e in errors)


def test_validate_negative_discount(validator):
    """Test validation of negative discount."""
    bill = Bill(
        restaurant_name="Test",
        date="2024-01-15",
        items=[
            BillItem(
                id="item-1",
                name="Test",
                quantity=1,
                unit_price=Decimal("100"),
                total=Decimal("100"),
                confidence=0.95
            )
        ],
        subtotal=Decimal("100"),
        tax=Decimal("0"),
        service_charge=Decimal("0"),
        discount=Decimal("-10"),
        printed_total=Decimal("90")
    )
    
    errors = validator.validate_bill(bill)
    assert any(e.field == "discount" for e in errors)


def test_validate_valid_members(validator, valid_members):
    """Test validation of valid members."""
    errors = validator.validate_members(valid_members)
    assert len(errors) == 0


def test_validate_too_few_members(validator):
    """Test validation when too few members."""
    members = [Member(id="member-1", name="Rahul")]
    errors = validator.validate_members(members)
    assert any("at least 2" in e.message.lower() for e in errors)


def test_validate_too_many_members(validator):
    """Test validation when too many members."""
    members = [Member(id=f"member-{i}", name=f"Member {i}") for i in range(8)]
    errors = validator.validate_members(members)
    assert any("maximum 7" in e.message.lower() for e in errors)


def test_validate_duplicate_member_ids(validator):
    """Test validation of duplicate member IDs."""
    members = [
        Member(id="member-1", name="Rahul"),
        Member(id="member-1", name="Priya")
    ]
    errors = validator.validate_members(members)
    assert any("duplicate" in e.message.lower() for e in errors)


def test_validate_duplicate_member_names(validator):
    """Test validation of duplicate member names."""
    members = [
        Member(id="member-1", name="Rahul"),
        Member(id="member-2", name="rahul")
    ]
    errors = validator.validate_members(members)
    assert any("duplicate" in e.message.lower() for e in errors)


def test_validate_valid_assignments(validator, valid_bill, valid_members):
    """Test validation of valid assignments."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2"])
    ]
    errors = validator.validate_assignments(assignments, valid_bill, valid_members)
    assert len(errors) == 0


def test_validate_no_assignments(validator, valid_bill, valid_members):
    """Test validation when no assignments."""
    errors = validator.validate_assignments([], valid_bill, valid_members)
    assert any("at least one" in e.message.lower() for e in errors)


def test_validate_invalid_item_in_assignment(validator, valid_bill, valid_members):
    """Test validation of invalid item in assignment."""
    assignments = [
        Assignment(item_id="item-999", member_ids=["member-1"])
    ]
    errors = validator.validate_assignments(assignments, valid_bill, valid_members)
    assert any("not found" in e.message.lower() for e in errors)


def test_validate_invalid_member_in_assignment(validator, valid_bill, valid_members):
    """Test validation of invalid member in assignment."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-999"])
    ]
    errors = validator.validate_assignments(assignments, valid_bill, valid_members)
    assert any("not found" in e.message.lower() for e in errors)


def test_validate_unassigned_items(validator, valid_bill, valid_members):
    """Test validation of unassigned items."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1"])
    ]
    # Add another item that won't be assigned
    valid_bill.items.append(
        BillItem(
            id="item-2",
            name="Test",
            quantity=1,
            unit_price=Decimal("100"),
            total=Decimal("100"),
            confidence=0.95
        )
    )
    errors = validator.validate_assignments(assignments, valid_bill, valid_members)
    assert any("unassigned" in e.message.lower() for e in errors)


def test_validate_calculation_match(validator):
    """Test validation when calculation matches."""
    is_valid, message = validator.validate_calculation(
        Decimal("100"),
        Decimal("100")
    )
    assert is_valid is True
    assert "match" in message.lower()


def test_validate_calculation_small_difference(validator):
    """Test validation with small difference."""
    is_valid, message = validator.validate_calculation(
        Decimal("100"),
        Decimal("100.01")
    )
    assert is_valid is True
    assert "small difference" in message.lower()


def test_validate_calculation_large_difference(validator):
    """Test validation with large difference."""
    is_valid, message = validator.validate_calculation(
        Decimal("100"),
        Decimal("105")
    )
    assert is_valid is False
    assert "significant difference" in message.lower()
