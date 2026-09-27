const uploadBtn = document.getElementById("upload-btn");
const pdfInput = document.getElementById("pdf-input");
const uploadStatus = document.getElementById("upload-status");
const askBtn = document.getElementById("ask-btn");
const questionInput = document.getElementById("question-input");
const chatLog = document.getElementById("chat-log");
 
uploadBtn.addEventListener("click", async () => {
  const file = pdfInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Choose a PDF first.";
    return;
  }
 
  uploadStatus.textContent = "Processing...";
  const formData = new FormData();
  formData.append("file", file);
 
  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();
    uploadStatus.textContent = res.ok ? data.message : `Error: ${data.error}`;
  } catch (err) {
    uploadStatus.textContent = `Error: ${err.message}`;
  }
});
 
askBtn.addEventListener("click", askQuestion);
questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") askQuestion();
});
 
async function askQuestion() {
  const question = questionInput.value.trim();
  if (!question) return;
 
  appendMessage("user", question);
  questionInput.value = "";
 
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
 
    if (!res.ok) {
      appendMessage("bot", `⚠️ ${data.error}`);
      return;
    }
 
    const sourcesHtml = data.sources
      .map((s) => `<div class="sources">from ${s.doc}: "${s.excerpt}"</div>`)
      .join("");
    appendMessage("bot", data.answer, sourcesHtml);
  } catch (err) {
    appendMessage("bot", `⚠️ ${err.message}`);
  }
}
 
function appendMessage(role, text, sourcesHtml = "") {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<div>${text}</div>${sourcesHtml}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}