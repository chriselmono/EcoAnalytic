from locust import HttpUser, task, between
import random

class Usuario(HttpUser):
    
    wait_time = between(1, 3)
    
    # Inicio de sesión 
    @task
    def login(self):
        data = {
            "usuario" : "admin",
            "password" : "123456"
        }
        
        response = self.client.post("/login", data=data, allow_redirects=True)
        
        print(response.status_code)
        
    # Registro
    @task
    def registro (self):
        numero = random