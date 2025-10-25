// app.js — minimal client that matches your working backend contract
// Posts to /api/chat with { messages } and expects { text } back.

// UI elements
const answerEl = document.getElementById('answer');
const qEl = document.getElementById('q');
const askBtn = document.getElementById('ask');

// Endpoint (change to "/chat" if your server uses that)
const ENDPOINT = "http://127.0.0.1:8000/api/chat";

// Optional: system prompt to enforce citations-first behavior
const SYSTEM_INSTRUCTION =
  "You are DeenCompass — a citations-first Islamic Q&A assistant. " +
  "Never issue a legal verdict (fatwā); this is educational guidance. " +
  "Always cite sources inline with chapter/surah, verse number from Quran, tafseer, sirah, fiqh, hadiths and hadith grading. " +
  "If citations are not found, state that plainly and ask clarifying questions; do NOT speculate. " +
  "Present major valid fiqh opinions fairly when relevant, and be gentle and compassionate.";

// Tiny extractor so you don't see raw JSON if the server shape changes
function extractText(data) {
  if (!data) return null;
  if (typeof data === "string") return data;
  if (typeof data.text === "string") return data.text; // your current server shape
  // Common fallbacks:
  if (data.content) return data.content;
  if (data.choices?.[0]?.message?.content) return data.choices[0].message.content;
  if (data.output_text) return data.output_text;
  if (Array.isArray(data.output) && data.output[0]?.content?.[0]?.text)
    return data.output[0].content[0].text;
  return null;
}

async function askOnce(questionText) {
  // Build message list: include a system guard + user message
  const messages = [
    { role: "system", content: SYSTEM_INSTRUCTION },
    { role: "user",   content: questionText }
  ];

  const r = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages })
  });

  if (!r.ok) {
    const reason = await r.text();
    throw new Error(`Server error (${r.status}): ${reason}`);
  }

  const data = await r.json();
  return extractText(data) || "(No text returned)";
}

// Wire button click
askBtn.addEventListener('click', async () => {
  const text = qEl.value.trim();
  if (!text) return;

  answerEl.textContent = "Thinking…";
  askBtn.disabled = true;

  try {
    const reply = await askOnce(text);
    answerEl.textContent = reply;
  } catch (err) {
    answerEl.textContent = "Error: " + err.message;
  } finally {
    askBtn.disabled = false;
  }
});

// Also allow Ctrl/Cmd+Enter to submit
qEl.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    askBtn.click();
  }
});
