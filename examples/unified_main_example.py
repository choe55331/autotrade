"""
64비트 REST API + 32비트 koapy 통합 예제

이 파일 하나로 모든 것이 가능합니다:
- 64비트 Python으로 실행
- FastAPI REST API 서버
- koapy로 키움 Open API 연동 (자동으로 32비트 서버 실행)

실행:
    python unified_main_example.py

    브라우저에서:
    http://localhost:8000/docs
"""
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

# 프로젝트 루트 경로
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# koapy 전역 컨텍스트 (앱 시작 시 한 번만 생성)
koapy_context = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 koapy 초기화/정리"""
    global koapy_context

    print("=" * 80)
    print("🚀 서버 시작 중...")
    print("=" * 80)
    print()

    # Python 비트 확인
    import struct
    bits = struct.calcsize("P") * 8
    print(f"✓ Python: {bits}-bit")

    # koapy 초기화
    try:
        from koapy import KiwoomOpenApiPlusEntrypoint

        print("✓ koapy 로드 성공")
        print("✓ 32비트 서버 자동 실행 중...")

        koapy_context = KiwoomOpenApiPlusEntrypoint()

        # 로그인 (선택사항 - credential 설정 시 자동 로그인)
        # koapy_context.EnsureConnected()

        print("✓ koapy 초기화 완료")
        print()
        print("✅ 서버 준비 완료!")
        print("   - REST API: http://localhost:8000")
        print("   - API Docs: http://localhost:8000/docs")
        print("   - koapy gRPC: localhost:5943")
        print()

    except ImportError:
        print("⚠️  koapy가 설치되지 않았습니다.")
        print("   설치: pip install koapy")
        print("   일부 기능이 제한될 수 있습니다.")
        koapy_context = None
    except Exception as e:
        print(f"⚠️  koapy 초기화 실패: {e}")
        koapy_context = None

    yield  # 앱 실행

    # 종료 시 정리
    print("\n🛑 서버 종료 중...")
    if koapy_context:
        try:
            koapy_context.close()
            print("✓ koapy 정리 완료")
        except:
            pass


# FastAPI 앱 생성
app = FastAPI(
    title="Autotrade API",
    description="64비트 REST API + 32비트 koapy 통합",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# REST API 엔드포인트
# ============================================================================

@app.get("/")
async def root():
    """루트 엔드포인트"""
    import struct
    bits = struct.calcsize("P") * 8

    return {
        "message": "Autotrade API",
        "python_bits": f"{bits}-bit",
        "koapy_available": koapy_context is not None,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "koapy": "connected" if koapy_context else "not initialized"
    }


@app.post("/login")
async def login(user_id: Optional[str] = None,
                user_password: Optional[str] = None,
                cert_password: Optional[str] = None,
                is_simulation: bool = True):
    """키움 로그인

    Args:
        user_id: 키움증권 ID (선택사항)
        user_password: 비밀번호 (선택사항)
        cert_password: 공인인증서 비밀번호 (선택사항)
        is_simulation: 모의투자 여부

    Returns:
        로그인 성공 여부
    """
    if not koapy_context:
        raise HTTPException(status_code=503, detail="koapy가 초기화되지 않았습니다")

    try:
        # Credential 구성
        credential = None
        if user_id and user_password and cert_password:
            credential = {
                'user_id': user_id,
                'user_password': user_password,
                'cert_password': cert_password,
                'is_simulation': is_simulation
            }

        # 로그인
        koapy_context.EnsureConnected(credential)

        # 연결 상태 확인
        state = koapy_context.GetConnectState()

        if state == 1:
            # 계좌 목록 가져오기
            accounts = koapy_context.GetAccountList()

            return {
                "success": True,
                "message": "로그인 성공",
                "accounts": accounts
            }
        else:
            raise HTTPException(status_code=401, detail="로그인 실패")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 오류: {str(e)}")


@app.get("/accounts")
async def get_accounts():
    """계좌 목록 조회"""
    if not koapy_context:
        raise HTTPException(status_code=503, detail="koapy가 초기화되지 않았습니다")

    try:
        # 연결 확인
        state = koapy_context.GetConnectState()
        if state != 1:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")

        accounts = koapy_context.GetAccountList()

        return {
            "success": True,
            "accounts": accounts
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/{code}")
async def get_stock_info(code: str):
    """주식 기본 정보 조회

    Args:
        code: 종목코드 (예: 005930)

    Returns:
        주식 기본 정보
    """
    if not koapy_context:
        raise HTTPException(status_code=503, detail="koapy가 초기화되지 않았습니다")

    try:
        # 연결 확인
        state = koapy_context.GetConnectState()
        if state != 1:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")

        # 기본 정보 조회
        info = koapy_context.GetStockBasicInfoAsDict(code)

        # 추가 정보
        name = koapy_context.GetMasterCodeName(code)
        price = koapy_context.GetMasterLastPrice(code)

        return {
            "success": True,
            "code": code,
            "name": name,
            "current_price": price,
            "info": info
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stock/{code}/daily")
async def get_daily_data(code: str, days: int = 20):
    """일별 주가 데이터 조회

    Args:
        code: 종목코드
        days: 조회 일수 (기본: 20일)

    Returns:
        일별 주가 데이터
    """
    if not koapy_context:
        raise HTTPException(status_code=503, detail="koapy가 초기화되지 않았습니다")

    try:
        state = koapy_context.GetConnectState()
        if state != 1:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")

        # DataFrame으로 조회
        df = koapy_context.GetDailyStockDataAsDataFrame(code, adjusted_price=True)

        # 상위 N일만
        df = df.head(days)

        # JSON 변환
        data = df.to_dict('records')

        return {
            "success": True,
            "code": code,
            "days": days,
            "data": data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/account/{account_no}/balance")
async def get_balance(account_no: str):
    """계좌 예수금 조회

    Args:
        account_no: 계좌번호

    Returns:
        예수금 정보
    """
    if not koapy_context:
        raise HTTPException(status_code=503, detail="koapy가 초기화되지 않았습니다")

    try:
        state = koapy_context.GetConnectState()
        if state != 1:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")

        # 예수금 조회
        deposit = koapy_context.GetDepositInfo(account_no)

        return {
            "success": True,
            "account_no": account_no,
            "deposit": deposit
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/account/{account_no}/stocks")
async def get_holdings(account_no: str):
    """계좌 보유 종목 조회

    Args:
        account_no: 계좌번호

    Returns:
        보유 종목 목록
    """
    if not koapy_context:
        raise HTTPException(status_code=503, detail="koapy가 초기화되지 않았습니다")

    try:
        state = koapy_context.GetConnectState()
        if state != 1:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")

        # 보유 종목 조회
        stocks = koapy_context.GetAccountStockInfo(account_no)

        return {
            "success": True,
            "account_no": account_no,
            "stocks": stocks or []
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 메인 실행
# ============================================================================

def main():
    """메인 함수"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║              🚀 Autotrade API Server                                     ║
║                                                                          ║
║  64비트 REST API + 32비트 koapy 통합 서버                                 ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

    # 서버 실행
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
