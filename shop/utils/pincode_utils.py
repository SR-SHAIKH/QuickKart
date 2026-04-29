import requests

def fetch_pincode_data(pincode):
    """
    Fetches area and city data from data.gov.in (via postalpincode.in) for a given pincode.
    Returns (area_name, city) or (None, None) if lookup fails.
    """
    try:
        url = f"https://api.postalpincode.in/pincode/{pincode}"
        response = requests.get(url, timeout=3)
        data = response.json()

        if data and data[0]['Status'] == 'Success':
            # Take the first entry from PostOffice array
            post = data[0]['PostOffice'][0]
            area = post.get('Name')
            city = post.get('District')
            return area, city
            
    except Exception as e:
        print("API ERROR:", e)
    
    return None, None
