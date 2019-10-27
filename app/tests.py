import requests

res = requests.post("http://34.94.220.156/request_user_loc", json={"current_user_id": "1","reques"})
print(res.json())
dic = res.json()["friends"]
for item in dic:
    print(item)