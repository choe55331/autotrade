"""
Enhanced WebSocket Manager with Advanced Stability Features
v1.0 - 안정성, 복원력, 모니터링 강화
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import deque

from .websocket_manager import WebSocketManager
from utils.logger_new import get_logger

logger = get_logger()


class ConnectionState(Enum):
    """WebSocket 연결 상태"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    LOGGED_IN = "logged_in"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class ConnectionMetrics:
    """연결 메트릭스"""
    total_connections: int = 0
    successful_connections: int = 0
    failed_connections: int = 0
    total_reconnects: int = 0
    successful_reconnects: int = 0
    messages_received: int = 0
    messages_sent: int = 0
    last_message_time: Optional[datetime] = None
    connection_uptime: float = 0.0
    average_latency_ms: float = 0.0


@dataclass
class PendingMessage:
    """대기중인 메시지"""
    data: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3


class EnhancedWebSocketManager:
    """
    향상된 WebSocket 매니저

    Features:
    - Exponential backoff reconnection
    - Heartbeat monitoring
    - Message queue for reliability
    - Connection health tracking
    - Comprehensive metrics
    - Circuit breaker pattern
    """

    def __init__(
        self,
        access_token: str,
        base_url: str = "https://api.kiwoom.com",
        heartbeat_interval: int = 30,
        heartbeat_timeout: int = 10,
        max_reconnect_attempts: int = 10,
        initial_reconnect_delay: float = 1.0,
        max_reconnect_delay: float = 60.0
    ):
        self.ws_manager = WebSocketManager(access_token, base_url)

        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self.max_reconnect_attempts = max_reconnect_attempts
        self.initial_reconnect_delay = initial_reconnect_delay
        self.max_reconnect_delay = max_reconnect_delay

        self.state = ConnectionState.DISCONNECTED
        self.metrics = ConnectionMetrics()

        self.message_queue: deque = deque(maxlen=1000)
        self.pending_messages: List[PendingMessage] = []

        self.last_heartbeat_sent: Optional[datetime] = None
        self.last_heartbeat_received: Optional[datetime] = None
        self.connection_start_time: Optional[datetime] = None

        self.heartbeat_task: Optional[asyncio.Task] = None
        self.queue_processor_task: Optional[asyncio.Task] = None

        self.reconnect_count = 0
        self.circuit_breaker_open = False
        self.circuit_breaker_reset_time: Optional[datetime] = None

        logger.info("EnhancedWebSocketManager initialized")

    async def connect(self) -> bool:
        """향상된 연결 로직"""
        if self.circuit_breaker_open:
            if datetime.now() < self.circuit_breaker_reset_time:
                logger.warning("Circuit breaker is open, connection not allowed")
                return False
            else:
                logger.info("Circuit breaker reset time reached, attempting connection")
                self.circuit_breaker_open = False

        self.state = ConnectionState.CONNECTING
        self.metrics.total_connections += 1

        try:
            success = await self.ws_manager.connect()

            if success:
                self.state = ConnectionState.LOGGED_IN
                self.metrics.successful_connections += 1
                self.connection_start_time = datetime.now()
                self.reconnect_count = 0

                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                self.queue_processor_task = asyncio.create_task(self._process_message_queue())

                logger.info("Enhanced WebSocket connected successfully")
                return True
            else:
                self.state = ConnectionState.FAILED
                self.metrics.failed_connections += 1
                self._maybe_open_circuit_breaker()
                return False

        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.state = ConnectionState.FAILED
            self.metrics.failed_connections += 1
            self._maybe_open_circuit_breaker()
            return False

    async def reconnect_with_backoff(self) -> bool:
        """지수 백오프를 사용한 재연결"""
        self.state = ConnectionState.RECONNECTING
        self.metrics.total_reconnects += 1

        for attempt in range(self.max_reconnect_attempts):
            if self.circuit_breaker_open:
                logger.error("Circuit breaker is open, stopping reconnect attempts")
                return False

            delay = min(
                self.initial_reconnect_delay * (2 ** attempt),
                self.max_reconnect_delay
            )

            logger.info(f"Reconnect attempt {attempt + 1}/{self.max_reconnect_attempts} after {delay:.1f}s")
            await asyncio.sleep(delay)

            try:
                await self.disconnect()

                if await self.connect():
                    self.metrics.successful_reconnects += 1
                    logger.info("Reconnection successful")

                    await self._resubscribe_all()
                    return True

            except Exception as e:
                logger.error(f"Reconnect attempt {attempt + 1} failed: {e}")
                continue

        logger.error(f"Failed to reconnect after {self.max_reconnect_attempts} attempts")
        self.state = ConnectionState.FAILED
        self._maybe_open_circuit_breaker()
        return False

    async def _heartbeat_loop(self):
        """하트비트 모니터링"""
        while self.state in [ConnectionState.CONNECTED, ConnectionState.LOGGED_IN]:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                if self.last_heartbeat_received:
                    time_since_last = (datetime.now() - self.last_heartbeat_received).total_seconds()

                    if time_since_last > self.heartbeat_interval + self.heartbeat_timeout:
                        logger.warning(f"Heartbeat timeout: {time_since_last:.1f}s since last message")
                        await self.reconnect_with_backoff()
                        break

                self.last_heartbeat_sent = datetime.now()

            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                break

    async def _process_message_queue(self):
        """메시지 큐 처리"""
        while self.state in [ConnectionState.CONNECTED, ConnectionState.LOGGED_IN]:
            try:
                if self.pending_messages:
                    pending = self.pending_messages[0]

                    try:
                        await self.ws_manager.websocket.send(pending.data)
                        self.pending_messages.pop(0)
                        self.metrics.messages_sent += 1

                    except Exception as e:
                        logger.error(f"Failed to send queued message: {e}")
                        pending.retry_count += 1

                        if pending.retry_count >= pending.max_retries:
                            logger.error("Message exceeded max retries, dropping")
                            self.pending_messages.pop(0)

                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Message queue processor error: {e}")
                await asyncio.sleep(1)

    async def send_with_queue(self, data: Dict[str, Any]) -> bool:
        """메시지 전송 (큐 사용)"""
        try:
            if self.state == ConnectionState.LOGGED_IN:
                await self.ws_manager.websocket.send(data)
                self.metrics.messages_sent += 1
                return True
            else:
                if len(self.pending_messages) < 1000:
                    self.pending_messages.append(
                        PendingMessage(data=data, timestamp=datetime.now())
                    )
                    logger.info("Message queued for later delivery")
                return False

        except Exception as e:
            logger.error(f"Send error: {e}")
            self.pending_messages.append(
                PendingMessage(data=data, timestamp=datetime.now())
            )
            return False

    async def _resubscribe_all(self):
        """모든 구독 재등록"""
        try:
            subscriptions = self.ws_manager.subscriptions.copy()

            for grp_no, sub_info in subscriptions.items():
                success = await self.ws_manager.subscribe(
                    stock_codes=sub_info['stock_codes'],
                    types=sub_info['types'],
                    grp_no=grp_no,
                    refresh=sub_info['refresh']
                )

                if success:
                    logger.info(f"Resubscribed: {grp_no}")
                else:
                    logger.error(f"Failed to resubscribe: {grp_no}")

        except Exception as e:
            logger.error(f"Resubscription error: {e}")

    def _maybe_open_circuit_breaker(self):
        """서킷 브레이커 열기 여부 판단"""
        failure_rate = (
            self.metrics.failed_connections / max(self.metrics.total_connections, 1)
        )

        if self.metrics.failed_connections >= 5 and failure_rate > 0.5:
            self.circuit_breaker_open = True
            self.circuit_breaker_reset_time = datetime.now() + timedelta(minutes=5)
            logger.error("Circuit breaker OPENED - too many failures")

    async def disconnect(self):
        """연결 종료"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        if self.queue_processor_task:
            self.queue_processor_task.cancel()

        if self.connection_start_time:
            self.metrics.connection_uptime += (
                datetime.now() - self.connection_start_time
            ).total_seconds()

        await self.ws_manager.disconnect()
        self.state = ConnectionState.DISCONNECTED

    def get_metrics(self) -> Dict[str, Any]:
        """메트릭스 조회"""
        return {
            'state': self.state.value,
            'metrics': {
                'total_connections': self.metrics.total_connections,
                'successful_connections': self.metrics.successful_connections,
                'failed_connections': self.metrics.failed_connections,
                'success_rate': (
                    self.metrics.successful_connections / max(self.metrics.total_connections, 1)
                ),
                'total_reconnects': self.metrics.total_reconnects,
                'successful_reconnects': self.metrics.successful_reconnects,
                'messages_received': self.metrics.messages_received,
                'messages_sent': self.metrics.messages_sent,
                'connection_uptime_hours': self.metrics.connection_uptime / 3600,
                'pending_messages': len(self.pending_messages),
                'circuit_breaker_open': self.circuit_breaker_open
            },
            'health': {
                'is_connected': self.state == ConnectionState.LOGGED_IN,
                'last_message_time': self.last_heartbeat_received,
                'connection_age_seconds': (
                    (datetime.now() - self.connection_start_time).total_seconds()
                    if self.connection_start_time else 0
                )
            }
        }

    async def subscribe(self, stock_codes: List[str], types: List[str], **kwargs) -> bool:
        """구독 (원본 메서드 래핑)"""
        return await self.ws_manager.subscribe(stock_codes, types, **kwargs)

    def register_callback(self, data_type: str, callback: Callable):
        """콜백 등록 (원본 메서드 래핑)"""
        self.ws_manager.register_callback(data_type, callback)

    async def receive_loop(self):
        """수신 루프 (원본 메서드 래핑 + 메트릭스)"""
        original_receive = self.ws_manager.receive_loop

        while self.state in [ConnectionState.CONNECTED, ConnectionState.LOGGED_IN]:
            try:
                await original_receive()
                self.metrics.messages_received += 1
                self.last_heartbeat_received = datetime.now()

            except Exception as e:
                logger.error(f"Receive loop error: {e}")
                await self.reconnect_with_backoff()
                break
