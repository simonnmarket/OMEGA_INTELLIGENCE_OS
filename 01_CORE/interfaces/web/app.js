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

// Renderers will be defined after helper functions

const renderFeed = (hasNewEvents = false) => {
    const container = document.getElementById('audit-feed');
    container.innerHTML = '';

    const recentLogs = [...appState.logs].reverse().slice(0, 50); // Show last 50

    recentLogs.forEach((log, index) => {
        const div = document.createElement('div');
        div.className = 'feed-item';

        // Highlight new events
        if (hasNewEvents && index === 0) {
            div.classList.add('new-event');
        }

        // Determine Module Name from Event Type
        let moduleName = 'Core System';
        if (log.event_type === 'RISK') moduleName = 'Risk Manager';
        if (log.event_type === 'ASSESSMENT') moduleName = 'Engine';
        if (log.event_type === 'AI_EXEC') moduleName = 'AI Interface';
        if (log.event_type === 'LIBRARY') moduleName = 'Controller';
        if (log.event_type === 'BRIDGE_INGEST') moduleName = 'Bridge Layer';

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

        const newStats = await statsRes.json();
        const newLogs = await logsRes.json();

        // Check for new events
        const hasNewEvents = newLogs.length > appState.logs.length;

        appState.stats = newStats;
        appState.logs = newLogs;

        renderStats();
        renderFeed(hasNewEvents);
        renderIngestedFiles();
        renderModuleBreakdown();
    } catch (err) {
        console.error("Connection lost", err);
        document.getElementById('sys-status').textContent = 'CONNECTING...';
        document.getElementById('sys-status').style.color = 'var(--status-warning)';
    }
};

// Animate counter
const animateCounter = (element, target) => {
    element.classList.add('animate');
    const current = parseInt(element.textContent) || 0;
    if (current === target) return;

    const duration = 500;
    const steps = 20;
    const increment = (target - current) / steps;
    let step = 0;

    const timer = setInterval(() => {
        step++;
        const value = Math.round(current + (increment * step));
        element.textContent = value;

        if (step >= steps) {
            clearInterval(timer);
            element.textContent = target;
        }
    }, duration / steps);
};

// Render Ingested Files
const renderIngestedFiles = () => {
    const ingestedEvents = appState.logs.filter(log => log.event_type === 'BRIDGE_INGEST');
    const ingestedCount = ingestedEvents.length;

    const countEl = document.getElementById('stat-ingested');
    animateCounter(countEl, ingestedCount);

    if (ingestedCount > 0) {
        document.getElementById('ingested-status').textContent = `${ingestedCount} Files`;
    }
};

// Render Module Breakdown
const renderModuleBreakdown = () => {
    const container = document.getElementById('module-breakdown');

    // Count events by module type
    const moduleCounts = {
        'Core': 0,
        'Risk Manager': 0,
        'Bridge': 0,
        'Engine': 0,
        'AI Interface': 0
    };

    appState.logs.forEach(log => {
        if (log.event_type === 'RISK' || log.event_type === 'CONFLICT') moduleCounts['Risk Manager']++;
        else if (log.event_type === 'BRIDGE_INGEST') moduleCounts['Bridge']++;
        else if (log.event_type === 'ASSESSMENT') moduleCounts['Engine']++;
        else if (log.event_type === 'AI_EXEC') moduleCounts['AI Interface']++;
        else moduleCounts['Core']++;
    });

    const colors = {
        'Core': '#3B82F6',
        'Risk Manager': '#F59E0B',
        'Bridge': '#10B981',
        'Engine': '#8B5CF6',
        'AI Interface': '#EC4899'
    };

    container.innerHTML = Object.entries(moduleCounts)
        .filter(([_, count]) => count > 0)
        .map(([name, count]) => `
            <div class="module-item">
                <div class="module-name">
                    <div class="module-indicator" style="background: ${colors[name]}; box-shadow: 0 0 8px ${colors[name]};"></div>
                    ${name}
                </div>
                <div class="module-count">${count}</div>
            </div>
        `).join('');
};

// Enhanced renderStats with animations
const renderStats = () => {
    const totalEvents = appState.stats.total_events || 0;
    animateCounter(document.getElementById('stat-events'), totalEvents);

    // Count risk scans
    const riskScans = appState.logs.filter(log => log.event_type === 'RISK').length;
    animateCounter(document.getElementById('stat-risk-scans'), riskScans);

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

// Navigation Logic
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        // Remove active class from all
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        // Add to clicked
        e.currentTarget.classList.add('active');

        const sectionName = e.currentTarget.querySelector('span').textContent;
        handleNavigation(sectionName);
    });
});

const handleNavigation = (section) => {
    const title = document.querySelector('.page-title');
    const content = document.querySelector('.content-wrapper');

    title.textContent = section;

    // Simulate View Change
    if (section === 'Dashboard') {
        document.querySelector('.grid').style.display = 'grid';
        document.querySelector('.feed-container').style.display = 'block';
        document.querySelector('.section-header').style.display = 'flex';
    } else if (section === 'Module Library') {
        alert("Module Library View: Coming in Phase 9");
    } else {
        // Simple feedback for now
        console.log(`Navigated to ${section}`);
    }
};

// Init
document.addEventListener('DOMContentLoaded', () => {
    fetchData(); // Initial load
    setInterval(fetchData, 3000); // Polling every 3s
});
