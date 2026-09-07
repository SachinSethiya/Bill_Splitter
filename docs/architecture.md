# FairShare Architecture

## Overview

FairShare follows a clean, modular architecture with clear separation of concerns between frontend and backend.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Browser (Frontend)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ index.html│  │review.html│  │result.html│             │
│  └──────────┘  └──────────┘  └──────────┘             │
│       │              │              │                    │
│  ┌──────────────────────────────────────────┐          │
│  │         Vanilla JavaScript               │          │
│  │  (app.js, review.js, result.js)          │          │
│  └──────────────────────────────────────────┘          │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                    │
│  ┌──────────────────────────────────────────┐          │
│  │              main.py                        │          │
│  │         (Application Entry Point)          │          │
│  └──────────────────────────────────────────┘          │
│                           │                              │
│  ┌──────────────────────┴─────────────────────┐        │
│  │                    Routes                    │        │
│  │  ┌──────────┐      ┌──────────┐            │        │
│  │  │ upload.py│      │calculate.py│           │        │
│  │  └──────────┘      └──────────┘            │        │
│  └──────────────────────┬─────────────────────┘        │
│                         │                              │
│  ┌──────────────────────┴─────────────────────┐        │
│  │                   Services                    │        │
│  │  ┌──────────────┐  ┌──────────────┐         │        │
│  │  │ bill_parser  │  │ calculator   │         │        │
│  │  └──────────────┘  └──────────────┘         │        │
│  │  ┌──────────────┐                           │        │
│  │  │  validator    │                           │        │
│  │  └──────────────┘                           │        │
│  └─────────────────────────────────────────────┘        │
│                         │                              │
│  ┌──────────────────────┴─────────────────────┐        │
│  │                   Models                     │        │
│  │  (Pydantic: Bill, BillItem, Member, etc.)    │        │
│  └─────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## Frontend Architecture

### Pages

1. **index.html** - Bill upload page
   - Drag and drop file upload
   - Image preview
   - Demo bill button

2. **review.html** - Bill review and assignment page
   - Restaurant information editing
   - Item table with editing
   - Bill charges editing
   - Validation display
   - Member management
   - Item assignment

3. **result.html** - Results display page
   - Per-person breakdown
   - Total verification

### JavaScript Modules

- **app.js**: Handles file upload, preview, and API calls for bill extraction
- **review.js**: Manages bill editing, member management, and item assignment
- **result.js**: Displays calculation results and verification

### State Management

Frontend uses `sessionStorage` to pass data between pages:
- `billData`: Extracted bill information
- `billImage`: Base64 encoded bill image
- `calculationResult`: Final calculation results

## Backend Architecture

### FastAPI Application

**main.py** is the entry point that:
- Initializes the FastAPI app
- Configures CORS middleware
- Mounts static files
- Includes route modules
- Serves frontend pages

### Routes

**upload.py**:
- `POST /api/upload` - Accepts bill image, returns extracted data
- Supports demo mode via query parameter

**calculate.py**:
- `POST /api/calculate` - Accepts bill, members, assignments, returns calculation results

### Services

**bill_parser.py**:
- Parses bill images (demo mode or AI/OCR)
- Returns structured Pydantic models
- Isolated from rest of application

**calculator.py**:
- Deterministic calculation engine
- Uses Decimal for monetary arithmetic
- Handles item splitting, proportional charge allocation
- Rounds and reconciles totals

**validator.py**:
- Validates bill data consistency
- Validates member constraints
- Validates assignment completeness
- Returns errors with severity levels

### Models

**bill.py** defines Pydantic models:
- `Bill`: Complete bill with items and charges
- `BillItem`: Individual line item
- `Member`: Group member
- `Assignment`: Item-to-members mapping
- `CalculationResult`: Final calculation output
- `MemberBreakdown`: Per-person breakdown

## Data Flow

### Upload Flow

```
User uploads image
    ↓
Frontend sends POST /api/upload
    ↓
bill_parser.parse_image()
    ↓
Returns Bill model
    ↓
Frontend stores in sessionStorage
    ↓
Redirects to review.html
```

### Calculation Flow

```
User reviews and assigns items
    ↓
Frontend sends POST /api/calculate
    ↓
validator.validate_bill()
validator.validate_members()
validator.validate_assignments()
    ↓
calculator.calculate()
    ↓
Returns CalculationResult
    ↓
Frontend stores in sessionStorage
    ↓
Redirects to result.html
```

## Key Design Decisions

### 1. No Frontend Framework
- Vanilla JavaScript for simplicity
- Beginner-friendly for someone who knows HTML
- No build step required

### 2. SessionStorage for State
- Simple state management
- Data persists across page navigation
- No backend session storage needed

### 3. Decimal for Calculations
- Precise monetary arithmetic
- Avoids floating-point errors
- Rounding strategy is deterministic

### 4. Modular Services
- Clear separation of concerns
- Easy to test individual components
- Easy to extend (e.g., add new parser)

### 5. Pydantic Models
- Automatic validation
- Type safety
- Clear data contracts

### 6. Demo Mode
- Application works without API keys
- Easy to test and demonstrate
- Fallback when AI/OCR unavailable

## Security Considerations

- API keys never exposed to frontend
- `.env` file in `.gitignore`
- CORS configured for development
- File uploads validated (type, size)
- Input validation via Pydantic

## Performance Considerations

- Static files served by FastAPI
- No database queries (stateless)
- Calculations are fast (in-memory)
- Image processing could be slow (future optimization)

## Scalability Considerations

Current architecture is suitable for:
- Single-server deployment
- Small to medium user base
- Stateless operations

Future improvements for scale:
- Add database for bill history
- Add caching for parsed bills
- Use CDN for static files
- Add rate limiting
- Use message queue for AI/OCR processing
