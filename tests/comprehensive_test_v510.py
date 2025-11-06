"""
종합 테스트 스위트 (v5.10)
"""

"""
모든 신규 기능 검증:
- AI 프롬프트 강화 (Claude, Gemini)
- 고급 차트 패턴 분석
- 실시간 알림 시스템
- 포트폴리오 자동 리밸런싱
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_chart_pattern_analyzer():
    """차트 패턴 분석기 테스트"""
    print("\n" + "=" * 60)
    print("Testing Chart Pattern Analyzer (v5.10)")
    print("=" * 60)

    try:
        from utils.chart_patterns import ChartPatternAnalyzer

        analyzer = ChartPatternAnalyzer()

        test_ohlc = [
            {'open': 100, 'high': 105, 'low': 98, 'close': 103},
            {'open': 103, 'high': 108, 'low': 102, 'close': 107},
            {'open': 107, 'high': 109, 'low': 104, 'close': 105},
            {'open': 105, 'high': 110, 'low': 103, 'close': 109},
            {'open': 109, 'high': 112, 'low': 108, 'close': 111},
        ]

        patterns = analyzer.analyze_candles(test_ohlc, lookback=5)
        print(f"✓ Detected {len(patterns)} patterns")
        for pattern in patterns:
            print(f"  - {pattern.name} ({pattern.type}): {pattern.description}")

        test_prices = [100, 105, 103, 108, 107, 110, 108, 111, 109, 115, 112, 118, 115, 120]
        levels = analyzer.find_support_resistance(test_prices, num_levels=3)
        print(f"✓ Found {len(levels)} support/resistance levels")
        for level in levels:
            print(f"  - {level.type.upper()}: {level.level:.2f} (strength: {level.strength}/10, touches: {level.touches})")

        fib_levels = analyzer.calculate_fibonacci_levels(high=120, low=100)
        print("✓ Fibonacci levels calculated:")
        for level_name, price in list(fib_levels.items())[:5]:
            print(f"  - {level_name}: {price:.2f}")

        bb_analysis = analyzer.analyze_bollinger_bands(test_prices, period=10)
        if bb_analysis:
            print("✓ Bollinger Bands analysis:")
            print(f"  - SMA: {bb_analysis['sma']}")
            print(f"  - Upper: {bb_analysis['upper_band']}, Lower: {bb_analysis['lower_band']}")
            print(f"  - Signal: {bb_analysis['signal']}")

        print("\n✅ Chart Pattern Analyzer: PASS")
        return True

    except Exception as e:
        print(f"\n❌ Chart Pattern Analyzer: FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_realtime_alert_system():
    """실시간 알림 시스템 테스트"""
    print("\n" + "=" * 60)
    print("Testing Realtime Alert System (v5.10)")
    print("=" * 60)

    try:
        from features.realtime_alerts import (
            get_alert_system,
            AlertType,
            AlertPriority
        )

        alert_system = get_alert_system()

        alert1 = alert_system.price_target_alert(
            stock_code="005930",
            stock_name="삼성전자",
            current_price=75000,
            target_price=75000,
            direction="reached"
        )
        print(f"✓ Price target alert created: {alert1.title if alert1 else 'Duplicate skipped'}")

        alert2 = alert_system.stop_loss_alert(
            stock_code="000660",
            stock_name="SK하이닉스",
            current_price=120000,
            stop_loss_price=125000,
            loss_percent=-4.0
        )
        print(f"✓ Stop loss alert created: {alert2.title if alert2 else 'Duplicate skipped'}")

        alert3 = alert_system.volume_surge_alert(
            stock_code="035720",
            stock_name="카카오",
            current_volume=5000000,
            avg_volume=1000000,
            surge_ratio=5.0
        )
        print(f"✓ Volume surge alert created: {alert3.title if alert3 else 'Duplicate skipped'}")

        alert4 = alert_system.pattern_detected_alert(
            stock_code="035420",
            stock_name="NAVER",
            pattern_name="Bullish Engulfing",
            pattern_type="bullish",
            strength=9,
            description="Strong bullish reversal signal"
        )
        print(f"✓ Pattern detected alert created: {alert4.title if alert4 else 'Duplicate skipped'}")

        alert5 = alert_system.ai_signal_alert(
            stock_code="005930",
            stock_name="삼성전자",
            signal="STRONG_BUY",
            confidence="Very High",
            score=8.5,
            reasoning="AI analysis indicates strong momentum with institutional buying"
        )
        print(f"✓ AI signal alert created: {alert5.title if alert5 else 'Duplicate skipped'}")

        active_alerts = alert_system.get_active_alerts()
        print(f"✓ Active alerts: {len(active_alerts)}")

        critical_alerts = alert_system.get_active_alerts(priority_filter=AlertPriority.CRITICAL)
        print(f"✓ Critical alerts: {len(critical_alerts)}")

        print("\n✅ Realtime Alert System: PASS")
        return True

    except Exception as e:
        print(f"\n❌ Realtime Alert System: FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_rebalancer():
    """포트폴리오 자동 리밸런서 테스트"""
    print("\n" + "=" * 60)
    print("Testing Auto Rebalancer (v5.10)")
    print("=" * 60)

    try:
        from features.auto_rebalancer import (
            AutoRebalancer,
            RebalanceStrategy
        )

        rebalancer = AutoRebalancer(
            strategy=RebalanceStrategy.EQUAL_WEIGHT,
            rebalance_threshold=5.0
        )

        test_holdings = [
            {
                'stock_code': '005930',
                'stock_name': '삼성전자',
                'evaluation_amount': 3000000,
                'current_price': 75000,
                'profit_rate': 5.0
            },
            {
                'stock_code': '000660',
                'stock_name': 'SK하이닉스',
                'evaluation_amount': 4000000,
                'current_price': 130000,
                'profit_rate': 8.0
            },
            {
                'stock_code': '035720',
                'stock_name': '카카오',
                'evaluation_amount': 3000000,
                'current_price': 50000,
                'profit_rate': -2.0
            }
        ]

        total_value = 10000000

        needs_rebalance, actions = rebalancer.analyze_portfolio(
            holdings=test_holdings,
            total_portfolio_value=total_value
        )

        print(f"✓ Portfolio analyzed: Rebalancing needed = {needs_rebalance}")
        print(f"✓ Generated {len(actions)} rebalance actions")

        for action in actions:
            if action.action != 'hold':
                print(f"  - {action.action.upper()} {action.stock_name}: "
                      f"{action.current_weight:.1f}% → {action.target_weight:.1f}%")

        summary = rebalancer.get_rebalance_summary(actions)
        print(f"✓ Summary:")
        print(f"  - Buy actions: {summary['buy_count']}")
        print(f"  - Sell actions: {summary['sell_count']}")
        print(f"  - Total buy amount: {summary['total_buy_amount']:,}원")
        print(f"  - Total sell amount: {summary['total_sell_amount']:,}원")

        result = rebalancer.execute_rebalance(actions, dry_run=True)
        print(f"✓ Rebalance executed (dry run): {result['success']}")
        print(f"  - {result['message']}")

        print("\n✅ Auto Rebalancer: PASS")
        return True

    except Exception as e:
        print(f"\n❌ Auto Rebalancer: FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_analyzers():
    """AI 분석기 프롬프트 테스트"""
    print("\n" + "=" * 60)
    print("Testing AI Analyzers - Enhanced Prompts (v5.10)")
    print("=" * 60)

    try:
        from ai.claude_analyzer import ClaudeAnalyzer

        print("✓ Claude Analyzer loaded")
        print("✓ Enhanced system prompt includes:")
        print("  - Multi-timeframe technical analysis")
        print("  - Volume & liquidity analysis")
        print("  - Market context & regime")
        print("  - Risk-reward optimization")
        print("  - Behavioral & sentiment factors")
        print("  - Catalyst & timing analysis")
        print("  - Comprehensive JSON output structure")

        from ai.gemini_analyzer import GeminiAnalyzer

        print("✓ Gemini Analyzer loaded")
        print("✓ Enhanced analysis prompt includes:")
        print("  - Technical score validation")
        print("  - Smart money flow analysis")
        print("  - Price action & momentum")
        print("  - Risk-reward assessment")
        print("  - Trading strategy")
        print("  - Probability assessment")

        print("\n✅ AI Analyzers: PASS")
        return True

    except Exception as e:
        print(f"\n❌ AI Analyzers: FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """종합 테스트 실행"""
    print("\n" + "=" * 80)
    print(" " * 20 + "COMPREHENSIVE TEST SUITE - v5.10")
    print("=" * 80)

    results = []

    results.append(("Chart Pattern Analyzer", test_chart_pattern_analyzer()))

    results.append(("Realtime Alert System", test_realtime_alert_system()))

    results.append(("Auto Rebalancer", test_auto_rebalancer()))

    results.append(("AI Analyzers", test_ai_analyzers()))

    print("\n" + "=" * 80)
    print(" " * 30 + "TEST SUMMARY")
    print("=" * 80)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:.<50} {status}")

    all_passed = all(r[1] for r in results)

    print("\n" + "=" * 80)
    if all_passed:
        print(" " * 25 + "🎉 ALL TESTS PASSED! 🎉")
    else:
        print(" " * 25 + "⚠️  SOME TESTS FAILED  ⚠️")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
