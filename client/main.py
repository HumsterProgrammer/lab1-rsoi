import requests

def test_post(name, age, address, work):
	posted_data = {"name":name, "age":age, "address":address, "work":work}
	resp = requests.post("https://lab1-rsoi-52zt.onrender.com/api/v1/persons", json=posted_data)
	print(resp.status_code)
	print(resp.json())

def test_delete(personId):
	#posted_data = {"name":name, "age":age, "address":address, "work":work}
	resp = requests.delete(f"https://lab1-rsoi-52zt.onrender.com/api/v1/persons/{personId}")
	print(resp.status_code)
	print(resp.json())

if __name__ == "__main__":
    #test_post("Ivan", 20, "Moscow, Tverskaya, 1", "Yandex")
