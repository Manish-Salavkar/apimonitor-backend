from pydantic import BaseModel

class StressTestConfig(BaseModel):
    target_host: str 
    target_endpoint: str
    api_key: str  # <--- NEW: Accept the key in the config
    
    num_users: int = 10
    spawn_rate: int = 2
    duration: int = 10