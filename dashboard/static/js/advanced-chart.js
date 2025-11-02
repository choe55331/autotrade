/**
 * Advanced Trading Chart - Enhanced UX Version
 * Features: Multiple Timeframes, Technical Indicators, Drawing Tools
 */

class AdvancedTradingChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.mainChart = null;
        this.candlestickSeries = null;
        this.rsiChart = null;
        this.macdChart = null;
        this.volumeChart = null;
        this.canvas = null;
        this.ctx = null;

        // Current state
        this.currentStockCode = '005930';
        this.currentTimeframe = 'D'; // D=일봉, W=주봉, M=월봉, 숫자=분봉
        this.rawData = null; // Store raw data for timeframe conversion

        // Series for indicators
        this.series = {
            ma5: null,
            ma20: null,
            ma60: null,
            ema12: null,
            ema26: null,
            bb_upper: null,
            bb_middle: null,
            bb_lower: null,
            rsi: null,
            macd_line: null,
            macd_signal: null,
            macd_histogram: null,
            volume: null
        };

        // Drawing tools state
        this.drawingMode = null;
        this.drawings = [];
        this.currentDrawing = null;
        this.isDrawing = false;
        this.startPoint = null;

        // Indicator visibility
        this.indicatorsVisible = {
            ma5: true,
            ma20: true,
            ma60: false,
            ema12: false,
            ema26: false,
            bb: false,
            rsi: true,
            macd: true,
            volume: true
        };

        // Panel visibility
        this.panelsVisible = {
            rsi: true,
            macd: true,
            volume: true
        };
    }

    initialize() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error('Chart container not found:', this.containerId);
            return;
        }

        // Create chart layout
        this.createChartLayout(container);

        // Initialize main chart
        this.initMainChart();

        // Initialize indicator charts
        if (this.panelsVisible.rsi) this.initRSIChart();
        if (this.panelsVisible.macd) this.initMACDChart();
        if (this.panelsVisible.volume) this.initVolumeChart();

        // Setup drawing tools
        this.setupDrawingTools();

        // Handle resize
        window.addEventListener('resize', () => this.handleResize());
    }

    createChartLayout(container) {
        container.innerHTML = `
            <!-- Enhanced Toolbar -->
            <div class="chart-toolbar-enhanced" id="chart-toolbar">
                <!-- Timeframe Group -->
                <div class="toolbar-section">
                    <div class="toolbar-section-title">
                        <i class="fas fa-clock"></i> 시간봉
                    </div>
                    <div class="toolbar-button-group">
                        <button class="tf-btn tf-minute" data-timeframe="1" onclick="advancedChart.changeTimeframe('1')" title="1분봉">1분</button>
                        <button class="tf-btn tf-minute" data-timeframe="3" onclick="advancedChart.changeTimeframe('3')" title="3분봉">3분</button>
                        <button class="tf-btn tf-minute" data-timeframe="5" onclick="advancedChart.changeTimeframe('5')" title="5분봉">5분</button>
                        <button class="tf-btn tf-minute" data-timeframe="10" onclick="advancedChart.changeTimeframe('10')" title="10분봉">10분</button>
                        <button class="tf-btn tf-minute" data-timeframe="30" onclick="advancedChart.changeTimeframe('30')" title="30분봉">30분</button>
                        <button class="tf-btn tf-minute" data-timeframe="60" onclick="advancedChart.changeTimeframe('60')" title="60분봉">60분</button>
                    </div>
                    <div class="toolbar-button-group">
                        <button class="tf-btn tf-major active" data-timeframe="D" onclick="advancedChart.changeTimeframe('D')" title="일봉">
                            <i class="fas fa-sun"></i> 일봉
                        </button>
                        <button class="tf-btn tf-major" data-timeframe="W" onclick="advancedChart.changeTimeframe('W')" title="주봉">
                            <i class="fas fa-calendar-week"></i> 주봉
                        </button>
                        <button class="tf-btn tf-major" data-timeframe="M" onclick="advancedChart.changeTimeframe('M')" title="월봉">
                            <i class="fas fa-calendar-alt"></i> 월봉
                        </button>
                    </div>
                </div>

                <!-- Indicators Group -->
                <div class="toolbar-section">
                    <div class="toolbar-section-title">
                        <i class="fas fa-chart-line"></i> 이동평균
                    </div>
                    <div class="toolbar-button-group">
                        <button class="ind-btn active" data-indicator="ma5" onclick="advancedChart.toggleIndicator('ma5')" title="5일 이동평균">
                            <span class="ind-color" style="background: #f59e0b;"></span> MA5
                        </button>
                        <button class="ind-btn active" data-indicator="ma20" onclick="advancedChart.toggleIndicator('ma20')" title="20일 이동평균">
                            <span class="ind-color" style="background: #3b82f6;"></span> MA20
                        </button>
                        <button class="ind-btn" data-indicator="ma60" onclick="advancedChart.toggleIndicator('ma60')" title="60일 이동평균">
                            <span class="ind-color" style="background: #8b5cf6;"></span> MA60
                        </button>
                        <button class="ind-btn" data-indicator="bb" onclick="advancedChart.toggleIndicator('bb')" title="볼린저 밴드">
                            <i class="fas fa-chart-area"></i> BB
                        </button>
                    </div>
                </div>

                <!-- Drawing Tools Group -->
                <div class="toolbar-section">
                    <div class="toolbar-section-title">
                        <i class="fas fa-pen"></i> 그리기
                    </div>
                    <div class="toolbar-button-group">
                        <button class="draw-btn" onclick="advancedChart.setDrawingMode('trendline')" title="추세선">
                            <i class="fas fa-slash"></i>
                        </button>
                        <button class="draw-btn" onclick="advancedChart.setDrawingMode('horizontal')" title="수평선">
                            <i class="fas fa-minus"></i>
                        </button>
                        <button class="draw-btn" onclick="advancedChart.setDrawingMode('vertical')" title="수직선">
                            <i class="fas fa-grip-lines-vertical"></i>
                        </button>
                        <button class="draw-btn" onclick="advancedChart.clearDrawings()" title="모두 지우기">
                            <i class="fas fa-eraser"></i>
                        </button>
                    </div>
                </div>

                <!-- Chart Controls -->
                <div class="toolbar-section">
                    <div class="toolbar-section-title">
                        <i class="fas fa-cog"></i> 설정
                    </div>
                    <div class="toolbar-button-group">
                        <button class="ctrl-btn" onclick="advancedChart.togglePanel('rsi')" title="RSI 패널">
                            <i class="fas fa-chart-line"></i> RSI
                        </button>
                        <button class="ctrl-btn" onclick="advancedChart.togglePanel('macd')" title="MACD 패널">
                            <i class="fas fa-signal"></i> MACD
                        </button>
                        <button class="ctrl-btn" onclick="advancedChart.togglePanel('volume')" title="거래량 패널">
                            <i class="fas fa-chart-bar"></i> 거래량
                        </button>
                    </div>
                </div>
            </div>

            <!-- Chart Panels -->
            <div style="position: relative;">
                <canvas id="drawing-canvas" style="position: absolute; top: 0; left: 0; z-index: 10; pointer-events: auto;"></canvas>
                <div id="main-chart-container" class="chart-panel-enhanced" style="height: 380px; position: relative;"></div>
            </div>
            <div id="rsi-chart-container" class="chart-panel-enhanced indicator-panel" style="height: 100px; margin-top: 5px;"></div>
            <div id="macd-chart-container" class="chart-panel-enhanced indicator-panel" style="height: 120px; margin-top: 5px;"></div>
            <div id="volume-chart-container" class="chart-panel-enhanced indicator-panel" style="height: 90px; margin-top: 5px;"></div>
        `;
    }

    initMainChart() {
        const container = document.getElementById('main-chart-container');

        this.mainChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 380,
            layout: {
                background: { color: '#1a1d2e' },
                textColor: '#a5b1c2',
            },
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
                vertLine: {
                    color: '#758ca3',
                    width: 1,
                    style: 1,
                    labelBackgroundColor: '#3b82f6',
                },
                horzLine: {
                    color: '#758ca3',
                    width: 1,
                    style: 1,
                    labelBackgroundColor: '#3b82f6',
                },
            },
            rightPriceScale: {
                borderColor: '#2a2e39',
                scaleMargins: {
                    top: 0.1,
                    bottom: 0.2,
                },
            },
            timeScale: {
                borderColor: '#2a2e39',
                timeVisible: true,
                secondsVisible: false,
            },
        });

        // Add candlestick series with better colors
        this.candlestickSeries = this.mainChart.addCandlestickSeries({
            upColor: '#22c55e',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#22c55e',
            wickDownColor: '#ef4444',
        });

        // Add MA series
        this.series.ma5 = this.mainChart.addLineSeries({
            color: '#f59e0b',
            lineWidth: 2,
            title: 'MA5',
            visible: this.indicatorsVisible.ma5,
            priceLineVisible: false,
        });

        this.series.ma20 = this.mainChart.addLineSeries({
            color: '#3b82f6',
            lineWidth: 2,
            title: 'MA20',
            visible: this.indicatorsVisible.ma20,
            priceLineVisible: false,
        });

        this.series.ma60 = this.mainChart.addLineSeries({
            color: '#8b5cf6',
            lineWidth: 2,
            title: 'MA60',
            visible: this.indicatorsVisible.ma60,
            priceLineVisible: false,
        });

        // Bollinger Bands
        this.series.bb_upper = this.mainChart.addLineSeries({
            color: '#6366f1',
            lineWidth: 1,
            lineStyle: 2,
            visible: this.indicatorsVisible.bb,
            priceLineVisible: false,
        });

        this.series.bb_middle = this.mainChart.addLineSeries({
            color: '#94a3b8',
            lineWidth: 1,
            visible: this.indicatorsVisible.bb,
            priceLineVisible: false,
        });

        this.series.bb_lower = this.mainChart.addLineSeries({
            color: '#6366f1',
            lineWidth: 1,
            lineStyle: 2,
            visible: this.indicatorsVisible.bb,
            priceLineVisible: false,
        });
    }

    initRSIChart() {
        const container = document.getElementById('rsi-chart-container');
        if (!container) return;

        this.rsiChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 100,
            layout: {
                background: { color: '#1a1d2e' },
                textColor: '#a5b1c2',
            },
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
            },
            rightPriceScale: {
                borderColor: '#2a2e39',
                scaleMargins: {
                    top: 0.1,
                    bottom: 0.1,
                },
            },
            timeScale: {
                borderColor: '#2a2e39',
                visible: false,
            },
        });

        this.series.rsi = this.rsiChart.addLineSeries({
            color: '#a855f7',
            lineWidth: 2,
            title: 'RSI(14)',
        });

        // Add reference lines
        this.rsiChart.addLineSeries({
            color: 'rgba(239, 68, 68, 0.5)',
            lineWidth: 1,
            lineStyle: 2,
            priceLineVisible: false,
        }).setData([{time: '2020-01-01', value: 70}, {time: '2030-01-01', value: 70}]);

        this.rsiChart.addLineSeries({
            color: 'rgba(34, 197, 94, 0.5)',
            lineWidth: 1,
            lineStyle: 2,
            priceLineVisible: false,
        }).setData([{time: '2020-01-01', value: 30}, {time: '2030-01-01', value: 30}]);

        // Sync with main chart
        this.mainChart.timeScale().subscribeVisibleTimeRangeChange(() => {
            const range = this.mainChart.timeScale().getVisibleRange();
            this.rsiChart.timeScale().setVisibleRange(range);
        });
    }

    initMACDChart() {
        const container = document.getElementById('macd-chart-container');
        if (!container) return;

        this.macdChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 120,
            layout: {
                background: { color: '#1a1d2e' },
                textColor: '#a5b1c2',
            },
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
            },
            rightPriceScale: {
                borderColor: '#2a2e39',
            },
            timeScale: {
                borderColor: '#2a2e39',
                visible: false,
            },
        });

        // Histogram
        this.series.macd_histogram = this.macdChart.addHistogramSeries({
            priceFormat: {
                type: 'volume',
            },
        });

        // MACD Line
        this.series.macd_line = this.macdChart.addLineSeries({
            color: '#3b82f6',
            lineWidth: 2,
            title: 'MACD',
            priceLineVisible: false,
        });

        // Signal Line
        this.series.macd_signal = this.macdChart.addLineSeries({
            color: '#f59e0b',
            lineWidth: 2,
            title: 'Signal',
            priceLineVisible: false,
        });

        // Sync with main chart
        this.mainChart.timeScale().subscribeVisibleTimeRangeChange(() => {
            const range = this.mainChart.timeScale().getVisibleRange();
            this.macdChart.timeScale().setVisibleRange(range);
        });
    }

    initVolumeChart() {
        const container = document.getElementById('volume-chart-container');
        if (!container) return;

        this.volumeChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 90,
            layout: {
                background: { color: '#1a1d2e' },
                textColor: '#a5b1c2',
            },
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
            },
            rightPriceScale: {
                borderColor: '#2a2e39',
            },
            timeScale: {
                borderColor: '#2a2e39',
                visible: true,
                timeVisible: true,
            },
        });

        this.series.volume = this.volumeChart.addHistogramSeries({
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: '',
        });

        // Sync with main chart
        this.mainChart.timeScale().subscribeVisibleTimeRangeChange(() => {
            const range = this.mainChart.timeScale().getVisibleRange();
            this.volumeChart.timeScale().setVisibleRange(range);
        });
    }

    async loadData(stockCode, timeframe = null) {
        try {
            this.currentStockCode = stockCode;
            if (timeframe) {
                this.currentTimeframe = timeframe;
            }

            const url = `/api/chart/${stockCode}?timeframe=D`; // Always fetch daily data first
            const response = await fetch(url);
            const data = await response.json();

            if (!data.success || !data.data || data.data.length === 0) {
                console.error('No chart data available');
                this.showError('차트 데이터를 불러올 수 없습니다.');
                return;
            }

            // Store raw data for timeframe conversion
            this.rawData = data;

            // Convert data based on timeframe
            const processedData = this.convertTimeframe(data.data, this.currentTimeframe);

            // Update chart
            this.updateChartWithData(processedData, data);

        } catch (error) {
            console.error('Error loading chart data:', error);
            this.showError('차트 데이터 로드 실패');
        }
    }

    convertTimeframe(dailyData, timeframe) {
        if (timeframe === 'D' || timeframe.match(/^\d+$/)) {
            // For daily or minute data, return as is
            return dailyData;
        }

        if (timeframe === 'W') {
            // Convert to weekly
            return this.aggregateToWeekly(dailyData);
        }

        if (timeframe === 'M') {
            // Convert to monthly
            return this.aggregateToMonthly(dailyData);
        }

        return dailyData;
    }

    aggregateToWeekly(dailyData) {
        const weekly = [];
        let weekData = [];
        let lastDate = null;

        dailyData.forEach((day, index) => {
            const date = new Date(day.time);
            const weekNum = this.getWeekNumber(date);

            if (lastDate && weekNum !== this.getWeekNumber(lastDate)) {
                // New week, aggregate previous week
                if (weekData.length > 0) {
                    weekly.push(this.aggregateCandles(weekData));
                    weekData = [];
                }
            }

            weekData.push(day);
            lastDate = date;

            // Last item
            if (index === dailyData.length - 1 && weekData.length > 0) {
                weekly.push(this.aggregateCandles(weekData));
            }
        });

        return weekly;
    }

    aggregateToMonthly(dailyData) {
        const monthly = [];
        let monthData = [];
        let lastMonth = null;

        dailyData.forEach((day, index) => {
            const date = new Date(day.time);
            const month = date.getFullYear() * 12 + date.getMonth();

            if (lastMonth !== null && month !== lastMonth) {
                // New month, aggregate previous month
                if (monthData.length > 0) {
                    monthly.push(this.aggregateCandles(monthData));
                    monthData = [];
                }
            }

            monthData.push(day);
            lastMonth = month;

            // Last item
            if (index === dailyData.length - 1 && monthData.length > 0) {
                monthly.push(this.aggregateCandles(monthData));
            }
        });

        return monthly;
    }

    aggregateCandles(candles) {
        if (candles.length === 0) return null;

        const firstCandle = candles[0];
        const lastCandle = candles[candles.length - 1];

        return {
            time: lastCandle.time, // Use last candle's time
            open: firstCandle.open,
            high: Math.max(...candles.map(c => c.high)),
            low: Math.min(...candles.map(c => c.low)),
            close: lastCandle.close,
        };
    }

    getWeekNumber(date) {
        const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
        const dayNum = d.getUTCDay() || 7;
        d.setUTCDate(d.getUTCDate() + 4 - dayNum);
        const yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
        return Math.ceil((((d - yearStart) / 86400000) + 1)/7);
    }

    updateChartWithData(chartData, originalData) {
        // Update chart title and price
        const chartStockName = document.getElementById('chart-stock-name');
        const chartPrice = document.getElementById('chart-price');
        if (chartStockName) {
            chartStockName.textContent = originalData.name || this.currentStockCode;
        }
        if (chartPrice && originalData.current_price) {
            chartPrice.textContent = '₩' + this.formatNumber(originalData.current_price);
        }

        // Set candlestick data
        this.candlestickSeries.setData(chartData);

        // Set indicator data
        const indicators = originalData.indicators || {};

        if (indicators.ma5 && this.series.ma5) {
            this.series.ma5.setData(indicators.ma5);
        }

        if (indicators.ma20 && this.series.ma20) {
            this.series.ma20.setData(indicators.ma20);
        }

        if (indicators.ma60 && this.series.ma60) {
            this.series.ma60.setData(indicators.ma60);
        }

        if (indicators.bb_upper && this.series.bb_upper) {
            this.series.bb_upper.setData(indicators.bb_upper);
            this.series.bb_middle.setData(indicators.bb_middle);
            this.series.bb_lower.setData(indicators.bb_lower);
        }

        if (indicators.rsi && this.series.rsi) {
            this.series.rsi.setData(indicators.rsi);
        }

        if (indicators.macd && this.series.macd_line) {
            const macdData = indicators.macd.map(item => ({
                time: item.time,
                value: item.macd
            }));

            const signalData = indicators.macd.map(item => ({
                time: item.time,
                value: item.signal
            }));

            const histogramData = indicators.macd.map(item => ({
                time: item.time,
                value: item.histogram,
                color: item.histogram >= 0 ? 'rgba(38, 166, 154, 0.8)' : 'rgba(239, 83, 80, 0.8)'
            }));

            this.series.macd_line.setData(macdData);
            this.series.macd_signal.setData(signalData);
            this.series.macd_histogram.setData(histogramData);
        }

        if (indicators.volume && this.series.volume) {
            this.series.volume.setData(indicators.volume);
        }

        console.log('Chart updated successfully');
    }

    toggleIndicator(indicator) {
        this.indicatorsVisible[indicator] = !this.indicatorsVisible[indicator];

        const btn = event.target.closest('[data-indicator="' + indicator + '"]');
        if (btn) {
            btn.classList.toggle('active');
        }

        switch(indicator) {
            case 'ma5':
                this.series.ma5.applyOptions({ visible: this.indicatorsVisible.ma5 });
                break;
            case 'ma20':
                this.series.ma20.applyOptions({ visible: this.indicatorsVisible.ma20 });
                break;
            case 'ma60':
                this.series.ma60.applyOptions({ visible: this.indicatorsVisible.ma60 });
                break;
            case 'bb':
                const visible = this.indicatorsVisible.bb;
                this.series.bb_upper.applyOptions({ visible });
                this.series.bb_middle.applyOptions({ visible });
                this.series.bb_lower.applyOptions({ visible });
                break;
        }
    }

    togglePanel(panel) {
        this.panelsVisible[panel] = !this.panelsVisible[panel];

        const container = document.getElementById(`${panel}-chart-container`);
        if (container) {
            container.style.display = this.panelsVisible[panel] ? 'block' : 'none';
        }

        // Toggle button state
        const btn = event.target.closest('.ctrl-btn');
        if (btn) {
            btn.classList.toggle('active');
        }

        // Resize charts
        setTimeout(() => this.handleResize(), 100);
    }

    async changeTimeframe(timeframe) {
        try {
            this.showLoading();

            // Update button states
            document.querySelectorAll('[data-timeframe]').forEach(btn => {
                if (btn.getAttribute('data-timeframe') === timeframe) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            this.currentTimeframe = timeframe;

            // If we have raw data, just convert it
            if (this.rawData && (timeframe === 'D' || timeframe === 'W' || timeframe === 'M')) {
                const processedData = this.convertTimeframe(this.rawData.data, timeframe);
                this.updateChartWithData(processedData, this.rawData);
            } else if (timeframe.match(/^\d+$/)) {
                // Minute data - fetch from server
                const url = `/api/chart/${this.currentStockCode}?timeframe=${timeframe}`;
                const response = await fetch(url);
                const data = await response.json();

                if (data.success && data.data) {
                    this.updateChartWithData(data.data, data);

                    // Show warning if fallback occurred
                    if (data.timeframe !== timeframe) {
                        this.showWarning(`${timeframe}분봉 데이터를 사용할 수 없어 일봉을 표시합니다.`);
                    }
                }
            } else {
                // Re-fetch data
                await this.loadData(this.currentStockCode, timeframe);
            }

        } catch (error) {
            console.error('Timeframe change error:', error);
            this.showError('시간봉 변경 실패');
        } finally {
            this.hideLoading();
        }
    }

    setDrawingMode(mode) {
        this.drawingMode = this.drawingMode === mode ? null : mode;

        // Update button states
        document.querySelectorAll('.draw-btn').forEach(btn => {
            const btnMode = btn.getAttribute('onclick')?.match(/setDrawingMode\('(.+?)'\)/)?.[1];
            if (btnMode && btnMode === mode) {
                if (this.drawingMode) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            }
        });

        if (this.drawingMode) {
            this.canvas.style.cursor = 'crosshair';
        } else {
            this.canvas.style.cursor = 'default';
        }
    }

    clearDrawings() {
        this.drawings = [];
        this.redrawCanvas();
    }

    setupDrawingTools() {
        this.canvas = document.getElementById('drawing-canvas');
        if (!this.canvas) return;

        const mainContainer = document.getElementById('main-chart-container');
        this.canvas.width = mainContainer.clientWidth;
        this.canvas.height = mainContainer.offsetHeight;
        this.ctx = this.canvas.getContext('2d');

        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        this.canvas.addEventListener('mouseleave', (e) => this.onMouseUp(e));
    }

    onMouseDown(e) {
        if (!this.drawingMode) return;

        const rect = this.canvas.getBoundingClientRect();
        this.isDrawing = true;
        this.startPoint = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    onMouseMove(e) {
        if (!this.isDrawing || !this.drawingMode) return;

        const rect = this.canvas.getBoundingClientRect();
        const currentPoint = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };

        this.redrawCanvas();

        this.ctx.strokeStyle = '#3b82f6';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([]);
        this.ctx.beginPath();

        if (this.drawingMode === 'trendline') {
            this.ctx.moveTo(this.startPoint.x, this.startPoint.y);
            this.ctx.lineTo(currentPoint.x, currentPoint.y);
        } else if (this.drawingMode === 'horizontal') {
            this.ctx.moveTo(0, this.startPoint.y);
            this.ctx.lineTo(this.canvas.width, this.startPoint.y);
        } else if (this.drawingMode === 'vertical') {
            this.ctx.moveTo(this.startPoint.x, 0);
            this.ctx.lineTo(this.startPoint.x, this.canvas.height);
        }

        this.ctx.stroke();
    }

    onMouseUp(e) {
        if (!this.isDrawing || !this.drawingMode) return;

        const rect = this.canvas.getBoundingClientRect();
        const endPoint = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };

        this.drawings.push({
            type: this.drawingMode,
            start: this.startPoint,
            end: endPoint,
            color: '#3b82f6'
        });

        this.isDrawing = false;
        this.redrawCanvas();
    }

    redrawCanvas() {
        if (!this.ctx) return;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.drawings.forEach(drawing => {
            this.ctx.strokeStyle = drawing.color;
            this.ctx.lineWidth = 2;
            this.ctx.setLineDash([]);
            this.ctx.beginPath();

            if (drawing.type === 'trendline') {
                this.ctx.moveTo(drawing.start.x, drawing.start.y);
                this.ctx.lineTo(drawing.end.x, drawing.end.y);
            } else if (drawing.type === 'horizontal') {
                this.ctx.moveTo(0, drawing.start.y);
                this.ctx.lineTo(this.canvas.width, drawing.start.y);
            } else if (drawing.type === 'vertical') {
                this.ctx.moveTo(drawing.start.x, 0);
                this.ctx.lineTo(drawing.start.x, this.canvas.height);
            }

            this.ctx.stroke();
        });
    }

    handleResize() {
        const mainContainer = document.getElementById('main-chart-container');
        const rsiContainer = document.getElementById('rsi-chart-container');
        const macdContainer = document.getElementById('macd-chart-container');
        const volumeContainer = document.getElementById('volume-chart-container');

        if (this.mainChart && mainContainer) {
            this.mainChart.applyOptions({ width: mainContainer.clientWidth });
        }
        if (this.rsiChart && rsiContainer) {
            this.rsiChart.applyOptions({ width: rsiContainer.clientWidth });
        }
        if (this.macdChart && macdContainer) {
            this.macdChart.applyOptions({ width: macdContainer.clientWidth });
        }
        if (this.volumeChart && volumeContainer) {
            this.volumeChart.applyOptions({ width: volumeContainer.clientWidth });
        }

        if (this.canvas && mainContainer) {
            this.canvas.width = mainContainer.clientWidth;
            this.canvas.height = mainContainer.offsetHeight;
            this.redrawCanvas();
        }
    }

    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    showLoading() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        let loader = container.querySelector('.chart-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.className = 'chart-loader';
            loader.innerHTML = `
                <div class="chart-loader-spinner"></div>
                <div class="chart-loader-text">차트 로딩 중...</div>
            `;
            container.appendChild(loader);
        }
        loader.style.display = 'flex';
    }

    hideLoading() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const loader = container.querySelector('.chart-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showWarning(message) {
        this.showToast(message, 'warning');
    }

    showToast(message, type = 'info') {
        const existingToasts = document.querySelectorAll('.chart-toast');
        existingToasts.forEach(toast => toast.remove());

        const toast = document.createElement('div');
        toast.className = `chart-toast chart-toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 10);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

// Global instance
let advancedChart = null;

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    advancedChart = new AdvancedTradingChart('main-chart');
    advancedChart.initialize();
    advancedChart.loadData('005930');
});
