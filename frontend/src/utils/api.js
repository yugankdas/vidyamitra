// ═══════════════════════════════════════
//  CENTRAL API CLIENT
//  All requests go through this module.
//  Backend base URL — update if you deploy elsewhere.
// ═══════════════════════════════════════

const API_BASE = 'http://localhost:8000';

// Auth token storage (in-memory for this session)
let _authToken = null;

function setAuthToken(token) {
  _authToken = token;
}

function getAuthToken() {
  return _authToken;
}

// Generic fetch wrapper
async function apiFetch(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (_authToken) headers['Authorization'] = `Bearer ${_authToken}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Auth ────────────────────────────────
const AuthAPI = {
  register: (email, password, name) =>
    apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    }),

  login: (email, password) =>
    apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
};

// ── AI Chat ─────────────────────────────
const ChatAPI = {
  send: (messages, system) =>
    apiFetch('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ messages, system }),
    }),
};

// ── Resume ──────────────────────────────
const ResumeAPI = {
  analyze: (resumeText, targetRole = '') =>
    apiFetch('/resume/analyze', {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText, target_role: targetRole }),
    }),
};

// ── Interview ───────────────────────────
const InterviewAPI = {
  generateQuestion: (role, mode = 'behavioral') =>
    apiFetch('/interview/question', {
      method: 'POST',
      body: JSON.stringify({ role, mode }),
    }),

  scoreAnswer: (question, answer, mode = 'behavioral') =>
    apiFetch('/interview/score', {
      method: 'POST',
      body: JSON.stringify({ question, answer, mode }),
    }),
};

// ── Quiz ────────────────────────────────
const QuizAPI = {
  generate: (domain, difficulty = 'medium', count = 8) =>
    apiFetch('/quiz/generate', {
      method: 'POST',
      body: JSON.stringify({ domain, difficulty, count }),
    }),

  submit: (questions, answers) =>
    apiFetch('/quiz/submit', {
      method: 'POST',
      body: JSON.stringify({ questions, answers }),
    }),
};

// ── Career ──────────────────────────────
const CareerAPI = {
  plan: (resumeText, targetRole, quizScores = {}) =>
    apiFetch('/career/plan', {
      method: 'POST',
      body: JSON.stringify({ resume_text: resumeText, target_role: targetRole, quiz_scores: quizScores }),
    }),

  skillGap: (currentSkills, targetRole) =>
    apiFetch('/career/skill-gap', {
      method: 'POST',
      body: JSON.stringify({ current_skills: currentSkills, target_role: targetRole }),
    }),
};

// ── Jobs ────────────────────────────────
const JobsAPI = {
  list: (role = '', location = 'India') =>
    apiFetch(`/jobs/list?role=${encodeURIComponent(role)}&location=${encodeURIComponent(location)}`),

  trends: () => apiFetch('/jobs/trends'),
};

// ── Progress ────────────────────────────
const ProgressAPI = {
  get: () => apiFetch('/progress'),
  update: (data) =>
    apiFetch('/progress', { method: 'POST', body: JSON.stringify(data) }),
};

// Export for use across modules
window.API = {
  base: API_BASE,
  setAuthToken,
  getAuthToken,
  auth: AuthAPI,
  chat: ChatAPI,
  resume: ResumeAPI,
  interview: InterviewAPI,
  quiz: QuizAPI,
  career: CareerAPI,
  jobs: JobsAPI,
  progress: ProgressAPI,
};
