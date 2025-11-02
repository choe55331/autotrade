/**
 * Advanced Chart with Indicators and Drawing Tools
 * Features: RSI, MACD, Volume, Moving Averages, Bollinger Bands, Drawing Tools
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
        if (this.indicatorsVisible.rsi) this.initRSIChart();
        if (this.indicatorsVisible.macd) this.initMACDChart();
        if (this.indicatorsVisible.volume) this.initVolumeChart();

        // Setup drawing tools
        this.setupDrawingTools();

        // Handle resize
        window.addEventListener('resize', () => this.handleResize());
    }

    createChartLayout(container) {
        container.innerHTML = `
            <div class="chart-toolbar" id="chart-toolbar">
                <div class="toolbar-group">
                    <label style="color: #9ca3af; font-size: 11px; margin-right: 5px;">시간:</label>
                    <button class="toolbar-btn timeframe-btn" data-timeframe="1" onclick="advancedChart.changeTimeframe('1')" title="1분봉">1분</button>
                    <button class="toolbar-btn timeframe-btn" data-timeframe="3" onclick="advancedChart.changeTimeframe('3')" title="3분봉">3분</button>
                    <button class="toolbar-btn timeframe-btn" data-timeframe="5" onclick="advancedChart.changeTimeframe('5')" title="5분봉">5분</button>
                    <button class="toolbar-btn timeframe-btn" data-timeframe="10" onclick="advancedChart.changeTimeframe('10')" title="10분봉">10분</button>
                    <button class="toolbar-btn timeframe-btn" data-timeframe="30" onclick="advancedChart.changeTimeframe('30')" title="30분봉">30분</button>
                    <button class="toolbar-btn timeframe-btn" data-timeframe="60" onclick="advancedChart.changeTimeframe('60')" title="60분봉">1시간</button>
                    <button class="toolbar-btn timeframe-btn active" data-timeframe="D" onclick="advancedChart.changeTimeframe('D')" title="일봉">일봉</button>
                    <button class="toolbar-btn timeframe-btn" data-timeframe="W" onclick="advancedChart.changeTimeframe('W')" title="주봉">주봉</button>
                    <button class="toolbar-btn timeframe-btn" data-timeframe="M" onclick="advancedChart.changeTimeframe('M')" title="월봉">월봉</button>
                </div>
                <div class="toolbar-group">
                    <label style="color: #9ca3af; font-size: 11px; margin-right: 5px;">지표:</label>
                    <button class="toolbar-btn active" onclick="advancedChart.toggleIndicator('ma5')" title="SMA 5">
                        <i class="fas fa-chart-line"></i> MA5
                    </button>
                    <button class="toolbar-btn active" onclick="advancedChart.toggleIndicator('ma20')" title="SMA 20">
                        <i class="fas fa-chart-line"></i> MA20
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.toggleIndicator('ma60')" title="SMA 60">
                        <i class="fas fa-chart-line"></i> MA60
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.toggleIndicator('bb')" title="Bollinger Bands">
                        <i class="fas fa-chart-area"></i> BB
                    </button>
                </div>
                <div class="toolbar-group">
                    <label style="color: #9ca3af; font-size: 11px; margin-right: 5px;">그리기:</label>
                    <button class="toolbar-btn" onclick="advancedChart.setDrawingMode('trendline')" title="추세선">
                        <i class="fas fa-slash"></i>
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.setDrawingMode('horizontal')" title="수평선">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.setDrawingMode('ray')" title="Ray (수평 연장선)">
                        <i class="fas fa-arrow-right"></i>
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.clearDrawings()" title="그리기 지우기">
                        <i class="fas fa-eraser"></i>
                    </button>
                </div>
            </div>

            <div style="position: relative;">
                <canvas id="drawing-canvas" style="position: absolute; top: 0; left: 0; z-index: 10; pointer-events: auto;"></canvas>
                <div id="main-chart-container" class="chart-panel" style="height: 300px; position: relative;"></div>
            </div>
            <div id="rsi-chart-container" class="chart-panel" style="height: 80px; margin-top: 5px;"></div>
            <div id="macd-chart-container" class="chart-panel" style="height: 100px; margin-top: 5px;"></div>
            <div id="volume-chart-container" class="chart-panel" style="height: 70px; margin-top: 5px;"></div>
        `;
    }

    initMainChart() {
        const container = document.getElementById('main-chart-container');

        this.mainChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 300,
            layout: {
                background: { color: '#1e2139' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: '#2d3250' },
                horzLines: { color: '#2d3250' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#2d3250',
            },
            timeScale: {
                borderColor: '#2d3250',
                timeVisible: true,
            },
        });

        // Add candlestick series
        this.candlestickSeries = this.mainChart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });

        // Add MA series
        this.series.ma5 = this.mainChart.addLineSeries({
            color: '#f59e0b',
            lineWidth: 1,
            title: 'MA5',
            visible: this.indicatorsVisible.ma5
        });

        this.series.ma20 = this.mainChart.addLineSeries({
            color: '#3b82f6',
            lineWidth: 1,
            title: 'MA20',
            visible: this.indicatorsVisible.ma20
        });

        this.series.ma60 = this.mainChart.addLineSeries({
            color: '#8b5cf6',
            lineWidth: 1,
            title: 'MA60',
            visible: this.indicatorsVisible.ma60
        });

        // Bollinger Bands
        this.series.bb_upper = this.mainChart.addLineSeries({
            color: '#6b7280',
            lineWidth: 1,
            lineStyle: 2, // Dashed
            visible: this.indicatorsVisible.bb
        });

        this.series.bb_middle = this.mainChart.addLineSeries({
            color: '#9ca3af',
            lineWidth: 1,
            visible: this.indicatorsVisible.bb
        });

        this.series.bb_lower = this.mainChart.addLineSeries({
            color: '#6b7280',
            lineWidth: 1,
            lineStyle: 2, // Dashed
            visible: this.indicatorsVisible.bb
        });
    }

    initRSIChart() {
        const container = document.getElementById('rsi-chart-container');

        this.rsiChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 80,
            layout: {
                background: { color: '#1e2139' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: '#2d3250' },
                horzLines: { color: '#2d3250' },
            },
            rightPriceScale: {
                borderColor: '#2d3250',
                scaleMargins: {
                    top: 0.1,
                    bottom: 0.1,
                },
            },
            timeScale: {
                borderColor: '#2d3250',
                visible: false,
            },
        });

        this.series.rsi = this.rsiChart.addLineSeries({
            color: '#8b5cf6',
            lineWidth: 2,
            title: 'RSI(14)',
        });

        // Add reference lines at 30 and 70
        this.rsiChart.addLineSeries({
            color: '#ef4444',
            lineWidth: 1,
            lineStyle: 2,
            priceLineVisible: false,
        }).setData([{time: '2020-01-01', value: 70}, {time: '2030-01-01', value: 70}]);

        this.rsiChart.addLineSeries({
            color: '#10b981',
            lineWidth: 1,
            lineStyle: 2,
            priceLineVisible: false,
        }).setData([{time: '2020-01-01', value: 30}, {time: '2030-01-01', value: 30}]);

        // Synchronize timeScale with main chart
        this.mainChart.timeScale().subscribeVisibleTimeRangeChange(() => {
            const range = this.mainChart.timeScale().getVisibleRange();
            this.rsiChart.timeScale().setVisibleRange(range);
        });
    }

    initMACDChart() {
        const container = document.getElementById('macd-chart-container');

        this.macdChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 100,
            layout: {
                background: { color: '#1e2139' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: '#2d3250' },
                horzLines: { color: '#2d3250' },
            },
            rightPriceScale: {
                borderColor: '#2d3250',
            },
            timeScale: {
                borderColor: '#2d3250',
                visible: false,
            },
        });

        // Histogram
        this.series.macd_histogram = this.macdChart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',
            },
        });

        // MACD Line
        this.series.macd_line = this.macdChart.addLineSeries({
            color: '#2962FF',
            lineWidth: 2,
            title: 'MACD',
        });

        // Signal Line
        this.series.macd_signal = this.macdChart.addLineSeries({
            color: '#FF6D00',
            lineWidth: 2,
            title: 'Signal',
        });

        // Synchronize timeScale with main chart
        this.mainChart.timeScale().subscribeVisibleTimeRangeChange(() => {
            const range = this.mainChart.timeScale().getVisibleRange();
            this.macdChart.timeScale().setVisibleRange(range);
        });
    }

    initVolumeChart() {
        const container = document.getElementById('volume-chart-container');

        this.volumeChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 70,
            layout: {
                background: { color: '#1e2139' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: '#2d3250' },
                horzLines: { color: '#2d3250' },
            },
            rightPriceScale: {
                borderColor: '#2d3250',
            },
            timeScale: {
                borderColor: '#2d3250',
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

        // Synchronize timeScale with main chart
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

            const url = `/api/chart/${stockCode}?timeframe=${this.currentTimeframe}`;
            const response = await fetch(url);
            const data = await response.json();

            if (!data.success || !data.data || data.data.length === 0) {
                console.error('No chart data available');
                return;
            }

            // Update chart title and price
            const chartStockName = document.getElementById('chart-stock-name');
            const chartPrice = document.getElementById('chart-price');
            if (chartStockName) {
                chartStockName.textContent = data.name || stockCode;
            }
            if (chartPrice && data.current_price) {
                chartPrice.textContent = '₩' + this.formatNumber(data.current_price);
            }

            // Set main candlestick data
            this.candlestickSeries.setData(data.data);

            // Set indicator data
            const indicators = data.indicators || {};

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
                // Format MACD data
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
                    color: item.histogram >= 0 ? '#26a69a' : '#ef5350'
                }));

                this.series.macd_line.setData(macdData);
                this.series.macd_signal.setData(signalData);
                this.series.macd_histogram.setData(histogramData);
            }

            if (indicators.volume && this.series.volume) {
                this.series.volume.setData(indicators.volume);
            }

            console.log('Chart data loaded successfully');
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    toggleIndicator(indicator) {
        this.indicatorsVisible[indicator] = !this.indicatorsVisible[indicator];

        const btn = event.target.closest('.toolbar-btn');
        btn.classList.toggle('active');

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

    async changeTimeframe(timeframe) {
        this.currentTimeframe = timeframe;

        // Update button states
        document.querySelectorAll('.timeframe-btn').forEach(btn => {
            if (btn.getAttribute('data-timeframe') === timeframe) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Reload data with new timeframe
        await this.loadData(this.currentStockCode, timeframe);
    }

    setDrawingMode(mode) {
        this.drawingMode = this.drawingMode === mode ? null : mode;

        // Update button states
        document.querySelectorAll('.toolbar-btn').forEach(btn => {
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
            console.log('Drawing mode activated:', mode);
            this.canvas.style.cursor = 'crosshair';
        } else {
            this.canvas.style.cursor = 'default';
        }
    }

    clearDrawings() {
        this.drawings = [];
        this.redrawCanvas();
        console.log('All drawings cleared');
    }

    setupDrawingTools() {
        this.canvas = document.getElementById('drawing-canvas');
        if (!this.canvas) return;

        const mainContainer = document.getElementById('main-chart-container');
        this.canvas.width = mainContainer.clientWidth;
        this.canvas.height = mainContainer.offsetHeight;
        this.ctx = this.canvas.getContext('2d');

        // Mouse events
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

        // Redraw all existing drawings
        this.redrawCanvas();

        // Draw current line being created
        this.ctx.strokeStyle = '#3b82f6';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();

        if (this.drawingMode === 'trendline') {
            this.ctx.moveTo(this.startPoint.x, this.startPoint.y);
            this.ctx.lineTo(currentPoint.x, currentPoint.y);
        } else if (this.drawingMode === 'horizontal') {
            this.ctx.moveTo(0, this.startPoint.y);
            this.ctx.lineTo(this.canvas.width, this.startPoint.y);
        } else if (this.drawingMode === 'ray') {
            this.ctx.moveTo(this.startPoint.x, this.startPoint.y);
            this.ctx.lineTo(this.canvas.width, this.startPoint.y);
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

        // Save the drawing
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

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Redraw all saved drawings
        this.drawings.forEach(drawing => {
            this.ctx.strokeStyle = drawing.color;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();

            if (drawing.type === 'trendline') {
                this.ctx.moveTo(drawing.start.x, drawing.start.y);
                this.ctx.lineTo(drawing.end.x, drawing.end.y);
            } else if (drawing.type === 'horizontal') {
                this.ctx.moveTo(0, drawing.start.y);
                this.ctx.lineTo(this.canvas.width, drawing.start.y);
            } else if (drawing.type === 'ray') {
                this.ctx.moveTo(drawing.start.x, drawing.start.y);
                this.ctx.lineTo(this.canvas.width, drawing.start.y);
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

        // Resize canvas
        if (this.canvas && mainContainer) {
            this.canvas.width = mainContainer.clientWidth;
            this.canvas.height = mainContainer.offsetHeight;
            this.redrawCanvas();
        }
    }

    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
}

// Global instance
let advancedChart = null;

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    advancedChart = new AdvancedTradingChart('main-chart');
    advancedChart.initialize();

    // Load default stock
    advancedChart.loadData('005930');
});
