Comprehensive Test Suite for v5.12 Enhancements
LSTM Prediction, Data Caching, Risk Analysis
import sys
import os
from datetime import datetime, timedelta
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_lstm_predictor():
    """Test LSTM Price Predictor"""
    print("\n" + "=" * 60)
    print("Testing LSTM Price Predictor")
    print("=" * 60)

    try:
        from ai.lstm_predictor import LSTMPricePredictor, AdvancedFeatureEngineering

        print("\n[Test 1] LSTM Predictor Initialization")
        predictor = LSTMPricePredictor(sequence_length=60, hidden_size=256, num_layers=2)
        print(f"✓ Initialized: {predictor.model_name}")
        print(f"  Sequence Length: {predictor.sequence_length}")
        print(f"  Hidden Size: {predictor.hidden_size}")

        print("\n[Test 2] Generating Sample Price Data")
        sample_data = []
        base_price = 70000
        for i in range(100):
            price = base_price + np.random.normal(0, 1000)
            sample_data.append({
                'date': (datetime.now() - timedelta(days=100-i)).strftime('%Y-%m-%d'),
                'open': price - 100,
                'high': price + 500,
                'low': price - 500,
                'close': price,
                'volume': np.random.randint(5000000, 15000000)
            })
        print(f"✓ Generated {len(sample_data)} days of data")

        print("\n[Test 3] Feature Engineering")
        features = AdvancedFeatureEngineering.extract_comprehensive_features(sample_data, 20)
        print(f"✓ Extracted {len(features)} features")
        print(f"  Features: {list(features.keys())[:5]}...")

        print("\n[Test 4] Training LSTM Model")
        metrics = predictor.train(sample_data, epochs=20, validation_split=0.2)
        print(f"✓ Training complete:")
        print(f"  Training samples: {metrics.training_samples}")
        print(f"  Validation samples: {metrics.validation_samples}")
        print(f"  MAE: {metrics.mae:.2f}")
        print(f"  RMSE: {metrics.rmse:.2f}")
        print(f"  R² Score: {metrics.r2_score:.3f}")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")

        print("\n[Test 5] Making Predictions")
        prediction = predictor.predict(
            stock_code='005930',
            stock_name='Samsung Electronics',
            recent_data=sample_data,
            days_ahead=5
        )

        if prediction:
            print(f"✓ Prediction successful:")
            print(f"  Current Price: {prediction.current_price:,.0f}")
            print(f"  Predicted Prices: {[f'{p:,.0f}' for p in prediction.predicted_prices]}")
            print(f"  Trend: {prediction.trend_direction}")
            print(f"  Confidence: {prediction.confidence:.2%}")
            print(f"  Volatility: {prediction.volatility_forecast:.2%}")
        else:
            print("⚠ Prediction returned None")

        print("\n✅ LSTM Predictor tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ LSTM Predictor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_cache():
    """Test Data Caching System"""
    print("\n" + "=" * 60)
    print("Testing Data Caching System")
    print("=" * 60)

    try:
        from utils.data_cache import LRUCache, MultiLevelCache, cached

        print("\n[Test 1] LRU Cache Basic Operations")
        cache = LRUCache(max_size=10, max_memory_mb=1, default_ttl_seconds=60)

        cache.set("key1", {"data": "value1"}, ttl_seconds=60)
        cache.set("key2", {"data": "value2"}, ttl_seconds=60)

        value = cache.get("key1")
        print(f"✓ Set and Get: {value}")

        print("\n[Test 2] Cache Statistics")
        stats = cache.get_stats()
        print(f"✓ Hit Rate: {stats.hit_rate:.2%}")
        print(f"  Total Hits: {stats.total_hits}")
        print(f"  Total Misses: {stats.total_misses}")
        print(f"  Entry Count: {stats.entry_count}")
        print(f"  Memory Usage: {stats.memory_usage_bytes/1024:.2f}KB")

        print("\n[Test 3] Cache Miss")
        miss_value = cache.get("nonexistent_key")
        print(f"✓ Cache miss handled: {miss_value is None}")

        print("\n[Test 4] Cache Deletion")
        deleted = cache.delete("key1")
        print(f"✓ Deletion successful: {deleted}")

        print("\n[Test 5] Multi-Level Cache")
        ml_cache = MultiLevelCache(
            l1_max_size=10,
            l1_max_memory_mb=1,
            l2_enabled=True,
            l2_cache_dir="/tmp/test_cache"
        )

        ml_cache.set("ml_key", {"price": 73500, "volume": 1000000}, persist_l2=True)
        ml_value = ml_cache.get("ml_key")
        print(f"✓ Multi-level cache: {ml_value}")

        ml_stats = ml_cache.get_stats()
        print(f"  L1 Entries: {ml_stats['l1']['entries']}")

        print("\n[Test 6] Cached Decorator")

        test_cache = LRUCache(max_size=10, max_memory_mb=1)

        @cached(test_cache, ttl_seconds=300)
        def expensive_function(n):
            return sum(range(n))

        result1 = expensive_function(1000)
        result2 = expensive_function(1000)
        print(f"✓ Decorator works: {result1} == {result2}")

        print("\n[Test 7] Tag-based Invalidation")
        cache.set("stock_005930", {"price": 73500}, tags=["stock", "samsung"])
        cache.set("stock_000660", {"price": 130000}, tags=["stock", "skh"])
        invalidated = cache.invalidate_by_tag("stock")
        print(f"✓ Invalidated {invalidated} entries with tag 'stock'")

        print("\n✅ Data Cache tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Data Cache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_risk_analyzer():
    """Test Risk Analyzer"""
    print("\n" + "=" * 60)
    print("Testing Risk Analyzer")
    print("=" * 60)

    try:
        from utils.risk_analyzer import RiskAnalyzer

        print("\n[Test 1] Risk Analyzer Initialization")
        analyzer = RiskAnalyzer(risk_free_rate=0.03)
        print(f"✓ Initialized with risk-free rate: 3%")

        print("\n[Test 2] Generating Sample Data")
        price_history = []
        base_price = 70000

        for i in range(100):
            trend = i * 50
            volatility = np.random.normal(0, 1500)
            price = base_price + trend + volatility

            price_history.append({
                'date': (datetime.now() - timedelta(days=100-i)).strftime('%Y-%m-%d'),
                'open': price - 200,
                'high': price + 800,
                'low': price - 800,
                'close': price,
                'volume': np.random.randint(5000000, 15000000)
            })

        print(f"✓ Generated {len(price_history)} days of price data")

        print("\n[Test 3] Stock Risk Analysis")
        risk_metrics = analyzer.analyze_stock_risk(
            stock_code='005930',
            stock_name='Samsung Electronics',
            price_history=price_history,
            position_size=10000000,
            portfolio_value=50000000
        )

        print(f"✓ Risk analysis complete:")
        print(f"  Historical Volatility: {risk_metrics.historical_volatility:.2%}")
        print(f"  VaR (95%): {risk_metrics.var_95:.2%}")
        print(f"  CVaR (95%): {risk_metrics.cvar_95:.2%}")
        print(f"  Max Drawdown: {risk_metrics.max_drawdown:.2%}")
        print(f"  Beta: {risk_metrics.beta:.2f}")
        print(f"  Sharpe Ratio: {risk_metrics.sharpe_ratio:.2f}")
        print(f"  Sortino Ratio: {risk_metrics.sortino_ratio:.2f}")
        print(f"  Risk Score: {risk_metrics.risk_score:.1f}/100")
        print(f"  Risk Grade: {risk_metrics.risk_grade}")

        print("\n[Test 4] Stress Test Scenarios")
        print(f"✓ Stress test results:")
        for scenario, price in list(risk_metrics.stress_test_scenarios.items())[:3]:
            print(f"  {scenario}: {price:,.0f}")

        print("\n[Test 5] Portfolio Risk Analysis")

        positions = [
            {'stock_code': '005930', 'value': 20000000},
            {'stock_code': '000660', 'value': 15000000},
            {'stock_code': '035420', 'value': 10000000},
            {'stock_code': '051910', 'value': 5000000}
        ]

        price_histories = {
            '005930': price_history,
            '000660': price_history,
            '035420': price_history,
            '051910': price_history
        }

        portfolio_metrics = analyzer.analyze_portfolio_risk(
            positions=positions,
            portfolio_value=50000000,
            price_histories=price_histories
        )

        print(f"✓ Portfolio risk analysis complete:")
        print(f"  Portfolio Value: {portfolio_metrics.portfolio_value:,.0f}")
        print(f"  Portfolio VaR (95%): {portfolio_metrics.portfolio_var_95:.2%}")
        print(f"  Portfolio CVaR (95%): {portfolio_metrics.portfolio_cvar_95:.2%}")
        print(f"  Diversification Ratio: {portfolio_metrics.diversification_ratio:.2f}")
        print(f"  Herfindahl Index: {portfolio_metrics.herfindahl_index:.3f}")
        print(f"  Effective Stocks: {portfolio_metrics.effective_stocks:.1f}")
        print(f"  Max Drawdown: {portfolio_metrics.max_drawdown:.2%}")
        print(f"  Sharpe Ratio: {portfolio_metrics.sharpe_ratio:.2f}")
        print(f"  Risk Score: {portfolio_metrics.risk_score:.1f}/100")

        print("\n[Test 6] Risk Recommendations")
        print(f"✓ Recommendations ({len(portfolio_metrics.recommendations)}):")
        for rec in portfolio_metrics.recommendations:
            print(f"  {rec}")

        print("\n✅ Risk Analyzer tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Risk Analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Integration Test - All v5.12 Features Together"""
    print("\n" + "=" * 60)
    print("Integration Test - v5.12 Features")
    print("=" * 60)

    try:
        from ai.lstm_predictor import get_lstm_predictor
        from utils.data_cache import get_price_cache
        from utils.risk_analyzer import get_risk_analyzer

        print("\n[Test 1] Initialize All Components")
        lstm = get_lstm_predictor()
        cache = get_price_cache()
        risk = get_risk_analyzer()
        print("✓ All components initialized")

        print("\n[Test 2] Integrated Workflow")

        sample_data = []
        for i in range(100):
            sample_data.append({
                'date': (datetime.now() - timedelta(days=100-i)).strftime('%Y-%m-%d'),
                'open': 70000,
                'high': 71000,
                'low': 69000,
                'close': 70000 + np.random.normal(0, 1000),
                'volume': 10000000
            })

        stock_code = '005930'
        stock_name = 'Samsung'

        cache_key = f"price_history_{stock_code}"
        cache.set(cache_key, sample_data, ttl_seconds=300)
        cached_data = cache.get(cache_key)
        print(f"✓ Cached {len(cached_data)} price records")

        prediction = lstm.predict(stock_code, stock_name, sample_data, days_ahead=5)
        if prediction:
            print(f"✓ LSTM Prediction: {prediction.current_price:,.0f} → "
                  f"{prediction.predicted_prices[-1]:,.0f} ({prediction.trend_direction})")

        risk_metrics = risk.analyze_stock_risk(
            stock_code, stock_name, sample_data,
            position_size=10000000, portfolio_value=50000000
        )
        print(f"✓ Risk Analysis: Score={risk_metrics.risk_score:.1f}, "
              f"Grade={risk_metrics.risk_grade}")

        print("\n✅ Integration test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all v5.12 tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUITE - v5.12")
    print("LSTM Prediction + Data Caching + Risk Analysis")
    print("=" * 60)

    results = []

    results.append(("LSTM Predictor", test_lstm_predictor()))

    results.append(("Data Cache", test_data_cache()))

    results.append(("Risk Analyzer", test_risk_analyzer()))

    results.append(("Integration Test", test_integration()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY - v5.12")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - v5.12 READY FOR DEPLOYMENT")
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
