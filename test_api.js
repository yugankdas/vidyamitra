const API_BASE = 'https://newvidyamitra.onrender.com';

async function testApi() {
  try {
    const res = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Origin': 'https://vidyamitra2026.netlify.app'
      },
      body: JSON.stringify({
        messages: [{ role: 'user', content: 'test request' }],
        system: ''
      })
    });
    
    console.log('Status:', res.status);
    console.log('Headers:', Object.fromEntries(res.headers));
    const data = await res.text();
    console.log('Data:', data.substring(0, 100));
  } catch(e) {
    console.error('Fetch Error:', e.message);
  }
}

testApi();
