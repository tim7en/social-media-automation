/**
 * Core Dashboard Functionality Tests
 * Tests for the main dashboard initialization, navigation, and utility functions
 */

describe('Dashboard Core Functionality', () => {
  let mockHTML;

  beforeEach(() => {
    // Set up basic HTML structure
    mockHTML = `
      <div class="dashboard-container">
        <nav class="sidebar">
          <ul class="nav-menu">
            <li class="nav-item active" data-section="overview">Overview</li>
            <li class="nav-item" data-section="content">Content Generation</li>
            <li class="nav-item" data-section="workflows">Workflows</li>
            <li class="nav-item" data-section="platforms">Platforms</li>
            <li class="nav-item" data-section="analytics">Analytics</li>
            <li class="nav-item" data-section="api-testing">API Testing</li>
            <li class="nav-item" data-section="monitoring">System Health</li>
          </ul>
        </nav>
        <main>
          <h1 id="section-title">Dashboard</h1>
          <section id="overview-section" class="content-section active"></section>
          <section id="content-section" class="content-section"></section>
          <section id="workflows-section" class="content-section"></section>
          <section id="platforms-section" class="content-section"></section>
          <section id="analytics-section" class="content-section"></section>
          <section id="api-testing-section" class="content-section"></section>
          <section id="monitoring-section" class="content-section"></section>
        </main>
        <div id="notifications" class="notifications-container"></div>
        <div id="modal" class="modal">
          <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modal-body"></div>
          </div>
        </div>
      </div>
    `;
    document.body.innerHTML = mockHTML;

    // Load the dashboard script
    require('../static/js/dashboard.js');
  });

  describe('Dashboard Initialization', () => {
    test('should initialize dashboard components', () => {
      expect(typeof window.initializeDashboard).toBe('function');
      
      // Mock Chart constructor calls
      window.initializeDashboard();
      
      expect(console.log).toHaveBeenCalledWith('Initializing Social Media Automation Dashboard...');
    });

    test('should setup event listeners', () => {
      expect(typeof window.setupEventListeners).toBe('function');
      
      window.setupEventListeners();
      
      // Check that window event listener was set up
      expect(window.addEventListener).toHaveBeenCalled();
    });

    test('should check authentication status', async () => {
      localStorage.setItem('auth_token', 'mock-token');
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ username: 'testuser', id: 1 })
      });

      await window.checkAuthStatus();
      
      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/me', {
        headers: { 'Authorization': 'Bearer mock-token' }
      });
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
  });

  describe('Section Navigation', () => {
    test('should switch to different sections', () => {
      window.switchSection('content');
      
      // Check navigation active state
      const activeNav = document.querySelector('.nav-item.active');
      expect(activeNav.getAttribute('data-section')).toBe('content');
      
      // Check content section active state
      const activeSection = document.querySelector('.content-section.active');
      expect(activeSection.id).toBe('content-section');
      
      // Check title update
      expect(document.getElementById('section-title').textContent).toBe('Content Generation');
    });

    test('should update section title correctly for all sections', () => {
      const sections = [
        { name: 'overview', title: 'System Overview' },
        { name: 'content', title: 'Content Generation' },
        { name: 'workflows', title: 'Workflow Management' },
        { name: 'platforms', title: 'Platform Integration' },
        { name: 'analytics', title: 'Analytics & Insights' },
        { name: 'api-testing', title: 'API Testing' },
        { name: 'monitoring', title: 'System Health' }
      ];

      sections.forEach(section => {
        window.switchSection(section.name);
        expect(document.getElementById('section-title').textContent).toBe(section.title);
      });
    });

    test('should handle unknown section gracefully', () => {
      window.switchSection('unknown');
      expect(document.getElementById('section-title').textContent).toBe('Dashboard');
    });
  });

  describe('Notification System', () => {
    test('should show notifications', () => {
      const notificationsContainer = document.getElementById('notifications');
      
      window.showNotification('Test message', 'success');
      
      const notification = notificationsContainer.querySelector('.notification');
      expect(notification).toBeTruthy();
      expect(notification.textContent).toContain('Test message');
      expect(notification.classList.contains('success')).toBe(true);
    });

    test('should handle different notification types', () => {
      const types = ['success', 'error', 'warning', 'info'];
      
      types.forEach(type => {
        window.showNotification(`Test ${type} message`, type);
        const notification = document.querySelector(`.notification.${type}`);
        expect(notification).toBeTruthy();
      });
    });

    test('should auto-remove notifications after timeout', () => {
      jest.useFakeTimers();
      
      window.showNotification('Test message', 'info');
      
      // Fast-forward time
      jest.advanceTimersByTime(5000);
      
      const notification = document.querySelector('.notification');
      expect(notification).toBeFalsy();
      
      jest.useRealTimers();
    });
  });

  describe('Modal Management', () => {
    test('should close modal', () => {
      const modal = document.getElementById('modal');
      modal.style.display = 'block';
      
      window.closeModal();
      
      expect(modal.style.display).toBe('none');
    });

    test('should clear modal content when closing', () => {
      const modalBody = document.getElementById('modal-body');
      modalBody.innerHTML = '<p>Test content</p>';
      
      window.closeModal();
      
      expect(modalBody.innerHTML).toBe('');
    });
  });

  describe('Utility Functions', () => {
    test('should generate random data', () => {
      const data = window.generateRandomData(5, 10, 20);
      
      expect(data).toHaveLength(5);
      data.forEach(value => {
        expect(value).toBeGreaterThanOrEqual(10);
        expect(value).toBeLessThanOrEqual(20);
      });
    });

    test('should update stat cards', () => {
      document.body.innerHTML += '<div id="test-stat" class="stat-value">0</div>';
      
      window.updateStatCard('test-stat', 42);
      
      const statElement = document.getElementById('test-stat');
      expect(statElement.textContent).toBe('42');
    });

    test('should handle missing stat card gracefully', () => {
      expect(() => {
        window.updateStatCard('non-existent', 42);
      }).not.toThrow();
    });
  });

  describe('Data Loading Functions', () => {
    test('should load section data based on section type', async () => {
      // Mock the individual load functions
      window.loadOverviewData = jest.fn().mockResolvedValue();
      window.loadContentData = jest.fn().mockResolvedValue();
      window.loadWorkflowData = jest.fn().mockResolvedValue();
      
      await window.loadSectionData('overview');
      expect(window.loadOverviewData).toHaveBeenCalled();
      
      await window.loadSectionData('content');
      expect(window.loadContentData).toHaveBeenCalled();
      
      await window.loadSectionData('workflows');
      expect(window.loadWorkflowData).toHaveBeenCalled();
    });

    test('should handle load errors gracefully', async () => {
      window.loadOverviewData = jest.fn().mockRejectedValue(new Error('Load failed'));
      
      await expect(window.loadSectionData('overview')).resolves.not.toThrow();
    });
  });
});