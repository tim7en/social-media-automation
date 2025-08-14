/**
 * Workflow Management Tests
 * Tests for workflow creation, management, and execution
 */

describe('Workflow Management', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="workflows-section" class="content-section">
        <div class="workflow-controls">
          <button onclick="createWorkflow()">Create New Workflow</button>
          <button onclick="loadWorkflowTemplates()">Load Templates</button>
        </div>
        <div id="active-workflows" class="workflows-list"></div>
        <div id="workflow-templates" class="templates-grid"></div>
      </div>
      <div id="modal" class="modal" style="display: none;">
        <div class="modal-content">
          <span class="close" onclick="closeModal()">&times;</span>
          <div id="modal-body">
            <form id="workflow-form">
              <input type="text" id="workflow-name" placeholder="Workflow Name">
              <select id="workflow-trigger">
                <option value="manual">Manual</option>
                <option value="scheduled">Scheduled</option>
                <option value="event">Event-based</option>
              </select>
              <textarea id="workflow-description" placeholder="Description"></textarea>
              <button type="button" onclick="saveWorkflow()">Save Workflow</button>
            </form>
          </div>
        </div>
      </div>
      <div id="notifications" class="notifications-container"></div>
    `;

    require('../static/js/dashboard.js');
  });

  describe('Workflow Creation', () => {
    test('should open workflow creation modal', () => {
      window.createWorkflow();

      const modal = document.getElementById('modal');
      expect(modal.style.display).toBe('block');

      const form = document.getElementById('workflow-form');
      expect(form).toBeTruthy();
    });

    test('should clear form when creating new workflow', () => {
      // Pre-fill form
      document.getElementById('workflow-name').value = 'Test Workflow';
      document.getElementById('workflow-description').value = 'Test Description';

      window.createWorkflow();

      expect(document.getElementById('workflow-name').value).toBe('');
      expect(document.getElementById('workflow-description').value).toBe('');
      expect(document.getElementById('workflow-trigger').value).toBe('manual');
    });

    test('should save new workflow successfully', async () => {
      const workflowData = {
        name: 'Test Workflow',
        trigger: 'scheduled',
        description: 'Automated posting workflow'
      };

      document.getElementById('workflow-name').value = workflowData.name;
      document.getElementById('workflow-trigger').value = workflowData.trigger;
      document.getElementById('workflow-description').value = workflowData.description;

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 123, ...workflowData })
      });

      window.loadWorkflowData = jest.fn().mockResolvedValue();

      await window.saveWorkflow();

      expect(fetch).toHaveBeenCalledWith('/api/v1/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(workflowData)
      });

      expect(window.showNotification).toHaveBeenCalledWith(
        'Workflow saved successfully',
        'success'
      );

      expect(window.loadWorkflowData).toHaveBeenCalled();

      // Modal should be closed
      const modal = document.getElementById('modal');
      expect(modal.style.display).toBe('none');
    });

    test('should handle workflow save errors', async () => {
      document.getElementById('workflow-name').value = 'Test Workflow';

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Invalid workflow data' })
      });

      await window.saveWorkflow();

      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to save workflow',
        'error'
      );
    });

    test('should validate required fields', async () => {
      // Don't fill in name
      document.getElementById('workflow-name').value = '';
      document.getElementById('workflow-description').value = 'Description';

      await window.saveWorkflow();

      expect(window.showNotification).toHaveBeenCalledWith(
        'Please fill in all required fields',
        'error'
      );

      expect(fetch).not.toHaveBeenCalled();
    });
  });

  describe('Workflow Templates', () => {
    test('should load workflow templates', async () => {
      const mockTemplates = [
        {
          id: 1,
          name: 'Daily Social Media Post',
          description: 'Automatically post content daily',
          trigger: 'scheduled',
          actions: ['generate_content', 'post_to_platforms']
        },
        {
          id: 2,
          name: 'Engagement Response',
          description: 'Auto-respond to comments',
          trigger: 'event',
          actions: ['detect_comment', 'generate_response', 'reply']
        }
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ templates: mockTemplates })
      });

      await window.loadWorkflowTemplates();

      expect(fetch).toHaveBeenCalledWith('/api/v1/workflows/templates');

      const templatesContainer = document.getElementById('workflow-templates');
      expect(templatesContainer.children.length).toBe(2);

      // Check first template
      const firstTemplate = templatesContainer.children[0];
      expect(firstTemplate.textContent).toContain('Daily Social Media Post');
      expect(firstTemplate.textContent).toContain('Automatically post content daily');
    });

    test('should handle empty templates', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ templates: [] })
      });

      await window.loadWorkflowTemplates();

      const templatesContainer = document.getElementById('workflow-templates');
      expect(templatesContainer.textContent).toContain('No templates available');
    });

    test('should create workflow from template', async () => {
      const template = {
        id: 1,
        name: 'Template Workflow',
        description: 'Template description',
        trigger: 'scheduled'
      };

      window.createWorkflow();

      window.useTemplate(template);

      expect(document.getElementById('workflow-name').value).toBe(template.name);
      expect(document.getElementById('workflow-description').value).toBe(template.description);
      expect(document.getElementById('workflow-trigger').value).toBe(template.trigger);
    });
  });

  describe('Active Workflows Display', () => {
    test('should display active workflows', () => {
      const mockWorkflows = [
        {
          id: 1,
          name: 'Daily Posts',
          status: 'active',
          lastRun: '2024-01-01T10:00:00Z',
          nextRun: '2024-01-02T10:00:00Z',
          trigger: 'scheduled'
        },
        {
          id: 2,
          name: 'Comment Responses',
          status: 'paused',
          lastRun: '2024-01-01T08:00:00Z',
          nextRun: null,
          trigger: 'event'
        }
      ];

      window.updateActiveWorkflows(mockWorkflows);

      const workflowsContainer = document.getElementById('active-workflows');
      expect(workflowsContainer.children.length).toBe(2);

      // Check first workflow
      const firstWorkflow = workflowsContainer.children[0];
      expect(firstWorkflow.textContent).toContain('Daily Posts');
      expect(firstWorkflow.textContent).toContain('active');
      expect(firstWorkflow.classList.contains('active')).toBe(true);

      // Check second workflow
      const secondWorkflow = workflowsContainer.children[1];
      expect(secondWorkflow.textContent).toContain('Comment Responses');
      expect(secondWorkflow.textContent).toContain('paused');
      expect(secondWorkflow.classList.contains('paused')).toBe(true);
    });

    test('should handle empty workflows list', () => {
      window.updateActiveWorkflows([]);

      const workflowsContainer = document.getElementById('active-workflows');
      expect(workflowsContainer.textContent).toContain('No active workflows');
    });

    test('should format workflow timestamps', () => {
      const workflow = {
        id: 1,
        name: 'Test Workflow',
        status: 'active',
        lastRun: '2024-01-01T10:30:00Z',
        nextRun: '2024-01-02T10:30:00Z'
      };

      window.updateActiveWorkflows([workflow]);

      const workflowElement = document.getElementById('active-workflows').children[0];
      expect(workflowElement.textContent).toContain('10:30');
    });
  });

  describe('Workflow Actions', () => {
    test('should start workflow', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'started' })
      });

      window.loadWorkflowData = jest.fn().mockResolvedValue();

      await window.startWorkflow(123);

      expect(fetch).toHaveBeenCalledWith('/api/v1/workflows/123/start', {
        method: 'POST'
      });

      expect(window.showNotification).toHaveBeenCalledWith(
        'Workflow started successfully',
        'success'
      );

      expect(window.loadWorkflowData).toHaveBeenCalled();
    });

    test('should pause workflow', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'paused' })
      });

      window.loadWorkflowData = jest.fn().mockResolvedValue();

      await window.pauseWorkflow(123);

      expect(fetch).toHaveBeenCalledWith('/api/v1/workflows/123/pause', {
        method: 'POST'
      });

      expect(window.showNotification).toHaveBeenCalledWith(
        'Workflow paused successfully',
        'success'
      );
    });

    test('should delete workflow with confirmation', async () => {
      // Mock window.confirm
      window.confirm = jest.fn(() => true);

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ deleted: true })
      });

      window.loadWorkflowData = jest.fn().mockResolvedValue();

      await window.deleteWorkflow(123);

      expect(window.confirm).toHaveBeenCalledWith(
        'Are you sure you want to delete this workflow?'
      );

      expect(fetch).toHaveBeenCalledWith('/api/v1/workflows/123', {
        method: 'DELETE'
      });

      expect(window.showNotification).toHaveBeenCalledWith(
        'Workflow deleted successfully',
        'success'
      );
    });

    test('should not delete workflow if not confirmed', async () => {
      window.confirm = jest.fn(() => false);

      await window.deleteWorkflow(123);

      expect(fetch).not.toHaveBeenCalled();
    });

    test('should handle workflow action errors', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Server error' })
      });

      await window.startWorkflow(123);

      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to start workflow',
        'error'
      );
    });
  });

  describe('Workflow Data Loading', () => {
    test('should load workflow data', async () => {
      const mockData = {
        active: [
          { id: 1, name: 'Workflow 1', status: 'active' },
          { id: 2, name: 'Workflow 2', status: 'paused' }
        ],
        recent: [
          { id: 3, name: 'Recent Workflow', status: 'completed' }
        ]
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      });

      window.updateActiveWorkflows = jest.fn();

      await window.loadWorkflowData();

      expect(fetch).toHaveBeenCalledWith('/api/v1/workflows');
      expect(window.updateActiveWorkflows).toHaveBeenCalledWith(mockData.active);
    });

    test('should handle workflow data loading errors', async () => {
      fetch.mockRejectedValueOnce(new Error('API error'));

      await window.loadWorkflowData();

      expect(window.showNotification).toHaveBeenCalledWith(
        'Failed to load workflow data',
        'error'
      );
    });
  });

  describe('Workflow Execution Monitoring', () => {
    test('should show workflow execution status', () => {
      const execution = {
        workflowId: 1,
        status: 'running',
        progress: 60,
        startTime: '2024-01-01T10:00:00Z',
        steps: [
          { name: 'Generate Content', status: 'completed' },
          { name: 'Schedule Post', status: 'running' },
          { name: 'Send Notifications', status: 'pending' }
        ]
      };

      window.showWorkflowExecution(execution);

      const modal = document.getElementById('modal');
      expect(modal.style.display).toBe('block');

      const modalBody = document.getElementById('modal-body');
      expect(modalBody.textContent).toContain('running');
      expect(modalBody.textContent).toContain('60%');
    });

    test('should update execution progress', () => {
      const progressBar = document.createElement('div');
      progressBar.id = 'execution-progress';
      progressBar.className = 'progress-bar';
      document.body.appendChild(progressBar);

      window.updateExecutionProgress(75);

      expect(progressBar.style.width).toBe('75%');
    });

    test('should handle execution errors', () => {
      const execution = {
        workflowId: 1,
        status: 'failed',
        error: 'Content generation failed',
        startTime: '2024-01-01T10:00:00Z'
      };

      window.showWorkflowExecution(execution);

      const modalBody = document.getElementById('modal-body');
      expect(modalBody.textContent).toContain('failed');
      expect(modalBody.textContent).toContain('Content generation failed');
    });
  });
});