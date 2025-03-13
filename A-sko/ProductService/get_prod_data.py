import requests
import json
import random

# enter the file path of the json 
file_path = "A-sko\Product_Details.json"
def fetch_api_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad status codes
        return response.json()  # No need for if-else block, response.json() handles non-200 status codes
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Example usage
api_url = "https://fakestoreapi.com/products"
data = fetch_api_data(api_url)

if data:
    for item in data:
        # Removing unnecessary keys
        item.pop('rating', None)
        item.pop('quantity/available', None)
        # Adding random rating and availability
        item['rating'] = random.randint(3, 5)
        item['available'] = random.randint(15, 20)
    
    # Filtering out electronics and jewelry
    items = [item for item in data if item['category'] not in ['electronics', 'jewelery']]
    
    # Adding ids to items
    for index, item in enumerate(items, start=1):
        item["id"] = index
    
    updated_json_data = json.dumps(items, indent=2)

    with open(file_path, "w") as file:
        file.write(updated_json_data)
else:
    print("Failed to fetch API data.")
