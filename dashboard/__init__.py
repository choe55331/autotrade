"""
dashboard 패키지
웹 대시보드
"""
# Apple-Style Dashboard를 기본으로 사용 (v3.0)
from .app_apple import run_dashboard, create_app

__all__ = ['run_dashboard', 'create_app']