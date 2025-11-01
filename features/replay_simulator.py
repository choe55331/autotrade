"""
AutoTrade Pro v4.0 - 과거 데이터 리플레이 시뮬레이터
실제 과거 시점의 시장 데이터를 재현하여 전략 테스트

주요 기능:
- 특정 날짜/시간의 시장 데이터 재현
- 호가창, 체결 내역 포함
- 실시간처럼 데이터 스트리밍
- 전략 실행 및 결과 기록
"""
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta, time
from pathlib import Path
import json
import time as time_module
from collections import deque
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MarketSnapshot:
    """시장 스냅샷"""
    timestamp: datetime
    stock_code: str
    price: float
    volume: int = 0

    # 호가창 데이터
    bid_prices: List[float] = field(default_factory=list)  # 매수호가 (5단계)
    bid_volumes: List[int] = field(default_factory=list)
    ask_prices: List[float] = field(default_factory=list)  # 매도호가 (5단계)
    ask_volumes: List[int] = field(default_factory=list)

    # 체결 데이터
    trade_price: float = 0.0
    trade_volume: int = 0

    # 추가 정보
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0


class ReplaySimulator:
    """과거 데이터 리플레이 시뮬레이터"""

    def __init__(
        self,
        data_directory: Path = None,
        playback_speed: float = 1.0
    ):
        """
        초기화

        Args:
            data_directory: 과거 데이터 디렉토리
            playback_speed: 재생 속도 (1.0 = 실시간, 10.0 = 10배속)
        """
        if data_directory is None:
            data_directory = Path("data/replay")

        self.data_directory = data_directory
        self.playback_speed = playback_speed

        # 데이터 저장
        self.snapshots: Dict[str, List[MarketSnapshot]] = {}

        # 재생 상태
        self.is_playing = False
        self.current_time: Optional[datetime] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # 콜백
        self.on_tick_callbacks: List[Callable] = []

        logger.info(f"리플레이 시뮬레이터 초기화: 속도={playback_speed}x")

    def load_historical_data(
        self,
        stock_code: str,
        date: str,
        data_source: str = "file"
    ) -> bool:
        """
        과거 데이터 로드

        Args:
            stock_code: 종목 코드
            date: 날짜 (YYYY-MM-DD)
            data_source: 데이터 소스 ('file', 'api', 'database')

        Returns:
            성공 여부
        """
        try:
            if data_source == "file":
                return self._load_from_file(stock_code, date)
            elif data_source == "api":
                return self._load_from_api(stock_code, date)
            elif data_source == "database":
                return self._load_from_database(stock_code, date)
            else:
                raise ValueError(f"Unknown data source: {data_source}")
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            return False

    def _load_from_file(self, stock_code: str, date: str) -> bool:
        """파일에서 데이터 로드"""
        file_path = self.data_directory / f"{stock_code}_{date}.json"

        if not file_path.exists():
            logger.warning(f"데이터 파일 없음: {file_path}")
            # 샘플 데이터 생성
            self._generate_sample_data(stock_code, date)
            return True

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            snapshots = []
            for item in data:
                snapshot = MarketSnapshot(
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    stock_code=item['stock_code'],
                    price=item['price'],
                    volume=item['volume'],
                    bid_prices=item['bid_prices'],
                    bid_volumes=item['bid_volumes'],
                    ask_prices=item['ask_prices'],
                    ask_volumes=item['ask_volumes'],
                    trade_price=item['trade_price'],
                    trade_volume=item['trade_volume'],
                    high=item['high'],
                    low=item['low'],
                    open=item['open']
                )
                snapshots.append(snapshot)

            self.snapshots[stock_code] = snapshots

            if snapshots:
                self.start_time = snapshots[0].timestamp
                self.end_time = snapshots[-1].timestamp

            logger.info(f"데이터 로드 완료: {stock_code}, {len(snapshots)}개 스냅샷")
            return True

        except Exception as e:
            logger.error(f"파일 로드 실패: {e}")
            return False

    def _load_from_api(self, stock_code: str, date: str) -> bool:
        """API에서 데이터 로드 (TODO: 실제 API 연동)"""
        logger.info("API 로드는 아직 구현되지 않았습니다. 샘플 데이터 생성")
        return self._generate_sample_data(stock_code, date)

    def _load_from_database(self, stock_code: str, date: str) -> bool:
        """데이터베이스에서 데이터 로드 (TODO: 실제 DB 연동)"""
        logger.info("DB 로드는 아직 구현되지 않았습니다. 샘플 데이터 생성")
        return self._generate_sample_data(stock_code, date)

    def _generate_sample_data(self, stock_code: str, date: str) -> bool:
        """샘플 데이터 생성 (테스트용)"""
        import random

        snapshots = []
        base_date = datetime.strptime(date, "%Y-%m-%d")
        base_price = 70000  # 초기 가격

        # 09:00 ~ 15:30까지 1분 간격으로 데이터 생성
        start_time = base_date.replace(hour=9, minute=0)
        end_time = base_date.replace(hour=15, minute=30)

        current_time = start_time
        current_price = base_price

        while current_time <= end_time:
            # 가격 변동 (랜덤 워크)
            price_change = random.randint(-500, 500)
            current_price = max(1000, current_price + price_change)

            # 호가창 데이터
            bid_prices = [current_price - (i * 50) for i in range(1, 6)]
            ask_prices = [current_price + (i * 50) for i in range(1, 6)]
            bid_volumes = [random.randint(100, 1000) for _ in range(5)]
            ask_volumes = [random.randint(100, 1000) for _ in range(5)]

            snapshot = MarketSnapshot(
                timestamp=current_time,
                stock_code=stock_code,
                price=current_price,
                volume=random.randint(1000, 10000),
                bid_prices=bid_prices,
                bid_volumes=bid_volumes,
                ask_prices=ask_prices,
                ask_volumes=ask_volumes,
                trade_price=current_price,
                trade_volume=random.randint(10, 100),
                high=current_price + random.randint(0, 500),
                low=current_price - random.randint(0, 500),
                open=base_price
            )

            snapshots.append(snapshot)
            current_time += timedelta(minutes=1)

        self.snapshots[stock_code] = snapshots

        if snapshots:
            self.start_time = snapshots[0].timestamp
            self.end_time = snapshots[-1].timestamp

        logger.info(f"샘플 데이터 생성 완료: {len(snapshots)}개")
        return True

    def register_callback(self, callback: Callable[[MarketSnapshot], None]):
        """틱 데이터 콜백 등록"""
        self.on_tick_callbacks.append(callback)

    def play(self, stock_codes: Optional[List[str]] = None):
        """
        리플레이 재생 시작

        Args:
            stock_codes: 재생할 종목 코드 리스트 (None이면 전체)
        """
        if not self.snapshots:
            logger.error("로드된 데이터가 없습니다")
            return

        self.is_playing = True
        self.current_time = self.start_time

        if stock_codes is None:
            stock_codes = list(self.snapshots.keys())

        logger.info(f"리플레이 시작: {self.start_time} ~ {self.end_time}")

        # 모든 종목의 데이터를 시간순으로 정렬
        all_snapshots = []
        for code in stock_codes:
            if code in self.snapshots:
                all_snapshots.extend(self.snapshots[code])

        all_snapshots.sort(key=lambda x: x.timestamp)

        # 재생
        prev_time = None
        for snapshot in all_snapshots:
            if not self.is_playing:
                break

            # 시간 간격 계산 및 대기
            if prev_time is not None:
                time_diff = (snapshot.timestamp - prev_time).total_seconds()
                sleep_time = time_diff / self.playback_speed
                if sleep_time > 0:
                    time_module.sleep(sleep_time)

            # 콜백 호출
            for callback in self.on_tick_callbacks:
                try:
                    callback(snapshot)
                except Exception as e:
                    logger.error(f"콜백 에러: {e}")

            self.current_time = snapshot.timestamp
            prev_time = snapshot.timestamp

        logger.info("리플레이 종료")
        self.is_playing = False

    def pause(self):
        """일시 정지"""
        self.is_playing = False
        logger.info("리플레이 일시 정지")

    def resume(self):
        """재개"""
        self.is_playing = True
        logger.info("리플레이 재개")

    def stop(self):
        """정지"""
        self.is_playing = False
        self.current_time = self.start_time
        logger.info("리플레이 정지")

    def get_current_snapshot(self, stock_code: str) -> Optional[MarketSnapshot]:
        """현재 시점의 스냅샷 조회"""
        if stock_code not in self.snapshots or self.current_time is None:
            return None

        # 현재 시간에 가장 가까운 스냅샷 찾기
        snapshots = self.snapshots[stock_code]
        for snapshot in snapshots:
            if snapshot.timestamp >= self.current_time:
                return snapshot

        return snapshots[-1] if snapshots else None

    def save_replay_data(self, stock_code: str, date: str):
        """리플레이 데이터를 파일로 저장"""
        if stock_code not in self.snapshots:
            logger.error(f"저장할 데이터 없음: {stock_code}")
            return

        file_path = self.data_directory / f"{stock_code}_{date}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        data = [asdict(snapshot) for snapshot in self.snapshots[stock_code]]

        # datetime을 문자열로 변환
        for item in data:
            item['timestamp'] = item['timestamp'].isoformat()

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"리플레이 데이터 저장: {file_path}")


# 사용 예시
if __name__ == "__main__":
    simulator = ReplaySimulator(playback_speed=10.0)

    # 과거 데이터 로드
    simulator.load_historical_data("005930", "2024-01-15")

    # 콜백 등록
    def on_tick(snapshot: MarketSnapshot):
        print(f"[{snapshot.timestamp}] {snapshot.stock_code}: {snapshot.price:,}원")

    simulator.register_callback(on_tick)

    # 재생
    simulator.play()
