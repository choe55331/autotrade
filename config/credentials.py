"""
config/credentials.py
API 키 및 민감정보 관리
"""

"""
로딩 우선순위:
1. _immutable/credentials/secrets.json (최우선)
2. 환경변수 (.env)
3. 기본값
"""
import os
import json
from pathlib import Path
from typing import Dict, Optional, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).parent.parent
SECRETS_FILE = PROJECT_ROOT / '_immutable' / 'credentials' / 'secrets.json'


class Credentials:
    """API 자격증명 관리 클래스"""

    def __init__(self):
        secrets = self._load_secrets()

        if not secrets:
            raise FileNotFoundError(
                f"\n{'='*80}\n"
                f"❌ secrets.json 파일이 없습니다!\n"
                f"{'='*80}\n"
                f"다음 명령어를 실행하여 API 키를 설정하세요:\n\n"
                f"  python setup_secrets.py\n\n"
                f"또는 수동으로 설정:\n"
                f"  1. cp _immutable/credentials/secrets.example.json _immutable/credentials/secrets.json\n"
                f"  2. secrets.json 파일을 열어서 실제 API 키를 입력\n"
                f"  3. chmod 400 _immutable/credentials/secrets.json (읽기 전용 설정)\n"
                f"{'='*80}\n"
            )

        kiwoom = secrets.get('kiwoom_rest', {})
        self.KIWOOM_REST_BASE_URL = kiwoom.get('base_url')
        self.KIWOOM_REST_APPKEY = kiwoom.get('appkey')
        self.KIWOOM_REST_SECRETKEY = kiwoom.get('secretkey')
        self.ACCOUNT_NUMBER = kiwoom.get('account_number')

        kiwoom_ws = secrets.get('kiwoom_websocket', {})
        self.KIWOOM_WEBSOCKET_URL = kiwoom_ws.get('url')

        gemini = secrets.get('gemini', {})
        self.GEMINI_API_KEY = gemini.get('api_key')
        self.GEMINI_MODEL_NAME = gemini.get('model_name')
        self.GEMINI_ENABLE_CROSS_CHECK = gemini.get('enable_cross_check', False)

        telegram = secrets.get('telegram', {})
        self.TELEGRAM_BOT_TOKEN = telegram.get('bot_token', '')
        self.TELEGRAM_CHAT_ID = telegram.get('chat_id', '')

        self._parse_account_number()

    def _load_secrets(self) -> Dict:
        """secrets.json 파일 로드"""
        if not SECRETS_FILE.exists():
            return {}

        try:
            with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ secrets.json 로드 실패, 환경변수 사용: {e}")
            return {}
    
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
        
        required_keys = {
            'KIWOOM_REST_APPKEY': self.KIWOOM_REST_APPKEY,
            'KIWOOM_REST_SECRETKEY': self.KIWOOM_REST_SECRETKEY,
            'ACCOUNT_NUMBER': self.ACCOUNT_NUMBER,
        }
        
        for key, value in required_keys.items():
            if not value or len(value) < 10:
                errors.append(f"{key}가 설정되지 않았거나 유효하지 않습니다")
        
        if self.ACCOUNT_NUMBER and '-' not in self.ACCOUNT_NUMBER:
            errors.append(
                f"ACCOUNT_NUMBER는 '계좌번호-접미사' 형식이어야 합니다: '{self.ACCOUNT_NUMBER}'"
            )
        
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
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """Gemini API 설정 반환"""
        return {
            'api_key': self.GEMINI_API_KEY,
            'model_name': self.GEMINI_MODEL_NAME,
            'enable_cross_check': self.GEMINI_ENABLE_CROSS_CHECK,
        }
    
    def get_telegram_config(self) -> Dict[str, str]:
        """Telegram 설정 반환"""
        return {
            'bot_token': self.TELEGRAM_BOT_TOKEN,
            'chat_id': self.TELEGRAM_CHAT_ID,
        }

_credentials_instance: Optional[Credentials] = None

def get_credentials() -> Credentials:
    """자격증명 싱글톤 인스턴스 반환"""
    global _credentials_instance
    if _credentials_instance is None:
        _credentials_instance = Credentials()
    return _credentials_instance

credentials = get_credentials()
KIWOOM_REST_BASE_URL = credentials.KIWOOM_REST_BASE_URL
KIWOOM_REST_APPKEY = credentials.KIWOOM_REST_APPKEY
KIWOOM_REST_SECRETKEY = credentials.KIWOOM_REST_SECRETKEY
ACCOUNT_NUMBER = credentials.ACCOUNT_NUMBER
KIWOOM_WEBSOCKET_URL = credentials.KIWOOM_WEBSOCKET_URL
GEMINI_API_KEY = credentials.GEMINI_API_KEY
GEMINI_MODEL_NAME = credentials.GEMINI_MODEL_NAME
GEMINI_ENABLE_CROSS_CHECK = credentials.GEMINI_ENABLE_CROSS_CHECK

__all__ = ['Credentials', 'get_credentials', 'credentials']