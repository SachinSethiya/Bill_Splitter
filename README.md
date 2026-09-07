# FairShare — AI Restaurant Bill Splitter

FairShare is a web application that allows groups of people to split restaurant bills fairly and accurately. Upload a bill photo, review the extracted data, assign items to members, and get a detailed breakdown of who owes what.

## Features

- **Bill Upload**: Drag and drop or select bill images (JPG, JPEG, PNG, WEBP)
- **AI/OCR Extraction**: Automatic bill data extraction (with demo mode fallback)
- **Human Review**: Edit and correct all extracted data before calculation
- **Flexible Assignment**: Assign items to specific members or share among everyone
- **Fair Calculation**: Deterministic calculation using Decimal arithmetic
- **Proportional Charges**: Tax and service charge allocated proportionally
- **Validation**: Detects subtotal and total mismatches
- **Detailed Breakdown**: Item-by-item breakdown for each person

## Technology

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Responsive design

### Backend
- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn

### Testing
- pytest

### Calculations
- Python Decimal for precise monetary arithmetic
- Never uses floating-point for final financial calculations

## Architecture

```
Bill_Splitter/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
│
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── bill.py             # Pydantic models (Bill, BillItem, Member, etc.)
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py           # Bill upload endpoint
│   │   └── calculate.py        # Calculation endpoint
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bill_parser.py      # Bill parsing service (demo + AI)
│   │   ├── calculator.py       # Deterministic calculation engine
│   │   └── validator.py        # Bill validation service
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_calculator.py  # Calculator tests
│       ├── test_validator.py   # Validator tests
│       └── test_api.py         # API endpoint tests
│
├── frontend/
│   ├── index.html              # Upload page
│   ├── review.html             # Review and assignment page
│   ├── result.html             # Results page
│   │
│   ├── css/
│   │   ├── style.css           # Main styles
│   │   └── review.css          # Review page styles
│   │
│   ├── js/
│   │   ├── app.js              # Upload page logic
│   │   ├── review.js           # Review page logic
│   │   └── result.js           # Results page logic
│   │
│   └── assets/
│
├── test_bills/
│   ├── README.md
│   └── ground_truth/
│
└── docs/
    ├── architecture.md
    ├── calculation_logic.md
    └── testing.md
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository** (if not already cloned):
   ```bash
   git clone https://github.com/SachinSethiya/Bill_Splitter.git
   cd Bill_Splitter
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables** (optional):
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your AI/OCR API key if you have one. If not configured, the app will use demo mode.

## Running the Application

### Start the Backend Server

```bash
python -m uvicorn backend.main:app --reload
```

The server will start at `http://127.0.0.1:8000`

### Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

## Usage

### 1. Upload Bill
- Click "Choose Image" or drag and drop a bill image
- Or click "Try Demo Bill" to use the demo data

### 2. Review and Correct
- Review the extracted restaurant information
- Edit items, quantities, and prices if needed
- Check the validation section for any mismatches
- Add or remove members (2-7 members)
- Assign each item to the people who consumed it

### 3. Calculate
- Click "Calculate Fair Share"
- Review the detailed breakdown for each person
- Verify that the sum of shares matches the bill total

## Demo Mode

The demo mode works without any API key. It uses a pre-configured bill from "Spice Garden" restaurant with:
- Chicken Biryani (2 × ₹300 = ₹600)
- Coke (2 × ₹60 = ₹120)
- Paneer Tikka (1 × ₹350 = ₹350)
- Water (1 × ₹30 = ₹30)
- GST: ₹99
- Service Charge: ₹110
- Total: ₹1309

## AI/OCR Configuration

To enable AI/OCR extraction:

1. Set up an account with a vision/LLM API provider
2. Add your API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Restart the server

If no API key is configured, the app automatically uses demo mode.

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest backend/tests/test_calculator.py
```

Run with verbose output:
```bash
pytest -v
```

## Calculation Methodology

FairShare uses a deterministic calculation algorithm:

1. **Item Splitting**: For each item, divide the total equally among assigned members
2. **Food Share**: Calculate each person's total food consumption
3. **Proportional Charges**: Allocate tax, service charge, and discount proportionally based on food share
4. **Rounding**: Round all amounts to 2 decimal places
5. **Reconciliation**: Ensure sum of member totals equals bill total

Example:
- If Rahul and Priya share a ₹600 item equally: Rahul pays ₹300, Priya pays ₹300
- If Rahul's food share is 60% of subtotal, he pays 60% of tax and service charge

See [docs/calculation_logic.md](docs/calculation_logic.md) for detailed explanation.

## Test Bill Dataset

The `test_bills/` directory is for collecting real bills to test OCR accuracy.

See [test_bills/README.md](test_bills/README.md) for guidelines on collecting and labeling test bills.

## Known Limitations

- AI/OCR extraction is not implemented yet (demo mode only)
- No support for multi-page bills
- No support for multiple currencies (Indian Rupees only)
- No user accounts or bill history
- No export to PDF or other formats

## Future Improvements

- Implement AI/OCR extraction with vision APIs
- Add support for multi-page bills
- Add currency selection
- Add bill history and saving
- Add export functionality
- Add mobile app
- Add bill templates for common restaurants

## Troubleshooting

### Server won't start
- Ensure Python 3.11+ is installed
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use

### Tests failing
- Ensure you're in the virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`
- Run tests with verbose output: `pytest -v`

### Frontend not loading
- Ensure the backend server is running
- Check browser console for errors
- Ensure you're accessing `http://127.0.0.1:8000`

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.