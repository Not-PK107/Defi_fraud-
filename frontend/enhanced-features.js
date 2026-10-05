/**
 * enhanced-features.js
 * Additional modern features and improvements for the DeFi Fraud Detection frontend
 * Includes real-time notifications, advanced analytics, and enhanced UX features
 */

// Enhanced State Management
const EnhancedState = {
  ...STATE,
  notifications: [],
  analytics: {
    totalScans: 0,
    highRiskFound: 0,
    averageScore: 0,
    recentScans: []
  },
  preferences: {
    autoRefresh: false,
    soundEnabled: true,
    animationsEnabled: true,
    compactMode: false
  },
  websocketConnected: false,
  realTimeAlerts: []
};

// Notification System
class NotificationManager {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    // Create notification container
    this.container = document.createElement('div');
    this.container.className = 'notification-container';
    this.container.innerHTML = '<div id="notifications"></div>';
    document.body.appendChild(this.container);
  }

  show(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icon = this.getIcon(type);
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-icon">${icon}</span>
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `;

    this.container.firstChild.appendChild(notification);

    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        if (notification.parentElement) {
          notification.remove();
        }
      }, duration);
    }

    // Play sound if enabled
    if (EnhancedState.preferences.soundEnabled) {
      this.playNotificationSound(type);
    }

    return notification;
  }

  getIcon(type) {
    const icons = {
      'success': '✅',
      'error': '❌', 
      'warning': '⚠️',
      'info': 'ℹ️',
      'fraud': '🚨',
      'clean': '🛡️'
    };
    return icons[type] || icons['info'];
  }

  playNotificationSound(type) {
    // Create audio context for notification sounds
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      // Different frequencies for different notification types
      const frequencies = {
        'success': 800,
        'error': 300,
        'warning': 600,
        'info': 500,
        'fraud': 200,
        'clean': 900
      };
      
      oscillator.frequency.setValueAtTime(frequencies[type] || 500, audioContext.currentTime);
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.2);
    } catch (e) {
      console.log('Audio not supported');
    }
  }
}

// Analytics Dashboard
class AnalyticsDashboard {
  constructor() {
    this.init();
  }

  init() {
    this.loadStoredAnalytics();
    this.createAnalyticsPanel();
  }

  loadStoredAnalytics() {
    const stored = localStorage.getItem('defi_analytics');
    if (stored) {
      EnhancedState.analytics = { ...EnhancedState.analytics, ...JSON.parse(stored) };
    }
  }

  saveAnalytics() {
    localStorage.setItem('defi_analytics', JSON.stringify(EnhancedState.analytics));
  }

  recordScan(result) {
    EnhancedState.analytics.totalScans++;
    EnhancedState.analytics.recentScans.unshift({
      address: result.wallet,
      score: result.risk_score,
      level: result.risk_level,
      timestamp: Date.now()
    });
    
    // Keep only last 50 scans
    EnhancedState.analytics.recentScans = EnhancedState.analytics.recentScans.slice(0, 50);
    
    if (result.risk_level === 'HIGH' || result.risk_level === 'CRITICAL') {
      EnhancedState.analytics.highRiskFound++;
    }
    
    // Calculate running average
    const scores = EnhancedState.analytics.recentScans.map(s => s.score);
    EnhancedState.analytics.averageScore = scores.reduce((a, b) => a + b, 0) / scores.length;
    
    this.saveAnalytics();
    this.updateAnalyticsDisplay();
  }

  createAnalyticsPanel() {
    // Create floating analytics button
    const analyticsBtn = document.createElement('button');
    analyticsBtn.className = 'analytics-toggle-btn';
    analyticsBtn.innerHTML = '📊';
    analyticsBtn.title = 'View Analytics Dashboard';
    analyticsBtn.onclick = () => this.toggleAnalyticsPanel();
    
    // Add to navigation
    const navActions = document.querySelector('.nav-actions');
    if (navActions) {
      navActions.appendChild(analyticsBtn);
    }
  }

  toggleAnalyticsPanel() {
    let panel = document.getElementById('analyticsPanel');
    
    if (!panel) {
      panel = this.createAnalyticsModal();
      document.body.appendChild(panel);
    }
    
    panel.style.display = panel.style.display === 'flex' ? 'none' : 'flex';
    
    if (panel.style.display === 'flex') {
      this.updateAnalyticsDisplay();
    }
  }

  createAnalyticsModal() {
    const modal = document.createElement('div');
    modal.id = 'analyticsPanel';
    modal.className = 'modal-backdrop';
    modal.innerHTML = `
      <div class="modal-dialog analytics-modal">
        <button class="modal-close-btn" onclick="document.getElementById('analyticsPanel').style.display='none'">×</button>
        <div class="card-header-classic">
          <h2><span>📊</span> Analytics Dashboard</h2>
          <span class="card-badge">Session Statistics</span>
        </div>
        
        <div class="analytics-grid">
          <div class="analytics-card">
            <div class="analytics-metric">
              <span class="metric-value" id="totalScansMetric">0</span>
              <span class="metric-label">Total Scans</span>
            </div>
          </div>
          
          <div class="analytics-card">
            <div class="analytics-metric">
              <span class="metric-value" id="highRiskMetric">0</span>
              <span class="metric-label">High Risk Found</span>
            </div>
          </div>
          
          <div class="analytics-card">
            <div class="analytics-metric">
              <span class="metric-value" id="averageScoreMetric">0.0</span>
              <span class="metric-label">Average Score</span>
            </div>
          </div>
          
          <div class="analytics-card">
            <div class="analytics-metric">
              <span class="metric-value" id="riskRateMetric">0%</span>
              <span class="metric-label">Risk Detection Rate</span>
            </div>
          </div>
        </div>
        
        <div class="recent-scans-section">
          <h3>Recent Scans</h3>
          <div class="recent-scans-list" id="recentScansList"></div>
        </div>
        
        <div class="analytics-actions">
          <button class="btn-classic-outline" onclick="analyticsManager.exportData()">
            📄 Export Data
          </button>
          <button class="btn-classic-outline" onclick="analyticsManager.clearData()">
            🗑️ Clear History
          </button>
        </div>
      </div>
    `;
    
    return modal;
  }

  updateAnalyticsDisplay() {
    const analytics = EnhancedState.analytics;
    
    // Update metrics
    const elements = {
      totalScansMetric: analytics.totalScans.toLocaleString(),
      highRiskMetric: analytics.highRiskFound.toLocaleString(),
      averageScoreMetric: analytics.averageScore.toFixed(1),
      riskRateMetric: analytics.totalScans > 0 ? 
        Math.round((analytics.highRiskFound / analytics.totalScans) * 100) + '%' : '0%'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    });
    
    // Update recent scans list
    this.updateRecentScansList();
  }

  updateRecentScansList() {
    const list = document.getElementById('recentScansList');
    if (!list) return;
    
    const recentScans = EnhancedState.analytics.recentScans.slice(0, 10);
    
    list.innerHTML = recentScans.map(scan => `
      <div class="recent-scan-item">
        <div class="scan-address">${this.truncateAddress(scan.address)}</div>
        <div class="scan-score risk-${scan.level.toLowerCase()}">${scan.score.toFixed(1)}</div>
        <div class="scan-time">${this.formatTime(scan.timestamp)}</div>
      </div>
    `).join('') || '<div class="no-scans">No scans yet</div>';
  }

  truncateAddress(address) {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  }

  formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
  }

  exportData() {
    const data = {
      analytics: EnhancedState.analytics,
      exportDate: new Date().toISOString(),
      version: "1.0"
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `defi-analytics-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    notificationManager.show('Analytics data exported successfully', 'success');
  }

  clearData() {
    if (confirm('Are you sure you want to clear all analytics data?')) {
      EnhancedState.analytics = {
        totalScans: 0,
        highRiskFound: 0,
        averageScore: 0,
        recentScans: []
      };
      this.saveAnalytics();
      this.updateAnalyticsDisplay();
      notificationManager.show('Analytics data cleared', 'info');
    }
  }
}

// Real-time WebSocket Connection (for live blockchain alerts)
class RealtimeManager {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    try {
      // Only connect WebSocket when served over http/https (not file://)
      if (!window.location.protocol.startsWith('http')) {
        console.log('WebSocket skipped: page not served over HTTP');
        return;
      }
      // Try to connect to WebSocket server for real-time updates
      const wsUrl = `ws://${window.location.host}/ws`;
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('🔌 WebSocket connected');
        EnhancedState.websocketConnected = true;
        this.reconnectAttempts = 0;
        notificationManager.show('Real-time updates enabled', 'success', 3000);
      };
      
      this.ws.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };
      
      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        EnhancedState.websocketConnected = false;
        this.attemptReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.log('WebSocket error:', error);
      };
      
    } catch (e) {
      console.log('WebSocket not available');
    }
  }


  handleMessage(data) {
    switch (data.type) {
      case 'new_fraud_alert':
        this.handleNewFraudAlert(data.payload);
        break;
      case 'blockchain_update':
        this.handleBlockchainUpdate(data.payload);
        break;
    }
  }

  handleNewFraudAlert(alert) {
    notificationManager.show(
      `🚨 New fraud alert: ${alert.wallet_address} (Score: ${alert.risk_score})`,
      'fraud',
      8000
    );
    
    EnhancedState.realTimeAlerts.unshift(alert);
    this.updateRealtimeAlertsDisplay();
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Attempting WebSocket reconnection (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, 5000 * this.reconnectAttempts);
    }
  }
}

// Enhanced UI Improvements
class UIEnhancements {
  constructor() {
    this.init();
  }

  init() {
    this.addKeyboardShortcuts();
    this.addAdvancedTooltips();
    this.addLoadingOverlays();
    this.addProgressiveWebAppFeatures();
  }

  addKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + Enter to analyze
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn && !analyzeBtn.disabled) {
          analyzeBtn.click();
        }
      }
      
      // Escape to close modals
      if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal-backdrop[style*="flex"]');
        openModals.forEach(modal => modal.style.display = 'none');
      }
      
      // Ctrl/Cmd + K to focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const walletInput = document.getElementById('walletInput');
        if (walletInput) {
          walletInput.focus();
          walletInput.select();
        }
      }
    });
  }

  addAdvancedTooltips() {
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'advanced-tooltip';
    document.body.appendChild(tooltip);

    // Add tooltips to feature cards
    document.addEventListener('mouseover', (e) => {
      const featureCard = e.target.closest('.feature-item-card');
      if (featureCard) {
        const title = featureCard.querySelector('.feat-title')?.textContent;
        const description = featureCard.querySelector('.feat-desc')?.textContent;
        
        if (title && description) {
          tooltip.innerHTML = `<strong>${title}</strong><br>${description}`;
          tooltip.style.display = 'block';
        }
      }
    });

    document.addEventListener('mousemove', (e) => {
      if (tooltip.style.display === 'block') {
        tooltip.style.left = e.pageX + 10 + 'px';
        tooltip.style.top = e.pageY + 10 + 'px';
      }
    });

    document.addEventListener('mouseout', (e) => {
      if (!e.target.closest('.feature-item-card')) {
        tooltip.style.display = 'none';
      }
    });
  }

  addLoadingOverlays() {
    // Enhanced loading states for better UX
    const originalStartAnalysis = window.startAnalysis;
    
    window.startAnalysis = async function(address, preloadedSample) {
      // Add loading overlay
      const overlay = document.createElement('div');
      overlay.className = 'loading-overlay';
      overlay.innerHTML = `
        <div class="loading-content">
          <div class="loading-spinner-large"></div>
          <h3>Analyzing Wallet...</h3>
          <p>Running ML models and blockchain verification</p>
        </div>
      `;
      document.body.appendChild(overlay);
      
      try {
        await originalStartAnalysis.call(this, address, preloadedSample);
      } finally {
        overlay.remove();
      }
    };
  }

  addProgressiveWebAppFeatures() {
    // Add to home screen functionality
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      this.showInstallPrompt();
    });
  }

  showInstallPrompt() {
    const installBtn = document.createElement('button');
    installBtn.className = 'install-app-btn';
    installBtn.innerHTML = '📱 Install App';
    installBtn.onclick = () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            notificationManager.show('App installed successfully!', 'success');
          }
          deferredPrompt = null;
          installBtn.remove();
        });
      }
    };
    
    const navActions = document.querySelector('.nav-actions');
    if (navActions) {
      navActions.appendChild(installBtn);
    }
  }
}

// Bulk Analysis Feature
class BulkAnalysisManager {
  constructor() {
    this.init();
  }

  init() {
    this.addBulkAnalysisButton();
  }

  addBulkAnalysisButton() {
    const bulkBtn = document.createElement('button');
    bulkBtn.className = 'btn-icon';
    bulkBtn.innerHTML = '📋';
    bulkBtn.title = 'Bulk Analysis';
    bulkBtn.onclick = () => this.openBulkAnalysisModal();
    
    const navActions = document.querySelector('.nav-actions');
    if (navActions) {
      navActions.appendChild(bulkBtn);
    }
  }

  openBulkAnalysisModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-backdrop';
    modal.innerHTML = `
      <div class="modal-dialog">
        <button class="modal-close-btn" onclick="this.parentElement.parentElement.remove()">×</button>
        <div class="card-header-classic">
          <h2><span>📋</span> Bulk Wallet Analysis</h2>
          <span class="card-badge">Batch Processing</span>
        </div>
        
        <div class="bulk-analysis-content">
          <textarea 
            id="bulkAddressList" 
            placeholder="Enter wallet addresses, one per line..."
            class="bulk-address-input"
            rows="10"
          ></textarea>
          
          <div class="bulk-controls">
            <button class="btn-classic-primary" onclick="bulkAnalysisManager.processBulkAnalysis()">
              🚀 Analyze All Wallets
            </button>
          </div>
          
          <div id="bulkResults" class="bulk-results"></div>
        </div>
      </div>
    `;
    
    modal.style.display = 'flex';
    document.body.appendChild(modal);
  }

  async processBulkAnalysis() {
    const textarea = document.getElementById('bulkAddressList');
    const resultsDiv = document.getElementById('bulkResults');
    
    if (!textarea || !resultsDiv) return;
    
    const addresses = textarea.value
      .split('\n')
      .map(addr => addr.trim())
      .filter(addr => addr.length === 42 && addr.startsWith('0x'));
    
    if (addresses.length === 0) {
      notificationManager.show('Please enter valid Ethereum addresses', 'warning');
      return;
    }
    
    resultsDiv.innerHTML = '<div class="bulk-progress">Processing...</div>';
    
    const results = [];
    for (let i = 0; i < addresses.length; i++) {
      try {
        const result = await this.analyzeSingleAddress(addresses[i]);
        results.push(result);
        
        // Update progress
        resultsDiv.innerHTML = `
          <div class="bulk-progress">
            Processed ${i + 1} of ${addresses.length} addresses...
          </div>
        `;
      } catch (e) {
        results.push({ 
          wallet: addresses[i], 
          error: e.message,
          risk_score: 'N/A',
          risk_level: 'ERROR'
        });
      }
    }
    
    this.displayBulkResults(results, resultsDiv);
  }

  async analyzeSingleAddress(address) {
    const response = await fetch(`${STATE.apiEndpoint}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address })
    });
    
    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.statusText}`);
    }
    
    return await response.json();
  }

  displayBulkResults(results, container) {
    const highRisk = results.filter(r => r.risk_level === 'HIGH' || r.risk_level === 'CRITICAL').length;
    const mediumRisk = results.filter(r => r.risk_level === 'MEDIUM').length;
    const lowRisk = results.filter(r => r.risk_level === 'LOW').length;
    const errors = results.filter(r => r.risk_level === 'ERROR').length;
    
    container.innerHTML = `
      <div class="bulk-summary">
        <h3>Analysis Summary</h3>
        <div class="summary-stats">
          <div class="stat-item danger">High Risk: ${highRisk}</div>
          <div class="stat-item warning">Medium Risk: ${mediumRisk}</div>
          <div class="stat-item success">Low Risk: ${lowRisk}</div>
          <div class="stat-item muted">Errors: ${errors}</div>
        </div>
      </div>
      
      <div class="bulk-results-table">
        <table class="classic-table">
          <thead>
            <tr>
              <th>Address</th>
              <th>Risk Score</th>
              <th>Risk Level</th>
              <th>Recommendation</th>
            </tr>
          </thead>
          <tbody>
            ${results.map(result => `
              <tr class="risk-${(result.risk_level || 'error').toLowerCase()}">
                <td class="address-cell">${result.wallet}</td>
                <td>${result.risk_score !== 'N/A' ? result.risk_score.toFixed(1) : 'N/A'}</td>
                <td><span class="chip-tag ${this.getRiskClass(result.risk_level)}">${result.risk_level}</span></td>
                <td>${result.recommendation || result.error || 'N/A'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      
      <div class="bulk-actions">
        <button class="btn-classic-outline" onclick="bulkAnalysisManager.exportBulkResults(${JSON.stringify(results).replace(/"/g, '&quot;')})">
          📄 Export Results
        </button>
      </div>
    `;
  }

  getRiskClass(riskLevel) {
    const classes = {
      'CRITICAL': 'danger',
      'HIGH': 'danger',
      'MEDIUM': 'warning', 
      'LOW': 'success',
      'ERROR': 'muted'
    };
    return classes[riskLevel] || 'muted';
  }

  exportBulkResults(results) {
    const csv = this.convertToCSV(results);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bulk-analysis-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  convertToCSV(results) {
    const headers = ['Address', 'Risk Score', 'Risk Level', 'Fraud Probability', 'Recommendation'];
    const rows = results.map(r => [
      r.wallet,
      r.risk_score !== 'N/A' ? r.risk_score : 'N/A',
      r.risk_level || 'ERROR',
      r.fraud_probability || 'N/A',
      (r.recommendation || r.error || 'N/A').replace(/,/g, ';')
    ]);
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }
}

// Initialize enhanced features
let notificationManager, analyticsManager, realtimeManager, uiEnhancements, bulkAnalysisManager;

document.addEventListener('DOMContentLoaded', () => {
  // Initialize enhanced features after DOM is ready
  notificationManager = new NotificationManager();
  analyticsManager = new AnalyticsDashboard();
  realtimeManager = new RealtimeManager();
  uiEnhancements = new UIEnhancements();
  bulkAnalysisManager = new BulkAnalysisManager();
  
  // Try to connect to real-time updates
  realtimeManager.connect();
  
  // Hook into existing analysis function to record analytics
  const originalRenderAnalysisResults = window.renderAnalysisResults;
  if (originalRenderAnalysisResults) {
    window.renderAnalysisResults = function(data) {
      originalRenderAnalysisResults.call(this, data);
      analyticsManager.recordScan(data);
      
      // Show notification based on result
      const type = (data.risk_level === 'HIGH' || data.risk_level === 'CRITICAL') ? 'fraud' : 
                   data.risk_level === 'MEDIUM' ? 'warning' : 'clean';
      const message = `Analysis complete: ${data.risk_level} risk (${data.risk_score.toFixed(1)}/100)`;
      notificationManager.show(message, type, 4000);
    };
  }
});

// Export for global access
window.EnhancedState = EnhancedState;
window.notificationManager = notificationManager;
window.analyticsManager = analyticsManager;
window.bulkAnalysisManager = bulkAnalysisManager;