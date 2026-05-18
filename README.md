# SOC Triage Assistant

Generates synthetic security logs for SOC analyst training, anomaly detection, and ML dataset construction. Uses Claude Haiku to produce realistic Linux, Windows, and network logs across a range of attack profiles and normal baseline activity, all grounded in a consistent network environment.

---

## Why

Real attack logs are proprietary, legally sensitive, or stripped of the contextual signals that make them useful for training. This tool generates correlated log data on demand, including matched network logs for every host-based attack scenario, anchored to a fictional but internally consistent organization with real hostnames, users, subnets, and security policies.

---

## Setup

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

---

## Environment

Every log is grounded in a network environment profile — a fictional organization with subnets, devices, users, and security policies. Logs reference this environment directly: real hostnames, real usernames, real IPs from a consistent internal network.

Environments are saved to a local library in `environments/` and can be reused, swapped, or edited at any time.

```bash
python environment.py                             # view active environment
python environment.py --new                       # generate and activate a new random environment
python environment.py --new --org="energy utility"  # specify org type
python environment.py --select                    # pick from saved library
python environment.py --list                      # list all saved environments
```

The active environment is stored in `environment.json`. Edit it directly to customize. Delete it to regenerate on next run. Every newly generated environment is automatically added to the library.

---

## Generating Logs

```bash
# Single profile + auto-generated companion network log
python attack-log-generator.py linux successful-breach 20

# Full corpus, all profiles, all OS types, all network companions
python attack-log-generator.py

# Full corpus at custom duration
python attack-log-generator.py all 20

# Network-only profile
python attack-log-generator.py network dns-exfiltration 15
```

### Environment flags

Prepend any of these to any command:

```bash
--new-env                  # generate and use a fresh random environment
--new-env --org=<type>     # generate for a specific org type
--select-env               # pick from saved library before generating
--no-env                   # skip environment context entirely
```

Examples:

```bash
python attack-log-generator.py --new-env linux successful-breach 20
python attack-log-generator.py --select-env windows password-spray 15
python attack-log-generator.py --no-env linux port-scan 10
```

---

## Attack Profiles

### Linux
| Profile | Description |
|---|---|
| `ssh-bruteforce` | Distributed brute force across common usernames |
| `slow-burn` | Evasive, rate-limited brute force with long pauses |
| `successful-breach` | Brute force, login, sudo enumeration, C2 callback |
| `port-scan` | Nmap-style scan and service enumeration |
| `normal` | Baseline business hours activity |

### Windows
| Profile | Description |
|---|---|
| `password-spray` | AD password spray (Event IDs 4625, 4624, 4648) |
| `successful-breach` | Auth failure, success, lateral movement (4624, 4672, 4688, 4776) |
| `privilege-escalation` | Scheduled task and service manipulation (4698, 4702, 7045) |
| `lateral-movement` | SMB and remote service execution (4624, 4648, 5140, 7036) |
| `normal` | Baseline AD environment activity |

### Network
| Profile | Description |
|---|---|
| `ssh-bruteforce` | Firewall/NetFlow correlated with SSH brute force |
| `slow-burn` | Sparse connection attempts across rotating source IPs |
| `successful-breach` | Port 22 traffic, outbound anomalies, C2 callback |
| `port-scan` | Sequential port hits, SYN probes, service enumeration |
| `password-spray` | SMB/Kerberos volume spike to domain controller |
| `lateral-movement` | Internal SMB and RPC between hosts |
| `privilege-escalation` | DCOM, WMI, scheduled task network activity |
| `c2-callback` | Beaconing traffic, regular intervals, DNS indicators |
| `dns-exfiltration` | Long query strings, TXT records, high query frequency |
| `normal` | Baseline network traffic |

Every Linux and Windows profile generates a correlated network log automatically.

---

## Output Structure

```
environments/          # saved environment library
  org_name.json
  ...

sample_logs/
  linux/
  windows/
  network/
    linux/
    windows/
    standalone/
```

---

## What's Next

- Log parser and normalization layer
- Classical ML anomaly pre-filter (XGBoost)
- Claude triage engine with MITRE ATT&CK classification
- IOC enrichment via AbuseIPDB and VirusTotal
- FastAPI backend
- SOC dashboard (React)

---

## Notes

- All IPs, hostnames, and usernames are fictional
- `sample_logs/` and `environments/` are gitignored
- For training and educational purposes only