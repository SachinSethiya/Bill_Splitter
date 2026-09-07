from decimal import Decimal
from typing import Optional
from backend.models.bill import Bill, BillItem
import os


class BillParser:
    """
    Bill parser service that extracts data from bill images.
    
    If AI/OCR API is configured, uses it for extraction.
    Otherwise, returns demo data or allows manual entry.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
    
    def parse_image(self, image_data: bytes, use_demo: bool = False) -> Bill:
        """
        Parse bill image and extract structured data.
        
        Args:
            image_data: Raw image bytes
            use_demo: If True, return demo bill data regardless of API key
            
        Returns:
            Bill object with extracted data
        """
        if use_demo or not self.api_key:
            return self._get_demo_bill()
        
        # TODO: Implement AI/OCR extraction when API key is available
        # For now, return demo data
        return self._get_demo_bill()
    
    def _get_demo_bill(self) -> Bill:
        """
        Return demo bill data for testing and demonstration.
        
        Restaurant: Spice Garden
        """
        return Bill(
            restaurant_name="Spice Garden",
            date="2024-01-15",
            bill_number="INV-2024-001",
            items=[
                BillItem(
                    id="item-1",
                    name="Chicken Biryani",
                    quantity=2,
                    unit_price=Decimal("300"),
                    total=Decimal("600"),
                    confidence=0.96
                ),
                BillItem(
                    id="item-2",
                    name="Coke",
                    quantity=2,
                    unit_price=Decimal("60"),
                    total=Decimal("120"),
                    confidence=0.95
                ),
                BillItem(
                    id="item-3",
                    name="Paneer Tikka",
                    quantity=1,
                    unit_price=Decimal("350"),
                    total=Decimal("350"),
                    confidence=0.94
                ),
                BillItem(
                    id="item-4",
                    name="Water",
                    quantity=1,
                    unit_price=Decimal("30"),
                    total=Decimal("30"),
                    confidence=0.98
                )
            ],
            subtotal=Decimal("1100"),
            tax=Decimal("99"),
            service_charge=Decimal("110"),
            discount=Decimal("0"),
            printed_total=Decimal("1309")
        )
    
    def is_api_configured(self) -> bool:
        """Check if AI/OCR API is configured."""
        return bool(self.api_key)
