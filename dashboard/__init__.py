"""
dashboard 패키지
웹 대시보드
"""
# Pro Dashboard를 기본으로 사용
from .dashboard_pro import run_dashboard, create_app

__all__ = ['run_dashboard', 'create_app']