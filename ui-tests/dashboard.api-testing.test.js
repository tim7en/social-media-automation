/**
 * API Testing Interface Tests
 * Tests for the API testing functionality in the dashboard
 */

describe('API Testing Interface', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="api-testing-section" class="content-section">
        <div class="api-test-container">
          <div class="api-controls">
            <select id="api-method">
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
            <input type="text" id="api-endpoint" placeholder="/api/v1/content/generate">
            <button onclick="executeApiTest()">Execute</button>
          </div>
          <div class="api-test-grid">
            <textarea id="api-request-body" placeholder='{"key": "value"}'></textarea>
            <pre id="api-response"></pre>
          </div>
          <div class="endpoint-buttons">
            <button onclick="quickTest('/health')">Health Check</button>
            <button onclick="quickTest('/api/v1/analytics/overview')">Analytics</button>
            <button onclick="quickTest('/api/v1/content/tasks')">Content Tasks</button>
            <button onclick="quickTest('/api/v1/platforms/status')">Platform Status</button>
          </div>
        </div>
      </div>
      <div id="notifications" class="notifications-container"></div>
    `;

    require('../static/js/dashboard.js');
  });

  describe('API Test Execution', () => {
    test('should execute GET request successfully', async () => {
      const mockResponse = { status: 'ok', data: 'test' };
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      document.getElementById('api-method').value = 'GET';
      document.getElementById('api-endpoint').value = '/api/v1/test';

      await window.executeApiTest();

      expect(fetch).toHaveBeenCalledWith('/api/v1/test', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const responseElement = document.getElementById('api-response');
      expect(responseElement.textContent).toBe(JSON.stringify(mockResponse, null, 2));
    });

    test('should execute POST request with body', async () => {
      const requestBody = { test: 'data' };
      const mockResponse = { success: true };
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      document.getElementById('api-method').value = 'POST';
      document.getElementById('api-endpoint').value = '/api/v1/content';
      document.getElementById('api-request-body').value = JSON.stringify(requestBody);

      await window.executeApiTest();

      expect(fetch).toHaveBeenCalledWith('/api/v1/content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
    });

    test('should include authorization header when token exists', async () => {
      localStorage.setItem('auth_token', 'test-token');
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      document.getElementById('api-method').value = 'GET';
      document.getElementById('api-endpoint').value = '/api/v1/protected';

      await window.executeApiTest();

      expect(fetch).toHaveBeenCalledWith('/api/v1/protected', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        }
      });
    });

    test('should handle API errors gracefully', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Bad request' })
      });

      document.getElementById('api-method').value = 'GET';
      document.getElementById('api-endpoint').value = '/api/v1/invalid';

      await window.executeApiTest();

      const responseElement = document.getElementById('api-response');
      expect(responseElement.textContent).toContain('Bad request');
    });

    test('should handle network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      document.getElementById('api-method').value = 'GET';
      document.getElementById('api-endpoint').value = '/api/v1/test';

      await window.executeApiTest();

      const responseElement = document.getElementById('api-response');
      expect(responseElement.textContent).toContain('Error: Network error');
    });

    test('should require endpoint to be provided', async () => {
      document.getElementById('api-endpoint').value = '';

      await window.executeApiTest();

      expect(fetch).not.toHaveBeenCalled();
      // Should show error notification
      expect(window.showNotification).toHaveBeenCalledWith(
        'Please enter an API endpoint', 
        'error'
      );
    });
  });

  describe('Quick Test Functionality', () => {
    test('should set up quick test parameters', () => {
      window.quickTest('/health');

      expect(document.getElementById('api-method').value).toBe('GET');
      expect(document.getElementById('api-endpoint').value).toBe('/health');
      expect(document.getElementById('api-request-body').value).toBe('');
    });

    test('should execute quick test', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy' })
      });

      window.quickTest('/api/v1/analytics/overview');

      // Wait for async execution
      await new Promise(resolve => setTimeout(resolve, 0));

      expect(fetch).toHaveBeenCalledWith('/api/v1/analytics/overview', expect.any(Object));
    });

    test('should work with all predefined endpoints', async () => {
      const endpoints = [
        '/health',
        '/api/v1/analytics/overview',
        '/api/v1/content/tasks',
        '/api/v1/platforms/status'
      ];

      fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'ok' })
      });

      for (const endpoint of endpoints) {
        window.quickTest(endpoint);
        expect(document.getElementById('api-endpoint').value).toBe(endpoint);
      }
    });
  });

  describe('Response Display', () => {
    test('should format JSON response properly', async () => {
      const complexResponse = {
        data: {
          users: [
            { id: 1, name: 'John' },
            { id: 2, name: 'Jane' }
          ],
          meta: { total: 2, page: 1 }
        }
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => complexResponse
      });

      document.getElementById('api-method').value = 'GET';
      document.getElementById('api-endpoint').value = '/api/v1/users';

      await window.executeApiTest();

      const responseElement = document.getElementById('api-response');
      const expectedFormat = JSON.stringify(complexResponse, null, 2);
      expect(responseElement.textContent).toBe(expectedFormat);
    });

    test('should clear previous response', async () => {
      const responseElement = document.getElementById('api-response');
      responseElement.textContent = 'Previous response';

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ new: 'response' })
      });

      document.getElementById('api-method').value = 'GET';
      document.getElementById('api-endpoint').value = '/api/v1/test';

      await window.executeApiTest();

      expect(responseElement.textContent).not.toContain('Previous response');
      expect(responseElement.textContent).toContain('new');
    });
  });

  describe('Request Body Handling', () => {
    test('should not include body for GET requests', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      document.getElementById('api-method').value = 'GET';
      document.getElementById('api-endpoint').value = '/api/v1/test';
      document.getElementById('api-request-body').value = '{"should": "be ignored"}';

      await window.executeApiTest();

      const fetchCall = fetch.mock.calls[0];
      expect(fetchCall[1]).not.toHaveProperty('body');
    });

    test('should include body for POST requests', async () => {
      const requestBody = '{"test": "data"}';
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      document.getElementById('api-method').value = 'POST';
      document.getElementById('api-endpoint').value = '/api/v1/test';
      document.getElementById('api-request-body').value = requestBody;

      await window.executeApiTest();

      const fetchCall = fetch.mock.calls[0];
      expect(fetchCall[1].body).toBe(requestBody);
    });

    test('should include body for PUT and DELETE requests', async () => {
      const methods = ['PUT', 'DELETE'];
      const requestBody = '{"test": "data"}';

      for (const method of methods) {
        fetch.mockClear();
        fetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({})
        });

        document.getElementById('api-method').value = method;
        document.getElementById('api-endpoint').value = '/api/v1/test';
        document.getElementById('api-request-body').value = requestBody;

        await window.executeApiTest();

        const fetchCall = fetch.mock.calls[0];
        expect(fetchCall[1].body).toBe(requestBody);
      }
    });
  });
});