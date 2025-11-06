/**
 * Real-time Dashboard Enhancer v1.0
 * 실시간 데이터 업데이트, 애니메이션, 인터랙션 강화
 */

class RealTimeEnhancer {
    constructor() {
        this.updateInterval = 5000;
        this.animationQueue = [];
        this.observers = new Map();
        this.cache = new Map();
        this.cacheTimeout = 30000;

        this.init();
    }

    init() {
        console.log('🚀 Real-time Dashboard Enhancer initialized');
        this.setupIntersectionObserver();
        this.setupMouseTracking();
        this.setupNumberAnimations();
        this.setupAutoRefresh();
        this.setupLoadingStates();
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in-up');
                    }
                });
            },
            { threshold: 0.1, rootMargin: '50px' }
        );

        document.querySelectorAll('.card, .stat-card, .glass-card').forEach((el) => {
            observer.observe(el);
        });

        this.observers.set('intersection', observer);
    }

    setupMouseTracking() {
        document.querySelectorAll('.glow-on-hover').forEach((el) => {
            el.addEventListener('mousemove', (e) => {
                const rect = el.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                el.style.setProperty('--mouse-x', `${x}px`);
                el.style.setProperty('--mouse-y', `${y}px`);
            });
        });
    }

    setupNumberAnimations() {
        const animateNumber = (el, start, end, duration = 1000) => {
            const range = end - start;
            const increment = range / (duration / 16);
            let current = start;

            const timer = setInterval(() => {
                current += increment;
                if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                    current = end;
                    clearInterval(timer);
                }

                const formatted = this.formatNumber(current);
                el.textContent = formatted;
            }, 16);

            return timer;
        };

        document.querySelectorAll('[data-animate-number]').forEach((el) => {
            const value = parseFloat(el.textContent.replace(/[^0-9.-]/g, ''));
            if (!isNaN(value)) {
                el.setAttribute('data-original-value', value);
                animateNumber(el, 0, value, 1000);
            }
        });
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return Math.round(num).toLocaleString();
    }

    setupAutoRefresh() {
        const refreshElements = document.querySelectorAll('[data-auto-refresh]');

        refreshElements.forEach((el) => {
            const url = el.getAttribute('data-refresh-url');
            const interval = parseInt(el.getAttribute('data-refresh-interval')) || this.updateInterval;

            if (url) {
                this.startAutoRefresh(el, url, interval);
            }
        });
    }

    async startAutoRefresh(element, url, interval) {
        const refresh = async () => {
            const cachedData = this.getCache(url);
            if (cachedData) {
                this.updateElement(element, cachedData);
                return;
            }

            try {
                element.classList.add('loading-shimmer');

                const response = await fetch(url, {
                    headers: { 'Accept': 'application/json' }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.setCache(url, data);
                    this.updateElement(element, data);
                } else {
                    console.error(`Failed to refresh ${url}:`, response.statusText);
                }
            } catch (error) {
                console.error(`Error refreshing ${url}:`, error);
            } finally {
                element.classList.remove('loading-shimmer');
            }
        };

        await refresh();
        setInterval(refresh, interval);
    }

    updateElement(element, data) {
        const updateType = element.getAttribute('data-update-type') || 'html';

        switch (updateType) {
            case 'number':
                this.updateNumber(element, data.value);
                break;
            case 'progress':
                this.updateProgress(element, data.percentage);
                break;
            case 'chart':
                this.updateChart(element, data);
                break;
            default:
                if (data.html) {
                    element.innerHTML = data.html;
                    this.reinitializeAnimations(element);
                }
        }

        element.classList.add('updated-flash');
        setTimeout(() => element.classList.remove('updated-flash'), 500);
    }

    updateNumber(element, newValue) {
        const current = parseFloat(element.textContent.replace(/[^0-9.-]/g, ''));
        const target = parseFloat(newValue);

        if (isNaN(current) || isNaN(target)) return;

        const range = target - current;
        const duration = 500;
        const steps = 30;
        const increment = range / steps;
        let step = 0;

        const animate = setInterval(() => {
            step++;
            const value = current + (increment * step);
            element.textContent = this.formatNumber(value);

            if (step >= steps) {
                clearInterval(animate);
                element.textContent = this.formatNumber(target);
            }
        }, duration / steps);
    }

    updateProgress(element, percentage) {
        const progressBar = element.querySelector('.progress-bar-fill');
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }

        const progressRing = element.querySelector('.progress-ring-circle');
        if (progressRing) {
            const circumference = 2 * Math.PI * parseFloat(progressRing.getAttribute('r'));
            const offset = circumference - (percentage / 100) * circumference;
            progressRing.style.strokeDashoffset = offset;
        }
    }

    updateChart(element, data) {
        const event = new CustomEvent('chart-update', { detail: data });
        element.dispatchEvent(event);
    }

    reinitializeAnimations(container) {
        container.querySelectorAll('.fade-in-up').forEach((el) => {
            el.classList.remove('fade-in-up');
            setTimeout(() => el.classList.add('fade-in-up'), 10);
        });

        this.setupNumberAnimations();
    }

    setupLoadingStates() {
        const originalFetch = window.fetch;

        window.fetch = async (...args) => {
            const url = args[0];
            const loadingId = `loading-${Date.now()}-${Math.random()}`;

            this.showGlobalLoading(loadingId);

            try {
                const response = await originalFetch(...args);
                return response;
            } finally {
                this.hideGlobalLoading(loadingId);
            }
        };
    }

    showGlobalLoading(id) {
        let indicator = document.getElementById('global-loading');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'global-loading';
            indicator.className = 'fixed top-0 left-0 right-0 h-1 z-50';
            indicator.innerHTML = '<div class="progress-bar-fill h-full"></div>';
            document.body.appendChild(indicator);
        }

        indicator.setAttribute('data-loading-count',
            (parseInt(indicator.getAttribute('data-loading-count')) || 0) + 1
        );

        indicator.style.display = 'block';
    }

    hideGlobalLoading(id) {
        const indicator = document.getElementById('global-loading');
        if (!indicator) return;

        const count = parseInt(indicator.getAttribute('data-loading-count')) || 1;
        const newCount = Math.max(0, count - 1);

        indicator.setAttribute('data-loading-count', newCount);

        if (newCount === 0) {
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 300);
        }
    }

    getCache(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;

        const now = Date.now();
        if (now - cached.timestamp > this.cacheTimeout) {
            this.cache.delete(key);
            return null;
        }

        return cached.data;
    }

    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    clearCache() {
        this.cache.clear();
    }

    addRippleEffect(element) {
        element.classList.add('ripple');

        element.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple-effect');

            this.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        });
    }

    toast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} alert-slide-in`;
        toast.innerHTML = `
            <div class="flex items-center gap-3 p-4 rounded-lg shadow-lg bg-white">
                <div class="toast-icon">${this.getToastIcon(type)}</div>
                <div class="toast-message">${message}</div>
            </div>
        `;

        const container = document.getElementById('toast-container') || this.createToastContainer();
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
        document.body.appendChild(container);
        return container;
    }

    getToastIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        return icons[type] || icons.info;
    }

    smoothScrollTo(element, duration = 500) {
        const targetPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        let startTime = null;

        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = easeInOutQuad(timeElapsed, startPosition, distance, duration);
            window.scrollTo(0, run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        }

        function easeInOutQuad(t, b, c, d) {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        }

        requestAnimationFrame(animation);
    }

    destroy() {
        this.observers.forEach((observer) => observer.disconnect());
        this.observers.clear();
        this.cache.clear();
        this.animationQueue = [];
    }
}

const enhancer = new RealTimeEnhancer();

window.dashboardEnhancer = enhancer;

document.addEventListener('DOMContentLoaded', () => {
    console.log('✨ Dashboard enhancements loaded');

    document.querySelectorAll('button, .btn').forEach((btn) => {
        enhancer.addRippleEffect(btn);
    });

    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach((link) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                enhancer.smoothScrollTo(target);
            }
        });
    });
});

export default RealTimeEnhancer;
