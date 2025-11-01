#!/usr/bin/env python3
"""
WebSocket 구독 기능 테스트

키움 WebSocket API 실시간 데이터 구독 테스트
실행 시 자동으로 test_results/ 폴더에 결과 저장
"""
import sys
import json
import asyncio
import websockets
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config import get_credentials


class Tee:
    """화면과 파일에 동시 출력"""
    def __init__(self, *files):
        self.files = files

    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


class WebSocketTester:
    def __init__(self):
        self.credentials = get_credentials()
        self.ws_url = self.credentials.KIWOOM_WEBSOCKET_URL
        self.appkey = self.credentials.KIWOOM_REST_APPKEY
        self.ws = None
        self.subscriptions = []

    async def connect(self):
        """WebSocket 연결"""
        print(f"WebSocket 연결 중...")
        print(f"URL: {self.ws_url}")

        try:
            self.ws = await websockets.connect(self.ws_url)
            print("✅ WebSocket 연결 성공")
            return True
        except Exception as e:
            print(f"❌ WebSocket 연결 실패: {e}")
            return False

    async def subscribe_price(self, stock_code: str):
        """
        실시간 가격 구독

        Args:
            stock_code: 종목코드 (예: "005930" - 삼성전자)
        """
        message = {
            "header": {
                "approval_key": self.appkey,
                "custtype": "P",
                "tr_type": "1",  # 구독
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": "H0STCNT0",  # 실시간 체결가
                    "tr_key": stock_code
                }
            }
        }

        print(f"\n실시간 가격 구독: {stock_code}")
        await self.ws.send(json.dumps(message))

        self.subscriptions.append({
            'type': 'price',
            'stock_code': stock_code,
            'tr_id': 'H0STCNT0'
        })

    async def subscribe_orderbook(self, stock_code: str):
        """
        실시간 호가 구독

        Args:
            stock_code: 종목코드
        """
        message = {
            "header": {
                "approval_key": self.appkey,
                "custtype": "P",
                "tr_type": "1",
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": "H0STASP0",  # 실시간 호가
                    "tr_key": stock_code
                }
            }
        }

        print(f"\n실시간 호가 구독: {stock_code}")
        await self.ws.send(json.dumps(message))

        self.subscriptions.append({
            'type': 'orderbook',
            'stock_code': stock_code,
            'tr_id': 'H0STASP0'
        })

    async def subscribe_index(self, index_code: str = "0001"):
        """
        실시간 지수 구독

        Args:
            index_code: 지수코드 (0001: KOSPI, 1001: KOSDAQ)
        """
        message = {
            "header": {
                "approval_key": self.appkey,
                "custtype": "P",
                "tr_type": "1",
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": "H0UPCNT0",  # 실시간 지수
                    "tr_key": index_code
                }
            }
        }

        print(f"\n실시간 지수 구독: {index_code}")
        await self.ws.send(json.dumps(message))

        self.subscriptions.append({
            'type': 'index',
            'index_code': index_code,
            'tr_id': 'H0UPCNT0'
        })

    async def unsubscribe(self, tr_id: str, tr_key: str):
        """
        구독 해제

        Args:
            tr_id: TR ID
            tr_key: 종목/지수 코드
        """
        message = {
            "header": {
                "approval_key": self.appkey,
                "custtype": "P",
                "tr_type": "2",  # 구독 해제
                "content-type": "utf-8"
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": tr_key
                }
            }
        }

        print(f"\n구독 해제: {tr_id} - {tr_key}")
        await self.ws.send(json.dumps(message))

    async def receive_messages(self, duration: int = 30):
        """
        메시지 수신 (지정된 시간 동안)

        Args:
            duration: 수신 시간 (초)
        """
        print(f"\n실시간 데이터 수신 중... ({duration}초)")
        print("-" * 80)

        start_time = asyncio.get_event_loop().time()
        message_count = 0

        try:
            while True:
                # 시간 체크
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > duration:
                    break

                # 메시지 수신 (타임아웃 1초)
                try:
                    message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                    message_count += 1

                    # 메시지 파싱
                    data = json.loads(message)

                    # 메시지 출력
                    tr_id = data.get('header', {}).get('tr_id', 'Unknown')
                    body = data.get('body', {})

                    print(f"[{message_count}] {datetime.now().strftime('%H:%M:%S')} - {tr_id}")
                    print(f"  Data: {json.dumps(body, ensure_ascii=False)[:100]}...")

                except asyncio.TimeoutError:
                    # 타임아웃은 정상 (메시지가 없을 수 있음)
                    pass
                except json.JSONDecodeError:
                    print(f"⚠️ JSON 파싱 실패")

        except Exception as e:
            print(f"❌ 수신 오류: {e}")

        print("-" * 80)
        print(f"총 {message_count}개 메시지 수신")

    async def disconnect(self):
        """WebSocket 연결 해제"""
        if self.ws:
            # 연결이 열려있는 경우에만 구독 해제
            if not self.ws.closed:
                try:
                    # 모든 구독 해제
                    for sub in self.subscriptions:
                        tr_id = sub['tr_id']
                        tr_key = sub.get('stock_code') or sub.get('index_code')
                        await self.unsubscribe(tr_id, tr_key)
                        await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"⚠️ 구독 해제 중 오류 (무시): {e}")

            # 연결 종료
            if not self.ws.closed:
                await self.ws.close()
            print("\n✅ WebSocket 연결 해제")

    async def run_test(self):
        """테스트 실행"""
        print("=" * 80)
        print("WebSocket 구독 기능 테스트")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 연결
        if not await self.connect():
            return

        # 대기 (연결 안정화)
        await asyncio.sleep(1)

        try:
            # 1. 삼성전자 실시간 가격 구독
            await self.subscribe_price("005930")
            await asyncio.sleep(0.5)

            # 2. 삼성전자 실시간 호가 구독
            await self.subscribe_orderbook("005930")
            await asyncio.sleep(0.5)

            # 3. KOSPI 지수 구독
            await self.subscribe_index("0001")
            await asyncio.sleep(0.5)

            # 4. 실시간 데이터 수신 (30초)
            await self.receive_messages(duration=30)

        finally:
            # 연결 해제
            await self.disconnect()

        print("\n" + "=" * 80)
        print("테스트 완료")
        print("=" * 80)


async def main():
    """메인 함수"""
    tester = WebSocketTester()
    await tester.run_test()


if __name__ == "__main__":
    # 결과 저장 디렉토리 생성
    result_dir = Path(__file__).parent / 'test_results'
    result_dir.mkdir(exist_ok=True)

    # 결과 파일명 (타임스탬프 포함)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = result_dir / f'websocket_test_{timestamp}.txt'

    # 화면과 파일에 동시 출력
    with open(result_file, 'w', encoding='utf-8') as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)

        try:
            print(f"결과 파일: {result_file}")
            print()
            print("⚠️  주의: WebSocket 테스트는 장 시작 시간(9:00-15:30)에만 작동합니다")
            print("⚠️  장 외 시간에는 실시간 데이터가 수신되지 않을 수 있습니다")
            print()

            # 사용자 확인
            response = input("테스트를 시작하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                asyncio.run(main())
            else:
                print("테스트 취소")

            print()
            print(f"✅ 결과 저장: {result_file}")
        finally:
            sys.stdout = original_stdout
