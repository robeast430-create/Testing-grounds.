import socket
import subprocess
import requests
import json
import hashlib
import os

class NetworkTools:
    def __init__(self):
        self.ping_count = 4
    
    def ping(self, host, count=4):
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), host],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            return f"Ping failed: {e}"
    
    def traceroute(self, host):
        try:
            result = subprocess.run(
                ["traceroute", host],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout
        except Exception as e:
            return f"Traceroute failed: {e}"
    
    def nslookup(self, hostname):
        try:
            result = subprocess.run(
                ["nslookup", hostname],
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            return f"NSLookup failed: {e}"
    
    def dig(self, domain, record_type="A"):
        try:
            result = subprocess.run(
                ["dig", domain, record_type, "+short"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception as e:
            return f"DIG failed: {e}"
    
    def netstat(self, listening=False):
        try:
            cmd = ["netstat", "-tuln"] if listening else ["netstat", "-tun"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Netstat failed: {e}"
    
    def ports_open(self, host, ports=[21, 22, 80, 443, 3306, 5432, 8080]):
        results = []
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                results.append(f"{port}: OPEN")
            sock.close()
        return "\n".join(results) if results else "No open ports found"
    
    def bandwidth_test(self, host="8.8.8.8"):
        try:
            import speedtest
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download()
            upload = st.upload()
            return f"Download: {download/1024/1024:.2f} Mbps\nUpload: {upload/1024/1024:.2f} Mbps"
        except:
            return "Speedtest failed"
    
    def ip_info(self, ip=None):
        try:
            url = f"http://ip-api.com/json/{ip if ip else ''}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data["status"] == "success":
                return json.dumps({
                    "ip": data.get("query"),
                    "country": data.get("country"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                    "isp": data.get("isp"),
                    "org": data.get("org"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon")
                }, indent=2)
            return "Could not get IP info"
        except Exception as e:
            return f"Error: {e}"
    
    def check_dns(self, domain):
        try:
            ip = socket.gethostbyname(domain)
            return f"{domain} -> {ip}"
        except socket.gaierror:
            return f"Could not resolve {domain}"
    
    def mac_lookup(self, mac):
        try:
            url = f"https://api.macvendors.com/{mac}"
            response = requests.get(url, timeout=5)
            return f"MAC {mac}: {response.text}"
        except:
            return f"Could not lookup MAC: {mac}"


class SecurityTools:
    def __init__(self):
        self.common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            27017: "MongoDB",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt"
        }
    
    def hash_string(self, text, algorithm="sha256"):
        if algorithm == "md5":
            return hashlib.md5(text.encode()).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(text.encode()).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(text.encode()).hexdigest()
        return "Unknown algorithm"
    
    def verify_hash(self, text, hash_value, algorithm="sha256"):
        computed = self.hash_string(text, algorithm)
        return computed.lower() == hash_value.lower()
    
    def generate_password(self, length=16, charset=None):
        import secrets
        import string
        
        if charset == "alpha":
            chars = string.ascii_letters
        elif charset == "alphanum":
            chars = string.ascii_letters + string.digits
        elif charset == "complex":
            chars = string.ascii_letters + string.digits + string.punctuation
        else:
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
        
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    def crack_hash(self, hash_value, wordlist=None):
        if not wordlist:
            return "Wordlist required for cracking"
        
        if not os.path.exists(wordlist):
            return f"Wordlist not found: {wordlist}"
        
        checked = 0
        with open(wordlist, "r") as f:
            for line in f:
                word = line.strip()
                for algo in ["md5", "sha1", "sha256"]:
                    if self.hash_string(word, algo) == hash_value.lower():
                        return f"Found: {word} (algorithm: {algo})"
                checked += 1
                if checked % 10000 == 0:
                    print(f"Checked {checked} words...")
        
        return f"No match found (checked {checked} words)"
    
    def encode_base64(self, text):
        import base64
        return base64.b64encode(text.encode()).decode()
    
    def decode_base64(self, encoded):
        import base64
        try:
            return base64.b64decode(encoded.encode()).decode()
        except:
            return "Invalid base64"
    
    def encode_hex(self, text):
        return text.encode().hex()
    
    def decode_hex(self, hex_str):
        return bytes.fromhex(hex_str).decode()
    
    def url_encode(self, text):
        return requests.utils.quote(text)
    
    def url_decode(self, text):
        return requests.utils.unquote(text)
    
    def xor_encrypt(self, data, key):
        return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(data, (key * (len(data) // len(key) + 1))[:len(data)]))
    
    def caesar_cipher(self, text, shift=3, decode=False):
        result = []
        for char in text:
            if char.isalpha():
                offset = 65 if char.isupper() else 97
                shift_amount = -shift if decode else shift
                result.append(chr((ord(char) - offset + shift_amount) % 26 + offset))
            else:
                result.append(char)
        return ''.join(result)


class PortScanner:
    def __init__(self):
        self.common_ports = sorted([21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017])
    
    def scan(self, host, ports=None, timeout=1):
        if ports is None:
            ports = self.common_ports
        
        open_ports = []
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((host, port))
            
            if result == 0:
                service = self.get_service_name(port)
                open_ports.append({"port": port, "service": service})
            
            sock.close()
        
        return open_ports
    
    def get_service_name(self, port):
        services = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            993: "IMAPS",
            995: "POP3S",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            6379: "Redis",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt",
            27017: "MongoDB"
        }
        return services.get(port, "Unknown")


class SSLChecker:
    def __init__(self):
        self.cert = None
    
    def get_cert(self, host, port=443):
        try:
            import ssl
            context = ssl.create_default_context()
            conn = socket.create_connection((host, port))
            ssock = context.wrap_socket(conn, server_hostname=host)
            cert = ssock.getpeercert()
            ssock.close()
            conn.close()
            return cert
        except Exception as e:
            return {"error": str(e)}
    
    def check_ssl(self, host, port=443):
        cert = self.get_cert(host, port)
        
        if "error" in cert:
            return cert["error"]
        
        from datetime import datetime
        not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        
        days_left = (not_after - datetime.now()).days
        
        return {
            "host": host,
            "valid": days_left > 0,
            "expires": not_after.isoformat(),
            "days_left": days_left,
            "issuer": dict(cert.get("issuer", []))
        }