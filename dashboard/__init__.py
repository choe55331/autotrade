"""
dashboard 패키지
웹 대시보드
"""
# Ultra Premium Dashboard를 기본으로 사용 (v2.0)
from .dashboard_ultra import run_dashboard, create_app

__all__ = ['run_dashboard', 'create_app']