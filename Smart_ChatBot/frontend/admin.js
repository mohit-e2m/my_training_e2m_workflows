/**
 * Admin Dashboard JavaScript
 * Handles data fetching, display, and interactions
 */

const API_BASE_URL = 'http://localhost:5000/api';

// State
let allLeads = [];
let stats = {};

// DOM Elements
const totalLeadsEl = document.getElementById('totalLeads');
const totalMessagesEl = document.getElementById('totalMessages');
const avgMessagesEl = document.getElementById('avgMessages');
const leadsTableBody = document.getElementById('leadsTableBody');
const topQuestionsList = document.getElementById('topQuestionsList');
const searchInput = document.getElementById('searchInput');
const refreshBtn = document.getElementById('refreshBtn');
const exportBtn = document.getElementById('exportBtn');
const chatHistoryModal = document.getElementById('chatHistoryModal');
const modalOverlay = document.getElementById('modalOverlay');
const modalClose = document.getElementById('modalClose');
const modalUserName = document.getElementById('modalUserName');
const modalBody = document.getElementById('modalBody');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    refreshBtn.addEventListener('click', loadAllData);
    exportBtn.addEventListener('click', exportToCSV);
    searchInput.addEventListener('input', handleSearch);
    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);
}

// Load all data
async function loadAllData() {
    await Promise.all([
        loadLeads(),
        loadStats()
    ]);
}

// Load leads from API
async function loadLeads() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/leads`);
        const data = await response.json();

        if (data.success) {
            allLeads = data.leads;
            displayLeads(allLeads);
        } else {
            showError('Failed to load leads');
        }
    } catch (error) {
        console.error('Error loading leads:', error);
        showError('Failed to connect to server');
    }
}

// Load stats from API
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/stats`);
        const data = await response.json();

        if (data.success) {
            stats = data.stats;
            displayStats(stats);
            displayTopQuestions(stats.top_questions || []);
        } else {
            showError('Failed to load stats');
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showError('Failed to connect to server');
    }
}

// Display stats
function displayStats(stats) {
    totalLeadsEl.textContent = stats.total_users || 0;
    totalMessagesEl.textContent = stats.total_messages || 0;

    const avg = stats.total_users > 0
        ? (stats.total_messages / stats.total_users).toFixed(1)
        : 0;
    avgMessagesEl.textContent = avg;
}

// Display leads in table
function displayLeads(leads) {
    if (leads.length === 0) {
        leadsTableBody.innerHTML = '<tr><td colspan="7" class="loading-row">No leads found</td></tr>';
        return;
    }

    leadsTableBody.innerHTML = leads.map(lead => `
        <tr>
            <td>${lead.id}</td>
            <td><strong>${escapeHtml(lead.name)}</strong></td>
            <td>${escapeHtml(lead.email)}</td>
            <td><span style="font-weight: 600; color: var(--primary-color);">${lead.message_count}</span></td>
            <td>${formatDate(lead.created_at)}</td>
            <td>${formatDate(lead.last_active)}</td>
            <td>
                <button class="btn-view-history" onclick="viewChatHistory(${lead.id}, '${escapeHtml(lead.name)}')">
                    View History
                </button>
            </td>
        </tr>
    `).join('');
}

// Display top questions
function displayTopQuestions(questions) {
    if (questions.length === 0) {
        topQuestionsList.innerHTML = '<p class="loading-text">No questions yet</p>';
        return;
    }

    topQuestionsList.innerHTML = questions.map(q => `
        <div class="question-item">
            <span class="question-text">${escapeHtml(q.question)}</span>
            <span class="question-count">${q.count}</span>
        </div>
    `).join('');
}

// View chat history for a user
async function viewChatHistory(userId, userName) {
    try {
        const response = await fetch(`${API_BASE_URL}/user/history/${userId}`);
        const data = await response.json();

        if (data.success) {
            modalUserName.textContent = `Chat History - ${userName}`;
            displayChatHistory(data.history);
            openModal();
        } else {
            alert('Failed to load chat history');
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
        alert('Failed to connect to server');
    }
}

// Display chat history in modal
function displayChatHistory(history) {
    if (history.length === 0) {
        modalBody.innerHTML = '<p class="loading-text">No chat history yet</p>';
        return;
    }

    // Reverse to show oldest first
    const sortedHistory = [...history].reverse();

    modalBody.innerHTML = sortedHistory.map(msg => `
        <div class="chat-history-item">
            <div class="chat-question">
                <strong>Q:</strong> ${escapeHtml(msg.question)}
            </div>
            <div class="chat-answer">
                <strong>A:</strong> ${escapeHtml(msg.answer)}
            </div>
            <div class="chat-meta">
                <span class="chat-source">${msg.source || 'unknown'}</span>
                <span>${formatDateTime(msg.timestamp)}</span>
            </div>
        </div>
    `).join('');
}

// Handle search
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase().trim();

    if (!searchTerm) {
        displayLeads(allLeads);
        return;
    }

    const filtered = allLeads.filter(lead =>
        lead.name.toLowerCase().includes(searchTerm) ||
        lead.email.toLowerCase().includes(searchTerm)
    );

    displayLeads(filtered);
}

// Export to CSV
function exportToCSV() {
    if (allLeads.length === 0) {
        alert('No data to export');
        return;
    }

    // Create CSV content
    const headers = ['ID', 'Name', 'Email', 'Messages', 'Joined', 'Last Active'];
    const rows = allLeads.map(lead => [
        lead.id,
        lead.name,
        lead.email,
        lead.message_count,
        formatDate(lead.created_at),
        formatDate(lead.last_active)
    ]);

    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chatbot_leads_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Modal functions
function openModal() {
    chatHistoryModal.classList.add('active');
}

function closeModal() {
    chatHistoryModal.classList.remove('active');
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    console.error(message);
    // Could add toast notification here
}
