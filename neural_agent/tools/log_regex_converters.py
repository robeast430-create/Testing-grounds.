import re
import os
import json
from datetime import datetime

class LogAnalyzer:
    def __init__(self, agent):
        self.agent = agent
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def parse_log_file(self, filepath, format="auto"):
        if not os.path.exists(filepath):
            return "File not found"
        
        entries = []
        
        with open(filepath, "r") as f:
            for line_num, line in enumerate(f, 1):
                entry = self.parse_log_line(line, format)
                if entry:
                    entry["line"] = line_num
                    entries.append(entry)
        
        return entries
    
    def parse_log_line(self, line, format="auto"):
        patterns = {
            "apache": r'(\S+) - \S+ \[(\S+) \S+\] "(\S+) (\S+)" (\d+)',
            "nginx": r'(\S+) - \S+ \[(\S+) \S+\] "(\S+) (\S+)" (\d+)',
            "syslog": r'(\S+\s+\d+\s+\S+) (\S+) (\S+): (.+)',
            "json": r'\{.*\}',
            "simple": r'(\S+)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[?(\w+)\]?\s*(.*)'
        }
        
        if format == "json":
            try:
                return json.loads(line)
            except:
                return None
        
        for fmt, pattern in patterns.items():
            match = re.match(pattern, line)
            if match:
                if fmt == "simple":
                    return {
                        "level": match.group(3),
                        "timestamp": match.group(2),
                        "message": match.group(4)
                    }
                elif fmt in ["apache", "nginx"]:
                    return {
                        "ip": match.group(1),
                        "timestamp": match.group(2),
                        "method": match.group(3),
                        "path": match.group(4),
                        "status": match.group(5)
                    }
                elif fmt == "syslog":
                    return {
                        "timestamp": match.group(1),
                        "host": match.group(2),
                        "service": match.group(3),
                        "message": match.group(4)
                    }
        
        return {"message": line.strip()}
    
    def analyze(self, filepath, format="auto"):
        entries = self.parse_log_file(filepath, format)
        
        if isinstance(entries, str):
            return entries
        
        stats = {
            "total_lines": len(entries),
            "by_level": {},
            "by_hour": {},
            "errors": [],
            "warnings": []
        }
        
        for entry in entries:
            level = entry.get("level", "UNKNOWN")
            if level in self.log_levels:
                stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            if level in ["ERROR", "CRITICAL"]:
                stats["errors"].append(entry)
            
            if level == "WARNING":
                stats["warnings"].append(entry)
            
            timestamp = entry.get("timestamp", "")
            if timestamp:
                try:
                    hour = timestamp.split()[1][:2] if " " in timestamp else timestamp[:2]
                    stats["by_hour"][hour] = stats["by_hour"].get(hour, 0) + 1
                except:
                    pass
        
        return stats
    
    def tail(self, filepath, lines=50):
        if not os.path.exists(filepath):
            return "File not found"
        
        with open(filepath, "r") as f:
            all_lines = f.readlines()
        
        return "".join(all_lines[-lines:])
    
    def grep(self, filepath, pattern, case_insensitive=False):
        if not os.path.exists(filepath):
            return "File not found"
        
        flags = re.IGNORECASE if case_insensitive else 0
        regex = re.compile(pattern, flags)
        
        matches = []
        with open(filepath, "r") as f:
            for line_num, line in enumerate(f, 1):
                if regex.search(line):
                    matches.append({
                        "line": line_num,
                        "content": line.rstrip()
                    })
        
        return matches
    
    def stats(self, filepath):
        if not os.path.exists(filepath):
            return "File not found"
        
        with open(filepath, "r") as f:
            lines = f.readlines()
        
        total = len(lines)
        empty = sum(1 for l in lines if not l.strip())
        
        return {
            "total_lines": total,
            "non_empty": total - empty,
            "empty": empty,
            "bytes": os.path.getsize(filepath)
        }


class RegexTools:
    def __init__(self):
        self.patterns = {
            "email": r'[\w.-]+@[\w.-]+\.\w+',
            "url": r'https?://\S+',
            "ip": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "date_iso": r'\d{4}-\d{2}-\d{2}',
            "date_us": r'\d{1,2}/\d{1,2}/\d{2,4}',
            "time": r'\d{2}:\d{2}(:\d{2})?',
            "hex_color": r'#[0-9a-fA-F]{3,6}',
            "uuid": r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            "mac": r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}',
            "hashtag": r'#\w+',
            "mention": r'@\w+',
            "html_tag": r'<[^>]+>',
            "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
        }
    
    def match(self, pattern, text, flags=0):
        regex = re.compile(pattern, flags)
        match = regex.search(text)
        if match:
            return {
                "matched": match.group(),
                "start": match.start(),
                "end": match.end(),
                "groups": match.groups()
            }
        return None
    
    def find_all(self, pattern, text, flags=0):
        regex = re.compile(pattern, flags)
        matches = regex.findall(text)
        return matches
    
    def replace(self, pattern, replacement, text, flags=0):
        regex = re.compile(pattern, flags)
        return regex.sub(replacement, text)
    
    def extract(self, pattern_type, text):
        pattern = self.patterns.get(pattern_type)
        if not pattern:
            return []
        return self.find_all(pattern, text)
    
    def validate(self, pattern, text):
        regex = re.compile(pattern)
        return regex.fullmatch(text) is not None
    
    def named_patterns(self):
        return list(self.patterns.keys())
    
    def test_pattern(self, pattern, text, flags=0):
        try:
            regex = re.compile(pattern, flags)
            matches = regex.findall(text)
            return {
                "valid": True,
                "matches": matches,
                "count": len(matches)
            }
        except re.error as e:
            return {
                "valid": False,
                "error": str(e)
            }


class FileConverter:
    def __init__(self):
        self.supported = ["csv", "json", "xml", "yaml", "ini"]
    
    def csv_to_json(self, csv_path, delimiter=",", has_header=True):
        import csv
        import json as json_module
        
        rows = []
        with open(csv_path, "r") as f:
            reader = csv.reader(f, delimiter=delimiter)
            if has_header:
                headers = next(reader)
                for row in reader:
                    rows.append(dict(zip(headers, row)))
            else:
                for row in reader:
                    rows.append(row)
        
        return json_module.dumps(rows, indent=2)
    
    def json_to_csv(self, json_path, csv_path, delimiter=","):
        import csv
        import json as json_module
        
        with open(json_path, "r") as f:
            data = json_module.load(f)
        
        if not data:
            return "No data to convert"
        
        if isinstance(data, list) and len(data) > 0:
            headers = list(data[0].keys()) if isinstance(data[0], dict) else [f"col{i}" for i in range(len(data[0]))]
        elif isinstance(data, dict):
            headers = list(data.keys())
            data = [data]
        else:
            return "Unsupported JSON structure"
        
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter)
            writer.writeheader()
            for item in data:
                if isinstance(item, dict):
                    writer.writerow(item)
        
        return f"Converted to {csv_path}"
    
    def json_to_xml(self, json_path, xml_path, root="data"):
        import json
        import xml.etree.ElementTree as ET
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        def dict_to_xml(parent, dictionary):
            for key, value in dictionary.items():
                child = ET.SubElement(parent, str(key))
                if isinstance(value, dict):
                    dict_to_xml(child, value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            item_elem = ET.SubElement(child, "item")
                            dict_to_xml(item_elem, item)
                        else:
                            ET.SubElement(child, "item").text = str(item)
                else:
                    child.text = str(value)
        
        root_elem = ET.Element(root)
        if isinstance(data, list):
            for item in data:
                dict_to_xml(root_elem, item)
        else:
            dict_to_xml(root_elem, data)
        
        ET.ElementTree(root_elem).write(xml_path, encoding="unicode")
        return f"Converted to {xml_path}"
    
    def yaml_to_json(self, yaml_path, json_path):
        try:
            import yaml
        except ImportError:
            return "PyYAML not installed"
        
        import json
        
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)
        
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return f"Converted to {json_path}"
    
    def json_to_yaml(self, json_path, yaml_path):
        try:
            import yaml
        except ImportError:
            return "PyYAML not installed"
        
        import json
        
        with open(json_path, "r") as f:
            data = json.load(f)
        
        with open(yaml_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
        
        return f"Converted to {yaml_path}"
    
    def ini_to_dict(self, ini_path):
        import configparser
        
        config = configparser.ConfigParser()
        config.read(ini_path)
        
        return {section: dict(config[section]) for section in config.sections()}


class ImageProcessor:
    def __init__(self):
        self.tools = {}
    
    def is_pillow_available(self):
        try:
            from PIL import Image
            return True
        except ImportError:
            return False
    
    def resize(self, image_path, output_path, width, height):
        if not self.is_pillow_available():
            return "Pillow not installed"
        
        from PIL import Image
        
        with Image.open(image_path) as img:
            resized = img.resize((width, height))
            resized.save(output_path)
        
        return f"Resized to {width}x{height}"
    
    def convert_format(self, image_path, output_path, format):
        if not self.is_pillow_available():
            return "Pillow not installed"
        
        from PIL import Image
        
        with Image.open(image_path) as img:
            img.save(output_path, format=format.upper())
        
        return f"Converted to {format}"
    
    def thumbnail(self, image_path, output_path, max_size=256):
        if not self.is_pillow_available():
            return "Pillow not installed"
        
        from PIL import Image
        
        with Image.open(image_path) as img:
            img.thumbnail((max_size, max_size))
            img.save(output_path)
        
        return f"Created thumbnail"
    
    def get_info(self, image_path):
        if not self.is_pillow_available():
            return "Pillow not installed"
        
        from PIL import Image
        
        with Image.open(image_path) as img:
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.width,
                "height": img.height
            }
    
    def crop(self, image_path, output_path, left, top, right, bottom):
        if not self.is_pillow_available():
            return "Pillow not installed"
        
        from PIL import Image
        
        with Image.open(image_path) as img:
            cropped = img.crop((left, top, right, bottom))
            cropped.save(output_path)
        
        return f"Cropped region: {left},{top} to {right},{bottom}"
    
    def rotate(self, image_path, output_path, degrees):
        if not self.is_pillow_available():
            return "Pillow not installed"
        
        from PIL import Image
        
        with Image.open(image_path) as img:
            rotated = img.rotate(degrees, expand=True)
            rotated.save(output_path)
        
        return f"Rotated {degrees} degrees"