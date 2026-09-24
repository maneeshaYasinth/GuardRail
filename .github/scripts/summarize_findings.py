import json
import os
import time
import urllib.error
import urllib.request

def load_findings():
    try:
        with open("tfsec-results.json") as f:
            data = json.load(f)
        return data.get("results", []) or []
    except FileNotFoundError:
        return []

def build_prompt(findings):
    if not findings:
        return None

    findings_text = ""
    for f in findings[:15]:
        findings_text += (
            f"- Rule: {f.get('rule_id')} | Severity: {f.get('severity')}\n"
            f"  Description: {f.get('description')}\n"
            f"  Location: {f.get('location', {}).get('filename')}:"
            f"{f.get('location', {}).get('start_line')}\n\n"
        )

    return (
        "You are a security assistant reviewing Terraform scan results for a "
        "junior DevOps engineer's learning project. Summarize the following "
        "tfsec findings in plain, encouraging English. Group by severity, "
        "explain the real-world risk of each in 1-2 sentences, and suggest a "
        "concrete fix. Keep it concise and use Markdown.\n\n"
        f"{findings_text}"
    )

def call_gemini(prompt, max_retries=3):
    api_key = os.environ["GEMINI_API_KEY"]
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
    )
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as error:
            if error.code in (503, 429) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise

def main():
    findings = load_findings()
    if not findings:
        summary = "✅ **GuardRail AI Summary:** No security findings detected in this change. Nice and clean!"
    else:
        prompt = build_prompt(findings)
        try:
            ai_text = call_gemini(prompt)
            summary = f"## 🛡️ GuardRail AI Security Summary\n\n{ai_text}"
        except Exception as error:
            summary = (
                "⚠️ AI summary temporarily unavailable "
                f"({error}). Raw tfsec findings are in the previous comment."
            )

    with open("ai-summary.md", "w") as f:
        f.write(summary)

if __name__ == "__main__":
    main()