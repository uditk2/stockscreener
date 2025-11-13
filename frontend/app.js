// ===================================
// Configuration
// ===================================
const API_BASE = window.location.origin + '/api/v1';
const POLL_INTERVAL = 3000; // 3 seconds

// ===================================
// State Management
// ===================================
const state = {
    isScreening: false,
    totalStocks: 0,
    screeningPollInterval: null
};

// ===================================
// DOM Elements
// ===================================
const elements = {
    // Status
    healthStatus: document.getElementById('healthStatus'),

    // Initialize
    initializeBtn: document.getElementById('initializeBtn'),
    viewStocksBtn: document.getElementById('viewStocksBtn'),
    totalStocks: document.getElementById('totalStocks'),
    initializeLoading: document.getElementById('initializeLoading'),
    initializeCard: document.getElementById('initializeCard'),

    // Screening
    screenBtn: document.getElementById('screenBtn'),
    concurrency: document.getElementById('concurrency'),
    processedCount: document.getElementById('processedCount'),
    breakoutCount: document.getElementById('breakoutCount'),
    errorCount: document.getElementById('errorCount'),
    screenLoading: document.getElementById('screenLoading'),
    screenProgress: document.getElementById('screenProgress'),
    progressText: document.getElementById('progressText'),
    screenCard: document.getElementById('screenCard'),

    // Radar
    refreshRadarBtn: document.getElementById('refreshRadarBtn'),
    radarCount: document.getElementById('radarCount'),
    radarList: document.getElementById('radarList'),
    radarCard: document.getElementById('radarCard'),

    // Modal
    stockListModal: document.getElementById('stockListModal'),
    closeModal: document.getElementById('closeModal'),
    stockListContent: document.getElementById('stockListContent'),

    // Toast
    toastContainer: document.getElementById('toastContainer')
};

// ===================================
// API Functions
// ===================================
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function checkHealth() {
    try {
        const data = await apiCall('/health');
        updateHealthStatus(true, data);
        return data;
    } catch (error) {
        updateHealthStatus(false);
        return null;
    }
}

async function initializeStocks(useFallback = false) {
    return await apiCall('/stocks/initialize', {
        method: 'POST',
        body: JSON.stringify({ use_fallback: useFallback })
    });
}

async function getStockList() {
    return await apiCall('/stocks/list');
}

async function startScreening(maxConcurrent = 5) {
    return await apiCall('/screen/all/sync', {
        method: 'POST',
        body: JSON.stringify({ max_concurrent: maxConcurrent })
    });
}

async function getRadarStocks() {
    return await apiCall('/radar');
}

// ===================================
// UI Update Functions
// ===================================
function updateHealthStatus(healthy, data = null) {
    const statusBadge = elements.healthStatus;
    const statusText = statusBadge.querySelector('.status-text');

    if (healthy) {
        statusBadge.classList.add('healthy');
        statusBadge.classList.remove('error');
        statusText.textContent = 'System Healthy';

        if (data && data.stock_count !== undefined) {
            state.totalStocks = data.stock_count;
            elements.totalStocks.textContent = data.stock_count;
        }
    } else {
        statusBadge.classList.add('error');
        statusBadge.classList.remove('healthy');
        statusText.textContent = 'System Error';
    }
}

function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function setLoading(element, isLoading) {
    if (isLoading) {
        element.classList.add('active');
    } else {
        element.classList.remove('active');
    }
}

function setButtonLoading(button, isLoading, originalText) {
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round">
                    <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
                </path>
            </svg>
            Loading...
        `;
    } else {
        button.disabled = false;
        button.innerHTML = originalText || button.dataset.originalText || 'Done';
    }
}

function updateScreeningProgress(results) {
    const { total, processed, breakouts, errors } = results;

    // Update stats
    elements.processedCount.textContent = processed || 0;
    elements.breakoutCount.textContent = breakouts || 0;
    elements.errorCount.textContent = errors || 0;

    // Update progress bar
    if (total && total > 0) {
        const percentage = Math.round((processed / total) * 100);
        elements.screenProgress.style.width = `${percentage}%`;
        elements.progressText.textContent = `${percentage}%`;
    }
}

function renderRadarStocks(stocks) {
    const radarList = elements.radarList;
    elements.radarCount.textContent = stocks.length;

    if (stocks.length === 0) {
        radarList.innerHTML = `
            <div class="empty-state">
                <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 6v6l4 2"/>
                </svg>
                <p>No stocks on radar yet</p>
                <p class="empty-hint">Start screening to detect breakout signals</p>
            </div>
        `;
        return;
    }

    radarList.innerHTML = stocks.map(stock => {
        const analysis = stock.breakout_analysis || {};
        const confidence = Math.round((analysis.confidence || 0) * 100);
        const confidenceClass = confidence >= 75 ? '' : 'medium';
        const signals = analysis.signals || [];

        return `
            <div class="radar-item">
                <div class="radar-header">
                    <span class="radar-symbol">${stock.symbol}</span>
                    <span class="confidence-badge ${confidenceClass}">${confidence}% confident</span>
                </div>
                <div class="radar-details">
                    <div class="radar-price">
                        Last Price: ₹${stock.last_price?.toFixed(2) || 'N/A'}
                        ${stock.added_at ? `• Added: ${new Date(stock.added_at).toLocaleString()}` : ''}
                    </div>
                    ${signals.length > 0 ? `
                        <div class="radar-signals">
                            ${signals.slice(0, 3).map(signal => `
                                <span class="signal-tag">${signal}</span>
                            `).join('')}
                            ${signals.length > 3 ? `<span class="signal-tag">+${signals.length - 3} more</span>` : ''}
                        </div>
                    ` : ''}
                    ${analysis.reasoning ? `
                        <div class="radar-reasoning">${analysis.reasoning}</div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function renderStockList(stocks) {
    const content = elements.stockListContent;

    if (stocks.length === 0) {
        content.innerHTML = '<p class="empty-state">No stocks initialized</p>';
        return;
    }

    content.innerHTML = `
        <div class="stock-grid">
            ${stocks.map(stock => `
                <div class="stock-chip">${stock.name || stock.symbol}</div>
            `).join('')}
        </div>
    `;
}

// ===================================
// Event Handlers
// ===================================
async function handleInitialize() {
    const button = elements.initializeBtn;
    const originalHTML = button.innerHTML;

    try {
        setButtonLoading(button, true);
        setLoading(elements.initializeLoading, true);
        elements.initializeCard.classList.add('active');

        showToast('Fetching stocks from NSE...', 'info');

        const data = await initializeStocks(false);

        elements.totalStocks.textContent = data.count || 0;
        state.totalStocks = data.count || 0;

        elements.initializeCard.classList.remove('active');
        elements.initializeCard.classList.add('completed');

        showToast(`Successfully initialized ${data.count} stocks!`, 'success');

        // Auto-refresh health
        await checkHealth();

    } catch (error) {
        showToast(`Error: ${error.message}`, 'error', 5000);
        elements.initializeCard.classList.remove('active');
    } finally {
        setButtonLoading(button, false, originalHTML);
        setLoading(elements.initializeLoading, false);
    }
}

async function handleViewStocks() {
    const modal = elements.stockListModal;
    const content = elements.stockListContent;

    modal.classList.add('active');
    content.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const data = await getStockList();
        renderStockList(data.stocks || []);
    } catch (error) {
        content.innerHTML = `<p class="empty-state">Error loading stocks: ${error.message}</p>`;
    }
}

async function handleStartScreening() {
    if (state.isScreening) {
        showToast('Screening already in progress', 'warning');
        return;
    }

    if (state.totalStocks === 0) {
        showToast('Please initialize stocks first', 'warning');
        return;
    }

    const button = elements.screenBtn;
    const originalHTML = button.innerHTML;
    const maxConcurrent = parseInt(elements.concurrency.value) || 5;

    try {
        state.isScreening = true;
        setButtonLoading(button, true);
        setLoading(elements.screenLoading, true);
        elements.screenCard.classList.add('active');
        elements.screenLoading.classList.remove('indeterminate');

        // Reset progress
        elements.screenProgress.style.width = '0%';
        elements.progressText.textContent = '0%';

        showToast('Starting stock screening...', 'info');

        const data = await startScreening(maxConcurrent);

        // Update final results
        updateScreeningProgress(data.results);

        elements.screenCard.classList.remove('active');
        elements.screenCard.classList.add('completed');

        showToast(
            `Screening complete! Found ${data.results.breakouts} breakouts out of ${data.results.processed} stocks`,
            'success',
            5000
        );

        // Auto-refresh radar
        await handleRefreshRadar();

    } catch (error) {
        showToast(`Error: ${error.message}`, 'error', 5000);
        elements.screenCard.classList.remove('active');
    } finally {
        state.isScreening = false;
        setButtonLoading(button, false, originalHTML);
        setLoading(elements.screenLoading, false);
    }
}

async function handleRefreshRadar() {
    const button = elements.refreshRadarBtn;
    const originalHTML = button.innerHTML;

    try {
        setButtonLoading(button, true);

        const data = await getRadarStocks();

        renderRadarStocks(data.stocks || []);

        if (data.count > 0) {
            elements.radarCard.classList.add('completed');
        }

    } catch (error) {
        showToast(`Error loading radar: ${error.message}`, 'error');
    } finally {
        setButtonLoading(button, false, originalHTML);
    }
}

function handleCloseModal() {
    elements.stockListModal.classList.remove('active');
}

// ===================================
// Event Listeners
// ===================================
elements.initializeBtn.addEventListener('click', handleInitialize);
elements.viewStocksBtn.addEventListener('click', handleViewStocks);
elements.screenBtn.addEventListener('click', handleStartScreening);
elements.refreshRadarBtn.addEventListener('click', handleRefreshRadar);
elements.closeModal.addEventListener('click', handleCloseModal);

// Close modal on outside click
elements.stockListModal.addEventListener('click', (e) => {
    if (e.target === elements.stockListModal) {
        handleCloseModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && elements.stockListModal.classList.contains('active')) {
        handleCloseModal();
    }
});

// ===================================
// Initialization
// ===================================
async function init() {
    showToast('Stock Screener UI Loaded', 'success', 2000);

    // Check health on load
    await checkHealth();

    // Auto-refresh health every 30 seconds
    setInterval(checkHealth, 30000);

    // Try to load radar on startup
    try {
        const data = await getRadarStocks();
        if (data.count > 0) {
            renderRadarStocks(data.stocks || []);
            elements.radarCard.classList.add('completed');
        }
    } catch (error) {
        console.log('No radar data on startup');
    }
}

// Start the app
init();
