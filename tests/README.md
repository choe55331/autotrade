# AutoTrade Tests

## 📁 Folder Structure (v5.4)

### `unit/`
Unit tests for individual functions and modules.
- Fast execution
- No external dependencies
- Mock API calls
- **Status**: Empty (to be added in future)

### `integration/`
Integration tests that verify components working together.
- Tests real API interactions
- Validates data flow between modules
- **Current tests**:
  - `test_account_balance.py` - Validates account balance calculation (stock value + remaining cash)
  - `test_nxt_current_price.py` - Validates NXT market price fetching during trading hours

### `manual/`
Manual tests and analysis scripts for debugging and development.
- Requires manual execution
- Interactive testing
- Performance analysis
- **Subfolders**:
  - `patches/` - Bug fix patches and validation scripts
  - `analysis/` - Data analysis and optimization scripts

### `archived/`
Archived tests kept for reference.
- Deprecated test files
- Old API validation scripts
- Historical test data

## 🚀 Running Tests

### Integration Tests
```bash
# Run account balance test
python tests/integration/test_account_balance.py

# Run NXT price test
python tests/integration/test_nxt_current_price.py
```

### Manual Tests
```bash
# Navigate to manual test directory
cd tests/manual

# Run specific manual test
python test_dashboard_api.py
```

## ✅ Test Requirements

All integration tests now use **cross-platform path resolution**:
```python
import os
import sys

# Works on both Windows and Linux
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
```

## 📝 Adding New Tests

### Unit Test Template
```python
"""
Test module description
"""
import unittest
from mymodule import my_function

class TestMyFunction(unittest.TestCase):
    def test_basic_case(self):
        result = my_function(input_data)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
```

### Integration Test Template
```python
"""
Integration test description
"""
import sys
import os

# Cross-platform path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from api.account import AccountAPI
from core.rest_client import KiwoomRESTClient

def test_integration():
    """Test description"""
    client = KiwoomRESTClient()
    api = AccountAPI(client)
    # ... test logic ...
    
if __name__ == "__main__":
    try:
        success = test_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
```

---
*Updated: 2025-11-05*
*Version: 5.4.0*
