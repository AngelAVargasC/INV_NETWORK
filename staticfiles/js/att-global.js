/*
===========================================
AT&T INVENTORY SYSTEM - GLOBAL JAVASCRIPT
===========================================
Funciones globales y utilidades del sistema
===========================================
*/

// === CONFIGURACIÓN GLOBAL ===
const ATT_CONFIG = {
    animation: {
        duration: 300,
        easing: 'ease-in-out'
    },
    breakpoints: {
        mobile: 480,
        tablet: 768,
        desktop: 1024
    }
};

// === UTILIDADES GENERALES ===
const ATTUtils = {
    // Formatear números
    formatNumber: (num, decimals = 0) => {
        if (num === null || num === undefined) return '0';
        return new Intl.NumberFormat('es-MX', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    },

    // Formatear moneda
    formatCurrency: (amount, currency = 'MXN') => {
        if (amount === null || amount === undefined) return '$0.00';
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: currency === 'USD' ? 'USD' : 'MXN',
            minimumFractionDigits: 2
        }).format(amount);
    },

    // Formatear números grandes (compacto)
    formatNumberCompact: (num) => {
        if (num === null || num === undefined) return '0';
        
        const absNum = Math.abs(num);
        if (absNum >= 1e9) {
            return (num / 1e9).toFixed(1) + 'B';
        } else if (absNum >= 1e6) {
            return (num / 1e6).toFixed(1) + 'M';
        } else if (absNum >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return num.toString();
    },

    // Formatear moneda compacta
    formatCurrencyCompact: (amount, currency = 'MXN') => {
        if (amount === null || amount === undefined) return '$0';
        
        const symbol = currency === 'USD' ? '$' : '$';
        const absAmount = Math.abs(amount);
        
        if (absAmount >= 1e9) {
            return symbol + (amount / 1e9).toFixed(1) + 'B';
        } else if (absAmount >= 1e6) {
            return symbol + (amount / 1e6).toFixed(1) + 'M';
        } else if (absAmount >= 1e3) {
            return symbol + (amount / 1e3).toFixed(1) + 'K';
        }
        return symbol + amount.toFixed(0);
    },

    // Detectar dispositivo móvil
    isMobile: () => {
        return window.innerWidth <= ATT_CONFIG.breakpoints.mobile;
    },

    // Detectar tablet
    isTablet: () => {
        return window.innerWidth > ATT_CONFIG.breakpoints.mobile && 
               window.innerWidth <= ATT_CONFIG.breakpoints.tablet;
    },

    // Animar elemento
    animate: (element, properties, duration = ATT_CONFIG.animation.duration) => {
        return new Promise((resolve) => {
            if (!element) {
                resolve();
                return;
            }

            const keyframes = [];
            const initialStyles = window.getComputedStyle(element);
            
            // Crear keyframes iniciales
            const initialKeyframe = {};
            Object.keys(properties).forEach(prop => {
                initialKeyframe[prop] = initialStyles[prop] || properties[prop];
            });
            keyframes.push(initialKeyframe);
            keyframes.push(properties);

            const animation = element.animate(keyframes, {
                duration: duration,
                easing: ATT_CONFIG.animation.easing,
                fill: 'forwards'
            });

            animation.onfinish = () => resolve();
        });
    },

    // Debounce para optimizar eventos
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle para optimizar eventos
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// === NOTIFICACIONES ===
const ATTNotifications = {
    show: (message, type = 'info', duration = 5000) => {
        const notification = document.createElement('div');
        notification.className = `att-notification att-notification-${type}`;
        notification.innerHTML = `
            <div class="att-notification-content">
                <i class="fas fa-${ATTNotifications.getIcon(type)}"></i>
                <span>${message}</span>
                <button class="att-notification-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Agregar estilos
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 400px;
            color: white;
        `;

        // Colores según tipo
        const colors = {
            success: 'background: linear-gradient(135deg, #10b981, #34d399);',
            error: 'background: linear-gradient(135deg, #ef4444, #f87171);',
            warning: 'background: linear-gradient(135deg, #f59e0b, #fbbf24);',
            info: 'background: linear-gradient(135deg, #3b82f6, #60a5fa);'
        };
        notification.style.cssText += colors[type] || colors.info;

        document.body.appendChild(notification);

        // Animar entrada
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto-cerrar
        const autoClose = setTimeout(() => {
            ATTNotifications.hide(notification);
        }, duration);

        // Cerrar manual
        const closeBtn = notification.querySelector('.att-notification-close');
        closeBtn.addEventListener('click', () => {
            clearTimeout(autoClose);
            ATTNotifications.hide(notification);
        });

        return notification;
    },

    hide: (notification) => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    },

    getIcon: (type) => {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
};

// === LOADING ===
const ATTLoading = {
    show: (target = document.body, message = 'Cargando...') => {
        const loader = document.createElement('div');
        loader.className = 'att-loading-overlay';
        loader.innerHTML = `
            <div class="att-loading-content">
                <div class="att-loading-spinner"></div>
                <div class="att-loading-text">${message}</div>
            </div>
        `;

        // Estilos del loader
        loader.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            border-radius: inherit;
        `;

        // Asegurar posición relativa en el target
        if (target !== document.body) {
            target.style.position = 'relative';
        }

        target.appendChild(loader);
        return loader;
    },

    hide: (loader) => {
        if (loader && loader.parentNode) {
            loader.style.opacity = '0';
            setTimeout(() => {
                if (loader.parentNode) {
                    loader.parentNode.removeChild(loader);
                }
            }, 300);
        }
    }
};

// === INICIALIZACIÓN ===
document.addEventListener('DOMContentLoaded', function() {
    // Agregar estilos dinámicos
    const style = document.createElement('style');
    style.textContent = `
        .att-notification-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .att-notification-close {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 0.25rem;
            margin-left: auto;
        }
        
        .att-loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(0, 168, 204, 0.3);
            border-top: 4px solid #00A8CC;
            border-radius: 50%;
            animation: att-spin 1s linear infinite;
        }
        
        .att-loading-content {
            text-align: center;
            color: #004B87;
        }
        
        .att-loading-text {
            margin-top: 1rem;
            font-weight: 600;
        }
        
        @keyframes att-spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    // Inicializar tooltips básicos
    document.querySelectorAll('[data-att-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'att-tooltip';
            tooltip.textContent = this.getAttribute('data-att-tooltip');
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                z-index: 9999;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            
            document.body.appendChild(tooltip);
            
            // Posicionar tooltip
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
            
            // Mostrar
            setTimeout(() => {
                tooltip.style.opacity = '1';
            }, 10);
            
            // Guardar referencia
            this._tooltip = tooltip;
        });

        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.style.opacity = '0';
                setTimeout(() => {
                    if (this._tooltip && this._tooltip.parentNode) {
                        this._tooltip.parentNode.removeChild(this._tooltip);
                    }
                    this._tooltip = null;
                }, 300);
            }
        });
    });

    console.log('🎯 AT&T Inventory System - Frontend Inicializado');
});

// === EXPORTAR PARA USO GLOBAL ===
window.ATTUtils = ATTUtils;
window.ATTNotifications = ATTNotifications;
window.ATTLoading = ATTLoading; 