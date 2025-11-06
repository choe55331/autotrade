"""
api/realtime.py
실시간 데이터 API (WebSocket 기반)
"""
import logging
from typing import Dict, Any, Optional, Callable, List

logger = logging.getLogger(__name__)


class RealtimeAPI:
    """
    실시간 데이터 API
    
    주요 기능:
    - 실시간 시세 구독
    - 실시간 호가 구독
    - 실시간 체결 구독
    - 계좌 실시간 정보
    
    Note: WebSocket 클라이언트가 필요합니다.
    """
    
    def __init__(self, ws_manager=None):
        """
        RealtimeAPI 초기화
        
        Args:
            ws_manager: WebSocket Manager 인스턴스 (선택)
        """
        self.ws_manager = ws_manager
        self.subscriptions = {}
        logger.info("RealtimeAPI 초기화 완료")
    
    def set_websocket_manager(self, ws_manager):
        """
        WebSocket Manager 설정
        
        Args:
            ws_manager: WebSocket Manager 인스턴스
        """
        self.ws_manager = ws_manager
        logger.info("WebSocket Manager 설정 완료")
    
    def subscribe_price(
        self,
        stock_codes: List[str],
        callback: Optional[Callable] = None
    ) -> bool:
        실시간 시세 구독
        
        Args:
            stock_codes: 종목코드 리스트
            callback: 데이터 수신 콜백
        
        Returns:
            성공 여부
        if not self.ws_manager:
            logger.error("WebSocket Manager가 설정되지 않았습니다")
            return False
        
        subscription_data = {
            "header": {
                "tr_id": "DOSK_H0_STCPR",
                "tr_type": "3"
            },
            "body": {
                "input": {
                    "stock_codes": stock_codes
                }
            }
        }
        
        try:
            result = self.ws_manager.subscribe(subscription_data)
            
            if result:
                for code in stock_codes:
                    self.subscriptions[f"price_{code}"] = callback
                logger.info(f"실시간 시세 구독 완료: {len(stock_codes)}개 종목")
                return True
            else:
                logger.error("실시간 시세 구독 실패")
                return False
        except Exception as e:
            logger.error(f"실시간 시세 구독 중 오류: {e}")
            return False
    
    def unsubscribe_price(self, stock_codes: List[str]) -> bool:
        """
        실시간 시세 구독 해제
        
        Args:
            stock_codes: 종목코드 리스트
        
        Returns:
            성공 여부
        """
        if not self.ws_manager:
            logger.error("WebSocket Manager가 설정되지 않았습니다")
            return False
        
        unsubscription_data = {
            "header": {
                "tr_id": "DOSK_H0_STCPR",
                "tr_type": "4"
            },
            "body": {
                "input": {
                    "stock_codes": stock_codes
                }
            }
        }
        
        try:
            result = self.ws_manager.unsubscribe(unsubscription_data)
            
            if result:
                for code in stock_codes:
                    self.subscriptions.pop(f"price_{code}", None)
                logger.info(f"실시간 시세 구독 해제 완료: {len(stock_codes)}개 종목")
                return True
            else:
                logger.error("실시간 시세 구독 해제 실패")
                return False
        except Exception as e:
            logger.error(f"실시간 시세 구독 해제 중 오류: {e}")
            return False
    
    def subscribe_orderbook(
        self,
        stock_codes: List[str],
        callback: Optional[Callable] = None
    ) -> bool:
        실시간 호가 구독
        
        Args:
            stock_codes: 종목코드 리스트
            callback: 데이터 수신 콜백
        
        Returns:
            성공 여부
        if not self.ws_manager:
            logger.error("WebSocket Manager가 설정되지 않았습니다")
            return False
        
        subscription_data = {
            "header": {
                "tr_id": "DOSK_H0_HOGABK",
                "tr_type": "3"
            },
            "body": {
                "input": {
                    "stock_codes": stock_codes
                }
            }
        }
        
        try:
            result = self.ws_manager.subscribe(subscription_data)
            
            if result:
                for code in stock_codes:
                    self.subscriptions[f"orderbook_{code}"] = callback
                logger.info(f"실시간 호가 구독 완료: {len(stock_codes)}개 종목")
                return True
            else:
                logger.error("실시간 호가 구독 실패")
                return False
        except Exception as e:
            logger.error(f"실시간 호가 구독 중 오류: {e}")
            return False
    
    def subscribe_execution(
        self,
        account_number: str,
        callback: Optional[Callable] = None
    ) -> bool:
        실시간 체결 구독
        
        Args:
            account_number: 계좌번호
            callback: 데이터 수신 콜백
        
        Returns:
            성공 여부
        if not self.ws_manager:
            logger.error("WebSocket Manager가 설정되지 않았습니다")
            return False
        
        parts = account_number.split('-')
        account_prefix = parts[0]
        account_suffix = parts[1] if len(parts) > 1 else '01'
        
        subscription_data = {
            "header": {
                "tr_id": "DOSK_H0_EXECRPT",
                "tr_type": "3"
            },
            "body": {
                "input": {
                    "account_code": account_prefix,
                    "account_suffix": account_suffix
                }
            }
        }
        
        try:
            result = self.ws_manager.subscribe(subscription_data)
            
            if result:
                self.subscriptions[f"execution_{account_number}"] = callback
                logger.info(f"실시간 체결 구독 완료: {account_number}")
                return True
            else:
                logger.error("실시간 체결 구독 실패")
                return False
        except Exception as e:
            logger.error(f"실시간 체결 구독 중 오류: {e}")
            return False
    
    def handle_message(self, message: Dict[str, Any]):
        """
        WebSocket 메시지 처리
        
        Args:
            message: 수신 메시지
        """
        try:
            tr_id = message.get('header', {}).get('tr_id', '')
            
            if 'STCPR' in tr_id:
                stock_code = message.get('body', {}).get('stock_code', '')
                callback = self.subscriptions.get(f"price_{stock_code}")
                if callback:
                    callback(message)
            
            elif 'HOGABK' in tr_id:
                stock_code = message.get('body', {}).get('stock_code', '')
                callback = self.subscriptions.get(f"orderbook_{stock_code}")
                if callback:
                    callback(message)
            
            elif 'EXECRPT' in tr_id:
                account_code = message.get('body', {}).get('account_code', '')
                account_suffix = message.get('body', {}).get('account_suffix', '')
                account_number = f"{account_code}-{account_suffix}"
                callback = self.subscriptions.get(f"execution_{account_number}")
                if callback:
                    callback(message)
            
        except Exception as e:
            logger.error(f"메시지 처리 중 오류: {e}")
    
    def get_subscriptions(self) -> Dict[str, Any]:
        """
        현재 구독 목록 반환
        
        Returns:
            구독 목록
        """
        return self.subscriptions.copy()
    
    def clear_subscriptions(self):
        """모든 구독 해제"""
        self.subscriptions.clear()
        logger.info("모든 구독 해제 완료")


__all__ = ['RealtimeAPI']