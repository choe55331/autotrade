"""
core/rest_client.py
키움증권 REST API 클라이언트 (최적화 버전)
"""
import requests
import json
import datetime
import time
import threading
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional

from .exceptions import (
    AuthenticationError,
    TokenExpiredError,
    RateLimitError,
    NetworkError,
    InvalidResponseError,
)

logger = logging.getLogger(__name__)


class KiwoomRESTClient:
    """
    키움증권 REST API 클라이언트 (싱글톤 패턴)
    
    주요 기능:
    - 자동 토큰 관리 (발급, 갱신, 만료 처리)
    - API 호출 속도 제한
    - 자동 재시도
    - 스레드 안전
    """
    
    _instance: Optional['KiwoomRESTClient'] = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """클라이언트 초기화"""
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            logger.info("KiwoomRESTClient 초기화 중 (싱글톤)")
            
            # 설정 로드
            self._load_config()
            
            # HTTP 세션 생성
            self.session = self._create_session()
            
            # 토큰 관리
            self.token: Optional[str] = None
            self.token_expiry: datetime.datetime = datetime.datetime.now()
            
            # 속도 제한 관리
            self.rate_limit_lock = threading.Lock()
            self.min_call_interval = 0.3  # config에서 가져오도록 수정 가능
            self.last_call_time = 0.0
            
            # 에러 메시지
            self.last_error_msg: Optional[str] = None
            
            # 초기 토큰 발급
            self._initialize_token()
            
            self._initialized = True
            logger.info("KiwoomRESTClient 초기화 완료")
    
    def _load_config(self):
        """설정 로드 및 검증"""
        try:
            from config import get_credentials, API_RATE_LIMIT, get_config

            credentials = get_credentials()
            kiwoom_config = credentials.get_kiwoom_config()

            self.base_url = kiwoom_config['base_url']
            self.appkey = kiwoom_config['appkey']
            self.appsecret = kiwoom_config['secretkey']
            self.account_number_full = kiwoom_config['account_number']
            self.account_prefix = kiwoom_config['account_prefix']
            self.account_suffix = kiwoom_config['account_suffix']

            # API 속도 제한 설정
            self.min_call_interval = API_RATE_LIMIT.get('REST_CALL_INTERVAL', 0.3)
            self.max_retries = API_RATE_LIMIT.get('REST_MAX_RETRIES', 3)
            self.retry_backoff = API_RATE_LIMIT.get('REST_RETRY_BACKOFF', 1.0)

            # 테스트 모드 설정
            try:
                config = get_config()
                self.test_mode = config.get('development', {}).get('test_mode', False)
            except:
                self.test_mode = False

            mode_str = "테스트 모드 (Mock API)" if self.test_mode else "실전 모드 (Real API)"
            logger.info(f"계좌번호: {self.account_prefix}-{self.account_suffix} - {mode_str}")
        except ImportError:
            # config 모듈이 없을 경우 기본값 사용
            logger.warning("config 모듈을 찾을 수 없습니다. 기본값을 사용합니다.")
            self.base_url = "https://api.kiwoom.com"
            self.appkey = ""
            self.appsecret = ""
            self.account_number_full = ""
            self.account_prefix = ""
            self.account_suffix = ""
            self.min_call_interval = 0.3
            self.max_retries = 3
            self.retry_backoff = 1.0
            self.test_mode = False
    
    def _create_session(self) -> requests.Session:
        """재시도 기능이 있는 HTTP 세션 생성"""
        session = requests.Session()

        # 500 에러는 재시도하지 않음 (서버 측 문제이므로 즉시 확인 필요)
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 502, 503, 504],  # 500 제거
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"],
            backoff_factor=self.retry_backoff
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        logger.info("HTTP 세션 생성 완료 (자동 재시도 활성화)")
        return session
    
    def _initialize_token(self):
        """초기 토큰 발급"""
        try:
            if not self._get_token():
                logger.warning(f"초기 API 토큰 발급 실패: {self.last_error_msg}")
            else:
                logger.info("초기 토큰 발급 성공")
        except Exception as e:
            logger.error(f"토큰 초기화 실패: {e}")
    
    def _is_token_valid(self) -> bool:
        """토큰 유효성 확인"""
        if not self.token:
            return False

        # 만료 5분 전까지 유효한 것으로 간주 (여유 시간 증가)
        # 이전: 1분 전 -> 갱신 실패 시 토큰 만료 위험
        # 개선: 5분 전 -> 갱신 실패해도 재시도 시간 확보
        buffer_time = datetime.timedelta(minutes=5)
        return datetime.datetime.now() < (self.token_expiry - buffer_time)
    
    def _get_token(self, retry_count: int = 0, max_retries: int = 3) -> bool:
        """
        API 토큰 발급/갱신 (재시도 로직 포함)

        Args:
            retry_count: 현재 재시도 횟수
            max_retries: 최대 재시도 횟수

        Returns:
            성공 여부
        """
        # 기존 토큰이 유효하면 재사용
        if self._is_token_valid():
            logger.debug(f"기존 토큰 사용 (만료: {self.token_expiry.strftime('%Y-%m-%d %H:%M:%S')})")
            return True

        # 테스트 모드: 실제 API 호출 스킵, Mock 토큰 사용
        if self.test_mode:
            logger.info("🧪 테스트 모드: API 토큰 발급 스킵 (Mock 토큰 사용)")
            self.token = "TEST_MOCK_TOKEN_FOR_DEVELOPMENT"
            self.token_expiry = datetime.datetime.now() + datetime.timedelta(days=1)
            self.last_error_msg = None
            return True

        retry_suffix = f" (재시도 {retry_count}/{max_retries})" if retry_count > 0 else ""
        logger.info(f"API 토큰 발급 시도{retry_suffix}...")

        token_url = f"{self.base_url}/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "secretkey": self.appsecret
        }
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "api-id": "au10001",
            "User-Agent": "KiwoomTradingBot/1.0"
        }

        try:
            res = self.session.post(
                token_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )

            logger.debug(f"토큰 요청 응답 상태: {res.status_code}")

            if res.status_code != 200:
                error_data = self._parse_error_response(res)
                self._set_error(f"토큰 발급 실패 ({res.status_code}): {error_data}")
                logger.error(f"토큰 요청 URL: {token_url}")
                logger.error(f"토큰 요청 본문: appkey={self.appkey[:10]}..., secretkey={self.appsecret[:10]}...")
                logger.error(f"응답 내용: {res.text[:500]}")

                # 재시도 로직 (네트워크 일시 오류 대응)
                if retry_count < max_retries and res.status_code in [500, 502, 503, 504]:
                    wait_time = 2 ** retry_count  # 지수 백오프: 1초, 2초, 4초
                    logger.warning(f"서버 오류 - {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                    return self._get_token(retry_count + 1, max_retries)

                return False

            token_data = res.json()
            success = self._process_token_response(token_data)

            # 토큰 발급 성공 시 재시도 카운터 리셋
            if success and retry_count > 0:
                logger.info(f"✅ 토큰 발급 성공 (재시도 {retry_count}회 만에 성공)")

            return success

        except requests.exceptions.Timeout:
            self._set_error("토큰 요청 시간 초과")

            # 타임아웃 시 재시도
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                logger.warning(f"타임아웃 - {wait_time}초 후 재시도...")
                time.sleep(wait_time)
                return self._get_token(retry_count + 1, max_retries)

            return False

        except requests.exceptions.RequestException as e:
            self._set_error(f"토큰 요청 네트워크 오류: {e}")

            # 네트워크 오류 시 재시도
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                logger.warning(f"네트워크 오류 - {wait_time}초 후 재시도...")
                time.sleep(wait_time)
                return self._get_token(retry_count + 1, max_retries)

            return False

        except Exception as e:
            self._set_error(f"토큰 발급 중 예외: {e}")
            logger.exception("토큰 발급 중 예외 발생")
            return False
    
    def _process_token_response(self, token_data: Dict[str, Any]) -> bool:
        """토큰 응답 처리 (한국투자증권 OpenAPI 형식)"""
        # 한국투자증권은 'token' 필드 사용 (access_token 아님)
        access_token = token_data.get('access_token') or token_data.get('token')
        expires_dt_str = token_data.get('access_token_token_expired') or token_data.get('expires_dt')
        
        if not access_token or not expires_dt_str:
            error_msg = token_data.get('return_msg', '알 수 없는 토큰 응답')
            error_code = token_data.get('return_code', 'N/A')
            self._set_error(f"토큰 발급 실패 ({error_code}): {error_msg}")
            return False
        
        try:
            self.token = access_token
            self.token_expiry = datetime.datetime.strptime(expires_dt_str, '%Y%m%d%H%M%S')
            
            logger.info(f"토큰 발급 성공 (만료: {self.token_expiry.strftime('%Y-%m-%d %H:%M:%S')})")
            self.last_error_msg = None
            return True
        
        except ValueError as e:
            self._set_error(f"토큰 만료 시간 파싱 실패: {expires_dt_str}")
            self.token = None
            return False
    
    def _revoke_token(self):
        """API 토큰 폐기"""
        if not self.token:
            logger.info("폐기할 토큰이 없습니다")
            return
        
        logger.info("API 토큰 폐기 시도...")
        
        revoke_url = f"{self.base_url}/oauth2/revoke"
        payload = {
            "appkey": self.appkey,
            "secretkey": self.appsecret,
            "token": self.token
        }
        headers = {"content-type": "application/json;charset=UTF-8"}
        
        try:
            res = self.session.post(
                revoke_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=5
            )
            
            if res.status_code == 200:
                revoke_data = res.json()
                if revoke_data.get("return_code") == 0:
                    logger.info("토큰 폐기 성공")
                else:
                    logger.warning(f"토큰 폐기 실패: {revoke_data.get('return_msg')}")
            else:
                logger.warning(f"토큰 폐기 요청 실패 ({res.status_code})")
        
        except Exception as e:
            logger.error(f"토큰 폐기 중 오류: {e}")
        
        finally:
            self.token = None
    
    def _handle_rate_limit(self):
        """API 호출 속도 제한 처리"""
        with self.rate_limit_lock:
            current_time = time.monotonic()
            elapsed = current_time - self.last_call_time
            wait_time = self.min_call_interval - elapsed
            
            if wait_time > 0:
                logger.debug(f"API 속도 제한: {wait_time:.3f}초 대기")
                time.sleep(wait_time)
            
            self.last_call_time = time.monotonic()
    
    def _set_error(self, msg: str):
        """에러 메시지 설정"""
        self.last_error_msg = msg
        logger.error(msg)
    
    def _parse_error_response(self, res: requests.Response) -> str:
        """에러 응답 파싱"""
        try:
            return str(res.json())
        except:
            return res.text[:200]
    
    def request(
        self,
        api_id: str,
        body: Dict[str, Any],
        path: str,
        http_method: str = "POST"
    ) -> Optional[Dict[str, Any]]:
        """
        API 요청 실행 (자동 토큰 관리)
        
        Args:
            api_id: API ID
            body: 요청 본문
            path: API 경로
            http_method: HTTP 메서드
        
        Returns:
            API 응답 딕셔너리
        """
        # 토큰 유효성 확인 및 갱신
        if not self._is_token_valid():
            if not self._get_token():
                logger.error(f"API 호출 실패 ({api_id}): 토큰 갱신 불가")
                return {
                    "return_code": -401,
                    "return_msg": f"토큰 갱신 실패: {self.last_error_msg}"
                }
        
        return self._execute_request(api_id, body, path, http_method, retry_on_auth=True)
    
    def _execute_request(
        self,
        api_id: str,
        body: Dict[str, Any],
        path: str,
        http_method: str,
        retry_on_auth: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        실제 API 요청 실행
        
        Args:
            api_id: API ID
            body: 요청 본문
            path: API 경로
            http_method: HTTP 메서드
            retry_on_auth: 401 에러 시 재시도 여부
        
        Returns:
            API 응답 딕셔너리
        """
        # 속도 제한 처리
        self._handle_rate_limit()
        
        # 헤더 구성
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {self.token}",
            "api-id": api_id
        }
        
        # URL 구성
        if not path.startswith("/"):
            path = "/" + path
        url = f"{self.base_url}{path}"
        
        logger.debug(f"[REST] {http_method} {url} (API ID: {api_id})")
        
        try:
            # 요청 본문 준비
            request_body_json = json.dumps(body, ensure_ascii=False) if body else None
            
            # HTTP 요청 실행
            start_time = time.monotonic()
            
            if http_method.upper() == "POST":
                res = self.session.post(url, headers=headers, data=request_body_json, timeout=10)
            elif http_method.upper() == "GET":
                res = self.session.get(url, headers=headers, params=body, timeout=10)
            else:
                return {
                    "return_code": -101,
                    "return_msg": f"지원하지 않는 HTTP 메서드: {http_method}"
                }
            
            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.info(f"[REST 응답] {api_id} - 상태:{res.status_code}, 지연:{elapsed_ms:.2f}ms")

            # 에러 상태 코드일 경우 상세 로그
            if res.status_code >= 400:
                logger.error(f"API 에러 응답 ({api_id}):")
                logger.error(f"  URL: {url}")
                logger.error(f"  상태 코드: {res.status_code}")
                logger.error(f"  요청 본문: {body}")
                logger.error(f"  응답 헤더: {dict(res.headers)}")
                logger.error(f"  응답 본문: {res.text[:1000]}")

            # 401 에러 처리 (토큰 갱신 후 재시도)
            if res.status_code == 401 and retry_on_auth:
                logger.warning(f"401 에러 - 토큰 갱신 후 재시도 ({api_id})")
                self.token = None
                
                if self._get_token():
                    return self._execute_request(api_id, body, path, http_method, retry_on_auth=False)
                else:
                    return {
                        "return_code": -401,
                        "return_msg": f"재시도 실패: {self.last_error_msg}"
                    }
            
            # HTTP 에러 확인
            res.raise_for_status()
            
            # 응답 파싱
            return self._process_api_response(res, api_id)
        
        except requests.exceptions.Timeout:
            logger.error(f"API 요청 시간 초과 ({api_id})")
            return {"return_code": -102, "return_msg": "API 요청 시간 초과"}
        
        except requests.exceptions.HTTPError as e:
            error_text = e.response.text[:200]
            logger.error(f"HTTP 오류 ({api_id}): {e.response.status_code} - {error_text}")
            return {
                "return_code": f"-{e.response.status_code}",
                "return_msg": f"HTTP 오류: {e.response.reason}",
                "error_detail": error_text
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"네트워크 오류 ({api_id}): {e}")
            return {"return_code": -103, "return_msg": f"네트워크 오류: {e}"}
        
        except Exception as e:
            logger.error(f"예외 발생 ({api_id}): {e}", exc_info=True)
            return {"return_code": -104, "return_msg": f"내부 오류: {e}"}
    
    def _process_api_response(self, res: requests.Response, api_id: str) -> Dict[str, Any]:
        """API 응답 처리"""
        try:
            result_data = res.json()
        except json.JSONDecodeError:
            logger.error(f"JSON 파싱 실패 ({api_id}): {res.text[:200]}")
            return {
                "return_code": -999,
                "return_msg": "응답 JSON 파싱 실패",
                "response_text": res.text[:200]
            }
        
        return_code = result_data.get('return_code', 0)
        return_msg = result_data.get('return_msg', '메시지 없음')

        if return_code != 0:
            logger.warning(f"API 로직 오류 ({api_id}): {return_msg} (코드: {return_code})")
            logger.debug(f"전체 응답: {result_data}")
        else:
            logger.info(f"API 호출 성공 ({api_id})")
            # output 데이터 유무 로깅
            if 'output' in result_data:
                output_data = result_data['output']
                if isinstance(output_data, list):
                    logger.debug(f"  output: 리스트 {len(output_data)}개 항목")
                elif isinstance(output_data, dict):
                    logger.debug(f"  output: 딕셔너리 {len(output_data)}개 키")
                else:
                    logger.debug(f"  output: {type(output_data)}")

        return result_data
    
    def get_account_info(self) -> Dict[str, Any]:
        """계좌 정보 반환"""
        return {
            'account_number': self.account_number_full,
            'account_prefix': self.account_prefix,
            'account_suffix': self.account_suffix,
        }
    
    def close(self):
        """클라이언트 종료 (토큰 폐기)"""
        logger.info("REST 클라이언트 종료 중...")
        self._revoke_token()
        self.session.close()
        logger.info("REST 클라이언트 종료 완료")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()


__all__ = ['KiwoomRESTClient']