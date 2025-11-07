"""
Comprehensive Test Suite for v5.13 Enhancements
WebSocket Streaming, Portfolio Optimization, Smart Execution
"""
import sys
import os
from datetime import datetime, timedelta
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_websocket_streaming():
    """Test WebSocket Streaming System"""
    print("\n" + "=" * 60)
    print("Testing WebSocket Streaming System")
    print("=" * 60)

    try:
        from utils.websocket_streaming import (
            WebSocketStreamManager, StreamingDataAggregator,
            MessagePriority, ConnectionState
        )

        print("\n[Test 1] WebSocket Manager Initialization")
        manager = WebSocketStreamManager(
            max_connections=100,
            max_message_queue=500,
            message_ttl_seconds=30
        )
        print(f"✓ Initialized: max_connections={manager.max_connections}")

        print("\n[Test 2] Register Connections")
        client_ids = ['client_001', 'client_002', 'client_003']
        for client_id in client_ids:
            success = manager.register_connection(client_id)
            print(f"✓ Registered {client_id}: {success}")

        print("\n[Test 3] Subscribe to Channels")
        for client_id in client_ids:
            manager.subscribe(client_id, 'prices', replay_history=False)
            manager.subscribe(client_id, 'alerts', replay_history=False)
        print(f"✓ All clients subscribed to channels")

        print("\n[Test 4] Broadcast Messages")
        sent = manager.broadcast(
            'prices',
            {'stock': '005930', 'price': 73500, 'volume': 1000000},
            priority=MessagePriority.HIGH
        )
        print(f"✓ Broadcasted to {sent} clients")

        print("\n[Test 5] Get Pending Messages")
        messages = manager.get_pending_messages('client_001', max_messages=10)
        print(f"✓ Retrieved {len(messages)} pending messages")
        if messages:
            print(f"  First message: channel={messages[0].channel}, "
                  f"priority={messages[0].priority.name}")

        print("\n[Test 6] Channel Statistics")
        channel_stats = manager.get_channel_stats()
        print(f"✓ Channel stats retrieved: {len(channel_stats)} channels")
        for channel, stats in channel_stats.items():
            print(f"  {channel}: {stats['subscriber_count']} subscribers")

        print("\n[Test 7] Global Statistics")
        global_stats = manager.get_global_stats()
        print(f"✓ Global stats:")
        print(f"  Messages sent: {global_stats.messages_sent}")
        print(f"  Active connections: {global_stats.active_connections}")
        print(f"  Avg latency: {global_stats.avg_latency_ms:.2f}ms")

        print("\n[Test 8] Rate Limiting")
        within_limit = manager.check_rate_limit('client_001')
        print(f"✓ Rate limit check: {within_limit}")

        print("\n[Test 9] Data Aggregator")
        aggregator = StreamingDataAggregator(aggregation_window_ms=100)
        aggregator.add_data('prices', {'price': 73500})
        aggregator.add_data('prices', {'price': 73600})
        aggregated = aggregator.get_aggregated_data('prices')
        print(f"✓ Aggregated {len(aggregated)} data points" if aggregated else "✓ No data")

        print("\n[Test 10] Connection Cleanup")
        manager.unregister_connection('client_003')
        remaining = len(manager.connections)
        print(f"✓ Connection removed, remaining: {remaining}")

        print("\n[OK] WebSocket Streaming tests passed!")
        return True

    except Exception as e:
        print(f"\n[X] WebSocket Streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_portfolio_optimizer():
    """Test Portfolio Optimizer"""
    print("\n" + "=" * 60)
    print("Testing Portfolio Optimizer")
    print("=" * 60)

    try:
        from strategy.portfolio_optimizer import (
            PortfolioOptimizer, OptimizationObjective
        )

        print("\n[Test 1] Portfolio Optimizer Initialization")
        optimizer = PortfolioOptimizer(risk_free_rate=0."03")
        print(f"✓ Initialized with risk-free rate: 3%")

        print("\n[Test 2] Generating Sample Price Histories")
        price_histories = {}
        stock_codes = ['005930', '000660', '035420', '051910']

        for stock in stock_codes:
            history = []
            base_price = np.random.uniform(50000, 150000)

            for i in range(100):
                price = base_price * (1 + np.random.normal(0, 0."02"))
                history.append({
                    'date': (datetime.now() - timedelta(days=100-i)).strftime('%Y-%m-%d'),
                    'close': price,
                    'volume': np.random.randint(1000000, 10000000)
                })

            price_histories[stock] = history

        print(f"✓ Generated price histories for {len(price_histories)} stocks")

        print("\n[Test 3] Optimize: Maximum Sharpe Ratio")
        result = optimizer.optimize(
            price_histories,
            objective=OptimizationObjective.MAX_SHARPE,
            constraints={'max_weight': 0.4, 'min_weight': 0.1}
        )
        print(f"✓ Optimization complete:")
        print(f"  Expected Return: {result.expected_return:.2%}")
        print(f"  Expected Volatility: {result.expected_volatility:.2%}")
        print(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
        print(f"  Weights: {list(result.weights.values())[:3]}...")
        print(f"  Constraints Satisfied: {result.constraints_satisfied}")

        print("\n[Test 4] Optimize: Minimum Volatility")
        result_min_vol = optimizer.optimize(
            price_histories,
            objective=OptimizationObjective.MIN_VOLATILITY
        )
        print(f"✓ Min volatility portfolio:")
        print(f"  Expected Volatility: {result_min_vol.expected_volatility:.2%}")
        print(f"  Expected Return: {result_min_vol.expected_return:.2%}")

        print("\n[Test 5] Optimize: Risk Parity")
        result_rp = optimizer.optimize(
            price_histories,
            objective=OptimizationObjective.RISK_PARITY
        )
        print(f"✓ Risk parity portfolio:")
        print(f"  Weights: {list(result_rp.weights.values())}")
        print(f"  Expected Return: {result_rp.expected_return:.2%}")

        print("\n[Test 6] Calculate Efficient Frontier")
        frontier = optimizer.calculate_efficient_frontier(
            price_histories,
            num_points=10,
            constraints={'max_weight': 0.5}
        )
        print(f"✓ Efficient frontier calculated: {len(frontier)} points")
        if frontier:
            print(f"  Min volatility point: return={frontier[0].expected_return:.2%}, "
                  f"vol={frontier[0].volatility:.2%}")
            print(f"  Max return point: return={frontier[-1].expected_return:.2%}, "
                  f"vol={frontier[-1].volatility:.2%}")

        print("\n[Test 7] Rebalancing Recommendations")
        current_weights = {'005930': 0.3, '000660': 0.3, '035420': 0.2, '051910': 0.2}
        recommendations = optimizer.rebalance_recommendation(
            current_weights,
            result.weights,
            portfolio_value=50000000,
            rebalance_threshold=0."05"
        )
        print(f"✓ Rebalancing recommendations: {len(recommendations)} actions")
        for stock, rec in list(recommendations.items())[:2]:
            print(f"  {stock}: {rec['action']} {rec['amount']:,.0f}원 "
                  f"(diff={rec['weight_diff']:+.2%})")

        print("\n[OK] Portfolio Optimizer tests passed!")
        return True

    except Exception as e:
        print(f"\n[X] Portfolio Optimizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_smart_execution():
    """Test Smart Order Execution"""
    print("\n" + "=" * 60)
    print("Testing Smart Order Execution")
    print("=" * 60)

    try:
        from strategy.smart_execution import (
            SmartOrderExecutor, ExecutionAlgorithm, MarketData
        )

        print("\n[Test 1] Smart Executor Initialization")
        executor = SmartOrderExecutor()
        print(f"✓ Initialized")

        print("\n[Test 2] Generating Market Data")
        market_data = []
        for i in range(20):
            md = MarketData(
                stock_code='005930',
                timestamp=datetime.now() - timedelta(minutes=20-i),
                price=73000 + np.random.normal(0, 500),
                volume=np.random.randint(50000, 150000),
                bid_price=72900,
                ask_price=73100,
                bid_volume=10000,
                ask_volume=10000
            )
            market_data.append(md)
        print(f"✓ Generated {len(market_data)} market data points")

        print("\n[Test 3] Execute Order: TWAP")
        result_twap = executor.execute_order(
            order_id='ORD001',
            stock_code='005930',
            stock_name='Samsung Electronics',
            quantity=10000,
            side='buy',
            algorithm=ExecutionAlgorithm.TWAP,
            duration_minutes=30,
            current_price=73000
        )
        print(f"✓ TWAP execution:")
        print(f"  Executed: {result_twap.executed_quantity}/{result_twap.total_quantity}")
        print(f"  Avg Price: {result_twap.average_price:,.0f}")
        print(f"  Slippage: {result_twap.slippage_bps:.2f}bps")
        print(f"  Slices: {result_twap.slices_executed}/{result_twap.slices_total}")

        print("\n[Test 4] Execute Order: VWAP")
        result_vwap = executor.execute_order(
            order_id='ORD002',
            stock_code='005930',
            stock_name='Samsung Electronics',
            quantity=15000,
            side='buy',
            algorithm=ExecutionAlgorithm.VWAP,
            duration_minutes=30,
            current_price=73000,
            market_data=market_data
        )
        print(f"✓ VWAP execution:")
        print(f"  Executed: {result_vwap.executed_quantity}/{result_vwap.total_quantity}")
        print(f"  Avg Price: {result_vwap.average_price:,.0f}")
        print(f"  Slippage: {result_vwap.slippage_bps:.2f}bps")

        print("\n[Test 5] Execute Order: Iceberg")
        result_iceberg = executor.execute_order(
            order_id='ORD003',
            stock_code='005930',
            stock_name='Samsung Electronics',
            quantity=20000,
            side='buy',
            algorithm=ExecutionAlgorithm.ICEBERG,
            duration_minutes=15,
            current_price=73000,
            params={'visible_quantity': 2000}
        )
        print(f"✓ Iceberg execution:")
        print(f"  Slices: {result_iceberg.slices_executed}")
        print(f"  Avg Price: {result_iceberg.average_price:,.0f}")

        print("\n[Test 6] Execute Order: POV")
        result_pov = executor.execute_order(
            order_id='ORD004',
            stock_code='005930',
            stock_name='Samsung Electronics',
            quantity=12000,
            side='sell',
            algorithm=ExecutionAlgorithm.POV,
            duration_minutes=30,
            current_price=73000,
            params={'participation_rate': 0.15}
        )
        print(f"✓ POV execution:")
        print(f"  Executed: {result_pov.executed_quantity}")
        print(f"  Slippage: {result_pov.slippage_bps:.2f}bps")

        print("\n[Test 7] Execute Order: Implementation Shortfall")
        result_is = executor.execute_order(
            order_id='ORD005',
            stock_code='005930',
            stock_name='Samsung Electronics',
            quantity=8000,
            side='buy',
            algorithm=ExecutionAlgorithm.IMPLEMENTATION_SHORTFALL,
            duration_minutes=20,
            current_price=73000,
            params={'urgency': 0.8}
        )
        print(f"✓ IS execution:")
        print(f"  Executed: {result_is.executed_quantity}")
        print(f"  Slices: {result_is.slices_executed}")

        print("\n[Test 8] Execute Order: Adaptive")
        result_adaptive = executor.execute_order(
            order_id='ORD006',
            stock_code='005930',
            stock_name='Samsung Electronics',
            quantity=10000,
            side='buy',
            algorithm=ExecutionAlgorithm.ADAPTIVE,
            duration_minutes=30,
            current_price=73000,
            market_data=market_data
        )
        print(f"✓ Adaptive execution:")
        print(f"  Executed: {result_adaptive.executed_quantity}")
        print(f"  Algorithm chosen: {result_adaptive.metadata}")

        print("\n[Test 9] Execution Statistics")
        stats = executor.get_execution_stats()
        print(f"✓ Execution stats:")
        print(f"  Total orders: {stats['total_orders']}")
        print(f"  Successful: {stats['successful_orders']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Avg slippage: {stats['avg_slippage_bps']:.2f}bps")
        print(f"  Total volume: {stats['total_volume']:,} shares")

        print("\n[OK] Smart Execution tests passed!")
        return True

    except Exception as e:
        print(f"\n[X] Smart Execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Integration Test - All v5.13 Features Together"""
    print("\n" + "=" * 60)
    print("Integration Test - v5.13 Features")
    print("=" * 60)

    try:
        from utils.websocket_streaming import get_stream_manager
        from strategy.portfolio_optimizer import get_portfolio_optimizer
        from strategy.smart_execution import get_smart_executor

        print("\n[Test 1] Initialize All Components")
        stream_mgr = get_stream_manager()
        optimizer = get_portfolio_optimizer()
        executor = get_smart_executor()
        print("✓ All components initialized")

        print("\n[Test 2] Integrated Workflow")

        stream_mgr.register_connection('trading_client')
        stream_mgr.subscribe('trading_client', 'portfolio_updates')

        price_histories = {}
        for stock in ['005930', '000660', '035420']:
            history = []
            for i in range(60):
                history.append({
                    'date': (datetime.now() - timedelta(days=60-i)).strftime('%Y-%m-%d'),
                    'close': 70000 + np.random.normal(0, 3000),
                    'volume': np.random.randint(5000000, 15000000)
                })
            price_histories[stock] = history

        result = optimizer.optimize(
            price_histories,
            objective=optimizer.OptimizationObjective.MAX_SHARPE
        )
        print(f"✓ Portfolio optimized: Sharpe={result.sharpe_ratio:.2f}")

        stream_mgr.broadcast(
            'portfolio_updates',
            {
                'weights': result.weights,
                'expected_return': result.expected_return,
                'sharpe_ratio': result.sharpe_ratio
            }
        )
        print("✓ Portfolio update broadcasted")

        for stock, weight in list(result.weights.items())[:2]:
            quantity = int(weight * 100000)
            exec_result = executor.execute_order(
                order_id=f'REBAL_{stock}',
                stock_code=stock,
                stock_name=f'Stock {stock}',
                quantity=quantity,
                side='buy',
                algorithm=executor.ExecutionAlgorithm.TWAP,
                duration_minutes=30,
                current_price=70000
            )
            print(f"✓ Executed order for {stock}: {exec_result.executed_quantity} shares")

        print("\n[OK] Integration test passed!")
        return True

    except Exception as e:
        print(f"\n[X] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all v5.13 tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUITE - v5.13")
    print("WebSocket Streaming + Portfolio Optimization + Smart Execution")
    print("=" * 60)

    results = []

    results.append(("WebSocket Streaming", test_websocket_streaming()))

    results.append(("Portfolio Optimizer", test_portfolio_optimizer()))

    results.append(("Smart Execution", test_smart_execution()))

    results.append(("Integration Test", test_integration()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY - v5.13")
    print("=" * 60)

    for name, result in results:
        status = "[OK] PASS" if result else "[X] FAIL"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - v5.13 READY FOR DEPLOYMENT")
    else:
        print("[WARNING]️ SOME TESTS FAILED - REVIEW REQUIRED")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARNING]️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Test execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
