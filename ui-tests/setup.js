// Test setup file for UI tests
require('@testing-library/jest-dom');

// Add Node.js polyfills for Jest environment
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Set up DOM environment
require('global-jsdom/register');

// Load mocks
require('./dashboard.mocks.js');

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
};

// Mock Chart.js
global.Chart = class MockChart {
  constructor() {
    this.data = null;
    this.options = null;
  }
  
  update() {}
  destroy() {}
  resize() {}
};

// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
  fetch.mockClear();
  
  // Reset DOM
  document.body.innerHTML = '';
  document.head.innerHTML = '';
});

// Mock window methods
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
    pathname: '/',
    search: '',
    hash: '',
  },
  writable: true,
});

// Mock window.addEventListener
window.addEventListener = jest.fn();
window.removeEventListener = jest.fn();

// Mock setTimeout/setInterval for tests that need them
jest.useFakeTimers();