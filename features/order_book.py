"""
실시간 호가창 (Order Book)
5단계 매수/매도 호가 표시 및 분석
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class OrderBookLevel:
    """호가 레벨"""
    price: int  # 호가 가격
    volume: int  # 잔량
    percent: float  # 전체 잔량 대비 비율


@dataclass
class OrderBook:
    """실시간 호가창 데이터"""
    stock_code: str
    stock_name: str
    current_price: int

    # 매도 호가 (5단계)
    ask_levels: List[OrderBookLevel]  # 매도1~5호가

    # 매수 호가 (5단계)
    bid_levels: List[OrderBookLevel]  # 매수1~5호가

    # 분석 지표
    total_ask_volume: int  # 총 매도 잔량
    total_bid_volume: int  # 총 매수 잔량
    spread: int  # 호가 스프레드
    spread_percent: float  # 스프레드 비율
    bid_ask_ratio: float  # 매수/매도 비율

    timestamp: float  # 업데이트 시각

    @property
    def is_bullish(self) -> bool:
        """강세 판단: 매수 잔량 > 매도 잔량"""
        return self.bid_ask_ratio > 1.2

    @property
    def is_bearish(self) -> bool:
        """약세 판단: 매도 잔량 > 매수 잔량"""
        return self.bid_ask_ratio < 0.8

    @property
    def pressure_type(self) -> str:
        """시장 압력 유형"""
        if self.is_bullish:
            return "매수 우위"
        elif self.is_bearish:
            return "매도 우위"
        else:
            return "균형"


class OrderBookService:
    """호가창 서비스"""

    def __init__(self, market_api):
        """
        Args:
            market_api: 시장 데이터 API
        """
        self.market_api = market_api
        self._cache: Dict[str, OrderBook] = {}
        self._cache_ttl = 1  # 1초 캐시

    def get_order_book(self, stock_code: str, stock_name: str = "") -> Optional[OrderBook]:
        """
        실시간 호가창 가져오기

        Args:
            stock_code: 종목 코드
            stock_name: 종목명 (옵션)

        Returns:
            OrderBook 또는 None
        """
        # 캐시 확인
        now = time.time()
        if stock_code in self._cache:
            cached = self._cache[stock_code]
            if now - cached.timestamp < self._cache_ttl:
                return cached

        try:
            # API에서 호가 데이터 가져오기
            orderbook_data = self.market_api.get_order_book(stock_code)

            if not orderbook_data:
                return None

            # 현재가
            current_price = int(orderbook_data.get('stck_prpr', 0))

            # 매도 호가 파싱 (5단계)
            ask_levels = []
            total_ask_volume = 0

            for i in range(1, 6):
                price = int(orderbook_data.get(f'askp{i}', 0))
                volume = int(orderbook_data.get(f'askp_rsqn{i}', 0))
                total_ask_volume += volume

                ask_levels.append(OrderBookLevel(
                    price=price,
                    volume=volume,
                    percent=0  # 나중에 계산
                ))

            # 매수 호가 파싱 (5단계)
            bid_levels = []
            total_bid_volume = 0

            for i in range(1, 6):
                price = int(orderbook_data.get(f'bidp{i}', 0))
                volume = int(orderbook_data.get(f'bidp_rsqn{i}', 0))
                total_bid_volume += volume

                bid_levels.append(OrderBookLevel(
                    price=price,
                    volume=volume,
                    percent=0  # 나중에 계산
                ))

            # 비율 계산
            for level in ask_levels:
                if total_ask_volume > 0:
                    level.percent = (level.volume / total_ask_volume) * 100

            for level in bid_levels:
                if total_bid_volume > 0:
                    level.percent = (level.volume / total_bid_volume) * 100

            # 스프레드 계산
            best_ask = ask_levels[0].price if ask_levels else 0
            best_bid = bid_levels[0].price if bid_levels else 0
            spread = best_ask - best_bid
            spread_percent = (spread / best_bid * 100) if best_bid > 0 else 0

            # 매수/매도 비율
            bid_ask_ratio = (total_bid_volume / total_ask_volume) if total_ask_volume > 0 else 0

            # OrderBook 생성
            order_book = OrderBook(
                stock_code=stock_code,
                stock_name=stock_name,
                current_price=current_price,
                ask_levels=ask_levels,
                bid_levels=bid_levels,
                total_ask_volume=total_ask_volume,
                total_bid_volume=total_bid_volume,
                spread=spread,
                spread_percent=spread_percent,
                bid_ask_ratio=bid_ask_ratio,
                timestamp=now
            )

            # 캐시에 저장
            self._cache[stock_code] = order_book

            return order_book

        except Exception as e:
            print(f"호가창 가져오기 실패 ({stock_code}): {e}")
            return None

    def analyze_order_book(self, stock_code: str) -> Dict[str, Any]:
        """
        호가창 분석

        Returns:
            분석 결과 딕셔너리
        """
        order_book = self.get_order_book(stock_code)

        if not order_book:
            return {
                'success': False,
                'message': '호가 데이터를 가져올 수 없습니다'
            }

        # 분석 결과
        analysis = {
            'success': True,
            'pressure_type': order_book.pressure_type,
            'is_bullish': order_book.is_bullish,
            'is_bearish': order_book.is_bearish,
            'bid_ask_ratio': order_book.bid_ask_ratio,
            'spread': order_book.spread,
            'spread_percent': order_book.spread_percent,
            'total_bid_volume': order_book.total_bid_volume,
            'total_ask_volume': order_book.total_ask_volume,
            'recommendation': self._get_recommendation(order_book)
        }

        return analysis

    def _get_recommendation(self, order_book: OrderBook) -> str:
        """
        호가창 기반 추천

        Returns:
            추천 메시지
        """
        if order_book.is_bullish and order_book.spread_percent < 0.5:
            return "💚 강한 매수세 + 좁은 스프레드 → 매수 고려"
        elif order_book.is_bullish:
            return "🟢 매수세 우위 → 관망 또는 매수"
        elif order_book.is_bearish and order_book.spread_percent < 0.5:
            return "❤️ 강한 매도세 → 진입 주의"
        elif order_book.is_bearish:
            return "🔴 매도세 우위 → 관망"
        elif order_book.spread_percent > 1.0:
            return "⚠️ 넓은 스프레드 → 유동성 부족, 진입 주의"
        else:
            return "⚖️ 균형 상태 → 중립"

    def get_order_book_for_dashboard(self, stock_code: str, stock_name: str = "") -> Dict[str, Any]:
        """
        대시보드용 호가창 데이터

        Returns:
            JSON 직렬화 가능한 딕셔너리
        """
        order_book = self.get_order_book(stock_code, stock_name)

        if not order_book:
            return {
                'success': False,
                'message': '호가 데이터 없음'
            }

        return {
            'success': True,
            'stock_code': order_book.stock_code,
            'stock_name': order_book.stock_name,
            'current_price': order_book.current_price,
            'ask_levels': [
                {
                    'price': level.price,
                    'volume': level.volume,
                    'percent': level.percent
                }
                for level in order_book.ask_levels
            ],
            'bid_levels': [
                {
                    'price': level.price,
                    'volume': level.volume,
                    'percent': level.percent
                }
                for level in order_book.bid_levels
            ],
            'total_ask_volume': order_book.total_ask_volume,
            'total_bid_volume': order_book.total_bid_volume,
            'spread': order_book.spread,
            'spread_percent': order_book.spread_percent,
            'bid_ask_ratio': order_book.bid_ask_ratio,
            'pressure_type': order_book.pressure_type,
            'is_bullish': order_book.is_bullish,
            'is_bearish': order_book.is_bearish,
            'recommendation': self._get_recommendation(order_book)
        }
