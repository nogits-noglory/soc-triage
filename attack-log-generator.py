import anthropic
import json
import os
import sys
from environment import (
    get_or_create_environment,
    generate_environment,
    save_environment,
    store_environment,
    select_environment,
    print_environment_summary
)

client = anthropic.Anthropic()

ATTACK_PROFILES = {
    "linux": {
        "ssh_bruteforce": "SSH brute force attack with multiple source IPs cycling through common usernames",
        "slow_burn": "slow, evasive SSH brute force spreading attempts over 15 minutes to avoid rate limiting, with long pauses between attempts",
        "successful_breach": "SSH brute force that eventually succeeds, followed by post-exploitation activity including sudo attempts and outbound connections",
        "port_scan": "Nmap-style port scan followed by targeted service enumeration",
        "normal": "completely normal Linux server activity during business hours — legitimate user logins, cron jobs, scheduled tasks, routine sudo commands, no anomalies whatsoever",
    },
    "windows": {
        "password_spray": "password spraying attack against Active Directory, generating Windows Security Event Log entries with Event IDs 4625, 4624, 4648",
        "successful_breach": "failed logins followed by a successful authentication, then lateral movement attempts with Event IDs 4624, 4672, 4688, 4776",
        "privilege_escalation": "low privilege user attempting privilege escalation via scheduled tasks and service manipulation, Event IDs 4698, 4702, 7045",
        "lateral_movement": "authenticated user performing lateral movement via SMB and remote service execution, Event IDs 4624, 4648, 5140, 7036",
        "normal": "completely normal Windows Active Directory environment during business hours — routine logins, group policy updates, scheduled tasks, software updates, no anomalies whatsoever",
    },
    "network": {
        "ssh_bruteforce": "firewall and NetFlow logs correlated with an SSH brute force attack — repeated connection attempts from external IPs to port 22, firewall deny rules triggering, DNS lookups for attacker infrastructure",
        "slow_burn": "firewall and NetFlow logs showing a slow, low-volume SSH brute force — sparse connections to port 22 spread over time, just below threshold alerting, from rotating source IPs",
        "successful_breach": "firewall and NetFlow logs correlated with a successful SSH breach — initial port 22 traffic, successful connection, then anomalous outbound connections to unknown IPs, DNS queries to suspicious domains, C2 callback traffic",
        "port_scan": "firewall logs showing Nmap-style port scan — sequential port hits across a single host, ICMP probes, SYN packets with no ACK responses, followed by targeted service connection attempts",
        "password_spray": "firewall and NetFlow logs correlated with Active Directory password spray — repeated SMB and Kerberos traffic from a single internal IP to the domain controller, event volume spike",
        "lateral_movement": "internal firewall and NetFlow logs showing lateral movement — SMB connections between internal hosts, unusual RPC traffic, new internal connections not seen in baseline",
        "privilege_escalation": "host-based firewall and process network logs showing privilege escalation attempts — unusual DCOM traffic, WMI remote calls, scheduled task network activity",
        "c2_callback": "firewall and NetFlow logs showing command and control beacon traffic — regular interval outbound connections to external IP, consistent packet sizes, HTTP/HTTPS to non-categorized domains, DNS tunneling indicators",
        "dns_exfiltration": "DNS server and firewall logs showing DNS exfiltration — abnormally long DNS query strings, high volume of TXT record requests, queries to newly registered domains, unusual query frequency from single host",
        "normal": "completely normal network traffic during business hours — routine DNS queries, expected internal host communications, normal web browsing patterns, standard update traffic, no anomalies",
    }
}

LOG_FORMAT_INSTRUCTIONS = {
    "linux": "Output ONLY raw syslog/auth.log format lines. Example: May 14 03:00:12 webserver sshd[2847]: Invalid user admin from 203.0.113.45 port 54321",
    "windows": "Output ONLY raw Windows Event Log XML format entries. Include EventID, TimeCreated, Computer, and relevant EventData fields. Use realistic but fictional hostnames and IPs.",
    "network": "Output ONLY raw firewall/NetFlow log lines in a mix of formats: iptables log format for firewall entries, and IPFIX/NetFlow format for flow records. Include realistic but fictional IPs, ports, protocols, and packet sizes. Example iptables: May 14 03:00:12 gateway kernel: IN=eth0 OUT=eth1 SRC=203.0.113.45 DST=192.168.1.10 PROTO=TCP SPT=54321 DPT=22 ACTION=DROP"
}

COMPANION_MAP = {
    "linux": {
        "ssh_bruteforce": "ssh_bruteforce",
        "slow_burn": "slow_burn",
        "successful_breach": "successful_breach",
        "port_scan": "port_scan",
        "normal": "normal",
    },
    "windows": {
        "password_spray": "password_spray",
        "successful_breach": "lateral_movement",
        "privilege_escalation": "privilege_escalation",
        "lateral_movement": "lateral_movement",
        "normal": "normal",
    }
}

def generate_log(os_type: str, attack_type: str, duration_minutes: int = 15, env: dict = None) -> str:
    profiles = ATTACK_PROFILES.get(os_type)
    if not profiles:
        raise ValueError(f"Unknown log type: {os_type}. Choose from: {list(ATTACK_PROFILES.keys())}")

    profile = profiles.get(attack_type)
    if not profile:
        raise ValueError(f"Unknown attack type '{attack_type}' for {os_type}. Available: {list(profiles.keys())}")

    format_instruction = LOG_FORMAT_INSTRUCTIONS[os_type]

    env_context = ""
    if env:
        env_context = f"""
Use this specific network environment for all hostnames, IPs, usernames, and context:

Organization: {env['org_name']} ({env['org_type']})
Domain: {env['domain']}
Business hours: {env['business_hours']['start']}-{env['business_hours']['end']}

Subnets:
{json.dumps(env['subnets'], indent=2)}

Devices (use these exact hostnames and IPs):
{json.dumps(env['devices'], indent=2)}

Users (use these exact usernames):
{json.dumps(env['users'], indent=2)}

Known external IPs (these are legitimate, everything else external is suspicious):
{json.dumps(env['known_external_ips'], indent=2)}

Security policies:
{json.dumps(env['policies'], indent=2)}

Make the logs internally consistent with this environment.
"""

    prompt = f"""You are simulating security log data. Generate {duration_minutes} minutes of realistic {os_type} log entries representing: {profile}

{env_context}
{format_instruction}

Use realistic timestamps starting from 2024-05-14 03:00:00. Output ONLY log lines, nothing else."""

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
    print(f"  Saved to {path}")

def generate_with_companion(os_type: str, attack_type: str, duration_minutes: int, env: dict = None):
    print(f"\nGenerating {os_type}/{attack_type} ({duration_minutes} minutes)...")
    logs = generate_log(os_type, attack_type, duration_minutes, env)
    save_logs(os_type, attack_type, logs)

    network_profile = COMPANION_MAP.get(os_type, {}).get(attack_type)
    if network_profile:
        print(f"Generating companion network/{network_profile}...")
        network_logs = generate_log("network", network_profile, duration_minutes, env)
        save_logs(f"network/{os_type}", attack_type, network_logs)

def generate_all(duration_minutes: int, env: dict = None):
    for os_type in ["linux", "windows"]:
        for attack_type in ATTACK_PROFILES[os_type]:
            generate_with_companion(os_type, attack_type, duration_minutes, env)

    standalone_network = ["c2_callback", "dns_exfiltration"]
    for profile in standalone_network:
        print(f"\nGenerating network/{profile} ({duration_minutes} minutes)...")
        logs = generate_log("network", profile, duration_minutes, env)
        save_logs("network/standalone", profile, logs)

if __name__ == "__main__":

    # Handle environment flags before parsing other args
    if "--new-env" in sys.argv:
        sys.argv.remove("--new-env")
        org_type = None
        for arg in sys.argv:
            if arg.startswith("--org="):
                org_type = arg.split("=", 1)[1]
                sys.argv.remove(arg)
                break
        print("Generating new environment...")
        env = generate_environment(org_type)
        save_environment(env)
        store_environment(env)
        print_environment_summary(env)

    elif "--select-env" in sys.argv:
        sys.argv.remove("--select-env")
        env = select_environment()
        if env:
            print_environment_summary(env)
        else:
            sys.exit(1)

    elif "--no-env" in sys.argv:
        sys.argv.remove("--no-env")
        env = None
        print("Skipping environment context.")

    else:
        env = get_or_create_environment()
        if env:
            print_environment_summary(env)

    # Generate logs
    if len(sys.argv) == 1:
        duration = 15
        print(f"Generating full log corpus ({duration} minutes each)...")
        generate_all(duration, env)
        print("\nDone. Full corpus saved to sample_logs/")

    elif sys.argv[1] == "all":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        print(f"Generating full log corpus ({duration} minutes each)...")
        generate_all(duration, env)
        print("\nDone. Full corpus saved to sample_logs/")

    elif len(sys.argv) >= 3:
        os_type = sys.argv[1]
        attack_type = sys.argv[2].replace("-", "_")
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 15

        if os_type == "network":
            print(f"\nGenerating network/{attack_type} ({duration} minutes)...")
            logs = generate_log("network", attack_type, duration, env)
            print(logs)
            save_logs("network/standalone", attack_type, logs)
        else:
            generate_with_companion(os_type, attack_type, duration, env)

    else:
        print("Usage:")
        print("  python attack-log-generator.py                               # full corpus")
        print("  python attack-log-generator.py all [duration]                # full corpus, custom duration")
        print("  python attack-log-generator.py <os> <attack> [duration]      # single profile + companion")
        print("  python attack-log-generator.py network <attack> [duration]   # network-only profile")
        print()
        print("Environment flags (prepend to any command):")
        print("  --new-env               generate and use a fresh environment")
        print("  --new-env --org=<type>  generate for a specific org type")
        print("  --select-env            pick from saved environments")
        print("  --no-env                skip environment context entirely")
        print()
        print("Available profiles:")
        for os_t, profiles in ATTACK_PROFILES.items():
            print(f"  {os_t}: {', '.join(profiles.keys())}")
        sys.exit(1)