console.log("AI Phishing Extension: background service worker loaded");

const API_URL = "http://127.0.0.1:5000/scan";

let lastNotifiedText = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== "SCAN_EMAIL") return;

  console.log("AI Phishing Extension: received SCAN_EMAIL, subject =", message.subject);
  sendResponse({ received: true });

  scanEmail(message.text, message.subject);
  return true;
});

async function scanEmail(text, subject) {
  try {
    console.log("AI Phishing Extension: calling Flask API...");

    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      console.error("AI Phishing Extension: API error status:", response.status);
      return;
    }

    const result = await response.json();
    console.log("AI Phishing Extension: API result:", result);

    chrome.storage.local.set({
      lastScan: {
        subject: subject,
        is_phishing: result.is_phishing,
        confidence: result.confidence,
        suspicious_words_found: result.suspicious_words_found,
        scannedAt: Date.now(),
      },
    });

    // Notify for every new email, regardless of phishing status
    if (text !== lastNotifiedText) {
      lastNotifiedText = text;
      showNotification(subject, result);
    }

  } catch (error) {
    console.error("AI Phishing Extension: fetch failed:", error);
  }
}

function showNotification(subject, result) {
  const confidencePct = Math.round(result.confidence * 100);
  const subjectPreview = subject ? `"${subject}"` : "This email";

  let title, message, priority;

  if (result.is_phishing) {
    title = "⚠️ Possible Phishing Email Detected";
    message = `${subjectPreview} looks suspicious (${confidencePct}% phishing confidence).`;
    if (result.suspicious_words_found && result.suspicious_words_found.length > 0) {
      message += ` Flagged terms: ${result.suspicious_words_found.join(", ")}.`;
    }
    priority = 2;
  } else {
    const safeConfidencePct = Math.round((1 - result.confidence) * 100);
    title = "✅ Email Looks Safe";
    message = `${subjectPreview} appears legitimate (${safeConfidencePct}% safe).`;
    priority = 0;
  }

  console.log("AI Phishing Extension: firing notification:", title, message);

  chrome.notifications.create({
    type: "basic",
    iconUrl: "icon.png",
    title: title,
    message: message,
    priority: priority,
  });
}