import requests

res = requests.post("http://34.94.220.156/get_all_users", json={"current_user_id": "1"})
print(res.json())
