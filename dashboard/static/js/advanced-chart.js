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
                    <button class="toolbar-btn" onclick="advancedChart.toggleIndicator('ma5')" title="SMA 5">
                        <i class="fas fa-chart-line"></i> MA5
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.toggleIndicator('ma20')" title="SMA 20">
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
                    <button class="toolbar-btn" onclick="advancedChart.setDrawingMode('trendline')" title="추세선">
                        <i class="fas fa-slash"></i>
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.setDrawingMode('horizontal')" title="수평선">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.setDrawingMode('vertical')" title="수직선">
                        <i class="fas fa-grip-lines-vertical"></i>
                    </button>
                    <button class="toolbar-btn" onclick="advancedChart.clearDrawings()" title="그리기 지우기">
                        <i class="fas fa-eraser"></i>
                    </button>
                </div>
            </div>

            <div id="main-chart-container" class="chart-panel" style="height: 400px;"></div>
            <div id="rsi-chart-container" class="chart-panel" style="height: 120px; margin-top: 10px;"></div>
            <div id="macd-chart-container" class="chart-panel" style="height: 150px; margin-top: 10px;"></div>
            <div id="volume-chart-container" class="chart-panel" style="height: 100px; margin-top: 10px;"></div>
        `;
    }

    initMainChart() {
        const container = document.getElementById('main-chart-container');

        this.mainChart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 400,
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
            height: 120,
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
            height: 150,
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

    async loadData(stockCode) {
        try {
            const response = await fetch(`/api/chart/${stockCode}`);
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

    setDrawingMode(mode) {
        this.drawingMode = this.drawingMode === mode ? null : mode;

        // Update button states
        document.querySelectorAll('.toolbar-btn').forEach(btn => {
            const btnMode = btn.getAttribute('onclick')?.match(/setDrawingMode\('(.+?)'\)/)?.[1];
            if (btnMode === mode) {
                btn.classList.toggle('active');
            }
        });

        // TODO: Implement actual drawing functionality
        // This requires additional canvas overlay or custom plugin
        if (this.drawingMode) {
            console.log('Drawing mode activated:', mode);
            alert(`그리기 모드: ${mode}\n\n차트를 클릭하여 그리기를 시작하세요.\n(이 기능은 추가 개발이 필요합니다)`);
        }
    }

    clearDrawings() {
        this.drawings = [];
        console.log('All drawings cleared');
        // TODO: Implement actual clearing
    }

    setupDrawingTools() {
        // TODO: Implement drawing tools
        // This requires creating a canvas overlay on top of the chart
        // or using a plugin system
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
