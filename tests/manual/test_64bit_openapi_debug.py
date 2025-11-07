"""
64비트 Open API 로그인 실패 디버깅 스크립트

목적: 로그인 실패 원인을 정확히 파악
"""
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import win32com.client
    import pythoncom
    import pywintypes
except ImportError:
    print("❌ pywin32 모듈이 설치되지 않았습니다!")
    sys.exit(1)


def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def check_kiwoom_processes():
    """실행 중인 Kiwoom 프로세스 확인"""
    import subprocess

    print_section("1️⃣ Kiwoom 프로세스 확인")

    try:
        # tasklist로 프로세스 확인
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq KH*'],
            capture_output=True,
            text=True
        )

        kiwoom_procs = []
        for line in result.stdout.split('\n'):
            if 'KH' in line or 'Kiwoom' in line or 'OpenAPI' in line:
                kiwoom_procs.append(line.strip())

        if kiwoom_procs:
            print("⚠️ 다음 Kiwoom 관련 프로세스가 실행 중입니다:")
            for proc in kiwoom_procs:
                print(f"   {proc}")
            print("\n💡 이 프로세스들이 Open API와 충돌할 수 있습니다.")
            print("   특히 HTS(영웅문)가 실행 중이면 충돌 가능성이 높습니다.")
            return False
        else:
            print("✅ Kiwoom 관련 프로세스 없음")
            return True

    except Exception as e:
        print(f"⚠️ 프로세스 확인 실패: {e}")
        return None


def check_ocx_registration():
    """OCX 등록 상태 확인"""
    print_section("2️⃣ OCX 등록 상태 확인")

    try:
        import winreg

        # CLSID 확인
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CLASSES_ROOT,
                r"KHOPENAPI.KHOpenAPICtrl.1\CLSID"
            )
            clsid, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            print(f"✅ ProgID 등록 확인: KHOPENAPI.KHOpenAPICtrl.1")
            print(f"   CLSID: {clsid}")

            # CLSID로 경로 확인
            key = winreg.OpenKey(
                winreg.HKEY_CLASSES_ROOT,
                f"CLSID\\{clsid}\\InprocServer32"
            )
            path, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            print(f"   OCX 경로: {path}")

            # 파일 존재 확인
            from pathlib import Path
            if Path(path).exists():
                print(f"   ✅ OCX 파일 존재")
                return True
            else:
                print(f"   ❌ OCX 파일 없음!")
                return False

        except WindowsError:
            print("❌ ProgID가 등록되지 않았습니다!")
            print("   C:\\OpenApi\\register.bat를 관리자 권한으로 실행하세요.")
            return False

    except Exception as e:
        print(f"⚠️ 레지스트리 확인 실패: {e}")
        return None


def check_com_initialization():
    """COM 초기화 확인"""
    print_section("3️⃣ COM 초기화")

    try:
        pythoncom.CoInitialize()
        print("✅ COM 아파트먼트 초기화 성공")
        return True
    except Exception as e:
        print(f"❌ COM 초기화 실패: {e}")
        return False


def test_activex_creation():
    """ActiveX 컨트롤 생성 테스트"""
    print_section("4️⃣ ActiveX 컨트롤 생성")

    try:
        ocx = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
        print("✅ ActiveX 컨트롤 생성 성공")

        # 메서드 확인
        try:
            # GetAPIModulePath 메서드 테스트 (로그인 없이 호출 가능)
            module_path = ocx.GetAPIModulePath()
            print(f"   API 모듈 경로: {module_path}")
        except:
            pass

        # GetConnectState 확인
        try:
            state = ocx.GetConnectState()
            print(f"   연결 상태: {state} (0=미연결)")
        except Exception as e:
            print(f"   연결 상태 확인 실패: {e}")

        return ocx
    except Exception as e:
        print(f"❌ ActiveX 컨트롤 생성 실패: {e}")
        return None


def test_event_handler(ocx):
    """이벤트 핸들러 연결 테스트"""
    print_section("5️⃣ 이벤트 핸들러 연결")

    class TestEventHandler:
        def OnEventConnect(self, err_code):
            print(f"   [이벤트] OnEventConnect 호출됨: err_code={err_code}")

    try:
        events = win32com.client.WithEvents(ocx, TestEventHandler)
        print("✅ 이벤트 핸들러 연결 성공")
        return events
    except Exception as e:
        print(f"❌ 이벤트 핸들러 연결 실패: {e}")
        return None


def test_commconnect(ocx):
    """CommConnect 호출 테스트"""
    print_section("6️⃣ CommConnect 호출")

    try:
        print("🔐 CommConnect() 호출 시도...")
        print("   (로그인창이 나타날 수 있습니다)")
        print()

        ret = ocx.CommConnect()

        print(f"   반환값: {ret}")

        if ret == 0:
            print("✅ CommConnect 호출 성공")
            print("   로그인창이 나타나면 수동으로 로그인하세요.")

            # 이벤트 대기
            print("\n   이벤트 대기 중 (20초)...")
            for i in range(20):
                pythoncom.PumpWaitingMessages()
                time.sleep(1)
                if i % 5 == 0:
                    state = ocx.GetConnectState()
                    print(f"   [{i}초] 연결 상태: {state}")

            return True
        else:
            print(f"❌ CommConnect 반환값 오류: {ret}")
            return False

    except pywintypes.com_error as e:
        print(f"❌ COM 오류 발생:")
        print(f"   오류 코드: {e.args[0]} (0x{e.args[0] & 0xFFFFFFFF:08X})")
        print(f"   오류 메시지: {e.args[1]}")

        # 오류 코드 해석
        error_code = e.args[0] & 0xFFFFFFFF

        if error_code == 0x800401FF:
            print("\n💡 오류 분석:")
            print("   0x800401FF = CO_E_NOTINITIALIZED 또는 일반적인 COM 호출 실패")
            print()
            print("   가능한 원인:")
            print("   1. 다른 Kiwoom 프로세스와 충돌 (가장 유력)")
            print("      → HTS(영웅문), OpenAPI 기반 다른 프로그램이 실행 중")
            print("   2. OCX 파일이 손상되었거나 권한 문제")
            print("   3. 로그인 서버 연결 실패")
            print("   4. 방화벽/백신 프로그램 차단")
            print()
            print("   해결 방법:")
            print("   1. 모든 Kiwoom 관련 프로그램 종료")
            print("   2. 키움증권 HTS(영웅문) 종료")
            print("   3. 작업 관리자에서 KH로 시작하는 프로세스 모두 종료")
            print("   4. Python 프로세스 모두 종료 후 재시도")

        return False

    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 디버깅 함수"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║              🔍 64비트 Open API 로그인 실패 디버깅                        ║
║                                                                          ║
║  단계별로 문제를 확인하여 정확한 원인을 찾습니다                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

    # 1. Kiwoom 프로세스 확인
    kiwoom_proc_ok = check_kiwoom_processes()
    if kiwoom_proc_ok == False:
        print("\n⚠️ 계속하려면 Enter를 누르세요 (권장: 프로세스 종료 후 재시도)")
        input()

    # 2. OCX 등록 확인
    ocx_ok = check_ocx_registration()
    if not ocx_ok:
        print("\n❌ OCX가 등록되지 않았습니다. 먼저 등록하세요.")
        return

    # 3. COM 초기화
    com_ok = check_com_initialization()
    if not com_ok:
        print("\n❌ COM 초기화 실패")
        return

    # 4. ActiveX 생성
    ocx = test_activex_creation()
    if not ocx:
        print("\n❌ ActiveX 컨트롤 생성 실패")
        return

    # 5. 이벤트 핸들러
    events = test_event_handler(ocx)
    if not events:
        print("\n⚠️ 이벤트 핸들러 연결 실패 (계속 진행)")

    # 6. CommConnect 호출
    success = test_commconnect(ocx)

    print_section("📊 최종 결과")

    if success:
        print("✅ 모든 단계 통과!")
        print("   로그인이 성공했다면 64비트 Open API가 정상 작동합니다.")
    else:
        print("❌ CommConnect 단계에서 실패")
        print()
        print("📌 추천 조치:")
        print("   1. 위의 오류 분석을 참고하세요")
        print("   2. 다른 Kiwoom 프로그램 모두 종료")
        print("   3. 재부팅 후 재시도")
        print("   4. 그래도 안 되면: DB 저장 방식 사용 (Open API 없이)")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()

    print("\n\n창을 닫으려면 Enter를 누르세요...")
    input()
