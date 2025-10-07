// Dashboard Inicio - JavaScript interactivo

document.addEventListener('DOMContentLoaded', function() {
    // Mostrar fecha actual con formato mejorado
    const currentDateElement = document.getElementById('currentDate');
    if (currentDateElement) {
        const now = new Date();
        currentDateElement.textContent = now.toLocaleDateString('es-VE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
        });
    }

    // Debug: verificar datos disponibles
    console.log('Datos recibidos del backend:', {
        labels: typeof labels !== 'undefined' ? labels : 'undefined',
        dataEncuestas: typeof dataEncuestas !== 'undefined' ? dataEncuestas : 'undefined',
        dataEncuestados: typeof dataEncuestados !== 'undefined' ? dataEncuestados : 'undefined',
        dataFotografias: typeof dataFotografias !== 'undefined' ? dataFotografias : 'undefined',
        totalEncuestas: typeof totalEncuestas !== 'undefined' ? totalEncuestas : 'undefined',
        totalEncuestados: typeof totalEncuestados !== 'undefined' ? totalEncuestados : 'undefined',
        totalFotografias: typeof totalFotografias !== 'undefined' ? totalFotografias : 'undefined'
    });

    // Verificar que existan los datos y crear datos de ejemplo si es necesario
    if (typeof labels === 'undefined' || typeof dataEncuestas === 'undefined') {
        console.warn('Los datos del backend no están disponibles, usando datos de ejemplo');
        // Crear datos de ejemplo para las últimas 30 días
        const today = new Date();
        const exampleLabels = [];
        const exampleDataEncuestas = [];
        const exampleDataEncuestados = [];
        const exampleDataFotografias = [];
        
        for (let i = 29; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            exampleLabels.push(date.toISOString().split('T')[0]);
            // Datos de ejemplo con variación realista
            exampleDataEncuestas.push(Math.floor(Math.random() * 5) + 1);
            exampleDataEncuestados.push(Math.floor(Math.random() * 8) + 2);
            exampleDataFotografias.push(Math.floor(Math.random() * 3) + 1);
        }
        
        // Usar datos de ejemplo
        window.labels = exampleLabels;
        window.dataEncuestas = exampleDataEncuestas;
        window.dataEncuestados = exampleDataEncuestados;
        window.dataFotografias = exampleDataFotografias;
        window.totalEncuestas = exampleDataEncuestas.reduce((a, b) => a + b, 0);
        window.totalEncuestados = exampleDataEncuestados.reduce((a, b) => a + b, 0);
        window.totalFotografias = exampleDataFotografias.reduce((a, b) => a + b, 0);
    } else {
        // Usar datos reales del backend
        window.labels = labels;
        window.dataEncuestas = dataEncuestas;
        window.dataEncuestados = dataEncuestados;
        window.dataFotografias = dataFotografias;
        window.totalEncuestas = totalEncuestas;
        window.totalEncuestados = totalEncuestados;
        window.totalFotografias = totalFotografias;
    }

    // Configuración de colores consistentes con realizar_encuesta.html
    const colors = {
        encuestas: { 
            primary: '#667eea',
            secondary: '#764ba2',
            gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            rgba: 'rgba(102, 126, 234, 0.3)'
        },
        encuestados: { 
            primary: '#4facfe',
            secondary: '#00f2fe',
            gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            rgba: 'rgba(79, 172, 254, 0.3)'
        },
        fotografias: { 
            primary: '#fa709a',
            secondary: '#fee140',
            gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            rgba: 'rgba(250, 112, 154, 0.3)'
        }
    };

    // Animación de contadores
    function animateCounter(element, target) {
        const duration = 2000;
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    }

    // Inicializar contadores animados
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        if (target) {
            animateCounter(counter, target);
        }
    });

    // Inicializar Chart.js si está disponible
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    } else {
        console.warn('Chart.js no está disponible');
        showChartPlaceholders();
    }

    function initializeCharts() {
        console.log('Inicializando gráficas...');
        
        // 1. Gráfica de Tendencia Principal (Líneas)
        const trendCtx = document.getElementById('trendChart');
        if (trendCtx) {
            console.log('Creando gráfica de tendencia...');
            new Chart(trendCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Encuestas',
                            data: dataEncuestas,
                            borderColor: colors.encuestas.primary,
                            backgroundColor: colors.encuestas.rgba,
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            pointBackgroundColor: colors.encuestas.primary,
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        },
                        {
                            label: 'Encuestados',
                            data: dataEncuestados,
                            borderColor: colors.encuestados.primary,
                            backgroundColor: colors.encuestados.rgba,
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            pointBackgroundColor: colors.encuestados.primary,
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        },
                        {
                            label: 'Fotografías',
                            data: dataFotografias,
                            borderColor: colors.fotografias.primary,
                            backgroundColor: colors.fotografias.rgba,
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            pointBackgroundColor: colors.fotografias.primary,
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { 
                        mode: 'index', 
                        intersect: false 
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: { 
                                usePointStyle: true, 
                                padding: 20, 
                                font: { 
                                    size: 12, 
                                    weight: '600' 
                                } 
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            borderColor: 'rgba(255, 255, 255, 0.2)',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: { 
                            beginAtZero: true, 
                            grid: { 
                                color: 'rgba(0, 0, 0, 0.05)',
                                drawBorder: false
                            },
                            ticks: {
                                font: { size: 11 }
                            }
                        },
                        x: { 
                            grid: { 
                                display: false 
                            },
                            ticks: { 
                                maxRotation: 45, 
                                minRotation: 45, 
                                font: { size: 10 } 
                            }
                        }
                    }
                }
            });
            console.log('Gráfica de tendencia creada');
        } else {
            console.error('No se encontró el elemento trendChart');
        }

        // 2. Gráfica de Distribución (Dona)
        const distributionCtx = document.getElementById('distributionChart');
        if (distributionCtx) {
            console.log('Creando gráfica de distribución...');
            new Chart(distributionCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Encuestas', 'Encuestados', 'Fotografías'],
                    datasets: [{
                        data: [totalEncuestas || 0, totalEncuestados || 0, totalFotografias || 0],
                        backgroundColor: [
                            colors.encuestas.primary,
                            colors.encuestados.primary,
                            colors.fotografias.primary
                        ],
                        borderWidth: 0,
                        hoverOffset: 15
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            position: 'bottom', 
                            labels: { 
                                padding: 15, 
                                usePointStyle: true, 
                                font: { 
                                    size: 12, 
                                    weight: '600' 
                                } 
                            } 
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            callbacks: {
                                label: function(context) {
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                                    return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                                }
                            }
                        }
                    }
                }
            });
            console.log('Gráfica de distribución creada');
        } else {
            console.error('No se encontró el elemento distributionChart');
        }

        // 3. Gráfica de Barras - Encuestas (última semana)
        const encuestasBarCtx = document.getElementById('encuestasBarChart');
        if (encuestasBarCtx) {
            console.log('Creando gráfica de barras...');
            new Chart(encuestasBarCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: labels.slice(-7),
                    datasets: [{
                        label: 'Encuestas',
                        data: dataEncuestas.slice(-7),
                        backgroundColor: colors.encuestas.primary,
                        borderRadius: 8,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false }, 
                        tooltip: { 
                            backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                            padding: 10 
                        } 
                    },
                    scales: { 
                        y: { 
                            beginAtZero: true, 
                            grid: { 
                                color: 'rgba(0, 0, 0, 0.05)' 
                            } 
                        }, 
                        x: { 
                            grid: { 
                                display: false 
                            } 
                        } 
                    }
                }
            });
            console.log('Gráfica de barras creada');
        } else {
            console.error('No se encontró el elemento encuestasBarChart');
        }

        // 4. Gráfica de Área - Encuestados (última semana)
        const encuestadosAreaCtx = document.getElementById('encuestadosAreaChart');
        if (encuestadosAreaCtx) {
            console.log('Creando gráfica de área...');
            new Chart(encuestadosAreaCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: labels.slice(-7),
                    datasets: [{
                        label: 'Encuestados',
                        data: dataEncuestados.slice(-7),
                        backgroundColor: colors.encuestados.rgba,
                        borderColor: colors.encuestados.primary,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 5,
                        pointBackgroundColor: colors.encuestados.primary,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false }, 
                        tooltip: { 
                            backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                            padding: 10 
                        } 
                    },
                    scales: { 
                        y: { 
                            beginAtZero: true, 
                            grid: { 
                                color: 'rgba(0, 0, 0, 0.05)' 
                            } 
                        }, 
                        x: { 
                            grid: { 
                                display: false 
                            } 
                        } 
                    }
                }
            });
            console.log('Gráfica de área creada');
        } else {
            console.error('No se encontró el elemento encuestadosAreaChart');
        }
        
        console.log('Todas las gráficas inicializadas correctamente');
    }

    function showChartPlaceholders() {
        const chartContainers = document.querySelectorAll('.chart-container, .chart-container-large');
        chartContainers.forEach(container => {
            container.innerHTML = '<div class="chart-placeholder"><i class="bi bi-graph-up me-2"></i>Gráfica no disponible</div>';
        });
    }

    // Efectos de hover en las tarjetas
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Efectos de hover en las acciones rápidas
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    quickActionBtns.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Animación de las barras de progreso
    setTimeout(() => {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach((bar, index) => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, index * 200);
        });
    }, 1000);

    // Efectos de entrada escalonados
    const animatedElements = document.querySelectorAll('.stat-card, .chart-card, .quick-actions-card');
    animatedElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.1}s`;
    });

    console.log('Dashboard inicializado correctamente');
});
