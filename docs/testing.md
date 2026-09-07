# FairShare Testing Guide

## Overview

FairShare has a comprehensive test suite using pytest. Tests cover the calculation engine, validation logic, and API endpoints.

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest backend/tests/test_calculator.py
pytest backend/tests/test_validator.py
pytest backend/tests/test_api.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage
```bash
pytest --cov=backend --cov-report=html
```

### Run Specific Test
```bash
pytest backend/tests/test_calculator.py::test_one_person_consuming_item
```

## Test Structure

### Test Files

1. **test_calculator.py** - Tests for the calculation engine
2. **test_validator.py** - Tests for validation logic
3. **test_api.py** - Tests for API endpoints

### Test Organization

Each test file uses pytest fixtures for common setup:

```python
@pytest.fixture
def calculator():
    return Calculator()

@pytest.fixture
def sample_bill():
    return Bill(...)

@pytest.fixture
def sample_members():
    return [Member(...), ...]
```

## Calculator Tests (`test_calculator.py`)

### Test Categories

#### Basic Item Splitting
- `test_one_person_consuming_item` - Single person pays full amount
- `test_two_people_sharing_item` - Equal split between two people
- `test_three_people_sharing_item` - Equal split among three people
- `test_everyone_sharing_item` - Equal split among all members

#### Consumption Patterns
- `test_different_consumption_levels` - Different people consume different items

#### Charge Allocation
- `test_proportional_tax_allocation` - Tax allocated proportionally
- `test_proportional_service_charge` - Service charge allocated proportionally
- `test_discount_allocation` - Discount allocated proportionally

#### Precision and Rounding
- `test_decimal_rounding` - All values rounded to 2 decimal places
- `test_final_total_reconciliation` - Sum equals bill total

#### Error Handling
- `test_missing_assignment_error` - Error when no assignments
- `test_no_members_error` - Error when no members

#### Edge Cases
- `test_multiple_quantities` - Items with quantity > 1
- `test_printed_total_mismatch_warning` - Handles mismatched totals

### Example Test

```python
def test_two_people_sharing_item(calculator, sample_bill, sample_members):
    """Test when two people share an item equally."""
    assignments = [
        Assignment(item_id="item-1", member_ids=["member-1", "member-2"])
    ]
    
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    rahul_breakdown = next(m for m in result.members if m.member_id == "member-1")
    priya_breakdown = next(m for m in result.members if m.member_id == "member-2")
    
    assert rahul_breakdown.food_subtotal == Decimal("300")
    assert priya_breakdown.food_subtotal == Decimal("300")
```

## Validator Tests (`test_validator.py`)

### Test Categories

#### Bill Validation
- `test_validate_valid_bill` - Valid bill passes
- `test_validate_empty_restaurant_name` - Empty name rejected
- `test_validate_no_items` - Empty items rejected
- `test_validate_duplicate_item_ids` - Duplicate IDs rejected
- `test_validate_subtotal_mismatch` - Subtotal mismatch warning
- `test_validate_total_mismatch` - Total mismatch warning

#### Item Validation
- `test_validate_item_empty_name` - Empty item name rejected
- `test_validate_invalid_quantity` - Invalid quantity rejected
- `test_validate_invalid_unit_price` - Negative price rejected
- `test_validate_item_total_mismatch` - Total mismatch warning

#### Charge Validation
- `test_validate_negative_tax` - Negative tax rejected
- `test_validate_negative_service_charge` - Negative service charge rejected
- `test_validate_negative_discount` - Negative discount rejected

#### Member Validation
- `test_validate_valid_members` - Valid members pass
- `test_validate_too_few_members` - Less than 2 rejected
- `test_validate_too_many_members` - More than 7 rejected
- `test_validate_duplicate_member_ids` - Duplicate IDs rejected
- `test_validate_duplicate_member_names` - Duplicate names rejected

#### Assignment Validation
- `test_validate_valid_assignments` - Valid assignments pass
- `test_validate_no_assignments` - No assignments rejected
- `test_validate_invalid_item_in_assignment` - Invalid item rejected
- `test_validate_invalid_member_in_assignment` - Invalid member rejected
- `test_validate_unassigned_items` - Unassigned items warning

#### Calculation Validation
- `test_validate_calculation_match` - Match passes
- `test_validate_calculation_small_difference` - Small difference passes
- `test_validate_calculation_large_difference` - Large difference fails

## API Tests (`test_api.py`)

### Test Categories

#### Endpoint Tests
- `test_health_check` - Health check endpoint
- `test_serve_index` - Index page serves correctly
- `test_upload_demo_bill` - Demo bill upload works
- `test_upload_without_file` - No file returns error

#### Calculation API
- `test_calculate_endpoint` - Valid calculation works
- `test_calculate_with_too_few_members` - Too few members rejected
- `test_calculate_with_no_assignments` - No assignments rejected
- `test_calculate_with_invalid_item_price` - Invalid price rejected

### Example Test

```python
def test_calculate_endpoint(client):
    """Test calculate endpoint with valid data."""
    payload = {
        "bill": {...},
        "members": [...],
        "assignments": [...]
    }
    
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "members" in data
    assert "bill_total" in data
    assert "verification" in data
```

## Writing New Tests

### Guidelines

1. **Use descriptive test names** that explain what is being tested
2. **Use fixtures** for common setup to avoid repetition
3. **Test one thing per test** - keep tests focused
4. **Use realistic data** - use actual Indian rupee values
5. **Test both success and failure** cases
6. **Test edge cases** - boundary conditions, empty inputs, etc.

### Template

```python
def test_descriptive_name(calculator, sample_bill, sample_members):
    """Brief description of what this test does."""
    # Arrange
    assignments = [...]
    
    # Act
    result = calculator.calculate(sample_bill, sample_members, assignments)
    
    # Assert
    assert result.something == expected_value
```

## Test Data

### Sample Bill
```python
Bill(
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
```

### Sample Members
```python
[
    Member(id="member-1", name="Rahul"),
    Member(id="member-2", name="Priya"),
    Member(id="member-3", name="Aman")
]
```

## Continuous Integration

For CI/CD, tests should run automatically on every push. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
```

## Test Coverage Goals

- **Calculator**: 100% coverage (critical financial logic)
- **Validator**: 95%+ coverage
- **API**: 90%+ coverage
- **Overall**: 90%+ coverage

## Debugging Failed Tests

### Run with Detailed Output
```bash
pytest -v -s
```

### Run with pdb Debugger
```bash
pytest --pdb
```

### Run Specific Failed Test
```bash
pytest backend/tests/test_calculator.py::test_name --pdb
```

### Print Variables
```python
def test_something():
    value = calculate()
    print(f"Value: {value}")  # Will show with -s flag
    assert value == expected
```

## Best Practices

1. **Isolate tests** - Each test should be independent
2. **Clean up** - Don't leave side effects
3. **Use assertions** - Be specific about what you're checking
4. **Document edge cases** - Add comments for complex scenarios
5. **Keep tests fast** - Avoid slow operations in tests
6. **Test error messages** - Verify error messages are helpful
