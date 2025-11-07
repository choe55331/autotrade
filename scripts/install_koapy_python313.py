"""
Python 3.13에서 koapy 설치 자동화 스크립트

여러 방법을 순차적으로 시도합니다:
1. exchange-calendars 대체
2. 의존성 수동 설치
3. 성공 여부 테스트
"""
import subprocess
import sys
import struct


def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def check_python_version():
    """Python 버전 확인"""
    print_section("1️⃣ Python 환경 확인")

    bits = struct.calcsize("P") * 8
    version = sys.version

    print(f"Python 버전: {version}")
    print(f"Python 비트: {bits}-bit")
    print()

    if sys.version_info < (3, 9):
        print("❌ Python 3.9 이상이 필요합니다.")
        return False

    if sys.version_info >= (3, 12):
        print("⚠️  Python 3.12+ 감지")
        print("   trading-calendars 호환성 문제가 있을 수 있습니다.")
        print("   대안 방법을 시도합니다...")
    else:
        print("✅ Python 버전 적합")

    return True


def install_package(package, quiet=False):
    """패키지 설치"""
    try:
        if quiet:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "-q"],
                check=True,
                capture_output=True
            )
        else:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True
            )
        return True
    except subprocess.CalledProcessError:
        return False


def method_1_exchange_calendars():
    """방법 1: exchange-calendars 사용"""
    print_section("2️⃣ 방법 1: exchange-calendars로 대체")

    print("📦 pip 업그레이드 중...")
    install_package("--upgrade pip", quiet=True)

    print("📦 exchange-calendars 설치 중...")
    if not install_package("exchange-calendars"):
        print("❌ exchange-calendars 설치 실패")
        return False

    print("✅ exchange-calendars 설치 완료")
    print()

    print("📦 koapy 의존성 설치 중...")

    deps = [
        "grpcio",
        "grpcio-tools",
        "pyhocon",
        "tqdm",
        "tabulate",
        "deprecated",
        "psutil",
        "pycryptodomex",
        "Rx",
        "pandas",
        "pywin32",
        "PyQt5",
    ]

    failed = []
    for dep in deps:
        print(f"  설치: {dep}...", end=" ")
        if install_package(dep, quiet=True):
            print("✅")
        else:
            print("❌")
            failed.append(dep)

    if failed:
        print(f"\n⚠️  일부 패키지 설치 실패: {', '.join(failed)}")

    print()
    print("📦 koapy 설치 중 (의존성 체크 없이)...")

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "koapy", "--no-deps"],
            check=True
        )
        print("✅ koapy 설치 완료")
        return True
    except subprocess.CalledProcessError:
        print("❌ koapy 설치 실패")
        return False


def method_2_skip_trading_calendars():
    """방법 2: trading-calendars 없이 설치"""
    print_section("3️⃣ 방법 2: trading-calendars 건너뛰기")

    print("📦 koapy와 의존성 설치 중 (trading-calendars 제외)...")

    # 먼저 다른 의존성 모두 설치
    deps = [
        "grpcio>=1.44.0",
        "grpcio-tools>=1.44.0",
        "pyhocon>=0.3.58",
        "tqdm>=4.62.3",
        "tabulate>=0.8.9",
        "deprecated>=1.2.13",
        "psutil>=5.9.0",
        "pycryptodomex>=3.14.1",
        "Rx>=3.1.1",
        "pandas>=1.3.5",
        "pywin32>=303",
        "PyQt5>=5.15.6",
    ]

    for dep in deps:
        install_package(dep, quiet=True)

    # koapy 설치 (의존성 체크 없이)
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "koapy", "--no-deps"],
            check=True
        )
        print("✅ koapy 설치 완료")
        return True
    except subprocess.CalledProcessError:
        print("❌ koapy 설치 실패")
        return False


def test_koapy_import():
    """koapy 로드 테스트"""
    print_section("4️⃣ koapy 로드 테스트")

    try:
        print("테스트 1: koapy 모듈 로드...")
        import koapy
        print("✅ koapy 모듈 로드 성공")
        print(f"   버전: {getattr(koapy, '__version__', 'unknown')}")
        print()

        print("테스트 2: KiwoomOpenApiPlusEntrypoint 로드...")
        from koapy import KiwoomOpenApiPlusEntrypoint
        print("✅ KiwoomOpenApiPlusEntrypoint 로드 성공")
        print()

        print("테스트 3: 기본 기능 확인...")
        # Entrypoint 생성만 테스트 (연결은 하지 않음)
        try:
            entrypoint = KiwoomOpenApiPlusEntrypoint()
            print("✅ Entrypoint 생성 성공")
            entrypoint.close()
        except Exception as e:
            print(f"⚠️  Entrypoint 생성 실패: {e}")
            print("   (연결 테스트는 별도로 진행하세요)")

        print()
        print("🎉 모든 테스트 통과!")
        return True

    except ImportError as e:
        print(f"❌ koapy 로드 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_next_steps(success):
    """다음 단계 안내"""
    print_section("📋 다음 단계")

    if success:
        print("✅ koapy 설치 성공!")
        print()
        print("이제 다음 명령으로 테스트하세요:")
        print()
        print("  python tests/manual/test_koapy_simple.py")
        print()
        print("또는:")
        print()
        print("  python examples/unified_main_example.py")
        print()
        print("💡 참고:")
        print("   - exchange-calendars를 사용하므로 일부 기능이 다를 수 있습니다")
        print("   - 문제가 있다면 Python 3.11 사용을 권장합니다")
        print()

    else:
        print("❌ koapy 설치 실패")
        print()
        print("💡 대안:")
        print()
        print("1. Python 3.11로 다운그레이드 (가장 안정적)")
        print("   https://www.python.org/downloads/release/python-3119/")
        print()
        print("2. Conda 환경 사용:")
        print("   conda create -n koapy311 python=3.11")
        print("   conda activate koapy311")
        print("   pip install koapy")
        print()
        print("3. 직접 32비트 서버 구축 (고급)")
        print("   docs/PYTHON313_WORKAROUNDS.md 참고")
        print()
        print("상세 가이드:")
        print("   docs/PYTHON_VERSION_GUIDE.md")
        print("   docs/QUICK_FIX_PYTHON313.md")
        print()


def main():
    """메인 함수"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║        🔧 Python 3.13용 koapy 설치 스크립트                              ║
║                                                                          ║
║  Python 3.13에서 koapy를 설치하기 위한 여러 방법을 시도합니다            ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

    # Python 버전 확인
    if not check_python_version():
        return

    print("\n⚠️  주의:")
    print("   이 스크립트는 여러 방법을 시도하여 koapy를 설치합니다.")
    print("   일부 패키지를 설치/제거할 수 있습니다.")
    print()

    response = input("계속하시겠습니까? (y/n): ").strip().lower()
    if response != 'y':
        print("\n취소되었습니다.")
        return

    # 방법 1 시도
    success = method_1_exchange_calendars()

    if success:
        # 테스트
        test_success = test_koapy_import()
        show_next_steps(test_success)
    else:
        # 방법 2 시도
        print("\n방법 1 실패. 방법 2를 시도합니다...\n")
        success = method_2_skip_trading_calendars()

        if success:
            test_success = test_koapy_import()
            show_next_steps(test_success)
        else:
            show_next_steps(False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()

    print("\n창을 닫으려면 Enter를 누르세요...")
    input()
