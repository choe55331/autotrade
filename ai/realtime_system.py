"""
Real-time Data Processing System
WebSocket-based streaming and event-driven trading
"""

"""
Author: AutoTrade Pro
Version: 4.2
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import asyncio
import json
from collections import deque
import threading
import queue

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("WARNING: websockets not available. Install with: pip install websockets")


@dataclass
class StreamingTick:
    """Real-time market tick"""
    stock_code: str
    timestamp: str
    price: float
    volume: int
    bid: float
    ask: float
    bid_size: int
    ask_size: int
    spread: float

    def __post_init__(self):
        """
        self.spread = self.ask - self.bid


@dataclass
class StreamingCandle:
    """Real-time candle aggregation"""
    stock_code: str
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: str
    is_closed: bool = False


@dataclass
class StreamingEvent:
    """Trading event"""
    event_type: str
    timestamp: str
    data: Dict[str, Any]
    priority: int = 0



class RealTimeDataStream:
    """
    Real-time data streaming system

    Features:
    - WebSocket connection
    - Tick aggregation to candles
    - Event queue management
    - Multi-symbol support
    - Reconnection handling
    """

    def __init__(self, buffer_size: int = 10000):
        """
        self.buffer_size = buffer_size
        self.tick_buffer: Dict[str, deque] = {}
        self.candle_buffer: Dict[str, deque] = {}
        self.event_queue = queue.PriorityQueue()

        self.subscribers: Dict[str, List[Callable]] = {
            'tick': [],
            'candle': [],
            'signal': [],
            'order': [],
            'fill': []
        }

        self.is_running = False
        self.websocket = None

        self.metrics = {
            'ticks_received': 0,
            'candles_generated': 0,
            'events_processed': 0,
            'latency_ms': 0.0,
            'throughput_tps': 0.0
        }

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to event type"""
        if event_type in self.subscribers:
            self.subscribers[event_type].append(callback)

    async def connect(self, ws_url: str):
        """Connect to WebSocket"""
        if not WEBSOCKETS_AVAILABLE:
            print("WebSocket not available, using mock stream")
            return

        try:
            self.websocket = await websockets.connect(ws_url)
            self.is_running = True
            print(f"[OK] Connected to {ws_url}")
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            self.is_running = False

    async def stream_data(self, stock_codes: List[str]):
        """
        Start streaming data

        Args:
            stock_codes: List of stock codes to stream
        """
        if not WEBSOCKETS_AVAILABLE:
            await self._mock_stream(stock_codes)
            return

        try:
            subscribe_msg = {
                'action': 'subscribe',
                'symbols': stock_codes
            }
            await self.websocket.send(json.dumps(subscribe_msg))

            while self.is_running:
                message = await self.websocket.recv()
                tick = self._parse_tick(message)

                if tick:
                    await self._process_tick(tick)

        except Exception as e:
            print(f"Streaming error: {e}")
            await self._reconnect(stock_codes)

    async def _mock_stream(self, stock_codes: List[str]):
        """Mock streaming for testing"""
        import random

        base_prices = {code: 73000 + random.randint(-5000, 5000) for code in stock_codes}

        while self.is_running:
            for code in stock_codes:
                price_change = random.uniform(-0.005, 0.005)
                price = base_prices[code] * (1 + price_change)
                base_prices[code] = price

                tick = StreamingTick(
                    stock_code=code,
                    timestamp=datetime.now().isoformat(),
                    price=price,
                    volume=random.randint(1, 100),
                    bid=price * 0.999,
                    ask=price * 1.001,
                    bid_size=random.randint(10, 1000),
                    ask_size=random.randint(10, 1000),
                    spread=0
                )

                await self._process_tick(tick)

            await asyncio.sleep(0.1)

    def _parse_tick(self, message: str) -> Optional[StreamingTick]:
        """Parse tick from message"""
        try:
            data = json.loads(message)
            return StreamingTick(**data)
        except Exception as e:
            print(f"Parse error: {e}")
            return None

    async def _process_tick(self, tick: StreamingTick):
        """Process incoming tick"""
        self.metrics['ticks_received'] += 1

        if tick.stock_code not in self.tick_buffer:
            self.tick_buffer[tick.stock_code] = deque(maxlen=self.buffer_size)
        self.tick_buffer[tick.stock_code].append(tick)

        event = StreamingEvent(
            event_type='tick',
            timestamp=tick.timestamp,
            data={'tick': tick}
        )
        self._publish_event(event)

        await self._aggregate_candle(tick)

    async def _aggregate_candle(self, tick: StreamingTick):
        """Aggregate ticks to candles"""
        intervals = ['1m', '5m', '1h']

        for interval in intervals:
            candle_key = f"{tick.stock_code}_{interval}"

            if candle_key not in self.candle_buffer:
                self.candle_buffer[candle_key] = deque(maxlen=1000)

            candles = self.candle_buffer[candle_key]

            if not candles or self._should_new_candle(candles[-1], tick.timestamp, interval):
                """
                candle = StreamingCandle(
                    stock_code=tick.stock_code,
                    interval=interval,
                    open=tick.price,
                    high=tick.price,
                    low=tick.price,
                    close=tick.price,
                    volume=tick.volume,
                    timestamp=tick.timestamp
                )
                candles.append(candle)

                if len(candles) > 1:
                    candles[-2].is_closed = True
                    self._publish_candle(candles[-2])
            else:
                candle = candles[-1]
                candle.high = max(candle.high, tick.price)
                candle.low = min(candle.low, tick.price)
                candle.close = tick.price
                candle.volume += tick.volume

    def _should_new_candle(self, candle: StreamingCandle, new_timestamp: str, interval: str) -> bool:
        """Check if should create new candle"""
        from datetime import datetime, timedelta

        candle_time = datetime.fromisoformat(candle.timestamp)
        new_time = datetime.fromisoformat(new_timestamp)

        interval_map = {
            '1m': timedelta(minutes=1),
            '5m': timedelta(minutes=5),
            '1h': timedelta(hours=1)
        }

        delta = interval_map.get(interval, timedelta(minutes=1))
        return new_time - candle_time >= delta

    def _publish_event(self, event: StreamingEvent):
        """Publish event to subscribers"""
        for callback in self.subscribers.get(event.event_type, []):
            """
            try:
                callback(event)
            except Exception as e:
                print(f"Callback error: {e}")

    def _publish_candle(self, candle: StreamingCandle):
        """Publish closed candle"""
        self.metrics['candles_generated'] += 1

        event = StreamingEvent(
            event_type='candle',
            timestamp=candle.timestamp,
            data={'candle': candle}
        )
        self._publish_event(event)

    async def _reconnect(self, stock_codes: List[str]):
        """Reconnect on failure"""
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries and self.is_running:
            try:
                await asyncio.sleep(2 ** retry_count)
                await self.connect(self.websocket.remote_address)
                await self.stream_data(stock_codes)
                return
            except Exception as e:
                retry_count += 1
                print(f"Reconnect attempt {retry_count}/{max_retries} failed: {e}")

        print("Max reconnection attempts reached")
        self.is_running = False

    def get_latest_tick(self, stock_code: str) -> Optional[StreamingTick]:
        """Get latest tick for stock"""
        if stock_code in self.tick_buffer and self.tick_buffer[stock_code]:
            return self.tick_buffer[stock_code][-1]
        return None

    def get_latest_candle(self, stock_code: str, interval: str = '1m') -> Optional[StreamingCandle]:
        """Get latest candle for stock"""
        key = f"{stock_code}_{interval}"
        if key in self.candle_buffer and self.candle_buffer[key]:
            return self.candle_buffer[key][-1]
        return None

    def get_candles(self, stock_code: str, interval: str = '1m', count: int = 100) -> List[StreamingCandle]:
        """Get recent candles"""
        key = f"{stock_code}_{interval}"
        if key in self.candle_buffer:
            return list(self.candle_buffer[key])[-count:]
        return []

    def stop(self):
        """Stop streaming"""
        self.is_running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())



class EventDrivenTradingEngine:
    """
    Event-driven trading engine

    Features:
    - Real-time signal generation
    - Order management
    - Position tracking
    - P&L calculation
    """

    def __init__(self, data_stream: RealTimeDataStream):
        """
        self.data_stream = data_stream
        self.positions: Dict[str, Dict] = {}
        self.pending_orders: List[Dict] = []
        self.filled_orders: List[Dict] = []

        self.pnl = 0.0
        self.unrealized_pnl = 0.0

        self.data_stream.subscribe('tick', self.on_tick)
        self.data_stream.subscribe('candle', self.on_candle)
        self.data_stream.subscribe('signal', self.on_signal)

    def on_tick(self, event: StreamingEvent):
        """Handle tick event"""
        tick = event.data['tick']

        if tick.stock_code in self.positions:
            pos = self.positions[tick.stock_code]
            pos['current_price'] = tick.price
            pos['unrealized_pnl'] = (tick.price - pos['avg_price']) * pos['quantity']

        self._check_exit_conditions(tick)

    def on_candle(self, event: StreamingEvent):
        """Handle candle event"""
        candle = event.data['candle']

        signal = self._generate_signal(candle)

        if signal:
            signal_event = StreamingEvent(
                event_type='signal',
                timestamp=datetime.now().isoformat(),
                data={'signal': signal}
            )
            self.data_stream._publish_event(signal_event)

    def on_signal(self, event: StreamingEvent):
        """Handle signal event"""
        signal = event.data['signal']

        if signal['action'] == 'buy':
            self.place_order('buy', signal['stock_code'], signal['quantity'])
        elif signal['action'] == 'sell':
            self.place_order('sell', signal['stock_code'], signal['quantity'])

    def _generate_signal(self, candle: StreamingCandle) -> Optional[Dict]:
        """Generate trading signal from candle"""
        candles = self.data_stream.get_candles(candle.stock_code, candle.interval, count=20)

        if len(candles) < 20:
            return None

        prices = [c.close for c in candles]
        ma_short = sum(prices[-5:]) / 5
        ma_long = sum(prices[-20:]) / 20

        if ma_short > ma_long * 1.01:
            return {
                'action': 'buy',
                'stock_code': candle.stock_code,
                'quantity': 10,
                'reason': 'MA crossover bullish'
            }
        elif ma_short < ma_long * 0.99:
            if candle.stock_code in self.positions:
                return {
                    'action': 'sell',
                    'stock_code': candle.stock_code,
                    'quantity': self.positions[candle.stock_code]['quantity'],
                    'reason': 'MA crossover bearish'
                }

        return None

    def place_order(self, action: str, stock_code: str, quantity: int):
        """Place order"""
        tick = self.data_stream.get_latest_tick(stock_code)
        if not tick:
            return

        price = tick.ask if action == 'buy' else tick.bid

        order = {
            'order_id': len(self.pending_orders) + 1,
            'action': action,
            'stock_code': stock_code,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }

        self.pending_orders.append(order)

        self._fill_order(order)

    def _fill_order(self, order: Dict):
        """Fill order"""
        order['status'] = 'filled'
        self.filled_orders.append(order)

        if order['action'] == 'buy':
            if order['stock_code'] not in self.positions:
                self.positions[order['stock_code']] = {
                    'quantity': 0,
                    'avg_price': 0,
                    'current_price': order['price']
                }

            pos = self.positions[order['stock_code']]
            total_cost = pos['avg_price'] * pos['quantity'] + order['price'] * order['quantity']
            total_quantity = pos['quantity'] + order['quantity']
            pos['avg_price'] = total_cost / total_quantity
            pos['quantity'] = total_quantity
            pos['current_price'] = order['price']

        elif order['action'] == 'sell':
            if order['stock_code'] in self.positions:
                pos = self.positions[order['stock_code']]
                pnl = (order['price'] - pos['avg_price']) * order['quantity']
                self.pnl += pnl

                pos['quantity'] -= order['quantity']
                if pos['quantity'] <= 0:
                    del self.positions[order['stock_code']]

        self.pending_orders = [o for o in self.pending_orders if o['order_id'] != order['order_id']]

    def _check_exit_conditions(self, tick: StreamingTick):
        """Check stop loss / take profit"""
        if tick.stock_code not in self.positions:
            return

        pos = self.positions[tick.stock_code]
        pnl_pct = (tick.price - pos['avg_price']) / pos['avg_price'] * 100

        if pnl_pct < -3:
            self.place_order('sell', tick.stock_code, pos['quantity'])

        elif pnl_pct > 5:
            self.place_order('sell', tick.stock_code, pos['quantity'])

    def get_portfolio_value(self) -> float:
        """Get current portfolio value"""
        total = self.pnl
        for pos in self.positions.values():
            """
            total += pos['current_price'] * pos['quantity']
        return total

    def get_status(self) -> Dict[str, Any]:
        """Get trading engine status"""
        return {
            'positions': len(self.positions),
            'pending_orders': len(self.pending_orders),
            'filled_orders': len(self.filled_orders),
            'realized_pnl': self.pnl,
            'unrealized_pnl': sum(p['unrealized_pnl'] for p in self.positions.values()),
            'total_pnl': self.pnl + sum(p['unrealized_pnl'] for p in self.positions.values())
        }


_data_stream = None
_trading_engine = None

def get_data_stream() -> RealTimeDataStream:
    """Get data stream instance"""
    global _data_stream
    if _data_stream is None:
        _data_stream = RealTimeDataStream()
    return _data_stream

def get_trading_engine() -> EventDrivenTradingEngine:
    """Get trading engine instance"""
    global _trading_engine
    if _trading_engine is None:
        stream = get_data_stream()
        _trading_engine = EventDrivenTradingEngine(stream)
    return _trading_engine


if __name__ == '__main__':
    print("🔄 Real-time Trading System Test")

    async def test():
        """
        stream = get_data_stream()
        engine = get_trading_engine()

        stream.is_running = True
        await stream._mock_stream(['005930', '000660'])

    print("[OK] Real-time system ready")
