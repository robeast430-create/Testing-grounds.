import boto3
import json
import os
from datetime import datetime

class AWSManager:
    def __init__(self, access_key=None, secret_key=None, region="us-east-1"):
        self.access_key = access_key or os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret_key = secret_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.region = region
        self._clients = {}
    
    def _get_client(self, service):
        if service not in self._clients:
            self._clients[service] = boto3.client(
                service,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
        return self._clients[service]
    
    def s3_list_buckets(self):
        try:
            s3 = self._get_client("s3")
            buckets = s3.list_buckets()["Buckets"]
            return [{"name": b["Name"], "created": b["CreationDate"].isoformat()} for b in buckets]
        except Exception as e:
            return {"error": str(e)}
    
    def s3_list_objects(self, bucket, prefix=""):
        try:
            s3 = self._get_client("s3")
            response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            return {"error": str(e)}
    
    def s3_upload_file(self, bucket, key, filepath):
        try:
            s3 = self._get_client("s3")
            s3.upload_file(filepath, bucket, key)
            return f"Uploaded {filepath} to s3://{bucket}/{key}"
        except Exception as e:
            return {"error": str(e)}
    
    def s3_download_file(self, bucket, key, filepath):
        try:
            s3 = self._get_client("s3")
            s3.download_file(bucket, key, filepath)
            return f"Downloaded s3://{bucket}/{key} to {filepath}"
        except Exception as e:
            return {"error": str(e)}
    
    def ec2_list_instances(self):
        try:
            ec2 = self._get_client("ec2")
            instances = ec2.describe_instances()
            result = []
            for reservation in instances["Reservations"]:
                for inst in reservation["Instances"]:
                    result.append({
                        "id": inst["InstanceId"],
                        "type": inst["InstanceType"],
                        "state": inst["State"]["Name"],
                        "public_ip": inst.get("PublicIpAddress"),
                        "private_ip": inst.get("PrivateIpAddress")
                    })
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def ec2_start(self, instance_id):
        try:
            ec2 = self._get_client("ec2")
            ec2.start_instances(InstanceIds=[instance_id])
            return f"Starting instance {instance_id}"
        except Exception as e:
            return {"error": str(e)}
    
    def ec2_stop(self, instance_id):
        try:
            ec2 = self._get_client("ec2")
            ec2.stop_instances(InstanceIds=[instance_id])
            return f"Stopping instance {instance_id}"
        except Exception as e:
            return {"error": str(e)}
    
    def lambda_list(self):
        try:
            lambda_client = self._get_client("lambda")
            functions = lambda_client.list_functions()
            return [{"name": f["FunctionName"], "runtime": f["Runtime"]} for f in functions["Functions"]]
        except Exception as e:
            return {"error": str(e)}
    
    def cloudwatch_get_metrics(self, namespace, metric_name):
        try:
            cw = self._get_client("cloudwatch")
            response = cw.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Period=300,
                StartTime=datetime.now().isoformat(),
                EndTime=datetime.now().isoformat(),
                Statistics=["Average"]
            )
            return response.get("Datapoints", [])
        except Exception as e:
            return {"error": str(e)}


class CloudflareManager:
    def __init__(self, api_token=None):
        self.api_token = api_token or os.environ.get("CLOUDFLARE_TOKEN")
        self.base_url = "https://api.cloudflare.com/client/v4"
    
    def _request(self, method, endpoint, data=None):
        import requests
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}
        
        response = requests.request(method, url, headers=headers, json=data)
        return response.json()
    
    def list_zones(self):
        return self._request("GET", "zones")
    
    def list_dns(self, zone_id):
        return self._request("GET", f"zones/{zone_id}/dns_records")
    
    def add_dns(self, zone_id, name, content, type="A", ttl=3600):
        data = {"type": type, "name": name, "content": content, "ttl": ttl}
        return self._request("POST", f"zones/{zone_id}/dns_records", data)
    
    def delete_dns(self, zone_id, record_id):
        return self._request("DELETE", f"zones/{zone_id}/dns_records/{record_id}")


class VercelManager:
    def __init__(self, token=None):
        self.token = token or os.environ.get("VERCEL_TOKEN")
        self.base_url = "https://api.vercel.com/v1"
    
    def _request(self, endpoint):
        import requests
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}
        return requests.get(url, headers=headers).json()
    
    def list_deployments(self):
        return self._request("deployments")
    
    def get_deployment(self, id):
        return self._request(f"deployments/{id}")
    
    def list_projects(self):
        return self._request("projects")


class SupabaseManager:
    def __init__(self, url, key):
        self.url = url
        self.key = key
    
    def select(self, table, filters=None, limit=100):
        import requests
        url = f"{self.url}/rest/v1/{table}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
        params = {"limit": limit}
        if filters:
            params.update(filters)
        return requests.get(url, headers=headers, params=params).json()
    
    def insert(self, table, data):
        import requests
        url = f"{self.url}/rest/v1/{table}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        return requests.post(url, headers=headers, json=data).json()
    
    def update(self, table, data, filters):
        import requests
        url = f"{self.url}/rest/v1/{table}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        return requests.patch(url, headers=headers, json=data, params=filters).json()
    
    def delete(self, table, filters):
        import requests
        url = f"{self.url}/rest/v1/{table}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}"
        }
        return requests.delete(url, headers=headers, params=filters).json()


class TerraformManager:
    def __init__(self, project_dir="./"):
        self.project_dir = project_dir
        self.state_file = os.path.join(project_dir, "terraform.tfstate")
    
    def init(self):
        import subprocess
        result = subprocess.run(["terraform", "init"], cwd=self.project_dir, capture_output=True, text=True)
        return result.stdout or result.stderr
    
    def plan(self, out_file=None):
        import subprocess
        cmd = ["terraform", "plan"]
        if out_file:
            cmd.extend(["-out", out_file])
        result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
        return result.stdout or result.stderr
    
    def apply(self, auto_approve=True):
        import subprocess
        cmd = ["terraform", "apply"]
        if auto_approve:
            cmd.append("-auto-approve")
        result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True, timeout=600)
        return result.stdout or result.stderr
    
    def destroy(self, auto_approve=True):
        import subprocess
        cmd = ["terraform", "destroy"]
        if auto_approve:
            cmd.append("-auto-approve")
        result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True, timeout=600)
        return result.stdout or result.stderr
    
    def show(self):
        import subprocess
        result = subprocess.run(["terraform", "show"], cwd=self.project_dir, capture_output=True, text=True)
        return result.stdout
    
    def state_list(self):
        import subprocess
        result = subprocess.run(["terraform", "state", "list"], cwd=self.project_dir, capture_output=True, text=True)
        return result.stdout.splitlines()
    
    def output(self):
        import subprocess
        result = subprocess.run(["terraform", "output"], cwd=self.project_dir, capture_output=True, text=True)
        return result.stdout