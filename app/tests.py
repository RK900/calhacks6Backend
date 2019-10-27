import requests

res = requests.post("http://127.0.0.1:5000/get_path", json={"username": "vik", "phone_number": "4084554877"})
print(res.status_code)
