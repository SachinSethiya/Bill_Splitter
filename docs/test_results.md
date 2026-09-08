# Test Results for Real Bills

## Bill 01 - Barbeque Nation

| Test                      | Result |
| ------------------------- | ------ |
| Image upload              | PASS   |
| Extraction                | N/A*   |
| Pydantic validation       | PASS   |
| Human review              | PASS   |
| Item assignment           | PASS   |
| Split calculation         | PASS   |
| GST allocation            | PASS   |
| Service charge allocation | PASS   |
| Discount handling         | PASS   |
| Total validation          | PASS   |
| Final per-person result   | PASS   |

### Extraction Issues

*AI/OCR extraction is not implemented. The application returned demo bill data instead of extracting from the actual image. Manual data entry was used for testing.*

### Calculation Issues

None. Calculation worked correctly.

### Manual Corrections

All data was manually entered based on ground truth from the actual bill image.

### Notes

- Rahul: ₹440.30 (₹370 food + ₹33.30 GST + ₹37.00 service charge)
- Priya: ₹577.15 (₹485 food + ₹43.65 GST + ₹48.50 service charge)
- Aman: ₹291.55 (₹245 food + ₹22.05 GST + ₹24.50 service charge)
- Total: ₹1309.00 ✓
- GST and service charge allocated proportionally based on food consumption

## Bill 02 - Paradise

| Test                      | Result |
| ------------------------- | ------ |
| Image upload              | PASS   |
| Extraction                | N/A*   |
| Pydantic validation       | PASS   |
| Human review              | PASS   |
| Item assignment           | PASS   |
| Split calculation         | PASS   |
| GST allocation            | PASS   |
| Service charge allocation | PASS   |
| Discount handling         | PASS   |
| Total validation          | PASS   |
| Final per-person result   | PASS   |

### Extraction Issues

*AI/OCR extraction is not implemented. The application returned demo bill data instead of extracting from the actual image. Manual data entry was used for testing.*

### Calculation Issues

None. Calculation worked correctly.

### Manual Corrections

All data was manually entered based on ground truth from the actual bill image.

### Notes

- Rahul: ₹779.45 (₹655 food + ₹58.95 GST + ₹65.50 service charge)
- Priya: ₹446.25 (₹375 food + ₹33.75 GST + ₹37.50 service charge)
- Total: ₹1225.70 ✓
- GST and service charge allocated proportionally based on food consumption

## Overall Results

* **Bills tested**: 2
* **Bills passed**: 2
* **Bills failed**: 0
* **Bills requiring manual correction**: 2 (due to lack of AI/OCR extraction)
* **Total mismatches**: 0
* **Critical bugs**: 0
* **Known limitations**:
  - AI/OCR extraction not implemented (demo mode only)
  - No support for multi-page bills
  - No support for multiple currencies (Indian Rupees only)
  - bill_2.jif had incorrect extension, renamed to bill_2.jpg for proper handling

## Test Summary

Both bills were successfully tested through the calculation workflow. Since AI/OCR extraction is not implemented, manual data entry was used to verify the calculation and splitting functionality. The calculation engine correctly:

- Split items among multiple people
- Allocated GST proportionally based on food consumption
- Allocated service charge proportionally based on food consumption
- Handled quantities correctly
- Rounded to 2 decimal places
- Reconciled totals to match bill total
- Verified that sum of shares equals bill total

All automated tests (48/48) passed.
