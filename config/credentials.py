"""
config/credentials.py
API 키 및 민감정보 관리
"""
import os
from dotenv import load_dotenv
from typing import Dict, Optional

# 환경변수 로드
load_dotenv()

class Credentials:
    """API 자격증명 관리 클래스"""
    
    def __init__(self):
        # Kiwoom API 설정
        self.KIWOOM_REST_BASE_URL = os.getenv('KIWOOM_REST_BASE_URL', 'https://api.kiwoom.com')
        self.KIWOOM_REST_APPKEY = os.getenv('KIWOOM_REST_APPKEY', 'TjgoRS0k_U-EcnCBxwn23EM6wbTxHiFmuMHGpIYObRU')
        self.KIWOOM_REST_SECRETKEY = os.getenv('KIWOOM_REST_SECRETKEY', 'LAcgLwxqlOduBocdLIDO57t4kHHjoyxVonSe2ghnt3U')
        self.ACCOUNT_NUMBER = os.getenv('ACCOUNT_NUMBER', '64523232-10')
        self.KIWOOM_WEBSOCKET_URL = os.getenv('KIWOOM_WEBSOCKET_URL', 'wss://api.kiwoom.com:10000/api/dostk/websocket')
        
        # Gemini API 설정
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyB1xDbzci0UpmcqG-2DJHH6EWv4QYBZUzQ')
        self.GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.5-flash')
        
        # Telegram 설정
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
        
        # Naver API 설정
        self.NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID', '_coT1S_U5iEz4WWlf_yp')
        self.NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET', 'PwkQiWJ_o0')
        
        # 계좌번호 파싱
        self._parse_account_number()
    
    def _parse_account_number(self):
        """계좌번호 파싱"""
        if '-' in self.ACCOUNT_NUMBER:
            parts = self.ACCOUNT_NUMBER.split('-')
            self.ACCOUNT_PREFIX = parts[0]
            self.ACCOUNT_SUFFIX = parts[1]
        else:
            self.ACCOUNT_PREFIX = ""
            self.ACCOUNT_SUFFIX = ""
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        자격증명 유효성 검증
        
        Returns:
            (is_valid, errors): 유효성 여부와 오류 목록
        """
        errors = []
        
        # 필수 키 검증
        required_keys = {
            'KIWOOM_REST_APPKEY': self.KIWOOM_REST_APPKEY,
            'KIWOOM_REST_SECRETKEY': self.KIWOOM_REST_SECRETKEY,
            'ACCOUNT_NUMBER': self.ACCOUNT_NUMBER,
        }
        
        for key, value in required_keys.items():
            if not value or len(value) < 10:
                errors.append(f"{key}가 설정되지 않았거나 유효하지 않습니다")
        
        # 계좌번호 형식 검증
        if self.ACCOUNT_NUMBER and '-' not in self.ACCOUNT_NUMBER:
            errors.append(
                f"ACCOUNT_NUMBER는 '계좌번호-접미사' 형식이어야 합니다: '{self.ACCOUNT_NUMBER}'"
            )
        
        # Gemini API 키 검증 (선택사항이지만 권장)
        if not self.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY가 설정되지 않았습니다 (AI 분석 사용 불가)")
        
        return len(errors) == 0, errors
    
    def get_kiwoom_config(self) -> Dict[str, str]:
        """Kiwoom API 설정 반환"""
        return {
            'base_url': self.KIWOOM_REST_BASE_URL,
            'appkey': self.KIWOOM_REST_APPKEY,
            'secretkey': self.KIWOOM_REST_SECRETKEY,
            'account_number': self.ACCOUNT_NUMBER,
            'account_prefix': self.ACCOUNT_PREFIX,
            'account_suffix': self.ACCOUNT_SUFFIX,
            'websocket_url': self.KIWOOM_WEBSOCKET_URL,
        }
    
    def get_gemini_config(self) -> Dict[str, str]:
        """Gemini API 설정 반환"""
        return {
            'api_key': self.GEMINI_API_KEY,
            'model_name': self.GEMINI_MODEL_NAME,
        }
    
    def get_telegram_config(self) -> Dict[str, str]:
        """Telegram 설정 반환"""
        return {
            'bot_token': self.TELEGRAM_BOT_TOKEN,
            'chat_id': self.TELEGRAM_CHAT_ID,
        }

# 싱글톤 인스턴스
_credentials_instance: Optional[Credentials] = None

def get_credentials() -> Credentials:
    """자격증명 싱글톤 인스턴스 반환"""
    global _credentials_instance
    if _credentials_instance is None:
        _credentials_instance = Credentials()
    return _credentials_instance

# 하위 호환성을 위한 변수 (기존 코드와의 호환)
credentials = get_credentials()
KIWOOM_REST_BASE_URL = credentials.KIWOOM_REST_BASE_URL
KIWOOM_REST_APPKEY = credentials.KIWOOM_REST_APPKEY
KIWOOM_REST_SECRETKEY = credentials.KIWOOM_REST_SECRETKEY
ACCOUNT_NUMBER = credentials.ACCOUNT_NUMBER
KIWOOM_WEBSOCKET_URL = credentials.KIWOOM_WEBSOCKET_URL
GEMINI_API_KEY = credentials.GEMINI_API_KEY
GEMINI_MODEL_NAME = credentials.GEMINI_MODEL_NAME

__all__ = ['Credentials', 'get_credentials', 'credentials']