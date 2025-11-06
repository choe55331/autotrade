"""
utils/time_utils.py
시간 관련 유틸리티

시간 파싱, 거래 시간 검증 등의 유틸리티 제공
"""
import logging
from datetime import datetime, time, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def parse_time_string(time_str: str) -> Optional[time]:
    """
    시간 문자열을 time 객체로 변환

    Args:
        time_str: 시간 문자열 (예: "09:00", "15:30")

    Returns:
        time 객체 (파싱 실패시 None)
    """
    if not time_str:
        logger.warning("Empty time string provided")
        return None

    try:
        # "HH:MM" 형식
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                hour = int(parts[0])
                minute = int(parts[1])
                return time(hour, minute)
            elif len(parts) == 3:
                hour = int(parts[0])
                minute = int(parts[1])
                second = int(parts[2])
                return time(hour, minute, second)

        # "HHMM" 형식 (4자리)
        elif len(time_str) == 4:
            hour = int(time_str[:2])
            minute = int(time_str[2:])
            return time(hour, minute)

        # "HHMMSS" 형식 (6자리)
        elif len(time_str) == 6:
            hour = int(time_str[:2])
            minute = int(time_str[2:4])
            second = int(time_str[4:])
            return time(hour, minute, second)

        else:
            logger.warning(f"Invalid time format: {time_str}")
            return None

    except (ValueError, IndexError) as e:
        logger.error(f"Failed to parse time string '{time_str}': {e}")
        return None


def get_market_open_time() -> time:
    """
    정규 시장 개장 시간 반환

    Returns:
        개장 시간 (09:00)
    """
    return time(9, 0)


def get_market_close_time() -> time:
    """
    정규 시장 폐장 시간 반환

    Returns:
        폐장 시간 (15:30)
    """
    return time(15, 30)


def get_market_lunch_start_time() -> time:
    """
    장중 점심시간 시작 시간 반환

    Returns:
        점심시간 시작 (12:00)
    """
    return time(12, 0)


def get_market_lunch_end_time() -> time:
    """
    장중 점심시간 종료 시간 반환

    Returns:
        점심시간 종료 (13:00)
    """
    return time(13, 0)


def is_market_hours(current_time: Optional[time] = None) -> bool:
    """
    현재 시간이 정규 거래 시간인지 확인

    Args:
        current_time: 확인할 시간 (None이면 현재 시간)

    Returns:
        거래 시간 여부
    """
    if current_time is None:
        current_time = datetime.now().time()

    market_open = get_market_open_time()
    market_close = get_market_close_time()

    return market_open <= current_time <= market_close


def is_lunch_time(current_time: Optional[time] = None) -> bool:
    """
    현재 시간이 점심시간인지 확인

    Args:
        current_time: 확인할 시간 (None이면 현재 시간)

    Returns:
        점심시간 여부
    """
    if current_time is None:
        current_time = datetime.now().time()

    lunch_start = get_market_lunch_start_time()
    lunch_end = get_market_lunch_end_time()

    return lunch_start <= current_time < lunch_end


def is_active_trading_hours(current_time: Optional[time] = None) -> bool:
    """
    현재 시간이 활발한 거래 시간인지 확인 (점심시간 제외)

    Args:
        current_time: 확인할 시간 (None이면 현재 시간)

    Returns:
        활발한 거래 시간 여부
    """
    if current_time is None:
        current_time = datetime.now().time()

    return is_market_hours(current_time) and not is_lunch_time(current_time)


def get_market_open_datetime() -> datetime:
    """
    오늘 시장 개장 시간 (datetime) 반환

    Returns:
        오늘 개장 datetime
    """
    today = datetime.now().date()
    market_open = get_market_open_time()
    return datetime.combine(today, market_open)


def get_market_close_datetime() -> datetime:
    """
    오늘 시장 폐장 시간 (datetime) 반환

    Returns:
        오늘 폐장 datetime
    """
    today = datetime.now().date()
    market_close = get_market_close_time()
    return datetime.combine(today, market_close)


def get_time_until_market_open() -> timedelta:
    """
    시장 개장까지 남은 시간 계산

    Returns:
        남은 시간 (timedelta)
    """
    now = datetime.now()
    market_open = get_market_open_datetime()

    # 이미 개장 시간이 지났으면 다음 날 개장 시간으로
    if now >= market_open:
        market_open += timedelta(days=1)

    return market_open - now


def get_time_until_market_close() -> timedelta:
    """
    시장 폐장까지 남은 시간 계산

    Returns:
        남은 시간 (timedelta)
    """
    now = datetime.now()
    market_close = get_market_close_datetime()

    # 이미 폐장 시간이 지났으면 다음 날 폐장 시간으로
    if now >= market_close:
        market_close += timedelta(days=1)

    return market_close - now


def format_time_delta(td: timedelta) -> str:
    """
    timedelta를 읽기 쉬운 문자열로 변환

    Args:
        td: timedelta 객체

    Returns:
        포맷된 문자열 (예: "2시간 30분")
    """
    total_seconds = int(td.total_seconds())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}시간")
    if minutes > 0:
        parts.append(f"{minutes}분")
    if seconds > 0 and hours == 0:  # 시간 단위가 있으면 초는 생략
        parts.append(f"{seconds}초")

    return " ".join(parts) if parts else "0초"


def get_trading_session() -> str:
    """
    현재 거래 세션 확인

    Returns:
        세션 종류 ("morning", "lunch", "afternoon", "closed")
    """
    now = datetime.now().time()

    if now < get_market_open_time():
        return "pre_market"
    elif now < get_market_lunch_start_time():
        return "morning"
    elif now < get_market_lunch_end_time():
        return "lunch"
    elif now < get_market_close_time():
        return "afternoon"
    else:
        return "after_hours"


def is_near_market_close(minutes: int = 30, current_time: Optional[time] = None) -> bool:
    """
    시장 마감이 임박했는지 확인

    Args:
        minutes: 몇 분 전부터 임박으로 판단할지 (기본: 30분)
        current_time: 확인할 시간 (None이면 현재 시간)

    Returns:
        마감 임박 여부
    """
    if current_time is None:
        current_time = datetime.now().time()

    market_close = get_market_close_time()

    # market_close에서 minutes분 전 시간 계산
    close_threshold = (
        datetime.combine(datetime.today(), market_close) -
        timedelta(minutes=minutes)
    ).time()

    return close_threshold <= current_time < market_close


def is_near_market_open(minutes: int = 10, current_time: Optional[time] = None) -> bool:
    """
    시장 개장이 임박했는지 확인

    Args:
        minutes: 몇 분 전부터 임박으로 판단할지 (기본: 10분)
        current_time: 확인할 시간 (None이면 현재 시간)

    Returns:
        개장 임박 여부
    """
    if current_time is None:
        current_time = datetime.now().time()

    market_open = get_market_open_time()

    # market_open 이전 minutes분 계산
    open_threshold = (
        datetime.combine(datetime.today(), market_open) -
        timedelta(minutes=minutes)
    ).time()

    return open_threshold <= current_time < market_open


def get_seconds_since_market_open(current_time: Optional[datetime] = None) -> int:
    """
    시장 개장 이후 경과 시간 (초)

    Args:
        current_time: 확인할 시간 (None이면 현재 시간)

    Returns:
        경과 시간 (초)
    """
    if current_time is None:
        current_time = datetime.now()

    market_open = get_market_open_datetime()

    if current_time < market_open:
        return 0

    elapsed = current_time - market_open
    return int(elapsed.total_seconds())


__all__ = [
    'parse_time_string',
    'get_market_open_time',
    'get_market_close_time',
    'get_market_lunch_start_time',
    'get_market_lunch_end_time',
    'is_market_hours',
    'is_lunch_time',
    'is_active_trading_hours',
    'get_market_open_datetime',
    'get_market_close_datetime',
    'get_time_until_market_open',
    'get_time_until_market_close',
    'format_time_delta',
    'get_trading_session',
    'is_near_market_close',
    'is_near_market_open',
    'get_seconds_since_market_open',
]
