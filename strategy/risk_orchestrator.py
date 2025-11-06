AutoTrade Pro - 통합 리스크 관리 조율 시스템
모든 리스크 관리 모듈을 통합 조율
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """리스크 수준"""
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskCheck:
    """리스크 체크 결과"""
    check_name: str
    passed: bool
    risk_level: RiskLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskAssessment:
    """종합 리스크 평가"""
    overall_risk_level: RiskLevel
    can_trade: bool
    checks: List[RiskCheck]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

    def get_failed_checks(self) -> List[RiskCheck]:
        """실패한 체크 목록"""
        return [check for check in self.checks if not check.passed]

    def get_high_risk_checks(self) -> List[RiskCheck]:
        """높은 리스크 체크 목록"""
        return [
            check for check in self.checks
            if check.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]


class RiskOrchestrator:
    """
    통합 리스크 관리 조율자

    기능:
    1. 정적 리스크 체크 (RiskManager)
    2. 동적 리스크 모드 관리 (DynamicRiskManager)
    3. 트레일링 스톱 관리 (TrailingStopManager)
    4. 고급 리스크 분석 (AdvancedRiskAnalytics)

    통합:
    - 모든 리스크 체크를 조율
    - 우선순위에 따라 리스크 평가
    - 종합 거래 가능 여부 판단
    """

    def __init__(self, settings: Optional[Dict] = None):
        self.settings = settings or {}

        self.static_risk_manager = None
        self.dynamic_risk_manager = None
        self.trailing_stop_manager = None
        self.risk_analytics = None

        self.risk_history: List[RiskAssessment] = []
        self.max_history_size = 1000

        self.enable_static_checks = self.settings.get('enable_static_checks', True)
        self.enable_dynamic_mode = self.settings.get('enable_dynamic_mode', True)
        self.enable_trailing_stop = self.settings.get('enable_trailing_stop', True)
        self.enable_analytics = self.settings.get('enable_analytics', False)

        logger.info("리스크 조율 시스템 초기화")

    def initialize_managers(self):
        """리스크 매니저들 초기화"""
        try:
            if self.enable_static_checks:
                from .risk_manager import RiskManager
                self.static_risk_manager = RiskManager(self.settings.get('static_risk', {}))
                logger.info("정적 리스크 매니저 초기화 완료")

            if self.enable_dynamic_mode:
                try:
                    from .dynamic_risk_manager import DynamicRiskManager
                    self.dynamic_risk_manager = DynamicRiskManager()
                    logger.info("동적 리스크 매니저 초기화 완료")
                except ImportError:
                    logger.warning("동적 리스크 매니저를 불러올 수 없습니다")

            if self.enable_trailing_stop:
                try:
                    from .trailing_stop_manager import TrailingStopManager
                    self.trailing_stop_manager = TrailingStopManager(
                        self.settings.get('trailing_stop', {})
                    )
                    logger.info("트레일링 스톱 매니저 초기화 완료")
                except ImportError:
                    logger.warning("트레일링 스톱 매니저를 불러올 수 없습니다")

            if self.enable_analytics:
                try:
                    from .advanced_risk_analytics import AdvancedRiskAnalytics
                    self.risk_analytics = AdvancedRiskAnalytics()
                    logger.info("고급 리스크 분석 초기화 완료")
                except ImportError:
                    logger.warning("고급 리스크 분석을 불러올 수 없습니다")

        except Exception as e:
            logger.error(f"리스크 매니저 초기화 실패: {e}")

    def assess_trading_risk(
        self,
        action: str,
        stock_code: str,
        quantity: int,
        price: float,
        account_info: Optional[Dict] = None,
        position_info: Optional[Dict] = None
    ) -> RiskAssessment:
        매매 리스크 종합 평가

        Args:
            action: 매매 행동 ("BUY" or "SELL")
            stock_code: 종목 코드
            quantity: 수량
            price: 가격
            account_info: 계좌 정보
            position_info: 포지션 정보

        Returns:
            종합 리스크 평가
        checks: List[RiskCheck] = []
        recommendations: List[str] = []

        if self.static_risk_manager:
            static_checks = self._check_static_risks(
                action, stock_code, quantity, price, account_info, position_info
            )
            checks.extend(static_checks)

        if self.dynamic_risk_manager:
            dynamic_checks = self._check_dynamic_risks(
                action, stock_code, quantity, price
            )
            checks.extend(dynamic_checks)

        if self.trailing_stop_manager and action == "SELL" and position_info:
            trailing_checks = self._check_trailing_stop(stock_code, price, position_info)
            checks.extend(trailing_checks)

        if self.risk_analytics and account_info:
            analytics_checks = self._check_analytics(account_info, position_info)
            checks.extend(analytics_checks)

        overall_risk_level = self._calculate_overall_risk(checks)
        can_trade = self._determine_tradability(checks, overall_risk_level)

        recommendations = self._generate_recommendations(checks, overall_risk_level)

        assessment = RiskAssessment(
            overall_risk_level=overall_risk_level,
            can_trade=can_trade,
            checks=checks,
            recommendations=recommendations
        )

        self._save_assessment(assessment)

        return assessment

    def _check_static_risks(
        self,
        action: str,
        stock_code: str,
        quantity: int,
        price: float,
        account_info: Optional[Dict],
        position_info: Optional[Dict]
    ) -> List[RiskCheck]:
        checks = []

        if not self.static_risk_manager or not account_info:
            return checks

        total_assets = account_info.get('total_assets', 0)
        position_value = quantity * price

        try:
            is_valid = self.static_risk_manager.validate_position_size(
                position_value, total_assets
            )
            checks.append(RiskCheck(
                check_name="포지션 크기 검증",
                passed=is_valid,
                risk_level=RiskLevel.LOW if is_valid else RiskLevel.HIGH,
                message=f"포지션 크기: {position_value:,}원 / 총 자산: {total_assets:,}원",
                metadata={'position_value': position_value, 'total_assets': total_assets}
            ))
        except Exception as e:
            logger.error(f"포지션 크기 검증 실패: {e}")

        daily_loss = account_info.get('daily_loss', 0)
        max_daily_loss = total_assets * self.settings.get('max_daily_loss_pct', 0.03)

        checks.append(RiskCheck(
            check_name="일일 손실 한도",
            passed=abs(daily_loss) < max_daily_loss,
            risk_level=RiskLevel.MEDIUM if abs(daily_loss) < max_daily_loss else RiskLevel.CRITICAL,
            message=f"일일 손실: {daily_loss:+,.0f}원 / 한도: {max_daily_loss:,.0f}원",
            metadata={'daily_loss': daily_loss, 'max_daily_loss': max_daily_loss}
        ))

        return checks

    def _check_dynamic_risks(
        self,
        action: str,
        stock_code: str,
        quantity: int,
        price: float
    ) -> List[RiskCheck]:
        checks = []

        if not self.dynamic_risk_manager:
            return checks

        try:
            current_mode = getattr(self.dynamic_risk_manager, 'current_mode', None)
            if current_mode:
                risk_level = RiskLevel.LOW

                if str(current_mode) == "CONSERVATIVE":
                    risk_level = RiskLevel.MEDIUM
                    checks.append(RiskCheck(
                        check_name="동적 리스크 모드",
                        passed=True,
                        risk_level=risk_level,
                        message=f"현재 모드: {current_mode} (보수적 거래 권장)",
                        metadata={'mode': str(current_mode)}
                    ))
        except Exception as e:
            logger.error(f"동적 리스크 체크 실패: {e}")

        return checks

    def _check_trailing_stop(
        self,
        stock_code: str,
        current_price: float,
        position_info: Dict
    ) -> List[RiskCheck]:
        checks = []

        if not self.trailing_stop_manager:
            return checks

        try:
            should_exit, reason = self.trailing_stop_manager.update(stock_code, current_price)

            checks.append(RiskCheck(
                check_name="트레일링 스톱",
                passed=not should_exit,
                risk_level=RiskLevel.HIGH if should_exit else RiskLevel.SAFE,
                message=f"트레일링 스톱: {reason if should_exit else '정상'}",
                metadata={'should_exit': should_exit, 'reason': reason}
            ))
        except Exception as e:
            logger.error(f"트레일링 스톱 체크 실패: {e}")

        return checks

    def _check_analytics(
        self,
        account_info: Dict,
        position_info: Optional[Dict]
    ) -> List[RiskCheck]:
        checks = []

        if not self.risk_analytics:
            return checks


        return checks

    def _calculate_overall_risk(self, checks: List[RiskCheck]) -> RiskLevel:
        """종합 리스크 레벨 계산"""
        if not checks:
            return RiskLevel.SAFE

        risk_levels = [check.risk_level for check in checks]

        if RiskLevel.CRITICAL in risk_levels:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_levels:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_levels:
            return RiskLevel.MEDIUM
        elif RiskLevel.LOW in risk_levels:
            return RiskLevel.LOW
        else:
            return RiskLevel.SAFE

    def _determine_tradability(
        self,
        checks: List[RiskCheck],
        overall_risk: RiskLevel
    ) -> bool:
        if overall_risk == RiskLevel.CRITICAL:
            return False

        failed_checks = [check for check in checks if not check.passed]

        high_risk_failures = [
            check for check in failed_checks
            if check.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]

        if len(high_risk_failures) >= 2:
            return False

        return True

    def _generate_recommendations(
        self,
        checks: List[RiskCheck],
        overall_risk: RiskLevel
    ) -> List[str]:
        recommendations = []

        failed_checks = [check for check in checks if not check.passed]

        for check in failed_checks:
            if "포지션 크기" in check.check_name:
                recommendations.append("포지션 크기를 줄이세요")
            elif "일일 손실" in check.check_name:
                recommendations.append("당일 거래를 중단하세요")
            elif "트레일링 스톱" in check.check_name:
                recommendations.append("즉시 청산을 고려하세요")

        if overall_risk == RiskLevel.CRITICAL:
            recommendations.append("⚠️ 긴급: 모든 거래를 중단하고 포지션을 정리하세요")
        elif overall_risk == RiskLevel.HIGH:
            recommendations.append("⚠️ 주의: 신규 진입을 자제하고 보수적으로 거래하세요")
        elif overall_risk == RiskLevel.MEDIUM:
            recommendations.append("주의: 리스크를 줄이고 신중하게 거래하세요")

        return recommendations

    def _save_assessment(self, assessment: RiskAssessment):
        """평가 결과 저장"""
        self.risk_history.append(assessment)

        if len(self.risk_history) > self.max_history_size:
            self.risk_history = self.risk_history[-self.max_history_size:]

    def get_risk_summary(self) -> Dict[str, Any]:
        """리스크 요약 정보"""
        if not self.risk_history:
            return {
                'total_assessments': 0,
                'recent_risk_level': 'N/A',
                'trade_approval_rate': 0.0
            }

        recent_assessments = self.risk_history[-100:]

        return {
            'total_assessments': len(self.risk_history),
            'recent_assessments': len(recent_assessments),
            'recent_risk_level': recent_assessments[-1].overall_risk_level.value,
            'trade_approval_rate': sum(1 for a in recent_assessments if a.can_trade) / len(recent_assessments),
            'critical_count': sum(1 for a in recent_assessments if a.overall_risk_level == RiskLevel.CRITICAL),
            'high_count': sum(1 for a in recent_assessments if a.overall_risk_level == RiskLevel.HIGH),
        }


_risk_orchestrator_instance: Optional[RiskOrchestrator] = None


def get_risk_orchestrator(settings: Optional[Dict] = None) -> RiskOrchestrator:
    """글로벌 리스크 조율자 인스턴스 반환"""
    global _risk_orchestrator_instance
    if _risk_orchestrator_instance is None:
        _risk_orchestrator_instance = RiskOrchestrator(settings)
        _risk_orchestrator_instance.initialize_managers()
    return _risk_orchestrator_instance
