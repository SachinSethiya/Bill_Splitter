from decimal import Decimal
from typing import List, Dict, Tuple
from backend.models.bill import Bill, BillItem, Member, Assignment


class ValidationError:
    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # "error" or "warning"
    
    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity
        }


class Validator:
    """
    Validates bill data for consistency and correctness.
    """
    
    def validate_bill(self, bill: Bill) -> List[ValidationError]:
        """
        Validate bill structure and data consistency.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for empty restaurant name
        if not bill.restaurant_name or bill.restaurant_name.strip() == "":
            errors.append(ValidationError(
                "restaurant_name",
                "Restaurant name cannot be empty"
            ))
        
        # Validate items
        if not bill.items:
            errors.append(ValidationError(
                "items",
                "Bill must have at least one item"
            ))
        
        # Check for duplicate item IDs
        item_ids = [item.id for item in bill.items]
        if len(item_ids) != len(set(item_ids)):
            errors.append(ValidationError(
                "items",
                "Duplicate item IDs detected"
            ))
        
        # Validate each item
        for item in bill.items:
            item_errors = self._validate_item(item)
            errors.extend(item_errors)
        
        # Calculate expected subtotal from items
        calculated_subtotal = sum(item.total for item in bill.items)
        
        # Check subtotal mismatch
        if calculated_subtotal != bill.subtotal:
            errors.append(ValidationError(
                "subtotal",
                f"Subtotal mismatch: calculated {calculated_subtotal} vs printed {bill.subtotal}",
                severity="warning"
            ))
        
        # Calculate expected total
        calculated_total = (
            bill.subtotal + bill.tax + bill.service_charge - bill.discount
        )
        
        # Check total mismatch
        if calculated_total != bill.printed_total:
            errors.append(ValidationError(
                "printed_total",
                f"Total mismatch: calculated {calculated_total} vs printed {bill.printed_total}",
                severity="warning"
            ))
        
        # Validate charges are non-negative
        if bill.tax < 0:
            errors.append(ValidationError("tax", "Tax cannot be negative"))
        
        if bill.service_charge < 0:
            errors.append(ValidationError(
                "service_charge",
                "Service charge cannot be negative"
            ))
        
        if bill.discount < 0:
            errors.append(ValidationError("discount", "Discount cannot be negative"))
        
        return errors
    
    def _validate_item(self, item: BillItem) -> List[ValidationError]:
        """Validate a single bill item."""
        errors = []
        
        if not item.name or item.name.strip() == "":
            errors.append(ValidationError(
                f"item_{item.id}",
                "Item name cannot be empty"
            ))
        
        if item.quantity <= 0:
            errors.append(ValidationError(
                f"item_{item.id}",
                f"Quantity must be positive (got {item.quantity})"
            ))
        
        if item.unit_price <= 0:
            errors.append(ValidationError(
                f"item_{item.id}",
                f"Unit price must be positive (got {item.unit_price})"
            ))
        
        if item.total < 0:
            errors.append(ValidationError(
                f"item_{item.id}",
                f"Total cannot be negative (got {item.total})"
            ))
        
        # Verify total matches quantity × unit_price
        expected_total = item.quantity * item.unit_price
        if item.total != expected_total:
            errors.append(ValidationError(
                f"item_{item.id}",
                f"Item total {item.total} does not match quantity × unit_price ({expected_total})",
                severity="warning"
            ))
        
        return errors
    
    def validate_members(self, members: List[Member]) -> List[ValidationError]:
        """Validate member list."""
        errors = []
        
        if len(members) < 2:
            errors.append(ValidationError(
                "members",
                f"At least 2 members required (got {len(members)})"
            ))
        
        if len(members) > 7:
            errors.append(ValidationError(
                "members",
                f"Maximum 7 members allowed (got {len(members)})"
            ))
        
        # Check for duplicate member IDs
        member_ids = [m.id for m in members]
        if len(member_ids) != len(set(member_ids)):
            errors.append(ValidationError(
                "members",
                "Duplicate member IDs detected"
            ))
        
        # Check for duplicate names
        names = [m.name.lower() for m in members]
        if len(names) != len(set(names)):
            errors.append(ValidationError(
                "members",
                "Duplicate member names detected"
            ))
        
        return errors
    
    def validate_assignments(
        self,
        assignments: List[Assignment],
        bill: Bill,
        members: List[Member]
    ) -> List[ValidationError]:
        """Validate item assignments."""
        errors = []
        
        if not assignments:
            errors.append(ValidationError(
                "assignments",
                "At least one assignment is required"
            ))
            return errors
        
        # Create lookups
        item_ids = {item.id for item in bill.items}
        member_ids = {m.id for m in members}
        
        assigned_item_ids = set()
        assigned_member_ids = set()
        
        for assignment in assignments:
            # Check item exists
            if assignment.item_id not in item_ids:
                errors.append(ValidationError(
                    f"assignment_{assignment.item_id}",
                    f"Item {assignment.item_id} not found in bill"
                ))
            else:
                assigned_item_ids.add(assignment.item_id)
            
            # Check assigned members exist
            for member_id in assignment.member_ids:
                if member_id not in member_ids:
                    errors.append(ValidationError(
                        f"assignment_{assignment.item_id}",
                        f"Member {member_id} not found"
                    ))
                else:
                    assigned_member_ids.add(member_id)
        
        # Check for unassigned items
        unassigned_items = item_ids - assigned_item_ids
        if unassigned_items:
            errors.append(ValidationError(
                "assignments",
                f"Unassigned items detected: {unassigned_items}",
                severity="warning"
            ))
        
        # Check for members with no assignments
        members_with_assignments = member_ids - assigned_member_ids
        if members_with_assignments:
            errors.append(ValidationError(
                "assignments",
                f"Members with no assignments: {members_with_assignments}",
                severity="warning"
            ))
        
        return errors
    
    def validate_calculation(
        self,
        bill_total: Decimal,
        shares_total: Decimal
    ) -> Tuple[bool, str]:
        """
        Validate that calculated shares match bill total.
        
        Returns:
            (is_valid, message)
        """
        difference = abs(bill_total - shares_total)
        
        if difference == Decimal('0'):
            return True, "✓ Shares match bill total"
        elif difference <= Decimal('0.02'):
            return True, f"⚠ Small difference detected (₹{difference})"
        else:
            return False, f"⚠ Significant difference detected (₹{difference})"
