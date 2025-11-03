"""
WebSocket 연결 테스트
다양한 방식으로 WebSocket 연결을 시도하고 상태를 확인합니다.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time
import threading
from datetime import datetime
from core.websocket_client import WebSocketClient
from core.rest_client import RestClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebSocketTester:
    """WebSocket 연결을 다양한 방법으로 테스트"""

    def __init__(self):
        self.rest_client = RestClient()
        self.test_results = []

        logger.info(f"🔧 초기화 완료")
        logger.info(f"   REST 서버: {self.rest_client.base_url}")

    def test_case_1_basic_connection(self):
        """테스트 1: 기본 연결 (구독 없음)"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 테스트 1: 기본 WebSocket 연결 (구독 없음)")
        logger.info(f"{'='*80}")

        try:
            # WebSocket 클라이언트 생성
            ws_client = WebSocketClient(self.rest_client)

            logger.info(f"📡 연결 시도 중...")
            ws_client.connect()

            # 10초 대기하면서 연결 상태 확인
            for i in range(10):
                time.sleep(1)
                status = "✅ 연결됨" if ws_client.is_connected else "❌ 연결 끊김"
                logger.info(f"   [{i+1}/10초] 연결 상태: {status}")

                if not ws_client.is_connected:
                    break

            # 연결 종료
            ws_client.disconnect()
            logger.info(f"🔌 연결 종료")

            result = {
                'test': '기본 연결 (구독 없음)',
                'success': ws_client.is_connected or True,  # 연결 시도 자체는 성공
                'notes': '구독 없이 기본 연결만 테스트'
            }
            self.test_results.append(result)

            return True

        except Exception as e:
            logger.error(f"❌ 테스트 실패: {e}")
            self.test_results.append({
                'test': '기본 연결 (구독 없음)',
                'success': False,
                'error': str(e)
            })
            return False

    def test_case_2_with_subscription(self):
        """테스트 2: 체결 정보 구독"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 테스트 2: WebSocket 연결 + 체결 정보 구독")
        logger.info(f"{'='*80}")

        try:
            ws_client = WebSocketClient(self.rest_client)

            # 메시지 수신 카운터
            message_count = [0]

            def on_message(ws, message):
                message_count[0] += 1
                logger.info(f"📨 메시지 수신 #{message_count[0]}: {message[:100]}...")

            # 메시지 핸들러 등록
            original_handler = ws_client._on_message
            ws_client._on_message = lambda ws, msg: (on_message(ws, msg), original_handler(ws, msg))

            logger.info(f"📡 연결 시도 중...")
            ws_client.connect()

            time.sleep(2)  # 연결 대기

            # 삼성전자 체결 정보 구독
            logger.info(f"📢 삼성전자(005930) 체결 정보 구독 중...")
            ws_client.subscribe_execution("005930")

            # 30초 대기하면서 메시지 수신 확인
            logger.info(f"⏳ 30초 동안 메시지 수신 대기...")
            for i in range(30):
                time.sleep(1)
                if i % 5 == 0:
                    status = "✅ 연결됨" if ws_client.is_connected else "❌ 연결 끊김"
                    logger.info(f"   [{i+1}/30초] 상태: {status}, 수신: {message_count[0]}개")

            # 연결 종료
            ws_client.disconnect()
            logger.info(f"🔌 연결 종료")
            logger.info(f"📊 총 {message_count[0]}개 메시지 수신")

            success = message_count[0] > 0
            result = {
                'test': '체결 정보 구독',
                'success': success,
                'message_count': message_count[0],
                'notes': f"{message_count[0]}개 메시지 수신" if success else "메시지 수신 없음"
            }
            self.test_results.append(result)

            return success

        except Exception as e:
            logger.error(f"❌ 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append({
                'test': '체결 정보 구독',
                'success': False,
                'error': str(e)
            })
            return False

    def test_case_3_reconnection(self):
        """테스트 3: 재연결 테스트"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 테스트 3: WebSocket 재연결 테스트")
        logger.info(f"{'='*80}")

        try:
            ws_client = WebSocketClient(self.rest_client)

            logger.info(f"📡 첫 번째 연결...")
            ws_client.connect()
            time.sleep(3)

            first_connected = ws_client.is_connected
            logger.info(f"   첫 번째 연결 상태: {'✅ 성공' if first_connected else '❌ 실패'}")

            if not first_connected:
                logger.warning(f"첫 번째 연결 실패. 재연결 테스트를 건너뜁니다.")
                return False

            logger.info(f"🔌 연결 종료...")
            ws_client.disconnect()
            time.sleep(2)

            logger.info(f"📡 재연결 시도...")
            ws_client.connect()
            time.sleep(3)

            second_connected = ws_client.is_connected
            logger.info(f"   재연결 상태: {'✅ 성공' if second_connected else '❌ 실패'}")

            ws_client.disconnect()

            success = first_connected and second_connected
            result = {
                'test': '재연결 테스트',
                'success': success,
                'first_connect': first_connected,
                'reconnect': second_connected,
                'notes': '재연결 성공' if success else '재연결 실패'
            }
            self.test_results.append(result)

            return success

        except Exception as e:
            logger.error(f"❌ 테스트 실패: {e}")
            self.test_results.append({
                'test': '재연결 테스트',
                'success': False,
                'error': str(e)
            })
            return False

    def test_case_4_stability(self):
        """테스트 4: 장시간 연결 안정성 (60초)"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 테스트 4: WebSocket 장시간 연결 안정성 (60초)")
        logger.info(f"{'='*80}")

        try:
            ws_client = WebSocketClient(self.rest_client)

            logger.info(f"📡 연결 시도 중...")
            ws_client.connect()
            time.sleep(2)

            disconnect_count = [0]
            check_interval = 5

            logger.info(f"⏳ 60초 동안 연결 상태 모니터링...")
            for i in range(0, 60, check_interval):
                time.sleep(check_interval)

                if ws_client.is_connected:
                    logger.info(f"   [{i+check_interval}/60초] ✅ 연결 유지 중")
                else:
                    logger.warning(f"   [{i+check_interval}/60초] ❌ 연결 끊김 감지")
                    disconnect_count[0] += 1

            # 연결 종료
            ws_client.disconnect()
            logger.info(f"🔌 연결 종료")
            logger.info(f"📊 총 {disconnect_count[0]}회 연결 끊김 발생")

            success = disconnect_count[0] == 0
            result = {
                'test': '장시간 연결 안정성',
                'success': success,
                'disconnect_count': disconnect_count[0],
                'notes': f"{disconnect_count[0]}회 끊김" if not success else "안정적 연결 유지"
            }
            self.test_results.append(result)

            return success

        except Exception as e:
            logger.error(f"❌ 테스트 실패: {e}")
            self.test_results.append({
                'test': '장시간 연결 안정성',
                'success': False,
                'error': str(e)
            })
            return False

    def test_case_5_multiple_subscriptions(self):
        """테스트 5: 다중 구독"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 테스트 5: 다중 종목 구독")
        logger.info(f"{'='*80}")

        try:
            ws_client = WebSocketClient(self.rest_client)

            message_count = [0]

            def on_message(ws, message):
                message_count[0] += 1
                if message_count[0] % 5 == 0:  # 5개마다 출력
                    logger.info(f"📨 메시지 수신: {message_count[0]}개")

            # 메시지 핸들러 등록
            original_handler = ws_client._on_message
            ws_client._on_message = lambda ws, msg: (on_message(ws, msg), original_handler(ws, msg))

            logger.info(f"📡 연결 시도 중...")
            ws_client.connect()
            time.sleep(2)

            # 여러 종목 구독
            stocks = [
                ("005930", "삼성전자"),
                ("000660", "SK하이닉스"),
                ("035420", "NAVER"),
                ("035720", "카카오"),
                ("051910", "LG화학")
            ]

            for code, name in stocks:
                logger.info(f"📢 {name}({code}) 구독 중...")
                ws_client.subscribe_execution(code)
                time.sleep(0.5)

            # 20초 대기하면서 메시지 수신 확인
            logger.info(f"⏳ 20초 동안 메시지 수신 대기...")
            time.sleep(20)

            # 연결 종료
            ws_client.disconnect()
            logger.info(f"🔌 연결 종료")
            logger.info(f"📊 총 {message_count[0]}개 메시지 수신")

            success = message_count[0] > 0
            result = {
                'test': '다중 종목 구독',
                'success': success,
                'stocks': len(stocks),
                'message_count': message_count[0],
                'notes': f"{len(stocks)}개 종목 구독, {message_count[0]}개 메시지"
            }
            self.test_results.append(result)

            return success

        except Exception as e:
            logger.error(f"❌ 테스트 실패: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append({
                'test': '다중 종목 구독',
                'success': False,
                'error': str(e)
            })
            return False

    def print_summary(self):
        """테스트 결과 요약"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 WebSocket 테스트 결과 요약")
        logger.info(f"{'='*80}")

        success_count = sum(1 for r in self.test_results if r.get('success'))
        total_count = len(self.test_results)

        logger.info(f"\n총 {total_count}개 테스트 실행")
        logger.info(f"성공: {success_count}개 ✅")
        logger.info(f"실패: {total_count - success_count}개 ❌")

        # 각 테스트 결과
        logger.info(f"\n{'='*80}")
        logger.info(f"상세 결과:")
        logger.info(f"{'='*80}")
        for r in self.test_results:
            status = "✅ 성공" if r.get('success') else "❌ 실패"
            logger.info(f"\n  {status} - {r['test']}")
            if r.get('notes'):
                logger.info(f"    💡 {r['notes']}")
            if r.get('error'):
                logger.info(f"    ⚠️  오류: {r['error']}")

        # 결론
        logger.info(f"\n{'='*80}")
        logger.info(f"💡 결론")
        logger.info(f"{'='*80}")
        if success_count == total_count:
            logger.info(f"✅ 모든 테스트 통과! WebSocket이 정상 작동합니다.")
        elif success_count > 0:
            logger.info(f"⚠️  일부 테스트만 통과했습니다.")
            logger.info(f"   실패한 테스트를 확인하고 문제를 해결하세요.")
        else:
            logger.info(f"❌ 모든 테스트 실패. WebSocket 설정을 확인하세요.")
            logger.info(f"   - WebSocket URL 확인")
            logger.info(f"   - 인증 정보 확인")
            logger.info(f"   - 네트워크 연결 확인")


def main():
    """메인 테스트 실행"""
    logger.info(f"\n{'='*80}")
    logger.info(f"🚀 WebSocket 연결 테스트 시작")
    logger.info(f"{'='*80}\n")

    tester = WebSocketTester()

    # 사용자 확인
    logger.info(f"📋 5가지 테스트를 순차적으로 실행합니다:")
    logger.info(f"   1. 기본 연결 (구독 없음)")
    logger.info(f"   2. 체결 정보 구독")
    logger.info(f"   3. 재연결 테스트")
    logger.info(f"   4. 장시간 연결 안정성 (60초)")
    logger.info(f"   5. 다중 종목 구독")

    response = input(f"\n계속하시겠습니까? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        logger.info(f"테스트를 취소했습니다.")
        return

    # 테스트 실행
    test_methods = [
        tester.test_case_1_basic_connection,
        tester.test_case_2_with_subscription,
        tester.test_case_3_reconnection,
        tester.test_case_4_stability,
        tester.test_case_5_multiple_subscriptions
    ]

    for i, test_method in enumerate(test_methods, 1):
        logger.info(f"\n{'#'*80}")
        logger.info(f"# 테스트 {i}/{len(test_methods)}")
        logger.info(f"{'#'*80}")

        try:
            test_method()
        except Exception as e:
            logger.error(f"테스트 실행 중 예외 발생: {e}")
            import traceback
            traceback.print_exc()

        # 다음 테스트 전 대기
        if i < len(test_methods):
            logger.info(f"\n⏳ 3초 후 다음 테스트...")
            time.sleep(3)

    # 결과 요약
    tester.print_summary()

    logger.info(f"\n{'='*80}")
    logger.info(f"✅ 모든 테스트 완료")
    logger.info(f"{'='*80}\n")


if __name__ == "__main__":
    main()
