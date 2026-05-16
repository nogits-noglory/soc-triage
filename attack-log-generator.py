import anthropic
import os
import sys

client = anthropic.Anthropic()

ATTACK_PROFILES = {
    "linux": {
        "ssh_bruteforce": "SSH brute force attack with multiple source IPs cycling through common usernames",
        "slow_burn": "slow, evasive SSH brute force spreading attempts over 15 minutes to avoid rate limiting, with long pauses between attempts",
        "successful_breach": "SSH brute force that eventually succeeds, followed by post-exploitation activity including sudo attempts and outbound connections",
        "port_scan": "Nmap-style port scan followed by targeted service enumeration",
    },
    "windows": {
        "password_spray": "password spraying attack against Active Directory, generating Windows Security Event Log entries with Event IDs 4625, 4624, 4648",
        "successful_breach": "failed logins followed by a successful authentication, then lateral movement attempts with Event IDs 4624, 4672, 4688, 4776",
        "privilege_escalation": "low privilege user attempting privilege escalation via scheduled tasks and service manipulation, Event IDs 4698, 4702, 7045",
        "lateral_movement": "authenticated user performing lateral movement via SMB and remote service execution, Event IDs 4624, 4648, 5140, 7036",
    }
}

LOG_FORMAT_INSTRUCTIONS = {
    "linux": "Output ONLY raw syslog/auth.log format lines. Example: May 14 03:00:12 webserver sshd[2847]: Invalid user admin from 203.0.113.45 port 54321",
    "windows": "Output ONLY raw Windows Event Log XML format entries. Include EventID, TimeCreated, Computer, and relevant EventData fields. Use realistic but fictional hostnames and IPs."
}

def generate_attack_sequence(os_type: str, attack_type: str, duration_minutes: int = 15) -> str:
    profiles = ATTACK_PROFILES.get(os_type)
    if not profiles:
        raise ValueError(f"Unknown OS type: {os_type}. Choose 'linux' or 'windows'")

    profile = profiles.get(attack_type)
    if not profile:
        raise ValueError(f"Unknown attack type: {attack_type}. Available for {os_type}: {list(profiles.keys())}")

    format_instruction = LOG_FORMAT_INSTRUCTIONS[os_type]

    prompt = f"""You are simulating a threat actor. Generate {duration_minutes} minutes of realistic {os_type} log entries representing: {profile}

{format_instruction}

Use realistic timestamps starting from 2024-05-14 03:00:00. Use realistic but fictional IPs, usernames, and hostnames. Output ONLY log lines, nothing else."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text

def save_logs(os_type: str, attack_type: str, logs: str):
    dir_path = f"sample_logs/{os_type}"
    os.makedirs(dir_path, exist_ok=True)
    path = f"{dir_path}/{attack_type}.log"
    with open(path, "w") as f:
        f.write(logs)
    print(f"Saved to {path}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        os_type = sys.argv[1]
        attack_type = sys.argv[2].replace("-", "_")
        duration = int(sys.argv[3]) if len(sys.argv) == 4 else 15
    else:
        print("Usage: python attacker.py <os_type> <attack_type> [duration_minutes]")
        print("\nAvailable profiles:")
        for os_t, profiles in ATTACK_PROFILES.items():
            print(f"  {os_t}: {', '.join(profiles.keys())}")
        sys.exit(1)

    print(f"\nGenerating {os_type}/{attack_type} attack sequence ({duration} minutes)...")
    logs = generate_attack_sequence(os_type, attack_type, duration)
    print(logs)
    save_logs(os_type, attack_type, logs)