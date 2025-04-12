import requests
from kubernetes import client, config
from datetime import datetime

# Load Kubernetes in-cluster config
config.load_incluster_config()

# Static configuration
PREDICTION_URL = "http://34.16.173.223:8000/predict"
SERVICE_NAMES = ["demo-api", "demo-api-2"]  # Add more service names here

# Current UTC timestamp in ISO 8601 format
current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

# Kubernetes API client
apps_v1 = client.AppsV1Api()

for service_name in SERVICE_NAMES:
    print(f"\n[INFO] Processing service: {service_name}")

    payload = {
        "timestamp": current_time,
        "serviceName": service_name
    }

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

        print(f"[INFO] Predicted pod count: {predicted_replicas}")
        print(f"[INFO] Previous pod count: {previous_replicas}")

        if predicted_replicas > previous_replicas:
            print(f"[INFO] Scaling UP: {previous_replicas} → {predicted_replicas}")
        elif predicted_replicas < previous_replicas:
            print(f"[INFO] Scaling DOWN: {previous_replicas} → {predicted_replicas}")
        else:
            print(f"[INFO] No scaling needed for '{service_name}'")

    except Exception as e:
        print(f"[ERROR] Failed to fetch prediction for '{service_name}': {e}")
        predicted_replicas = 1  # fallback

    # Patch deployment with predicted replica count
    patch_body = {
        "spec": {
            "replicas": predicted_replicas
        }
    }

    try:
        apps_v1.patch_namespaced_deployment(
            name=service_name,
            namespace="default",
            body=patch_body
        )
        print(f"[SUCCESS] Scaled '{service_name}' to {predicted_replicas} replicas")
    except Exception as e:
        print(f"[ERROR] Failed to scale deployment '{service_name}': {e}")
