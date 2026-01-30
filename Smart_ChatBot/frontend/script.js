/**
 * Smart Chatbot Frontend Script with User Registration
 * Handles UI interactions, user registration, API calls, and message display
 */

const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const chatbotButton = document.getElementById('chatbotButton');
const chatbotWindow = document.getElementById('chatbotWindow');
const chatbotHistory = document.getElementById('chatbotHistory');
const historyDropdown = document.getElementById('historyDropdown');
const historyList = document.getElementById('historyList');
const chatbotClose = document.getElementById('chatbotClose');
const chatbotBody = document.getElementById('chatbotBody');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const questionsContainer = document.getElementById('questionsContainer');
const chatbotBadge = document.getElementById('chatbotBadge');
const inlineRegistration = document.getElementById('inlineRegistration');
const chatWelcome = document.getElementById('chatWelcome');
const registrationForm = document.getElementById('registrationFormElement');

// State
let isOpen = false;
let predefinedQuestions = [];
let currentUser = null; // {id, name, email}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkUserSession();
    setupEventListeners();
});

// Check for existing user session
function checkUserSession() {
    const savedUser = getUserSession();

    if (savedUser) {
        currentUser = savedUser;
        console.log('User session found:', currentUser);
    } else {
        console.log('No user session found');
    }

    // Always load predefined questions
    loadPredefinedQuestions();
}

// Event Listeners
function setupEventListeners() {
    chatbotButton.addEventListener('click', handleChatbotButtonClick);
    chatbotClose.addEventListener('click', toggleChatbot);
    sendButton.addEventListener('click', handleSendMessage);
    registrationForm.addEventListener('submit', handleRegistration);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });

    // History Toggle
    if (chatbotHistory) {
        chatbotHistory.addEventListener('click', (e) => {
            e.stopPropagation();
            historyDropdown.classList.toggle('active');
            chatbotHistory.classList.toggle('active');
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (historyDropdown && historyDropdown.classList.contains('active')) {
            if (!historyDropdown.contains(e.target) && !chatbotHistory.contains(e.target)) {
                historyDropdown.classList.remove('active');
                chatbotHistory.classList.remove('active');
            }
        }
    });
}

// Handle chatbot button click
function handleChatbotButtonClick() {
    toggleChatbot();

    // Show appropriate content based on user session
    if (!currentUser) {
        showInlineRegistration();
    } else {
        // Update header with user's name for returning users
        updateChatHeader(currentUser.name);
        showChatWelcome();

        // Fetch and display recent questions for returning users
        fetchRecentQuestions(currentUser.id);
    }
}

// Show inline registration form
function showInlineRegistration() {
    inlineRegistration.style.display = 'block';
    chatWelcome.style.display = 'none';
    chatInput.disabled = true;
    chatInput.placeholder = 'Please register first...';
    sendButton.disabled = true;

    // Focus on name input
    setTimeout(() => {
        document.getElementById('userName').focus();
    }, 300);
}

// Show chat welcome message
function showChatWelcome() {
    inlineRegistration.style.display = 'none';
    chatWelcome.style.display = 'block';
    chatInput.disabled = false;
    chatInput.placeholder = 'Type your message...';
    sendButton.disabled = false;
}

// Handle user registration
async function handleRegistration(e) {
    e.preventDefault();

    const name = document.getElementById('userName').value.trim();
    const email = document.getElementById('userEmail').value.trim();

    if (!name || !email) {
        alert('Please enter both name and email');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/user/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email })
        });

        const data = await response.json();

        if (data.success) {
            currentUser = {
                id: data.user_id,
                name: data.name,
                email: data.email
            };

            // Save to localStorage
            saveUserSession(currentUser);

            // Hide registration form and show chat
            inlineRegistration.style.display = 'none';

            // Update chat header with user name
            updateChatHeader(data.name);

            // Display recent questions if any
            if (data.recent_questions && data.recent_questions.length > 0) {
                displayRecentQuestions(data.recent_questions);
            } else {
                // Show welcome message
                showChatWelcome();
            }

            // Enable chat input
            chatInput.disabled = false;
            chatInput.placeholder = 'Type your message...';
            sendButton.disabled = false;
            chatInput.focus();
        } else {
            alert('Registration failed: ' + data.error);
        }
    } catch (error) {
        console.error('Error registering user:', error);
        alert('Failed to register. Please try again.');
    }
}

// Save user session to localStorage
function saveUserSession(user) {
    localStorage.setItem('chatbot_user', JSON.stringify(user));
}

// Get user session from localStorage
function getUserSession() {
    const userStr = localStorage.getItem('chatbot_user');
    return userStr ? JSON.parse(userStr) : null;
}

// Update chat header with user name
function updateChatHeader(name) {
    const headerText = document.querySelector('.header-text');
    if (headerText) {
        // Check if greeting already exists
        let greeting = headerText.querySelector('.user-greeting');
        if (!greeting) {
            greeting = document.createElement('p');
            greeting.className = 'user-greeting';
            headerText.appendChild(greeting);
        }
        greeting.textContent = `Hello, ${name}`;
    }
}

// Fetch recent questions for returning users
async function fetchRecentQuestions(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/user/history/${userId}`);
        const data = await response.json();

        if (data.success && data.history && data.history.length > 0) {
            // Show only the last 5 questions
            const recentQuestions = data.history.slice(-5);
            displayRecentQuestions(recentQuestions);
        }
    } catch (error) {
        console.error('Error fetching recent questions:', error);
        // Don't show error to user, just continue without recent questions
    }
}

// Display recent questions in dropdown
function displayRecentQuestions(questions) {
    if (questions.length === 0) {
        historyList.innerHTML = '<div class="empty-history">No recent questions</div>';
        showChatWelcome();
        return;
    }

    showChatWelcome();
    historyList.innerHTML = ''; // Clear existing

    questions.reverse().forEach(msg => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        // HTML escape the question for safety
        const safeQuestion = msg.question.replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
        historyItem.textContent = safeQuestion;
        historyItem.addEventListener('click', () => {
            sendMessage(msg.question);
            historyDropdown.classList.remove('active');
            chatbotHistory.classList.remove('active');
        });
        historyList.appendChild(historyItem);
    });
}

// Toggle Chatbot Window
function toggleChatbot() {
    isOpen = !isOpen;

    if (isOpen) {
        chatbotWindow.classList.add('open');
        chatbotButton.style.display = 'none';
        chatInput.focus();
        chatbotBadge.style.display = 'none';
    } else {
        chatbotWindow.classList.remove('open');
        chatbotButton.style.display = 'flex';
    }
}

// Load Predefined Questions
async function loadPredefinedQuestions() {
    try {
        const response = await fetch(`${API_BASE_URL}/questions`);
        const data = await response.json();

        if (data.success) {
            predefinedQuestions = data.questions;
            displayPredefinedQuestions(data.questions);
        }
    } catch (error) {
        console.error('Error loading questions:', error);
        displayErrorMessage('Failed to load quick questions. Please try typing your question.');
    }
}

// Display Predefined Questions
function displayPredefinedQuestions(questions) {
    questionsContainer.innerHTML = '';

    // Show first 5 questions initially
    const questionsToShow = questions.slice(0, 5);

    questionsToShow.forEach(q => {
        const chip = document.createElement('button');
        chip.className = 'question-chip';
        chip.textContent = q.question;
        chip.addEventListener('click', () => {
            sendMessage(q.question);
        });
        questionsContainer.appendChild(chip);
    });
}

// Handle Send Message
function handleSendMessage() {
    const message = chatInput.value.trim();

    if (message) {
        sendMessage(message);
        chatInput.value = '';
    }
}

// Send Message
async function sendMessage(message) {
    // Display user message
    addMessage(message, 'user');

    // Hide predefined questions after first message
    const questionsSection = document.getElementById('predefinedQuestions');
    if (questionsSection) {
        questionsSection.style.display = 'none';
    }

    // Hide recent questions section if exists
    const recentSection = document.querySelector('.recent-questions-section');
    if (recentSection) {
        recentSection.style.display = 'none';
    }

    // Show typing indicator
    const typingIndicator = addTypingIndicator();

    try {
        const requestBody = { message };

        // Add user_id if user is logged in
        if (currentUser) {
            requestBody.user_id = currentUser.id;
        }

        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        // Remove typing indicator
        typingIndicator.remove();

        if (data.success) {
            // Add bot response with typing animation
            addMessageWithTyping(data.response, 'bot');

            // Show dynamic "Need Help?" button if bot suggests support
            if (data.suggest_support) {
                addDynamicSupportButton(message);
            }

            // Log source for debugging
            console.log('Response source:', data.source);
            if (data.metadata) {
                console.log('Metadata:', data.metadata);
            }
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        typingIndicator.remove();
        addMessage('Sorry, I\'m having trouble connecting. Please check if the backend server is running.', 'bot');
    }
}

// Add dynamic support button after bot message
function addDynamicSupportButton(userQuery) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot-message'; // usage of chat-message instead of message

    const buttonContainer = document.createElement('div');
    buttonContainer.style.cssText = 'display: flex; justify-content: flex-start; margin-top: 0.5rem; width: 100%;';

    const helpButton = document.createElement('button');
    helpButton.className = 'dynamic-help-button';
    helpButton.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 16px; height: 16px;">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        Need Help?
    `;

    helpButton.addEventListener('click', () => {
        openSupportModalWithQuery(userQuery);
    });

    buttonContainer.appendChild(helpButton);
    messageDiv.appendChild(buttonContainer);
    chatbotBody.appendChild(messageDiv);
    scrollToBottom();
}

// Convert Markdown to HTML
function convertMarkdownToHTML(text) {
    // Convert **bold** to <strong>
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert email addresses to clickable links
    text = text.replace(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)/gi, '<a href="mailto:$1" style="color: #00d4ff; text-decoration: underline;">$1</a>');

    // Convert URLs to clickable links
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" style="color: #00d4ff; text-decoration: underline;">$1</a>');

    // Split into lines for processing
    const lines = text.split('\n');
    let result = [];
    let inOrderedList = false;
    let inUnorderedList = false;
    let currentParagraph = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmedLine = line.trim();

        // Check for numbered list (1. item)
        if (/^\d+\.\s+/.test(trimmedLine)) {
            // Close any open paragraph
            if (currentParagraph.length > 0) {
                result.push('<p>' + currentParagraph.join(' ') + '</p>');
                currentParagraph = [];
            }

            if (!inOrderedList) {
                if (inUnorderedList) {
                    result.push('</ul>');
                    inUnorderedList = false;
                }
                result.push('<ol>');
                inOrderedList = true;
            }
            result.push('<li>' + trimmedLine.replace(/^\d+\.\s+/, '') + '</li>');
        }
        // Check for bullet list (* item or - item)
        else if (/^[\*\-]\s+/.test(trimmedLine)) {
            // Close any open paragraph
            if (currentParagraph.length > 0) {
                result.push('<p>' + currentParagraph.join(' ') + '</p>');
                currentParagraph = [];
            }

            if (!inUnorderedList) {
                if (inOrderedList) {
                    result.push('</ol>');
                    inOrderedList = false;
                }
                result.push('<ul>');
                inUnorderedList = true;
            }
            result.push('<li>' + trimmedLine.replace(/^[\*\-]\s+/, '') + '</li>');
        }
        // Empty line - paragraph break
        else if (trimmedLine === '') {
            // Close any open lists
            if (inOrderedList) {
                result.push('</ol>');
                inOrderedList = false;
            }
            if (inUnorderedList) {
                result.push('</ul>');
                inUnorderedList = false;
            }

            // Close current paragraph if it has content
            if (currentParagraph.length > 0) {
                result.push('<p>' + currentParagraph.join(' ') + '</p>');
                currentParagraph = [];
            }
        }
        // Regular line - add to current paragraph
        else {
            // Close any open lists
            if (inOrderedList) {
                result.push('</ol>');
                inOrderedList = false;
            }
            if (inUnorderedList) {
                result.push('</ul>');
                inUnorderedList = false;
            }

            currentParagraph.push(trimmedLine);
        }
    }

    // Close any remaining paragraph
    if (currentParagraph.length > 0) {
        result.push('<p>' + currentParagraph.join(' ') + '</p>');
    }

    // Close any open lists
    if (inOrderedList) result.push('</ol>');
    if (inUnorderedList) result.push('</ul>');

    return result.join('');
}

// Add Message to Chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');

    // For bot messages, convert markdown to HTML
    if (sender === 'bot') {
        textDiv.innerHTML = convertMarkdownToHTML(text);
    } else {
        textDiv.textContent = text;
    }

    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(contentDiv);
    chatbotBody.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();

    return messageDiv;
}

// Add Message with Typing Animation
function addMessageWithTyping(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textDiv = document.createElement('div');

    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(contentDiv);
    chatbotBody.appendChild(messageDiv);

    // For bot messages, show formatted HTML immediately for better readability
    if (sender === 'bot') {
        textDiv.innerHTML = convertMarkdownToHTML(text);
        scrollToBottom();
    } else {
        // For user messages, use typing animation
        textDiv.textContent = '';
        let index = 0;
        const typingSpeed = 20;

        function typeCharacter() {
            if (index < text.length) {
                textDiv.textContent += text.charAt(index);
                index++;
                scrollToBottom();
                setTimeout(typeCharacter, typingSpeed);
            }
        }
        typeCharacter();
    }

    return messageDiv;
}

// Add Typing Indicator
function addTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot-message';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';

    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        indicator.appendChild(dot);
    }

    messageDiv.appendChild(indicator);
    chatbotBody.appendChild(messageDiv);

    scrollToBottom();

    return messageDiv;
}

// Display Error Message
function displayErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.padding = '0.75rem';
    errorDiv.style.background = '#fee2e2';
    errorDiv.style.color = '#991b1b';
    errorDiv.style.borderRadius = '0.5rem';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.textContent = message;

    questionsContainer.appendChild(errorDiv);
}

// Scroll to Bottom
function scrollToBottom() {
    chatbotBody.scrollTop = chatbotBody.scrollHeight;
}

// Auto-open chatbot after 3 seconds (optional - remove if not desired)
setTimeout(() => {
    if (!isOpen) {
        // Pulse animation on badge
        chatbotBadge.style.animation = 'bounce 1s infinite';
    }
}, 3000);

// ===== Inline Support Form =====
let activeSupportForm = null;

// Show inline support form
function showInlineSupportForm(prefillQuery = '') {
    if (!currentUser) {
        addMessage('Please register first before contacting support.', 'bot');
        return;
    }

    // Remove any existing support form
    if (activeSupportForm) {
        activeSupportForm.remove();
        activeSupportForm = null;
    }

    // Hide predefined questions
    const predefinedQuestions = document.getElementById('predefinedQuestions');
    if (predefinedQuestions) {
        predefinedQuestions.style.display = 'none';
    }

    // Create support form element
    const supportFormContainer = document.createElement('div');
    supportFormContainer.className = 'inline-support';
    supportFormContainer.innerHTML = `
        <div class="chat-message bot-message">
            <div class="message-content">
                <p><strong>Contact Support</strong></p>
                <p>Can't find what you're looking for? Send us a message and we'll get back to you shortly.</p>
            </div>
        </div>
        <div class="support-form-inline">
            <form id="dynamicSupportForm">
                <div class="form-group-inline">
                    <label for="dynamicSupportSubject">Subject</label>
                    <input type="text" id="dynamicSupportSubject" name="subject" placeholder="Brief description" required>
                </div>
                <div class="form-group-inline">
                    <label for="dynamicSupportMessage">Message</label>
                    <textarea id="dynamicSupportMessage" name="message" rows="4" placeholder="Describe your issue or question..." required></textarea>
                </div>
                <button type="submit" class="btn-submit-inline">
                    Send Message →
                </button>
            </form>
        </div>
    `;

    // Append to chat body
    chatbotBody.appendChild(supportFormContainer);
    activeSupportForm = supportFormContainer;

    // Pre-fill if query provided
    if (prefillQuery) {
        document.getElementById('dynamicSupportSubject').value = prefillQuery.substring(0, 100);
        document.getElementById('dynamicSupportMessage').value = prefillQuery;
    }

    // Setup form submission handler
    const form = document.getElementById('dynamicSupportForm');
    form.addEventListener('submit', handleSupportFormSubmit);

    // Scroll to bottom with delay to ensure form is rendered
    setTimeout(() => {
        scrollToBottom();
        // Focus on subject field
        document.getElementById('dynamicSupportSubject').focus();
    }, 100);
}

// Handle support form submission
async function handleSupportFormSubmit(e) {
    e.preventDefault();

    const subject = document.getElementById('dynamicSupportSubject').value.trim();
    const message = document.getElementById('dynamicSupportMessage').value.trim();

    if (!subject || !message) {
        return;
    }

    // Disable form
    const submitBtn = e.target.querySelector('.btn-submit-inline');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending...';

    // Remove form
    if (activeSupportForm) {
        activeSupportForm.remove();
        activeSupportForm = null;
    }

    // Show loading indicator
    const loadingIndicator = addTypingIndicator();

    // Scroll to show loading indicator
    setTimeout(() => scrollToBottom(), 100);

    try {
        const response = await fetch(`${API_BASE_URL}/support/ticket`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                subject: subject,
                message: message
            })
        });

        const data = await response.json();

        // Remove loading indicator
        loadingIndicator.remove();

        if (data.success) {
            // Show success message
            addMessage(`✓ Your support ticket has been submitted successfully! We'll get back to you at ${currentUser.email} shortly.`, 'bot');

            // Scroll to show success message
            setTimeout(() => scrollToBottom(), 100);
        } else {
            addMessage('Sorry, there was an error submitting your ticket. Please try again.', 'bot');
            setTimeout(() => scrollToBottom(), 100);
        }
    } catch (error) {
        console.error('Error submitting support ticket:', error);
        loadingIndicator.remove();
        addMessage('Sorry, there was an error submitting your ticket. Please try again.', 'bot');
        setTimeout(() => scrollToBottom(), 100);
    }
}

// Update the dynamic support button to use inline form
function openSupportModalWithQuery(query) {
    showInlineSupportForm(query);
}


// Admin login function
function openAdminLogin(event) {
    event.preventDefault();

    const username = prompt('Enter admin username:');
    if (username === null) return; // User cancelled

    const password = prompt('Enter admin password:');
    if (password === null) return; // User cancelled

    if (username === 'admin' && password === 'admin') {
        window.location.href = 'admin.html';
    } else {
        alert('Invalid credentials. Please try again.');
    }
}
