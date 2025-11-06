features/status_monitor.py
시스템 상태 모니터링 - Gemini, REST API, WebSocket, 테스트모드 연결 상태 추적
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """연결 상태"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CHECKING = "checking"
    DISABLED = "disabled"
    ERROR = "error"


class StatusMonitor:
    """
    시스템 상태 모니터링

    추적 항목:
    - Gemini API 연결 상태
    - REST API 연결 상태
    - WebSocket 연결 상태
    - 테스트 모드 활성화 여부
    """

    def __init__(self):
        """상태 모니터 초기화"""
        self.status: Dict[str, Dict[str, Any]] = {
            "gemini": {
                "status": ConnectionStatus.DISABLED,
                "last_check": None,
                "last_success": None,
                "error_message": None,
                "response_time_ms": None
            },
            "rest_api": {
                "status": ConnectionStatus.DISABLED,
                "last_check": None,
                "last_success": None,
                "error_message": None,
                "response_time_ms": None
            },
            "websocket": {
                "status": ConnectionStatus.DISABLED,
                "last_check": None,
                "last_success": None,
                "error_message": None,
                "response_time_ms": None
            },
            "test_mode": {
                "status": ConnectionStatus.DISABLED,
                "last_check": None,
                "enabled": False,
                "test_date": None,
                "reason": None
            }
        }

        logger.info("상태 모니터 초기화 완료")

    def check_gemini_status(self) -> ConnectionStatus:
        """
        Gemini API 연결 상태 확인

        Returns:
            연결 상태
        """
        try:
            from ai.gemini_analyzer import GeminiAnalyzer

            start_time = time.time()
            self.status["gemini"]["status"] = ConnectionStatus.CHECKING
            self.status["gemini"]["last_check"] = datetime.now().isoformat()

            try:
                analyzer = GeminiAnalyzer()

                test_prompt = "Test connection. Reply with OK."

                if hasattr(analyzer, 'model') and analyzer.model is not None:
                    response_time = (time.time() - start_time) * 1000

                    self.status["gemini"]["status"] = ConnectionStatus.CONNECTED
                    self.status["gemini"]["last_success"] = datetime.now().isoformat()
                    self.status["gemini"]["error_message"] = None
                    self.status["gemini"]["response_time_ms"] = round(response_time, 2)

                    logger.info("Gemini API 연결 확인 완료")
                    return ConnectionStatus.CONNECTED
                else:
                    raise Exception("Gemini model not initialized")

            except Exception as e:
                self.status["gemini"]["status"] = ConnectionStatus.ERROR
                self.status["gemini"]["error_message"] = str(e)
                logger.error(f"Gemini API 연결 실패: {e}")
                return ConnectionStatus.ERROR

        except ImportError:
            self.status["gemini"]["status"] = ConnectionStatus.DISABLED
            self.status["gemini"]["error_message"] = "Gemini module not available"
            logger.warning("Gemini 모듈을 찾을 수 없습니다")
            return ConnectionStatus.DISABLED

    def check_rest_api_status(self) -> ConnectionStatus:
        """
        REST API 연결 상태 확인

        Returns:
            연결 상태
        """
        try:
            from core.rest_client import KiwoomRESTClient

            start_time = time.time()
            self.status["rest_api"]["status"] = ConnectionStatus.CHECKING
            self.status["rest_api"]["last_check"] = datetime.now().isoformat()

            client = KiwoomRESTClient.get_instance()

            if client._is_token_valid():
                response_time = (time.time() - start_time) * 1000

                self.status["rest_api"]["status"] = ConnectionStatus.CONNECTED
                self.status["rest_api"]["last_success"] = datetime.now().isoformat()
                self.status["rest_api"]["error_message"] = None
                self.status["rest_api"]["response_time_ms"] = round(response_time, 2)

                logger.info("REST API 연결 확인 완료")
                return ConnectionStatus.CONNECTED
            else:
                if client._get_token():
                    response_time = (time.time() - start_time) * 1000

                    self.status["rest_api"]["status"] = ConnectionStatus.CONNECTED
                    self.status["rest_api"]["last_success"] = datetime.now().isoformat()
                    self.status["rest_api"]["error_message"] = None
                    self.status["rest_api"]["response_time_ms"] = round(response_time, 2)

                    logger.info("REST API 토큰 재발급 완료")
                    return ConnectionStatus.CONNECTED
                else:
                    self.status["rest_api"]["status"] = ConnectionStatus.ERROR
                    self.status["rest_api"]["error_message"] = "Token acquisition failed"
                    logger.error("REST API 토큰 발급 실패")
                    return ConnectionStatus.ERROR

        except Exception as e:
            self.status["rest_api"]["status"] = ConnectionStatus.ERROR
            self.status["rest_api"]["error_message"] = str(e)
            logger.error(f"REST API 연결 확인 실패: {e}")
            return ConnectionStatus.ERROR

    def check_websocket_status(self) -> ConnectionStatus:
        """
        WebSocket 연결 상태 확인

        Returns:
            연결 상태
        """
        try:
            from core.websocket_client import WebSocketClient

            self.status["websocket"]["status"] = ConnectionStatus.DISABLED
            self.status["websocket"]["last_check"] = datetime.now().isoformat()
            self.status["websocket"]["error_message"] = "Not implemented - WebSocket client needs integration"

            logger.info("WebSocket 모듈 확인 완료 (연결 상태 미구현)")
            return ConnectionStatus.DISABLED

        except ImportError:
            self.status["websocket"]["status"] = ConnectionStatus.DISABLED
            self.status["websocket"]["error_message"] = "WebSocket module not available"
            logger.warning("WebSocket 모듈을 찾을 수 없습니다")
            return ConnectionStatus.DISABLED

    def check_test_mode_status(self) -> ConnectionStatus:
        """
        테스트 모드 활성화 여부 확인

        Returns:
            연결 상태
        """
        try:
            from features.test_mode_manager import TestModeManager
            from utils.trading_date import is_market_hours, get_last_trading_date

            self.status["test_mode"]["last_check"] = datetime.now().isoformat()

            test_manager = TestModeManager()
            is_test = test_manager.check_and_activate_test_mode()

            if is_test:
                self.status["test_mode"]["status"] = ConnectionStatus.CONNECTED
                self.status["test_mode"]["enabled"] = True
                self.status["test_mode"]["test_date"] = test_manager.test_date

                now = datetime.now()
                if now.weekday() in [5, 6]:
                    reason = "주말"
                elif now.hour < 8:
                    reason = "오전 8시 이전"
                elif now.hour >= 20:
                    reason = "오후 8시 이후"
                elif not is_market_hours():
                    reason = "장 마감 시간"
                else:
                    reason = "알 수 없음"

                self.status["test_mode"]["reason"] = reason
                logger.info(f"테스트 모드 활성화됨: {reason}")
                return ConnectionStatus.CONNECTED
            else:
                self.status["test_mode"]["status"] = ConnectionStatus.DISCONNECTED
                self.status["test_mode"]["enabled"] = False
                self.status["test_mode"]["test_date"] = None
                self.status["test_mode"]["reason"] = "정규 장 시간"
                logger.info("테스트 모드 비활성화됨: 정규 장 시간")
                return ConnectionStatus.DISCONNECTED

        except Exception as e:
            self.status["test_mode"]["status"] = ConnectionStatus.ERROR
            self.status["test_mode"]["enabled"] = False
            self.status["test_mode"]["error_message"] = str(e)
            logger.error(f"테스트 모드 확인 실패: {e}")
            return ConnectionStatus.ERROR

    def check_all_status(self) -> Dict[str, Any]:
        """
        모든 시스템 상태 확인

        Returns:
            전체 상태 딕셔너리
        """
        logger.info("전체 시스템 상태 확인 시작...")

        self.check_gemini_status()
        self.check_rest_api_status()
        self.check_websocket_status()
        self.check_test_mode_status()

        logger.info("전체 시스템 상태 확인 완료")
        return self.get_status_summary()

    def get_status_summary(self) -> Dict[str, Any]:
        """
        상태 요약 정보 반환

        Returns:
            상태 요약
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "components": {
                "gemini": {
                    "status": self.status["gemini"]["status"].value,
                    "connected": self.status["gemini"]["status"] == ConnectionStatus.CONNECTED,
                    "last_check": self.status["gemini"]["last_check"],
                    "error": self.status["gemini"]["error_message"]
                },
                "rest_api": {
                    "status": self.status["rest_api"]["status"].value,
                    "connected": self.status["rest_api"]["status"] == ConnectionStatus.CONNECTED,
                    "last_check": self.status["rest_api"]["last_check"],
                    "error": self.status["rest_api"]["error_message"]
                },
                "websocket": {
                    "status": self.status["websocket"]["status"].value,
                    "connected": self.status["websocket"]["status"] == ConnectionStatus.CONNECTED,
                    "last_check": self.status["websocket"]["last_check"],
                    "error": self.status["websocket"]["error_message"]
                },
                "test_mode": {
                    "status": self.status["test_mode"]["status"].value,
                    "enabled": self.status["test_mode"]["enabled"],
                    "last_check": self.status["test_mode"]["last_check"],
                    "test_date": self.status["test_mode"]["test_date"],
                    "reason": self.status["test_mode"]["reason"]
                }
            }
        }

    def get_status_color(self, component: str) -> str:
        """
        컴포넌트의 상태 색상 반환

        Args:
            component: 컴포넌트 이름 (gemini, rest_api, websocket, test_mode)

        Returns:
            색상 코드 (green, red, yellow, gray)
        """
        if component not in self.status:
            return "gray"

        status = self.status[component]["status"]

        if status == ConnectionStatus.CONNECTED:
            return "green"
        elif status in [ConnectionStatus.ERROR, ConnectionStatus.DISCONNECTED]:
            return "red"
        elif status == ConnectionStatus.CHECKING:
            return "yellow"
        else:
            return "gray"


_status_monitor_instance: Optional[StatusMonitor] = None


def get_status_monitor() -> StatusMonitor:
    """
    StatusMonitor 싱글톤 인스턴스 반환

    Returns:
        StatusMonitor 인스턴스
    """
    global _status_monitor_instance

    if _status_monitor_instance is None:
        _status_monitor_instance = StatusMonitor()

    return _status_monitor_instance


__all__ = ['StatusMonitor', 'ConnectionStatus', 'get_status_monitor']
