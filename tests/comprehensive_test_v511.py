"""
Comprehensive Test Suite for v5.11 Enhancements
Dashboard UX, Performance Monitoring, Advanced Backtesting
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_performance_monitor():
    """Test Performance Monitor"""
    print("\n" + "=" * 60)
    print("Testing Performance Monitor")
    print("=" * 60)

    try:
        from utils.performance_monitor import PerformanceMonitor
        import time

        monitor = PerformanceMonitor()

        print("\n[Test 1] Context Manager for Performance Measurement")
        with monitor.measure("test_operation", {"category": "test"}):
            time.sleep(0.1)
        print("✓ Context manager measurement successful")

        print("\n[Test 2] Decorator for Function Tracking")

        @monitor.track(name="test_function")
        def sample_function(n):
            """Sample function for testing"""
            total = 0
            for i in range(n):
                total += i
            return total

        result = sample_function(1000)
        print(f"✓ Decorator tracking successful (result: {result})")

        print("\n[Test 3] Performance Statistics")
        stats = monitor.get_statistics()
        print(f"✓ Statistics retrieved: {len(stats)} metrics tracked")
        if stats:
            for name, stat in list(stats.items())[:3]:
                print(f"  - {name}: avg={stat['avg_duration']:.4f}s, calls={stat['count']}")

        print("\n[Test 4] Bottleneck Detection")
        bottlenecks = monitor.detect_bottlenecks(threshold_seconds=0.0)
        print(f"✓ Bottleneck detection complete: {len(bottlenecks)} found")

        print("\n[Test 5] Performance Report Generation")
        report = monitor.generate_report(include_system=True)
        print(f"✓ Report generated with {len(report.get('metrics', {}))} metrics")
        print(f"  System metrics included: {bool(report.get('system_info'))}")

        print("\n[Test 6] Export Metrics to JSON")
        json_path = "/tmp/performance_metrics_test.json"
        monitor.export_to_json(json_path)
        print(f"✓ Metrics exported to {json_path}")

        print("\n✅ Performance Monitor tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Performance Monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_backtester():
    """Test Advanced Backtester"""
    print("\n" + "=" * 60)
    print("Testing Advanced Backtester")
    print("=" * 60)

    try:
        from ai.advanced_backtester import AdvancedBacktester

        print("\n[Test 1] Backtester Initialization")
        backtester = AdvancedBacktester(
            initial_capital=10_000_000,
            commission_rate=0.00015,
            slippage_rate=0.001,
            tax_rate=0.0023
        )
        print(f"✓ Backtester initialized with capital: {backtester.initial_capital:,.0f}원")

        print("\n[Test 2] Creating Sample Market Data")
        sample_data = {
            '005930': [
                {
                    'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'open': 70000 + i * 100,
                    'high': 71000 + i * 100,
                    'low': 69000 + i * 100,
                    'close': 70500 + i * 100,
                    'volume': 10_000_000
                }
                for i in range(20, -1, -1)
            ]
        }
        print(f"✓ Sample data created: {len(sample_data['005930'])} days")

        print("\n[Test 3] Running Buy-and-Hold Strategy")

        def buy_and_hold_strategy(backtester, current_date, stock_data):
            """Simple buy-and-hold strategy"""
            if backtester.current_date_index == 0:
                price = stock_data[0]['close']
                quantity = int(backtester.cash * 0.9 / price)
                if quantity > 0:
                    backtester.buy('005930', 'Samsung', price, quantity)

        result = backtester.run_backtest(buy_and_hold_strategy, sample_data)
        print(f"✓ Backtest completed")
        print(f"  Final Equity: {result.final_equity:,.0f}원")
        print(f"  Total Return: {result.total_return:.2f}%")
        print(f"  Total Trades: {result.total_trades}")

        print("\n[Test 4] Risk Metrics Calculation")
        print(f"✓ Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"✓ Sortino Ratio: {result.sortino_ratio:.2f}")
        print(f"✓ Max Drawdown: {result.max_drawdown:.2f}%")
        print(f"✓ Win Rate: {result.win_rate:.2f}%")

        print("\n[Test 5] Trade History")
        print(f"✓ Trades recorded: {len(result.trades)}")
        if result.trades:
            print(f"  First trade: {result.trades[0]}")

        print("\n[Test 6] Equity Curve")
        print(f"✓ Equity curve points: {len(result.equity_curve)}")
        if len(result.equity_curve) >= 2:
            print(f"  Start: {result.equity_curve[0]['equity']:,.0f}원")
            print(f"  End: {result.equity_curve[-1]['equity']:,.0f}원")

        print("\n[Test 7] Monte Carlo Simulation")
        if result.total_trades > 0:
            mc_result = backtester.monte_carlo_simulation(result, num_simulations=100)
            print(f"✓ Monte Carlo simulation complete")
            print(f"  Mean Return: {mc_result['mean_return']:.2f}%")
            print(f"  Std Dev: {mc_result['std_return']:.2f}%")
            print(f"  95% VaR: {mc_result['var_95']:.2f}%")
        else:
            print("⚠ Skipped (no trades to simulate)")

        print("\n✅ Advanced Backtester tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Advanced Backtester test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_loading_utils_structure():
    """Test Loading Utils JavaScript file structure"""
    print("\n" + "=" * 60)
    print("Testing Loading Utils JavaScript Structure")
    print("=" * 60)

    try:
        js_file = "/home/user/autotrade/dashboard/static/js/loading-utils.js"

        print("\n[Test 1] File Existence")
        if not os.path.exists(js_file):
            print(f"❌ File not found: {js_file}")
            return False
        print(f"✓ File exists: {js_file}")

        print("\n[Test 2] File Content Structure")
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_components = [
            'class LoadingManager',
            'class ToastManager',
            'animateNumber',
            'smoothScrollTo',
            'fadeIn',
            'fadeOut',
            'lazyLoadImages',
            'debounce',
            'throttle'
        ]

        for component in required_components:
            if component in content:
                print(f"✓ Found: {component}")
            else:
                print(f"❌ Missing: {component}")
                return False

        print(f"\n✓ Total file size: {len(content):,} characters")
        print(f"✓ Total lines: {content.count(chr(10)) + 1}")

        print("\n✅ Loading Utils structure tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Loading Utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_animations_css_structure():
    """Test Animations CSS file structure"""
    print("\n" + "=" * 60)
    print("Testing Animations CSS Structure")
    print("=" * 60)

    try:
        css_file = "/home/user/autotrade/dashboard/static/css/animations.css"

        print("\n[Test 1] File Existence")
        if not os.path.exists(css_file):
            print(f"❌ File not found: {css_file}")
            return False
        print(f"✓ File exists: {css_file}")

        print("\n[Test 2] CSS Content Structure")
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()

        required_animations = [
            '.loading-spinner',
            '.skeleton',
            '.progress-bar',
            '.fade-in',
            '.slide-in-left',
            '.scale-in',
            '.pulse',
            '.bounce',
            '.shimmer',
            '.loading-dots',
            '@keyframes spinner-rotate',
            '@keyframes skeleton-loading',
            '@keyframes fadeIn',
            '@media (prefers-reduced-motion: reduce)'
        ]

        for animation in required_animations:
            if animation in content:
                print(f"✓ Found: {animation}")
            else:
                print(f"❌ Missing: {animation}")
                return False

        print(f"\n✓ Total file size: {len(content):,} characters")
        print(f"✓ Total lines: {content.count(chr(10)) + 1}")

        print("\n✅ Animations CSS structure tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Animations CSS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all v5.11 tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUITE - v5.11")
    print("Dashboard UX + Performance Monitoring + Advanced Backtesting")
    print("=" * 60)

    results = []

    results.append(("Performance Monitor", test_performance_monitor()))

    results.append(("Advanced Backtester", test_advanced_backtester()))

    results.append(("Loading Utils JavaScript", test_loading_utils_structure()))

    results.append(("Animations CSS", test_animations_css_structure()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY - v5.11")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - v5.11 READY FOR DEPLOYMENT")
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
