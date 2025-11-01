"""
AutoTrade Pro v4.0 - 통합 설정 관리 시스템
모든 기능의 설정을 중앙에서 관리하고 UI에서 동적으로 조정

주요 기능:
- YAML 기반 설정 저장/로드
- 실시간 설정 업데이트
- 설정 검증 및 기본값
- 설정 변경 이벤트 처리
"""
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging
from copy import deepcopy

logger = logging.getLogger(__name__)


class UnifiedSettingsManager:
    """통합 설정 관리자"""

    DEFAULT_SETTINGS = {
        # ==================================================
        # 시스템 설정
        # ==================================================
        "system": {
            "trading_enabled": True,
            "test_mode": False,
            "auto_start": False,
            "logging_level": "INFO",
            "max_concurrent_analysis": 3,
        },

        # ==================================================
        # 리스크 관리 설정
        # ==================================================
        "risk_management": {
            "max_position_size": 0.30,           # 최대 포지션 크기 (30%)
            "max_daily_loss": 0.03,              # 일일 최대 손실 (3%)
            "max_total_loss": 0.10,              # 총 최대 손실 (10%)
            "stop_loss_rate": 0.05,              # 기본 손절 비율 (5%)
            "take_profit_rate": 0.10,            # 기본 익절 비율 (10%)
            "max_consecutive_losses": 3,         # 최대 연속 손실 횟수
            "position_limit": 5,                 # 최대 보유 종목 수
            "emergency_stop_loss": 0.15,         # 긴급 손절 (15%)

            # 동적 손절/익절 (Trailing Stop)
            "enable_trailing_stop": True,
            "trailing_stop_atr_multiplier": 2.0,  # ATR 승수
            "trailing_stop_activation_pct": 0.03, # 활성화 수익률 (3%)

            # 켈리 배팅
            "enable_kelly_criterion": False,
            "kelly_fraction": 0.5,                # 켈리 공식 비율 (보수적)
        },

        # ==================================================
        # 매매 전략 설정
        # ==================================================
        "strategies": {
            # 모멘텀 전략
            "momentum": {
                "enabled": True,
                "short_ma_period": 5,
                "long_ma_period": 20,
                "rsi_period": 14,
                "rsi_overbought": 70,
                "rsi_oversold": 30,
            },

            # 변동성 돌파 전략
            "volatility_breakout": {
                "enabled": True,
                "k_value": 0.5,                    # 변동폭 승수
                "entry_time": "09:05",             # 진입 시각
                "exit_time": "15:15",              # 청산 시각
                "use_volume_filter": True,
            },

            # 페어 트레이딩 전략
            "pairs_trading": {
                "enabled": False,
                "pairs": [
                    ["005930", "000660"],          # 삼성전자 - SK하이닉스
                ],
                "spread_threshold": 2.0,            # 표준편차 임계값
                "lookback_period": 60,              # 롤백 기간 (일)
            },

            # 수급 추종 전략
            "institutional_following": {
                "enabled": True,
                "min_net_buy_volume": 1000000000,  # 최소 순매수 금액 (10억)
                "consecutive_days": 3,              # 연속 매수 일수
            },
        },

        # ==================================================
        # AI 분석 설정
        # ==================================================
        "ai_analysis": {
            "enabled": True,
            "default_analyzer": "gemini",          # gemini, gpt4, claude, ensemble
            "min_confidence_score": 0.7,           # 최소 신뢰도
            "timeout_seconds": 30,

            # 시장 레짐 분류
            "market_regime_classification": {
                "enabled": True,
                "update_interval_hours": 4,
                "regimes": {
                    "bull": "모멘텀",                # 상승장 → 모멘텀 전략
                    "bear": "방어적",                # 하락장 → 방어적 전략
                    "sideways": "역추세",            # 횡보장 → 역추세 전략
                },
            },

            # AI 스코어링 가중치
            "scoring_weights": {
                "technical_score": 0.30,
                "fundamental_score": 0.20,
                "ai_prediction_score": 0.25,
                "sentiment_score": 0.15,
                "volume_score": 0.10,
            },
        },

        # ==================================================
        # 백테스팅 설정
        # ==================================================
        "backtesting": {
            "default_initial_capital": 10000000,   # 1천만원
            "commission_rate": 0.00015,            # 0.015%
            "slippage_pct": 0.0005,                # 0.05%
            "generate_report": True,
            "report_format": "html",               # html, pdf

            # 리포트 포함 항목
            "report_includes": {
                "equity_curve": True,
                "drawdown_chart": True,
                "monthly_returns": True,
                "trade_list": True,
                "correlation_matrix": True,
            },
        },

        # ==================================================
        # 파라미터 최적화 설정
        # ==================================================
        "optimization": {
            "method": "bayesian",                  # grid, random, bayesian
            "n_trials": 50,
            "n_jobs": -1,                          # 병렬 처리 (-1 = 모든 CPU)
            "timeout_minutes": 60,

            # 최적화 목표
            "objective_metric": "sharpe_ratio",    # sharpe_ratio, total_return, max_drawdown
        },

        # ==================================================
        # 자동 리밸런싱 설정
        # ==================================================
        "rebalancing": {
            "enabled": False,
            "method": "time_based",                 # time_based, threshold_based
            "frequency_days": 30,                   # 시간 기반 주기
            "threshold_pct": 0.05,                  # 임계값 기반 (5% 이탈)

            # 리스크 패리티
            "use_risk_parity": False,
            "target_volatility": 0.15,              # 목표 변동성 (15%)
        },

        # ==================================================
        # 스크리닝 및 스코어링 설정
        # ==================================================
        "screening": {
            "max_candidates": 50,
            "min_market_cap": 100000000000,         # 최소 시가총액 (1000억)
            "min_volume": 100000,                   # 최소 거래량
            "min_price": 1000,                      # 최소 주가

            # 퀀트 팩터 스크리닝
            "quant_factors": {
                "value": {
                    "enabled": True,
                    "per_max": 15,
                    "pbr_max": 1.5,
                },
                "quality": {
                    "enabled": True,
                    "roe_min": 10,
                    "debt_ratio_max": 100,
                },
                "momentum": {
                    "enabled": True,
                    "return_1m_min": 0.05,
                    "return_3m_min": 0.10,
                },
            },
        },

        # ==================================================
        # 알림 설정
        # ==================================================
        "notification": {
            "enabled": True,
            "channels": {
                "email": False,
                "sms": False,
                "telegram": False,
                "web_push": True,
            },

            # 알림 이벤트
            "events": {
                "order_executed": True,
                "ai_signal": True,
                "stop_loss_triggered": True,
                "daily_report": True,
                "system_error": True,
            },
        },

        # ==================================================
        # UI 설정
        # ==================================================
        "ui": {
            "theme": "light",                       # light, dark
            "language": "ko",                       # ko, en
            "refresh_interval_seconds": 5,
            "show_guide_tour": True,

            # 대시보드 위젯 설정
            "dashboard_widgets": [
                {"id": "account_summary", "enabled": True, "position": {"x": 0, "y": 0, "w": 6, "h": 4}},
                {"id": "holdings", "enabled": True, "position": {"x": 6, "y": 0, "w": 6, "h": 4}},
                {"id": "ai_analysis", "enabled": True, "position": {"x": 0, "y": 4, "w": 12, "h": 6}},
                {"id": "chart", "enabled": True, "position": {"x": 0, "y": 10, "w": 8, "h": 8}},
                {"id": "order_book", "enabled": True, "position": {"x": 8, "y": 10, "w": 4, "h": 8}},
            ],
        },

        # ==================================================
        # 고급 주문 설정
        # ==================================================
        "advanced_orders": {
            "enable_stop_orders": True,
            "enable_ioc_orders": True,              # Immediate Or Cancel
            "enable_fok_orders": True,              # Fill Or Kill
            "default_order_type": "limit",          # market, limit, stop
        },

        # ==================================================
        # 시스템 이상 감지 설정
        # ==================================================
        "anomaly_detection": {
            "enabled": True,
            "check_interval_minutes": 5,
            "alert_threshold": 0.8,                 # 이상 확률 임계값

            # 모니터링 대상
            "monitor_items": {
                "api_response_time": True,
                "order_failure_rate": True,
                "account_balance_change": True,
                "system_cpu_usage": True,
                "system_memory_usage": True,
            },
        },
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        통합 설정 관리자 초기화

        Args:
            config_path: 설정 파일 경로 (없으면 기본 경로 사용)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "unified_settings.yaml"

        self.config_path = config_path
        self.settings = {}
        self.change_listeners: Dict[str, list] = {}

        # 설정 로드
        self.load()

    def load(self) -> Dict[str, Any]:
        """설정 파일에서 로드 (없으면 기본값 사용)"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.settings = yaml.safe_load(f) or {}
                logger.info(f"설정 로드 완료: {self.config_path}")
            else:
                logger.info("설정 파일이 없어 기본값 사용")
                self.settings = deepcopy(self.DEFAULT_SETTINGS)
                self.save()  # 기본 설정 파일 생성
        except Exception as e:
            logger.error(f"설정 로드 실패: {e}, 기본값 사용")
            self.settings = deepcopy(self.DEFAULT_SETTINGS)

        # 기본값과 병합 (새로운 설정 추가 시 대응)
        self._merge_with_defaults()
        return self.settings

    def save(self) -> bool:
        """설정을 파일에 저장"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.settings,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False
                )
            logger.info(f"설정 저장 완료: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        설정 값 가져오기

        Args:
            key_path: 점(.)으로 구분된 설정 경로 (예: "risk_management.max_position_size")
            default: 기본값

        Returns:
            설정 값
        """
        keys = key_path.split('.')
        value = self.settings

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any, save_immediately: bool = True) -> bool:
        """
        설정 값 변경

        Args:
            key_path: 점(.)으로 구분된 설정 경로
            value: 새로운 값
            save_immediately: 즉시 파일에 저장 여부

        Returns:
            성공 여부
        """
        keys = key_path.split('.')
        settings = self.settings

        try:
            # 마지막 키 전까지 탐색
            for key in keys[:-1]:
                if key not in settings:
                    settings[key] = {}
                settings = settings[key]

            # 값 설정
            old_value = settings.get(keys[-1])
            settings[keys[-1]] = value

            # 변경 이벤트 발생
            self._notify_change(key_path, old_value, value)

            # 저장
            if save_immediately:
                self.save()

            logger.info(f"설정 변경: {key_path} = {value}")
            return True
        except Exception as e:
            logger.error(f"설정 변경 실패: {e}")
            return False

    def get_category(self, category: str) -> Dict[str, Any]:
        """카테고리별 설정 가져오기"""
        return self.settings.get(category, {})

    def update_category(self, category: str, settings: Dict[str, Any], save_immediately: bool = True) -> bool:
        """카테고리별 설정 일괄 업데이트"""
        try:
            if category not in self.settings:
                self.settings[category] = {}

            old_settings = self.settings[category].copy()
            self.settings[category].update(settings)

            # 변경 이벤트
            self._notify_change(category, old_settings, self.settings[category])

            if save_immediately:
                self.save()

            logger.info(f"카테고리 설정 업데이트: {category}")
            return True
        except Exception as e:
            logger.error(f"카테고리 설정 업데이트 실패: {e}")
            return False

    def reset_to_defaults(self, category: Optional[str] = None) -> bool:
        """기본값으로 리셋"""
        try:
            if category:
                if category in self.DEFAULT_SETTINGS:
                    self.settings[category] = deepcopy(self.DEFAULT_SETTINGS[category])
                    logger.info(f"카테고리 {category} 기본값 복원")
            else:
                self.settings = deepcopy(self.DEFAULT_SETTINGS)
                logger.info("전체 설정 기본값 복원")

            self.save()
            return True
        except Exception as e:
            logger.error(f"기본값 복원 실패: {e}")
            return False

    def register_change_listener(self, key_path: str, callback: Callable):
        """설정 변경 리스너 등록"""
        if key_path not in self.change_listeners:
            self.change_listeners[key_path] = []
        self.change_listeners[key_path].append(callback)

    def _notify_change(self, key_path: str, old_value: Any, new_value: Any):
        """설정 변경 알림"""
        if key_path in self.change_listeners:
            for callback in self.change_listeners[key_path]:
                try:
                    callback(key_path, old_value, new_value)
                except Exception as e:
                    logger.error(f"변경 리스너 실행 실패: {e}")

    def _merge_with_defaults(self):
        """기본 설정과 병합 (새로운 설정 항목 추가)"""
        def merge_dict(default: dict, current: dict) -> dict:
            for key, value in default.items():
                if key not in current:
                    current[key] = value
                elif isinstance(value, dict) and isinstance(current[key], dict):
                    merge_dict(value, current[key])
            return current

        self.settings = merge_dict(deepcopy(self.DEFAULT_SETTINGS), self.settings)

    def export_to_json(self, file_path: Path) -> bool:
        """JSON 형식으로 내보내기"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON 설정 내보내기 완료: {file_path}")
            return True
        except Exception as e:
            logger.error(f"JSON 내보내기 실패: {e}")
            return False

    def import_from_json(self, file_path: Path) -> bool:
        """JSON 형식에서 가져오기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            self.settings = imported_settings
            self.save()
            logger.info(f"JSON 설정 가져오기 완료: {file_path}")
            return True
        except Exception as e:
            logger.error(f"JSON 가져오기 실패: {e}")
            return False


# 싱글톤 인스턴스
_unified_settings_manager: Optional[UnifiedSettingsManager] = None


def get_unified_settings() -> UnifiedSettingsManager:
    """통합 설정 관리자 인스턴스 가져오기 (싱글톤)"""
    global _unified_settings_manager
    if _unified_settings_manager is None:
        _unified_settings_manager = UnifiedSettingsManager()
    return _unified_settings_manager
