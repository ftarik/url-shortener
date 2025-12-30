"""
Example usage of the URL Shortener API
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def main():
    print("=== URL Shortener API Example ===\n")
    
    # 1. Create a shortened URL
    print("1. Creating shortened URL...")
    response = requests.post(
        f"{BASE_URL}/shorten",
        json={
            "url": "https://www.python.org/dev/peps/pep-0020/",
            "custom_code": "zen",
            "expires_in_days": 7
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"   ✓ Short URL created: {data['short_url']}")
        print(f"   ✓ Expires: {data['expires_at']}")
        short_code = data['short_code']
    else:
        print(f"   ✗ Error: {response.json()}")
        return
    
    print()
    
    # 2. Create another URL with auto-generated code
    print("2. Creating URL with auto-generated code...")
    response = requests.post(
        f"{BASE_URL}/shorten",
        json={"url": "https://fastapi.tiangolo.com/"}
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"   ✓ Short URL: {data['short_url']}")
        print(f"   ✓ Code: {data['short_code']}")
    
    print()
    
    # 3. Access the shortened URL (simulate a visit)
    print("3. Visiting shortened URL...")
    response = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
    if response.status_code == 307:
        print(f"   ✓ Redirects to: {response.headers['location']}")
    
    print()
    
    # 4. Get analytics
    print("4. Getting analytics...")
    response = requests.get(f"{BASE_URL}/analytics/{short_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Total clicks: {data['total_clicks']}")
        if data['analytics']:
            latest = data['analytics'][-1]
            print(f"   ✓ Latest visit: {latest['visited_at']}")
            print(f"   ✓ User agent: {latest['user_agent']}")
    
    print()
    
    # 5. Download QR code
    print("5. Downloading QR code...")
    response = requests.get(f"{BASE_URL}/qr/{short_code}")
    if response.status_code == 200:
        filename = f"{short_code}_qr.png"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"   ✓ QR code saved as: {filename}")
    
    print()
    
    # 6. List service info
    print("6. Getting service information...")
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Service: {data['service']} v{data['version']}")
        print(f"   ✓ Features: {', '.join(data['features'])}")
    
    print("\n=== Example completed ===")


if __name__ == "__main__":
    main()
