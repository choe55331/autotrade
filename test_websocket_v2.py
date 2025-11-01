#!/usr/bin/env python3
"""
WebSocket 실시간 데이터 구독 테스트 (올바른 형식 사용)

키움 WebSocket API 실시간 데이터 구독 테스트
문서: kiwoom_docs/실시간시세.md 기준
"""
import sys
import json
import asyncio
import websockets
from datetime import datetime
from pathlib import Path

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


class WebSocketTesterV2:
    """
    키움 WebSocket 실시간 데이터 구독 테스터 (확장 버전)

    지원하는 TR 유형 (18개 전체 지원):
    - 00: 주문체결 (계좌 기반, item 불필요) - 주문 접수/체결/정정/취소
    - 04: 잔고 (계좌 기반, item 불필요) - 계좌 잔고 변동
    - 0A: 주식시세 - 현재가, 대비, 거래량, 거래대금
    - 0B: 주식체결 - 체결가, 체결량
    - 0C: 주식우선호가 - 매도/매수 우선호가, 예상체결가
    - 0D: 주식호가잔량 - 10단계 호가 및 잔량
    - 0E: 주식시간외호가 - 시간외 단일가
    - 0F: 주식당일거래원 - 거래원별 매매 현황
    - 0G: ETF NAV - ETF 순자산가치, 괴리율
    - 0H: 주식예상체결 - 장 시작 전 예상체결가/량
    - 0J: 업종지수 - 업종별 지수, 등락률
    - 0U: 업종등락 - 업종 내 상승/하락/보합 종목 수
    - 0g: 주식종목정보 - 시가총액, 액면가, 상장주식수
    - 0m: ELW 이론가 - ELW 이론가, 내재변동성
    - 0s: 장시작시간 - 장 운영 시간, 구분
    - 0u: ELW 지표 - 델타, 감마, 세타, 베가
    - 0w: 종목프로그램매매 - 차익/비차익 매수/매도
    - 1h: VI발동/해제 - 변동성완화장치 발동/해제
    """

    def __init__(self):
        self.credentials = get_credentials()
        self.ws_url = self.credentials.KIWOOM_WEBSOCKET_URL
        self.appkey = self.credentials.KIWOOM_REST_APPKEY
        self.ws = None
        self.registered_types = []

    async def connect(self):
        """WebSocket 연결"""
        print(f"WebSocket 연결 중...")
        print(f"URL: {self.ws_url}")

        try:
            # WebSocket 연결 (헤더는 첫 메시지에 포함)
            self.ws = await websockets.connect(self.ws_url)
            print("✅ WebSocket 연결 성공")
            return True
        except Exception as e:
            print(f"❌ WebSocket 연결 실패: {e}")
            return False

    async def register_realtime(self, items: list, types: list, grp_no: str = "1", refresh: str = "1"):
        """
        실시간 데이터 등록

        Args:
            items: 종목코드 리스트 (예: ["005930", "000660"])
                  주문체결(00), 잔고(04)는 빈 리스트 [""]
            types: TR 타입 리스트 (예: ["0A", "0B"])
            grp_no: 그룹번호 (기본값: "1")
            refresh: 기존등록유지여부 (0:유지안함, 1:유지, 기본값: "1")
        """
        message = {
            "header": {
                "approval_key": self.appkey,
                "custtype": "P",
                "tr_type": "3",
                "content-type": "utf-8"
            },
            "body": {
                "trnm": "REG",
                "grp_no": grp_no,
                "refresh": refresh,
                "data": [{
                    "item": items,
                    "type": types
                }]
            }
        }

        print(f"\n실시간 데이터 등록:")
        print(f"  종목: {items}")
        print(f"  타입: {types}")

        await self.ws.send(json.dumps(message))

        # 등록 응답 대기
        response = await asyncio.wait_for(self.ws.recv(), timeout=5.0)
        response_data = json.loads(response)

        # body에서 return_code 확인
        body = response_data.get('body', {})
        if body.get('return_code') == 0:
            print(f"✅ 등록 성공")
            self.registered_types.extend(types)
        else:
            print(f"❌ 등록 실패: {body.get('return_msg', response_data)}")

        return body.get('return_code') == 0

    async def unregister_realtime(self, items: list, types: list, grp_no: str = "1"):
        """
        실시간 데이터 해지

        Args:
            items: 종목코드 리스트
            types: TR 타입 리스트
            grp_no: 그룹번호
        """
        message = {
            "header": {
                "approval_key": self.appkey,
                "custtype": "P",
                "tr_type": "3",
                "content-type": "utf-8"
            },
            "body": {
                "trnm": "REMOVE",
                "grp_no": grp_no,
                "data": [{
                    "item": items,
                    "type": types
                }]
            }
        }

        print(f"\n실시간 데이터 해지:")
        print(f"  종목: {items}")
        print(f"  타입: {types}")

        await self.ws.send(json.dumps(message))

    async def receive_messages(self, duration: int = 30):
        """
        실시간 데이터 수신

        Args:
            duration: 수신 시간 (초)
        """
        print(f"\n실시간 데이터 수신 중... ({duration}초)")
        print("-" * 80)

        start_time = asyncio.get_event_loop().time()
        message_count = 0
        message_by_type = {}

        try:
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > duration:
                    break

                try:
                    message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                    message_count += 1

                    data = json.loads(message)

                    # body에서 실시간 데이터 확인
                    body = data.get('body', {})
                    if body.get('trnm') == 'REAL':
                        for item_data in body.get('data', []):
                            msg_type = item_data.get('type', 'Unknown')
                            msg_name = item_data.get('name', 'Unknown')
                            msg_item = item_data.get('item', '')
                            msg_values = item_data.get('values', {})

                            # 타입별 카운트
                            if msg_type not in message_by_type:
                                message_by_type[msg_type] = 0
                            message_by_type[msg_type] += 1

                            # 주요 데이터만 출력
                            print(f"[{message_count}] {datetime.now().strftime('%H:%M:%S')} - {msg_name} ({msg_type})")
                            if msg_item:
                                print(f"  종목: {msg_item}")

                            # 타입별 주요 필드 출력
                            if msg_type == '00':  # 주문체결
                                print(f"  주문번호: {msg_values.get('9203')}, 상태: {msg_values.get('913')}, "
                                      f"종목: {msg_values.get('302')}, 수량: {msg_values.get('900')}, "
                                      f"가격: {msg_values.get('901')}")
                            elif msg_type == '04':  # 잔고
                                print(f"  종목: {msg_values.get('302')}, 수량: {msg_values.get('930')}, "
                                      f"매입가: {msg_values.get('931')}, 현재가: {msg_values.get('10')}")
                            elif msg_type in ['0A', '0B']:  # 주식시세, 주식체결
                                print(f"  현재가: {msg_values.get('10')}, 대비: {msg_values.get('11')}, "
                                      f"거래량: {msg_values.get('13')}, 거래대금: {msg_values.get('14')}")
                            elif msg_type == '0C':  # 주식우선호가
                                print(f"  매도우선호가: {msg_values.get('27')}, 매수우선호가: {msg_values.get('28')}, "
                                      f"예상체결가: {msg_values.get('23')}")
                            elif msg_type == '0D':  # 주식호가잔량
                                print(f"  매도호가: {msg_values.get('27')}, 매수호가: {msg_values.get('28')}, "
                                      f"매도잔량: {msg_values.get('41')}, 매수잔량: {msg_values.get('51')}")
                            elif msg_type == '0E':  # 주식시간외호가
                                print(f"  단일가: {msg_values.get('10010')}, 대비: {msg_values.get('11')}")
                            elif msg_type == '0F':  # 주식당일거래원
                                print(f"  외국계순매수: {msg_values.get('621')}, 증권사코드: {msg_values.get('620')}")
                            elif msg_type == '0G':  # ETF NAV
                                print(f"  NAV: {msg_values.get('548')}, 괴리율: {msg_values.get('549')}")
                            elif msg_type == '0H':  # 주식예상체결
                                print(f"  예상체결가: {msg_values.get('23')}, 예상체결량: {msg_values.get('24')}, "
                                      f"대비: {msg_values.get('25')}")
                            elif msg_type == '0J':  # 업종지수
                                print(f"  현재지수: {msg_values.get('10')}, 대비: {msg_values.get('11')}, "
                                      f"등락률: {msg_values.get('12')}")
                            elif msg_type == '0U':  # 업종등락
                                print(f"  상승종목수: {msg_values.get('252')}, 하락종목수: {msg_values.get('251')}, "
                                      f"보합종목수: {msg_values.get('253')}")
                            elif msg_type == '0g':  # 주식종목정보
                                print(f"  시가총액: {msg_values.get('307')}, 액면가: {msg_values.get('305')}, "
                                      f"상장주식수: {msg_values.get('306')}")
                            elif msg_type == '0m':  # ELW 이론가
                                print(f"  이론가: {msg_values.get('589')}, 내재변동성: {msg_values.get('590')}")
                            elif msg_type == '0s':  # 장시작시간
                                print(f"  장운영시간: {msg_values.get('215')}, 장운영구분: {msg_values.get('216')}")
                            elif msg_type == '0u':  # ELW 지표
                                print(f"  델타: {msg_values.get('595')}, 감마: {msg_values.get('596')}, "
                                      f"세타: {msg_values.get('597')}, 베가: {msg_values.get('598')}")
                            elif msg_type == '0w':  # 종목프로그램매매
                                print(f"  차익매수: {msg_values.get('679')}, 차익매도: {msg_values.get('680')}, "
                                      f"비차익매수: {msg_values.get('681')}, 비차익매도: {msg_values.get('682')}")
                            elif msg_type == '1h':  # VI발동/해제
                                print(f"  VI구분: {msg_values.get('729')}, VI발동가: {msg_values.get('730')}, "
                                      f"VI발동시간: {msg_values.get('731')}")
                            else:
                                # 처음 5개 필드만 출력
                                preview = {k: v for k, v in list(msg_values.items())[:5]}
                                print(f"  데이터: {preview}")

                            print()

                except asyncio.TimeoutError:
                    pass
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON 파싱 실패: {e}")

        except Exception as e:
            print(f"❌ 수신 오류: {e}")

        print("-" * 80)
        print(f"총 {message_count}개 메시지 수신")
        print(f"\n타입별 메시지 수:")
        for msg_type, count in message_by_type.items():
            print(f"  {msg_type}: {count}건")

    async def disconnect(self):
        """WebSocket 연결 해제"""
        if self.ws:
            try:
                # 모든 등록 해제
                if self.registered_types:
                    await self.unregister_realtime([""], self.registered_types)
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"⚠️ 구독 해제 중 오류 (무시): {e}")

            try:
                await self.ws.close()
            except Exception as e:
                print(f"⚠️ WebSocket 닫기 중 오류 (무시): {e}")

            print("\n✅ WebSocket 연결 해제")

    async def run_comprehensive_test(self):
        """포괄적인 테스트 실행"""
        print("=" * 80)
        print("WebSocket 실시간 데이터 구독 테스트 (v2 - 확장)")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 연결
        if not await self.connect():
            return

        await asyncio.sleep(1)

        try:
            # 테스트 1: 주식 시세 + 체결 + 종목정보
            print("\n" + "=" * 80)
            print("테스트 1: 주식 시세(0A) + 체결(0B) + 종목정보(0g) - 삼성전자")
            print("=" * 80)
            success = await self.register_realtime(
                items=["005930"],
                types=["0A", "0B", "0g"]
            )
            if success:
                await self.receive_messages(duration=15)

            # 테스트 2: 주식 호가잔량 + 우선호가
            print("\n" + "=" * 80)
            print("테스트 2: 주식 호가잔량(0D) + 우선호가(0C) - 삼성전자, 현대차")
            print("=" * 80)
            success = await self.register_realtime(
                items=["005930", "005380"],
                types=["0D", "0C"],
                refresh="0"  # 기존 등록 제거하고 새로 등록
            )
            if success:
                await self.receive_messages(duration=15)

            # 테스트 3: 업종지수 + 업종등락
            print("\n" + "=" * 80)
            print("테스트 3: 업종지수(0J) + 업종등락(0U) - KOSPI, KOSDAQ")
            print("=" * 80)
            success = await self.register_realtime(
                items=["0001", "1001"],  # KOSPI, KOSDAQ
                types=["0J", "0U"],
                refresh="0"
            )
            if success:
                await self.receive_messages(duration=10)

            # 테스트 4: 주식예상체결 + 시간외호가
            print("\n" + "=" * 80)
            print("테스트 4: 주식예상체결(0H) + 시간외호가(0E) - 삼성전자")
            print("=" * 80)
            print("⚠️ 주의: 장 시작 전/후에만 데이터 수신됨")
            success = await self.register_realtime(
                items=["005930"],
                types=["0H", "0E"],
                refresh="0"
            )
            if success:
                await self.receive_messages(duration=10)

            # 테스트 5: 거래원 + 프로그램매매 + VI
            print("\n" + "=" * 80)
            print("테스트 5: 당일거래원(0F) + 프로그램매매(0w) + VI발동/해제(1h) - 삼성전자")
            print("=" * 80)
            success = await self.register_realtime(
                items=["005930"],
                types=["0F", "0w", "1h"],
                refresh="0"
            )
            if success:
                await self.receive_messages(duration=10)

            # 테스트 6: ETF NAV
            print("\n" + "=" * 80)
            print("테스트 6: ETF NAV(0G) - KODEX 200")
            print("=" * 80)
            success = await self.register_realtime(
                items=["069500"],  # KODEX 200
                types=["0G"],
                refresh="0"
            )
            if success:
                await self.receive_messages(duration=10)

            # 테스트 7: ELW 이론가 + 지표
            print("\n" + "=" * 80)
            print("테스트 7: ELW 이론가(0m) + ELW 지표(0u)")
            print("=" * 80)
            print("⚠️ 주의: ELW 종목에만 적용됨")
            success = await self.register_realtime(
                items=[""],  # ELW 종목코드가 필요함
                types=["0m", "0u"],
                refresh="0"
            )
            if success:
                await self.receive_messages(duration=5)

            # 테스트 8: 장시작시간
            print("\n" + "=" * 80)
            print("테스트 8: 장시작시간(0s)")
            print("=" * 80)
            success = await self.register_realtime(
                items=[""],
                types=["0s"],
                refresh="0"
            )
            if success:
                await self.receive_messages(duration=5)

            # 테스트 9: 주문체결 + 잔고 (계좌 기반)
            print("\n" + "=" * 80)
            print("테스트 9: 주문체결(00) + 잔고(04) - 계좌 기반")
            print("=" * 80)
            print("⚠️ 주의: 실제 주문/체결이 발생해야 데이터 수신됨")
            success = await self.register_realtime(
                items=[""],  # 계좌 기반이므로 빈 문자열
                types=["00", "04"],
                refresh="0"
            )
            if success:
                await self.receive_messages(duration=10)

        finally:
            await self.disconnect()

        print("\n" + "=" * 80)
        print("테스트 완료")
        print("=" * 80)


async def main():
    """메인 함수"""
    tester = WebSocketTesterV2()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    # 결과 저장 디렉토리 생성
    result_dir = Path(__file__).parent / 'test_results'
    result_dir.mkdir(exist_ok=True)

    # 결과 파일명
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = result_dir / f'websocket_test_v2_{timestamp}.txt'

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
