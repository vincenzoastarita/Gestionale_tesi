/**
 * Charts initialization and configuration for the Sales Order Management System
 */

/**
 * Create a bar chart for sales data
 * @param {string} elementId - The ID of the canvas element
 * @param {Array} data - The data array
 * @param {Array} labels - The labels array
 * @param {string} label - The dataset label
 */
function createSalesBarChart(elementId, data, labels, label = 'Monthly Sales') {
    const ctx = document.getElementById(elementId)?.getContext('2d');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: 'rgba(13, 110, 253, 0.5)',
                borderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '€' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Sales: €' + context.raw.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a pie chart for category distribution
 * @param {string} elementId - The ID of the canvas element
 * @param {Array} data - The data array
 * @param {Array} labels - The labels array
 */
function createCategoryPieChart(elementId, data, labels) {
    const ctx = document.getElementById(elementId)?.getContext('2d');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${percentage}% (€${value.toLocaleString()})`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a doughnut chart for order status distribution
 * @param {string} elementId - The ID of the canvas element
 * @param {Array} data - The data array
 * @param {Array} labels - The labels array
 */
function createStatusDoughnutChart(elementId, data, labels) {
    const ctx = document.getElementById(elementId)?.getContext('2d');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(255, 206, 86, 0.7)', // pending - yellow
                    'rgba(54, 162, 235, 0.7)', // confirmed - blue
                    'rgba(75, 192, 192, 0.7)', // shipped - teal
                    'rgba(40, 167, 69, 0.7)',  // delivered - green
                    'rgba(220, 53, 69, 0.7)'   // cancelled - red
                ],
                borderColor: [
                    'rgba(255, 206, 86, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(40, 167, 69, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${percentage}% (${value} orders)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a line chart for commission trends
 * @param {string} elementId - The ID of the canvas element
 * @param {Array} salesData - The sales data array
 * @param {Array} commissionData - The commission data array
 * @param {Array} labels - The labels array
 */
function createCommissionLineChart(elementId, salesData, commissionData, labels) {
    const ctx = document.getElementById(elementId)?.getContext('2d');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Sales',
                    data: salesData,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'Commission',
                    data: commissionData,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '€' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            return label + ': €' + context.raw.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update chart data
 * @param {Chart} chart - The Chart.js instance
 * @param {Array} data - The new data array
 * @param {Array} labels - The new labels array (optional)
 */
function updateChartData(chart, data, labels = null) {
    if (!chart) return;
    
    chart.data.datasets[0].data = data;
    if (labels) {
        chart.data.labels = labels;
    }
    
    chart.update();
}

/**
 * Generate random data for testing charts
 * @param {number} count - Number of data points to generate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {Array} Array of random numbers
 */
function generateRandomData(count, min, max) {
    return Array.from({ length: count }, () => 
        Math.floor(Math.random() * (max - min + 1)) + min
    );
}

/**
 * Initialize all charts on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Any additional chart initialization can be added here
    // Most charts are initialized in their respective template files
});
