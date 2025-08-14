/**
 * Content Generation Interface Tests
 * Tests for content generation and platform management functionality
 */

describe('Content Generation Interface', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="content-section" class="content-section">
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
        <div id="content-queue" class="content-queue"></div>
        <div id="generation-logs" class="logs-container"></div>
      </div>
      <div id="platforms-section" class="content-section">
        <div class="platform-grid">
          <div class="platform-card">
            <h3>Instagram</h3>
            <div id="instagram-status" class="status-indicator"></div>
            <button onclick="testPlatformConnection('instagram')">Test Connection</button>
          </div>
          <div class="platform-card">
            <h3>YouTube</h3>
            <div id="youtube-status" class="status-indicator"></div>
            <button onclick="testPlatformConnection('youtube')">Test Connection</button>
          </div>
          <div class="platform-card">
            <h3>TikTok</h3>
            <div id="tiktok-status" class="status-indicator"></div>
            <button onclick="testPlatformConnection('tiktok')">Test Connection</button>
          </div>
        </div>
      </div>
      <div id="notifications" class="notifications-container"></div>
    `;

    require('../static/js/dashboard.js');
  });

  describe('Content Generation', () => {
    test('should generate test content successfully', async () => {
      window.loadContentData = jest.fn().mockResolvedValue();
      
      document.getElementById('content-type').value = 'post';
      document.getElementById('target-platform').value = 'instagram';

      const promise = window.generateTestContent();

      // Fast-forward timers for the mock delay
      jest.advanceTimersByTime(2000);

      await promise;

      expect(window.showNotification).toHaveBeenCalledWith(
        'Generating post content for instagram...',
        'info'
      );
      expect(window.showNotification).toHaveBeenCalledWith(
        'Test content generation started successfully',
        'success'
      );
      expect(window.loadContentData).toHaveBeenCalled();
    });

    test('should handle content generation errors', async () => {
      window.loadContentData = jest.fn().mockRejectedValue(new Error('Load failed'));
      
      document.getElementById('content-type').value = 'video';
      document.getElementById('target-platform').value = 'youtube';

      const promise = window.generateTestContent();
      jest.advanceTimersByTime(2000);

      await promise;

      expect(window.showNotification).toHaveBeenCalledWith(
        'Generating video content for youtube...',
        'info'
      );
      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to generate test content',
        'error'
      );
    });

    test('should work with all content types and platforms', async () => {
      window.loadContentData = jest.fn().mockResolvedValue();
      
      const contentTypes = ['post', 'story', 'video'];
      const platforms = ['instagram', 'youtube', 'tiktok'];

      for (const contentType of contentTypes) {
        for (const platform of platforms) {
          document.getElementById('content-type').value = contentType;
          document.getElementById('target-platform').value = platform;

          const promise = window.generateTestContent();
          jest.advanceTimersByTime(2000);
          await promise;

          expect(window.showNotification).toHaveBeenCalledWith(
            `Generating ${contentType} content for ${platform}...`,
            'info'
          );
        }
      }
    });
  });

  describe('Platform Connection Testing', () => {
    test('should test platform connection successfully', async () => {
      // Mock Math.random to ensure success
      const originalRandom = Math.random;
      Math.random = jest.fn(() => 0.8); // > 0.3, so success

      const promise = window.testPlatformConnection('instagram');
      jest.advanceTimersByTime(1500);
      await promise;

      expect(window.showNotification).toHaveBeenCalledWith(
        'Testing instagram connection...',
        'info'
      );
      expect(window.showNotification).toHaveBeenCalledWith(
        'instagram connection successful',
        'success'
      );

      const statusElement = document.getElementById('instagram-status');
      expect(statusElement.className).toBe('status-indicator connected');

      Math.random = originalRandom;
    });

    test('should handle platform connection failure', async () => {
      // Mock Math.random to ensure failure
      const originalRandom = Math.random;
      Math.random = jest.fn(() => 0.1); // < 0.3, so failure

      const promise = window.testPlatformConnection('youtube');
      jest.advanceTimersByTime(1500);
      await promise;

      expect(window.showNotification).toHaveBeenCalledWith(
        'Testing youtube connection...',
        'info'
      );
      expect(window.showNotification).toHaveBeenCalledWith(
        'youtube connection failed',
        'error'
      );

      const statusElement = document.getElementById('youtube-status');
      expect(statusElement.className).toBe('status-indicator');

      Math.random = originalRandom;
    });

    test('should handle connection test errors', async () => {
      // Mock setTimeout to throw error
      const originalSetTimeout = global.setTimeout;
      global.setTimeout = jest.fn((callback, delay) => {
        throw new Error('Timer error');
      });

      await window.testPlatformConnection('tiktok');

      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to test tiktok connection',
        'error'
      );

      global.setTimeout = originalSetTimeout;
    });

    test('should test all platforms', async () => {
      const platforms = ['instagram', 'youtube', 'tiktok'];
      const originalRandom = Math.random;
      Math.random = jest.fn(() => 0.8); // Ensure success

      for (const platform of platforms) {
        const promise = window.testPlatformConnection(platform);
        jest.advanceTimersByTime(1500);
        await promise;

        expect(window.showNotification).toHaveBeenCalledWith(
          `Testing ${platform} connection...`,
          'info'
        );
        
        const statusElement = document.getElementById(`${platform}-status`);
        expect(statusElement.className).toBe('status-indicator connected');
      }

      Math.random = originalRandom;
    });
  });

  describe('Content Queue Management', () => {
    test('should update content queue display', () => {
      const mockQueueData = [
        { id: 1, type: 'post', platform: 'instagram', status: 'pending' },
        { id: 2, type: 'story', platform: 'instagram', status: 'processing' },
        { id: 3, type: 'video', platform: 'youtube', status: 'completed' }
      ];

      window.updateGenerationQueue(mockQueueData);

      const queueContainer = document.getElementById('content-queue');
      expect(queueContainer.children.length).toBe(3);

      // Check first item
      const firstItem = queueContainer.children[0];
      expect(firstItem.textContent).toContain('post');
      expect(firstItem.textContent).toContain('instagram');
      expect(firstItem.textContent).toContain('pending');
    });

    test('should handle empty queue', () => {
      window.updateGenerationQueue([]);

      const queueContainer = document.getElementById('content-queue');
      expect(queueContainer.children.length).toBe(1);
      expect(queueContainer.textContent).toContain('No items in queue');
    });

    test('should update queue with different statuses', () => {
      const statuses = ['pending', 'processing', 'completed', 'failed'];
      const mockData = statuses.map((status, index) => ({
        id: index + 1,
        type: 'post',
        platform: 'instagram',
        status
      }));

      window.updateGenerationQueue(mockData);

      const queueContainer = document.getElementById('content-queue');
      statuses.forEach((status, index) => {
        const item = queueContainer.children[index];
        expect(item.classList.contains(status)).toBe(true);
      });
    });
  });

  describe('Generation Logs', () => {
    test('should update generation logs', () => {
      const mockLogs = [
        { timestamp: '2024-01-01T10:00:00Z', message: 'Content generation started', level: 'info' },
        { timestamp: '2024-01-01T10:01:00Z', message: 'Content generated successfully', level: 'success' },
        { timestamp: '2024-01-01T10:02:00Z', message: 'Upload failed', level: 'error' }
      ];

      window.updateGenerationLogs(mockLogs);

      const logsContainer = document.getElementById('generation-logs');
      expect(logsContainer.children.length).toBe(3);

      // Check log entries
      mockLogs.forEach((log, index) => {
        const logEntry = logsContainer.children[index];
        expect(logEntry.textContent).toContain(log.message);
        expect(logEntry.classList.contains(log.level)).toBe(true);
      });
    });

    test('should handle empty logs', () => {
      window.updateGenerationLogs([]);

      const logsContainer = document.getElementById('generation-logs');
      expect(logsContainer.children.length).toBe(1);
      expect(logsContainer.textContent).toContain('No logs available');
    });

    test('should format timestamps correctly', () => {
      const mockLogs = [
        { 
          timestamp: '2024-01-01T10:00:00Z', 
          message: 'Test message', 
          level: 'info' 
        }
      ];

      window.updateGenerationLogs(mockLogs);

      const logEntry = document.getElementById('generation-logs').children[0];
      const timeElement = logEntry.querySelector('.timestamp');
      expect(timeElement.textContent).toBe('10:00:00');
    });
  });

  describe('Data Loading Functions', () => {
    test('should load content data', async () => {
      window.updateGenerationQueue = jest.fn();
      window.updateGenerationLogs = jest.fn();
      window.updateAIServiceStatus = jest.fn();

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          queue: [],
          logs: [],
          aiServices: {}
        })
      });

      await window.loadContentData();

      expect(fetch).toHaveBeenCalledWith('/api/v1/content/status');
      expect(window.updateGenerationQueue).toHaveBeenCalled();
      expect(window.updateGenerationLogs).toHaveBeenCalled();
      expect(window.updateAIServiceStatus).toHaveBeenCalled();
    });

    test('should load platform data', async () => {
      const mockPlatformData = {
        instagram: { connected: true, lastSync: '2024-01-01T10:00:00Z' },
        youtube: { connected: false, lastSync: null },
        tiktok: { connected: true, lastSync: '2024-01-01T09:00:00Z' }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPlatformData
      });

      await window.loadPlatformData();

      expect(fetch).toHaveBeenCalledWith('/api/v1/platforms/status');

      // Check status indicators were updated
      Object.keys(mockPlatformData).forEach(platform => {
        const statusElement = document.getElementById(`${platform}-status`);
        if (mockPlatformData[platform].connected) {
          expect(statusElement.classList.contains('connected')).toBe(true);
        } else {
          expect(statusElement.classList.contains('connected')).toBe(false);
        }
      });
    });

    test('should handle data loading errors', async () => {
      fetch.mockRejectedValueOnce(new Error('API error'));

      await window.loadContentData();

      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to load content data',
        'error'
      );
    });
  });
});