import requests

url = "http://localhost:5000/webhook"
payload = {
    "from": "tester",
    "body": "Oi"
}

response = requests.post(url, json=payload)
print("Status:", response.status_code)
print("Resposta:", response.text)
