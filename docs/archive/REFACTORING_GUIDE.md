# AutoTrade Pro v4.2 - Refactoring Guide
**4가지 CRITICAL 이슈 해결 가이드**

---

## ✅ 완료된 작업 (v4.2)

### 1. ✅ CRITICAL #1: Logging 시스템 통합 (3 → 1)
**상태**: 완료
**파일**: `utils/logger_new.py`, `utils/__init__.py`

#### 변경 사항:
- `logger_new.py`를 표준 로거로 채택 (Loguru 기반)
- Rate-limiting 기능 내장 (`RateLimitedLogger` 클래스)
- `utils/__init__.py`에서 logger_new 모듈 export
- 80% I/O 감소 예상

#### 사용 방법:
```python
# 기본 로깅
from utils import get_logger
logger = get_logger()
logger.info("메시지")

# Rate-limited 로깅 (고빈도 로그)
from utils import get_rate_limited_logger
rate_logger = get_rate_limited_logger(rate_limit_seconds=1.0)
rate_logger.info("price_update", f"가격: {price}")
```

#### 다음 단계:
- [ ] 기존 `logger.py` 사용 코드를 `logger_new.py`로 마이그레이션
- [ ] `rate_limited_logger.py` 직접 사용 코드 제거
- [ ] 테스트 및 검증

---

### 2. ✅ CRITICAL #2: Position 클래스 표준화 (4 → 1)
**상태**: 기반 완료 (마이그레이션 필요)
**파일**: `core/types.py`, `core/__init__.py`

#### 변경 사항:
- 표준 `Position` 클래스 생성 → `core/types.py`
- `OrderAction`, `OrderType`, `PositionStatus` Enum 정의
- `Trade`, `MarketSnapshot` 타입 표준화
- 완전한 손익 추적, Stop-loss/Take-profit 지원

#### 사용 방법:
```python
# 표준 Position 사용
from core import Position, PositionStatus

position = Position(
    stock_code="005930",
    quantity=10,
    purchase_price=70000,
    stock_name="삼성전자"
)

# 현재가 업데이트 (손익 자동 계산)
position.update_current_price(72000)
print(f"손익: {position.profit_loss:+,.0f}원 ({position.profit_loss_rate:+.2f}%)")

# Stop-loss 체크
if position.check_stop_loss():
    print("손절가 도달!")
```

#### 마이그레이션 가이드:

**Step 1: strategy/position_manager.py 업데이트**
```python
# Before
from dataclasses import dataclass

@dataclass
class Position:
    # ...

# After
from core import Position

# PositionManager는 그대로 사용, Position만 import 변경
class PositionManager:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
```

**Step 2: ai/backtesting.py 업데이트**
```python
# Before
@dataclass
class Position:
    stock_code: str
    quantity: int
    avg_price: float
    # ...

# After
from core import Position

# 기존 Position 제거, core.Position 사용
```

**Step 3: features/paper_trading.py 업데이트**
```python
# Before
class PaperPosition:
    # ...

# After
from core import Position

# PaperPosition → Position으로 변경
```

**Step 4: database/models.py ORM 변환 함수 제공**
```python
from core import Position as CorePosition

class Position(Base):
    """DB ORM Position (기존 유지)"""
    __tablename__ = 'positions'
    # ... SQLAlchemy fields

    def to_core_position(self) -> CorePosition:
        """ORM → Core Position 변환"""
        return CorePosition(
            stock_code=self.stock_code,
            quantity=self.quantity,
            purchase_price=self.avg_price,
            stock_name=self.stock_name,
            # ...
        )

    @classmethod
    def from_core_position(cls, pos: CorePosition):
        """Core Position → ORM 변환"""
        return cls(
            stock_code=pos.stock_code,
            quantity=pos.quantity,
            avg_price=pos.purchase_price,
            # ...
        )
```

#### 영향받는 파일 (총 15개):
1. `strategy/position_manager.py` ✓ (Position 정의 제거)
2. `ai/backtesting.py` ✓ (Position 제거, core import)
3. `features/paper_trading.py` ✓
4. `database/models.py` (변환 함수 추가)
5. `strategy/portfolio_manager.py`
6. `strategy/base_strategy.py`
7. `strategy/trailing_stop_manager.py`
8. `features/ai_mode.py`
9. `api/account.py`
10. `dashboard/app_apple.py`
11. ... (기타 Position 사용 코드)

#### 예상 시간: **3-4일**

---

## 🟡 진행 중 (우선순위 높음)

### 3. 🟡 CRITICAL #3: Configuration 시스템 통합 (5 → 1)
**상태**: 계획 중
**목표**: 5개 설정 시스템을 Pydantic 기반 단일 시스템으로 통합

#### 현재 문제:
- **5개 설정 시스템 공존**:
  1. `config/settings.py` - 기본 설정
  2. `config/trading_params.py` - 트레이딩 파라미터
  3. `config/unified_settings.py` - 통합 설정 (v4.0)
  4. `config/config_manager.py` - 설정 관리자
  5. `config/parameter_standards.py` - 파라미터 표준 (v4.1)

- 25개+ 파일에서 일관성 없이 import
- 57번의 서로 다른 설정 접근자 호출
- 설정이 제대로 적용되지 않을 위험

#### 통합 계획:

**Step 1: Pydantic 기반 통합 설정 스키마 생성**
```python
# config/schemas.py (NEW)
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional

class RiskManagementConfig(BaseModel):
    """리스크 관리 설정"""
    max_position_size: float = Field(0.3, ge=0.0, le=1.0, description="최대 포지션 비중")
    stop_loss_pct: float = Field(0.05, ge=0.0, le=1.0, description="손절 비율")
    position_limit: int = Field(10, ge=1, le=50, description="최대 포지션 수")
    daily_loss_limit: float = Field(0.05, ge=0.0, le=1.0, description="일일 손실 한도")

class TradingConfig(BaseModel):
    """트레이딩 설정"""
    min_price: int = 1000
    max_price: int = 1000000
    min_volume: int = 10000
    commission_rate: float = 0.00015

class AIConfig(BaseModel):
    """AI 설정"""
    enabled: bool = True
    confidence_threshold: float = 0.7
    models: list = ["gemini", "ensemble"]

class AutoTradeConfig(BaseModel):
    """통합 설정 (루트)"""
    risk_management: RiskManagementConfig = RiskManagementConfig()
    trading: TradingConfig = TradingConfig()
    ai: AIConfig = AIConfig()

    # YAML 파일에서 로드
    @classmethod
    def from_yaml(cls, path: str):
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    # 저장
    def save_yaml(self, path: str):
        import yaml
        with open(path, 'w') as f:
            yaml.dump(self.dict(), f)
```

**Step 2: 단일 설정 매니저 생성**
```python
# config/manager.py (UNIFIED)
class ConfigManager:
    """통합 설정 관리자 (싱글톤)"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = AutoTradeConfig.from_yaml('config/settings.yaml')
        return cls._instance

    def get(self, path: str, default=None):
        """dot notation으로 설정 가져오기

        예: get('risk_management.max_position_size')
        """
        keys = path.split('.')
        value = self.config
        for key in keys:
            value = getattr(value, key, default)
            if value is default:
                return default
        return value

    def set(self, path: str, value):
        """설정 업데이트"""
        keys = path.split('.')
        obj = self.config
        for key in keys[:-1]:
            obj = getattr(obj, key)
        setattr(obj, keys[-1], value)

    def save(self):
        """설정 저장"""
        self.config.save_yaml('config/settings.yaml')

# 전역 함수
_manager = ConfigManager()

def get_config() -> AutoTradeConfig:
    return _manager.config

def get_setting(path: str, default=None):
    return _manager.get(path, default)

def set_setting(path: str, value):
    _manager.set(path, value)
```

**Step 3: 기존 코드 마이그레이션**
```python
# Before (5가지 다른 방식)
from config import settings
from config.trading_params import get_params
from config.unified_settings import get_unified_settings
from config.config_manager import get_config
from config.parameter_standards import StandardParameters

max_pos = settings.MAX_POSITION_SIZE
max_pos = get_params()['max_position']
max_pos = get_unified_settings().get('risk_management.max_position_size')
max_pos = get_config().risk_management['max_position_size']
max_pos = StandardParameters.normalize('max_position_ratio')

# After (단일 방식)
from config import get_setting

max_pos = get_setting('risk_management.max_position_size')
```

#### 영향받는 파일: **25개+**
#### 예상 시간: **1주일**

---

### 4. 🟡 CRITICAL #4: Risk Management 통합 (6 → 1)
**상태**: 계획 중
**목표**: 6개 리스크 모듈을 단일 RiskManagementEngine으로 통합

#### 현재 문제:
- **6개 리스크 모듈 중복**:
  1. `strategy/risk_manager.py` - 기본 리스크 관리
  2. `strategy/dynamic_risk_manager.py` - 동적 리스크
  3. `strategy/risk_orchestrator.py` - 리스크 통합 (v4.1)
  4. `strategy/advanced_risk_analytics.py` - 고급 분석
  5. `strategy/trailing_stop_manager.py` - 트레일링 스톱
  6. `ai/kelly_criterion.py` - Kelly 포지션 사이징

- 유사한 메서드 중복: `validate_position_size()`, `check_daily_loss_limit()`
- 리스크 체크가 제대로 작동하지 않을 위험

#### 통합 계획:

**Step 1: 통합 리스크 엔진 아키텍처**
```python
# strategy/risk_engine.py (NEW)
from core import Position
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskCheck:
    """리스크 체크 결과"""
    check_type: str
    passed: bool
    risk_level: RiskLevel
    message: str
    value: float
    threshold: float

class RiskManagementEngine:
    """통합 리스크 관리 엔진

    6개 모듈 통합:
    - RiskManager (기본 체크)
    - DynamicRiskManager (동적 모드)
    - RiskOrchestrator (통합 평가)
    - AdvancedRiskAnalytics (VaR/CVaR)
    - TrailingStopManager (트레일링 스톱)
    - KellyCriterion (포지션 사이징)
    """

    def __init__(self, config):
        self.config = config
        self.position_sizer = KellyPositionSizer()
        self.stop_tracker = TrailingStopTracker()

    # ========== 기본 체크 (RiskManager) ==========
    def check_position_size(self, position_value: float, total_value: float) -> RiskCheck:
        """포지션 사이즈 체크"""
        ratio = position_value / total_value if total_value > 0 else 0
        max_ratio = self.config.get('risk_management.max_position_size')

        return RiskCheck(
            check_type="position_size",
            passed=ratio <= max_ratio,
            risk_level=RiskLevel.HIGH if ratio > max_ratio else RiskLevel.LOW,
            message=f"포지션 비중: {ratio:.1%} (한도: {max_ratio:.1%})",
            value=ratio,
            threshold=max_ratio
        )

    def check_daily_loss_limit(self, daily_pnl: float, account_value: float) -> RiskCheck:
        """일일 손실 한도 체크"""
        loss_pct = abs(daily_pnl) / account_value if account_value > 0 else 0
        limit = self.config.get('risk_management.daily_loss_limit')

        return RiskCheck(
            check_type="daily_loss",
            passed=loss_pct <= limit if daily_pnl < 0 else True,
            risk_level=RiskLevel.CRITICAL if loss_pct > limit else RiskLevel.LOW,
            message=f"일일 손실: {loss_pct:.1%} (한도: {limit:.1%})",
            value=loss_pct,
            threshold=limit
        )

    def check_position_limit(self, current_positions: int) -> RiskCheck:
        """포지션 개수 한도 체크"""
        limit = self.config.get('risk_management.position_limit')

        return RiskCheck(
            check_type="position_count",
            passed=current_positions < limit,
            risk_level=RiskLevel.MEDIUM if current_positions >= limit else RiskLevel.LOW,
            message=f"포지션 수: {current_positions} (한도: {limit})",
            value=current_positions,
            threshold=limit
        )

    # ========== 동적 리스크 (DynamicRiskManager) ==========
    def get_dynamic_mode(self, market_volatility: float, portfolio_drawdown: float) -> str:
        """시장 상황에 따른 동적 리스크 모드"""
        if market_volatility > 0.3 or portfolio_drawdown > 0.15:
            return "CONSERVATIVE"
        elif market_volatility < 0.15 and portfolio_drawdown < 0.05:
            return "AGGRESSIVE"
        else:
            return "NORMAL"

    # ========== 고급 분석 (AdvancedRiskAnalytics) ==========
    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        """Value at Risk 계산"""
        import numpy as np
        return np.percentile(returns, (1 - confidence) * 100)

    def calculate_cvar(self, returns: List[float], confidence: float = 0.95) -> float:
        """Conditional VaR 계산"""
        import numpy as np
        var = self.calculate_var(returns, confidence)
        return np.mean([r for r in returns if r <= var])

    # ========== 트레일링 스톱 (TrailingStopManager) ==========
    def update_trailing_stop(self, position: Position) -> float:
        """트레일링 스톱 가격 업데이트"""
        return self.stop_tracker.update(position)

    # ========== 포지션 사이징 (KellyCriterion) ==========
    def calculate_optimal_position_size(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        account_value: float
    ) -> float:
        """Kelly Criterion 포지션 사이징"""
        return self.position_sizer.calculate(win_rate, avg_win, avg_loss, account_value)

    # ========== 통합 평가 (RiskOrchestrator) ==========
    def assess_trading_risk(
        self,
        action: str,
        stock_code: str,
        quantity: int,
        price: float,
        account_info: Dict,
        positions: Dict[str, Position]
    ) -> Dict[str, Any]:
        """통합 리스크 평가"""
        checks = []

        # 1. 기본 체크
        position_value = quantity * price
        checks.append(self.check_position_size(position_value, account_info['total_value']))
        checks.append(self.check_position_limit(len(positions)))
        checks.append(self.check_daily_loss_limit(
            account_info.get('daily_pnl', 0),
            account_info['total_value']
        ))

        # 2. 동적 모드 체크
        mode = self.get_dynamic_mode(
            account_info.get('market_volatility', 0.2),
            account_info.get('portfolio_drawdown', 0.0)
        )

        # 3. 전체 평가
        all_passed = all(check.passed for check in checks)
        max_risk = max((check.risk_level for check in checks), key=lambda x: x.value)

        return {
            'can_trade': all_passed,
            'risk_level': max_risk.value,
            'mode': mode,
            'checks': checks,
            'recommendation': self._generate_recommendation(checks, mode)
        }

    def _generate_recommendation(self, checks: List[RiskCheck], mode: str) -> str:
        """리스크 기반 추천 생성"""
        failed = [c for c in checks if not c.passed]
        if not failed:
            return f"{mode} 모드: 거래 가능"
        else:
            return f"{mode} 모드: 다음 체크 실패 - {', '.join(c.check_type for c in failed)}"


# Helper classes
class KellyPositionSizer:
    """Kelly Criterion 포지션 사이징"""
    def calculate(self, win_rate: float, avg_win: float, avg_loss: float, capital: float) -> float:
        if avg_loss == 0:
            return 0
        q = 1 - win_rate
        kelly = (win_rate / avg_loss) - (q / avg_win)
        return max(0, min(kelly, 0.25)) * capital  # Cap at 25%


class TrailingStopTracker:
    """트레일링 스톱 추적"""
    def __init__(self):
        self.highest_prices = {}

    def update(self, position: Position) -> float:
        """트레일링 스톱 가격 업데이트"""
        code = position.stock_code
        current = position.current_price

        # 최고가 업데이트
        if code not in self.highest_prices:
            self.highest_prices[code] = current
        else:
            self.highest_prices[code] = max(self.highest_prices[code], current)

        # 트레일링 스톱 가격 (최고가의 95%)
        return self.highest_prices[code] * 0.95


# 전역 인스턴스
_engine = None

def get_risk_engine():
    global _engine
    if _engine is None:
        from config import get_config
        _engine = RiskManagementEngine(get_config())
    return _engine
```

**Step 2: 기존 모듈 통합**
- `risk_manager.py` → `RiskManagementEngine.check_*` 메서드
- `dynamic_risk_manager.py` → `get_dynamic_mode()`
- `advanced_risk_analytics.py` → `calculate_var/cvar()`
- `trailing_stop_manager.py` → `TrailingStopTracker`
- `kelly_criterion.py` → `KellyPositionSizer`
- `risk_orchestrator.py` → `assess_trading_risk()`

**Step 3: 마이그레이션**
```python
# Before (6가지 다른 모듈)
from strategy.risk_manager import RiskManager
from strategy.dynamic_risk_manager import DynamicRiskManager
from strategy.risk_orchestrator import RiskOrchestrator
# ...

risk_mgr = RiskManager()
dynamic_mgr = DynamicRiskManager()
orchestrator = RiskOrchestrator()

# After (단일 엔진)
from strategy.risk_engine import get_risk_engine

engine = get_risk_engine()
result = engine.assess_trading_risk(...)
```

#### 영향받는 파일: **20개+**
#### 예상 시간: **1-2주**

---

## 📋 전체 타임라인

| Phase | Task | Status | Time | Priority |
|-------|------|--------|------|----------|
| **Phase 1** | Logging 통합 | ✅ 완료 | 1일 | CRITICAL |
| **Phase 1** | Position 표준화 | ✅ 기반 완료 | 1일 | CRITICAL |
| **Phase 1** | Position 마이그레이션 | 🟡 진행 필요 | 3-4일 | CRITICAL |
| **Phase 2** | Configuration 통합 | 🟡 계획됨 | 1주 | CRITICAL |
| **Phase 3** | Risk Management 통합 | 🟡 계획됨 | 1-2주 | CRITICAL |
| **Phase 4** | 코드 중복 제거 | ⏳ 대기 | 1주 | HIGH |
| **Phase 5** | 테스트 재조직 | ⏳ 대기 | 3-4일 | HIGH |
| **Phase 6** | AI 모듈 재구조화 | ⏳ 대기 | 1-2주 | MEDIUM |

**총 예상 시간**: 6-8주 (풀타임 기준)

---

## 🎯 즉시 실행 가능한 Next Steps

### 이번 주:
1. ✅ Logging 시스템 통합 완료
2. ✅ Position 표준 타입 생성
3. 🔜 Position 마이그레이션 시작 (ai/backtesting.py부터)
4. 🔜 Configuration 통합 설계 착수

### 다음 주:
1. Position 마이그레이션 완료
2. Configuration Pydantic 스키마 생성
3. 기존 설정 코드 마이그레이션 시작

### 이번 달:
1. Configuration 통합 완료
2. Risk Management 통합 시작
3. 코드 중복 제거 시작

---

## 📊 성공 지표

완료 시 달성할 메트릭:

- [ ] 로깅 시스템: 3 → 1 (✅)
- [ ] Position 클래스: 4 → 1 (🔜)
- [ ] Configuration 시스템: 5 → 1 (🔜)
- [ ] Risk 모듈: 6 → 1 (🔜)
- [ ] 코드 중복: -15-20% (~3,000줄)
- [ ] Import 시간: < 2초
- [ ] Type hint 커버리지: > 80%
- [ ] 테스트 커버리지: > 70%

---

## 🤝 도움이 필요한 경우

각 Phase는 독립적으로 진행 가능합니다. 우선순위대로 하나씩 완료하는 것을 권장합니다.

**현재 상태**: Phase 1 부분 완료 (Logging ✅, Position 기반 ✅)
**다음 작업**: Position 마이그레이션 → ai/backtesting.py 수정

---

**마지막 업데이트**: 2025-11-01
**버전**: v4.2
