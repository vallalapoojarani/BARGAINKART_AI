// BargainKart Chart.js Visualizations Controller

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize User Analytics Dashboard Charts
    if (document.getElementById('monthlySpendingChart')) {
        initUserAnalyticsCharts();
    }

    // 2. Initialize Admin Dashboard Charts
    if (document.getElementById('userGrowthChart')) {
        initAdminCharts();
    }
});

// Default Chart.js Dark Theme Options
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(148, 163, 184, 0.12)';
Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

async function initUserAnalyticsCharts() {
    try {
        const res = await fetch('/api/dashboard/stats');
        const stats = await res.json();

        // 1. Monthly Spending (Area Line)
        new Chart(document.getElementById('monthlySpendingChart'), {
            type: 'line',
            data: {
                labels: stats.monthly_spending.labels,
                datasets: [{
                    label: 'Monthly Spend (₹)',
                    data: stats.monthly_spending.spending,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.15)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#6366f1',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { ticks: { callback: v => '₹' + (v / 1000) + 'k' } }
                }
            }
        });

        // 2. Monthly Savings (Bar)
        new Chart(document.getElementById('monthlySavingsChart'), {
            type: 'bar',
            data: {
                labels: stats.monthly_savings.labels,
                datasets: [{
                    label: 'Unlocked Savings (₹)',
                    data: stats.monthly_savings.savings,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { ticks: { callback: v => '₹' + (v / 1000) + 'k' } }
                }
            }
        });

        // 3. Price Comparison (Multi-bar)
        new Chart(document.getElementById('priceComparisonChart'), {
            type: 'bar',
            data: {
                labels: stats.price_comparison.labels,
                datasets: [
                    {
                        label: 'Listed Price',
                        data: stats.price_comparison.current,
                        backgroundColor: '#64748b',
                        borderRadius: 4
                    },
                    {
                        label: 'Lowest Verified Price',
                        data: stats.price_comparison.lowest,
                        backgroundColor: '#06b6d4',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { ticks: { callback: v => '₹' + (v / 1000) + 'k' } }
                }
            }
        });

        // 4. Authenticity Distribution (Doughnut)
        new Chart(document.getElementById('authenticityDistChart'), {
            type: 'doughnut',
            data: {
                labels: stats.authenticity_dist.labels,
                datasets: [{
                    data: stats.authenticity_dist.data,
                    backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                cutout: '70%'
            }
        });

        // 5. Negotiation Success (Doughnut)
        new Chart(document.getElementById('negotiationSuccessChart'), {
            type: 'doughnut',
            data: {
                labels: stats.negotiation_success.labels,
                datasets: [{
                    data: stats.negotiation_success.data,
                    backgroundColor: ['#8b5cf6', '#06b6d4', '#64748b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } },
                cutout: '65%'
            }
        });

        // 6. Category Spending (Polar Area)
        new Chart(document.getElementById('categorySpendingChart'), {
            type: 'polarArea',
            data: {
                labels: stats.category_spending.labels,
                datasets: [{
                    data: stats.category_spending.data,
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.7)',
                        'rgba(6, 182, 212, 0.7)',
                        'rgba(168, 85, 247, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(245, 158, 11, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'right' } }
            }
        });

        // 7. Order Status (Horizontal Bar)
        new Chart(document.getElementById('orderStatusChart'), {
            type: 'bar',
            data: {
                labels: stats.order_status.labels,
                datasets: [{
                    label: 'Orders',
                    data: stats.order_status.data,
                    backgroundColor: '#6366f1',
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });

        // 8. Price History Trend (Line)
        new Chart(document.getElementById('priceHistoryChart'), {
            type: 'line',
            data: {
                labels: stats.price_history.labels,
                datasets: [{
                    label: 'Flagship Price Trajectory (₹)',
                    data: stats.price_history.data,
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#a855f7'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { ticks: { callback: v => '₹' + (v / 1000) + 'k' } }
                }
            }
        });

    } catch (e) {
        console.error('Error rendering analytics charts:', e);
    }
}

async function initAdminCharts() {
    try {
        const res = await fetch('/api/admin/metrics');
        const m = await res.json();

        // 1. User Growth
        new Chart(document.getElementById('userGrowthChart'), {
            type: 'line',
            data: {
                labels: m.user_growth.labels,
                datasets: [{
                    label: 'Active Users',
                    data: m.user_growth.data,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        // 2. Orders Volume
        new Chart(document.getElementById('adminOrdersChart'), {
            type: 'bar',
            data: {
                labels: m.orders_volume.labels,
                datasets: [{
                    label: 'Order Volume',
                    data: m.orders_volume.data,
                    backgroundColor: '#10b981',
                    borderRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        // 3. Platform Revenue
        new Chart(document.getElementById('adminRevenueChart'), {
            type: 'line',
            data: {
                labels: m.revenue_trend.labels,
                datasets: [{
                    label: 'GMV Revenue (₹)',
                    data: m.revenue_trend.data,
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        // 4. Negotiation Distribution
        new Chart(document.getElementById('adminNegChart'), {
            type: 'doughnut',
            data: {
                labels: m.negotiation_distribution.labels,
                datasets: [{
                    data: m.negotiation_distribution.data,
                    backgroundColor: ['#10b981', '#6366f1', '#f43f5e'],
                    borderWidth: 0
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '65%' }
        });

        // 5. Authenticity Risk
        new Chart(document.getElementById('adminRiskChart'), {
            type: 'doughnut',
            data: {
                labels: m.authenticity_risk.labels,
                datasets: [{
                    data: m.authenticity_risk.data,
                    backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
                    borderWidth: 0
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '65%' }
        });

        // 6. Price Trends
        new Chart(document.getElementById('adminPriceTrendChart'), {
            type: 'line',
            data: {
                labels: m.price_trends.labels,
                datasets: [{
                    label: 'Average Price Index',
                    data: m.price_trends.data,
                    borderColor: '#f59e0b',
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

    } catch (e) {
        console.error('Error rendering admin charts:', e);
    }
}
