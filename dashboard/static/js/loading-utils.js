/**
 * Loading & Animation Utilities (v5.11)
 * 로딩 상태 관리, 스켈레톤 UI, 애니메이션 헬퍼
 */

// ============================================================================
// Loading State Manager
// ============================================================================

class LoadingManager {
    constructor() {
        this.loadingStates = new Map();
        this.defaultTimeout = 30000; // 30 seconds
    }

    /**
     * Show loading state for a specific element
     * @param {string} elementId - Target element ID
     * @param {Object} options - Loading options
     */
    show(elementId, options = {}) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Element not found: ${elementId}`);
            return;
        }

        const config = {
            type: options.type || 'spinner', // spinner, skeleton, dots, progress
            size: options.size || 'md', // sm, md, lg
            text: options.text || 'Loading...',
            overlay: options.overlay !== false,
            ...options
        };

        // Save original content
        if (!this.loadingStates.has(elementId)) {
            this.loadingStates.set(elementId, {
                originalContent: element.innerHTML,
                originalClass: element.className
            });
        }

        // Apply loading state
        element.classList.add('loading-active');

        if (config.overlay) {
            element.style.position = 'relative';
        }

        const loadingHTML = this._getLoadingHTML(config);

        if (config.overlay) {
            element.innerHTML += loadingHTML;
        } else {
            element.innerHTML = loadingHTML;
        }

        // Auto-hide after timeout
        if (config.timeout !== false) {
            setTimeout(() => {
                this.hide(elementId);
            }, config.timeout || this.defaultTimeout);
        }
    }

    /**
     * Hide loading state
     * @param {string} elementId - Target element ID
     */
    hide(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const savedState = this.loadingStates.get(elementId);
        if (savedState) {
            element.innerHTML = savedState.originalContent;
            element.className = savedState.originalClass;
            this.loadingStates.delete(elementId);
        }

        element.classList.remove('loading-active');
    }

    /**
     * Generate loading HTML based on type
     * @param {Object} config - Loading configuration
     * @returns {string} Loading HTML
     */
    _getLoadingHTML(config) {
        const sizeClass = `loading-${config.type}-${config.size}`;

        switch (config.type) {
            case 'spinner':
                return `
                    <div class="loading-overlay" style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: rgba(255, 255, 255, 0.9);
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        z-index: 1000;
                    ">
                        <div class="loading-spinner ${sizeClass}"></div>
                        ${config.text ? `<p style="margin-top: 12px; color: #6b7280;">${config.text}</p>` : ''}
                    </div>
                `;

            case 'skeleton':
                return `
                    <div class="skeleton-container">
                        <div class="skeleton skeleton-title"></div>
                        <div class="skeleton skeleton-text"></div>
                        <div class="skeleton skeleton-text"></div>
                        <div class="skeleton skeleton-text" style="width: 80%;"></div>
                    </div>
                `;

            case 'dots':
                return `
                    <div class="loading-overlay" style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: rgba(255, 255, 255, 0.9);
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        z-index: 1000;
                    ">
                        <div class="loading-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        ${config.text ? `<p style="margin-top: 12px; color: #6b7280;">${config.text}</p>` : ''}
                    </div>
                `;

            case 'progress':
                return `
                    <div class="loading-overlay" style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: rgba(255, 255, 255, 0.9);
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        z-index: 1000;
                        padding: 20px;
                    ">
                        <div class="progress-bar" style="width: 100%; max-width: 400px;">
                            <div class="progress-bar-fill" style="width: 0%" id="${config.progressId || 'progress-bar'}"></div>
                        </div>
                        ${config.text ? `<p style="margin-top: 12px; color: #6b7280;">${config.text}</p>` : ''}
                    </div>
                `;

            default:
                return `<div class="loading-spinner"></div>`;
        }
    }

    /**
     * Update progress bar
     * @param {string} progressId - Progress bar ID
     * @param {number} percent - Percentage (0-100)
     */
    updateProgress(progressId, percent) {
        const progressBar = document.getElementById(progressId);
        if (progressBar) {
            progressBar.style.width = `${Math.min(100, Math.max(0, percent))}%`;
        }
    }
}

// Global loading manager instance
const loadingManager = new LoadingManager();

// ============================================================================
// Toast Notifications
// ============================================================================

class ToastManager {
    constructor() {
        this.container = null;
        this.toasts = [];
        this.maxToasts = 5;
        this._createContainer();
    }

    _createContainer() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 12px;
                max-width: 400px;
            `;
            document.body.appendChild(this.container);
        }
    }

    /**
     * Show toast notification
     * @param {string} message - Toast message
     * @param {Object} options - Toast options
     */
    show(message, options = {}) {
        const config = {
            type: options.type || 'info', // success, error, warning, info
            duration: options.duration || 3000,
            dismissible: options.dismissible !== false,
            ...options
        };

        // Remove oldest toast if at max capacity
        if (this.toasts.length >= this.maxToasts) {
            this.dismiss(this.toasts[0].id);
        }

        const toast = this._createToast(message, config);
        this.container.appendChild(toast.element);
        this.toasts.push(toast);

        // Auto-dismiss
        if (config.duration > 0) {
            toast.timeout = setTimeout(() => {
                this.dismiss(toast.id);
            }, config.duration);
        }

        return toast.id;
    }

    _createToast(message, config) {
        const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const element = document.createElement('div');

        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        element.className = 'alert-slide-in';
        element.style.cssText = `
            background: white;
            border-left: 4px solid ${colors[config.type]};
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: start;
            gap: 12px;
            min-width: 300px;
        `;

        element.innerHTML = `
            <div style="
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background: ${colors[config.type]};
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                flex-shrink: 0;
            ">${icons[config.type]}</div>
            <div style="flex: 1; color: #374151; font-size: 14px;">
                ${message}
            </div>
            ${config.dismissible ? `
                <button onclick="toastManager.dismiss('${id}')" style="
                    background: none;
                    border: none;
                    color: #9ca3af;
                    cursor: pointer;
                    font-size: 18px;
                    padding: 0;
                    line-height: 1;
                ">&times;</button>
            ` : ''}
        `;

        return {
            id,
            element,
            timeout: null
        };
    }

    /**
     * Dismiss toast
     * @param {string} toastId - Toast ID
     */
    dismiss(toastId) {
        const index = this.toasts.findIndex(t => t.id === toastId);
        if (index !== -1) {
            const toast = this.toasts[index];

            // Clear timeout
            if (toast.timeout) {
                clearTimeout(toast.timeout);
            }

            // Fade out animation
            toast.element.style.transition = 'opacity 0.3s, transform 0.3s';
            toast.element.style.opacity = '0';
            toast.element.style.transform = 'translateX(100%)';

            setTimeout(() => {
                if (toast.element.parentNode) {
                    toast.element.parentNode.removeChild(toast.element);
                }
            }, 300);

            this.toasts.splice(index, 1);
        }
    }

    success(message, duration) {
        return this.show(message, { type: 'success', duration });
    }

    error(message, duration) {
        return this.show(message, { type: 'error', duration: duration || 5000 });
    }

    warning(message, duration) {
        return this.show(message, { type: 'warning', duration });
    }

    info(message, duration) {
        return this.show(message, { type: 'info', duration });
    }
}

// Global toast manager instance
const toastManager = new ToastManager();

// ============================================================================
// Number Counter Animation
// ============================================================================

function animateNumber(element, start, end, duration = 1000, formatter = null) {
    const startTime = Date.now();
    const range = end - start;

    function update() {
        const now = Date.now();
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function (ease-out)
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (range * eased);

        element.textContent = formatter ? formatter(current) : Math.round(current);

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// ============================================================================
// Smooth Scroll with Animation
// ============================================================================

function smoothScrollTo(targetId, duration = 500) {
    const target = document.getElementById(targetId);
    if (!target) return;

    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function
        const eased = 1 - Math.pow(1 - progress, 3);

        window.scrollTo(0, startPosition + (distance * eased));

        if (progress < 1) {
            requestAnimationFrame(animation);
        }
    }

    requestAnimationFrame(animation);
}

// ============================================================================
// Fade Element In/Out
// ============================================================================

function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.display = 'block';

    let start = null;
    function step(timestamp) {
        if (!start) start = timestamp;
        const progress = Math.min((timestamp - start) / duration, 1);
        element.style.opacity = progress;

        if (progress < 1) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}

function fadeOut(element, duration = 300) {
    let start = null;
    function step(timestamp) {
        if (!start) start = timestamp;
        const progress = Math.min((timestamp - start) / duration, 1);
        element.style.opacity = 1 - progress;

        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            element.style.display = 'none';
        }
    }

    requestAnimationFrame(step);
}

// ============================================================================
// Lazy Loading for Images
// ============================================================================

function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('fade-in');
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// ============================================================================
// Debounce Function
// ============================================================================

function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================================================
// Throttle Function
// ============================================================================

function throttle(func, limit = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================================================
// Export to global scope
// ============================================================================

window.loadingManager = loadingManager;
window.toastManager = toastManager;
window.animateNumber = animateNumber;
window.smoothScrollTo = smoothScrollTo;
window.fadeIn = fadeIn;
window.fadeOut = fadeOut;
window.initLazyLoading = initLazyLoading;
window.debounce = debounce;
window.throttle = throttle;

// Auto-initialize lazy loading on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLazyLoading);
} else {
    initLazyLoading();
}
