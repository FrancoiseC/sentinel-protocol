import os
import subprocess
import ipaddress
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

# Load environment variables from the separated .env file
load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    exit("\n[!] CRITICAL ERROR: GOOGLE_API_KEY not set in .env file.\n")

print("Initializing Live Sentinel Protocol...")

@tool("Live SIFT Netstat")
def live_sift_netstat() -> str:
    """Executes 'ss -tnp' to pull live network connections directly from the system."""
    try:
        return subprocess.check_output(['ss', '-tnp'], text=True)
    except Exception as e:
        return f"Tool Execution Failed: {e}"

@tool("Check Microsoft IP Range")
def check_microsoft_ip(ip_address: str) -> str:
    """Checks if an IP address falls within known Microsoft IP ranges."""
    microsoft_ranges = [
        "13.64.0.0/11", "20.0.0.0/8", "40.64.0.0/10",
        "52.0.0.0/8", "104.40.0.0/13", "157.54.0.0/15"
    ]
    try:
        ip = ipaddress.ip_address(ip_address)
        for cidr in microsoft_ranges:
            if ip in ipaddress.ip_network(cidr):
                return f"{ip_address} IS a Microsoft IP (matches {cidr})"
        return f"{ip_address} is NOT a Microsoft IP range — RULE-003 applies"
    except ValueError:
        return f"Invalid IP address: {ip_address}"

SIFT_KNOWN_RULES = """
=== SIFT KNOWN RULES ===
RULE-001: svchost.exe MUST only connect to Microsoft IP ranges
RULE-002: lsass.exe MUST NOT listen on any network port
RULE-003: Any process on port 443 to non-Microsoft IP is HIGH SUSPICION (applies to RULE-003 only)
"""

fiduciary_llm = LLM(model="gemini/gemini-2.5-flash", api_key=api_key)

triage = Agent(
    role="Triage Analyst",
    goal="Extract ALL suspicious IPs and PIDs from the Live SIFT Netstat tool, and verify IP ranges using the Check Microsoft IP Range tool.",
    backstory="Senior IR analyst. Read raw output and verify IP ownership. Do not invent severity labels.",
    verbose=True,
    tools=[live_sift_netstat, check_microsoft_ip],
    llm=fiduciary_llm
)

auditor = Agent(
    role="Integrity Auditor",
    goal="Verify analyst findings line by line against raw tool output, SIFT KNOWN RULES, and independently run the Check Microsoft IP Range tool.",
    backstory="Fiduciary safety net. You VETO anything not explicitly found in the tool output or rules block. Independently verify IP ranges.",
    verbose=True,
    tools=[check_microsoft_ip],
    llm=fiduciary_llm
)

t1 = Task(
    description=f"1. Execute 'Live SIFT Netstat'.\n2. Extract IPs, PIDs, and run the 'Check Microsoft IP Range' tool on destination IPs.\n3. Flag violations against these rules:\n{SIFT_KNOWN_RULES}\n4. Include the raw tool output in your final answer so the Auditor can verify it.",
    expected_output="Raw tool output followed by Structured findings: PID, Executable, Destination, Rule, IP Verification.",
    agent=triage
)

t2 = Task(
    description=f"1. Read the raw tool output AND the known rules:\n{SIFT_KNOWN_RULES}\n2. Verify each Analyst claim verbatim against BOTH sources, including running independent IP checks.\n3. Issue [VETOED] if they hallucinate or skip checks. Issue [APPROVED] if perfect.",
    expected_output="Fiduciary Audit Log with [APPROVED] or [VETOED]",
    agent=auditor,
    context=[t1]
)

crew = Crew(
    agents=[triage, auditor], 
    tasks=[t1, t2], 
    process=Process.sequential,
    memory=False,
    planning=False
)

print("\n=== EXECUTING LIVE SIFT AUTOMATION LOOP ===")
print(crew.kickoff())