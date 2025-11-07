from typing import Dict, Any

STOCK_ANALYSIS_PROMPT_V7 = """당신은 20년 경력의 퀀트 헤지펀드 매니저입니다.

다음 한국 주식을 심층 분석하여 매수/보유/매도 결정을 내려주세요.

"""
=== 종목 기본 정보 ===
종목명: {stock_name} ({stock_code})
현재가: {current_price:,}원
등락률: {change_rate:+.2f}%
거래량: {volume:,}주
거래대금: {traded_amount:,}원

=== 기술적 지표 분석 ===
{technical_indicators}

=== 시장 참여자 동향 ===
기관 순매수: {institutional_net_buy:,}원
외국인 순매수: {foreign_net_buy:,}원
프로그램 매매: {program_net_buy:,}원
매수호가 강도: {bid_ask_ratio:.2f}
{investor_analysis}

=== 종합 평가 점수 (440점 만점) ===
총점: {score}점 ({percentage:.1f}%)
등급: {grade}
{score_breakdown}

=== 시장 상황 ===
KOSPI: {kospi_index:,} ({kospi_change:+.2f}%)
시장 심리: {market_sentiment}
거래량 비교: 전일 대비 {volume_ratio:.1f}배
{market_context}

=== 현재 포트폴리오 ===
{portfolio_info}

=== 리스크 요인 ===
{risk_factors}

=== 분석 요구사항 ===

1. **기술적 분석**: 가격 추세, 지지/저항선, 모멘텀 지표 종합 평가
2. **시장 참여자 분석**: 기관/외국인/개인의 매매 동향이 시사하는 바
3. **거래량 분석**: 거래량 급증/감소의 의미와 가격 변동과의 관계
4. **리스크 평가**: 단기 급등 후 조정 가능성, 매물대 저항, 시장 전체 분위기
5. **타이밍 분석**: 지금 매수가 적절한지, 대기가 나은지, 분할 매수가 나은지
6. **목표가/손절가**: 합리적인 수익 실현 목표와 리스크 관리 포인트

**중요**: 다음 JSON 형식으로만 응답하세요.

```json
{{
  "signal": "buy" | "hold" | "sell",
  "confidence_level": "Very High" | "High" | "Medium" | "Low",
  "confidence_score": 0.0~100.0,
  "overall_score": 0.0~10.0,
  "reasons": [
    "구체적인 근거 1 (지표 수치 포함)",
    "구체적인 근거 2",
    "구체적인 근거 3"
  ],
  "risks": [
    "주요 리스크 요인 1",
    "주요 리스크 요인 2"
  ],
  "entry_strategy": "immediate" | "wait_pullback" | "split_buy" | "avoid",
  "target_price": 목표가 (숫자),
  "stop_loss": 손절가 (숫자),
  "holding_period": "단기(1-3일)" | "중기(1-2주)" | "장기(1개월+)",
  "detailed_reasoning": "종합 분석 (5-7문장, 구체적인 수치와 근거 포함)",
  "key_points": [
    "핵심 포인트 1",
    "핵심 포인트 2",
    "핵심 포인트 3"
  ]
}}
```"""

"""
def format_technical_indicators(indicators: Dict[str, Any]) -> str:
    if not indicators:
        return "기술적 지표 정보 없음"

    lines = []

    if 'ma5' in indicators and 'ma20' in indicators:
        ma5 = indicators['ma5']
        ma20 = indicators['ma20']
        ma_trend = "상승" if ma5 > ma20 else "하락"
        lines.append(f"이동평균선: MA5 {ma5:,}원, MA20 {ma20:,}원 ({ma_trend} 배열)")

    if 'rsi' in indicators:
        rsi = indicators['rsi']
        rsi_signal = "과매수" if rsi > 70 else "과매도" if rsi < 30 else "중립"
        lines.append(f"RSI(14): {rsi:.1f} ({rsi_signal})")

    if 'macd' in indicators:
        lines.append(f"MACD: {indicators['macd']:.2f}")

    if 'bollinger' in indicators:
        bb = indicators['bollinger']
        lines.append(f"볼린저밴드: 상단 {bb['upper']:,}원, 하단 {bb['lower']:,}원")

    if 'volume_ma' in indicators:
        lines.append(f"거래량 이동평균 대비: {indicators['volume_ratio']:.1f}배")

    return "\n".join(lines) if lines else "기술적 지표 계산 중"

def format_score_breakdown(breakdown: Dict[str, float]) -> str:
    if not breakdown:
        return ""

    lines = []
    for key, value in sorted(breakdown.items(), key=lambda x: -x[1]):
        percentage = (value / 44) * 100 if value > 0 else 0
        status = "🟢" if percentage >= 70 else "🟡" if percentage >= 50 else "🔴"
        lines.append(f"{status} {key}: {value:.1f}/44점 ({percentage:.0f}%)")

    return "\n".join(lines)

def format_investor_analysis(data: Dict[str, Any]) -> str:
    inst = data.get('institutional_net_buy', 0)
    foreign = data.get('foreign_net_buy', 0)

    lines = []

    if inst > 0 and foreign > 0:
        lines.append("[OK] 기관과 외국인이 동시 순매수 중 (강력한 상승 신호)")
    elif inst < 0 and foreign < 0:
        lines.append("[WARNING]️ 기관과 외국인이 동시 순매도 중 (약세 신호)")
    elif inst > 0:
        lines.append("🔵 기관 순매수 중 (외국인은 관망)")
    elif foreign > 0:
        lines.append("🌍 외국인 순매수 중 (기관은 관망)")
    else:
        lines.append("⚪ 주요 투자자 관망 중")

    bid_ask = data.get('bid_ask_ratio', 1.0)
    if bid_ask > 1.5:
        lines.append(f"💪 강한 매수세 (매수호가 {bid_ask:.2f}배)")
    elif bid_ask < 0.7:
        lines.append(f"[DOWN] 강한 매도세 (매수호가 {bid_ask:.2f}배)")

    return "\n".join(lines) if lines else ""

def format_market_context(market_data: Dict[str, Any]) -> str:
    lines = []

    market_trend = market_data.get('trend', '')
    if market_trend:
        lines.append(f"시장 추세: {market_trend}")

    sector_trend = market_data.get('sector_trend', '')
    if sector_trend:
        lines.append(f"업종 추세: {sector_trend}")

    volatility = market_data.get('volatility', '')
    if volatility:
        lines.append(f"변동성: {volatility}")

    return "\n".join(lines) if lines else ""

def format_risk_factors(data: Dict[str, Any]) -> str:
    risks = []

    change_rate = abs(data.get('change_rate', 0))
    if change_rate > 5:
        risks.append(f"[WARNING]️ 단기 급등/급락 ({change_rate:.1f}%) - 조정 가능성")

    volume_ratio = data.get('volume_ratio', 1.0)
    if volume_ratio > 3:
        risks.append(f"[WARNING]️ 거래량 급증 ({volume_ratio:.1f}배) - 단기 과열 주의")

    rsi = data.get('rsi', 50)
    if rsi > 75:
        risks.append(f"[WARNING]️ RSI 과매수 구간 ({rsi:.1f}) - 조정 대기 권장")
    elif rsi < 25:
        risks.append(f"[WARNING]️ RSI 과매도 구간 ({rsi:.1f}) - 추가 하락 가능")

    market_change = data.get('kospi_change', 0)
    if market_change < -1.5:
        risks.append(f"[WARNING]️ 시장 전체 약세 (KOSPI {market_change:+.2f}%)")

    if not risks:
        risks.append("[OK] 특별한 리스크 요인 없음")

    return "\n".join(risks)

def create_enhanced_prompt(
    stock_data: Dict[str, Any],
    score_info: Dict[str, Any],
    portfolio_info: str = "",
    market_data: Dict[str, Any] = None
) -> str:
    market_data = market_data or {}

    return STOCK_ANALYSIS_PROMPT_V7.format(
        stock_name=stock_data.get('stock_name', ''),
        stock_code=stock_data.get('stock_code', ''),
        current_price=stock_data.get('current_price', 0),
        change_rate=stock_data.get('change_rate', 0.0),
        volume=stock_data.get('volume', 0),
        traded_amount=stock_data.get('current_price', 0) * stock_data.get('volume', 0),
        technical_indicators=format_technical_indicators(stock_data.get('technical', {})),
        institutional_net_buy=stock_data.get('institutional_net_buy', 0),
        foreign_net_buy=stock_data.get('foreign_net_buy', 0),
        program_net_buy=stock_data.get('program_net_buy', 0),
        bid_ask_ratio=stock_data.get('bid_ask_ratio', 1.0),
        investor_analysis=format_investor_analysis(stock_data),
        score=score_info.get('score', 0),
        percentage=score_info.get('percentage', 0),
        grade=score_info.get('grade', 'C'),
        score_breakdown=format_score_breakdown(score_info.get('breakdown', {})),
        kospi_index=market_data.get('kospi_index', 2500),
        kospi_change=market_data.get('kospi_change', 0),
        market_sentiment=market_data.get('sentiment', '중립'),
        volume_ratio=stock_data.get('volume_ratio', 1.0),
        market_context=format_market_context(market_data),
        portfolio_info=portfolio_info or "보유 종목 없음",
        risk_factors=format_risk_factors(stock_data)
    )
