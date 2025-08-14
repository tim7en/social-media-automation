/**
 * System Monitoring and Health Tests
 * Tests for system health monitoring, logging, and performance tracking
 */

describe('System Monitoring and Health', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="monitoring-section" class="content-section">
        <div class="monitoring-grid">
          <div class="health-card">
            <h3>System Health</h3>
            <div id="system-health" class="health-indicators">
              <div class="health-item" id="api-health">
                <span class="health-label">API Server</span>
                <span class="health-status">Unknown</span>
              </div>
              <div class="health-item" id="database-health">
                <span class="health-label">Database</span>
                <span class="health-status">Unknown</span>
              </div>
              <div class="health-item" id="redis-health">
                <span class="health-label">Redis Cache</span>
                <span class="health-status">Unknown</span>
              </div>
            </div>
          </div>
          <div class="health-card">
            <h3>Resource Usage</h3>
            <div id="resource-usage">
              <canvas id="resourceChart"></canvas>
            </div>
          </div>
          <div class="health-card">
            <h3>Active Tasks</h3>
            <div id="active-tasks" class="tasks-list"></div>
          </div>
          <div class="health-card">
            <h3>System Logs</h3>
            <div id="system-logs" class="logs-container">
              <div class="logs-controls">
                <button onclick="refreshLogs()">Refresh</button>
                <button onclick="clearLogs()">Clear</button>
                <button onclick="exportLogs()">Export</button>
              </div>
              <div id="logs-content"></div>
            </div>
          </div>
        </div>
      </div>
      <div id="notifications" class="notifications-container"></div>
    `;

    require('../static/js/dashboard.js');
  });

  describe('System Health Monitoring', () => {
    test('should load system health data', async () => {
      const mockHealthData = {
        api: { status: 'healthy', responseTime: 45 },
        database: { status: 'healthy', connections: 5 },
        redis: { status: 'warning', memory: '85%' },
        overall: 'healthy'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealthData
      });

      await window.loadSystemHealth();

      expect(fetch).toHaveBeenCalledWith('/api/v1/health');

      // Check health indicators were updated
      const apiHealth = document.getElementById('api-health');
      expect(apiHealth.querySelector('.health-status').textContent).toBe('Healthy');
      expect(apiHealth.classList.contains('healthy')).toBe(true);

      const databaseHealth = document.getElementById('database-health');
      expect(databaseHealth.querySelector('.health-status').textContent).toBe('Healthy');

      const redisHealth = document.getElementById('redis-health');
      expect(redisHealth.querySelector('.health-status').textContent).toBe('Warning');
      expect(redisHealth.classList.contains('warning')).toBe(true);
    });

    test('should handle unhealthy system components', async () => {
      const mockHealthData = {
        api: { status: 'error', error: 'Connection timeout' },
        database: { status: 'error', error: 'Connection failed' },
        redis: { status: 'healthy' },
        overall: 'error'
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealthData
      });

      await window.loadSystemHealth();

      const apiHealth = document.getElementById('api-health');
      expect(apiHealth.querySelector('.health-status').textContent).toBe('Error');
      expect(apiHealth.classList.contains('error')).toBe(true);

      const databaseHealth = document.getElementById('database-health');
      expect(databaseHealth.querySelector('.health-status').textContent).toBe('Error');
      expect(databaseHealth.classList.contains('error')).toBe(true);
    });

    test('should handle health check errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Health check failed'));

      await window.loadSystemHealth();

      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to load system health',
        'error'
      );

      // All health indicators should show unknown status
      const healthItems = document.querySelectorAll('.health-item');
      healthItems.forEach(item => {
        expect(item.querySelector('.health-status').textContent).toBe('Unknown');
        expect(item.classList.contains('unknown')).toBe(true);
      });
    });

    test('should auto-refresh health data', async () => {
      window.loadSystemHealth = jest.fn().mockResolvedValue();
      
      window.startHealthMonitoring();
      
      jest.advanceTimersByTime(10000); // 10 seconds
      
      expect(window.loadSystemHealth).toHaveBeenCalled();
    });
  });

  describe('Resource Usage Monitoring', () => {
    test('should display resource usage chart', async () => {
      const mockResourceData = {
        cpu: { current: 45, average: 38, max: 85 },
        memory: { current: 68, available: 32, total: 100 },
        disk: { used: 45, available: 55, total: 100 },
        network: { incoming: 1250, outgoing: 890 }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResourceData
      });

      window.initializeCharts();
      await window.loadResourceUsage();

      expect(fetch).toHaveBeenCalledWith('/api/v1/monitoring/resources');

      const resourceChart = window.charts.resourceChart;
      expect(resourceChart).toBeDefined();
      expect(resourceChart.data.datasets.length).toBeGreaterThan(0);
    });

    test('should update resource chart with real-time data', () => {
      window.initializeCharts();
      
      const resourceData = {
        labels: ['CPU', 'Memory', 'Disk'],
        datasets: [{
          label: 'Usage %',
          data: [45, 68, 45],
          backgroundColor: ['#ff6b6b', '#4ecdc4', '#45b7d1']
        }]
      };

      window.updateResourceChart(resourceData);

      const chart = window.charts.resourceChart;
      expect(chart.data).toEqual(resourceData);
      expect(chart.update).toHaveBeenCalled();
    });

    test('should handle high resource usage alerts', async () => {
      const highUsageData = {
        cpu: { current: 95, threshold: 90 },
        memory: { current: 88, threshold: 85 },
        disk: { current: 92, threshold: 90 }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => highUsageData
      });

      await window.loadResourceUsage();

      expect(window.showNotification).toHaveBeenCalledWith(
        'High CPU usage detected (95%)',
        'warning'
      );
      expect(window.showNotification).toHaveBeenCalledWith(
        'High memory usage detected (88%)',
        'warning'
      );
      expect(window.showNotification).toHaveBeenCalledWith(
        'High disk usage detected (92%)',
        'warning'
      );
    });
  });

  describe('Active Tasks Monitoring', () => {
    test('should display active tasks', () => {
      const mockTasks = [
        {
          id: 1,
          name: 'Content Generation',
          status: 'running',
          progress: 75,
          startTime: '2024-01-01T10:00:00Z'
        },
        {
          id: 2,
          name: 'Instagram Upload',
          status: 'queued',
          progress: 0,
          queuePosition: 3
        },
        {
          id: 3,
          name: 'Analytics Sync',
          status: 'completed',
          progress: 100,
          completedTime: '2024-01-01T10:05:00Z'
        }
      ];

      window.updateActiveTasks(mockTasks);

      const tasksContainer = document.getElementById('active-tasks');
      expect(tasksContainer.children.length).toBe(3);

      // Check running task
      const runningTask = tasksContainer.children[0];
      expect(runningTask.textContent).toContain('Content Generation');
      expect(runningTask.textContent).toContain('running');
      expect(runningTask.textContent).toContain('75%');
      expect(runningTask.classList.contains('running')).toBe(true);

      // Check queued task
      const queuedTask = tasksContainer.children[1];
      expect(queuedTask.textContent).toContain('Instagram Upload');
      expect(queuedTask.textContent).toContain('queued');
      expect(queuedTask.classList.contains('queued')).toBe(true);

      // Check completed task
      const completedTask = tasksContainer.children[2];
      expect(completedTask.textContent).toContain('Analytics Sync');
      expect(completedTask.textContent).toContain('completed');
      expect(completedTask.classList.contains('completed')).toBe(true);
    });

    test('should handle empty tasks list', () => {
      window.updateActiveTasks([]);

      const tasksContainer = document.getElementById('active-tasks');
      expect(tasksContainer.textContent).toContain('No active tasks');
    });

    test('should update task progress bars', () => {
      const task = {
        id: 1,
        name: 'Test Task',
        status: 'running',
        progress: 60
      };

      window.updateActiveTasks([task]);

      const tasksContainer = document.getElementById('active-tasks');
      const progressBar = tasksContainer.querySelector('.progress-bar');
      expect(progressBar.style.width).toBe('60%');
    });
  });

  describe('System Logs Management', () => {
    test('should refresh logs', async () => {
      const mockLogs = [
        {
          timestamp: '2024-01-01T10:00:00Z',
          level: 'info',
          message: 'System started successfully',
          component: 'api'
        },
        {
          timestamp: '2024-01-01T10:01:00Z',
          level: 'warning',
          message: 'High memory usage detected',
          component: 'monitor'
        },
        {
          timestamp: '2024-01-01T10:02:00Z',
          level: 'error',
          message: 'Failed to connect to external API',
          component: 'platforms'
        }
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ logs: mockLogs })
      });

      await window.refreshLogs();

      expect(fetch).toHaveBeenCalledWith('/api/v1/monitoring/logs');

      const logsContent = document.getElementById('logs-content');
      expect(logsContent.children.length).toBe(3);

      // Check log entries
      mockLogs.forEach((log, index) => {
        const logEntry = logsContent.children[index];
        expect(logEntry.textContent).toContain(log.message);
        expect(logEntry.classList.contains(log.level)).toBe(true);
      });
    });

    test('should clear logs', async () => {
      // Add some logs first
      const logsContent = document.getElementById('logs-content');
      logsContent.innerHTML = '<div class="log-entry">Test log</div>';

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ cleared: true })
      });

      await window.clearLogs();

      expect(fetch).toHaveBeenCalledWith('/api/v1/monitoring/logs', {
        method: 'DELETE'
      });

      expect(logsContent.innerHTML).toBe('');
      expect(window.showNotification).toHaveBeenCalledWith(
        'Logs cleared successfully',
        'success'
      );
    });

    test('should export logs', async () => {
      const mockLogData = 'log1\nlog2\nlog3';
      
      fetch.mockResolvedValueOnce({
        ok: true,
        text: async () => mockLogData
      });

      // Mock URL.createObjectURL and document.createElement
      global.URL.createObjectURL = jest.fn(() => 'blob:url');
      const mockAnchor = {
        href: '',
        download: '',
        click: jest.fn()
      };
      document.createElement = jest.fn(() => mockAnchor);

      await window.exportLogs();

      expect(fetch).toHaveBeenCalledWith('/api/v1/monitoring/logs/export');
      expect(mockAnchor.download).toBe('system-logs.txt');
      expect(mockAnchor.click).toHaveBeenCalled();
    });

    test('should filter logs by level', () => {
      const allLogs = [
        { level: 'info', message: 'Info message' },
        { level: 'warning', message: 'Warning message' },
        { level: 'error', message: 'Error message' }
      ];

      window.updateLogs(allLogs);

      // Filter by error level
      window.filterLogs('error');

      const logsContent = document.getElementById('logs-content');
      const visibleLogs = Array.from(logsContent.children).filter(
        log => log.style.display !== 'none'
      );
      
      expect(visibleLogs.length).toBe(1);
      expect(visibleLogs[0].textContent).toContain('Error message');
    });

    test('should search logs', () => {
      const logs = [
        { level: 'info', message: 'User login successful' },
        { level: 'info', message: 'Content generated' },
        { level: 'error', message: 'Login failed' }
      ];

      window.updateLogs(logs);
      window.searchLogs('login');

      const logsContent = document.getElementById('logs-content');
      const visibleLogs = Array.from(logsContent.children).filter(
        log => log.style.display !== 'none'
      );
      
      expect(visibleLogs.length).toBe(2);
      expect(visibleLogs[0].textContent).toContain('User login successful');
      expect(visibleLogs[1].textContent).toContain('Login failed');
    });
  });

  describe('Performance Metrics', () => {
    test('should display performance metrics', async () => {
      const mockMetrics = {
        responseTime: {
          average: 245,
          p95: 450,
          p99: 890
        },
        throughput: {
          requestsPerSecond: 125,
          requestsPerMinute: 7500
        },
        errors: {
          rate: 0.02,
          count: 15
        }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetrics
      });

      await window.loadPerformanceMetrics();

      expect(fetch).toHaveBeenCalledWith('/api/v1/monitoring/performance');

      // Check metrics display
      expect(document.getElementById('avg-response-time').textContent).toBe('245ms');
      expect(document.getElementById('requests-per-second').textContent).toBe('125');
      expect(document.getElementById('error-rate').textContent).toBe('2.0%');
    });

    test('should update performance charts', () => {
      const performanceData = {
        labels: ['00:00', '00:05', '00:10', '00:15'],
        datasets: [{
          label: 'Response Time (ms)',
          data: [250, 235, 280, 245],
          borderColor: '#007bff'
        }]
      };

      window.initializeCharts();
      window.updatePerformanceChart(performanceData);

      const chart = window.charts.performanceChart;
      expect(chart.data).toEqual(performanceData);
      expect(chart.update).toHaveBeenCalled();
    });
  });

  describe('Monitoring Data Loading', () => {
    test('should load all monitoring data', async () => {
      window.loadSystemHealth = jest.fn().mockResolvedValue();
      window.loadResourceUsage = jest.fn().mockResolvedValue();
      window.loadActiveTasks = jest.fn().mockResolvedValue();
      window.refreshLogs = jest.fn().mockResolvedValue();

      await window.loadMonitoringData();

      expect(window.loadSystemHealth).toHaveBeenCalled();
      expect(window.loadResourceUsage).toHaveBeenCalled();
      expect(window.loadActiveTasks).toHaveBeenCalled();
      expect(window.refreshLogs).toHaveBeenCalled();
    });

    test('should handle monitoring data loading errors gracefully', async () => {
      window.loadSystemHealth = jest.fn().mockRejectedValue(new Error('Health check failed'));
      window.loadResourceUsage = jest.fn().mockResolvedValue();
      window.loadActiveTasks = jest.fn().mockResolvedValue();
      window.refreshLogs = jest.fn().mockResolvedValue();

      await window.loadMonitoringData();

      // Should continue loading other data even if one fails
      expect(window.loadResourceUsage).toHaveBeenCalled();
      expect(window.loadActiveTasks).toHaveBeenCalled();
      expect(window.refreshLogs).toHaveBeenCalled();
    });
  });
});