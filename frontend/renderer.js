// DOM Elements
const authScreen = document.getElementById('auth-screen');
const appContainer = document.getElementById('app-container');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const authError = document.getElementById('auth-error');
const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const displayUser = document.getElementById('display-user');
const sidebar = document.getElementById('sidebar');
const collapseBtn = document.getElementById('collapse-btn');
const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');

const API_BASE = "http://127.0.0.1:8000";
let ws;
let currentAiMessageDiv = null;
let sidebarCollapsed = false;
let currentConversationId = null; 

console.log("✅ DOM Elements loaded successfully");

// --- 1. AUTHENTICATION ---
async function authenticate(action) {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!username || !password) {
        console.warn("Username or password is empty");
        return;
    }

    try {
        let response;
        if (action === 'register') {
            response = await fetch(`${API_BASE}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
        } else {
            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);
            response = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });
        }

        const data = await response.json();

        if (response.ok) {
            if (action === 'register') {
                authError.style.color = "#a8d4ff";
                authError.innerText = "Registered successfully! Now click Login.";
            } else {
                authError.innerText = "";
                displayUser.innerText = username;
                connectWebSocket(data.access_token);

                authScreen.classList.add('hidden');
                appContainer.classList.remove('hidden');
                sidebarCollapsed = false;
                sidebar.classList.remove('collapsed');
                collapseBtn.innerText = '✕';

                
                await initConversations(username);
            }
        } else {
            authError.innerText = data.detail || "Authentication failed.";
        }
    } catch (err) {
        authError.innerText = "Cannot connect to backend.";
        console.error("Authentication error:", err);
    }
}

document.getElementById('login-btn').addEventListener('click', () => authenticate('login'));
document.getElementById('register-btn').addEventListener('click', () => authenticate('register'));


// --- 1.5 SIDEBAR COLLAPSE/EXPAND TOGGLE ---
collapseBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    sidebarCollapsed = true;
    sidebar.classList.add('collapsed');
    toggleSidebarBtn.style.display = 'flex';
});

toggleSidebarBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    sidebarCollapsed = false;
    sidebar.classList.remove('collapsed');
    toggleSidebarBtn.style.display = 'none';
});


// --- 2. WEBSOCKET & STREAMING LOGIC ---
function connectWebSocket(token) {
    ws = new WebSocket(`ws://127.0.0.1:8000/ws?token=${token}`);

    ws.onmessage = (event) => {
        const chunk = event.data;

        if (chunk === "<END_OF_STREAM>") {
            currentAiMessageDiv = null;
            return;
        }

        if (!currentAiMessageDiv) {
            currentAiMessageDiv = document.createElement('div');
            currentAiMessageDiv.classList.add('msg', 'msg-ai');
            const content = document.createElement('div');
            content.classList.add('msg-content');
            currentAiMessageDiv.appendChild(content);
            chatBox.appendChild(currentAiMessageDiv);
        }

        currentAiMessageDiv.querySelector('.msg-content').innerText += chunk;
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    ws.onerror = (error) => console.error("WebSocket error:", error);
    ws.onclose = () => console.log("WebSocket closed");
}


// --- 3. SENDING MESSAGES ---
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;

    
    if (!currentConversationId) {
        currentConversationId = await createConversation(displayUser.innerText);
        await loadSidebarHistory(displayUser.innerText); // refresh sidebar to show the new chat
    }

    // 1. Show user message
    appendMessage('user', text);

    // 2. Send to backend, tagged with the conversation id
    ws.send(JSON.stringify({ conversation_id: currentConversationId, message: text }));

    // 3. Clean up
    messageInput.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
    currentAiMessageDiv = null;

    // 4. Refresh sidebar (title may have just been set from this first message)
    loadSidebarHistory(displayUser.innerText);
}

function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('msg', role === 'user' ? 'msg-user' : 'msg-ai');
    const content = document.createElement('div');
    content.classList.add('msg-content');
    content.innerText = text;
    msgDiv.appendChild(content);
    chatBox.appendChild(msgDiv);
}

document.getElementById('send-btn').addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});


// --- 4. SIDEBAR BUTTONS LOGIC ---
document.getElementById('new-chat-btn').addEventListener('click', async () => {
    currentConversationId = await createConversation(displayUser.innerText);
    chatBox.innerHTML = "";
    currentAiMessageDiv = null;
    await loadSidebarHistory(displayUser.innerText);
});

document.getElementById('logout-btn').addEventListener('click', () => {
    if (ws) ws.close();
    chatBox.innerHTML = "";
    usernameInput.value = "";
    passwordInput.value = "";
    currentConversationId = null;

    appContainer.classList.add('hidden');
    authScreen.classList.remove('hidden');
    sidebar.classList.remove('collapsed');
    sidebarCollapsed = false;
});


// --- 5. CONVERSATION HELPERS ---
async function createConversation(username) {
    const response = await fetch(`${API_BASE}/conversations/${username}`, { method: 'POST' });
    const convo = await response.json();
    return convo.id;
}

async function initConversations(username) {
    await loadSidebarHistory(username);

    const response = await fetch(`${API_BASE}/conversations/${username}`);
    const conversations = await response.json();

    if (conversations.length > 0) {
        // Open the most recent conversation automatically
        await openConversation(conversations[0].id);
    } else {
        // No conversations yet — start clean, first send will create one
        currentConversationId = null;
        chatBox.innerHTML = "";
    }
}

async function openConversation(conversationId) {
    currentConversationId = conversationId;
    currentAiMessageDiv = null;

    const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`);
    const messages = await response.json();

    chatBox.innerHTML = "";
    messages.forEach(msg => {
        if (!msg.content) return;
        appendMessage(msg.role === 'user' ? 'user' : 'ai', msg.content);
    });
    chatBox.scrollTop = chatBox.scrollHeight;

    highlightActiveHistoryItem(conversationId);
}

function highlightActiveHistoryItem(conversationId) {
    document.querySelectorAll('.history-item').forEach(el => {
        el.classList.toggle('active', Number(el.dataset.id) === conversationId);
    });
}


// --- 6. LOAD SIDEBAR HISTORY (list of conversations, not messages) ---
async function loadSidebarHistory(username) {
    try {
        const response = await fetch(`${API_BASE}/conversations/${username}`);
        if (!response.ok) {
            console.warn("⚠️ Conversation list fetch failed:", response.status);
            return;
        }

        const conversations = await response.json();
        const historyList = document.getElementById('history-list');
        if (!historyList) return;

        historyList.innerHTML = "";

        conversations.forEach(convo => {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.dataset.id = convo.id;

            const title = convo.title && convo.title.trim() !== "" ? convo.title : "New Conversation";
            const truncated = title.length > 30 ? title.substring(0, 30) + "..." : title;

            item.textContent = truncated;
            item.title = title;

            item.addEventListener('click', () => {
                openConversation(convo.id);
            });

            historyList.appendChild(item);
        });

        highlightActiveHistoryItem(currentConversationId);
    } catch (e) {
        console.error("❌ Failed to load sidebar history:", e);
    }
}