document.addEventListener('DOMContentLoaded', function() {
    const chartContainer = document.getElementById('chartData');
    if (!chartContainer) return;

    // Récupération des données depuis le DOM
    const salesLabels = JSON.parse(chartContainer.dataset.salesLabels);
    const salesData = JSON.parse(chartContainer.dataset.salesData);
    const ordersData = JSON.parse(chartContainer.dataset.ordersData);
    const topLabels = JSON.parse(chartContainer.dataset.topLabels);
    const topQuantities = JSON.parse(chartContainer.dataset.topData);

    // Graphique Tendances
    new Chart(document.getElementById('salesChart'), {
        type: 'line',
        data: {
            labels: salesLabels,
            datasets: [
                { label: 'Ventes (Ar)', data: salesData, borderColor: '#198754', tension: 0.3, yAxisID: 'y' },
                { label: 'Commandes', data: ordersData, borderColor: '#0dcaf0', tension: 0.3, yAxisID: 'y1' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { type: 'linear', position: 'left' },
                y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false } }
            }
        }
    });

    // Graphique Top Produits
    new Chart(document.getElementById('topProductsChart'), {
        type: 'bar',
        data: {
            labels: topLabels,
            datasets: [{
                data: topQuantities,
                backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
});

    // Toast helper (Bootstrap 5) - creates container if missing and shows a toast
    function ensureToastContainer() {
        let wrapper = document.getElementById('ts-toast-wrapper');
        if (!wrapper) {
            wrapper = document.createElement('div');
            wrapper.id = 'ts-toast-wrapper';
            wrapper.className = 'position-fixed top-0 end-0 p-3';
            wrapper.style.zIndex = 1080;
            const inner = document.createElement('div');
            inner.id = 'ts-toast-container';
            wrapper.appendChild(inner);
            document.body.appendChild(wrapper);
        }
        // Make visible when created or if hidden
        wrapper.style.display = 'block';
        return document.getElementById('ts-toast-container');
    }

    function showToast(message, title = '', type = 'info', autohide = true, delay = 5000) {
        const container = ensureToastContainer();
        const toast = document.createElement('div');
        let bgClass = 'bg-primary text-white';
        if (type === 'success') bgClass = 'bg-success text-white';
        if (type === 'danger') bgClass = 'bg-danger text-white';
        if (type === 'warning') bgClass = 'bg-warning text-dark';

        toast.className = 'toast align-items-center ' + bgClass + ' border-0';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        const inner = document.createElement('div');
        inner.className = 'd-flex';

        const body = document.createElement('div');
        body.className = 'toast-body';
        if (title) {
            const strong = document.createElement('strong');
            strong.className = 'me-2';
            strong.textContent = title + ':';
            body.appendChild(strong);
        }
        body.appendChild(document.createTextNode(' ' + message));

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-close btn-close-white me-2 m-auto';
        btn.setAttribute('data-bs-dismiss', 'toast');
        btn.setAttribute('aria-label', 'Close');

        inner.appendChild(body);
        inner.appendChild(btn);
        toast.appendChild(inner);

        container.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { autohide: autohide, delay: delay });
        bsToast.show();
        toast.addEventListener('hidden.bs.toast', function () { toast.remove(); });
        return bsToast;
    }