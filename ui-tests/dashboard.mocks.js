/**
 * Mock Implementation for Dashboard.js Functions
 * This file provides mock implementations for functions that are referenced
 * but not fully implemented in the code snippets
 */

// Mock implementations to make tests work with the actual dashboard.js
window.initializeCharts = window.initializeCharts || function() {
  window.charts = window.charts || {};
  const chartIds = ['performanceChart', 'platformBreakdownChart', 'overviewChart', 'resourceChart'];
  
  chartIds.forEach(id => {
    if (document.getElementById(id)) {
      window.charts[id] = {
        config: { type: getChartType(id) },
        data: { labels: [], datasets: [] },
        update: jest.fn(),
        resize: jest.fn(),
        destroy: jest.fn()
      };
    }
  });
};

function getChartType(chartId) {
  if (chartId.includes('breakdown')) return 'doughnut';
  if (chartId.includes('performance')) return 'line';
  if (chartId.includes('resource')) return 'radar';
  return 'bar';
}

// Mock data loading functions
window.loadOverviewData = window.loadOverviewData || jest.fn().mockResolvedValue();
window.loadContentData = window.loadContentData || jest.fn().mockResolvedValue();
window.loadWorkflowData = window.loadWorkflowData || jest.fn().mockResolvedValue();
window.loadPlatformData = window.loadPlatformData || jest.fn().mockResolvedValue();
window.loadAnalyticsData = window.loadAnalyticsData || jest.fn().mockResolvedValue();
window.loadMonitoringData = window.loadMonitoringData || jest.fn().mockResolvedValue();
window.loadSystemHealth = window.loadSystemHealth || jest.fn().mockResolvedValue();
window.loadRecentActivity = window.loadRecentActivity || jest.fn().mockResolvedValue();

// Mock utility functions
window.showNotification = window.showNotification || function(message, type = 'info') {
  const container = document.getElementById('notifications');
  if (container) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    container.appendChild(notification);
    
    // Auto-remove after timeout
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 5000);
  }
};

window.updateStatCard = window.updateStatCard || function(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.classList.add('updating');
    
    // Format number with commas
    const formattedValue = typeof value === 'number' && value >= 1000 
      ? value.toLocaleString()
      : value.toString();
    
    element.textContent = formattedValue;
    
    setTimeout(() => {
      element.classList.remove('updating');
    }, 300);
  }
};

window.updateGenerationQueue = window.updateGenerationQueue || function(queueData) {
  const container = document.getElementById('content-queue');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!queueData || queueData.length === 0) {
    container.innerHTML = '<div class="empty-state">No items in queue</div>';
    return;
  }
  
  queueData.forEach(item => {
    const queueItem = document.createElement('div');
    queueItem.className = `queue-item ${item.status}`;
    queueItem.innerHTML = `
      <span class="queue-type">${item.type}</span>
      <span class="queue-platform">${item.platform}</span>
      <span class="queue-status">${item.status}</span>
    `;
    container.appendChild(queueItem);
  });
};

window.updateGenerationLogs = window.updateGenerationLogs || function(logs) {
  const container = document.getElementById('generation-logs');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!logs || logs.length === 0) {
    container.innerHTML = '<div class="empty-state">No logs available</div>';
    return;
  }
  
  logs.forEach(log => {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${log.level}`;
    
    const timestamp = new Date(log.timestamp).toLocaleTimeString();
    logEntry.innerHTML = `
      <span class="timestamp">${timestamp}</span>
      <span class="message">${log.message}</span>
    `;
    container.appendChild(logEntry);
  });
};

window.updateAIServiceStatus = window.updateAIServiceStatus || function(services) {
  Object.keys(services).forEach(serviceName => {
    const element = document.getElementById(`${serviceName}-service`);
    if (element) {
      const status = services[serviceName];
      element.className = `service-status ${status.connected ? 'connected' : 'disconnected'}`;
    }
  });
};

window.updateActiveWorkflows = window.updateActiveWorkflows || function(workflows) {
  const container = document.getElementById('active-workflows');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!workflows || workflows.length === 0) {
    container.innerHTML = '<div class="empty-state">No active workflows</div>';
    return;
  }
  
  workflows.forEach(workflow => {
    const workflowElement = document.createElement('div');
    workflowElement.className = `workflow-item ${workflow.status}`;
    workflowElement.innerHTML = `
      <h4>${workflow.name}</h4>
      <span class="status">${workflow.status}</span>
      <span class="last-run">${workflow.lastRun ? new Date(workflow.lastRun).toLocaleTimeString() : 'Never'}</span>
    `;
    container.appendChild(workflowElement);
  });
};

// Chart update functions
window.updateContentChart = window.updateContentChart || function(data) {
  if (window.charts && window.charts.platformBreakdownChart) {
    window.charts.platformBreakdownChart.data = data;
    window.charts.platformBreakdownChart.update();
  }
};

window.updatePlatformChart = window.updatePlatformChart || function(data) {
  if (window.charts && window.charts.performanceChart) {
    window.charts.performanceChart.data = data;
    window.charts.performanceChart.update();
  }
};

window.updateResourceChart = window.updateResourceChart || function(data) {
  if (window.charts && window.charts.resourceChart) {
    window.charts.resourceChart.data = data;
    window.charts.resourceChart.update();
  }
};

window.updatePerformanceChart = window.updatePerformanceChart || function(data) {
  if (window.charts && window.charts.performanceChart) {
    window.charts.performanceChart.data = data;
    window.charts.performanceChart.update();
  }
};

// Advanced functions for monitoring and workflows
window.updateActiveTasks = window.updateActiveTasks || function(tasks) {
  const container = document.getElementById('active-tasks');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!tasks || tasks.length === 0) {
    container.innerHTML = '<div class="empty-state">No active tasks</div>';
    return;
  }
  
  tasks.forEach(task => {
    const taskElement = document.createElement('div');
    taskElement.className = `task-item ${task.status}`;
    taskElement.innerHTML = `
      <h4>${task.name}</h4>
      <div class="progress-bar" style="width: ${task.progress}%"></div>
      <span class="status">${task.status}</span>
    `;
    container.appendChild(taskElement);
  });
};

window.updateContentPerformance = window.updateContentPerformance || function(performance) {
  const container = document.getElementById('content-performance');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!performance || performance.length === 0) {
    container.innerHTML = '<div class="empty-state">No performance data available</div>';
    return;
  }
  
  // Sort by engagement (descending)
  const sortedPerformance = performance.sort((a, b) => b.engagement - a.engagement);
  
  sortedPerformance.forEach(item => {
    const performanceElement = document.createElement('div');
    performanceElement.className = 'performance-item';
    performanceElement.innerHTML = `
      <h4>${item.title}</h4>
      <span class="platform">${item.platform}</span>
      <span class="engagement">${item.engagement}</span>
      <span class="reach">${item.reach}</span>
    `;
    container.appendChild(performanceElement);
  });
};

// Auto-refresh and data management
window.startAutoRefresh = window.startAutoRefresh || function() {
  if (window.refreshInterval) {
    clearInterval(window.refreshInterval);
  }
  
  window.refreshInterval = setInterval(async () => {
    try {
      await window.loadOverviewData();
    } catch (error) {
      window.showNotification('Failed to refresh data', 'error');
    }
  }, 30000);
};

window.refreshData = window.refreshData || async function() {
  try {
    await Promise.all([
      window.loadOverviewData(),
      window.loadSystemHealth(),
      window.loadRecentActivity()
    ]);
    window.showNotification('Data refreshed successfully', 'success');
  } catch (error) {
    window.showNotification('Failed to refresh data', 'error');
  }
};

// Additional workflow functions
window.startWorkflow = window.startWorkflow || async function(workflowId) {
  try {
    const response = await fetch(`/api/v1/workflows/${workflowId}/start`, {
      method: 'POST'
    });
    if (response.ok) {
      window.showNotification('Workflow started successfully', 'success');
      await window.loadWorkflowData();
    } else {
      window.showNotification('Failed to start workflow', 'error');
    }
  } catch (error) {
    window.showNotification('Failed to start workflow', 'error');
  }
};

window.pauseWorkflow = window.pauseWorkflow || async function(workflowId) {
  try {
    const response = await fetch(`/api/v1/workflows/${workflowId}/pause`, {
      method: 'POST'
    });
    if (response.ok) {
      window.showNotification('Workflow paused successfully', 'success');
      await window.loadWorkflowData();
    } else {
      window.showNotification('Failed to pause workflow', 'error');
    }
  } catch (error) {
    window.showNotification('Failed to pause workflow', 'error');
  }
};

window.deleteWorkflow = window.deleteWorkflow || async function(workflowId) {
  if (!window.confirm('Are you sure you want to delete this workflow?')) {
    return;
  }
  
  try {
    const response = await fetch(`/api/v1/workflows/${workflowId}`, {
      method: 'DELETE'
    });
    if (response.ok) {
      window.showNotification('Workflow deleted successfully', 'success');
      await window.loadWorkflowData();
    } else {
      window.showNotification('Failed to delete workflow', 'error');
    }
  } catch (error) {
    window.showNotification('Failed to delete workflow', 'error');
  }
};

// Export logs functionality
window.exportLogs = window.exportLogs || async function() {
  try {
    const response = await fetch('/api/v1/monitoring/logs/export');
    if (response.ok) {
      const logData = await response.text();
      const blob = new Blob([logData], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = 'system-logs.txt';
      a.click();
      
      URL.revokeObjectURL(url);
    }
  } catch (error) {
    window.showNotification('Failed to export logs', 'error');
  }
};

module.exports = {};