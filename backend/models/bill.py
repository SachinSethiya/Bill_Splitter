from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import List, Optional
from datetime import date


class BillItem(BaseModel):
    id: str
    name: str
    quantity: int
    unit_price: Decimal
    total: Decimal
    confidence: float


class Member(BaseModel):
    id: str
    name: str = Field(min_length=1, max_length=50)


class Assignment(BaseModel):
    item_id: str
    member_ids: List[str] = Field(min_length=1)


class Bill(BaseModel):
    restaurant_name: str
    date: str
    bill_number: Optional[str] = None
    items: List[BillItem]
    subtotal: Decimal
    tax: Decimal
    service_charge: Decimal
    discount: Decimal
    printed_total: Decimal


class MemberBreakdown(BaseModel):
    member_id: str
    member_name: str
    items: List[dict]
    food_subtotal: Decimal
    tax_share: Decimal
    service_charge_share: Decimal
    discount_share: Decimal
    total: Decimal


class CalculationResult(BaseModel):
    members: List[MemberBreakdown]
    bill_total: Decimal
    shares_total: Decimal
    difference: Decimal
    verification: str
    subtotal: Decimal
    tax: Decimal
    service_charge: Decimal
    discount: Decimal
