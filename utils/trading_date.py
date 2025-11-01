"""
utils/trading_date.py
거래일 계산 유틸리티
"""
from datetime import datetime, timedelta


def get_last_trading_date() -> str:
    """
    시장 탐색을 위한 최근 거래일 반환

    규칙:
    - 평일 08:00 ~ 23:59 → 그날 날짜 사용
    - 평일 00:00 ~ 07:59 → 전날 날짜 사용
    - 토요일 → 금요일 날짜 사용
    - 일요일 → 금요일 날짜 사용

    Returns:
        YYYYMMDD 형식의 날짜 문자열
    """
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()  # 0=월요일, 6=일요일

    # 기준 날짜
    target_date = now

    # 평일 새벽 시간 (00:00 ~ 07:59)
    if current_weekday < 5 and current_hour < 8:
        # 전날 사용
        target_date = now - timedelta(days=1)
        # 만약 전날이 일요일이면 금요일로
        if target_date.weekday() == 6:
            target_date = target_date - timedelta(days=2)

    # 토요일
    elif current_weekday == 5:
        # 금요일 사용
        target_date = now - timedelta(days=1)

    # 일요일
    elif current_weekday == 6:
        # 금요일 사용
        target_date = now - timedelta(days=2)

    # 평일 08:00 이후는 그날 날짜 사용

    return target_date.strftime('%Y%m%d')


def get_trading_date_with_fallback(days_back: int = 5) -> list:
    """
    최근 거래일부터 여러 날짜를 반환 (폴백용)

    Args:
        days_back: 과거 며칠까지 반환할지

    Returns:
        날짜 리스트 (최근 날짜부터)
    """
    dates = []
    last_trading_date_str = get_last_trading_date()
    last_trading_date = datetime.strptime(last_trading_date_str, '%Y%m%d')

    current_date = last_trading_date
    count = 0

    while count < days_back:
        # 주말 제외
        if current_date.weekday() < 5:
            dates.append(current_date.strftime('%Y%m%d'))
            count += 1
        current_date = current_date - timedelta(days=1)

    return dates


def is_market_hours() -> bool:
    """
    현재가 장 운영 시간인지 확인

    Returns:
        장 운영 시간 여부
    """
    now = datetime.now()
    current_weekday = now.weekday()
    current_hour = now.hour
    current_minute = now.minute

    # 주말은 무조건 False
    if current_weekday >= 5:
        return False

    # 평일 09:00 ~ 15:30
    if current_hour == 9:
        return True
    elif 10 <= current_hour < 15:
        return True
    elif current_hour == 15 and current_minute <= 30:
        return True

    return False


def is_after_market_hours() -> bool:
    """
    장 마감 후인지 확인 (장마감 후 ~ 자정)

    Returns:
        장 마감 후 여부
    """
    now = datetime.now()
    current_weekday = now.weekday()
    current_hour = now.hour
    current_minute = now.minute

    # 주말은 False
    if current_weekday >= 5:
        return False

    # 평일 15:30 이후 ~ 23:59
    if current_hour > 15:
        return True
    elif current_hour == 15 and current_minute > 30:
        return True

    return False


def should_use_test_mode() -> bool:
    """
    테스트 모드를 사용해야 하는지 확인

    조건:
    - 휴일 (토요일, 일요일)
    - 평일 오후 8시(20:00) ~ 오전 8시(08:00)

    Returns:
        테스트 모드 사용 여부
    """
    now = datetime.now()
    current_weekday = now.weekday()  # 0=월요일, 6=일요일
    current_hour = now.hour

    # 주말은 항상 테스트 모드
    if current_weekday >= 5:
        return True

    # 평일: 20:00 ~ 23:59 또는 00:00 ~ 07:59
    if current_hour >= 20 or current_hour < 8:
        return True

    return False


__all__ = [
    'get_last_trading_date',
    'get_trading_date_with_fallback',
    'is_market_hours',
    'is_after_market_hours',
    'should_use_test_mode'
]
