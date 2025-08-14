/**
 * Dashboard Integration Tests
 * End-to-end tests for complete user workflows and interactions
 */

describe('Dashboard Integration Tests', () => {
  beforeEach(() => {
    // Set up complete dashboard HTML
    document.body.innerHTML = `
      <div class="dashboard-container">
        <nav class="sidebar">
          <div class="sidebar-header">
            <h2><i class="fas fa-robot"></i> SM Automation</h2>
            <p>Debug Dashboard</p>
          </div>
          <ul class="nav-menu">
            <li class="nav-item active" data-section="overview">
              <i class="fas fa-tachometer-alt"></i>
              <span>Overview</span>
            </li>
            <li class="nav-item" data-section="content">
              <i class="fas fa-magic"></i>
              <span>Content Generation</span>
            </li>
            <li class="nav-item" data-section="workflows">
              <i class="fas fa-project-diagram"></i>
              <span>Workflows</span>
            </li>
            <li class="nav-item" data-section="platforms">
              <i class="fas fa-share-alt"></i>
              <span>Platforms</span>
            </li>
            <li class="nav-item" data-section="analytics">
              <i class="fas fa-chart-line"></i>
              <span>Analytics</span>
            </li>
            <li class="nav-item" data-section="api-testing">
              <i class="fas fa-code"></i>
              <span>API Testing</span>
            </li>
            <li class="nav-item" data-section="monitoring">
              <i class="fas fa-heartbeat"></i>
              <span>System Health</span>
            </li>
          </ul>
        </nav>
        
        <main class="main-content">
          <div class="section-header">
            <h1 id="section-title">System Overview</h1>
            <button onclick="refreshData()" class="btn btn-secondary">
              <i class="fas fa-sync"></i> Refresh
            </button>
          </div>
          
          <!-- Overview Section -->
          <section id="overview-section" class="content-section active">
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
          </section>
          
          <!-- Content Section -->
          <section id="content-section" class="content-section">
            <div class="content-controls">
              <select id="content-type">
                <option value="post">Post</option>
                <option value="story">Story</option>
                <option value="video">Video</option>
              </select>
              <select id="target-platform">
                <option value="instagram">Instagram</option>
                <option value="youtube">YouTube</option>
                <option value="tiktok">TikTok</option>
              </select>
              <button onclick="generateTestContent()">Generate Content</button>
            </div>
          </section>
          
          <!-- API Testing Section -->
          <section id="api-testing-section" class="content-section">
            <div class="api-controls">
              <select id="api-method">
                <option value="GET">GET</option>
                <option value="POST">POST</option>
              </select>
              <input type="text" id="api-endpoint" placeholder="/health">
              <button onclick="executeApiTest()">Execute</button>
            </div>
            <pre id="api-response"></pre>
          </section>
          
          <!-- Other sections would be here -->
          <section id="workflows-section" class="content-section"></section>
          <section id="platforms-section" class="content-section"></section>
          <section id="analytics-section" class="content-section"></section>
          <section id="monitoring-section" class="content-section"></section>
        </main>
      </div>
      
      <div id="notifications" class="notifications-container"></div>
      <div id="modal" class="modal">
        <div class="modal-content">
          <span class="close" onclick="closeModal()">&times;</span>
          <div id="modal-body"></div>
        </div>
      </div>
    `;

    require('../static/js/dashboard.js');
  });

  describe('Complete User Workflows', () => {
    test('should complete content generation workflow', async () => {
      // Start with overview section
      expect(document.querySelector('.nav-item.active').getAttribute('data-section')).toBe('overview');
      
      // Navigate to content section
      window.switchSection('content');
      expect(document.querySelector('.content-section.active').id).toBe('content-section');
      
      // Configure content generation
      document.getElementById('content-type').value = 'post';
      document.getElementById('target-platform').value = 'instagram';
      
      // Mock API responses
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ task_id: 123, status: 'started' })
      });
      
      // Generate content
      const promise = window.generateTestContent();
      jest.advanceTimersByTime(2000);
      await promise;
      
      // Verify notifications
      expect(window.showNotification).toHaveBeenCalledWith(
        'Generating post content for instagram...',
        'info'
      );
      expect(window.showNotification).toHaveBeenCalledWith(
        'Test content generation started successfully',
        'success'
      );
    });

    test('should complete API testing workflow', async () => {
      // Navigate to API testing section
      window.switchSection('api-testing');
      
      // Set up API test
      document.getElementById('api-method').value = 'GET';
      document.getElementById('api-endpoint').value = '/health';
      
      const mockResponse = { status: 'healthy', timestamp: '2024-01-01T10:00:00Z' };
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });
      
      // Execute test
      await window.executeApiTest();
      
      // Verify response display
      const responseElement = document.getElementById('api-response');
      expect(responseElement.textContent).toBe(JSON.stringify(mockResponse, null, 2));
      
      // Verify notification
      expect(window.showNotification).toHaveBeenCalledWith(
        'API request successful',
        'success'
      );
    });

    test('should handle authentication workflow', async () => {
      // Set up authentication token
      localStorage.setItem('auth_token', 'valid-token');
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ username: 'testuser', id: 1 })
      });
      
      // Check authentication
      await window.checkAuthStatus();
      
      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/me', {
        headers: { 'Authorization': 'Bearer valid-token' }
      });
      
      // Now make an authenticated API request
      window.switchSection('api-testing');
      document.getElementById('api-endpoint').value = '/api/v1/protected';
      
      fetch.mockClear();
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'protected data' })
      });
      
      await window.executeApiTest();
      
      expect(fetch).toHaveBeenCalledWith('/api/v1/protected', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid-token'
        }
      });
    });
  });

  describe('Error Handling Workflows', () => {
    test('should handle API failure gracefully', async () => {
      window.switchSection('api-testing');
      
      document.getElementById('api-endpoint').value = '/api/v1/fail';
      
      fetch.mockRejectedValueOnce(new Error('Network error'));
      
      await window.executeApiTest();
      
      const responseElement = document.getElementById('api-response');
      expect(responseElement.textContent).toContain('Error: Network error');
      
      expect(window.showNotification).toHaveBeenCalledWith(
        'API request failed',
        'error'
      );
    });

    test('should handle authentication failure', async () => {
      localStorage.setItem('auth_token', 'invalid-token');
      
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      });
      
      await window.checkAuthStatus();
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
    });

    test('should handle content generation failure', async () => {
      window.switchSection('content');
      
      window.loadContentData = jest.fn().mockRejectedValue(new Error('Load failed'));
      
      const promise = window.generateTestContent();
      jest.advanceTimersByTime(2000);
      await promise;
      
      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to generate test content',
        'error'
      );
    });
  });

  describe('Data Refresh Workflows', () => {
    test('should refresh all data when refresh button is clicked', async () => {
      // Mock all data loading functions
      window.loadOverviewData = jest.fn().mockResolvedValue();
      window.loadSystemHealth = jest.fn().mockResolvedValue();
      window.loadRecentActivity = jest.fn().mockResolvedValue();
      
      await window.refreshData();
      
      expect(window.loadOverviewData).toHaveBeenCalled();
      expect(window.loadSystemHealth).toHaveBeenCalled();
      expect(window.loadRecentActivity).toHaveBeenCalled();
      
      expect(window.showNotification).toHaveBeenCalledWith(
        'Data refreshed successfully',
        'success'
      );
    });

    test('should auto-refresh data in background', async () => {
      window.loadOverviewData = jest.fn().mockResolvedValue();
      
      window.startAutoRefresh();
      
      // Fast-forward time to trigger auto-refresh
      jest.advanceTimersByTime(30000);
      
      expect(window.loadOverviewData).toHaveBeenCalled();
    });
  });

  describe('Section Navigation Workflows', () => {
    test('should navigate through all sections and load appropriate data', async () => {
      const sections = [
        { name: 'overview', title: 'System Overview' },
        { name: 'content', title: 'Content Generation' },
        { name: 'workflows', title: 'Workflow Management' },
        { name: 'platforms', title: 'Platform Integration' },
        { name: 'analytics', title: 'Analytics & Insights' },
        { name: 'api-testing', title: 'API Testing' },
        { name: 'monitoring', title: 'System Health' }
      ];

      // Mock data loading functions
      window.loadOverviewData = jest.fn().mockResolvedValue();
      window.loadContentData = jest.fn().mockResolvedValue();
      window.loadWorkflowData = jest.fn().mockResolvedValue();
      window.loadPlatformData = jest.fn().mockResolvedValue();
      window.loadAnalyticsData = jest.fn().mockResolvedValue();
      window.loadMonitoringData = jest.fn().mockResolvedValue();

      for (const section of sections) {
        window.switchSection(section.name);
        
        // Check navigation state
        const activeNav = document.querySelector('.nav-item.active');
        expect(activeNav.getAttribute('data-section')).toBe(section.name);
        
        // Check content section state
        const activeSection = document.querySelector('.content-section.active');
        expect(activeSection.id).toBe(`${section.name}-section`);
        
        // Check title
        expect(document.getElementById('section-title').textContent).toBe(section.title);
      }
      
      // Verify data loading functions were called
      expect(window.loadOverviewData).toHaveBeenCalled();
      expect(window.loadContentData).toHaveBeenCalled();
      expect(window.loadWorkflowData).toHaveBeenCalled();
      expect(window.loadPlatformData).toHaveBeenCalled();
      expect(window.loadAnalyticsData).toHaveBeenCalled();
      expect(window.loadMonitoringData).toHaveBeenCalled();
    });

    test('should handle navigation with keyboard shortcuts', () => {
      // Simulate keyboard navigation
      const event = new KeyboardEvent('keydown', { key: 'ArrowDown' });
      document.dispatchEvent(event);
      
      // Should move to next section
      const activeNav = document.querySelector('.nav-item.active');
      expect(activeNav.getAttribute('data-section')).toBe('content');
    });
  });

  describe('Modal Workflows', () => {
    test('should open and close modal properly', () => {
      const modal = document.getElementById('modal');
      const modalBody = document.getElementById('modal-body');
      
      // Open modal
      modal.style.display = 'block';
      modalBody.innerHTML = '<p>Test content</p>';
      
      expect(modal.style.display).toBe('block');
      expect(modalBody.innerHTML).toBe('<p>Test content</p>');
      
      // Close modal
      window.closeModal();
      
      expect(modal.style.display).toBe('none');
      expect(modalBody.innerHTML).toBe('');
    });

    test('should close modal when clicking outside', () => {
      const modal = document.getElementById('modal');
      modal.style.display = 'block';
      
      const clickEvent = new MouseEvent('click', { target: modal });
      Object.defineProperty(clickEvent, 'target', { value: modal, enumerable: true });
      
      window.dispatchEvent(clickEvent);
      
      expect(modal.style.display).toBe('none');
    });
  });

  describe('Notification System Workflows', () => {
    test('should show multiple notifications and manage them properly', () => {
      window.showNotification('First message', 'info');
      window.showNotification('Second message', 'success');
      window.showNotification('Third message', 'error');
      
      const notifications = document.querySelectorAll('.notification');
      expect(notifications.length).toBe(3);
      
      // Check notification types
      expect(notifications[0].classList.contains('info')).toBe(true);
      expect(notifications[1].classList.contains('success')).toBe(true);
      expect(notifications[2].classList.contains('error')).toBe(true);
    });

    test('should auto-remove notifications after timeout', () => {
      jest.useFakeTimers();
      
      window.showNotification('Test message', 'info');
      
      let notifications = document.querySelectorAll('.notification');
      expect(notifications.length).toBe(1);
      
      // Fast-forward time
      jest.advanceTimersByTime(5000);
      
      notifications = document.querySelectorAll('.notification');
      expect(notifications.length).toBe(0);
      
      jest.useRealTimers();
    });
  });

  describe('Performance and Responsiveness', () => {
    test('should handle rapid section switching', async () => {
      const sections = ['overview', 'content', 'analytics', 'monitoring'];
      
      // Mock data loading to be fast
      window.loadOverviewData = jest.fn().mockResolvedValue();
      window.loadContentData = jest.fn().mockResolvedValue();
      window.loadAnalyticsData = jest.fn().mockResolvedValue();
      window.loadMonitoringData = jest.fn().mockResolvedValue();
      
      // Rapidly switch sections
      for (let i = 0; i < 10; i++) {
        const section = sections[i % sections.length];
        window.switchSection(section);
      }
      
      // Should end up on the last section without errors
      const activeSection = document.querySelector('.content-section.active');
      expect(activeSection.id).toBe('content-section'); // Last section in the cycle
    });

    test('should handle multiple simultaneous API requests', async () => {
      const promises = [];
      
      // Set up multiple endpoints
      const endpoints = ['/health', '/api/v1/status', '/api/v1/analytics'];
      
      fetch.mockImplementation((url) => {
        return Promise.resolve({
          ok: true,
          json: async () => ({ endpoint: url, status: 'ok' })
        });
      });
      
      window.switchSection('api-testing');
      
      // Execute multiple API tests simultaneously
      for (const endpoint of endpoints) {
        document.getElementById('api-endpoint').value = endpoint;
        promises.push(window.executeApiTest());
      }
      
      await Promise.all(promises);
      
      expect(fetch).toHaveBeenCalledTimes(3);
    });
  });

  describe('Accessibility and User Experience', () => {
    test('should maintain focus management during navigation', () => {
      const firstNavItem = document.querySelector('.nav-item[data-section="overview"]');
      firstNavItem.focus();
      
      expect(document.activeElement).toBe(firstNavItem);
      
      window.switchSection('content');
      
      const secondNavItem = document.querySelector('.nav-item[data-section="content"]');
      expect(secondNavItem.classList.contains('active')).toBe(true);
    });

    test('should provide keyboard navigation support', () => {
      // Test Tab navigation
      const navItems = document.querySelectorAll('.nav-item');
      navItems.forEach(item => {
        expect(item.getAttribute('tabindex')).not.toBe('-1');
      });
    });

    test('should show loading states during async operations', async () => {
      window.switchSection('content');
      
      // Mock a slow loading operation
      window.loadContentData = jest.fn(() => new Promise(resolve => {
        setTimeout(resolve, 1000);
      }));
      
      const loadingPromise = window.loadSectionData('content');
      
      // Should show loading indicator
      expect(document.querySelector('.loading-indicator')).toBeTruthy();
      
      jest.advanceTimersByTime(1000);
      await loadingPromise;
      
      // Loading indicator should be gone
      expect(document.querySelector('.loading-indicator')).toBeFalsy();
    });
  });
});