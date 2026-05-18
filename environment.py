import anthropic
import json
import os
import random

client = anthropic.Anthropic()

ENVIRONMENTS_DIR = "environments"
ACTIVE_ENV_PATH = "environment.json"

ORG_TYPES = [
    "small medical clinic",
    "regional bank",
    "manufacturing plant",
    "law firm",
    "e-commerce company",
    "university department",
    "government contractor",
    "energy utility",
    "retail chain",
    "software startup",
    "logistics company",
    "defense contractor",
    "hospital network",
    "insurance company",
    "municipal government"
]

def generate_environment(org_type: str = None) -> dict:
    if not org_type:
        org_type = random.choice(ORG_TYPES)

    prompt = f"""Generate a realistic corporate network environment profile for a {org_type}.

Return ONLY a JSON object with exactly this structure, no explanation:

{{
    "org_name": "fictional company name",
    "org_type": "{org_type}",
    "domain": "fictional.internal",
    "timezone": "America/Phoenix",
    "business_hours": {{
        "start": "08:00",
        "end": "18:00",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    }},
    "subnets": {{
        "dmz": "x.x.x.x/28",
        "internal": "x.x.x.x/24",
        "management": "x.x.x.x/28",
        "guest": "x.x.x.x/24"
    }},
    "devices": [
        {{
            "hostname": "fictional-hostname",
            "ip": "x.x.x.x",
            "role": "firewall|domain_controller|web_server|file_server|workstation|printer|vpn_gateway",
            "os": "operating system",
            "subnet": "dmz|internal|management"
        }}
    ],
    "users": [
        {{
            "username": "realistic username",
            "full_name": "fictional full name",
            "role": "standard|admin|service_account",
            "department": "department name",
            "groups": ["group names"],
            "workstation": "their usual workstation hostname",
            "typical_login_hours": "08:00-17:00"
        }}
    ],
    "policies": {{
        "mfa_required": true,
        "allowed_external_ssh": false,
        "allowed_rdp_external": false,
        "password_policy": "90 day rotation",
        "failed_login_threshold": 5,
        "vpn_required_remote": true
    }},
    "known_external_ips": [
        {{
            "ip": "x.x.x.x",
            "description": "what this IP is e.g. office VPN egress, vendor API"
        }}
    ],
    "threat_intel": {{
        "recently_blocked": [],
        "watchlist": []
    }}
}}

Make it realistic and internally consistent. Include 6-10 devices and 8-12 users. Use fictional but plausible names."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    env = json.loads(raw)
    return env

def save_environment(env: dict, path: str = ACTIVE_ENV_PATH):
    """Save environment to active slot."""
    with open(path, "w") as f:
        json.dump(env, f, indent=2)
    print(f"Environment saved to {path}")

def store_environment(env: dict) -> str:
    """Save environment to the environments library."""
    os.makedirs(ENVIRONMENTS_DIR, exist_ok=True)
    slug = env["org_name"].lower().replace(" ", "_").replace(".", "")
    filename = f"{slug}.json"
    path = os.path.join(ENVIRONMENTS_DIR, filename)
    
    # Handle name collisions
    counter = 1
    while os.path.exists(path):
        path = os.path.join(ENVIRONMENTS_DIR, f"{slug}_{counter}.json")
        counter += 1

    with open(path, "w") as f:
        json.dump(env, f, indent=2)
    
    print(f"Stored to library: {path}")
    return path

def list_environments() -> list[tuple[str, str]]:
    """Return list of (display_name, filepath) from the environments library."""
    if not os.path.exists(ENVIRONMENTS_DIR):
        return []
    
    envs = []
    for filename in sorted(os.listdir(ENVIRONMENTS_DIR)):
        if filename.endswith(".json"):
            path = os.path.join(ENVIRONMENTS_DIR, filename)
            try:
                with open(path) as f:
                    data = json.load(f)
                display = f"{data['org_name']} ({data['org_type']})"
                envs.append((display, path))
            except Exception:
                envs.append((filename, path))
    return envs

def select_environment() -> dict:
    """Interactive menu to pick an environment from the library."""
    envs = list_environments()
    
    if not envs:
        print("No saved environments found. Generate one first.")
        return None

    print("\n=== SAVED ENVIRONMENTS ===")
    for i, (display, _) in enumerate(envs, 1):
        print(f"  [{i}] {display}")
    print()

    while True:
        try:
            choice = int(input("Select environment: "))
            if 1 <= choice <= len(envs):
                path = envs[choice - 1][1]
                with open(path) as f:
                    env = json.load(f)
                save_environment(env)
                print(f"Active environment set to: {env['org_name']}")
                return env
            print(f"Enter a number between 1 and {len(envs)}")
        except ValueError:
            print("Enter a valid number")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None

def load_environment(path: str = ACTIVE_ENV_PATH) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def get_or_create_environment(org_type: str = None) -> dict:
    env = load_environment()
    if env:
        print(f"Using environment: {env['org_name']} ({env['org_type']})")
        return env

    print("No environment.json found. Generating randomized environment...")
    env = generate_environment(org_type)
    save_environment(env)
    store_environment(env)
    print(f"Generated: {env['org_name']} ({env['org_type']})")
    return env

def print_environment_summary(env: dict):
    print(f"\n{'='*50}")
    print(f"  {env['org_name'].upper()}")
    print(f"  {env['org_type']} | {env['domain']}")
    print(f"{'='*50}")
    print(f"\nSubnets:")
    for zone, subnet in env['subnets'].items():
        print(f"  {zone:<12} {subnet}")
    print(f"\nDevices ({len(env['devices'])}):")
    for d in env['devices']:
        print(f"  {d['ip']:<16} {d['hostname']:<20} {d['role']}")
    print(f"\nUsers ({len(env['users'])}):")
    for u in env['users']:
        print(f"  {u['username']:<20} {u['role']:<15} {u['department']}")
    print(f"\nPolicies:")
    for k, v in env['policies'].items():
        print(f"  {k:<30} {v}")
    print()

if __name__ == "__main__":
    import sys

    if "--new" in sys.argv:
        org_type = None
        for arg in sys.argv:
            if arg.startswith("--org="):
                org_type = arg.split("=", 1)[1]
        print("Generating new environment...")
        env = generate_environment(org_type)
        save_environment(env)
        store_environment(env)
        print_environment_summary(env)

    elif "--select" in sys.argv:
        env = select_environment()
        if env:
            print_environment_summary(env)

    elif "--list" in sys.argv:
        envs = list_environments()
        if not envs:
            print("No saved environments.")
        else:
            print("\n=== SAVED ENVIRONMENTS ===")
            for i, (display, path) in enumerate(envs, 1):
                print(f"  [{i}] {display}")
                print(f"      {path}")

    else:
        env = get_or_create_environment()
        print_environment_summary(env)