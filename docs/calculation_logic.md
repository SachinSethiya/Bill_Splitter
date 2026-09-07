# FairShare Calculation Logic

## Overview

FairShare uses a deterministic calculation algorithm to ensure fair and accurate bill splitting. All monetary calculations use Python's `Decimal` type to avoid floating-point errors.

## Core Principles

1. **Deterministic**: Same inputs always produce same outputs
2. **Precise**: Uses Decimal arithmetic, never floating-point
3. **Fair**: Charges allocated proportionally to consumption
4. **Transparent**: Clear breakdown of each person's share
5. **Consistent**: Sum of shares always equals bill total

## Calculation Steps

### Step 1: Item Splitting

For each item, the total cost is divided equally among all assigned members.

**Formula:**
```
share_per_person = item_total / number_of_assigned_members
```

**Examples:**
- Item: Chicken Biryani (2 × ₹300 = ₹600)
- Assigned to: Rahul, Priya
- Rahul's share: ₹600 / 2 = ₹300
- Priya's share: ₹600 / 2 = ₹300

- Item: Water (1 × ₹30 = ₹30)
- Assigned to: Rahul, Priya, Aman (3 people)
- Each person's share: ₹30 / 3 = ₹10

### Step 2: Calculate Food Shares

Each person's food share is the sum of all item shares they consume.

**Formula:**
```
food_share = Σ(item_shares_for_person)
```

**Example:**
- Rahul's items:
  - Chicken Biryani: ₹300
  - Water: ₹10
- Rahul's food share: ₹300 + ₹10 = ₹310

### Step 3: Allocate Additional Charges Proportionally

Tax, service charge, and discount are allocated proportionally based on each person's food share relative to the subtotal.

**Formulas:**
```
tax_share = (food_share / subtotal) × tax
service_charge_share = (food_share / subtotal) × service_charge
discount_share = (food_share / subtotal) × discount
```

**Example:**
- Bill subtotal: ₹1100
- Rahul's food share: ₹310
- Total tax: ₹99
- Rahul's tax share: (₹310 / ₹1100) × ₹99 = ₹27.81

**Important:** Charges are NOT divided equally by number of people. They are proportional to consumption.

### Step 4: Calculate Final Amount

Each person's final amount is:

**Formula:**
```
final_amount = food_share + tax_share + service_charge_share - discount_share
```

**Example:**
- Rahul's food share: ₹310
- Rahul's tax share: ₹27.81
- Rahul's service charge share: ₹31.00
- Rahul's discount share: ₹0
- Rahul's final: ₹310 + ₹27.81 + ₹31.00 = ₹368.81

### Step 5: Rounding

All monetary values are rounded to 2 decimal places using "round half up" strategy.

**Example:**
- ₹27.813 → ₹27.81
- ₹27.815 → ₹27.82
- ₹27.817 → ₹27.82

### Step 6: Reconciliation

After rounding, the sum of all member totals might not exactly equal the bill total due to rounding errors. The system reconciles this deterministically:

1. Calculate the difference: `bill_total - sum(member_totals)`
2. If difference is non-zero, add it to the first member's total
3. This ensures: `sum(member_totals) == bill_total`

**Example:**
- Bill total: ₹1309.00
- Sum of member totals after rounding: ₹1308.99
- Difference: ₹0.01
- Add ₹0.01 to first member's total
- Final sum: ₹1309.00 ✓

## Complete Example

### Bill Data
```
Restaurant: Spice Garden
Items:
  - Chicken Biryani: 2 × ₹300 = ₹600
  - Coke: 2 × ₹60 = ₹120
  - Paneer Tikka: 1 × ₹350 = ₹350
  - Water: 1 × ₹30 = ₹30
Subtotal: ₹1100
GST: ₹99
Service Charge: ₹110
Discount: ₹0
Total: ₹1309
```

### Members
- Rahul
- Priya
- Aman

### Assignments
- Chicken Biryani: Rahul, Priya
- Coke: Rahul, Aman
- Paneer Tikka: Priya, Aman
- Water: Everyone

### Calculation

**Step 1: Item Splitting**
- Chicken Biryani (₹600): Rahul ₹300, Priya ₹300
- Coke (₹120): Rahul ₹60, Aman ₹60
- Paneer Tikka (₹350): Priya ₹175, Aman ₹175
- Water (₹30): Everyone ₹10 each

**Step 2: Food Shares**
- Rahul: ₹300 + ₹60 + ₹10 = ₹370
- Priya: ₹300 + ₹175 + ₹10 = ₹485
- Aman: ₹60 + ₹175 + ₹10 = ₹245

**Verification: ₹370 + ₹485 + ₹245 = ₹1100 ✓**

**Step 3: Proportional Charges**
- Rahul's tax: (₹370/₹1100) × ₹99 = ₹33.36
- Priya's tax: (₹485/₹1100) × ₹99 = ₹43.68
- Aman's tax: (₹245/₹1100) × ₹99 = ₹21.96

- Rahul's service charge: (₹370/₹1100) × ₹110 = ₹37.00
- Priya's service charge: (₹485/₹1100) × ₹110 = ₹48.50
- Aman's service charge: (₹245/₹1100) × ₹110 = ₹24.50

**Step 4: Final Amounts**
- Rahul: ₹370 + ₹33.36 + ₹37.00 = ₹440.36
- Priya: ₹485 + ₹43.68 + ₹48.50 = ₹577.18
- Aman: ₹245 + ₹21.96 + ₹24.50 = ₹291.46

**Verification: ₹440.36 + ₹577.18 + ₹291.46 = ₹1309.00 ✓**

## Edge Cases

### Unassigned Items
If an item is not assigned to anyone, the validator will show a warning. The calculation will not proceed until all items are assigned.

### Single Person Consumption
If an item is consumed by only one person, that person pays the full amount.

### Everyone Sharing
If an item is shared by everyone, it's divided equally among all members.

### Zero Subtotal
If subtotal is ₹0 (shouldn't happen in normal bills), all charge allocations are ₹0.

### Negative Values
The validator prevents negative quantities, prices, and charges.

### Rounding Differences
Small rounding differences (≤ ₹0.02) are automatically reconciled. Larger differences indicate a calculation error.

## Implementation Details

### Decimal Precision
```python
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 10  # Sufficient for 2 decimal places
ROUNDING = ROUND_HALF_UP
```

### Division Helper
```python
def _divide_decimal(numerator: Decimal, denominator: int) -> Decimal:
    result = numerator / Decimal(denominator)
    return result.quantize(Decimal('0.01'), ROUNDING)
```

### Reconciliation
```python
difference = bill_total - shares_total
if abs(difference) > Decimal('0.00'):
    member_breakdowns[0].total += difference
    member_breakdowns[0].total = member_breakdowns[0].total.quantize(
        Decimal('0.01'), ROUNDING
    )
```

## Testing

The calculation logic is thoroughly tested in `backend/tests/test_calculator.py`:

- One person consuming item
- Two people sharing item
- Three people sharing item
- Everyone sharing item
- Different consumption levels
- Proportional GST
- Proportional service charge
- Discount allocation
- Decimal rounding
- Final total reconciliation
- Missing assignment
- Invalid price
- Invalid quantity
- Printed total mismatch
- Multiple quantities

All tests use realistic Indian rupee values.
