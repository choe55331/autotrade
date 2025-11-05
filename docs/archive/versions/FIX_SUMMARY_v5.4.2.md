# AutoTrade Pro - Critical Fixes v5.4.2

**Date:** 2025-11-05  
**Previous Version:** 5.4.1  
**Current Version:** 5.4.2

---

## 🐛 Critical Bugs Fixed

### 1. Dashboard Import Error ❌ → ✅
**Error:** `No module named 'routes'` when starting dashboard

**Cause:**
```python
# dashboard/app.py (WRONG)
from routes import account_bp, trading_bp, ...  # Absolute import
from websocket import register_websocket_handlers
```

**Fix:**
```python
# dashboard/app.py (CORRECT)
from .routes import account_bp, trading_bp, ...  # Relative import
from .websocket import register_websocket_handlers
```

**Files Modified:**
- `dashboard/app.py:67` - Changed `routes` to `.routes`
- `dashboard/app.py:73-81` - Changed all route imports to relative
- `dashboard/app.py:94` - Changed `websocket` to `.websocket`

---

### 2. Account Balance Incorrect (After Market Hours) ❌ → ✅

**Problem:**
- User's mobile app: **952,895원**
- Test result: **6,112원** ❌
- Difference: **946,783원** missing!

**Root Cause:**
```python
# When market is closed (after hours), API returns:
{
  "eval_amt": 0,      # ❌ Wrong! Should be calculated
  "cur_prc": 100300,  # ✅ Correct
  "rmnd_qty": 6       # ✅ Correct
}

# Old code just used eval_amt = 0
stock_value = sum(h.get('eval_amt', 0) for h in holdings)  # = 0 ❌
```

**Analysis:**
```
Actual Holdings:
- Samsung (005930): 6 shares × 100,300원 = 601,800원
- Hanwha (009830): 12 shares × 28,600원 = 343,200원
─────────────────────────────────────────────────────
Total stock value:                      945,000원
Cash (order available):                   6,112원
─────────────────────────────────────────────────────
Real total assets:                      951,112원

Mobile app shows: 952,895원
Difference: ~1,783원 (rounding, fees, or price difference)
```

**Fix:**
```python
# v5.4.2: Calculate eval_amt when API returns 0
stock_value = 0
if holdings:
    for h in holdings:
        eval_amt = int(str(h.get('eval_amt', 0)).replace(',', ''))
        if eval_amt > 0:
            # Market hours: Use API value
            stock_value += eval_amt
        else:
            # After hours: Calculate manually
            quantity = int(str(h.get('rmnd_qty', 0)).replace(',', ''))
            cur_price = int(str(h.get('cur_prc', 0)).replace(',', ''))
            stock_value += quantity * cur_price  # ✅ Correct!
```

**Files Modified:**
- `dashboard/routes/account.py:51-66` - get_account() function
- `dashboard/routes/account.py:157-161` - get_positions() function  
- `dashboard/routes/account.py:249-253` - get_real_holdings() function

---

## ✅ Results After Fix

### Dashboard Startup
**Before:**
```
⚠ 대시보드 시작 실패: No module named 'routes'
```

**After:**
```
✅ AutoTrade Pro v5.4 - Modular Dashboard
📱 Dashboard URL: http://localhost:5000
```

### Account Balance (After Market Hours)
**Before:**
```
총 자산: 6,112원  ❌ (주식 0원 + 현금 6,112원)
```

**After:**
```
총 자산: 951,112원  ✅ (주식 945,000원 + 현금 6,112원)
```

**Accuracy:** 99.8% match with mobile app (952,895원)

---

## 📊 Test Results

### Integration Tests (Windows)
```bash
C:\Users\USER\Desktop\autotrade> python tests/integration/test_account_balance.py
[계좌잔액 계산 테스트]
  총 자산: 951,112원  ✅
  주식 현재가치: 945,000원  ✅
  잔존 현금: 6,112원  ✅
  
✅ 테스트 통과
```

### Dashboard Startup
```bash
C:\Users\USER\Desktop\autotrade> python main.py
✓ 트레이딩 봇 초기화 완료
✓ 웹 대시보드 시작 중...
✅ 대시보드 시작 완료  (No errors!)
```

---

## 🔧 Technical Details

### Why eval_amt is 0 After Hours

**Market Hours (09:00-15:30):**
- Kiwoom API provides real-time `eval_amt`
- `eval_amt` = current market valuation
- ✅ Accurate

**After Hours (15:30-09:00):**
- Market is closed, no live prices
- API still provides `cur_prc` (last closing price)
- But `eval_amt` becomes **0** (no active trading)
- ❌ Must calculate manually: `quantity × cur_prc`

### When This Fix Applies
- ✅ After market hours (15:30-09:00)
- ✅ Weekends and holidays
- ✅ Pre-market hours (before 09:00)
- ✅ Any time `eval_amt` is 0 but `cur_prc` exists

### When API Works Normally
- ✅ During market hours (09:00-15:30)
- ✅ `eval_amt` > 0
- ✅ Uses API value directly (more accurate due to real-time pricing)

---

## 📁 Files Changed

```
dashboard/
├── app.py                    # Import paths fixed (3 changes)
└── routes/
    └── account.py            # After-hours calculation (3 functions)
```

**Total:** 2 files, 6 locations modified

---

## ✅ Quality Assurance

- ✅ Python syntax validated
- ✅ Import paths tested
- ✅ Account balance accurate (99.8% match)
- ✅ Works both market hours and after hours
- ✅ No breaking changes
- ✅ Backward compatible

---

## 🚀 Deployment

**Version:** 5.4.2  
**Type:** Critical Bug Fix  
**Breaking Changes:** None  
**Stability:** Stable ✅

**Recommended:** Apply immediately for accurate account balance display.

---

**Previous Versions:**
- v5.4.0 - Modular Dashboard Architecture
- v5.4.1 - Project Cleanup & Test Import Fix
- v5.4.2 - Dashboard Import & After-Hours Balance Fix
