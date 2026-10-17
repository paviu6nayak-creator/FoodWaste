/**
 * FoodWise Web Application Frontend Logic
 * Connects with FastAPI endpoints: /api/waste, /api/analytics, /api/insights
 */

const API_BASE = window.location.origin.includes(':8000') 
  ? '' 
  : (window.location.protocol === 'file:' ? 'http://localhost:8000' : '');

// State
let allRecords = [];
let analyticsData = null;
let insightsData = null;
let currentDeletingId = null;
let dashCategoryChart = null;
let dashReasonChart = null;
let analyticsBarChart = null;
let analyticsPieChart = null;

// Category icons map
const CATEGORY_ICONS = {
  Rice: '🍚',
  Vegetables: '🥕',
  Fruits: '🍎',
  Dairy: '🧀',
  Bread: '🍞',
  Meat: '🍗',
  Snacks: '🍿',
  Other: '📦'
};

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  setupGreetingAndDate();
  setupNavListeners();
  setupFormPreviewListeners();
  checkApiHealth();
  loadAllData();
});

// Dynamic Greeting & Date
function setupGreetingAndDate() {
  const hour = new Date().getHours();
  let greeting = 'Good Day! 👋';
  if (hour < 12) greeting = 'Good Morning! ☀️';
  else if (hour < 17) greeting = 'Good Afternoon! 🌤️';
  else greeting = 'Good Evening! 🌙';

  const greetingEl = document.getElementById('header-greeting');
  if (greetingEl) greetingEl.textContent = greeting;

  const dateEl = document.getElementById('current-date-badge');
  if (dateEl) {
    const options = { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' };
    dateEl.textContent = new Date().toLocaleDateString('en-US', options);
  }
}

// Navigation & View Switching
function setupNavListeners() {
  const navButtons = document.querySelectorAll('.nav-item');
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetView = btn.dataset.view;
      switchView(targetView);
    });
  });
}

function switchView(viewName) {
  // Update nav buttons
  document.querySelectorAll('.nav-item').forEach(btn => {
    if (btn.dataset.view === viewName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Update views
  document.querySelectorAll('.view').forEach(view => {
    if (view.id === `view-${viewName}`) {
      view.classList.add('active');
    } else {
      view.classList.remove('active');
    }
  });

  // Re-render charts if entering charts view
  if (viewName === 'analytics') {
    renderAnalyticsCharts();
  } else if (viewName === 'dashboard') {
    renderDashboardCharts();
  }
}

// Check Backend Health
async function checkApiHealth() {
  const statusIndicator = document.getElementById('status-indicator');
  const statusText = document.getElementById('status-text');

  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (res.ok) {
      statusIndicator.className = 'status-indicator online';
      statusText.textContent = 'API Connected';
    } else {
      throw new Error('API degraded');
    }
  } catch (err) {
    statusIndicator.className = 'status-indicator';
    statusIndicator.style.backgroundColor = '#DE5252';
    statusText.textContent = 'Offline (Local)';
  }
}

// Load All Application Data
async function loadAllData() {
  await Promise.allSettled([
    fetchWasteRecords(),
    fetchAnalytics(),
    fetchInsights()
  ]);
}

// 1. Fetch Waste Records
async function fetchWasteRecords() {
  try {
    const res = await fetch(`${API_BASE}/api/waste`);
    if (!res.ok) throw new Error('Failed to fetch records');
    allRecords = await res.json();
  } catch (err) {
    console.warn('API error, using cached/demo records:', err);
  }
  renderRecordsTable(allRecords);
  renderRecentActivity(allRecords);
}

// 2. Fetch Analytics
async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/api/analytics`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    analyticsData = await res.json();
  } catch (err) {
    // Fallback calculation from records
    analyticsData = calculateLocalAnalytics(allRecords);
  }
  updateDashboardMetrics(analyticsData);
  renderDashboardCharts();
  renderAnalyticsCharts();
  updateCalculator(analyticsData.total_loss || 0);
}

// 3. Fetch Insights
async function fetchInsights() {
  try {
    const res = await fetch(`${API_BASE}/api/insights`);
    if (!res.ok) throw new Error('Failed to fetch insights');
    insightsData = await res.json();
  } catch (err) {
    insightsData = {
      score: 85,
      insights: ["🌱 Good progress! Keep tracking your meals consistently."],
      tips: [
        "Store dairy on middle shelves to avoid temperature changes.",
        "Label cooked meals with expiry dates to prioritize leftover use."
      ]
    };
  }
  updateInsightsView(insightsData);
}

// Local analytics fallback calculator
function calculateLocalAnalytics(records) {
  const totalItems = records.length;
  let totalQty = 0;
  let totalLoss = 0;
  const byCategory = {};
  const byReason = {};

  records.forEach(r => {
    const q = parseFloat(r.quantity) || 0;
    const p = parseFloat(r.price) || 0;
    totalQty += q;
    totalLoss += (q * p);

    const cat = r.category || 'Other';
    byCategory[cat] = (byCategory[cat] || 0) + q;

    const reas = r.reason || 'Other';
    byReason[reas] = (byReason[reas] || 0) + 1;
  });

  return {
    total_items: totalItems,
    total_quantity: Math.round(totalQty * 100) / 100,
    total_loss: Math.round(totalLoss * 100) / 100,
    top_category: Object.keys(byCategory)[0] || 'None',
    by_category: byCategory,
    by_reason: byReason,
    top_foods: []
  };
}

// Render Dashboard Metrics
function updateDashboardMetrics(data) {
  if (!data) return;

  const totalQtyEl = document.getElementById('dash-total-qty');
  if (totalQtyEl) totalQtyEl.innerHTML = `${(data.total_quantity || 0).toFixed(2)} <span class="metric-unit">kg</span>`;

  const totalLossEl = document.getElementById('dash-total-loss');
  if (totalLossEl) totalLossEl.textContent = `₹ ${(data.total_loss || 0).toFixed(2)}`;

  const totalRecordsEl = document.getElementById('dash-total-records');
  if (totalRecordsEl) totalRecordsEl.textContent = data.total_items || 0;

  const topCategoryPill = document.getElementById('top-category-pill');
  if (topCategoryPill) topCategoryPill.textContent = `Top: ${data.top_category || 'None'}`;
}

// Render Recent Waste Activity on Dashboard
function renderRecentActivity(records) {
  const container = document.getElementById('dash-recent-list');
  if (!container) return;

  if (!records || records.length === 0) {
    container.innerHTML = `<div class="empty-state">No waste records logged yet. Click "Log Waste Entry" to start.</div>`;
    return;
  }

  const recent = records.slice(0, 4);
  container.innerHTML = recent.map(item => {
    const icon = CATEGORY_ICONS[item.category] || '🍱';
    const loss = ((parseFloat(item.quantity) || 0) * (parseFloat(item.price) || 0)).toFixed(2);
    return `
      <div class="recent-item">
        <div class="recent-left">
          <div class="recent-icon">${icon}</div>
          <div>
            <div class="recent-name">${escapeHtml(item.food_name || 'Food item')}</div>
            <div class="recent-cat">${item.category} • ${item.reason}</div>
          </div>
        </div>
        <div class="recent-right">
          <div class="recent-loss">₹ ${loss}</div>
          <div class="recent-qty">${item.quantity} ${item.unit || 'kg'}</div>
        </div>
      </div>
    `;
  }).join('');
}

// Update Insights & Scores
function updateInsightsView(data) {
  if (!data) return;

  const score = data.score !== undefined ? data.score : 85;

  // Mini sidebar score
  const miniVal = document.getElementById('sidebar-score-val');
  const miniBar = document.getElementById('sidebar-score-bar');
  if (miniVal) miniVal.textContent = `${score}/100`;
  if (miniBar) miniBar.style.width = `${score}%`;

  // Dashboard score card
  const dashScore = document.getElementById('dash-score');
  const dashBadge = document.getElementById('dash-score-badge');
  if (dashScore) dashScore.textContent = `${score}/100`;
  if (dashBadge) {
    if (score >= 85) dashBadge.textContent = '🌟 Excellent';
    else if (score >= 70) dashBadge.textContent = '👍 Good';
    else if (score >= 50) dashBadge.textContent = '⚠️ Moderate';
    else dashBadge.textContent = '🚨 Needs Focus';
  }

  // Dashboard insights list
  const dashInsights = document.getElementById('dash-insights-list');
  if (dashInsights) {
    const list = data.insights && data.insights.length > 0 ? data.insights : data.tips;
    dashInsights.innerHTML = (list || []).slice(0, 3).map(tip => `
      <div class="insight-item">
        <span>${escapeHtml(tip)}</span>
      </div>
    `).join('');
  }

  // Insights View Elements
  const heroNum = document.getElementById('insights-score-num');
  const heroStatus = document.getElementById('insights-score-status');
  const circleProgress = document.getElementById('circle-progress-path');
  const circleText = document.getElementById('circle-score-text');

  if (heroNum) heroNum.textContent = `${score} / 100`;
  if (circleText) circleText.textContent = `${score}%`;
  if (circleProgress) circleProgress.setAttribute('stroke-dasharray', `${score}, 100`);

  if (heroStatus) {
    if (score >= 85) heroStatus.textContent = 'Outstanding Kitchen Management!';
    else if (score >= 70) heroStatus.textContent = 'Good Kitchen Progress, Room to Optimize';
    else if (score >= 50) heroStatus.textContent = 'Moderate Waste Habits Detected';
    else heroStatus.textContent = 'High Food Waste Detected — Action Needed';
  }

  // Dynamic Algorithmic Feed
  const dynamicFeed = document.getElementById('insights-dynamic-feed');
  if (dynamicFeed) {
    const dyn = data.insights && data.insights.length > 0 ? data.insights : [];
    if (dyn.length === 0) {
      dynamicFeed.innerHTML = `
        <div class="insight-pill-card">
          <span class="insight-icon">🌱</span>
          <span>Great job! No major repetitive waste pattern detected in your logs.</span>
        </div>
      `;
    } else {
      dynamicFeed.innerHTML = dyn.map(msg => `
        <div class="insight-pill-card">
          <span class="insight-icon">💡</span>
          <span>${escapeHtml(msg)}</span>
        </div>
      `).join('');
    }
  }
}

// Render Data Table in Records View
function renderRecordsTable(records) {
  const tbody = document.getElementById('records-table-body');
  const counter = document.getElementById('records-counter');
  if (!tbody) return;

  if (!records || records.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty-state">No food waste records found.</td></tr>`;
    if (counter) counter.textContent = 'Showing 0 records';
    return;
  }

  if (counter) counter.textContent = `Showing ${records.length} records`;

  tbody.innerHTML = records.map(r => {
    const loss = ((parseFloat(r.quantity) || 0) * (parseFloat(r.price) || 0)).toFixed(2);
    const dateFormatted = r.date ? r.date.split(' ')[0] : 'Today';
    return `
      <tr>
        <td style="font-weight: 700; color: var(--text-muted);">#${r.id}</td>
        <td style="font-weight: 700;">${escapeHtml(r.food_name || 'Item')}</td>
        <td><span class="badge-cat">${CATEGORY_ICONS[r.category] || '📦'} ${r.category}</span></td>
        <td><strong>${r.quantity}</strong> ${r.unit || 'kg'}</td>
        <td>₹ ${parseFloat(r.price || 0).toFixed(2)}</td>
        <td style="font-weight: 800; color: var(--danger);">₹ ${loss}</td>
        <td><span class="badge-reason">${escapeHtml(r.reason || 'Other')}</span></td>
        <td style="color: var(--text-muted); font-size: 12.5px;">${dateFormatted}</td>
        <td style="text-align: right;">
          <button class="btn-del" title="Delete record" onclick="openDeleteModal(${r.id}, '${escapeHtml(r.food_name || '')}')">🗑️</button>
        </td>
      </tr>
    `;
  }).join('');
}

// Filter Records Table
function filterRecordsTable() {
  const query = (document.getElementById('record-search')?.value || '').toLowerCase();
  const categoryFilter = document.getElementById('filter-category')?.value || 'ALL';
  const reasonFilter = document.getElementById('filter-reason')?.value || 'ALL';

  const filtered = allRecords.filter(r => {
    const matchesName = (r.food_name || '').toLowerCase().includes(query);
    const matchesCat = categoryFilter === 'ALL' || r.category === categoryFilter;
    const matchesReason = reasonFilter === 'ALL' || r.reason === reasonFilter;
    return matchesName && matchesCat && matchesReason;
  });

  renderRecordsTable(filtered);
}

// Form Quick Chips
function fillFoodName(name, category, price) {
  const nameInput = document.getElementById('food_name');
  const catInput = document.getElementById('category');
  const priceInput = document.getElementById('price');

  if (nameInput) nameInput.value = name;
  if (catInput) catInput.value = category;
  if (priceInput) priceInput.value = price;

  updateFormLivePreview();
}

// Live Form Preview Listeners
function setupFormPreviewListeners() {
  ['food_name', 'category', 'quantity', 'unit', 'price', 'reason'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', updateFormLivePreview);
      el.addEventListener('change', updateFormLivePreview);
    }
  });
}

function updateFormLivePreview() {
  const name = document.getElementById('food_name')?.value || '—';
  const cat = document.getElementById('category')?.value || '—';
  const qty = parseFloat(document.getElementById('quantity')?.value) || 0;
  const unit = document.getElementById('unit')?.value || 'kg';
  const price = parseFloat(document.getElementById('price')?.value) || 0;
  const reason = document.getElementById('reason')?.value || '—';

  const loss = (qty * price).toFixed(2);

  const prevName = document.getElementById('preview-name');
  const prevCat = document.getElementById('preview-category');
  const prevQty = document.getElementById('preview-qty');
  const prevReason = document.getElementById('preview-reason');
  const prevLoss = document.getElementById('preview-loss');

  if (prevName) prevName.textContent = name;
  if (prevCat) prevCat.textContent = cat;
  if (prevQty) prevQty.textContent = `${qty.toFixed(2)} ${unit}`;
  if (prevReason) prevReason.textContent = reason;
  if (prevLoss) prevLoss.textContent = `₹ ${loss}`;
}

function resetFormPreview() {
  setTimeout(updateFormLivePreview, 50);
}

// Handle Form Submission (Add Record)
async function handleFormSubmit(e) {
  e.preventDefault();
  const form = document.getElementById('add-waste-form');
  const btn = document.getElementById('btn-save-record');

  const food_name = document.getElementById('food_name').value.trim();
  const category = document.getElementById('category').value;
  const quantity = parseFloat(document.getElementById('quantity').value);
  const unit = document.getElementById('unit').value;
  const price = parseFloat(document.getElementById('price').value);
  const reason = document.getElementById('reason').value;

  if (!food_name || !category || isNaN(quantity) || isNaN(price)) {
    showToast('Please fill all required fields correctly', 'error');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Saving...';

  const payload = {
    food_name,
    category,
    quantity,
    unit,
    price,
    reason
  };

  try {
    const res = await fetch(`${API_BASE}/api/waste`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Failed to save record');

    showToast(`Successfully added "${food_name}"!`, 'success');
    form.reset();
    resetFormPreview();

    // Reload all data & switch to dashboard or records
    await loadAllData();
    switchView('dashboard');
  } catch (err) {
    showToast('Error saving record. Please ensure backend is running.', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>＋</span> Save Waste Record';
  }
}

// Delete Record Modal
function openDeleteModal(recordId, foodName) {
  currentDeletingId = recordId;
  const modal = document.getElementById('delete-modal');
  const msg = document.getElementById('delete-modal-msg');
  if (msg) msg.textContent = `Are you sure you want to delete "${foodName}" (Record #${recordId})?`;
  if (modal) modal.classList.add('active');

  const confirmBtn = document.getElementById('confirm-delete-btn');
  if (confirmBtn) {
    confirmBtn.onclick = executeDelete;
  }
}

function closeDeleteModal() {
  const modal = document.getElementById('delete-modal');
  if (modal) modal.classList.remove('active');
  currentDeletingId = null;
}

async function executeDelete() {
  if (!currentDeletingId) return;
  const id = currentDeletingId;
  closeDeleteModal();

  try {
    const res = await fetch(`${API_BASE}/api/waste/${id}`, {
      method: 'DELETE'
    });

    if (!res.ok) throw new Error('Delete failed');

    showToast(`Record #${id} deleted successfully.`, 'success');
    await loadAllData();
  } catch (err) {
    showToast('Could not delete record from backend.', 'error');
  }
}

// Export Records to CSV
function exportRecordsCSV() {
  if (!allRecords || allRecords.length === 0) {
    showToast('No records available to export.', 'error');
    return;
  }

  const headers = ['ID', 'Food Name', 'Category', 'Quantity', 'Unit', 'Price', 'Reason', 'Date'];
  const rows = allRecords.map(r => [
    r.id,
    `"${(r.food_name || '').replace(/"/g, '""')}"`,
    r.category,
    r.quantity,
    r.unit,
    r.price,
    `"${(r.reason || '').replace(/"/g, '""')}"`,
    r.date
  ]);

  const csvContent = 'data:text/csv;charset=utf-8,' 
    + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `foodwise_waste_records_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast('Exported CSV successfully!', 'success');
}

// Financial Calculator
function updateCalculator(currentLoss) {
  const currentLossEl = document.getElementById('calc-current-loss');
  if (currentLossEl) currentLossEl.textContent = `₹ ${currentLoss.toFixed(2)}`;

  const s20 = document.getElementById('calc-save-20');
  const s50 = document.getElementById('calc-save-50');
  const s80 = document.getElementById('calc-save-80');

  if (s20) s20.textContent = `Save ₹ ${(currentLoss * 0.20).toFixed(2)}`;
  if (s50) s50.textContent = `Save ₹ ${(currentLoss * 0.50).toFixed(2)}`;
  if (s80) s80.textContent = `Save ₹ ${(currentLoss * 0.80).toFixed(2)}`;
}

// Chart.js Visualizations
function renderDashboardCharts() {
  if (!window.Chart || !analyticsData) return;

  const cats = analyticsData.by_category || {};
  const catLabels = Object.keys(cats);
  const catValues = Object.values(cats);

  const reasons = analyticsData.by_reason || {};
  const reasonLabels = Object.keys(reasons);
  const reasonValues = Object.values(reasons);

  // Category Doughnut Chart
  const ctxCat = document.getElementById('dashCategoryChart');
  if (ctxCat) {
    if (dashCategoryChart) dashCategoryChart.destroy();
    dashCategoryChart = new Chart(ctxCat, {
      type: 'doughnut',
      data: {
        labels: catLabels.length ? catLabels : ['No Data'],
        datasets: [{
          data: catValues.length ? catValues : [1],
          backgroundColor: [
            '#C86D7D', '#E4A38B', '#2E7D59', '#BA5868',
            '#D9822B', '#8E4351', '#EDB39E', '#7A696F'
          ],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: 'Plus Jakarta Sans', size: 11 } } }
        },
        cutout: '65%'
      }
    });
  }

  // Reason Polar / Bar Chart
  const ctxReason = document.getElementById('dashReasonChart');
  if (ctxReason) {
    if (dashReasonChart) dashReasonChart.destroy();
    dashReasonChart = new Chart(ctxReason, {
      type: 'pie',
      data: {
        labels: reasonLabels.length ? reasonLabels : ['No Data'],
        datasets: [{
          data: reasonValues.length ? reasonValues : [1],
          backgroundColor: [
            '#E4A38B', '#C86D7D', '#DE5252', '#38956B',
            '#B38E75', '#A39399'
          ],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { family: 'Plus Jakarta Sans', size: 11 } } }
        }
      }
    });
  }
}

function renderAnalyticsCharts() {
  if (!window.Chart || !analyticsData) return;

  const cats = analyticsData.by_category || {};
  const catLabels = Object.keys(cats);
  const catValues = Object.values(cats);

  const reasons = analyticsData.by_reason || {};
  const reasonLabels = Object.keys(reasons);
  const reasonValues = Object.values(reasons);

  // Full Bar Chart
  const ctxBar = document.getElementById('analyticsBarChart');
  if (ctxBar) {
    if (analyticsBarChart) analyticsBarChart.destroy();
    analyticsBarChart = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: catLabels.length ? catLabels : ['None'],
        datasets: [{
          label: 'Quantity Wasted (kg)',
          data: catValues.length ? catValues : [0],
          backgroundColor: '#C86D7D',
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(200, 109, 125, 0.08)' } },
          x: { grid: { display: false } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // Analytics Pie Chart
  const ctxPie = document.getElementById('analyticsPieChart');
  if (ctxPie) {
    if (analyticsPieChart) analyticsPieChart.destroy();
    analyticsPieChart = new Chart(ctxPie, {
      type: 'pie',
      data: {
        labels: reasonLabels.length ? reasonLabels : ['None'],
        datasets: [{
          data: reasonValues.length ? reasonValues : [1],
          backgroundColor: [
            '#C86D7D', '#E4A38B', '#2E7D59', '#BA5868',
            '#D9822B', '#DE5252'
          ],
          borderWidth: 2,
          borderColor: '#FFFFFF'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12 } }
        }
      }
    });
  }

  // Top Foods List
  const topFoodsList = document.getElementById('top-foods-list');
  if (topFoodsList) {
    const foods = analyticsData.top_foods || [];
    if (foods.length === 0) {
      topFoodsList.innerHTML = `<div class="empty-state">No repeat foods identified yet.</div>`;
    } else {
      topFoodsList.innerHTML = foods.map(f => `
        <div class="top-food-row">
          <div>
            <span class="top-food-name">${escapeHtml(f.name)}</span>
            <span style="font-size: 12px; color: var(--text-muted); margin-left: 8px;">(${f.count} logs)</span>
          </div>
          <span class="top-food-stat">${f.quantity} kg</span>
        </div>
      `).join('');
    }
  }
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : (type === 'error' ? '❌' : 'ℹ️')}</span>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Utility: HTML Escaping
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
