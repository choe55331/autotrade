# 대시보드 실질적 개선 가이드

**날짜**: 2025-11-05
**목적**: 대시보드를 실제 필요한 정보 중심으로 재구성

---

## ✅ 완료된 작업

### 1. API 엔드포인트 추가 (app_apple.py)
- ✅ `/api/virtual-trades` - 가상매매 전략별 거래 기록
- ✅ `/api/websocket/subscriptions` - 웹소켓 구독 리스트
- ✅ `/api/portfolio/real-holdings` - 실제 보유 종목 상세 (ATR 기반 손절/익절)

---

## 📋 대시보드 HTML 수정 필요 사항

### 파일: `dashboard/templates/dashboard_main.html` (2479줄)

---

### 🗑️ 제거할 섹션

#### 1. 사이드바 - AI 시스템 (626-640줄)
```html
<!-- 제거 -->
<div class="section-title">AI 시스템</div>
<ul class="stat-list">
    <li class="stat-item">
        <span class="stat-label">스캐닝 종목</span>
        <span class="stat-value" id="scanning-count">0</span>
    </li>
    ...
</ul>
```

#### 2. 사이드바 - 가상 매매 성과 (642-656줄)
```html
<!-- 제거 -->
<div class="section-title">가상 매매 성과</div>
<ul class="stat-list">
    <li class="stat-item">
        <span class="stat-label">총 수익률</span>
        <span class="stat-value" id="paper-return">0%</span>
    </li>
    ...
</ul>
```

---

### ➕ 추가할 섹션

#### 1. 사이드바 - 웹소켓 구독 현황 (626줄 위치)

```html
<!-- 추가 -->
<div class="section-title">웹소켓 구독 현황</div>
<ul class="stat-list">
    <li class="stat-item">
        <span class="stat-label">현재가 구독</span>
        <span class="stat-value" id="ws-price-count">0종목</span>
    </li>
    <li class="stat-item">
        <span class="stat-label">호가 구독</span>
        <span class="stat-value" id="ws-orderbook-count">0종목</span>
    </li>
    <li class="stat-item">
        <span class="stat-label">체결 구독</span>
        <span class="stat-value" id="ws-execution-count">0종목</span>
    </li>
</ul>

<!-- 구독 상세 리스트 -->
<div class="section-title" style="margin-top: 15px;">
    구독 종목
    <button onclick="refreshSubscriptions()" style="float: right; background: none; border: none; color: var(--color-primary); cursor: pointer; font-size: 11px;">
        <i class="fas fa-sync-alt"></i> 새로고침
    </button>
</div>
<div id="subscription-list" style="max-height: 200px; overflow-y: auto;">
    <!-- JavaScript로 동적 생성 -->
</div>
```

#### 2. 새 탭 - 가상매매 거래 기록 (탭 2 대체)

**탭 버튼 수정** (697줄):
```html
<button class="tab" onclick="switchTab(2)">
    <i class="fas fa-history"></i> 가상매매 거래기록
</button>
```

**탭 컨텐츠** (Tab 2):
```html
<!-- Tab 2: 가상매매 거래 기록 -->
<div class="tab-content" id="tab-virtual-trades">
    <div class="card">
        <div class="card-header">
            <div class="card-title">
                <i class="fas fa-history"></i>
                가상매매 전략별 거래 기록
            </div>
            <button onclick="refreshVirtualTrades()" class="btn btn-sm">
                <i class="fas fa-sync-alt"></i> 새로고침
            </button>
        </div>

        <!-- 전략 선택 탭 -->
        <div style="border-bottom: 1px solid var(--border-color); margin-bottom: 20px;">
            <button class="strategy-tab active" onclick="showStrategyTrades('공격적')" id="tab-공격적">
                공격적
            </button>
            <button class="strategy-tab" onclick="showStrategyTrades('보수적')" id="tab-보수적">
                보수적
            </button>
            <button class="strategy-tab" onclick="showStrategyTrades('균형')" id="tab-균형">
                균형
            </button>
        </div>

        <!-- 전략 요약 -->
        <div id="strategy-summary-공격적" class="strategy-summary">
            <div class="grid-4">
                <div class="stat-card">
                    <div class="stat-label">총 자산</div>
                    <div class="stat-value" id="aggressive-total-value">₩0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">손익</div>
                    <div class="stat-value" id="aggressive-pnl">₩0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">수익률</div>
                    <div class="stat-value" id="aggressive-pnl-rate">0%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">승률</div>
                    <div class="stat-value" id="aggressive-win-rate">0%</div>
                </div>
            </div>
        </div>

        <!-- 거래 내역 테이블 -->
        <div id="trades-table-공격적" class="trades-table">
            <table>
                <thead>
                    <tr>
                        <th>시간</th>
                        <th>구분</th>
                        <th>종목</th>
                        <th>수량</th>
                        <th>가격</th>
                        <th>금액</th>
                        <th>손익</th>
                        <th>사유</th>
                    </tr>
                </thead>
                <tbody id="trades-tbody-공격적">
                    <!-- JavaScript로 동적 생성 -->
                </tbody>
            </table>
        </div>
    </div>
</div>
```

#### 3. 포트폴리오 탭 업그레이드 (Tab 4)

**기존 포트폴리오 차트 대체**:
```html
<!-- Tab 4: 포트폴리오 (ATR 기반 손절/익절 표시) -->
<div class="tab-content" id="tab-portfolio">
    <div class="card">
        <div class="card-header">
            <div class="card-title">
                <i class="fas fa-chart-pie"></i>
                실제 보유 종목 (ATR 기반 동적 손절/익절)
            </div>
            <button onclick="refreshPortfolio()" class="btn btn-sm">
                <i class="fas fa-sync-alt"></i> 새로고침
            </button>
        </div>

        <div id="portfolio-holdings">
            <!-- JavaScript로 동적 생성 -->
        </div>
    </div>
</div>
```

**보유 종목 카드 템플릿**:
```html
<div class="holding-card">
    <div class="holding-header">
        <div>
            <div class="holding-name">{stock_name}</div>
            <div class="holding-code">{stock_code}</div>
        </div>
        <div class="holding-pnl {pnl-class}">
            {pnl_rate}%
        </div>
    </div>

    <div class="holding-stats">
        <div class="stat-row">
            <span>보유수량</span>
            <span>{quantity}주</span>
        </div>
        <div class="stat-row">
            <span>평균단가</span>
            <span>₩{avg_price:,}</span>
        </div>
        <div class="stat-row">
            <span>현재가</span>
            <span>₩{current_price:,}</span>
        </div>
        <div class="stat-row">
            <span>평가금액</span>
            <span>₩{eval_amount:,}</span>
        </div>
    </div>

    <!-- ATR 기반 손절/익절 -->
    <div class="atr-zone">
        <div class="atr-header">
            <i class="fas fa-shield-alt"></i>
            ATR 기반 손절/익절 (실시간)
        </div>

        <!-- 손절가 -->
        <div class="atr-row stop-loss">
            <div class="atr-label">
                <i class="fas fa-arrow-down"></i>
                손절가
            </div>
            <div class="atr-value">₩{stop_loss_price:,}</div>
            <div class="atr-distance {stop-class}">
                {distance_to_stop}%
            </div>
        </div>

        <!-- 현재가 바 -->
        <div class="price-bar-container">
            <div class="price-bar">
                <div class="price-marker" style="left: {position}%">
                    <div class="marker-label">현재</div>
                </div>
            </div>
            <div class="price-labels">
                <span>손절</span>
                <span>목표</span>
            </div>
        </div>

        <!-- 익절가 -->
        <div class="atr-row take-profit">
            <div class="atr-label">
                <i class="fas fa-arrow-up"></i>
                익절가
            </div>
            <div class="atr-value">₩{take_profit_price:,}</div>
            <div class="atr-distance {profit-class}">
                {distance_to_target}%
            </div>
        </div>
    </div>
</div>
```

---

## 📜 JavaScript 함수 추가

### 1. 웹소켓 구독 새로고침
```javascript
// 웹소켓 구독 리스트 조회
function refreshSubscriptions() {
    fetch('/api/websocket/subscriptions')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const subs = data.data;

                // 카운트 업데이트
                document.getElementById('ws-price-count').textContent =
                    `${subs.price.length}종목`;
                document.getElementById('ws-orderbook-count').textContent =
                    `${subs.orderbook.length}종목`;
                document.getElementById('ws-execution-count').textContent =
                    `${subs.execution.length}종목`;

                // 구독 리스트 렌더링
                const listHtml = subs.price.map(item => `
                    <div class="subscription-item">
                        <div>
                            <span class="sub-name">${item.stock_name}</span>
                            <span class="sub-code">${item.stock_code}</span>
                        </div>
                        <span class="sub-type">현재가</span>
                    </div>
                `).join('');

                document.getElementById('subscription-list').innerHTML =
                    listHtml || '<div style="color: var(--text-secondary); padding: 10px; text-align: center;">구독 중인 종목 없음</div>';
            }
        });
}

// 5초마다 자동 새로고침
setInterval(refreshSubscriptions, 5000);
```

### 2. 가상매매 거래 기록 조회
```javascript
// 가상매매 거래 기록 조회
function refreshVirtualTrades() {
    fetch('/api/virtual-trades')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const trades = data.data;

                // 각 전략별 데이터 렌더링
                ['공격적', '보수적', '균형'].forEach(strategy => {
                    if (trades[strategy]) {
                        const summary = trades[strategy].summary;
                        const tradeList = trades[strategy].trades;

                        // 요약 업데이트
                        updateStrategySummary(strategy, summary);

                        // 거래 내역 테이블 업데이트
                        updateTradesTable(strategy, tradeList);
                    }
                });
            }
        });
}

function updateStrategySummary(strategy, summary) {
    const prefix = strategy === '공격적' ? 'aggressive' :
                   strategy === '보수적' ? 'conservative' : 'balanced';

    document.getElementById(`${prefix}-total-value`).textContent =
        `₩${summary.total_value.toLocaleString()}`;
    document.getElementById(`${prefix}-pnl`).textContent =
        `${summary.total_pnl >= 0 ? '+' : ''}₩${summary.total_pnl.toLocaleString()}`;
    document.getElementById(`${prefix}-pnl-rate`).textContent =
        `${summary.total_pnl_rate >= 0 ? '+' : ''}${summary.total_pnl_rate.toFixed(2)}%`;
    document.getElementById(`${prefix}-win-rate`).textContent =
        `${summary.win_rate.toFixed(1)}%`;
}

function updateTradesTable(strategy, trades) {
    const tbody = document.getElementById(`trades-tbody-${strategy}`);

    if (!trades || trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-secondary);">거래 내역 없음</td></tr>';
        return;
    }

    const html = trades.map(trade => {
        const isBuy = trade.type === 'buy';
        const timestamp = new Date(trade.timestamp).toLocaleString('ko-KR', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        return `
            <tr class="trade-row ${isBuy ? 'buy' : 'sell'}">
                <td>${timestamp}</td>
                <td>
                    <span class="trade-type ${isBuy ? 'buy' : 'sell'}">
                        ${isBuy ? '매수' : '매도'}
                    </span>
                </td>
                <td>${trade.stock_name}</td>
                <td>${trade.quantity}주</td>
                <td>₩${trade.price.toLocaleString()}</td>
                <td>₩${trade.amount.toLocaleString()}</td>
                <td>
                    ${!isBuy && trade.realized_pnl ? `
                        <span class="${trade.realized_pnl >= 0 ? 'profit' : 'loss'}">
                            ${trade.realized_pnl >= 0 ? '+' : ''}₩${trade.realized_pnl.toLocaleString()}
                            (${trade.realized_pnl_rate >= 0 ? '+' : ''}${trade.realized_pnl_rate.toFixed(2)}%)
                        </span>
                    ` : '-'}
                </td>
                <td>${trade.reason || '-'}</td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = html;
}

// 30초마다 자동 새로고침
setInterval(refreshVirtualTrades, 30000);
```

### 3. 포트폴리오 실제 데이터 조회 (ATR)
```javascript
// 실제 포트폴리오 조회 (ATR 기반)
function refreshPortfolio() {
    fetch('/api/portfolio/real-holdings')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const holdings = data.data;
                renderPortfolioHoldings(holdings);
            }
        });
}

function renderPortfolioHoldings(holdings) {
    const container = document.getElementById('portfolio-holdings');

    if (!holdings || holdings.length === 0) {
        container.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">보유 종목 없음</div>';
        return;
    }

    const html = holdings.map(holding => {
        const pnlClass = holding.pnl >= 0 ? 'profit' : 'loss';
        const stopClass = holding.distance_to_stop < 0 ? 'danger' : 'safe';
        const profitClass = holding.distance_to_target < 0 ? 'reached' : 'pending';

        // 현재가 위치 계산 (손절 ~ 익절 사이)
        const range = holding.take_profit_price - holding.stop_loss_price;
        const currentOffset = holding.current_price - holding.stop_loss_price;
        const position = Math.max(0, Math.min(100, (currentOffset / range) * 100));

        return `
            <div class="holding-card">
                <div class="holding-header">
                    <div>
                        <div class="holding-name">${holding.stock_name}</div>
                        <div class="holding-code">${holding.stock_code}</div>
                    </div>
                    <div class="holding-pnl ${pnlClass}">
                        ${holding.pnl_rate >= 0 ? '+' : ''}${holding.pnl_rate}%
                    </div>
                </div>

                <div class="holding-stats">
                    <div class="stat-row">
                        <span>보유수량</span>
                        <span>${holding.quantity}주</span>
                    </div>
                    <div class="stat-row">
                        <span>평균단가</span>
                        <span>₩${holding.avg_price.toLocaleString()}</span>
                    </div>
                    <div class="stat-row">
                        <span>현재가</span>
                        <span class="${pnlClass}">₩${holding.current_price.toLocaleString()}</span>
                    </div>
                    <div class="stat-row">
                        <span>평가금액</span>
                        <span>₩${holding.eval_amount.toLocaleString()}</span>
                    </div>
                </div>

                <div class="atr-zone">
                    <div class="atr-header">
                        <i class="fas fa-shield-alt"></i>
                        ATR 기반 손절/익절 (실시간)
                    </div>

                    <div class="atr-row stop-loss">
                        <div class="atr-label">
                            <i class="fas fa-arrow-down"></i>
                            손절가
                        </div>
                        <div class="atr-value">₩${holding.stop_loss_price.toLocaleString()}</div>
                        <div class="atr-distance ${stopClass}">
                            ${holding.distance_to_stop.toFixed(2)}%
                        </div>
                    </div>

                    <div class="price-bar-container">
                        <div class="price-bar">
                            <div class="price-marker" style="left: ${position}%">
                                <div class="marker-label">현재</div>
                            </div>
                        </div>
                        <div class="price-labels">
                            <span>손절</span>
                            <span>목표</span>
                        </div>
                    </div>

                    <div class="atr-row take-profit">
                        <div class="atr-label">
                            <i class="fas fa-arrow-up"></i>
                            익절가
                        </div>
                        <div class="atr-value">₩${holding.take_profit_price.toLocaleString()}</div>
                        <div class="atr-distance ${profitClass}">
                            +${holding.distance_to_target.toFixed(2)}%
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    container.innerHTML = html;
}

// 10초마다 자동 새로고침 (ATR 실시간 반영)
setInterval(refreshPortfolio, 10000);
```

---

## 🎨 CSS 스타일 추가

```css
/* 웹소켓 구독 리스트 */
.subscription-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 10px;
    border-bottom: 1px solid var(--border-color);
}

.sub-name {
    font-size: 12px;
    color: var(--text-primary);
    margin-right: 5px;
}

.sub-code {
    font-size: 10px;
    color: var(--text-secondary);
}

.sub-type {
    font-size: 10px;
    padding: 2px 8px;
    background: var(--color-primary);
    color: white;
    border-radius: 10px;
}

/* 가상매매 거래 기록 */
.strategy-tab {
    padding: 10px 20px;
    border: none;
    background: none;
    color: var(--text-secondary);
    cursor: pointer;
    border-bottom: 2px solid transparent;
}

.strategy-tab.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
}

.trades-table {
    margin-top: 20px;
    overflow-x: auto;
}

.trades-table table {
    width: 100%;
    border-collapse: collapse;
}

.trades-table th,
.trades-table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
    font-size: 12px;
}

.trade-type.buy {
    color: var(--color-success);
}

.trade-type.sell {
    color: var(--color-danger);
}

/* 포트폴리오 보유 종목 */
.holding-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

.holding-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.holding-name {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
}

.holding-code {
    font-size: 12px;
    color: var(--text-secondary);
}

.holding-pnl {
    font-size: 20px;
    font-weight: 700;
}

.holding-pnl.profit {
    color: var(--color-success);
}

.holding-pnl.loss {
    color: var(--color-danger);
}

.holding-stats {
    background: var(--bg-secondary);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    font-size: 13px;
}

/* ATR 존 */
.atr-zone {
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 8px;
    padding: 15px;
}

.atr-header {
    font-size: 13px;
    font-weight: 600;
    color: var(--color-primary);
    margin-bottom: 15px;
}

.atr-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-radius: 6px;
    margin-bottom: 10px;
}

.atr-row.stop-loss {
    background: rgba(239, 68, 68, 0.1);
}

.atr-row.take-profit {
    background: rgba(34, 197, 94, 0.1);
}

.atr-label {
    font-size: 12px;
    color: var(--text-secondary);
}

.atr-value {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}

.atr-distance {
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 12px;
    font-weight: 600;
}

.atr-distance.danger {
    background: var(--color-danger);
    color: white;
}

.atr-distance.safe {
    background: rgba(34, 197, 94, 0.2);
    color: var(--color-success);
}

.price-bar-container {
    margin: 15px 0;
}

.price-bar {
    height: 8px;
    background: linear-gradient(to right, #ef4444, #fbbf24, #22c55e);
    border-radius: 4px;
    position: relative;
}

.price-marker {
    position: absolute;
    top: -25px;
    transform: translateX(-50%);
    width: 2px;
    height: 40px;
    background: white;
    border: 2px solid var(--color-primary);
}

.marker-label {
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 10px;
    font-weight: 600;
    color: var(--color-primary);
    white-space: nowrap;
}

.price-labels {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: var(--text-secondary);
    margin-top: 5px;
}
```

---

## 🚀 적용 단계

### Phase 1: API 테스트 (완료 ✅)
- API 엔드포인트 3개 추가 완료
- 테스트 필요

### Phase 2: 사이드바 수정
1. AI 시스템 / 가상매매 성과 제거
2. 웹소켓 구독 현황 추가
3. 구독 종목 리스트 추가

### Phase 3: 가상매매 탭 교체
1. 탭 2 기존 내용 제거
2. 거래 기록 UI 추가
3. JavaScript 함수 연동

### Phase 4: 포트폴리오 업그레이드
1. 탭 4 기존 차트 제거
2. ATR 기반 상세 정보 추가
3. 실시간 업데이트 (10초)

---

## 📝 사용 방법

### 대시보드 접속 후
1. **사이드바**: 웹소켓 구독 현황 실시간 확인
2. **탭 2**: 가상매매 전략별 거래 내역 확인
3. **탭 4**: 보유 종목 ATR 기반 손절/익절 확인

### 자동 새로고침
- 웹소켓 구독: 5초
- 가상매매 거래: 30초
- 포트폴리오 (ATR): 10초

---

## ⚠️ 주의사항

1. **ATR 계산**: 일봉 데이터 14개 이상 필요
2. **웹소켓 구독**: WebSocketManager 구현 필요 (WEBSOCKET_SUBSCRIPTION_GUIDE.md 참고)
3. **캐시**: 대시보드 캐시 지우고 새로고침 (Ctrl+Shift+R)

---

이 문서를 참고해서 단계적으로 적용하시면 됩니다!
