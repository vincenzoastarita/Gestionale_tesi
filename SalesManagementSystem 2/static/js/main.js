/**
 * Main JavaScript file for the Sales Order Management System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000);
    });
    
    // Add event listener for customer selection in new order form
    const customerSelect = document.getElementById('customer_id');
    if (customerSelect) {
        customerSelect.addEventListener('change', function() {
            const customerId = this.value;
            const priceListSection = document.getElementById('customer-price-list-section');
            
            if (customerId) {
                // Mostra la sezione del listino prezzi
                if (priceListSection) {
                    priceListSection.style.display = 'block';
                }
                
                // Carica il listino prezzi per questo cliente
                fetch(`/api/customers/${customerId}/price-list`)
                    .then(response => response.json())
                    .then(products => {
                        populateCustomerPriceList(products);
                    })
                    .catch(error => {
                        console.error('Error fetching price list:', error);
                        if (priceListSection) {
                            const tableBody = document.querySelector('#customer-products-table tbody');
                            if (tableBody) {
                                tableBody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Errore durante il caricamento del listino prezzi</td></tr>';
                            }
                        }
                    });
            } else {
                // Nascondi la sezione del listino prezzi se nessun cliente è selezionato
                if (priceListSection) {
                    priceListSection.style.display = 'none';
                }
            }
        });
    }
    
    // Filtra la tabella dei prodotti in base alla ricerca
    const productSearch = document.getElementById('product-search');
    if (productSearch) {
        productSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('#customer-products-table tbody tr');
            
            tableRows.forEach(row => {
                if (row.cells.length > 1) { // Verifica che la riga abbia celle (non è la riga di messaggio)
                    const productCode = row.cells[0].textContent.toLowerCase();
                    const productName = row.cells[1].textContent.toLowerCase();
                    const shouldShow = productCode.includes(searchTerm) || productName.includes(searchTerm);
                    row.style.display = shouldShow ? '' : 'none';
                }
            });
        });
    }
    
    // Add event listener for product price lookup
    const productSelects = document.querySelectorAll('select[id^="modal_product_id"]');
    productSelects.forEach(select => {
        select.addEventListener('change', function() {
            const productId = this.value;
            const customerId = document.getElementById('customer_id')?.value;
            
            if (productId && customerId) {
                // Fetch custom price for this customer and product
                fetch(`/api/customers/${customerId}/price/${productId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.price) {
                            const priceInput = document.getElementById('modal_price');
                            if (priceInput) {
                                priceInput.value = data.price;
                            }
                        }
                    })
                    .catch(error => console.error('Error fetching price:', error));
            }
        });
    });
    
    // Handle sidebar toggling on mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
        });
    }
    
    // Format number inputs as currency
    const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm="true"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Filter tables
    const tableFilters = document.querySelectorAll('.table-filter');
    tableFilters.forEach(filter => {
        filter.addEventListener('input', function() {
            const tableId = this.getAttribute('data-table');
            const table = document.getElementById(tableId);
            if (table) {
                const value = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.indexOf(value) > -1 ? '' : 'none';
                });
            }
        });
    });
});

/**
 * Popola la tabella del listino prezzi del cliente con i prodotti ricevuti dall'API
 * @param {Array} products - Array di prodotti con prezzo personalizzato
 */
function populateCustomerPriceList(products) {
    const tableBody = document.querySelector('#customer-products-table tbody');
    if (!tableBody) return;
    
    if (!products || products.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Nessun prodotto disponibile</td></tr>';
        return;
    }
    
    let html = '';
    products.forEach(product => {
        const hasCustomPrice = product.has_custom_price ? 'text-primary fw-bold' : '';
        
        html += `<tr>
            <td>${product.code}</td>
            <td>${product.name}</td>
            <td class="${hasCustomPrice}">${formatCurrency(product.price)}</td>
            <td>
                <input type="number" class="form-control form-control-sm product-quantity" 
                    data-product-id="${product.id}" 
                    data-product-name="${product.name}"
                    data-product-price="${product.price}" 
                    min="0" value="0" step="0.01">
            </td>
            <td>
                <button type="button" class="btn btn-sm btn-primary add-product-btn" 
                    data-product-id="${product.id}">
                    <i class="fas fa-plus"></i>
                </button>
            </td>
        </tr>`;
    });
    
    tableBody.innerHTML = html;
    
    // Aggiungi listener per i pulsanti di aggiunta
    const addButtons = tableBody.querySelectorAll('.add-product-btn');
    addButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const quantityInput = tableBody.querySelector(`input[data-product-id="${productId}"]`);
            
            if (quantityInput && parseFloat(quantityInput.value) > 0) {
                addProductToOrder(
                    productId,
                    quantityInput.getAttribute('data-product-name'),
                    parseFloat(quantityInput.value),
                    parseFloat(quantityInput.getAttribute('data-product-price')),
                    5 // Tasso di commissione di default (5%)
                );
                
                // Reset della quantità dopo l'aggiunta
                quantityInput.value = "0";
            } else {
                alert('Inserisci una quantità valida maggiore di zero.');
            }
        });
    });
}

/**
 * Aggiunge un prodotto all'ordine
 * @param {string} productId - ID del prodotto
 * @param {string} productName - Nome del prodotto
 * @param {number} quantity - Quantità
 * @param {number} price - Prezzo unitario
 * @param {number} commissionRate - Tasso di commissione (%)
 */
function addProductToOrder(productId, productName, quantity, price, commissionRate) {
    const orderItemsTable = document.querySelector('#orderItemsTable tbody');
    const itemCount = document.getElementById('item_count');
    
    if (!orderItemsTable || !itemCount) return;
    
    const index = parseInt(itemCount.value);
    const total = price * quantity;
    
    const newRow = document.createElement('tr');
    newRow.innerHTML = `
        <td>
            ${productName}
            <input type="hidden" name="product_id_${index}" value="${productId}">
        </td>
        <td>
            ${formatCurrency(price)}
            <input type="hidden" name="price_${index}" value="${price}">
        </td>
        <td>
            ${quantity}
            <input type="hidden" name="quantity_${index}" value="${quantity}">
        </td>
        <td>
            ${commissionRate}%
            <input type="hidden" name="commission_rate_${index}" value="${commissionRate}">
        </td>
        <td>${formatCurrency(total)}</td>
        <td>
            <button type="button" class="btn btn-sm btn-danger remove-item-btn">
                <i class="fas fa-trash"></i>
            </button>
        </td>
    `;
    
    // Aggiungi la riga alla tabella
    orderItemsTable.appendChild(newRow);
    
    // Incrementa il contatore degli elementi
    itemCount.value = (index + 1).toString();
    
    // Aggiorna il totale dell'ordine
    updateOrderTotal();
    
    // Aggiungi l'event listener per il pulsante di rimozione
    const removeButton = newRow.querySelector('.remove-item-btn');
    if (removeButton) {
        removeButton.addEventListener('click', function() {
            newRow.remove();
            updateOrderTotal();
        });
    }
}

/**
 * Aggiorna il totale dell'ordine
 */
function updateOrderTotal() {
    const orderItemsTable = document.getElementById('orderItemsTable');
    const orderTotalElement = document.getElementById('orderTotale');
    
    if (!orderItemsTable || !orderTotalElement) return;
    
    let total = 0;
    
    // Calcola il totale sommando tutti gli importi nella colonna del totale (quinta colonna)
    const rows = orderItemsTable.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 5) {
            const cellText = cells[4].textContent;
            // Rimuovi il simbolo di valuta e le virgole, poi converti in numero
            const itemTotal = parseFloat(cellText.replace(/[^\d,-]/g, '').replace(',', '.'));
            if (!isNaN(itemTotal)) {
                total += itemTotal;
            }
        }
    });
    
    // Aggiorna l'elemento del totale
    orderTotalElement.textContent = formatCurrency(total);
}

/**
 * Format a number as currency
 * @param {number} value - The value to format
 * @param {string} locale - The locale to use for formatting (default: en-US)
 * @param {string} currency - The currency code (default: EUR)
 * @returns {string} Formatted currency string
 */
function formatCurrency(value, locale = 'en-US', currency = 'EUR') {
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency
    }).format(value);
}

/**
 * Format a date as a string
 * @param {Date|string} date - The date to format
 * @param {string} locale - The locale to use for formatting (default: en-US)
 * @returns {string} Formatted date string
 */
function formatDate(date, locale = 'en-US') {
    if (typeof date === 'string') {
        date = new Date(date);
    }
    
    return new Intl.DateTimeFormat(locale, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(date);
}

/**
 * Calculate the total for an order
 * @param {Array} items - Array of order items with price and quantity
 * @returns {number} Total amount
 */
function calculateOrderTotal(items) {
    return items.reduce((total, item) => {
        return total + (item.price * item.quantity);
    }, 0);
}

/**
 * Toggle visibility of an element
 * @param {string} elementId - The ID of the element to toggle
 */
function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        if (element.style.display === 'none') {
            element.style.display = '';
        } else {
            element.style.display = 'none';
        }
    }
}
