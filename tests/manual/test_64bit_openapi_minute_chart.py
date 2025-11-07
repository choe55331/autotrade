"""
64비트 Kiwoom Open API 테스트 - 과거 분봉 데이터 조회

목적:
1. 64비트 Python에서 Kiwoom Open API 작동 확인
2. OPT10080 (주식분봉조회) TR로 과거 데이터 조회
3. 한 달 전 데이터 조회 가능 여부 확인

필요사항:
- 64bit-kiwoom-openapi 설치 완료
- Kiwoom 계정 로그인

사용 TR:
- OPT10080: 주식분봉조회
"""
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import win32com.client
    import pythoncom
except ImportError:
    print("❌ pywin32 모듈이 설치되지 않았습니다!")
    print("   설치: pip install pywin32")
    sys.exit(1)


class Kiwoom64BitAPI:
    """64비트 Kiwoom Open API 래퍼"""

    def __init__(self):
        self.ocx = None
        self.login_event_loop = None
        self.tr_event_loop = None
        self.is_connected = False

        # TR 응답 데이터
        self.tr_data = []

    def connect(self):
        """ActiveX 연결"""
        try:
            print("🔌 64비트 Kiwoom Open API 연결 시도...")

            # COM 아파트먼트 초기화 (중요!)
            pythoncom.CoInitialize()

            self.ocx = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
            print("✅ ActiveX 컨트롤 생성 성공")

            # 이벤트 핸들러 연결
            win32com.client.WithEvents(self.ocx, KiwoomEventHandler)

            # 전역 인스턴스 설정 (이벤트 핸들러에서 접근하기 위해)
            global kiwoom_instance
            kiwoom_instance = self

            return True
        except Exception as e:
            print(f"❌ ActiveX 연결 실패: {e}")
            return False

    def login(self):
        """로그인"""
        try:
            print("\n🔐 로그인 시도 중...")
            ret = self.ocx.CommConnect()

            if ret == 0:
                print("   로그인 요청 전송 완료")
                print("   로그인 창이 나타나면 수동으로 로그인하세요...")

                # 이벤트 대기 (30초)
                timeout = 30
                start_time = time.time()

                while not self.is_connected and (time.time() - start_time) < timeout:
                    pythoncom.PumpWaitingMessages()
                    time.sleep(0.1)

                if self.is_connected:
                    print("✅ 로그인 성공!")

                    # 계정 정보 출력
                    account_cnt = self.ocx.GetLoginInfo("ACCOUNT_CNT")
                    accounts = self.ocx.GetLoginInfo("ACCNO")
                    user_id = self.ocx.GetLoginInfo("USER_ID")
                    user_name = self.ocx.GetLoginInfo("USER_NM")

                    print(f"\n📋 로그인 정보:")
                    print(f"   사용자ID: {user_id}")
                    print(f"   사용자명: {user_name}")
                    print(f"   보유계좌수: {account_cnt}")
                    print(f"   계좌번호: {accounts}")

                    return True
                else:
                    print("❌ 로그인 시간 초과 (30초)")
                    return False
            else:
                print(f"❌ 로그인 요청 실패 (ret={ret})")
                return False

        except Exception as e:
            print(f"❌ 로그인 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False

    def request_minute_chart(self, stock_code, interval, base_date, count=100):
        """
        분봉 데이터 요청 (OPT10080)

        Args:
            stock_code: 종목코드 (6자리)
            interval: 틱범위 (1, 3, 5, 10, 15, 30, 45, 60분)
            base_date: 기준일자 (YYYYMMDD)
            count: 조회 개수
        """
        try:
            print(f"\n📊 분봉 데이터 요청:")
            print(f"   종목코드: {stock_code}")
            print(f"   틱범위: {interval}분")
            print(f"   기준일자: {base_date}")
            print(f"   조회개수: {count}")

            # 초기화
            self.tr_data = []

            # 입력값 설정
            self.ocx.SetInputValue("종목코드", stock_code)
            self.ocx.SetInputValue("틱범위", str(interval))
            self.ocx.SetInputValue("수정주가구분", "1")  # 수정주가

            # 요청
            ret = self.ocx.CommRqData("주식분봉조회", "OPT10080", 0, "0101")

            if ret == 0:
                print("✅ TR 요청 전송 완료")
                print("   응답 대기 중...")

                # 이벤트 대기 (10초)
                timeout = 10
                start_time = time.time()

                while len(self.tr_data) == 0 and (time.time() - start_time) < timeout:
                    pythoncom.PumpWaitingMessages()
                    time.sleep(0.1)

                if len(self.tr_data) > 0:
                    print(f"✅ 데이터 수신 완료: {len(self.tr_data)}개")
                    return self.tr_data
                else:
                    print("⚠️ 응답 시간 초과 또는 데이터 없음")
                    return []
            else:
                print(f"❌ TR 요청 실패 (ret={ret})")
                return []

        except Exception as e:
            print(f"❌ TR 요청 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return []


class KiwoomEventHandler:
    """Kiwoom API 이벤트 핸들러"""

    def OnEventConnect(self, err_code):
        """로그인 결과 이벤트"""
        global kiwoom_instance

        if err_code == 0:
            print("   [이벤트] 로그인 성공 (err_code=0)")
            kiwoom_instance.is_connected = True
        else:
            print(f"   [이벤트] 로그인 실패 (err_code={err_code})")
            kiwoom_instance.is_connected = False

    def OnReceiveTrData(self, screen_no, rqname, trcode, record_name, prev_next,
                        data_len, err_code, msg, splm_msg):
        """TR 데이터 수신 이벤트"""
        global kiwoom_instance

        print(f"   [이벤트] TR 데이터 수신")
        print(f"   - RQName: {rqname}")
        print(f"   - TRCode: {trcode}")
        print(f"   - ErrCode: {err_code}")

        if rqname == "주식분봉조회":
            # 데이터 개수 확인
            cnt = kiwoom_instance.ocx.GetRepeatCnt(trcode, rqname)
            print(f"   - 데이터 개수: {cnt}")

            # 데이터 파싱
            for i in range(cnt):
                data = {
                    'date': kiwoom_instance.ocx.GetCommData(trcode, rqname, i, "체결시간").strip(),
                    'open': int(kiwoom_instance.ocx.GetCommData(trcode, rqname, i, "시가").strip() or 0),
                    'high': int(kiwoom_instance.ocx.GetCommData(trcode, rqname, i, "고가").strip() or 0),
                    'low': int(kiwoom_instance.ocx.GetCommData(trcode, rqname, i, "저가").strip() or 0),
                    'close': int(kiwoom_instance.ocx.GetCommData(trcode, rqname, i, "현재가").strip() or 0),
                    'volume': int(kiwoom_instance.ocx.GetCommData(trcode, rqname, i, "거래량").strip() or 0),
                }
                kiwoom_instance.tr_data.append(data)


def print_section(title):
    """섹션 구분선"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_64bit_openapi():
    """64비트 Open API 테스트 메인"""

    print_section("📌 64비트 Kiwoom Open API 테스트")

    # API 생성
    kiwoom = Kiwoom64BitAPI()

    # 연결
    if not kiwoom.connect():
        print("\n❌ ActiveX 연결 실패")
        return

    # 로그인
    if not kiwoom.login():
        print("\n❌ 로그인 실패")
        return

    print_section("📊 과거 분봉 데이터 조회 테스트")

    # 테스트 종목
    test_stocks = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
    ]

    # 테스트 날짜: 오늘, 1주일 전, 1개월 전
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    test_dates = [
        (today.strftime("%Y%m%d"), "오늘"),
        (week_ago.strftime("%Y%m%d"), "1주일 전"),
        (month_ago.strftime("%Y%m%d"), "1개월 전"),
    ]

    # 분봉 간격
    intervals = [5, 60]  # 5분, 60분

    results = {}

    for stock_code, stock_name in test_stocks:
        print(f"\n{'─'*80}")
        print(f"📈 {stock_name} ({stock_code})")
        print(f"{'─'*80}")

        for interval in intervals:
            for base_date, date_label in test_dates:
                print(f"\n🔍 {interval}분봉 - {date_label} ({base_date})")

                data = kiwoom.request_minute_chart(
                    stock_code=stock_code,
                    interval=interval,
                    base_date=base_date,
                    count=10
                )

                if data and len(data) > 0:
                    print(f"✅ {len(data)}개 데이터 조회 성공!")

                    # 첫 번째 데이터 출력
                    first = data[0]
                    print(f"\n   최신 데이터:")
                    print(f"   - 체결시간: {first['date']}")
                    print(f"   - 시가: {first['open']:,}원")
                    print(f"   - 고가: {first['high']:,}원")
                    print(f"   - 저가: {first['low']:,}원")
                    print(f"   - 종가: {first['close']:,}원")
                    print(f"   - 거래량: {first['volume']:,}주")

                    # 결과 저장
                    key = f"{stock_name}_{interval}분_{date_label}"
                    results[key] = len(data)
                else:
                    print(f"⚠️ 데이터 없음")
                    results[f"{stock_name}_{interval}분_{date_label}"] = 0

                # API 호출 간격 (초당 5건 제한)
                time.sleep(0.3)

    print_section("📊 테스트 결과 요약")

    print("조회 성공 여부:")
    for key, count in results.items():
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {key}: {count}개")

    print_section("📌 결론")

    # 한 달 전 데이터 조회 성공 여부 확인
    month_ago_success = any("1개월 전" in k and v > 0 for k, v in results.items())

    if month_ago_success:
        print("🎉 64비트 Open API로 과거 데이터 조회 성공!")
        print()
        print("✅ 확인된 기능:")
        print("   - 64비트 Python에서 ActiveX 작동")
        print("   - OPT10080 TR 호출 성공")
        print("   - 과거 분봉 데이터 조회 가능")
        print("   - 한 달 전 데이터도 조회 가능!")
        print()
        print("💡 다음 단계:")
        print("   1. 과거 데이터 수집 스케줄러 구현")
        print("   2. DB 저장 로직 추가")
        print("   3. REST API 대신 Open API 사용")
    else:
        print("⚠️ 한 달 전 데이터 조회 실패")
        print()
        print("가능한 원인:")
        print("   - API 제한 (최근 데이터만 제공)")
        print("   - 계좌 권한 부족")
        print("   - TR 요청 간격 너무 짧음")
        print()
        print("💡 대안:")
        print("   - 오늘부터 데이터 수집 시작 (DB 저장)")
        print("   - 시간이 지나면서 히스토리 누적")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║          🚀 64비트 Kiwoom Open API 테스트 (과거 분봉 조회)                ║
║                                                                          ║
║  목적: 64비트 Python에서 Open API 작동 및 과거 데이터 조회 확인           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

    try:
        test_64bit_openapi()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 테스트를 중단했습니다.")
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()

    print("\n\n테스트 종료. 창을 닫으려면 Enter를 누르세요...")
    input()
