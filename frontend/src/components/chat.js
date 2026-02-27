// ═══════════════════════════════════════
//  AI CHAT COMPONENT
//  Calls your FastAPI /ai/chat endpoint
//  which proxies to Groq API
// ═══════════════════════════════════════

const CHAT_SYSTEM = `You are VidyāMitra, an expert AI career advisor for Indian tech students and professionals. Deep expertise in:
- ATS resume optimization for Indian companies (Swiggy, Razorpay, Zomato, Flipkart, FAANG India)
- Skill gap analysis for Backend, Frontend, ML, DevOps, Full Stack roles
- Career planning with actionable roadmaps
- Mock interview coaching using STAR method and technical prep
- Salary benchmarks for Bengaluru, Mumbai, Delhi, Pune, Hyderabad
- Learning resources (Coursera, YouTube, LeetCode, System Design Primer)
Be concise (3-4 sentences), practical, and encouraging. Use **bold** for key terms. Indian context when relevant.`;

let chatHistory = [];

function chatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChat();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function quickChat(btn) {
  const text = btn.textContent.replace(/^[^\s]+\s/, '');
  const input = document.getElementById('chatInput');
  if (input) { input.value = text; sendChat(); }
}

async function sendChat() {
  const input = document.getElementById('chatInput');
  const sendBtn = document.getElementById('chatSendBtn');
  if (!input) return;

  const text = input.value.trim();
  if (!text) return;

  addMsg(text, 'user');
  input.value = '';
  autoResize(input);

  const quickBtns = document.getElementById('chatQuickBtns');
  if (quickBtns) quickBtns.style.display = 'none';
  if (sendBtn) sendBtn.disabled = true;

  chatHistory.push({ role: 'user', content: text });
  const typingId = addTyping();

  try {
    // Call our FastAPI backend which proxies to Groq
    const data = await window.API.chat.send(chatHistory, CHAT_SYSTEM);
    const reply = data.reply || data.content || 'I had trouble responding. Please try again.';
    removeTyping(typingId);
    chatHistory.push({ role: 'assistant', content: reply });
    addMsg(reply, 'ai');
  } catch (err) {
    removeTyping(typingId);
    addMsg('Connection issue. Make sure the backend is running on port 8000.', 'ai');
    console.error('Chat error:', err);
  }

  if (sendBtn) sendBtn.disabled = false;
}

function addMsg(text, role) {
  const msgs = document.getElementById('chatMessages');
  if (!msgs) return;
  const div = document.createElement('div');
  div.className = 'cmsg ' + role;
  const fmt = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
  div.innerHTML = `
    <div class="cmsg-av ${role}">${role === 'ai' ? 'V' : '👤'}</div>
    <div class="cmsg-bubble ${role}">${fmt}</div>
  `;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function addTyping() {
  const msgs = document.getElementById('chatMessages');
  const id = 'ty' + Date.now();
  const div = document.createElement('div');
  div.className = 'cmsg';
  div.id = id;
  div.innerHTML = `
    <div class="cmsg-av ai">V</div>
    <div class="cmsg-bubble ai">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// Export globals
window.chatKey = chatKey;
window.autoResize = autoResize;
window.quickChat = quickChat;
window.sendChat = sendChat;
