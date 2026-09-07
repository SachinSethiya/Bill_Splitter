from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import List, Optional
from datetime import date


class BillItem(BaseModel):
    id: str
    name: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    total: Decimal = Field(ge=0)
    confidence: float = Field(ge=0, le=1)

    @field_validator('total')
    def validate_total(cls, v, info):
        if 'quantity' in info.data and 'unit_price' in info.data:
            expected = info.data['quantity'] * info.data['unit_price']
            if v != expected:
                raise ValueError(f'Total {v} does not match quantity × unit_price ({expected})')
        return v


class Member(BaseModel):
    id: str
    name: str = Field(min_length=1, max_length=50)


class Assignment(BaseModel):
    item_id: str
    member_ids: List[str] = Field(min_length=1)


class Bill(BaseModel):
    restaurant_name: str = Field(min_length=1, max_length=100)
    date: str
    bill_number: Optional[str] = None
    items: List[BillItem] = Field(min_length=1)
    subtotal: Decimal = Field(ge=0)
    tax: Decimal = Field(ge=0)
    service_charge: Decimal = Field(ge=0)
    discount: Decimal = Field(ge=0)
    printed_total: Decimal = Field(ge=0)

    @field_validator('date')
    def validate_date(cls, v):
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError('Date must be in ISO format (YYYY-MM-DD)')
        return v


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
