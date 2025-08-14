// Dashboard JavaScript - Main functionality for the Social Media Automation Debug Dashboard

// Global variables
let currentSection = 'overview';
let currentUser = null;
let authToken = localStorage.getItem('auth_token');
let refreshInterval = null;
let charts = {};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    if (authToken) {
        loadInitialData();
    }
    startAutoRefresh();
});

// Initialize dashboard components
function initializeDashboard() {
    console.log('Initializing Social Media Automation Dashboard...');
    
    // Check authentication status
    checkAuthStatus();
    
    // Initialize charts
    initializeCharts();
    
    // Load mock data for demo purposes
    loadMockData();
    
    showNotification('Dashboard initialized successfully', 'success');
}

// Setup event listeners
function setupEventListeners() {
    // Navigation menu
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            switchSection(section);
        });
    });
    
    // Window resize handler
    window.addEventListener('resize', function() {
        Object.values(charts).forEach(chart => {
            if (chart) chart.resize();
        });
    });
    
    // Modal close handler
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('modal');
        if (event.target === modal) {
            closeModal();
        }
    });
}

// Authentication functions
async function checkAuthStatus() {
    if (!authToken) {
        console.log('No auth token found');
        return;
    }
    
    try {
        const response = await fetch('/api/v1/auth/me', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            console.log('User authenticated:', currentUser.username);
        } else {
            authToken = null;
            localStorage.removeItem('auth_token');
            console.log('Authentication failed');
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        authToken = null;
        localStorage.removeItem('auth_token');
    }
}

// Section navigation
function switchSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
    
    // Update content sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    // Update section title
    const titleMap = {
        'overview': 'System Overview',
        'content': 'Content Generation',
        'workflows': 'Workflow Management',
        'platforms': 'Platform Integration',
        'analytics': 'Analytics & Insights',
        'api-testing': 'API Testing',
        'monitoring': 'System Health',
        'api-keys': 'API Key Management'
    };
    
    document.getElementById('section-title').textContent = titleMap[sectionName] || 'Dashboard';
    currentSection = sectionName;
    
    // Load section-specific data
    loadSectionData(sectionName);
}

// Load section-specific data
async function loadSectionData(section) {
    switch (section) {
        case 'overview':
            await loadOverviewData();
            break;
        case 'content':
            await loadContentData();
            break;
        case 'workflows':
            await loadWorkflowData();
            break;
        case 'platforms':
            await loadPlatformData();
            break;
        case 'analytics':
            await loadAnalyticsData();
            break;
        case 'monitoring':
            await loadMonitoringData();
            break;
    }
}

// Data loading functions
async function loadInitialData() {
    try {
        await Promise.all([
            loadOverviewData(),
            loadSystemHealth(),
            loadRecentActivity()
        ]);
    } catch (error) {
        console.error('Failed to load initial data:', error);
        showNotification('Failed to load dashboard data', 'error');
    }
}

async function loadOverviewData() {
    try {
        // Mock data for demonstration - replace with actual API calls
        updateStatCard('active-tasks', Math.floor(Math.random() * 20) + 5);
        updateStatCard('content-generated', Math.floor(Math.random() * 100) + 50);
        updateStatCard('content-published', Math.floor(Math.random() * 80) + 30);
        updateStatCard('system-errors', Math.floor(Math.random() * 5));
        
        updateContentChart();
        updatePlatformChart();
    } catch (error) {
        console.error('Failed to load overview data:', error);
    }
}

async function loadContentData() {
    try {
        // Load generation queue
        const queueData = await mockApiCall('/api/v1/content/queue');
        updateGenerationQueue(queueData);
        
        // Load AI service status
        const serviceStatus = await mockApiCall('/api/v1/services/status');
        updateAIServiceStatus(serviceStatus);
        
        // Load generation logs
        const logs = await mockApiCall('/api/v1/content/logs');
        updateGenerationLogs(logs);
    } catch (error) {
        console.error('Failed to load content data:', error);
    }
}

async function loadWorkflowData() {
    try {
        const workflows = await mockApiCall('/api/v1/workflows');
        updateActiveWorkflows(workflows);
        
        const history = await mockApiCall('/api/v1/workflows/history');
        updateWorkflowHistory(history);
    } catch (error) {
        console.error('Failed to load workflow data:', error);
    }
}

async function loadPlatformData() {
    try {
        const platforms = ['youtube', 'instagram', 'tiktok', 'facebook'];
        
        for (const platform of platforms) {
            const status = await mockApiCall(`/api/v1/platforms/${platform}/status`);
            updatePlatformStatus(platform, status);
        }
    } catch (error) {
        console.error('Failed to load platform data:', error);
    }
}

async function loadAnalyticsData() {
    try {
        const analytics = await mockApiCall('/api/v1/analytics/overview');
        updateAnalyticsData(analytics);
    } catch (error) {
        console.error('Failed to load analytics data:', error);
    }
}

async function loadMonitoringData() {
    try {
        const health = await mockApiCall('/health/detailed');
        updateSystemHealthData(health);
        
        const logs = await mockApiCall('/api/v1/logs');
        updateSystemLogs(logs);
    } catch (error) {
        console.error('Failed to load monitoring data:', error);
    }
}

// Chart initialization and updates
function initializeCharts() {
    // Content generation chart
    const contentCtx = document.getElementById('contentChart');
    if (contentCtx) {
        charts.contentChart = new Chart(contentCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Content Generated',
                    data: [12, 19, 8, 15, 22, 13, 18],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Platform performance chart
    const platformCtx = document.getElementById('platformChart');
    if (platformCtx) {
        charts.platformChart = new Chart(platformCtx, {
            type: 'doughnut',
            data: {
                labels: ['YouTube', 'Instagram', 'TikTok', 'Facebook'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: ['#ff0000', '#e4405f', '#000000', '#1877f2']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Performance chart
    const performanceCtx = document.getElementById('performanceChart');
    if (performanceCtx) {
        charts.performanceChart = new Chart(performanceCtx, {
            type: 'bar',
            data: {
                labels: ['Views', 'Engagement', 'Shares', 'Comments'],
                datasets: [{
                    label: 'This Week',
                    data: [12500, 850, 320, 180],
                    backgroundColor: '#667eea'
                }, {
                    label: 'Last Week',
                    data: [10200, 720, 280, 150],
                    backgroundColor: '#764ba2'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Resource usage chart
    const resourceCtx = document.getElementById('resourceChart');
    if (resourceCtx) {
        charts.resourceChart = new Chart(resourceCtx, {
            type: 'line',
            data: {
                labels: Array.from({length: 10}, (_, i) => `${10-i}m ago`),
                datasets: [{
                    label: 'CPU %',
                    data: generateRandomData(10, 20, 80),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)'
                }, {
                    label: 'Memory %',
                    data: generateRandomData(10, 30, 70),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

function updateContentChart() {
    if (charts.contentChart) {
        charts.contentChart.data.datasets[0].data = generateRandomData(7, 5, 25);
        charts.contentChart.update();
    }
}

function updatePlatformChart() {
    if (charts.platformChart) {
        charts.platformChart.data.datasets[0].data = [
            Math.floor(Math.random() * 50) + 30,
            Math.floor(Math.random() * 30) + 15,
            Math.floor(Math.random() * 25) + 10,
            Math.floor(Math.random() * 15) + 5
        ];
        charts.platformChart.update();
    }
}

// UI update functions
function updateStatCard(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function updateGenerationQueue(data) {
    const container = document.getElementById('generation-queue');
    if (!container) return;
    
    container.innerHTML = '';
    
    const mockQueue = [
        { id: 1, type: 'Video', status: 'processing', title: 'AI Content Creation Guide' },
        { id: 2, type: 'Image', status: 'completed', title: 'Social Media Tips Carousel' },
        { id: 3, type: 'Text', status: 'failed', title: 'Weekly Newsletter Content' },
        { id: 4, type: 'Video', status: 'processing', title: 'Platform Comparison Video' }
    ];
    
    mockQueue.forEach(item => {
        const queueItem = document.createElement('div');
        queueItem.className = `queue-item ${item.status}`;
        queueItem.innerHTML = `
            <div>
                <strong>${item.title}</strong>
                <br><small>${item.type}</small>
            </div>
            <span class="status-badge ${item.status}">${item.status}</span>
        `;
        container.appendChild(queueItem);
    });
}

function updateAIServiceStatus(data) {
    const container = document.getElementById('ai-services');
    if (!container) return;
    
    container.innerHTML = '';
    
    const services = [
        { name: 'OpenAI GPT-4', status: 'online' },
        { name: 'ElevenLabs', status: 'online' },
        { name: 'Fliki', status: 'limited' },
        { name: 'HeyGen', status: 'offline' }
    ];
    
    services.forEach(service => {
        const serviceItem = document.createElement('div');
        serviceItem.className = 'service-item';
        serviceItem.innerHTML = `
            <span class="service-name">${service.name}</span>
            <span class="status-badge ${service.status}">${service.status}</span>
        `;
        container.appendChild(serviceItem);
    });
}

function updateGenerationLogs(data) {
    const container = document.getElementById('generation-logs');
    if (!container) return;
    
    const logs = [
        { time: '14:23:45', level: 'info', message: 'Started video generation for "AI Guide"' },
        { time: '14:22:12', level: 'success', message: 'Voice generation completed successfully' },
        { time: '14:21:08', level: 'warning', message: 'High API usage detected for OpenAI' },
        { time: '14:20:33', level: 'error', message: 'Failed to connect to Fliki API' }
    ];
    
    container.innerHTML = logs.map(log => 
        `<div class="log-entry ${log.level}">[${log.time}] ${log.message}</div>`
    ).join('');
}

function updateActiveWorkflows(data) {
    const container = document.getElementById('active-workflows');
    if (!container) return;
    
    const workflows = [
        { id: 1, name: 'Daily Content Creation', status: 'running', progress: 75 },
        { id: 2, name: 'Weekly Analytics Report', status: 'scheduled', progress: 0 },
        { id: 3, name: 'Multi-Platform Publishing', status: 'completed', progress: 100 }
    ];
    
    container.innerHTML = workflows.map(workflow => `
        <div class="workflow-item">
            <div class="workflow-title">${workflow.name}</div>
            <div class="workflow-status">
                <span class="status-badge ${workflow.status}">${workflow.status}</span>
                <small>${workflow.progress}%</small>
            </div>
        </div>
    `).join('');
}

function updateWorkflowHistory(data) {
    const container = document.getElementById('workflow-history');
    if (!container) return;
    
    const history = [
        { name: 'Content Batch #47', time: '2 hours ago', status: 'completed' },
        { name: 'Platform Sync', time: '4 hours ago', status: 'completed' },
        { name: 'Analytics Collection', time: '6 hours ago', status: 'failed' }
    ];
    
    container.innerHTML = history.map(item => `
        <div class="workflow-item">
            <div class="workflow-title">${item.name}</div>
            <div class="workflow-status">
                <small>${item.time}</small>
                <span class="status-badge ${item.status}">${item.status}</span>
            </div>
        </div>
    `).join('');
}

function updatePlatformStatus(platform, data) {
    const statusIndicator = document.getElementById(`${platform}-status`);
    if (statusIndicator) {
        statusIndicator.className = 'status-indicator connected';
    }
    
    // Update platform-specific stats
    const stats = {
        youtube: { uploads: 15, quota: '45%' },
        instagram: { posts: 28, rate: 'OK' },
        tiktok: { videos: 12, api: 'Limited' },
        facebook: { posts: 8, pages: 3 }
    };
    
    const platformStats = stats[platform];
    if (platformStats) {
        Object.keys(platformStats).forEach(key => {
            const element = document.getElementById(`${platform}-${key}`);
            if (element) {
                element.textContent = platformStats[key];
            }
        });
    }
}

function updateRecentActivity() {
    const container = document.getElementById('activity-feed');
    if (!container) return;
    
    const activities = [
        {
            icon: 'fas fa-check',
            type: 'success',
            title: 'Content Published',
            description: 'Video "AI Content Tips" published to YouTube',
            time: '5 minutes ago'
        },
        {
            icon: 'fas fa-cog',
            type: 'info',
            title: 'Workflow Started',
            description: 'Daily content generation workflow initiated',
            time: '15 minutes ago'
        },
        {
            icon: 'fas fa-exclamation-triangle',
            type: 'warning',
            title: 'API Limit Warning',
            description: 'OpenAI API usage at 85% of daily limit',
            time: '32 minutes ago'
        },
        {
            icon: 'fas fa-upload',
            type: 'success',
            title: 'Content Generated',
            description: 'New video content generated successfully',
            time: '1 hour ago'
        }
    ];
    
    container.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">
                <i class="${activity.icon}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-description">${activity.description}</div>
            </div>
            <div class="activity-time">${activity.time}</div>
        </div>
    `).join('');
}

function updateSystemHealthData(data) {
    const container = document.getElementById('system-health');
    if (!container) return;
    
    const healthItems = [
        { name: 'API Server', status: 'healthy', value: 'Running' },
        { name: 'Database', status: 'healthy', value: 'Connected' },
        { name: 'Redis', status: 'healthy', value: 'Connected' },
        { name: 'Celery Worker', status: 'warning', value: '2/3 Active' }
    ];
    
    container.innerHTML = healthItems.map(item => `
        <div class="health-item">
            <span>${item.name}</span>
            <span class="status-badge ${item.status}">${item.value}</span>
        </div>
    `).join('');
}

function updateSystemLogs(data) {
    const container = document.getElementById('system-logs');
    if (!container) return;
    
    const logs = [
        '[2024-01-15 14:30:22] INFO: Application started successfully',
        '[2024-01-15 14:29:45] INFO: Database connection established',
        '[2024-01-15 14:29:30] WARN: High memory usage detected (78%)',
        '[2024-01-15 14:28:12] INFO: Celery worker started',
        '[2024-01-15 14:27:55] ERROR: Failed to connect to external API',
        '[2024-01-15 14:27:30] INFO: Redis connection established'
    ];
    
    container.innerHTML = logs.map(log => {
        const level = log.includes('ERROR') ? 'error' : 
                     log.includes('WARN') ? 'warning' : 
                     'info';
        return `<div class="log-entry ${level}">${log}</div>`;
    }).join('');
}

// Action functions
async function generateTestContent() {
    const contentType = document.getElementById('content-type').value;
    const platform = document.getElementById('target-platform').value;
    
    showNotification(`Generating ${contentType} content for ${platform}...`, 'info');
    
    try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 2000));
        showNotification('Test content generation started successfully', 'success');
        
        // Refresh content data
        await loadContentData();
    } catch (error) {
        showNotification('Failed to generate test content', 'error');
    }
}

async function testPlatformConnection(platform) {
    showNotification(`Testing ${platform} connection...`, 'info');
    
    try {
        // Mock API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        const success = Math.random() > 0.3; // 70% success rate
        if (success) {
            showNotification(`${platform} connection successful`, 'success');
            document.getElementById(`${platform}-status`).className = 'status-indicator connected';
        } else {
            showNotification(`${platform} connection failed`, 'error');
            document.getElementById(`${platform}-status`).className = 'status-indicator';
        }
    } catch (error) {
        showNotification(`Failed to test ${platform} connection`, 'error');
    }
}

function viewPlatformLogs(platform) {
    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = `
        <h3>${platform.toUpperCase()} Platform Logs</h3>
        <div class="log-viewer">
            <div class="log-entry info">[14:30:15] INFO: Connection established to ${platform} API</div>
            <div class="log-entry success">[14:29:42] SUCCESS: Content uploaded to ${platform}</div>
            <div class="log-entry warning">[14:28:20] WARN: Rate limit approaching for ${platform}</div>
            <div class="log-entry error">[14:27:05] ERROR: Failed to authenticate with ${platform}</div>
            <div class="log-entry info">[14:26:30] INFO: Retrying ${platform} API call</div>
        </div>
    `;
    document.getElementById('modal').style.display = 'block';
}

async function executeApiTest() {
    const method = document.getElementById('api-method').value;
    const endpoint = document.getElementById('api-endpoint').value;
    const requestBody = document.getElementById('api-request-body').value;
    
    if (!endpoint) {
        showNotification('Please enter an API endpoint', 'error');
        return;
    }
    
    try {
        let options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (authToken) {
            options.headers['Authorization'] = `Bearer ${authToken}`;
        }
        
        if (method !== 'GET' && requestBody) {
            options.body = requestBody;
        }
        
        showNotification('Executing API request...', 'info');
        
        const response = await fetch(endpoint, options);
        const data = await response.json();
        
        const responseElement = document.getElementById('api-response');
        responseElement.textContent = JSON.stringify(data, null, 2);
        
        if (response.ok) {
            showNotification('API request successful', 'success');
        } else {
            showNotification('API request failed', 'error');
        }
    } catch (error) {
        document.getElementById('api-response').textContent = `Error: ${error.message}`;
        showNotification('API request failed', 'error');
    }
}

function quickTest(endpoint) {
    document.getElementById('api-method').value = 'GET';
    document.getElementById('api-endpoint').value = endpoint;
    document.getElementById('api-request-body').value = '';
    executeApiTest();
}

async function loadAnalytics() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    if (!startDate || !endDate) {
        showNotification('Please select date range', 'error');
        return;
    }
    
    showNotification('Loading analytics data...', 'info');
    
    try {
        // Mock analytics data
        const analytics = {
            views: Math.floor(Math.random() * 100000) + 50000,
            engagement: Math.floor(Math.random() * 10000) + 5000,
            shares: Math.floor(Math.random() * 1000) + 500,
            comments: Math.floor(Math.random() * 500) + 200
        };
        
        // Update engagement metrics
        const metricsContainer = document.getElementById('engagement-metrics');
        if (metricsContainer) {
            metricsContainer.innerHTML = Object.entries(analytics).map(([key, value]) => `
                <div class="metric-item">
                    <span class="metric-label">${key.toUpperCase()}</span>
                    <span class="metric-value">${value.toLocaleString()}</span>
                </div>
            `).join('');
        }
        
        showNotification('Analytics loaded successfully', 'success');
    } catch (error) {
        showNotification('Failed to load analytics', 'error');
    }
}

// Utility functions
function refreshData() {
    loadSectionData(currentSection);
    showNotification('Data refreshed', 'success');
}

function exportLogs() {
    // Create mock log data
    const logData = {
        timestamp: new Date().toISOString(),
        system_health: 'Good',
        active_tasks: document.getElementById('active-tasks').textContent,
        errors: document.getElementById('system-errors').textContent,
        logs: Array.from(document.querySelectorAll('.log-entry')).map(entry => entry.textContent)
    };
    
    const blob = new Blob([JSON.stringify(logData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `debug-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Logs exported successfully', 'success');
}

function refreshLogs() {
    updateSystemLogs();
    showNotification('Logs refreshed', 'success');
}

function clearLogs() {
    const logViewer = document.getElementById('system-logs');
    if (logViewer) {
        logViewer.innerHTML = '<div class="log-entry info">Logs cleared</div>';
    }
    showNotification('Logs cleared', 'info');
}

function createWorkflow() {
    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = `
        <h3>Create New Workflow</h3>
        <form id="workflow-form">
            <div class="control-group">
                <label>Workflow Name:</label>
                <input type="text" id="workflow-name" placeholder="Enter workflow name">
            </div>
            <div class="control-group">
                <label>Template:</label>
                <select id="workflow-template">
                    <option value="content-generation">Content Generation</option>
                    <option value="multi-platform-publish">Multi-Platform Publishing</option>
                    <option value="analytics-report">Analytics Report</option>
                    <option value="custom">Custom Workflow</option>
                </select>
            </div>
            <div class="control-group">
                <label>Description:</label>
                <textarea id="workflow-description" placeholder="Describe the workflow purpose"></textarea>
            </div>
            <div style="margin-top: 1rem;">
                <button type="button" class="btn btn-primary" onclick="saveWorkflow()">Create Workflow</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            </div>
        </form>
    `;
    document.getElementById('modal').style.display = 'block';
}

function saveWorkflow() {
    const name = document.getElementById('workflow-name').value;
    const template = document.getElementById('workflow-template').value;
    
    if (!name) {
        showNotification('Please enter a workflow name', 'error');
        return;
    }
    
    showNotification('Workflow created successfully', 'success');
    closeModal();
    loadWorkflowData();
}

function loadWorkflowTemplates() {
    showNotification('Loading workflow templates...', 'info');
    // This would load predefined templates
    setTimeout(() => {
        showNotification('Templates loaded', 'success');
    }, 1000);
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : type === 'warning' ? 'exclamation-triangle' : 'info'}"></i>
        <span>${message}</span>
    `;
    
    const container = document.getElementById('notifications');
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

function startAutoRefresh() {
    // Refresh overview data every 30 seconds
    refreshInterval = setInterval(() => {
        if (currentSection === 'overview') {
            loadOverviewData();
        }
    }, 30000);
}

// Mock API call function
async function mockApiCall(endpoint, data = null) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
    
    // Return mock data based on endpoint
    switch (endpoint) {
        case '/api/v1/content/queue':
            return { queue: [], count: 4 };
        case '/api/v1/services/status':
            return { services: [] };
        default:
            return { status: 'ok', data: {} };
    }
}

function loadMockData() {
    // Set initial date range for analytics
    const today = new Date();
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    document.getElementById('start-date').value = lastWeek.toISOString().split('T')[0];
    document.getElementById('end-date').value = today.toISOString().split('T')[0];
    
    // Load initial activity feed
    updateRecentActivity();
}

function generateRandomData(length, min, max) {
    return Array.from({length}, () => Math.floor(Math.random() * (max - min + 1)) + min);
}

// Expose global functions
window.switchSection = switchSection;
window.generateTestContent = generateTestContent;
window.testPlatformConnection = testPlatformConnection;
window.viewPlatformLogs = viewPlatformLogs;
window.executeApiTest = executeApiTest;
window.quickTest = quickTest;
window.loadAnalytics = loadAnalytics;
window.refreshData = refreshData;
window.exportLogs = exportLogs;
window.refreshLogs = refreshLogs;
window.clearLogs = clearLogs;
window.createWorkflow = createWorkflow;
window.saveWorkflow = saveWorkflow;
window.loadWorkflowTemplates = loadWorkflowTemplates;
window.closeModal = closeModal;