"""
core/websocket_client.py
WebSocket 클라이언트 (기존 websocket 모듈과 통합)
"""
import json
import logging
import threading
import time
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    키움증권 WebSocket 클라이언트
    
    주요 기능:
    - WebSocket 연결 관리
    - 자동 재연결
    - 메시지 송수신
    - 콜백 처리
    
    Note: 기존 websocket 모듈이 있다면 그것을 사용하고,
          이 파일은 필요시 참고용으로 사용하세요.
    """
    
    def __init__(self, url: str, token: str):
        """
        WebSocket 클라이언트 초기화
        
        Args:
            url: WebSocket URL
            token: 인증 토큰
        """
        self.url = url
        self.token = token
        self.ws = None
        self.is_connected = False
        self.should_reconnect = True
        self.reconnect_delay = 5
        self.max_reconnects = 10
        self.reconnect_count = 0
        
        # 콜백
        self.on_message_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        self.on_open_callback: Optional[Callable] = None
        self.on_close_callback: Optional[Callable] = None
        
        # 스레드
        self.ws_thread: Optional[threading.Thread] = None
        
        logger.info("WebSocket 클라이언트 초기화 완료")
    
    def connect(self):
        """WebSocket 연결"""
        try:
            import websocket
            
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                header=[f"authorization: Bearer {self.token}"]
            )
            
            # 별도 스레드에서 실행
            self.ws_thread = threading.Thread(
                target=self.ws.run_forever,
                daemon=True
            )
            self.ws_thread.start()
            
            logger.info("WebSocket 연결 시도 중...")
            
        except ImportError:
            logger.error("websocket-client 패키지가 설치되지 않았습니다")
            logger.error("pip install websocket-client 실행 필요")
        except Exception as e:
            logger.error(f"WebSocket 연결 실패: {e}")
    
    def disconnect(self):
        """WebSocket 연결 해제"""
        self.should_reconnect = False
        
        if self.ws:
            try:
                self.ws.close()
                logger.info("WebSocket 연결 해제 완료")
            except Exception as e:
                logger.error(f"WebSocket 연결 해제 중 오류: {e}")
        
        self.is_connected = False
    
    def send(self, data: Dict[str, Any]):
        """
        메시지 전송
        
        Args:
            data: 전송할 데이터 (딕셔너리)
        """
        if not self.is_connected:
            logger.warning("WebSocket이 연결되지 않았습니다")
            return False
        
        try:
            message = json.dumps(data, ensure_ascii=False)
            self.ws.send(message)
            logger.debug(f"메시지 전송: {message[:100]}")
            return True
        except Exception as e:
            logger.error(f"메시지 전송 실패: {e}")
            return False
    
    def subscribe(self, subscription_data: Dict[str, Any]):
        """
        구독 요청
        
        Args:
            subscription_data: 구독 데이터
        """
        return self.send(subscription_data)
    
    def unsubscribe(self, unsubscription_data: Dict[str, Any]):
        """
        구독 해제
        
        Args:
            unsubscription_data: 구독 해제 데이터
        """
        return self.send(unsubscription_data)
    
    def register_callbacks(
        self,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_open: Optional[Callable] = None,
        on_close: Optional[Callable] = None
    ):
        """
        콜백 함수 등록
        
        Args:
            on_message: 메시지 수신 콜백
            on_error: 에러 콜백
            on_open: 연결 성공 콜백
            on_close: 연결 종료 콜백
        """
        if on_message:
            self.on_message_callback = on_message
        if on_error:
            self.on_error_callback = on_error
        if on_open:
            self.on_open_callback = on_open
        if on_close:
            self.on_close_callback = on_close
        
        logger.info("WebSocket 콜백 등록 완료")
    
    def _on_open(self, ws):
        """연결 성공 핸들러"""
        self.is_connected = True
        self.reconnect_count = 0
        logger.info("WebSocket 연결 성공")
        
        if self.on_open_callback:
            try:
                self.on_open_callback(ws)
            except Exception as e:
                logger.error(f"on_open 콜백 실행 중 오류: {e}")
    
    def _on_message(self, ws, message):
        """메시지 수신 핸들러"""
        logger.debug(f"메시지 수신: {message[:100]}")
        
        if self.on_message_callback:
            try:
                data = json.loads(message)
                self.on_message_callback(data)
            except json.JSONDecodeError as e:
                logger.error(f"메시지 JSON 파싱 실패: {e}")
            except Exception as e:
                logger.error(f"on_message 콜백 실행 중 오류: {e}")
    
    def _on_error(self, ws, error):
        """에러 핸들러"""
        logger.error(f"WebSocket 오류: {error}")
        
        if self.on_error_callback:
            try:
                self.on_error_callback(error)
            except Exception as e:
                logger.error(f"on_error 콜백 실행 중 오류: {e}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """연결 종료 핸들러"""
        self.is_connected = False
        logger.info(f"WebSocket 연결 종료 (코드: {close_status_code}, 메시지: {close_msg})")
        
        if self.on_close_callback:
            try:
                self.on_close_callback(close_status_code, close_msg)
            except Exception as e:
                logger.error(f"on_close 콜백 실행 중 오류: {e}")
        
        # 재연결 시도
        if self.should_reconnect and self.reconnect_count < self.max_reconnects:
            self.reconnect_count += 1
            logger.info(f"재연결 시도 {self.reconnect_count}/{self.max_reconnects} (#{self.reconnect_delay}초 후)")
            time.sleep(self.reconnect_delay)
            self.connect()
        elif self.reconnect_count >= self.max_reconnects:
            logger.error("최대 재연결 횟수 초과. 재연결을 중단합니다.")


__all__ = ['WebSocketClient']