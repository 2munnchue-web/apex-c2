#!/bin/bash
echo "💖 DEPLOYING APEX-C2"
sudo apt update
sudo apt install -y python3-pip nmap rustscan hydra sqlmap nikto gobuster crackmapexec netifaces
pip3 install --user cryptography pillow requests netifaces
cp apex_c2.py ~/apex-c2/
chmod +x ~/apex-c2/apex_c2.py
echo "✅ Done! Run: python3 ~/apex-c2/apex_c2.py"
