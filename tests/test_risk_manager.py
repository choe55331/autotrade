Unified Risk Manager Tests

import pytest
from strategy.risk.unified_risk_manager import UnifiedRiskManager, RiskMode


class TestUnifiedRiskManager:
    """UnifiedRiskManager 테스트"""

    @pytest.fixture
    def risk_manager(self):
        """RiskManager 인스턴스"""
        return UnifiedRiskManager(initial_capital=10_000_000)

    def test_initialization(self, risk_manager):
        """초기화 테스트"""
        assert risk_manager.initial_capital == 10_000_000
        assert risk_manager.current_mode == RiskMode.MODERATE

    def test_position_size_calculation(self, risk_manager):
        """포지션 크기 계산 테스트"""
        quantity = risk_manager.calculate_position_size(
            stock_price=70000,
            available_cash=10_000_000
        )

        assert quantity > 0
        assert quantity * 70000 <= 10_000_000

    def test_exit_thresholds(self, risk_manager):
        """청산 임계값 테스트"""
        entry_price = 70000
        thresholds = risk_manager.get_exit_thresholds(entry_price)

        assert 'stop_loss' in thresholds
        assert 'take_profit' in thresholds
        assert thresholds['stop_loss'] < entry_price
        assert thresholds['take_profit'] > entry_price

    def test_kelly_criterion(self, risk_manager):
        """Kelly Criterion 테스트"""
        kelly_pct = risk_manager._calculate_kelly_criterion(
            win_rate=0.6,
            risk_reward_ratio=2.0
        )

        assert kelly_pct > 0
        assert kelly_pct <= 25.0

    def test_mode_switching(self, risk_manager):
        """모드 전환 테스트"""
        initial_mode = risk_manager.current_mode

        risk_manager.switch_mode(RiskMode.AGGRESSIVE)

        assert risk_manager.current_mode == RiskMode.AGGRESSIVE
        assert risk_manager.current_mode != initial_mode
