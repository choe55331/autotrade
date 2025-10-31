"""
dashboard/dashboard_pro.py
Professional Flask Dashboard
"""
import logging
from flask import Flask, render_template_string, jsonify, request
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI Trading Pro Dashboard</title>
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        /* Header */
        .header {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            color: #333;
            font-size: 32px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .header h1 i {
            color: var(--primary);
        }

        .status-group {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .status-badge {
            padding: 10px 20px;
            border-radius: 24px;
            font-weight: bold;
            font-size: 15px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .status-running { background: var(--success); color: white; }
        .status-stopped { background: var(--danger); color: white; }

        /* Grid */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }

        .card {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }

        .card-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }

        .card-icon.blue { color: var(--primary); }
        .card-icon.green { color: var(--success); }
        .card-icon.red { color: var(--danger); }
        .card-icon.orange { color: var(--warning); }

        .card h2 {
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
            font-weight: 600;
        }

        .card-value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }

        .card-change {
            font-size: 16px;
            font-weight: 600;
        }

        .profit { color: var(--success); }
        .loss { color: var(--danger); }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }

        .stat-item {
            text-align: center;
            padding: 16px;
            border-right: 1px solid #eee;
        }

        .stat-item:last-child {
            border-right: none;
        }

        .stat-label {
            color: #666;
            font-size: 13px;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }

        /* Controls */
        .controls {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }

        .controls h2 {
            color: #333;
            font-size: 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .controls h2 i {
            color: var(--primary);
        }

        .btn-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        button {
            padding: 14px 28px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-success { background: var(--success); color: white; }
        .btn-success:hover { background: #059669; transform: translateY(-2px); }

        .btn-danger { background: var(--danger); color: white; }
        .btn-danger:hover { background: #dc2626; transform: translateY(-2px); }

        .btn-primary { background: var(--primary); color: white; }
        .btn-primary:hover { background: #5568d3; transform: translateY(-2px); }

        .btn-warning { background: var(--warning); color: white; }
        .btn-warning:hover { background: #d97706; transform: translateY(-2px); }

        /* Table */
        .table-container {
            background: white;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow-x: auto;
        }

        .table-container h2 {
            color: #333;
            font-size: 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .table-container h2 i {
            color: var(--primary);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 14px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }

        td {
            color: #333;
            font-size: 14px;
        }

        tr:hover {
            background: #f8f9fa;
        }

        /* Footer */
        .footer {
            text-align: center;
            color: white;
            margin-top: 24px;
            padding: 16px;
            font-size: 14px;
        }

        .footer i {
            margin: 0 4px;
        }

        /* AI Badge */
        .ai-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            margin-left: 8px;
        }

        /* Activity Panel */
        .candidate-card {
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
            cursor: pointer;
            transition: all 0.2s;
        }

        .candidate-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .candidate-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .candidate-code {
            font-weight: bold;
            color: #333;
            font-size: 16px;
        }

        .candidate-score {
            background: var(--primary);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }

        .candidate-name {
            color: #666;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .candidate-reason {
            font-size: 13px;
            color: #888;
            font-style: italic;
        }

        .candidate-badges {
            display: flex;
            gap: 4px;
            margin-top: 8px;
        }

        .badge {
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        }

        .badge-ai {
            background: #10b981;
            color: white;
        }

        .badge-plan {
            background: #f59e0b;
            color: white;
        }

        .activity-item {
            padding: 12px;
            background: #f8f9fa;
            border-radius: 6px;
            margin-bottom: 8px;
            border-left: 3px solid #ddd;
        }

        .activity-item.info {
            border-left-color: var(--primary);
        }

        .activity-item.success {
            border-left-color: var(--success);
        }

        .activity-item.warning {
            border-left-color: var(--warning);
        }

        .activity-item.error {
            border-left-color: var(--danger);
        }

        .activity-time {
            font-size: 11px;
            color: #999;
            margin-bottom: 4px;
        }

        .activity-message {
            font-size: 14px;
            color: #333;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }

            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .stat-item {
                border-right: none;
                border-bottom: 1px solid #eee;
            }

            .stat-item:last-child {
                border-bottom: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>
                <i class="fas fa-robot"></i>
                AI Trading Pro
                <span class="ai-badge">GEMINI AI</span>
            </h1>
            <div class="status-group">
                <span class="status-badge" id="bot-status">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loading...
                </span>
                <span style="color: #666; font-size: 14px;" id="last-update"></span>
            </div>
        </div>

        <!-- Main Stats Cards -->
        <div class="grid">
            <div class="card">
                <i class="fas fa-wallet card-icon blue"></i>
                <h2>총 자산</h2>
                <div class="card-value" id="total-assets">-</div>
                <div class="card-change" id="assets-change">-</div>
            </div>

            <div class="card">
                <i class="fas fa-coins card-icon green"></i>
                <h2>보유 현금</h2>
                <div class="card-value" id="cash">-</div>
                <div class="card-change" id="cash-ratio">-</div>
            </div>

            <div class="card">
                <i class="fas fa-chart-line card-icon orange"></i>
                <h2>총 손익</h2>
                <div class="card-value" id="profit-loss">-</div>
                <div class="card-change" id="profit-rate">-</div>
            </div>

            <div class="card">
                <i class="fas fa-percentage card-icon red"></i>
                <h2>승률</h2>
                <div class="card-value" id="win-rate">-</div>
                <div class="card-change" id="total-trades">-</div>
            </div>
        </div>

        <!-- Detailed Stats -->
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-label"><i class="fas fa-layer-group"></i> 보유 종목</div>
                <div class="stat-value" id="position-count">-</div>
            </div>
            <div class="stat-item">
                <div class="stat-label"><i class="fas fa-chart-pie"></i> 평가 금액</div>
                <div class="stat-value" id="stocks-value">-</div>
            </div>
            <div class="stat-item">
                <div class="stat-label"><i class="fas fa-bullseye"></i> 최대 포지션</div>
                <div class="stat-value" id="max-positions">-</div>
            </div>
            <div class="stat-item">
                <div class="stat-label"><i class="fas fa-brain"></i> AI 분석</div>
                <div class="stat-value" id="ai-analyses">-</div>
            </div>
            <div class="stat-item">
                <div class="stat-label"><i class="fas fa-clock"></i> 실행 시간</div>
                <div class="stat-value" id="running-hours">-</div>
            </div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <h2><i class="fas fa-gamepad"></i> 제어 패널</h2>
            <div class="btn-group">
                <button class="btn-success" onclick="startBot()">
                    <i class="fas fa-play"></i> 시작
                </button>
                <button class="btn-danger" onclick="stopBot()">
                    <i class="fas fa-stop"></i> 정지
                </button>
                <button class="btn-warning" onclick="pauseBuy()">
                    <i class="fas fa-pause"></i> 매수 중지
                </button>
                <button class="btn-success" onclick="resumeBuy()">
                    <i class="fas fa-play-circle"></i> 매수 재개
                </button>
                <button class="btn-primary" onclick="refreshData()">
                    <i class="fas fa-sync-alt"></i> 새로고침
                </button>
            </div>
        </div>

        <!-- Holdings Table -->
        <div class="table-container">
            <h2><i class="fas fa-list"></i> 보유 종목 상세</h2>
            <table>
                <thead>
                    <tr>
                        <th>종목코드</th>
                        <th>종목명</th>
                        <th>수량</th>
                        <th>매수가</th>
                        <th>현재가</th>
                        <th>손익</th>
                        <th>수익률</th>
                    </tr>
                </thead>
                <tbody id="holdings-tbody">
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 40px;">
                            <i class="fas fa-spinner fa-spin" style="font-size: 24px; color: #999;"></i>
                            <p style="color: #999; margin-top: 12px;">로딩 중...</p>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Real-time Trading Activity Panel -->
        <div class="activity-panel" style="background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 24px;">
            <h2 style="color: #333; font-size: 20px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-chart-line" style="color: var(--primary);"></i>
                실시간 매매 활동
            </h2>

            <!-- Current Screening Status -->
            <div class="screening-status" id="screening-status" style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                    <span style="font-weight: 600; color: #666;">상태:</span>
                    <span id="screen-status" style="color: #333;">대기 중</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                    <span style="font-weight: 600; color: #666;">시장:</span>
                    <span id="screen-market" style="color: #333;">-</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                    <span style="font-weight: 600; color: #666;">검색 조건:</span>
                    <span id="screen-conditions" style="color: #333;">-</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                    <span style="font-weight: 600; color: #666;">후보 종목:</span>
                    <span id="screen-candidates" style="color: #333;">0개</span>
                </div>
            </div>

            <!-- Candidate Stocks -->
            <div class="candidates-section" id="candidates-section" style="margin-top: 20px;">
                <h3 style="color: #333; font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-star" style="color: var(--warning);"></i>
                    후보 종목
                </h3>
                <div class="candidates-grid" id="candidates-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; margin-top: 12px;">
                    <p style="text-align: center; color: #999;">후보 종목이 없습니다</p>
                </div>
            </div>

            <!-- Activity Feed -->
            <div class="activity-feed" id="activity-feed" style="margin-top: 20px;">
                <h3 style="color: #333; font-size: 16px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-stream" style="color: var(--primary);"></i>
                    활동 로그
                </h3>
                <div class="feed-container" id="feed-container" style="max-height: 300px; overflow-y: auto; margin-top: 12px;">
                    <p style="text-align: center; color: #999;">활동 기록이 없습니다</p>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <i class="fas fa-clock"></i> 자동 새로고침: 10초마다
            <i class="fas fa-calendar"></i> 마지막 업데이트: <span id="update-time">-</span>
        </div>
    </div>

    <script>
        // Data refresh
        async function refreshData() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('데이터 로드 실패:', error);
            }
        }

        // Update dashboard
        function updateDashboard(data) {
            // Status
            const statusEl = document.getElementById('bot-status');
            if (data.is_running) {
                statusEl.innerHTML = '<i class="fas fa-check-circle"></i> 실행 중';
                statusEl.className = 'status-badge status-running';
            } else {
                statusEl.innerHTML = '<i class="fas fa-times-circle"></i> 정지됨';
                statusEl.className = 'status-badge status-stopped';
            }

            // Account
            const account = data.account || {};
            document.getElementById('total-assets').textContent = formatNumber(account.total_assets || 0) + '원';
            document.getElementById('cash').textContent = formatNumber(account.cash || 0) + '원';
            document.getElementById('stocks-value').textContent = formatNumber(account.stocks_value || 0) + '원';

            const profitLoss = account.total_profit_loss || 0;
            const profitRate = account.total_profit_loss_rate || 0;
            const profitClass = profitLoss >= 0 ? 'profit' : 'loss';

            document.getElementById('profit-loss').textContent = formatNumber(profitLoss) + '원';
            document.getElementById('profit-loss').className = 'card-value ' + profitClass;
            document.getElementById('profit-rate').textContent = (profitRate >= 0 ? '+' : '') + profitRate.toFixed(2) + '%';
            document.getElementById('profit-rate').className = 'card-change ' + profitClass;

            // Cash ratio
            const cashRatio = account.total_assets > 0 ? (account.cash / account.total_assets * 100) : 0;
            document.getElementById('cash-ratio').textContent = cashRatio.toFixed(1) + '% 현금 비율';

            // Stats
            const stats = data.stats || {};
            document.getElementById('position-count').textContent = (data.positions?.length || 0);
            document.getElementById('max-positions').textContent = data.max_positions || 5;
            document.getElementById('win-rate').textContent = (stats.win_rate || 0).toFixed(1) + '%';
            document.getElementById('total-trades').textContent = (stats.total_trades || 0) + ' trades';
            document.getElementById('ai-analyses').textContent = (stats.ai_analyses || 0);
            document.getElementById('running-hours').textContent = (stats.running_hours || 0).toFixed(1) + 'h';

            // Holdings
            updateHoldingsTable(data.holdings || []);

            // Update time
            const now = new Date();
            document.getElementById('update-time').textContent = now.toLocaleTimeString();
        }

        // Update holdings table
        function updateHoldingsTable(holdings) {
            const tbody = document.getElementById('holdings-tbody');

            if (!holdings || holdings.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 40px;">
                            <i class="fas fa-inbox" style="font-size: 48px; color: #ccc;"></i>
                            <p style="color: #999; margin-top: 12px;">보유 종목이 없습니다</p>
                        </td>
                    </tr>
                `;
                return;
            }

            let html = '';
            holdings.forEach(h => {
                const profitClass = h.profit_loss >= 0 ? 'profit' : 'loss';
                html += `
                    <tr>
                        <td><strong>${h.stock_code}</strong></td>
                        <td>${h.stock_name}</td>
                        <td>${formatNumber(h.quantity)}</td>
                        <td>${formatNumber(h.purchase_price)}원</td>
                        <td>${formatNumber(h.current_price)}원</td>
                        <td class="${profitClass}"><strong>${formatNumber(h.profit_loss)}원</strong></td>
                        <td class="${profitClass}"><strong>${h.profit_loss_rate >= 0 ? '+' : ''}${h.profit_loss_rate.toFixed(2)}%</strong></td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }

        // Control functions
        async function startBot() {
            await controlBot('start');
        }

        async function stopBot() {
            await controlBot('stop');
        }

        async function pauseBuy() {
            await controlBot('pause_buy');
        }

        async function resumeBuy() {
            await controlBot('resume_buy');
        }

        async function controlBot(action) {
            try {
                const response = await fetch('/api/control', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action})
                });
                const data = await response.json();
                if (data.success || data.message) {
                    refreshData();
                }
            } catch (error) {
                console.error('제어 오류:', error);
            }
        }

        // Utility
        function formatNumber(num) {
            return new Intl.NumberFormat('ko-KR').format(Math.round(num));
        }

        // Activity panel refresh
        async function refreshActivityData() {
            try {
                const response = await fetch('/api/activity');
                const data = await response.json();
                updateActivityPanel(data);
            } catch (error) {
                console.error('Activity data load failed:', error);
            }
        }

        // Update activity panel
        function updateActivityPanel(data) {
            // Screening status
            const screening = data.screening || {};
            document.getElementById('screen-status').textContent =
                getStatusText(screening.status);
            document.getElementById('screen-market').textContent =
                screening.market || '-';
            document.getElementById('screen-conditions').textContent =
                formatConditions(screening.conditions);
            document.getElementById('screen-candidates').textContent =
                (screening.candidates_found || 0) + '개';

            // Candidates
            updateCandidates(data.candidates || []);

            // Activity feed
            updateActivityFeed(data.activities || []);
        }

        // Update candidates
        function updateCandidates(candidates) {
            const grid = document.getElementById('candidates-grid');

            if (!candidates || candidates.length === 0) {
                grid.innerHTML = '<p style="text-align: center; color: #999;">후보 종목이 없습니다</p>';
                return;
            }

            let html = '';
            candidates.forEach(c => {
                html += `
                    <div class="candidate-card" onclick="showCandidateDetail('${c.stock_code}')">
                        <div class="candidate-header">
                            <span class="candidate-code">${c.stock_code}</span>
                            <span class="candidate-score">${c.score.toFixed(1)}</span>
                        </div>
                        <div class="candidate-name">${c.stock_name}</div>
                        <div class="candidate-reason">${c.reason}</div>
                        <div class="candidate-badges">
                            ${c.ai_analyzed ? '<span class="badge badge-ai">AI분석완료</span>' : ''}
                            ${c.buy_plan_ready ? '<span class="badge badge-plan">매수계획</span>' : ''}
                        </div>
                    </div>
                `;
            });
            grid.innerHTML = html;
        }

        // Update activity feed
        function updateActivityFeed(activities) {
            const container = document.getElementById('feed-container');

            if (!activities || activities.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">활동 기록이 없습니다</p>';
                return;
            }

            let html = '';
            activities.slice().reverse().slice(0, 20).forEach(act => {
                const time = new Date(act.timestamp).toLocaleTimeString();
                html += `
                    <div class="activity-item ${act.level}">
                        <div class="activity-time">${time}</div>
                        <div class="activity-message">${act.message}</div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        // Utility functions
        function getStatusText(status) {
            const statusMap = {
                'idle': '대기 중',
                'screening': '종목 스크리닝 중',
                'analyzing': 'AI 분석 중',
                'trading': '매매 진행 중'
            };
            return statusMap[status] || status;
        }

        function formatConditions(conditions) {
            if (!conditions || Object.keys(conditions).length === 0) {
                return '-';
            }
            return Object.entries(conditions)
                .map(([k, v]) => `${k}: ${v}`)
                .join(', ');
        }

        function showCandidateDetail(stockCode) {
            // TODO: Show modal with detailed AI analysis and buy plan
            alert(`종목 상세: ${stockCode}\n\n상세 패널을 곧 추가하겠습니다!`);
        }

        // Initial load and auto-refresh
        refreshData();
        refreshActivityData();
        setInterval(refreshData, 10000);  // 10 seconds
        setInterval(refreshActivityData, 5000);  // 5 seconds
    </script>
</body>
</html>
"""


def create_app(bot_instance=None):
    """
    Flask 앱 생성 (Pro Version)
    """
    app = Flask(__name__)
    app.config['bot'] = bot_instance

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
            status = {
                'is_running': getattr(bot, 'is_running', False),
                'account': {},
                'positions': [],
                'holdings': [],
                'max_positions': 5,
                'stats': {},
            }

            # 계좌 정보
            if hasattr(bot, 'account_api'):
                try:
                    deposit_info = bot.account_api.get_deposit()
                    balance_info = bot.account_api.get_balance()
                    account_summary = bot.account_api.get_account_summary()

                    cash = 0
                    if deposit_info:
                        cash_str = deposit_info.get('entr') or deposit_info.get('pymn_alow_amt') or '0'
                        cash = int(cash_str)

                    stocks_value = 0
                    total_profit_loss = 0
                    total_assets = cash + stocks_value

                    status['account'] = {
                        'total_assets': total_assets,
                        'cash': cash,
                        'stocks_value': stocks_value,
                        'total_profit_loss': total_profit_loss,
                        'total_profit_loss_rate': 0,
                    }

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

                    logger.info(f"✓ 계좌 정보 조회 성공: 총 자산={total_assets:,}원")

                except Exception as e:
                    logger.error(f"계좌 정보 조회 실패: {e}")
                    status['account'] = {
                        'total_assets': 0,
                        'cash': 0,
                        'stocks_value': 0,
                        'total_profit_loss': 0,
                        'total_profit_loss_rate': 0,
                    }

            # 전략 정보
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
                return jsonify({'success': True, 'message': '봇 시작됨'})

            elif action == 'stop':
                bot.stop()
                return jsonify({'success': True, 'message': '봇 정지됨'})

            elif action == 'pause_buy':
                bot.pause_buy = True
                return jsonify({'success': True, 'message': '매수 중지됨'})

            elif action == 'resume_buy':
                bot.pause_buy = False
                return jsonify({'success': True, 'message': '매수 재개됨'})

            else:
                return jsonify({'error': '알 수 없는 동작'}), 400

        except Exception as e:
            logger.error(f"제어 오류: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/activity')
    def api_activity():
        """실시간 활동 데이터 API"""
        try:
            from utils.activity_monitor import get_monitor
            monitor = get_monitor()
            return jsonify(monitor.get_dashboard_data())
        except Exception as e:
            logger.error(f"활동 데이터 조회 오류: {e}")
            return jsonify({
                'screening': {
                    'status': 'idle',
                    'market': '',
                    'conditions': {},
                    'candidates_found': 0
                },
                'activities': [],
                'candidates': [],
                'ai_analyses': {},
                'buy_plans': {},
                'user_settings': {}
            })

    return app


def run_dashboard(bot_instance=None, host='0.0.0.0', port=5000, debug=False):
    """
    Pro Dashboard 실행
    """
    app = create_app(bot_instance)
    logger.info(f"Pro Dashboard 시작: http://{host}:{port}")

    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,
        threaded=True
    )


__all__ = ['run_dashboard', 'create_app']
