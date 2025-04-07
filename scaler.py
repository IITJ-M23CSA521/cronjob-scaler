# scaler.py

import requests
from kubernetes import client, config

# Load Kubernetes in-cluster config
config.load_incluster_config()

# Get replica count from model-service
try:
    response = requests.get("http://model-service/predict")
    response.raise_for_status()
    replicas = int(response.json().get("replicas", 2))
    print(f"[INFO] Predicted replicas from model: {replicas}")
except Exception as e:
    print(f"[ERROR] Failed to fetch prediction: {e}")
    replicas = 2  # Fallback

# Patch the demo-api deployment
apps_v1 = client.AppsV1Api()

patch_body = {
    "spec": {
        "replicas": replicas
    }
}

try:
    apps_v1.patch_namespaced_deployment(
        name="demo-api",
        namespace="default",
        body=patch_body
    )
    print(f"[SUCCESS] Scaled 'demo-api' to {replicas} replicas")
except Exception as e:
    print(f"[ERROR] Failed to scale deployment: {e}")
