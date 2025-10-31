"""
dashboard 패키지
웹 대시보드

v4.2 AI-Powered Dashboard:
- 18 AI systems integrated
- 38 API endpoints
- Real-time trading with WebSocket
- Advanced portfolio optimization
- Multi-agent consensus system
"""
# Apple-Style Dashboard를 기본으로 사용 (v4.2)
from .app_apple import run_dashboard, create_app

__all__ = ['run_dashboard', 'create_app']