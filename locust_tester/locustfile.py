import os
from locust import HttpUser, task, between

# Read config from Environment Variables
TARGET_ENDPOINT = os.getenv("TARGET_ENDPOINT", "/")
API_KEY = os.getenv("API_KEY", "")

class DynamicApiUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # 1. Add standard API Key (Even if we bypass DB checks, it's good practice to send it)
        if API_KEY:
            self.client.headers.update({"X-API-KEY": API_KEY})
        
        # 2. INJECT BYPASS HEADER
        # This tells the backend: "I am a stress test. Do not log me."
        self.client.headers.update({"X-STRESS-TEST": "true"})

    @task
    def stress_test_endpoint(self):
        self.client.get(TARGET_ENDPOINT, name=TARGET_ENDPOINT)