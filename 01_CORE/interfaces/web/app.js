const API_BASE = '/api';

// State
let appState = {
    logs: [],
    stats: {}
};

// Utils
const formatTime = (isoString) => {
    if (!isoString) return '--:--:--';
    return new Date(isoString).toLocaleTimeString('en-US', { hour12: false });
};

const getStatusClass = (eventType) => {
    if (eventType === 'CONFLICT') return 'status-CONFLICT';
    if (eventType === 'PROCESS' || eventType === 'SUCCESS') return 'status-SUCCESS';
    if (eventType === 'ASSESSMENT') return 'status-INFO';
    return 'status-INFO';
};

const getModuleBadgeClass = (eventType) => {
    if (eventType === 'RISK' || eventType === 'CONFLICT') return 'badge-risk';
    return 'badge-core';
};

// Renderers
const renderStats = () => {
    document.getElementById('stat-events').textContent = appState.stats.total_events || 0;

    // Update system status
    const statusEl = document.getElementById('sys-status');
    if (appState.stats.system_status === 'ONLINE') {
        statusEl.textContent = 'OPERATIONAL';
        document.querySelector('.status-dot').style.background = 'var(--status-success)';
        document.querySelector('.status-dot').style.boxShadow = '0 0 8px var(--status-success)';
    } else {
        statusEl.textContent = 'OFFLINE';
        document.querySelector('.status-dot').style.background = 'var(--status-error)';
        document.querySelector('.status-dot').style.boxShadow = 'none';
        document.querySelector('.status-dot').style.animation = 'none';
    }
};

const renderFeed = () => {
    const container = document.getElementById('audit-feed');
    container.innerHTML = '';

    const recentLogs = [...appState.logs].reverse().slice(0, 50); // Show last 50

    recentLogs.forEach(log => {
        const div = document.createElement('div');
        div.className = 'feed-item';

        // Determine Module Name from Event Type
        let moduleName = 'Core System';
        if (log.event_type === 'RISK') moduleName = 'Risk Manager';
        if (log.event_type === 'ASSESSMENT') moduleName = 'Engine';
        if (log.event_type === 'AI_EXEC') moduleName = 'AI Interface';
        if (log.event_type === 'LIBRARY') moduleName = 'Controller';

        div.innerHTML = `
            <span style="font-weight: 500">${log.message}</span>
            <span class="feed-module">
                <div class="module-badge ${getModuleBadgeClass(log.event_type)}"></div>
                ${moduleName}
            </span>
            <span class="feed-time">${formatTime(log.timestamp)}</span>
            <div class="feed-status ${getStatusClass(log.event_type)}">${log.event_type}</div>
        `;
        container.appendChild(div);
    });
};

// Fetch
const fetchData = async () => {
    try {
        const [statsRes, logsRes] = await Promise.all([
            fetch(`${API_BASE}/stats`),
            fetch(`${API_BASE}/audit`)
        ]);

        appState.stats = await statsRes.json();
        appState.logs = await logsRes.json();

        renderStats();
        renderFeed();
    } catch (err) {
        console.error("Connection lost", err);
        document.getElementById('sys-status').textContent = 'CONNECTING...';
        document.getElementById('sys-status').style.color = 'var(--status-warning)';
    }
};

// Init
document.addEventListener('DOMContentLoaded', () => {
    fetchData(); // Initial load
    setInterval(fetchData, 3000); // Polling every 3s
});
