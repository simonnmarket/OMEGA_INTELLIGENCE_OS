const API_BASE = '/api';

// State
let appState = {
    logs: [],
    stats: {},
    modules: []
};

// Utils
const formatTime = (isoString) => {
    return new Date(isoString).toLocaleTimeString();
};

// Components
const renderStats = () => {
    document.getElementById('stat-events').textContent = appState.stats.total_events || 0;
    document.getElementById('stat-status').textContent = appState.stats.system_status || 'OFFLINE';
    document.getElementById('stat-last').textContent = appState.stats.last_active ? formatTime(appState.stats.last_active) : '--:--';
};

const renderLogs = () => {
    const container = document.getElementById('audit-feed');
    container.innerHTML = '';
    
    // Reverse logs to show newest first
    const recentLogs = [...appState.logs].reverse();
    
    recentLogs.forEach(log => {
        const div = document.createElement('div');
        div.className = 'log-entry';
        div.innerHTML = `
            <span class="log-time">[${formatTime(log.timestamp)}]</span>
            <span class="log-type type-${log.event_type}">${log.event_type}</span>
            <span class="log-msg">${log.message}</span>
        `;
        container.appendChild(div);
    });
};

// Data Fetching
const fetchData = async () => {
    try {
        const [statsRes, logsRes] = await Promise.all([
            fetch(`${API_BASE}/stats`),
            fetch(`${API_BASE}/audit`)
        ]);
        
        appState.stats = await statsRes.json();
        appState.logs = await logsRes.json();
        
        renderStats();
        renderLogs();
    } catch (err) {
        console.error("Connection lost", err);
        document.getElementById('stat-status').textContent = 'CONNECTION LOST';
        document.getElementById('stat-status').style.color = 'var(--danger)';
    }
};

// Init
document.addEventListener('DOMContentLoaded', () => {
    fetchData(); // Initial load
    setInterval(fetchData, 2000); // Polling every 2s
});
