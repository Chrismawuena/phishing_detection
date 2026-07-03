console.log("AI Phishing Extension: content script loaded");

function getOpenEmailText() {
  const bodyEl = document.querySelector(".a3s.aiL") || document.querySelector(".a3s");
  if (!bodyEl) return null;
  return bodyEl.innerText.trim();
}

function getEmailSubject() {
  const subjectEl = document.querySelector("h2.hP");
  return subjectEl ? subjectEl.innerText.trim() : "";
}

let lastSentText = null;

function scanCurrentEmail() {
  const text = getOpenEmailText();

  if (!text) {
    console.log("AI Phishing Extension: no email body found yet");
    return;
  }

  if (text === lastSentText) {
    console.log("AI Phishing Extension: same email, skipping");
    return;
  }

  console.log("AI Phishing Extension: found email text, length =", text.length);

  lastSentText = text;
  const subject = getEmailSubject();

  console.log("AI Phishing Extension: sending to background.js, subject =", subject);

  try {
    chrome.runtime.sendMessage(
      { type: "SCAN_EMAIL", text: text, subject: subject },
      function (response) {
        if (chrome.runtime.lastError) {
          console.error("AI Phishing Extension: sendMessage error:", chrome.runtime.lastError.message);
        } else {
          console.log("AI Phishing Extension: background acknowledged:", response);
        }
      }
    );
  } catch (err) {
    console.error("AI Phishing Extension: chrome.runtime error:", err);
  }
}

let debounceTimer = null;
const observer = new MutationObserver(() => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(scanCurrentEmail, 600);
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
});

// Try once on load in case email is already open
setTimeout(scanCurrentEmail, 1000);