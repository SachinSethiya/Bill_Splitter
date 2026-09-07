from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import List, Dict
from backend.models.bill import Bill, Member, Assignment, MemberBreakdown, CalculationResult

# Set precision for Decimal calculations
getcontext().prec = 10


class Calculator:
    """
    Deterministic bill calculator using Decimal for precise monetary calculations.
    
    Calculation methodology:
    1. For each item, split equally among assigned members
    2. Calculate each person's food consumption (sum of their item shares)
    3. Allocate tax, service charge, discount proportionally based on food share
    4. Round final amounts to 2 decimal places
    5. Reconcile any rounding differences deterministically
    """
    
    def __init__(self):
        self.ROUNDING = ROUND_HALF_UP
    
    def calculate(
        self,
        bill: Bill,
        members: List[Member],
        assignments: List[Assignment]
    ) -> CalculationResult:
        """
        Calculate fair shares for all members.
        
        Args:
            bill: The bill with items and charges
            members: List of members
            assignments: List of which members consume which items
            
        Returns:
            CalculationResult with detailed breakdown for each member
        """
        # Validate inputs
        if not members:
            raise ValueError("At least one member is required")
        if not assignments:
            raise ValueError("At least one assignment is required")
        
        # Create member lookup
        member_map = {m.id: m for m in members}
        
        # Create item lookup
        item_map = {item.id: item for item in bill.items}
        
        # Calculate final bill total
        bill_total = (
            bill.subtotal + bill.tax + bill.service_charge - bill.discount
        )
        
        # Initialize member food shares
        member_food_shares: Dict[str, Decimal] = {
            m.id: Decimal('0') for m in members
        }
        
        # Track item details for each member
        member_items: Dict[str, List[dict]] = {
            m.id: [] for m in members
        }
        
        # Process each assignment
        for assignment in assignments:
            if assignment.item_id not in item_map:
                raise ValueError(f"Item {assignment.item_id} not found in bill")
            
            item = item_map[assignment.item_id]
            assigned_member_ids = assignment.member_ids
            
            # Validate all assigned members exist
            for member_id in assigned_member_ids:
                if member_id not in member_map:
                    raise ValueError(f"Member {member_id} not found")
            
            # Calculate share per person for this item
            share_per_person = self._divide_decimal(
                item.total,
                len(assigned_member_ids)
            )
            
            # Add to each member's food share
            for member_id in assigned_member_ids:
                member_food_shares[member_id] += share_per_person
                member_items[member_id].append({
                    'name': item.name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total': item.total,
                    'share': share_per_person
                })
        
        # Verify total food shares equals subtotal
        total_food_shares = sum(member_food_shares.values())
        if total_food_shares != bill.subtotal:
            # Small floating point differences can occur, reconcile
            diff = bill.subtotal - total_food_shares
            if abs(diff) < Decimal('0.01'):
                # Add difference to first member deterministically
                first_member_id = members[0].id
                member_food_shares[first_member_id] += diff
            else:
                raise ValueError(
                    f"Food shares total {total_food_shares} does not match "
                    f"bill subtotal {bill.subtotal}"
                )
        
        # Allocate additional charges proportionally
        member_breakdowns = []
        
        for member in members:
            food_share = member_food_shares[member.id]
            
            # Proportional allocation of charges
            if bill.subtotal > 0:
                tax_share = self._divide_decimal(
                    food_share * bill.tax,
                    bill.subtotal
                )
                service_charge_share = self._divide_decimal(
                    food_share * bill.service_charge,
                    bill.subtotal
                )
                discount_share = self._divide_decimal(
                    food_share * bill.discount,
                    bill.subtotal
                )
            else:
                tax_share = Decimal('0')
                service_charge_share = Decimal('0')
                discount_share = Decimal('0')
            
            # Calculate total
            total = (
                food_share + tax_share + service_charge_share - discount_share
            )
            
            member_breakdowns.append(MemberBreakdown(
                member_id=member.id,
                member_name=member.name,
                items=member_items[member.id],
                food_subtotal=food_share.quantize(Decimal('0.01'), self.ROUNDING),
                tax_share=tax_share.quantize(Decimal('0.01'), self.ROUNDING),
                service_charge_share=service_charge_share.quantize(
                    Decimal('0.01'), self.ROUNDING
                ),
                discount_share=discount_share.quantize(
                    Decimal('0.01'), self.ROUNDING
                ),
                total=total.quantize(Decimal('0.01'), self.ROUNDING)
            ))
        
        # Calculate shares total
        shares_total = sum(
            breakdown.total for breakdown in member_breakdowns
        )
        
        # Reconcile rounding difference
        difference = bill_total - shares_total
        if abs(difference) > Decimal('0.00'):
            # Add difference to first member deterministically
            member_breakdowns[0].total = (
                member_breakdowns[0].total + difference
            ).quantize(Decimal('0.01'), self.ROUNDING)
            shares_total = sum(
                breakdown.total for breakdown in member_breakdowns
            )
        
        # Determine verification status
        verification = (
            "✓ Shares match bill total" 
            if shares_total == bill_total 
            else "⚠ Difference detected"
        )
        
        return CalculationResult(
            members=member_breakdowns,
            bill_total=bill_total.quantize(Decimal('0.01'), self.ROUNDING),
            shares_total=shares_total.quantize(Decimal('0.01'), self.ROUNDING),
            difference=difference.quantize(Decimal('0.01'), self.ROUNDING),
            verification=verification,
            subtotal=bill.subtotal.quantize(Decimal('0.01'), self.ROUNDING),
            tax=bill.tax.quantize(Decimal('0.01'), self.ROUNDING),
            service_charge=bill.service_charge.quantize(Decimal('0.01'), self.ROUNDING),
            discount=bill.discount.quantize(Decimal('0.01'), self.ROUNDING)
        )
    
    def _divide_decimal(self, numerator: Decimal, denominator: int) -> Decimal:
        """
        Divide a Decimal by an integer with proper rounding.
        """
        if denominator == 0:
            raise ValueError("Cannot divide by zero")
        result = numerator / Decimal(denominator)
        return result.quantize(Decimal('0.01'), self.ROUNDING)
