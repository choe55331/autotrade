"""
대시보드 API 테스트 스크립트
실제로 데이터를 반환하는지 확인합니다.
"""
import requests
import json
from datetime import datetime


def test_api_endpoint(endpoint, description):
    """API 엔드포인트 테스트"""
    url = f"http://127.0.0.1:5000{endpoint}"

    print(f"\n{'='*80}")
    print(f"테스트: {description}")
    print(f"URL: {url}")
    print(f"{'='*80}")

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공! (HTTP {response.status_code})")
            print(f"\n응답 데이터:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if endpoint == '/api/account':
                if data.get('total_assets', 0) == 0 and data.get('cash', 0) == 0:
                    print(f"\n⚠️  경고: 모든 값이 0입니다. 하드코딩이거나 데이터가 없을 수 있습니다.")
                else:
                    print(f"\n✅ 실제 데이터 확인됨!")

            elif endpoint == '/api/status':
                if 'system' in data and 'risk' in data and 'scanning' in data:
                    print(f"\n✅ 구조 정상!")
                    print(f"   - Uptime: {data['system'].get('uptime', 'N/A')}")
                    print(f"   - Risk Mode: {data['risk'].get('mode', 'N/A')}")
                    print(f"   - Fast Scan: {data['scanning']['fast_scan']['count']} 종목")
                else:
                    print(f"\n⚠️  경고: 응답 구조가 예상과 다릅니다.")

            elif endpoint == '/api/positions':
                if isinstance(data, list):
                    print(f"\n✅ {len(data)}개 포지션")
                    if len(data) == 0:
                        print(f"   (보유 종목 없음)")
                else:
                    print(f"\n⚠️  경고: 배열이 아닙니다.")

            elif endpoint == '/api/activities':
                if isinstance(data, list):
                    print(f"\n✅ {len(data)}개 활동")
                    for i, activity in enumerate(data[:3]):
                        print(f"   [{i+1}] {activity.get('time', 'N/A')} - {activity.get('type', 'N/A')}: {activity.get('message', 'N/A')}")
                else:
                    print(f"\n⚠️  경고: 배열이 아닙니다.")

            elif endpoint == '/api/performance':
                if isinstance(data, list):
                    print(f"\n✅ {len(data)}개 데이터 포인트")
                    if len(data) > 0:
                        print(f"   최신: {data[-1]}")
                    else:
                        print(f"   (데이터 없음)")
                else:
                    print(f"\n⚠️  경고: 배열이 아닙니다.")

            elif endpoint == '/api/system-connections':
                print(f"\n연결 상태:")
                print(f"   - REST API: {'✅ 연결됨' if data.get('rest_api') else '❌ 끊김'}")
                print(f"   - WebSocket: {'✅ 연결됨' if data.get('websocket') else '❌ 끊김'}")
                print(f"   - Gemini AI: {'✅ 연결됨' if data.get('gemini') else '❌ 끊김'}")
                print(f"   - 테스트 모드: {'🧪 활성' if data.get('test_mode') else '⚡ 비활성'}")
                print(f"   - Database: {'✅ 연결됨' if data.get('database') else '❌ 끊김'}")

            return True

        else:
            print(f"❌ 실패! (HTTP {response.status_code})")
            print(f"응답: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ 연결 실패! 대시보드가 실행 중인지 확인하세요.")
        print(f"   python main.py를 먼저 실행하세요.")
        return False

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              AutoTrade Pro - Dashboard API 테스트                         ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️  주의: 이 스크립트를 실행하기 전에 먼저 다음 명령어로 봇을 실행하세요:

   python main.py

그러면 http://127.0.0.1:5000 에서 대시보드가 실행됩니다.

    endpoints = [
        ('/api/account', '계좌 정보'),
        ('/api/positions', '보유 종목'),
        ('/api/candidates', 'AI 후보 종목'),
        ('/api/activities', '활동 로그'),
        ('/api/status', '시스템 상태'),
        ('/api/performance', '성과 차트'),
        ('/api/system-connections', '연결 상태'),
    ]

    results = []

    for endpoint, description in endpoints:
        success = test_api_endpoint(endpoint, description)
        results.append((endpoint, success))

    print(f"\n\n{'='*80}")
    print(f"테스트 결과 요약")
    print(f"{'='*80}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for endpoint, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{status} - {endpoint}")

    print(f"\n총 {total}개 중 {passed}개 통과 ({passed/total*100:.1f}%)")

    if passed == total:
        print(f"\n🎉 모든 API 엔드포인트가 정상 작동합니다!")
    else:
        print(f"\n⚠️  일부 API 엔드포인트에 문제가 있습니다.")
        print(f"   main.py가 실행 중인지 확인하세요.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n테스트 중단됨.")
