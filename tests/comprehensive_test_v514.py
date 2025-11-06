Comprehensive Test Suite for v5.14 Enhancements
Market Scanner, Trading Bot
import sys
import os
from datetime import datetime, timedelta
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_market_scanner():
    """Test Market Scanner"""
    print("\n" + "=" * 60)
    print("Testing Market Scanner")
    print("=" * 60)

    try:
        from features.market_scanner import (
            MarketScanner, ScannerSignal, SignalStrength
        )

        print("\n[Test 1] Market Scanner Initialization")
        scanner = MarketScanner(
            volume_spike_threshold=2.0,
            volatility_threshold=2.5,
            breakout_lookback=20
        )
        print(f"✓ Initialized: volume_threshold={scanner.volume_spike_threshold}")

        print("\n[Test 2] Generating Sample Market Data")
        market_data = {}
        price_histories = {}

        stock_codes = ['005930', '000660', '035420']

        for stock in stock_codes:
            volume_spike = 3.0 if stock == '005930' else 1.0
            market_data[stock] = {
                'stock_code': stock,
                'stock_name': f'Stock {stock}',
                'price': 70000 + np.random.normal(0, 2000),
                'volume': int(100000 * volume_spike),
                'high': 72000,
                'low': 68000,
                'bid': 69900,
                'ask': 70100
            }

            history = []
            for i in range(30):
                history.append({
                    'date': (datetime.now() - timedelta(days=30-i)).strftime('%Y-%m-%d'),
                    'open': 70000,
                    'high': 71000,
                    'low': 69000,
                    'close': 70000 + np.random.normal(0, 1000),
                    'volume': 100000
                })

            price_histories[stock] = history

        print(f"✓ Generated data for {len(market_data)} stocks")

        print("\n[Test 3] Scanning Market")
        signals = scanner.scan_market(market_data, price_histories)
        print(f"✓ Scan complete: {len(signals)} signals found")

        for signal in signals[:3]:
            print(f"  - {signal.stock_name}: {signal.signal_type.value} "
                  f"(strength={signal.strength.name}, confidence={signal.confidence:.2f})")

        print("\n[Test 4] Top Opportunities")
        opportunities = scanner.get_top_opportunities(
            signals,
            min_confidence=0.6,
            min_strength=SignalStrength.MODERATE,
            top_n=5
        )
        print(f"✓ Found {len(opportunities)} top opportunities")

        print("\n[Test 5] Scanner Statistics")
        stats = scanner.get_statistics()
        print(f"✓ Statistics:")
        print(f"  Total signals: {stats.total_signals}")
        print(f"  Avg confidence: {stats.avg_confidence:.2f}")
        print(f"  Opportunities: {stats.opportunities_found}")

        print("\n✅ Market Scanner tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Market Scanner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trading_bot():
    """Test Trading Bot"""
    print("\n" + "=" * 60)
    print("Testing Trading Bot")
    print("=" * 60)

    try:
        from strategy.trading_bot import (
            AutomatedTradingBot, TradingMode, BotStatus,
            MomentumStrategy, MeanReversionStrategy, BreakoutStrategy
        )

        print("\n[Test 1] Trading Bot Initialization")
        bot = AutomatedTradingBot(
            initial_capital=10000000,
            max_position_size=0.2,
            max_positions=5,
            stop_loss_pct=0.05,
            take_profit_pct=0.10,
            trading_mode=TradingMode.PAPER
        )
        print(f"✓ Initialized: capital={bot.initial_capital:,.0f}, mode={bot.trading_mode.value}")

        print("\n[Test 2] Adding Strategies")
        bot.add_strategy(MomentumStrategy(lookback_period=20, threshold=0.05))
        bot.add_strategy(MeanReversionStrategy(lookback_period=20, std_threshold=2.0))
        bot.add_strategy(BreakoutStrategy(lookback_period=20, breakout_threshold=0.02))
        print(f"✓ Added {len(bot.strategies)} strategies")

        print("\n[Test 3] Starting Bot")
        bot.start()
        print(f"✓ Bot started: status={bot.status.value}")

        print("\n[Test 4] Generating Market Data")
        market_data = {}
        price_histories = {}

        stock_codes = ['005930', '000660', '035420', '051910', '005380']

        for i, stock in enumerate(stock_codes):
            trend = 1000 if i == 0 else 0

            market_data[stock] = {
                'stock_code': stock,
                'stock_name': f'Stock {stock}',
                'price': 70000 + trend + np.random.normal(0, 500),
                'volume': 1000000,
                'high': 71000 + trend,
                'low': 69000 + trend
            }

            history = []
            for j in range(30):
                day_trend = trend * (j / 30) if i == 0 else 0
                history.append({
                    'date': (datetime.now() - timedelta(days=30-j)).strftime('%Y-%m-%d'),
                    'open': 70000 + day_trend,
                    'high': 71000 + day_trend,
                    'low': 69000 + day_trend,
                    'close': 70000 + day_trend + np.random.normal(0, 500),
                    'volume': 1000000
                })

            price_histories[stock] = history

        print(f"✓ Generated data for {len(market_data)} stocks")

        print("\n[Test 5] Executing Trading Cycle")
        for cycle in range(3):
            bot.execute_cycle(market_data, price_histories)
            print(f"✓ Cycle {cycle + 1} complete: "
                  f"positions={len(bot.positions)}, cash={bot.cash:,.0f}")

        print("\n[Test 6] Bot Performance")
        perf = bot.get_performance()
        print(f"✓ Performance metrics:")
        print(f"  Total trades: {perf.total_trades}")
        print(f"  Current positions: {perf.current_positions}")
        print(f"  Win rate: {perf.win_rate:.1%}")
        print(f"  Total P&L: {perf.total_pnl:+,.0f}원 ({perf.total_pnl_pct:+.2f}%)")
        print(f"  Available capital: {perf.available_capital:,.0f}원")

        print("\n[Test 7] Testing Stop-Loss")
        if bot.positions:
            for stock_code, position in list(bot.positions.items()):
                market_data[stock_code]['price'] = position.entry_price * 0.92
                position.current_price = market_data[stock_code]['price']

            bot._check_exit_conditions(market_data)
            print(f"✓ Stop-loss check complete")

        print("\n[Test 8] Pause and Resume")
        bot.pause()
        print(f"✓ Bot paused: status={bot.status.value}")

        bot.resume()
        print(f"✓ Bot resumed: status={bot.status.value}")

        print("\n[Test 9] Stopping Bot")
        bot.stop()
        print(f"✓ Bot stopped: status={bot.status.value}")

        print("\n✅ Trading Bot tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Trading Bot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Integration Test - All v5.14 Features Together"""
    print("\n" + "=" * 60)
    print("Integration Test - v5.14 Features")
    print("=" * 60)

    try:
        from features.market_scanner import get_market_scanner
        from strategy.trading_bot import get_trading_bot

        print("\n[Test 1] Initialize All Components")
        scanner = get_market_scanner()
        bot = get_trading_bot()
        print("✓ All components initialized")

        print("\n[Test 2] Integrated Workflow")

        market_data = {}
        price_histories = {}

        for stock in ['005930', '000660', '035420', '051910']:
            market_data[stock] = {
                'stock_code': stock,
                'stock_name': f'Stock {stock}',
                'price': 70000 + np.random.normal(0, 2000),
                'volume': np.random.randint(500000, 2000000),
                'high': 72000,
                'low': 68000,
                'bid': 69900,
                'ask': 70100
            }

            history = []
            for i in range(40):
                history.append({
                    'date': (datetime.now() - timedelta(days=40-i)).strftime('%Y-%m-%d'),
                    'open': 70000,
                    'high': 71000,
                    'low': 69000,
                    'close': 70000 + np.random.normal(0, 1000),
                    'volume': 1000000
                })

            price_histories[stock] = history

        signals = scanner.scan_market(market_data, price_histories)
        print(f"✓ Market scan: {len(signals)} signals")

        opportunities = scanner.get_top_opportunities(signals, top_n=3)
        print(f"✓ Top opportunities: {len(opportunities)}")

        bot.start()
        bot.execute_cycle(market_data, price_histories)
        print(f"✓ Bot executed: {len(bot.positions)} positions opened")

        perf = bot.get_performance()
        print(f"✓ Bot performance: {perf.total_trades} trades, "
              f"{perf.total_pnl:+,.0f}원 P&L")

        print("\n✅ Integration test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all v5.14 tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUITE - v5.14")
    print("Market Scanner + Trading Bot")
    print("=" * 60)

    results = []

    results.append(("Market Scanner", test_market_scanner()))

    results.append(("Trading Bot", test_trading_bot()))

    results.append(("Integration Test", test_integration()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY - v5.14")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - v5.14 READY FOR DEPLOYMENT")
    else:
        print("⚠️ SOME TESTS FAILED - REVIEW REQUIRED")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
