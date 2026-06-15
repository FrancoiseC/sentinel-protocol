# Sentinel Protocol (SIFT Sentinel Fiduciary Agent)
## 🏛️ Project Manifesto
The **Sentinel Protocol** is an autonomous, multi-agent fiduciary safety net designed to eliminate probabilistic hallucinations in network monitoring. 
In traditional AI-driven monitoring, LLMs often "guess" the state of a system. The Sentinel Protocol enforces a **Strict Integrity Verification Loop**, where raw system evidence is gathered by a *Triage Analyst* and independently cross-referenced by an *Integrity Auditor* against hard-coded deterministic rules. If a claim cannot be verified, it is **[VETOED]**.
---
## ⚙️ Architecture & Logic
The system utilizes a two-agent sequential process to guarantee system integrity:
1. **Triage Analyst**: Executes raw system commands (e.g., `ss -tnp`) and identifies network activity.
2. **Integrity Auditor**: Acts as the Fiduciary Safety Net. It performs independent lookups (such as CIDR range validation) and verifies Analyst findings against the **SIFT Known Rules**.
### SIFT Known Rules
* **RULE-001**: `svchost.exe` MUST only connect to authorized Microsoft IP ranges.
* **RULE-002**: `lsass.exe` MUST NOT listen on any network port.
* **RULE-003**: Any process on port 443 to a non-Microsoft IP is flagged as **HIGH SUSPICION**.
---
## 🛠️ The Self-Correction Story
During the MVP development, the protocol initially failed by incorrectly identifying valid service connections as "suspicious." 
Instead of letting the LLM "tune" its behavior (which leads to more hallucinations), we **self-corrected the architecture**. We implemented a deterministic tool—`Check Microsoft IP Range`—which uses Python’s `ipaddress` library to perform mathematically certain validation of IP ranges. The Auditor now uses this tool to provide a definitive `[APPROVED]` or `[VETOED]` verdict.
---
## 🚀 Deployment & Execution
### Prerequisites
* Python 3.10+
* `crewai` and `crewai[google-genai]`
* A Google Gemini API Key
### Execution Flow
1. **Clone the repo:**
   ```bash
   git clone [https://github.com/FrancoiseC/sentinel-protocol.git](https://github.com/FrancoiseC/sentinel-protocol.git)
   cd sentinel-protocol