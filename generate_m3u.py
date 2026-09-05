import requests

url = 'https://boti.my.id/index.php?api=playlist&email=mbkidriss9%40gmail.com&password=12345678'
headers = {'Accept': 'application/json'}

response = requests.get(url, headers=headers)
# Menampilkan 1500 karakter pertama agar tidak terlalu panjang di chat
print(response.text[:1500]) 
