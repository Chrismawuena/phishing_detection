const resultEl = document.getElementById("result");

chrome.storage.local.get("lastScan", (data) => {
  const scan = data.lastScan;

  if (!scan) {
    resultEl.innerHTML = `<div class="status neutral">No email scanned yet. Open an email in Gmail to scan it.</div>`;
    return;
  }

  const confidencePct = Math.round(scan.confidence * 100);
  const statusClass = scan.is_phishing ? "danger" : "safe";
  const statusLabel = scan.is_phishing ? "⚠️ Likely Phishing" : "✓ Looks Safe";

  let wordsHtml = "";
  if (scan.suspicious_words_found && scan.suspicious_words_found.length > 0) {
    wordsHtml = `<div class="words">Flagged terms: ${scan.suspicious_words_found.join(", ")}</div>`;
  }

  resultEl.innerHTML = `
    <div class="subject">${escapeHtml(scan.subject || "(no subject)")}</div>
    <div class="status ${statusClass}">${statusLabel}</div>
    <div class="confidence">Confidence: ${confidencePct}%</div>
    ${wordsHtml}
  `;
});

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}