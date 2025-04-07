import requests
import json
from kubernetes import client, config

# Load kube config (inside the cluster)
config.load_incluster_config()

# Kubernetes API client
api = client.AppsV1Api()

# Call your ML model API to get desired number of replicas
response = requests.get("http://model-service/predict")
predicted_replicas = int(response.json().get("replicas", 2))

# Patch the deployment
deployment_name = "model-service"
namespace = "default"

patch = {
    "spec": {
        "replicas": predicted_replicas
    }
}

api.patch_namespaced_deployment(
    name=deployment_name,
    namespace=namespace,
    body=patch
)

print(f"Scaled {deployment_name} to {predicted_replicas} replicas.")
