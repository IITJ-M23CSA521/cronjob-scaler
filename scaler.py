import requests
from kubernetes import client, config
from datetime import datetime

# Load Kubernetes in-cluster config
config.load_incluster_config()

# Static configuration
PREDICTION_URL = "http://localhost:8000/predict"
SERVICE_NAME = "demo-api"

# Generate current UTC timestamp in ISO format
current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

# Request payload
payload = {
    "timestamp": current_time,
    "serviceName": SERVICE_NAME
}

# Get predicted number of replicas
try:
    response = requests.post(
        PREDICTION_URL,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    data = response.json()
    predicted_replicas = int(data.get("current_pod_num", 2))
    previous_replicas = int(data.get("previous_pod_num", 2))
    
    print(f"[INFO] Predicted current pod count from model: {predicted_replicas}")
    print(f"[INFO] Previous pod count: {previous_replicas}")

    # Determine increment or decrement logic
    if predicted_replicas > previous_replicas:
        print(f"[INFO] Scaling up from {previous_replicas} to {predicted_replicas} replicas")
    elif predicted_replicas < previous_replicas:
        print(f"[INFO] Scaling down from {previous_replicas} to {predicted_replicas} replicas")
    else:
        print(f"[INFO] No scaling needed. Current replicas ({predicted_replicas}) match previous replicas.")

except Exception as e:
    print(f"[ERROR] Failed to fetch prediction: {e}")
    predicted_replicas = 1  # fallback default

# Patch the Kubernetes deployment to match the predicted replicas
apps_v1 = client.AppsV1Api()
patch_body = {
    "spec": {
        "replicas": predicted_replicas
    }
}

try:
    apps_v1.patch_namespaced_deployment(
        name=SERVICE_NAME,
        namespace="default",
        body=patch_body
    )
    print(f"[SUCCESS] Scaled '{SERVICE_NAME}' to {predicted_replicas} replicas")
except Exception as e:
    print(f"[ERROR] Failed to scale deployment: {e}")
