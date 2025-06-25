/*
===========================================
AT&T INVENTORY SYSTEM - DASHBOARD JS
===========================================
Funcionalidades específicas del dashboard
===========================================
*/

// === CONFIGURACIÓN DEL DASHBOARD ===
const DashboardConfig = {
    formatMode: 'compact', // 'compact' o 'detailed'
    animationDelay: 100,
    refreshInterval: 300000, // 5 minutos
    localStorageKey: 'att_dashboard_format'
};

// === FORMATEO DE NÚMEROS ===
const DashboardFormatter = {
    // Formatear número según el modo actual
    formatNumber: (value, options = {}) => {
        if (!value && value !== 0) return '0';
        
        const config = {
            decimals: options.decimals || 0,
            currency: options.currency || null,
            compact: DashboardConfig.formatMode === 'compact',
            ...options
        };

        if (config.currency) {
            return DashboardFormatter.formatCurrency(value, config.currency, config.compact);
        }

        if (config.compact) {
            return ATTUtils.formatNumberCompact(value);
        } else {
            return ATTUtils.formatNumber(value, config.decimals);
        }
    },

    // Formatear moneda
    formatCurrency: (value, currency = 'MXN', compact = false) => {
        if (!value && value !== 0) return currency === 'USD' ? '$0.00' : '$0.00';
        
        if (compact) {
            return ATTUtils.formatCurrencyCompact(value, currency);
        } else {
            return ATTUtils.formatCurrency(value, currency);
        }
    },

    // Formatear porcentaje
    formatPercentage: (value, decimals = 1) => {
        if (!value && value !== 0) return '0%';
        return value.toFixed(decimals) + '%';
    }
};

// === GESTOR DE FORMATO ===
const FormatManager = {
    // Inicializar formato desde localStorage
    init: () => {
        const savedFormat = localStorage.getItem(DashboardConfig.localStorageKey);
        if (savedFormat) {
            DashboardConfig.formatMode = savedFormat;
        }
        FormatManager.updateFormatButton();
        FormatManager.updateAllNumbers();
    },

    // Alternar formato
    toggle: () => {
        DashboardConfig.formatMode = DashboardConfig.formatMode === 'compact' ? 'detailed' : 'compact';
        localStorage.setItem(DashboardConfig.localStorageKey, DashboardConfig.formatMode);
        
        FormatManager.updateFormatButton();
        FormatManager.updateAllNumbers();
        
        // Notificación
        const message = DashboardConfig.formatMode === 'compact' 
            ? 'Formato compacto activado' 
            : 'Formato detallado activado';
        ATTNotifications.show(message, 'info', 2000);
    },

    // Actualizar botón de formato
    updateFormatButton: () => {
        const button = document.getElementById('format-toggle');
        if (button) {
            const icon = button.querySelector('i');
            const isCompact = DashboardConfig.formatMode === 'compact';
            
            icon.className = isCompact ? 'fas fa-expand-alt' : 'fas fa-compress-alt';
            button.setAttribute('data-att-tooltip', 
                isCompact ? 'Cambiar a formato detallado' : 'Cambiar a formato compacto'
            );
        }
    },

    // Actualizar todos los números en la página
    updateAllNumbers: () => {
        // Elementos con formato de número
        document.querySelectorAll('[data-toggle-format]').forEach(element => {
            const fullValue = parseFloat(element.getAttribute('data-full'));
            const compactValue = element.getAttribute('data-compact');
            const currency = element.getAttribute('data-currency');
            const decimals = parseInt(element.getAttribute('data-decimals')) || 0;

            if (!isNaN(fullValue)) {
                let formattedValue;
                
                if (DashboardConfig.formatMode === 'compact') {
                    formattedValue = compactValue || DashboardFormatter.formatNumber(fullValue, {
                        currency: currency,
                        decimals: decimals
                    });
                } else {
                    formattedValue = DashboardFormatter.formatNumber(fullValue, {
                        currency: currency,
                        decimals: decimals,
                        compact: false
                    });
                }

                // Animar el cambio
                element.style.transition = 'all 0.3s ease';
                element.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    element.textContent = formattedValue;
                    element.style.transform = 'scale(1)';
                }, 150);
            }
        });
    }
};

// === ANIMACIONES DEL DASHBOARD ===
const DashboardAnimations = {
    // Animar entrada de elementos
    animateIn: () => {
        // Animar métricas principales
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * DashboardConfig.animationDelay);
        });

        // Animar secciones de análisis
        const analysisSections = document.querySelectorAll('.analysis-section');
        analysisSections.forEach((section, index) => {
            section.style.opacity = '0';
            section.style.transform = 'translateX(' + (index % 2 === 0 ? '-30px' : '30px') + ')';
            
            setTimeout(() => {
                section.style.transition = 'all 0.6s ease';
                section.style.opacity = '1';
                section.style.transform = 'translateX(0)';
            }, (metricCards.length * DashboardConfig.animationDelay) + (index * DashboardConfig.animationDelay));
        });
    },

    // Animar contador de números
    animateCounters: () => {
        document.querySelectorAll('.metric-value[data-animate-counter]').forEach(element => {
            const target = parseFloat(element.getAttribute('data-animate-counter'));
            const duration = 2000; // 2 segundos
            const start = performance.now();
            
            const animate = (currentTime) => {
                const elapsed = currentTime - start;
                const progress = Math.min(elapsed / duration, 1);
                
                // Easing function
                const easeOutQuart = 1 - Math.pow(1 - progress, 4);
                const current = target * easeOutQuart;
                
                element.textContent = DashboardFormatter.formatNumber(current);
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            };
            
            requestAnimationFrame(animate);
        });
    }
};

// === ACTUALIZACIÓN DE DATOS ===
const DashboardUpdater = {
    // Actualizar datos del dashboard
    refresh: async () => {
        try {
            // Mostrar indicador de carga
            const loader = ATTLoading.show(document.querySelector('.dashboard-content'), 'Actualizando datos...');
            
            // Simular llamada AJAX (reemplazar con llamada real)
            const response = await fetch(window.location.href, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                // Aquí se procesarían los nuevos datos
                ATTNotifications.show('Datos actualizados correctamente', 'success');
            } else {
                throw new Error('Error al actualizar datos');
            }
            
            ATTLoading.hide(loader);
        } catch (error) {
            console.error('Error al actualizar dashboard:', error);
            ATTNotifications.show('Error al actualizar los datos', 'error');
        }
    },

    // Configurar actualización automática
    setupAutoRefresh: () => {
        setInterval(() => {
            DashboardUpdater.refresh();
        }, DashboardConfig.refreshInterval);
    }
};

// === INTERACCIONES ===
const DashboardInteractions = {
    // Configurar tooltips avanzados
    setupTooltips: () => {
        document.querySelectorAll('[data-dashboard-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', function() {
                const content = this.getAttribute('data-dashboard-tooltip');
                const position = this.getAttribute('data-tooltip-position') || 'top';
                
                // Crear tooltip personalizado
                const tooltip = document.createElement('div');
                tooltip.className = 'dashboard-tooltip dashboard-tooltip-' + position;
                tooltip.innerHTML = content;
                tooltip.style.cssText = `
                    position: absolute;
                    background: rgba(0, 75, 135, 0.95);
                    color: white;
                    padding: 0.75rem 1rem;
                    border-radius: 8px;
                    font-size: 0.875rem;
                    z-index: 9999;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                    max-width: 300px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                `;
                
                document.body.appendChild(tooltip);
                
                // Posicionar tooltip
                const rect = this.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                
                let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                let top = rect.top - tooltipRect.height - 10;
                
                // Ajustar si se sale de la pantalla
                if (left < 10) left = 10;
                if (left + tooltipRect.width > window.innerWidth - 10) {
                    left = window.innerWidth - tooltipRect.width - 10;
                }
                
                tooltip.style.left = left + 'px';
                tooltip.style.top = top + 'px';
                
                // Mostrar
                setTimeout(() => {
                    tooltip.style.opacity = '1';
                }, 10);
                
                this._dashboardTooltip = tooltip;
            });

            element.addEventListener('mouseleave', function() {
                if (this._dashboardTooltip) {
                    this._dashboardTooltip.style.opacity = '0';
                    setTimeout(() => {
                        if (this._dashboardTooltip && this._dashboardTooltip.parentNode) {
                            this._dashboardTooltip.parentNode.removeChild(this._dashboardTooltip);
                        }
                        this._dashboardTooltip = null;
                    }, 300);
                }
            });
        });
    },

    // Configurar clicks en métricas
    setupMetricClicks: () => {
        document.querySelectorAll('.metric-card[data-click-action]').forEach(card => {
            card.style.cursor = 'pointer';
            card.addEventListener('click', function() {
                const action = this.getAttribute('data-click-action');
                const url = this.getAttribute('data-click-url');
                
                switch (action) {
                    case 'navigate':
                        if (url) window.location.href = url;
                        break;
                    case 'modal':
                        // Implementar modal si es necesario
                        break;
                    default:
                        console.log('Acción no definida:', action);
                }
            });
        });
    }
};

// === INICIALIZACIÓN ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Inicializando Dashboard AT&T...');
    
    // Inicializar componentes
    FormatManager.init();
    DashboardAnimations.animateIn();
    DashboardInteractions.setupTooltips();
    DashboardInteractions.setupMetricClicks();
    
    // Configurar botón de formato
    const formatButton = document.getElementById('format-toggle');
    if (formatButton) {
        formatButton.addEventListener('click', FormatManager.toggle);
    }
    
    // Configurar actualización automática (deshabilitado por defecto)
    // DashboardUpdater.setupAutoRefresh();
    
    // Animar contadores después de las animaciones de entrada
    setTimeout(() => {
        DashboardAnimations.animateCounters();
    }, 1000);
    
    console.log('✅ Dashboard AT&T inicializado correctamente');
});

// === EXPORTAR PARA USO GLOBAL ===
window.DashboardFormatter = DashboardFormatter;
window.FormatManager = FormatManager;
window.DashboardUpdater = DashboardUpdater; 