import subprocess
import threading
import time
import json
import os

class BluetoothManager:
    def __init__(self, agent):
        self.agent = agent
        self.connected_devices = {}
        self.paired_devices = {}
        self.discovery_thread = None
        self.discovery_running = False
    
    def is_bluetooth_available(self):
        try:
            result = subprocess.run(["which", "bluetoothctl"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def scan(self, duration=10):
        if not self.is_bluetooth_available():
            return "Bluetooth not available on this system"
        
        self.discovery_running = True
        devices = []
        
        def scan_thread():
            try:
                proc = subprocess.Popen(
                    ["bluetoothctl", "scan", "on"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                time.sleep(duration)
                proc.terminate()
                
                result = subprocess.run(
                    ["bluetoothctl", "devices"],
                    capture_output=True,
                    text=True
                )
                
                for line in result.stdout.strip().split("\n"):
                    if line.startswith("Device"):
                        parts = line.split(" ", 2)
                        if len(parts) >= 3:
                            mac, name = parts[1], parts[2]
                            devices.append({"mac": mac, "name": name})
                
                self.discovery_running = False
            except Exception as e:
                self.discovery_running = False
                return str(e)
        
        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()
        
        return f"Scanning for {duration}s... Use 'bluetooth devices' to see results"
    
    def devices(self):
        if not self.is_bluetooth_available():
            return "Bluetooth not available"
        
        try:
            result = subprocess.run(
                ["bluetoothctl", "devices"],
                capture_output=True,
                text=True
            )
            
            devices = []
            for line in result.stdout.strip().split("\n"):
                if line.startswith("Device"):
                    parts = line.split(" ", 2)
                    if len(parts) >= 3:
                        devices.append({
                            "mac": parts[1],
                            "name": parts[2]
                        })
            
            if devices:
                output = "Discovered devices:\n"
                for d in devices:
                    output += f"  {d['name']} ({d['mac']})\n"
                return output.strip()
            else:
                return "No devices found. Run 'bluetooth scan' first."
        except Exception as e:
            return f"Error: {e}"
    
    def pair(self, mac):
        if not self.is_bluetooth_available():
            return "Bluetooth not available"
        
        try:
            result = subprocess.run(
                ["bluetoothctl", "pair", mac],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.paired_devices[mac] = {"paired_at": time.time()}
                return f"Paired with {mac}"
            else:
                return f"Pairing failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Pairing timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def connect(self, mac):
        if not self.is_bluetooth_available():
            return "Bluetooth not available"
        
        try:
            result = subprocess.run(
                ["bluetoothctl", "connect", mac],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.connected_devices[mac] = {
                    "connected_at": time.time(),
                    "active": True
                }
                return f"Connected to {mac}"
            else:
                return f"Connection failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Connection timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def disconnect(self, mac):
        if not self.is_bluetooth_available():
            return "Bluetooth not available"
        
        try:
            result = subprocess.run(
                ["bluetoothctl", "disconnect", mac],
                capture_output=True,
                text=True
            )
            
            if mac in self.connected_devices:
                del self.connected_devices[mac]
            
            if result.returncode == 0:
                return f"Disconnected from {mac}"
            else:
                return f"Disconnect failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def paired(self):
        if not self.is_bluetooth_available():
            return "Bluetooth not available"
        
        try:
            result = subprocess.run(
                ["bluetoothctl", "paired-devices"],
                capture_output=True,
                text=True
            )
            
            devices = []
            for line in result.stdout.strip().split("\n"):
                if line.startswith("Device"):
                    parts = line.split(" ", 2)
                    if len(parts) >= 3:
                        devices.append({
                            "mac": parts[1],
                            "name": parts[2]
                        })
            
            if devices:
                output = "Paired devices:\n"
                for d in devices:
                    status = "connected" if d["mac"] in self.connected_devices else "disconnected"
                    output += f"  {d['name']} ({d['mac']}) - {status}\n"
                return output.strip()
            else:
                return "No paired devices"
        except Exception as e:
            return f"Error: {e}"
    
    def connected(self):
        if self.connected_devices:
            output = "Connected devices:\n"
            for mac, info in self.connected_devices.items():
                output += f"  {mac} (since {time.strftime('%H:%M:%S', time.localtime(info['connected_at']))})\n"
            return output.strip()
        else:
            return "No connected devices"
    
    def remove(self, mac):
        if not self.is_bluetooth_available():
            return "Bluetooth not available"
        
        try:
            result = subprocess.run(
                ["bluetoothctl", "remove", mac],
                capture_output=True,
                text=True
            )
            
            if mac in self.connected_devices:
                del self.connected_devices[mac]
            if mac in self.paired_devices:
                del self.paired_devices[mac]
            
            if result.returncode == 0:
                return f"Removed {mac}"
            else:
                return f"Remove failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def power(self, state):
        if not self.is_bluetooth_available():
            return "Bluetooth not available"
        
        action = "on" if state else "off"
        try:
            result = subprocess.run(
                ["bluetoothctl", "power", action],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Bluetooth powered {'on' if state else 'off'}"
            else:
                return f"Power failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def status(self):
        if not self.is_bluetooth_available():
            return "Bluetooth: Not available"
        
        try:
            result = subprocess.run(
                ["bluetoothctl", "show"],
                capture_output=True,
                text=True
            )
            
            output = "Bluetooth Status:\n"
            
            if "Powered: yes" in result.stdout:
                output += "  Power: On\n"
            elif "Powered: no" in result.stdout:
                output += "  Power: Off\n"
            
            if "Discovering: yes" in result.stdout:
                output += "  Discovering: Yes\n"
            
            connected = len(self.connected_devices)
            output += f"  Connected devices: {connected}\n"
            
            return output.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def send_file(self, mac, filepath):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        if mac not in self.connected_devices:
            return f"Not connected to {mac}. Connect first."
        
        try:
            filename = os.path.basename(filepath)
            result = subprocess.run(
                ["obexftp", "-b", mac, "-put", filepath],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return f"Sent {filename} to {mac}"
            else:
                return f"Send failed: {result.stderr}"
        except FileNotFoundError:
            return "obexftp not installed. Cannot send files."
        except subprocess.TimeoutExpired:
            return "File transfer timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def info(self, mac):
        if not self.is_bluetooth_available():
            return "Bluetooth not available"
        
        try:
            result = subprocess.run(
                ["bluetoothctl", "info", mac],
                capture_output=True,
                text=True
            )
            
            return result.stdout or f"No info for {mac}"
        except Exception as e:
            return f"Error: {e}"