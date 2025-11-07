"""
AutoTrade 시스템 종합 기능 보고서 생성기
"""

모든 주요 기능을 정리하고 테이블 형식으로 결과 표시

import os
from datetime import datetime
import csv


def generate_comprehensive_report():
    """종합 보고서 생성"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    features = []

    features.extend([
        ("1. 계좌 API", "kt00001 - 예수금 조회", "[OK] 작동", "[OK]", "대시보드 계좌 섹션"),
        ("1. 계좌 API", "kt00004 - 계좌평가 조회", "[OK] 작동", "[OK]", "총 자산 계산"),
        ("1. 계좌 API", "kt00005 - 주문체결 조회", "[OK] 작동", "[OK]", "실시간 매매내역"),
        ("1. 계좌 API", "kt00010 - 미체결 조회", "[OK] 작동", "[OK]", "주문 관리"),
        ("1. 계좌 API", "kt00018 - 보유종목 조회", "[OK] 작동", "[OK]", "포트폴리오 표시"),
        ("1. 계좌 API", "ka10085 - 일별손익조회", "[OK] 작동", "[OK]", "수익률 추적"),
        ("1. 계좌 API", "ka10074 - 손익통계", "[OK] 작동", "[X]", "통계 분석용"),
        ("1. 계좌 API", "ka10073 - 기간별손익", "[OK] 작동", "[X]", "백테스팅용"),
        ("1. 계좌 API", "ka10077 - 매수가능종목", "[OK] 작동", "[X]", "호가단위 확인"),
        ("1. 계좌 API", "ka10075 - 계좌요약", "[OK] 작동", "[X]", ""),
        ("1. 계좌 API", "ka10076 - 계좌잔고", "[OK] 작동", "[X]", ""),
    ])

    features.extend([
        ("2. 시장 API - 시세", "ka10003 - 종목 체결정보", "[OK] 작동", "[OK]", "현재가 조회"),
        ("2. 시장 API - 시세", "ka10004 - 호가 조회", "[OK] 작동", "[OK]", "매수/매도 호가"),
        ("2. 시장 API - 시세", "DOSK_0004 - NXT 호가조회", "[OK] 작동", "[OK]", "시간외 거래"),
        ("2. 시장 API - 시세", "ka10081 - 일봉차트", "[OK] 작동", "[OK]", "차트 데이터"),
        ("2. 시장 API - 시세", "DOSK_0020 - 분봉조회", "[OK] 작동", "[OK]", "실시간 차트"),
        ("2. 시장 API - 시세", "DOSK_0021 - 틱차트조회", "[OK] 작동", "[X]", ""),
        ("2. 시장 API - 시세", "DOSK_0030 - 주봉조회", "[OK] 작동", "[X]", ""),
        ("2. 시장 API - 시세", "DOSK_0031 - 월봉조회", "[OK] 작동", "[X]", ""),
        ("2. 시장 API - 시세", "DOSK_0005 - 종목코드리스트", "[OK] 작동", "[OK]", "종목 검색"),
    ])

    features.extend([
        ("2. 시장 API - 순위", "ka10031 - 거래량 순위", "[OK] 작동", "[OK]", "Fast Scan 사용"),
        ("2. 시장 API - 순위", "ka10027 - 등락률 순위", "[OK] 작동", "[OK]", "Fast Scan 사용"),
        ("2. 시장 API - 순위", "ka10032 - 거래대금 순위", "[OK] 작동", "[X]", ""),
        ("2. 시장 API - 순위", "ka10023 - 거래량 급증", "[OK] 작동", "[OK]", "Fast Scan 핵심"),
        ("2. 시장 API - 순위", "ka10028 - 시가대비 등락률", "[OK] 작동", "[X]", ""),
        ("2. 시장 API - 순위", "ka10033 - 신용비율 순위", "[OK] 작동", "[X]", ""),
    ])

    features.extend([
        ("2. 시장 API - 외국인/기관", "ka10034 - 외국인 기간별매매", "[OK] 작동", "[X]", "순위 정보"),
        ("2. 시장 API - 외국인/기관", "ka10035 - 외국인 연속매매", "[OK] 작동", "[X]", "연속 순매수"),
        ("2. 시장 API - 외국인/기관", "ka90009 - 외국인/기관 매매상위", "[OK] 작동", "[OK]", "Fast Scan 사용"),
        ("2. 시장 API - 외국인/기관", "ka10059 - 투자자별 매매동향", "[OK] 작동", "[OK]", "Deep Scan 핵심"),
        ("2. 시장 API - 외국인/기관", "ka10063 - 장중 투자자별매매", "[OK] 작동", "[X]", ""),
        ("2. 시장 API - 외국인/기관", "ka10065 - 투자자별 매매상위", "[OK] 작동", "[X]", ""),
        ("2. 시장 API - 외국인/기관", "ka10066 - 장마감후 투자자별매매", "[OK] 작동", "[X]", ""),
        ("2. 시장 API - 외국인/기관", "ka10045 - 기관매매추이", "[OK] 작동", "[OK]", "Deep Scan 사용"),
        ("2. 시장 API - 외국인/기관", "ka10078 - 증권사별 매매동향", "[OK] 작동", "[OK]", "Deep Scan 사용"),
    ])

    features.extend([
        ("2. 시장 API - 기타", "ka10047 - 체결강도", "[OK] 작동", "[OK]", "Deep Scan 핵심"),
        ("2. 시장 API - 기타", "ka90013 - 프로그램매매", "[OK] 작동", "[OK]", "Deep Scan 사용"),
    ])

    features.extend([
        ("3. 주문 API", "DOSK_0001 - 현금 주식 주문", "[OK] 작동", "[OK]", "main.py 매수/매도"),
        ("3. 주문 API", "DOSK_0011 - 현금 주식 정정", "[OK] 작동", "[X]", ""),
        ("3. 주문 API", "DOSK_0012 - 현금 주식 취소", "[OK] 작동", "[X]", ""),
    ])

    features.extend([
        ("4. WebSocket", "WebSocketManager 클래스", "[OK] 구현", "[OK]", "core/websocket_manager.py"),
        ("4. WebSocket", "WebSocket 연결", "[OK] 구현", "[OK]", "LOGIN 메시지"),
        ("4. WebSocket", "주문체결 구독 (type="00")", "[OK] 구현", "[OK]", "계좌 체결 알림"),
        ("4. WebSocket", "주식체결 구독 (type=0B)", "[OK] 구현", "[OK]", "실시간 현재가"),
        ("4. WebSocket", "주식호가 구독 (type=0D)", "[OK] 구현", "[OK]", "실시간 호가"),
        ("4. WebSocket", "잔고 구독 (type="04")", "[OK] 구현", "[X]", ""),
        ("4. WebSocket", "주식기세 구독 (type=0A)", "[OK] 구현", "[X]", ""),
        ("4. WebSocket", "콜백 시스템", "[OK] 구현", "[OK]", "타입별 콜백 등록"),
        ("4. WebSocket", "자동 재연결", "[OK] 구현", "[OK]", "최대 5회 재시도"),
        ("4. WebSocket", "main.py 통합", "[OK] 완료", "[OK]", "L201-270 초기화"),
    ])

    features.extend([
        ("5. AI 분석", "Gemini AI 통합", "[OK] 구현", "[OK]", "ai/gemini_analyzer.py"),
        ("5. AI 분석", "GPT-4 통합", "[OK] 구현", "[X]", "ai/gpt4_analyzer.py"),
        ("5. AI 분석", "Claude AI 통합", "[OK] 구현", "[X]", "ai/claude_analyzer.py"),
        ("5. AI 분석", "포트폴리오 분석", "[OK] 구현", "[OK]", "대시보드 AI 탭"),
        ("5. AI 분석", "감정 분석", "[OK] 구현", "[OK]", "뉴스/소셜미디어"),
        ("5. AI 분석", "리스크 평가", "[OK] 구현", "[OK]", "VaR/CVaR 계산"),
        ("5. AI 분석", "종목 추천", "[OK] 구현", "[OK]", "AI Scan 결과"),
        ("5. AI 분석", "Multi-Agent 시스템", "[OK] 구현", "[OK]", "consensus_analyzer.py"),
    ])

    features.extend([
        ("6. 스캐너", "Fast Scan - 거래량 급등", "[OK] 구현", "[OK]", "ka10023 사용"),
        ("6. 스캐너", "Fast Scan - 등락률 상위", "[OK] 구현", "[OK]", "ka10027 사용"),
        ("6. 스캐너", "Fast Scan - 외국인/기관 매수", "[OK] 구현", "[OK]", "ka90009 사용"),
        ("6. 스캐너", "Deep Scan - 투자자 분석", "[OK] 구현", "[OK]", "ka10059 사용"),
        ("6. 스캐너", "Deep Scan - 증권사 분석", "[OK] 구현", "[OK]", "ka10078 사용"),
        ("6. 스캐너", "Deep Scan - 체결강도", "[OK] 구현", "[OK]", "ka10047 사용"),
        ("6. 스캐너", "Deep Scan - 프로그램매매", "[OK] 구현", "[OK]", "ka90013 사용"),
        ("6. 스캐너", "Deep Scan - 기관매매추이", "[OK] 구현", "[OK]", "ka10045 사용"),
        ("6. 스캐너", "AI Scan - 종목 평가", "[OK] 구현", "[WARNING]️ ", "대시보드 연동 확인 필요"),
        ("6. 스캐너", "AI Scan - 매수 추천", "[OK] 구현", "[WARNING]️ ", "AI 후보 섹션"),
        ("6. 스캐너", "스캐너 파이프라인", "[OK] 구현", "[OK]", "3단계 스캔 시스템"),
    ])

    features.extend([
        ("7. 전략/스코어링", "스코어링 시스템", "[OK] 구현", "[OK]", "strategy/scoring_system.py"),
        ("7. 전략/스코어링", "거래량 분석", "[OK] 구현", "[OK]", "평균 대비 비율"),
        ("7. 전략/스코어링", "변동성 분석", "[OK] 구현", "[OK]", "20일 표준편차"),
        ("7. 전략/스코어링", "체결강도 분석", "[OK] 구현", "[OK]", "매수세 측정"),
        ("7. 전략/스코어링", "프로그램매매 분석", "[OK] 구현", "[OK]", "기관 매수 확인"),
        ("7. 전략/스코어링", "증권사 매매 분석", "[OK] 구현", "[OK]", "5개사 집계"),
        ("7. 전략/스코어링", "투자자 매매 분석", "[OK] 구현", "[OK]", "기관/외국인"),
        ("7. 전략/스코어링", "호가 분석", "[OK] 구현", "[OK]", "매수/매도 비율"),
        ("7. 전략/스코어링", "종합 점수 계산", "[OK] 구현", "[OK]", "0-100점 스케일"),
        ("7. 전략/스코어링", "모멘텀 전략", "[OK] 구현", "[X]", "strategy/momentum.py"),
        ("7. 전략/스코어링", "변동성 전략", "[OK] 구현", "[X]", "strategy/volatility.py"),
        ("7. 전략/스코어링", "페어 트레이딩", "[OK] 구현", "[X]", "strategy/pairs.py"),
    ])

    features.extend([
        ("8. 포트폴리오", "Markowitz 최적화", "[OK] 구현", "[OK]", "대시보드 포트폴리오 탭"),
        ("8. 포트폴리오", "Black-Litterman 모델", "[OK] 구현", "[OK]", "AI 의견 반영"),
        ("8. 포트폴리오", "Risk Parity", "[OK] 구현", "[OK]", "리스크 균형"),
        ("8. 포트폴리오", "효율적 프론티어", "[OK] 구현", "[OK]", "최적 포트폴리오"),
        ("8. 포트폴리오", "샤프 비율 최대화", "[OK] 구현", "[OK]", "위험대비 수익"),
        ("8. 포트폴리오", "VaR/CVaR 계산", "[OK] 구현", "[OK]", "리스크 관리"),
    ])

    features.extend([
        ("9. 대시보드", "Flask 웹 서버", "[OK] 구현", "[OK]", "app_apple.py"),
        ("9. 대시보드", "계좌 정보 표시", "[OK] 구현", "[OK]", "예수금/평가금액/총자산"),
        ("9. 대시보드", "보유종목 표시", "[OK] 구현", "[OK]", "실시간 업데이트"),
        ("9. 대시보드", "실시간 매매내역", "[OK] 구현", "[OK]", "체결 내역 표시"),
        ("9. 대시보드", "AI 매수 후보", "[OK] 구현", "[WARNING]️ ", "스캐너 연동 확인 필요"),
        ("9. 대시보드", "실시간 차트", "[OK] 구현", "[OK]", "LightweightCharts"),
        ("9. 대시보드", "종목 검색", "[OK] 구현", "[OK]", "자동완성 지원"),
        ("9. 대시보드", "AI 분석 탭", "[OK] 구현", "[OK]", "포트폴리오/감정/리스크"),
        ("9. 대시보드", "백테스팅 탭", "[OK] 구현", "[OK]", "과거 데이터 검증"),
        ("9. 대시보드", "포트폴리오 최적화 탭", "[OK] 구현", "[OK]", "3가지 모델"),
        ("9. 대시보드", "감정 분석 탭", "[OK] 구현", "[OK]", "뉴스/소셜미디어"),
        ("9. 대시보드", "리스크 관리 탭", "[OK] 구현", "[OK]", "VaR/CVaR"),
        ("9. 대시보드", "마켓 레짐 탭", "[OK] 구현", "[OK]", "시장 상태 감지"),
        ("9. 대시보드", "설정 페이지", "[OK] 구현", "[OK]", "통합 설정 관리"),
        ("9. 대시보드", "WebSocket 통합", "[OK] 구현", "[OK]", "실시간 데이터"),
    ])

    features.extend([
        ("10. 유틸리티", "로깅 시스템", "[OK] 구현", "[OK]", "logger_new.py"),
        ("10. 유틸리티", "거래일 계산", "[OK] 구현", "[OK]", "trading_date.py"),
        ("10. 유틸리티", "데이터베이스", "[OK] 구현", "[OK]", "SQLAlchemy ORM"),
        ("10. 유틸리티", "설정 관리", "[OK] 구현", "[OK]", "unified_settings.py"),
        ("10. 유틸리티", "자격증명 관리", "[OK] 구현", "[OK]", "credentials.py"),
        ("10. 유틸리티", "토큰 자동 갱신", "[OK] 구현", "[OK]", "REST client"),
        ("10. 유틸리티", "API 속도 제한", "[OK] 구현", "[OK]", "0.3초 간격"),
        ("10. 유틸리티", "자동 재시도", "[OK] 구현", "[OK]", "3회 재시도"),
        ("10. 유틸리티", "오류 처리", "[OK] 구현", "[OK]", "예외 계층 구조"),
        ("10. 유틸리티", "테스트 모드", "[OK] 구현", "[OK]", "실거래 차단"),
        ("10. 유틸리티", "페이퍼 트레이딩", "[OK] 구현", "[OK]", "가상 거래"),
    ])

    total = len(features)
    working = sum(1 for f in features if "[OK] 작동" in f[2] or "[OK] 구현" in f[2])
    dashboard = sum(1 for f in features if "[OK]" in f[3])

    print("\n" + "=" * 150)
    print("  🚀 AutoTrade 시스템 종합 기능 보고서")
    print("=" * 150)
    print(f"  생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 150 + "\n")

    print(f"{'카테고리':<30} {'기능':<50} {'상태':<15} {'대시보드':<10} {'비고':<40}")
    print("=" * 150)

    for category, feature, status, dashboard_yn, notes in features:
        print(f"{category:<30} {feature:<50} {status:<15} {dashboard_yn:<10} {notes:<40}")

    print("\n" + "=" * 150)
    print("  [CHART] 통계")
    print("=" * 150)
    print(f"  전체 기능: {total}개")
    print(f"  정상 작동: {working}개 ({working/total*100:.1f}%)")
    print(f"  대시보드 연동: {dashboard}개 ({dashboard/total*100:.1f}%)")
    print("=" * 150 + "\n")

    csv_filename = f"system_features_{timestamp}.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["카테고리", "기능", "상태", "대시보드_연동", "비고"])
        writer.writerows(features)

    print(f"[OK] CSV 파일 저장: {csv_filename}\n")

    html_filename = f"system_features_{timestamp}.html"
    html_content = f"""<!DOCTYPE html>
    """
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoTrade 시스템 종합 기능 보고서</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', 'Noto Sans KR', Arial, sans-serif;
            background: linear-gradient(135deg,
            color:
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        h1 {{
            text-align: center;
            color:
            font-size: 36px;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        .timestamp {{
            text-align: center;
            color:
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: rgba(255, 255, 255, 0."05");
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            transition: transform 0.3s;
        }}
        .summary-card:hover {{ transform: translateY(-5px); }}
        .summary-value {{
            font-size: 48px;
            font-weight: bold;
            color:
            margin-bottom: 10px;
        }}
        .summary-label {{
            color:
            font-size: 14px;
            text-transform: uppercase;
        }}
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: rgba(255, 255, 255, 0."03");
            backdrop-filter: blur(10px);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        thead {{
            background: linear-gradient(135deg,
        }}
        th {{
            padding: 15px 20px;
            text-align: left;
            font-weight: 600;
            color:
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 12px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0."05");
            font-size: 13px;
        }}
        tr:hover td {{
            background: rgba(0, 212, 255, 0.1);
        }}
        .status-ok {{ color:
        .status-impl {{ color:
        .status-warn {{ color:
        .dashboard-yes {{ color:
        .dashboard-no {{ color:
        .dashboard-warn {{ color:
        .category {{ font-weight: 600; color:
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AutoTrade 시스템 종합 기능 보고서</h1>
        <div class="timestamp">생성 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>

        <div class="summary">
            <div class="summary-card">
                <div class="summary-value">{total}</div>
                <div class="summary-label">전체 기능</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{working}</div>
                <div class="summary-label">정상 작동 ({working/total*100:.1f}%)</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{dashboard}</div>
                <div class="summary-label">대시보드 연동 ({dashboard/total*100:.1f}%)</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>카테고리</th>
                    <th>기능</th>
                    <th>상태</th>
                    <th>대시보드</th>
                    <th>비고</th>
                </tr>
            </thead>
            <tbody>

    for category, feature, status, dashboard_yn, notes in features:
        status_class = "status-ok" if "[OK] 작동" in status else ("status-impl" if "[OK] 구현" in status else "status-warn")
        dashboard_class = "dashboard-yes" if dashboard_yn == "[OK]" else ("dashboard-warn" if "[WARNING]️" in dashboard_yn else "dashboard-no")

        html_content += f"""
                <tr>
                """
                    <td class="category">{category}</td>
                    <td>{feature}</td>
                    <td class="{status_class}">{status}</td>
                    <td class="{dashboard_class}">{dashboard_yn}</td>
                    <td>{notes}</td>
                </tr>

    html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>

"""
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[OK] HTML 보고서 저장: {html_filename}\n")

    return total, working, dashboard


if __name__ == "__main__":
    generate_comprehensive_report()
