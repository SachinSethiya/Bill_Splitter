from fastapi import APIRouter, UploadFile, File, Query
from backend.services.bill_parser import BillParser

router = APIRouter()
parser = BillParser()


@router.post("/upload")
async def upload_bill(
    file: UploadFile = File(None),
    demo: bool = Query(False, description="Use demo bill data")
):
    """
    Upload a bill image and extract structured data.
    
    If demo=true is passed, returns demo bill data without requiring an image.
    """
    if demo:
        # Return demo bill data
        bill = parser.parse_image(b"", use_demo=True)
        return bill.model_dump()
    
    if not file:
        return {"error": "No file uploaded"}
    
    # Read file content
    content = await file.read()
    
    # Parse the bill
    bill = parser.parse_image(content)
    
    return bill.model_dump()
