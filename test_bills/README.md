# Test Bills Dataset

This directory is for collecting real restaurant bills to test OCR/AI extraction accuracy.

## Purpose

The test bills dataset helps:
- Evaluate OCR/AI extraction accuracy
- Identify edge cases in bill formats
- Improve the bill parser service
- Ensure robustness across different bill styles

## Collection Guidelines

### Bill Types to Collect

Collect at least 12 real bills covering these scenarios:

1. **Normal clear bill** - Well-lit, clear text, standard format
2. **Dim lighting** - Low light conditions affecting readability
3. **Crumpled bill** - Wrinkled or folded bill
4. **Steep camera angle** - Photo taken at an angle
5. **Faded thermal print** - Old thermal print with fading text
6. **Handwriting on bill** - Bill with handwritten notes
7. **Two scripts/languages** - Bill with multiple languages
8. **Long bill requiring two photos** - Multi-page or very long bill
9. **Dense item list** - Many items in small space
10. **Multiple quantities** - Items with various quantities
11. **Multiple taxes/service charges** - Complex charge structure
12. **Bill with incorrect printed total** - Arithmetic error on bill

### Photo Guidelines

- Use high-resolution photos (at least 1080p)
- Ensure text is readable
- Include the entire bill in frame
- Avoid glare and shadows
- Use good lighting when possible
- Take multiple angles if needed

### Privacy Considerations

- **Redact personal information**: Phone numbers, addresses, card numbers
- **Redact sensitive data**: Credit card numbers, signatures
- **Keep restaurant data**: Restaurant name, items, prices are fine
- **No real names**: Use anonymized names if people are listed

## Ground Truth Template

For each bill, create a ground truth file in `test_bills/ground_truth/` with the following format:

### Filename Convention

Use descriptive filenames:
```
restaurant_name_scenario.jpg
restaurant_name_scenario_ground_truth.json
```

Examples:
```
spice_garden_normal.jpg → spice_garden_normal_ground_truth.json
paradise_dim_lighting.jpg → paradise_dim_lighting_ground_truth.json
```

### Ground Truth JSON Format

```json
{
  "filename": "spice_garden_normal.jpg",
  "restaurant": "Spice Garden",
  "date": "2024-01-15",
  "bill_number": "INV-2024-001",
  "items": [
    {
      "name": "Chicken Biryani",
      "quantity": 2,
      "unit_price": 300,
      "total": 600
    },
    {
      "name": "Coke",
      "quantity": 2,
      "unit_price": 60,
      "total": 120
    }
  ],
  "subtotal": 720,
  "tax": 65,
  "service_charge": 72,
  "discount": 0,
  "printed_total": 857,
  "correct_total": 857,
  "notes": "Clear bill, standard format"
}
```

### Field Descriptions

- **filename**: Name of the bill image file
- **restaurant**: Restaurant name (as printed on bill)
- **date**: Date on the bill (YYYY-MM-DD format)
- **bill_number**: Bill/invoice number if present
- **items**: Array of line items
  - **name**: Item name exactly as printed
  - **quantity**: Quantity (integer)
  - **unit_price**: Price per unit (number)
  - **total**: Line item total (quantity × unit_price)
- **subtotal**: Sum of all item totals
- **tax**: GST/tax amount
- **service_charge**: Service charge amount
- **discount**: Discount amount (if any)
- **printed_total**: Total as printed on bill
- **correct_total**: Mathematically correct total (may differ from printed_total if bill has error)
- **notes**: Any observations about the bill

## Example Ground Truth

```json
{
  "filename": "spice_garden_normal.jpg",
  "restaurant": "Spice Garden",
  "date": "2024-01-15",
  "bill_number": "INV-2024-001",
  "items": [
    {
      "name": "Chicken Biryani",
      "quantity": 2,
      "unit_price": 300,
      "total": 600
    },
    {
      "name": "Coke",
      "quantity": 2,
      "unit_price": 60,
      "total": 120
    },
    {
      "name": "Paneer Tikka",
      "quantity": 1,
      "unit_price": 350,
      "total": 350
    },
    {
      "name": "Water",
      "quantity": 1,
      "unit_price": 30,
      "total": 30
    }
  ],
  "subtotal": 1100,
  "tax": 99,
  "service_charge": 110,
  "discount": 0,
  "printed_total": 1309,
  "correct_total": 1309,
  "notes": "Clear thermal print, standard Indian restaurant format"
}
```

## Validation

Before submitting a ground truth file:

1. **Verify arithmetic**:
   - Each item total = quantity × unit_price
   - Subtotal = sum of all item totals
   - Correct total = subtotal + tax + service_charge - discount

2. **Check for completeness**:
   - All required fields present
   - All items listed
   - No missing charges

3. **Format validation**:
   - Valid JSON syntax
   - Numbers are numbers (not strings)
   - Date in YYYY-MM-DD format

## Using the Dataset

### Manual Testing

Use the ground truth to manually verify OCR extraction:
1. Run the parser on the bill image
2. Compare extracted data with ground truth
3. Calculate accuracy metrics

### Automated Testing

Future implementation will include:
- Automated accuracy testing
- Comparison metrics (precision, recall, F1)
- Visual diff tools
- Batch processing

## Contributing

To contribute test bills:

1. Take photos following the guidelines
2. Redact sensitive information
3. Create ground truth JSON file
4. Place both files in appropriate directories
5. Submit a pull request with description

## Current Status

This dataset is currently empty. We need to collect real bills to improve OCR accuracy.

## License

Contributed test bills should be licensed under the same license as the project (MIT). By contributing, you agree that your contributions can be used for testing and improvement of the application.
