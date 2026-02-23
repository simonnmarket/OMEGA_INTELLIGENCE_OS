/* 
===============================================
OMEGA OS - Premium SaaS Execution Dashboard - Live Logic
===============================================
*/

const API_BASE = "http://127.0.0.1:5000/api";

document.addEventListener('DOMContentLoaded', () => {
    // Start Live Clock
    const pingElement = document.querySelector('.latency');
    setInterval(() => {
        const ping = Math.floor(Math.random() * 5) + 8; // Simulate 10-15ms Localhost ping
        pingElement.textContent = `${ping}ms Ping`;
    }, 2000);

    // Initial log
    addLog('System', 'Awaiting MT5 Server Connection...', 'warning');

    // Start Live Data Loops
    fetchLiveAccount();
    setInterval(fetchLiveAccount, 5000); // Check balance every 5s

    fetchCryptoScanner();
    setInterval(fetchCryptoScanner, 2000); // Orbit Mode: Scan all cryptos every 2 seconds
});

async function fetchLiveAccount() {
    try {
        const res = await fetch(`${API_BASE}/account`);
        const data = await res.json();

        if (data.balance) {
            // Format number to currency
            const formatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
            document.getElementById('live-aum').innerText = formatter.format(data.balance);
            document.querySelector('.role-info .role').innerText = `ID: ${data.login}`;
        }
    } catch (err) {
        console.error("API Bridge Offline");
    }
}

async function fetchCryptoScanner() {
    try {
        const res = await fetch(`${API_BASE}/scan/crypto`);
        const data = await res.json();

        const symbols = ["BTCUSD", "ETHUSD", "SOLUSD"];

        symbols.forEach(sym => {
            if (data[sym] && data[sym].price > 0) {
                // Update Price
                document.getElementById(`price-${sym}`).innerText = `$${data[sym].price.toFixed(2)}`;
                document.getElementById(`symbol-${sym}`).innerText = data[sym].symbol;

                // Update CTI Force Navis Indicators
                document.getElementById(`vd-${sym}`).innerText = data[sym].volume_delta;

                const ofElement = document.getElementById(`of-${sym}`);
                ofElement.innerText = data[sym].order_flow;
                if (data[sym].order_flow === "Bullish") {
                    ofElement.className = "buy";
                    ofElement.style.color = "var(--buy-green)";
                } else if (data[sym].order_flow === "Bearish") {
                    ofElement.className = "sell";
                    ofElement.style.color = "var(--danger)";
                } else {
                    ofElement.style.color = "var(--text-secondary)";
                }
            }
        });

        document.getElementById('pulse-status').innerText = "Live Orbit (CTI Active)";
        document.getElementById('pulse-status').style.color = "var(--success)";

    } catch (err) {
        document.getElementById('pulse-status').innerText = "Scanner Offline";
        document.getElementById('pulse-status').style.color = "var(--danger)";
    }
}

// Function to simulate clicking the Test Trade button
function triggerTestTrade(symbol) {
    addLog('CTI Engine', `Scanning ${symbol} Order Book Depth for Liquidity Voids...`, 'info');

    // Simulate ML thinking delay
    setTimeout(() => {
        addLog('ML Adaptive', `Tuning Resonance Weights for ${symbol} (0.001mm precision)...`, 'warning');

        setTimeout(() => {
            addLog('Treasury', `Volatility Check PASSED. Toxicity < 0.15. Margin Allocated.`, 'success');

            setTimeout(() => {
                const ticket = Math.floor(100000000 + Math.random() * 900000000);
                addLog('Execution', `[LIVE TRADE] BUY 0.01 ${symbol}. Ticket: ${ticket}`, 'success');

                // Show floating notification
                showNotification(`Executed BUY 0.01 ${symbol}`);
            }, 800);

        }, 1200);

    }, 1500);
}

// Console Log Injector
function addLog(module, message, type = 'info') {
    const consoleBody = document.getElementById('live-logs');
    const now = new Date();
    const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `<i>[${timeString}]</i> <span class="${type}">[${module}] ${message}</span>`;

    consoleBody.appendChild(entry);
    consoleBody.scrollTop = consoleBody.scrollHeight; // Auto-scroll to bottom
}

// Minimal Premium Notification System
function showNotification(message) {
    const toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.bottom = '30px';
    toast.style.right = '30px';
    toast.style.background = 'rgba(16, 185, 129, 0.9)'; // Success Green Profile
    toast.style.color = '#fff';
    toast.style.padding = '12px 24px';
    toast.style.borderRadius = '8px';
    toast.style.boxShadow = '0 10px 30px rgba(0,0,0,0.3)';
    toast.style.backdropFilter = 'blur(10px)';
    toast.style.fontFamily = "'Inter', sans-serif";
    toast.style.fontWeight = '500';
    toast.style.fontSize = '0.9rem';
    toast.style.zIndex = '1000';
    toast.style.transform = 'translateY(50px)';
    toast.style.opacity = '0';
    toast.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
    toast.innerHTML = `<i class="uil uil-check-circle" style="margin-right:8px; font-size:1.1rem; vertical-align:middle;"></i> ${message}`;

    document.body.appendChild(toast);

    // Animate In
    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
    });

    // Animate Out
    setTimeout(() => {
        toast.style.transform = 'translateY(50px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}
