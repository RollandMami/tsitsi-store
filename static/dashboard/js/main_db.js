window.dashboardData = {
    salesLabels: JSON.parse('{{ sales_labels_json|safe }}'),
    salesData: JSON.parse('{{ sales_data_json|safe }}'),
    ordersData: JSON.parse('{{ orders_data_json|safe }}'),
    topLabels: JSON.parse('{{ top_products_labels_json|safe }}'),
    topData: JSON.parse('{{ top_products_data_json|safe }}')
};

document.addEventListener('DOMContentLoaded', function() {
    const data = window.dashboardData;
    if (!data || !data.salesLabels) return;

    // Graphique Principal
    const salesCtx = document.getElementById('salesChart');
    if (salesCtx) {
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: data.salesLabels,
                datasets: [
                    {
                        label: 'Ventes (Ar)',
                        data: data.salesData,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        fill: true,
                        tension: 0.3,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Commandes',
                        data: data.ordersData,
                        borderColor: '#0dcaf9',
                        fill: false,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { type: 'linear', position: 'left', beginAtZero: true },
                    y1: { type: 'linear', position: 'right', beginAtZero: true, grid: { display: false } }
                }
            }
        });
    }

    // Top Produits
    const topCtx = document.getElementById('topProductsChart');
    if (topCtx) {
        new Chart(topCtx, {
            type: 'bar', // Tu peux aussi tester 'horizontalBar' ou changer l'indexAxis
            data: {
                labels: data.topLabels.map(label => label.length > 15 ? label.substring(0, 15) + '...' : label),
                datasets: [{
                    label: 'Unités',
                    data: data.topData,
                    backgroundColor: '#0d6efd',
                    borderRadius: 5
                }]
            },
            options: {
                indexAxis: 'y', // Transforme en barres horizontales pour mieux lire les noms
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            // Affiche le nom complet au survol de la souris
                            label: function(context) {
                                return data.topLabels[context.dataIndex] + ': ' + context.raw;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                         beginAtZero: true,
                         grid: { color: '#E9E4D9' }, // Grille assortie au beige
                         ticks: { color: '#8B8579' }
                    },
                    y: {
                        ticks: {
                            font: { size: 10, color: '#8B8579' } // Réduit un peu la police des noms
                        }
                    }
                }
            }
        });
    }
});