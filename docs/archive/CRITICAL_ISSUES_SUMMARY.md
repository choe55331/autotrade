# Critical Issues Summary - AutoTrade Pro

## 🔴 CRITICAL BUGS FOUND (3)

### Issue #1: Bare `except:` Clause in REST Client
**File**: `/home/user/autotrade/core/rest_client.py:297`
**Method**: `_parse_error_response()`
**Severity**: CRITICAL

```python
# CURRENT (BAD):
def _parse_error_response(self, res: requests.Response) -> str:
    try:
        return str(res.json())
    except:                    # ❌ Catches EVERYTHING
        return res.text[:200]

# SHOULD BE:
def _parse_error_response(self, res: requests.Response) -> str:
    try:
        return str(res.json())
    except (json.JSONDecodeError, Exception) as e:  # ✓ Specific
        logger.warning(f"Error parsing response: {e}")
        return res.text[:200]
```

**Impact**:
- Catches SystemExit, KeyboardInterrupt, etc.
- Masks real errors
- Can silently fail without logging

**Fix Time**: 2 minutes

---

### Issue #2: Type Mismatch in Error Codes
**File**: `/home/user/autotrade/core/rest_client.py:422`
**Method**: `_execute_request()`
**Severity**: CRITICAL

```python
# CURRENT (BAD):
except requests.exceptions.HTTPError as e:
    error_text = e.response.text[:200]
    logger.error(f"HTTP 오류 ({api_id}): {e.response.status_code} - {error_text}")
    return {
        "return_code": f"-{e.response.status_code}",  # ❌ STRING!
        "return_msg": f"HTTP 오류: {e.response.reason}",
        "error_detail": error_text
    }

# SHOULD BE:
    return {
        "return_code": -int(e.response.status_code),  # ✓ INT
        "return_msg": f"HTTP 오류: {e.response.reason}",
        "error_detail": error_text
    }
```

**Impact**:
- Code checking `if response['return_code'] == 401:` will FAIL
- Comparison with strings instead of ints breaks logic
- Cascading failures in error handling

**Evidence**:
```python
# Line 321-326: Code expects INT
if not self._is_token_valid():
    if not self._get_token():
        return {
            "return_code": -401,  # ← INT expected
            "return_msg": f"..."
        }
```

**Fix Time**: 2 minutes

---

### Issue #3: Missing WebSocket Heartbeat
**File**: `/home/user/autotrade/core/websocket_client.py`
**Severity**: CRITICAL

```python
# PROBLEM: No ping/pong mechanism
class WebSocketClient:
    def connect(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            header=[f"authorization: Bearer {self.token}"]
            # ❌ No: ping_interval, ping_timeout, etc.
        )
```

**Impact**:
- WebSocket can silently disconnect (network hiccup, firewall timeout)
- No detection mechanism
- Market data stream dies without warning
- Trading decisions based on stale data

**Risk Scenario**:
```
19:00 → WebSocket closes (network timeout, firewall NAT session expires)
19:01 → Code thinks connection is alive (no error callback triggered)
19:05 → Uses old prices to make trade decisions
LOSS: Real-time data is 5+ minutes stale
```

**Fix**: Add heartbeat
```python
self.ws = websocket.WebSocketApp(
    self.url,
    on_open=self._on_open,
    on_message=self._on_message,
    on_error=self._on_error,
    on_close=self._on_close,
    header=[f"authorization: Bearer {self.token}"],
    ping_interval=30,      # ✓ Ping every 30s
    ping_timeout=10        # ✓ Timeout after 10s
)
```

**Fix Time**: 5 minutes

---

## 🟡 HIGH PRIORITY ISSUES (3)

### Issue #4: API Server Completely Stubbed
**File**: `/home/user/autotrade/api_server/main.py`
**Lines**: 20+ TODO comments
**Severity**: HIGH

```python
@app.get("/api/system/status")
async def get_system_status():
    # TODO: Implement real status retrieval from bot instance
    return {
        "running": False,
        "test_mode": False,
        ...
    }  # All hardcoded, not connected to actual bot
```

**Impact**:
- FastAPI server exists but returns fake data
- Dashboard can't communicate with actual bot
- Real trading decisions not visible to UI

**Fix Time**: 4-6 hours (depends on bot architecture)

---

### Issue #5: Duplicate Configuration Systems
**File**: 
- `/home/user/autotrade/config/config_manager.py` (OLD)
- `/home/user/autotrade/config/manager.py` (NEW)
**Location**: main.py:16-20
**Severity**: HIGH

```python
# CURRENT: Try-catch fallback (no clear winner)
try:
    from config.manager import get_config
except ImportError:
    from config.config_manager import get_config

# PROBLEM:
# - Two systems can get out of sync
# - User doesn't know which one is active
# - Migration path unclear
# - Duplicate code increases maintenance burden
```

**Impact**:
- Settings changes in one might not apply to the other
- Debugging configuration issues is confusing
- Upgrade/downgrade path unclear

**Fix Time**: 2-3 hours to consolidate

---

### Issue #6: Test Mode Hardcoded Data
**File**: `/home/user/autotrade/features/test_mode_manager.py:410-415`
**Severity**: HIGH

```python
# NOT CALCULATED, HARDCODED:
technical_analysis = {
    "rsi": 45.2,           # ❌ Fixed value, not computed
    "macd": "매수 신호",   # ❌ Fake result
    "bollinger": "중립",   # ❌ Fake result
    "volume": "평균 대비 120%"  # ❌ Fake
}
```

**Impact**:
- Test results mislead developers
- Features might pass weekend tests but fail in live trading
- False confidence in untested code paths

**Fix Time**: 3-4 hours to add real calculations

---

## 🟠 MEDIUM PRIORITY (3)

### Issue #7: No Timeout in Gemini API
**File**: `/home/user/autotrade/ai/gemini_analyzer.py`
**Severity**: MEDIUM

```python
try:
    response = self.model.generate_content(prompt)  # No timeout!
    # Could hang indefinitely if API is slow/broken
```

**Fix**:
```python
# Add timeout
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Gemini API timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout
try:
    response = self.model.generate_content(prompt)
finally:
    signal.alarm(0)
```

---

### Issue #8: Inconsistent Error Responses
**File**: Multiple (api/market.py, api/account.py, etc.)
**Severity**: MEDIUM

```python
# Some return None:
def get_stock_price(code):
    if error:
        return None  # ❌

# Some return empty dict:
def get_orderbook(code):
    if error:
        return {}  # ❌

# Inconsistent caller experience
result = get_stock_price("005930")
if result:  # Works with None
    ...

result = get_orderbook("005930")
if result:  # Always True even when empty!
    ...
```

**Standard Response**:
```python
def get_stock_price(code):
    if error:
        return {
            "return_code": -1,
            "return_msg": "조회 실패",
            "output": None
        }
```

---

### Issue #9: No Rate Limit Backoff
**File**: `/home/user/autotrade/ai/gemini_analyzer.py`
**Severity**: MEDIUM

```python
# No retry logic for rate limits
try:
    response = self.model.generate_content(prompt)
except:
    logger.error(f"API call failed")  # Just logs, doesn't retry
```

**Should have**:
```python
@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(RateLimitError)
)
def generate_analysis(self, prompt):
    return self.model.generate_content(prompt)
```

---

## Summary Table

| # | Issue | File | Severity | Fix Time |
|---|-------|------|----------|----------|
| 1 | Bare `except:` | rest_client.py:297 | 🔴 CRITICAL | 2 min |
| 2 | Type mismatch (INT/STRING) | rest_client.py:422 | 🔴 CRITICAL | 2 min |
| 3 | WebSocket no heartbeat | websocket_client.py | 🔴 CRITICAL | 5 min |
| 4 | API server stubbed | api_server/main.py | 🟡 HIGH | 4-6 hrs |
| 5 | Duplicate config systems | config/ | 🟡 HIGH | 2-3 hrs |
| 6 | Hardcoded test data | test_mode_manager.py | 🟡 HIGH | 3-4 hrs |
| 7 | No Gemini timeout | gemini_analyzer.py | 🟠 MEDIUM | 1 hr |
| 8 | Inconsistent errors | api/*.py | 🟠 MEDIUM | 2 hrs |
| 9 | No rate limit retry | gemini_analyzer.py | 🟠 MEDIUM | 1.5 hrs |

---

## Implementation Priority

**Phase 1 (Immediate - 2 hours total)**
1. Fix bare `except:` (2 min)
2. Fix type mismatch (2 min)
3. Add WebSocket heartbeat (5 min)
4. Write unit tests (1.5 hours)
5. Verify all changes work

**Phase 2 (This week - 6-9 hours)**
4. Consolidate config systems (2-3 hours)
5. Implement API server (4-6 hours)

**Phase 3 (Next week - 5 hours)**
6. Fix test mode with real calculations (3-4 hours)
7. Add rate limit retry (1-1.5 hours)

---

## Testing Recommendations

After fixes:
```bash
# Test error handling
pytest tests/test_error_handling.py -v

# Test REST client
pytest tests/test_rest_client.py -v

# Test WebSocket resilience
python tests/test_websocket_resilience.py

# Integration test
python run_weekend_test.py
```
