"""
dashboard/dashboard.py
Flask 기반 웹 대시보드
"""
import logging
from flask import Flask, render_template_string, jsonify, request
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def create_app(bot_instance=None):
    """
    Flask 앱 생성
    
    Args:
        bot_instance: 트레이딩 봇 인스턴스
    
    Returns:
        Flask app
    """
    app = Flask(__name__)
    app.config['bot'] = bot_instance
    
    # ==================== HTML 템플릿 ====================
    
    DASHBOARD_HTML = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>자동매매 대시보드</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            h1 {
                color: #333;
                font-size: 28px;
                margin-bottom: 10px;
            }
            .status {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            .status-badge {
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            .status-running { background: #10b981; color: white; }
            .status-stopped { background: #ef4444; color: white; }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .card h2 {
                color: #555;
                font-size: 18px;
                margin-bottom: 15px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .stat {
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }
            .stat:last-child { border-bottom: none; }
            .stat-label { color: #666; }
            .stat-value {
                font-weight: bold;
                color: #333;
            }
            .profit { color: #10b981; }
            .loss { color: #ef4444; }
            .controls {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            button {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }
            .btn-primary {
                background: #667eea;
                color: white;
            }
            .btn-primary:hover {
                background: #5568d3;
            }
            .btn-danger {
                background: #ef4444;
                color: white;
            }
            .btn-danger:hover {
                background: #dc2626;
            }
            .btn-success {
                background: #10b981;
                color: white;
            }
            .btn-success:hover {
                background: #059669;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }
            th {
                background: #f8f9fa;
                font-weight: bold;
                color: #555;
            }
            .refresh-info {
                text-align: center;
                color: white;
                margin-top: 20px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 자동매매 대시보드</h1>
                <div class="status">
                    <span class="status-badge" id="bot-status">로딩 중...</span>
                    <span id="last-update"></span>
                </div>
            </div>
            
            <div class="grid">
                <!-- 계좌 정보 -->
                <div class="card">
                    <h2>💰 계좌 정보</h2>
                    <div class="stat">
                        <span class="stat-label">총 자산</span>
                        <span class="stat-value" id="total-assets">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">보유 현금</span>
                        <span class="stat-value" id="cash">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">평가 금액</span>
                        <span class="stat-value" id="stocks-value">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">총 손익</span>
                        <span class="stat-value" id="profit-loss">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">수익률</span>
                        <span class="stat-value" id="profit-rate">-</span>
                    </div>
                </div>
                
                <!-- 포지션 정보 -->
                <div class="card">
                    <h2>📊 포지션 정보</h2>
                    <div class="stat">
                        <span class="stat-label">보유 종목 수</span>
                        <span class="stat-value" id="position-count">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">최대 포지션</span>
                        <span class="stat-value" id="max-positions">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">가용 슬롯</span>
                        <span class="stat-value" id="available-slots">-</span>
                    </div>
                </div>
                
                <!-- 매매 통계 -->
                <div class="card">
                    <h2>📈 매매 통계</h2>
                    <div class="stat">
                        <span class="stat-label">총 거래</span>
                        <span class="stat-value" id="total-trades">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">승률</span>
                        <span class="stat-value" id="win-rate">-</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">AI 분석 수</span>
                        <span class="stat-value" id="ai-analyses">-</span>
                    </div>
                </div>
            </div>
            
            <!-- 제어 패널 -->
            <div class="card">
                <h2>🎮 제어 패널</h2>
                <div class="controls">
                    <button class="btn-success" onclick="startBot()">▶️ 시작</button>
                    <button class="btn-danger" onclick="stopBot()">⏹️ 정지</button>
                    <button class="btn-primary" onclick="pauseBuy()">⏸️ 매수 중지</button>
                    <button class="btn-primary" onclick="resumeBuy()">▶️ 매수 재개</button>
                    <button class="btn-primary" onclick="refreshData()">🔄 새로고침</button>
                </div>
            </div>
            
            <!-- 보유 종목 -->
            <div class="card">
                <h2>📋 보유 종목</h2>
                <table>
                    <thead>
                        <tr>
                            <th>종목명</th>
                            <th>수량</th>
                            <th>매수가</th>
                            <th>현재가</th>
                            <th>손익</th>
                            <th>수익률</th>
                        </tr>
                    </thead>
                    <tbody id="holdings-table">
                        <tr><td colspan="6" style="text-align:center;">로딩 중...</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="refresh-info">
                ⏱️ 자동 새로고침: 10초마다 | 마지막 업데이트: <span id="update-time">-</span>
            </div>
        </div>
        
        <script>
            // 데이터 새로고침
            async function refreshData() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    updateDashboard(data);
                } catch (error) {
                    console.error('데이터 로드 실패:', error);
                }
            }
            
            // 대시보드 업데이트
            function updateDashboard(data) {
                // 상태
                const statusEl = document.getElementById('bot-status');
                if (data.is_running) {
                    statusEl.textContent = '🟢 실행 중';
                    statusEl.className = 'status-badge status-running';
                } else {
                    statusEl.textContent = '🔴 정지됨';
                    statusEl.className = 'status-badge status-stopped';
                }
                
                // 계좌 정보
                document.getElementById('total-assets').textContent = 
                    (data.account?.total_assets || 0).toLocaleString() + '원';
                document.getElementById('cash').textContent = 
                    (data.account?.cash || 0).toLocaleString() + '원';
                document.getElementById('stocks-value').textContent = 
                    (data.account?.stocks_value || 0).toLocaleString() + '원';
                
                const profitLoss = data.account?.total_profit_loss || 0;
                const profitRate = data.account?.total_profit_loss_rate || 0;
                const profitClass = profitLoss >= 0 ? 'profit' : 'loss';
                
                document.getElementById('profit-loss').innerHTML = 
                    `<span class="${profitClass}">${profitLoss >= 0 ? '+' : ''}${profitLoss.toLocaleString()}원</span>`;
                document.getElementById('profit-rate').innerHTML = 
                    `<span class="${profitClass}">${profitRate >= 0 ? '+' : ''}${profitRate.toFixed(2)}%</span>`;
                
                // 포지션 정보
                document.getElementById('position-count').textContent = data.positions?.length || 0;
                document.getElementById('max-positions').textContent = data.max_positions || 5;
                document.getElementById('available-slots').textContent = 
                    (data.max_positions || 5) - (data.positions?.length || 0);
                
                // 매매 통계
                document.getElementById('total-trades').textContent = data.stats?.total_trades || 0;
                document.getElementById('win-rate').textContent = 
                    (data.stats?.win_rate || 0).toFixed(1) + '%';
                document.getElementById('ai-analyses').textContent = data.stats?.ai_analyses || 0;
                
                // 보유 종목 테이블
                const holdingsTable = document.getElementById('holdings-table');
                if (data.holdings && data.holdings.length > 0) {
                    holdingsTable.innerHTML = data.holdings.map(h => `
                        <tr>
                            <td>${h.stock_name}</td>
                            <td>${h.quantity.toLocaleString()}주</td>
                            <td>${h.purchase_price.toLocaleString()}원</td>
                            <td>${h.current_price.toLocaleString()}원</td>
                            <td class="${h.profit_loss >= 0 ? 'profit' : 'loss'}">
                                ${h.profit_loss >= 0 ? '+' : ''}${h.profit_loss.toLocaleString()}원
                            </td>
                            <td class="${h.profit_loss_rate >= 0 ? 'profit' : 'loss'}">
                                ${h.profit_loss_rate >= 0 ? '+' : ''}${h.profit_loss_rate.toFixed(2)}%
                            </td>
                        </tr>
                    `).join('');
                } else {
                    holdingsTable.innerHTML = '<tr><td colspan="6" style="text-align:center;">보유 종목 없음</td></tr>';
                }
                
                // 업데이트 시간
                const now = new Date();
                document.getElementById('update-time').textContent = now.toLocaleTimeString();
            }
            
            // 봇 제어 함수들
            async function startBot() {
                await fetch('/api/control', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: 'start'})
                });
                refreshData();
            }
            
            async function stopBot() {
                await fetch('/api/control', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: 'stop'})
                });
                refreshData();
            }
            
            async function pauseBuy() {
                await fetch('/api/control', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: 'pause_buy'})
                });
                refreshData();
            }
            
            async function resumeBuy() {
                await fetch('/api/control', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: 'resume_buy'})
                });
                refreshData();
            }
            
            // 초기 로드 및 자동 새로고침
            refreshData();
            setInterval(refreshData, 10000);  // 10초마다 새로고침
        </script>
    </body>
    </html>
    """
    
    # ==================== 라우트 ====================
    
    @app.route('/')
    def index():
        """대시보드 메인 페이지"""
        return render_template_string(DASHBOARD_HTML)
    
    @app.route('/api/status')
    def api_status():
        """봇 상태 API"""
        bot = app.config.get('bot')

        if bot is None:
            return jsonify({
                'is_running': False,
                'error': '봇 인스턴스가 없습니다'
            })

        try:
            # 봇 상태 수집
            status = {
                'is_running': getattr(bot, 'is_running', False),
                'account': {},
                'positions': [],
                'holdings': [],
                'max_positions': 5,
                'stats': {},
            }

            # 계좌 정보 직접 가져오기
            if hasattr(bot, 'account_api'):
                try:
                    # 예수금 조회
                    deposit_info = bot.account_api.get_deposit()

                    # 잔고 조회
                    balance_info = bot.account_api.get_balance()

                    # 계좌 요약
                    account_summary = bot.account_api.get_account_summary()

                    status['account'] = {
                        'total_assets': account_summary.get('total_evaluation', 0),
                        'cash': deposit_info.get('deposit', 0),
                        'stocks_value': balance_info.get('total_evaluation', 0),
                        'total_profit_loss': balance_info.get('total_profit_loss', 0),
                        'total_profit_loss_rate': balance_info.get('profit_loss_rate', 0),
                    }

                    # 보유 종목 상세
                    holdings = bot.account_api.get_holdings()
                    if holdings:
                        status['holdings'] = [
                            {
                                'stock_code': h.get('stock_code', ''),
                                'stock_name': h.get('stock_name', ''),
                                'quantity': h.get('quantity', 0),
                                'purchase_price': h.get('avg_buy_price', 0),
                                'current_price': h.get('current_price', 0),
                                'profit_loss': h.get('profit_loss', 0),
                                'profit_loss_rate': h.get('profit_loss_rate', 0),
                            }
                            for h in holdings
                        ]

                    logger.info(f"✓ 계좌 정보 조회 성공: 총 자산={status['account']['total_assets']:,}원")

                except Exception as e:
                    logger.error(f"계좌 정보 조회 실패: {e}")
                    # 기본값 설정
                    status['account'] = {
                        'total_assets': 0,
                        'cash': 0,
                        'stocks_value': 0,
                        'total_profit_loss': 0,
                        'total_profit_loss_rate': 0,
                    }

            # 포지션 정보 (전략에서)
            if hasattr(bot, 'strategy'):
                try:
                    status['positions'] = list(bot.strategy.get_all_positions().values())
                    status['max_positions'] = bot.strategy.get_config('max_positions', 5)
                    status['stats'] = bot.strategy.get_statistics()
                except Exception as e:
                    logger.error(f"전략 정보 조회 실패: {e}")

            return jsonify(status)

        except Exception as e:
            logger.error(f"상태 조회 오류: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/control', methods=['POST'])
    def api_control():
        """봇 제어 API"""
        bot = app.config.get('bot')
        
        if bot is None:
            return jsonify({'error': '봇 인스턴스가 없습니다'}), 400
        
        data = request.json
        action = data.get('action')
        
        try:
            if action == 'start':
                bot.start()
                return jsonify({'message': '봇 시작됨'})
            
            elif action == 'stop':
                bot.stop()
                return jsonify({'message': '봇 정지됨'})
            
            elif action == 'pause_buy':
                bot.pause_buy = True
                return jsonify({'message': '매수 중지됨'})
            
            elif action == 'resume_buy':
                bot.pause_buy = False
                return jsonify({'message': '매수 재개됨'})
            
            else:
                return jsonify({'error': '알 수 없는 동작'}), 400
                
        except Exception as e:
            logger.error(f"제어 오류: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app


def run_dashboard(bot_instance=None, host='0.0.0.0', port=5000, debug=False):
    """
    대시보드 실행

    Args:
        bot_instance: 트레이딩 봇 인스턴스
        host: 호스트
        port: 포트
        debug: 디버그 모드
    """
    app = create_app(bot_instance)
    logger.info(f"대시보드 시작: http://{host}:{port}")

    # Flask 서버 실행 (백그라운드 스레드에서 안전하게 실행)
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,  # 리로더 비활성화 (멀티스레드 환경에서 문제 방지)
        threaded=True        # 멀티스레드 지원
    )


__all__ = ['run_dashboard', 'create_app']