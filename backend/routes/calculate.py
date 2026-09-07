from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import List
from backend.services.calculator import Calculator
from backend.services.validator import Validator

router = APIRouter()
calculator = Calculator()
validator = Validator()


class MemberInput(BaseModel):
    id: str
    name: str


class AssignmentInput(BaseModel):
    item_id: str
    member_ids: List[str]


class BillInput(BaseModel):
    restaurant_name: str
    date: str
    bill_number: str = None
    items: List[dict]
    subtotal: Decimal
    tax: Decimal
    service_charge: Decimal
    discount: Decimal
    printed_total: Decimal


class CalculateRequest(BaseModel):
    bill: BillInput
    members: List[MemberInput]
    assignments: List[AssignmentInput]


@router.post("/calculate")
async def calculate_shares(request: CalculateRequest):
    """
    Calculate fair shares for all members based on bill and assignments.
    """
    try:
        # Convert input to proper models
        from backend.models.bill import Bill, BillItem, Member, Assignment
        
        # Convert bill items
        bill_items = [
            BillItem(
                id=item['id'],
                name=item['name'],
                quantity=item['quantity'],
                unit_price=Decimal(str(item['unit_price'])),
                total=Decimal(str(item['total'])),
                confidence=item.get('confidence', 0)
            )
            for item in request.bill.items
        ]
        
        # Create bill
        bill = Bill(
            restaurant_name=request.bill.restaurant_name,
            date=request.bill.date,
            bill_number=request.bill.bill_number,
            items=bill_items,
            subtotal=Decimal(str(request.bill.subtotal)),
            tax=Decimal(str(request.bill.tax)),
            service_charge=Decimal(str(request.bill.service_charge)),
            discount=Decimal(str(request.bill.discount)),
            printed_total=Decimal(str(request.bill.printed_total))
        )
        
        # Create members
        members = [
            Member(id=m.id, name=m.name)
            for m in request.members
        ]
        
        # Create assignments
        assignments = [
            Assignment(item_id=a.item_id, member_ids=a.member_ids)
            for a in request.assignments
        ]
        
        # Validate
        bill_errors = validator.validate_bill(bill)
        member_errors = validator.validate_members(members)
        assignment_errors = validator.validate_assignments(assignments, bill, members)
        
        all_errors = bill_errors + member_errors + assignment_errors
        
        # Return errors if any critical ones exist
        critical_errors = [e for e in all_errors if e.severity == "error"]
        if critical_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "errors": [e.to_dict() for e in critical_errors]
                }
            )
        
        # Calculate shares
        result = calculator.calculate(bill, members, assignments)
        
        return result.model_dump()
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
