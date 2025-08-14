/**
 * Analytics and Chart Tests
 * Tests for analytics data visualization and chart functionality
 */

describe('Analytics and Charts', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="analytics-section" class="content-section">
        <div class="analytics-grid">
          <div class="analytics-card">
            <h3>Performance Overview</h3>
            <canvas id="performanceChart"></canvas>
          </div>
          <div class="analytics-card">
            <h3>Platform Breakdown</h3>
            <canvas id="platformBreakdownChart"></canvas>
          </div>
          <div class="analytics-card">
            <h3>Engagement Metrics</h3>
            <div id="engagement-metrics" class="metrics-list"></div>
          </div>
          <div class="analytics-card">
            <h3>Content Performance</h3>
            <div id="content-performance" class="performance-list"></div>
          </div>
        </div>
      </div>
      <div id="overview-section" class="content-section">
        <div class="stats-grid">
          <div class="stat-card">
            <h3>Total Posts</h3>
            <span id="total-posts" class="stat-value">0</span>
          </div>
          <div class="stat-card">
            <h3>Active Platforms</h3>
            <span id="active-platforms" class="stat-value">0</span>
          </div>
          <div class="stat-card">
            <h3>Total Engagement</h3>
            <span id="total-engagement" class="stat-value">0</span>
          </div>
        </div>
        <canvas id="overviewChart"></canvas>
      </div>
    `;

    require('../static/js/dashboard.js');
  });

  describe('Chart Initialization', () => {
    test('should initialize charts', () => {
      window.initializeCharts();

      // Check that Chart constructor was called for each chart
      const chartIds = ['performanceChart', 'platformBreakdownChart', 'overviewChart'];
      chartIds.forEach(id => {
        expect(window.charts[id]).toBeDefined();
      });
    });

    test('should handle missing chart elements gracefully', () => {
      // Remove a chart element
      document.getElementById('performanceChart').remove();

      expect(() => {
        window.initializeCharts();
      }).not.toThrow();
    });

    test('should create different chart types', () => {
      window.initializeCharts();

      // Performance chart should be a line chart
      expect(window.charts.performanceChart.config?.type).toBe('line');
      
      // Platform breakdown should be a doughnut chart
      expect(window.charts.platformBreakdownChart.config?.type).toBe('doughnut');
      
      // Overview chart should be a bar chart
      expect(window.charts.overviewChart.config?.type).toBe('bar');
    });
  });

  describe('Chart Data Updates', () => {
    beforeEach(() => {
      window.initializeCharts();
    });

    test('should update content chart data', () => {
      const mockData = {
        labels: ['Instagram', 'YouTube', 'TikTok'],
        datasets: [{
          data: [45, 30, 25],
          backgroundColor: ['#E4405F', '#FF0000', '#000000']
        }]
      };

      window.updateContentChart(mockData);

      const chart = window.charts.platformBreakdownChart;
      expect(chart.data).toEqual(mockData);
      expect(chart.update).toHaveBeenCalled();
    });

    test('should update platform chart data', () => {
      const mockData = {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        datasets: [{
          label: 'Posts',
          data: [10, 15, 12, 18],
          borderColor: '#007bff'
        }]
      };

      window.updatePlatformChart(mockData);

      const chart = window.charts.performanceChart;
      expect(chart.data).toEqual(mockData);
      expect(chart.update).toHaveBeenCalled();
    });

    test('should handle empty chart data', () => {
      const emptyData = {
        labels: [],
        datasets: []
      };

      expect(() => {
        window.updateContentChart(emptyData);
        window.updatePlatformChart(emptyData);
      }).not.toThrow();
    });
  });

  describe('Analytics Data Loading', () => {
    test('should load analytics data successfully', async () => {
      const mockAnalyticsData = {
        overview: {
          totalPosts: 156,
          activePlatforms: 3,
          totalEngagement: 12450
        },
        performance: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr'],
          datasets: [{
            label: 'Engagement',
            data: [1200, 1900, 3000, 2500]
          }]
        },
        platforms: {
          instagram: { posts: 45, engagement: 5670 },
          youtube: { posts: 12, engagement: 8900 },
          tiktok: { posts: 23, engagement: 3400 }
        }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalyticsData
      });

      await window.loadAnalyticsData();

      expect(fetch).toHaveBeenCalledWith('/api/v1/analytics/overview');

      // Check that stat cards were updated
      expect(document.getElementById('total-posts').textContent).toBe('156');
      expect(document.getElementById('active-platforms').textContent).toBe('3');
      expect(document.getElementById('total-engagement').textContent).toBe('12450');
    });

    test('should handle analytics loading errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Analytics API error'));

      await window.loadAnalyticsData();

      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to load analytics data',
        'error'
      );
    });

    test('should load engagement metrics', async () => {
      const mockMetrics = [
        { platform: 'Instagram', likes: 1200, comments: 85, shares: 34 },
        { platform: 'YouTube', likes: 890, comments: 45, shares: 67 },
        { platform: 'TikTok', likes: 2300, comments: 120, shares: 89 }
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ metrics: mockMetrics })
      });

      await window.loadAnalytics();

      const metricsContainer = document.getElementById('engagement-metrics');
      expect(metricsContainer.children.length).toBe(3);

      mockMetrics.forEach((metric, index) => {
        const metricElement = metricsContainer.children[index];
        expect(metricElement.textContent).toContain(metric.platform);
        expect(metricElement.textContent).toContain(metric.likes.toString());
        expect(metricElement.textContent).toContain(metric.comments.toString());
        expect(metricElement.textContent).toContain(metric.shares.toString());
      });
    });
  });

  describe('Content Performance Display', () => {
    test('should display content performance data', () => {
      const mockPerformance = [
        { 
          id: 1, 
          title: 'Summer Campaign Post', 
          platform: 'Instagram',
          engagement: 1250,
          reach: 5600,
          publishDate: '2024-01-01T10:00:00Z'
        },
        { 
          id: 2, 
          title: 'Product Demo Video', 
          platform: 'YouTube',
          engagement: 890,
          reach: 3400,
          publishDate: '2024-01-02T14:30:00Z'
        }
      ];

      window.updateContentPerformance(mockPerformance);

      const performanceContainer = document.getElementById('content-performance');
      expect(performanceContainer.children.length).toBe(2);

      const firstItem = performanceContainer.children[0];
      expect(firstItem.textContent).toContain('Summer Campaign Post');
      expect(firstItem.textContent).toContain('Instagram');
      expect(firstItem.textContent).toContain('1250');
      expect(firstItem.textContent).toContain('5600');
    });

    test('should handle empty performance data', () => {
      window.updateContentPerformance([]);

      const performanceContainer = document.getElementById('content-performance');
      expect(performanceContainer.textContent).toContain('No performance data available');
    });

    test('should sort performance data by engagement', () => {
      const mockPerformance = [
        { id: 1, title: 'Low Engagement', engagement: 100 },
        { id: 2, title: 'High Engagement', engagement: 1000 },
        { id: 3, title: 'Medium Engagement', engagement: 500 }
      ];

      window.updateContentPerformance(mockPerformance);

      const performanceContainer = document.getElementById('content-performance');
      const items = Array.from(performanceContainer.children);
      
      // Should be sorted by engagement (descending)
      expect(items[0].textContent).toContain('High Engagement');
      expect(items[1].textContent).toContain('Medium Engagement');
      expect(items[2].textContent).toContain('Low Engagement');
    });
  });

  describe('Stat Card Updates', () => {
    test('should update stat cards with formatted numbers', () => {
      window.updateStatCard('total-posts', 1234567);
      expect(document.getElementById('total-posts').textContent).toBe('1,234,567');

      window.updateStatCard('total-engagement', 45678);
      expect(document.getElementById('total-engagement').textContent).toBe('45,678');
    });

    test('should handle zero values', () => {
      window.updateStatCard('total-posts', 0);
      expect(document.getElementById('total-posts').textContent).toBe('0');
    });

    test('should handle decimal values', () => {
      window.updateStatCard('engagement-rate', 23.45);
      expect(document.getElementById('engagement-rate').textContent).toBe('23.45');
    });

    test('should animate stat card updates', () => {
      const statElement = document.getElementById('total-posts');
      
      window.updateStatCard('total-posts', 100);
      
      // Check for animation class
      expect(statElement.classList.contains('updating')).toBe(true);
      
      // After animation completes
      jest.advanceTimersByTime(300);
      expect(statElement.classList.contains('updating')).toBe(false);
    });
  });

  describe('Chart Responsive Behavior', () => {
    beforeEach(() => {
      window.initializeCharts();
    });

    test('should resize charts on window resize', () => {
      const resizeEvent = new Event('resize');
      window.dispatchEvent(resizeEvent);

      Object.values(window.charts).forEach(chart => {
        expect(chart.resize).toHaveBeenCalled();
      });
    });

    test('should handle chart resize errors gracefully', () => {
      // Mock a chart with a failing resize method
      window.charts.performanceChart.resize = jest.fn(() => {
        throw new Error('Resize failed');
      });

      const resizeEvent = new Event('resize');
      
      expect(() => {
        window.dispatchEvent(resizeEvent);
      }).not.toThrow();
    });
  });

  describe('Real-time Data Updates', () => {
    test('should refresh analytics data automatically', async () => {
      window.loadAnalyticsData = jest.fn().mockResolvedValue();
      
      window.startAutoRefresh();
      
      // Fast-forward timer
      jest.advanceTimersByTime(30000); // 30 seconds
      
      expect(window.loadAnalyticsData).toHaveBeenCalled();
    });

    test('should stop auto-refresh when switching sections', () => {
      window.startAutoRefresh();
      
      // Verify interval was set
      expect(setInterval).toHaveBeenCalled();
      
      window.switchSection('content');
      
      // Should clear the interval
      expect(clearInterval).toHaveBeenCalled();
    });

    test('should handle auto-refresh errors', async () => {
      window.loadAnalyticsData = jest.fn().mockRejectedValue(new Error('Refresh failed'));
      
      window.startAutoRefresh();
      jest.advanceTimersByTime(30000);
      
      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to refresh data',
        'error'
      );
    });
  });
});