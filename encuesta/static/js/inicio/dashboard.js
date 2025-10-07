// Dashboard Inicio - JavaScript para gráficas interactivas con Colores Vivos

document.addEventListener('DOMContentLoaded', function() {
    // Mostrar fecha actual
    const currentDateElement = document.getElementById('currentDate');
    if (currentDateElement) {
        currentDateElement.textContent = new Date().toLocaleDateString('es-VE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    // Verificar que existan los datos
    if (typeof labels === 'undefined' || typeof dataEncuestas === 'undefined') {
        console.error('Los datos del backend no están disponibles');
        return;
    }

        // Configuración de colores suaves (como en la imagen)
        const colors = {
            encuestas: { 
                gradient1: '#FFD966',  // Amarillo suave
                gradient2: '#FFC933',
                rgba: 'rgb(255, 217, 102)'
            },
            encuestados: { 
                gradient1: '#81C784',  // Verde suave
                gradient2: '#66BB6A',
                rgba: 'rgb(129, 199, 132)'
            },
            comunidades: { 
                gradient1: '#64B5F6',  // Azul suave
                gradient2: '#42A5F5',
                rgba: 'rgb(100, 180, 246)'
            },
            rojo: {
                gradient1: '#E57373',  // Rojo suave
                gradient2: '#EF5350',
                rgba: 'rgba(229, 115, 115, 0.3)'
            }
        }

    // 1. Gráfica de Tendencia (Líneas) - Principal
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        new Chart(trendCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Encuestas',
                        data: dataEncuestas,
                        borderColor: colors.encuestas.gradient1,
                        backgroundColor: colors.encuestas.rgba,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: colors.encuestas.gradient1,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    },
                    {
                        label: 'Encuestados',
                        data: dataEncuestados,
                        borderColor: colors.encuestados.gradient1,
                        backgroundColor: colors.encuestados.rgba,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: colors.encuestados.gradient1,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    },
                    {
                        label: 'Comunidades',
                        data: dataComunidades,
                        borderColor: colors.comunidades.gradient1,
                        backgroundColor: colors.comunidades.rgba,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        pointBackgroundColor: colors.comunidades.gradient1,
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
    }

    // 2. Gráfica de Distribución (Dona)
    const distributionCtx = document.getElementById('distributionChart');
    if (distributionCtx && typeof totalEncuestas !== 'undefined') {
        new Chart(distributionCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Encuestas', 'Encuestados', 'Comunidades'],
                datasets: [{
                    data: [totalEncuestas, totalEncuestados, totalComunidades],
                    backgroundColor: [
                        colors.encuestas.gradient1,
                        colors.encuestados.gradient1,
                        colors.comunidades.gradient1
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
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        });
    }

    // 3. Gráfica de Barras - Encuestas (última semana)
    const encuestasBarCtx = document.getElementById('encuestasBarChart');
    if (encuestasBarCtx) {
        new Chart(encuestasBarCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels.slice(-7),
                datasets: [{
                    label: 'Encuestas',
                    data: dataEncuestas.slice(-7),
                    backgroundColor: colors.encuestas.gradient1,
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
    }

    // 4. Gráfica de Área - Encuestados (última semana) - Con rojo vivo
    const encuestadosAreaCtx = document.getElementById('encuestadosAreaChart');
    if (encuestadosAreaCtx) {
        new Chart(encuestadosAreaCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels.slice(-7),
                datasets: [{
                    label: 'Encuestados',
                    data: dataEncuestados.slice(-7),
                    backgroundColor: colors.rojo.rgba,
                    borderColor: colors.rojo.gradient1,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointBackgroundColor: colors.rojo.gradient1,
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
    }

    // 5. Gráfica Polar - Comunidades (última semana) - Colores vivos variados
    const comunidadesPolarCtx = document.getElementById('comunidadesPolarChart');
    if (comunidadesPolarCtx) {
        new Chart(comunidadesPolarCtx.getContext('2d'), {
            type: 'polarArea',
            data: {
                labels: labels.slice(-7),
                datasets: [{
                    data: dataComunidades.slice(-7),
                     backgroundColor: [
                        'rgba(100, 180, 246, 0.93)',  // Azul suave
                        'rgba(245, 234, 81)',  // Amarillo suave
                        'rgba(109, 228, 115, 0.94)',  // Verde suave
                        'rgba(229, 115, 115, 0.8)',  // Rojo suave
                        'rgba(100, 180, 246, 0.93)',  // Azul suave claro
                        'rgb(245, 234, 81)',  // Amarillo suave claro
                        'rgba(109, 228, 115, 0.94)'   // Verde suave claro
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        position: 'bottom', 
                        labels: { 
                            padding: 10, 
                            font: { size: 10 } 
                        } 
                    },
                    tooltip: { 
                        backgroundColor: 'rgba(0, 0, 0, 0.8)', 
                        padding: 10 
                    }
                },
                scales: { 
                    r: { 
                        beginAtZero: true, 
                        grid: { 
                            color: 'rgba(0, 0, 0, 0.05)' 
                        } 
                    } 
                }
            }
        });
    }
});