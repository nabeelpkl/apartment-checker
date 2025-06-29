import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

ROOM_TYPES = {
    1: "1-Bedroom",
    2: "2-Bedroom",
    3: "3-Bedroom",
}

BASE_URL = "https://www.wasl.ae/en/search/residential"
LOCATION = "muhaisnah-fourth"

def check_listings(room):
    params = {
        "sortfield": "Price",
        "order": "Asc",
        "location": LOCATION,
        "room": room,
        "view": "grid"
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    # Always save the HTML response for debugging
    with open(f"debug_response_{room}.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    if response.status_code != 200:
        print(f"❌ Failed to fetch listings for {ROOM_TYPES[room]} (Status: {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Check if we got a CAPTCHA page
    if "Radware Captcha Page" in response.text or "hcaptcha" in response.text.lower():
        print(f"⚠️ CAPTCHA detected for {ROOM_TYPES[room]}. The website is blocking automated requests.")
        return None
    
    # Try different container selectors
    container = None
    container_selectors = [
        "div.all-units-section.cs_search_card.search-content",
        "div.all-units-section",
        "div.search-content"
    ]
    
    for selector in container_selectors:
        container = soup.select_one(selector)
        if container:
            break
    
    if not container:
        print(f"⚠️ Could not find listings container for {ROOM_TYPES[room]}. The page structure may have changed.")
        return None

    # Look for listings first, regardless of "no search found" message
    listings = container.find_all("section", class_="all-units-cards")
    
    if not listings:
        # Only show "no search found" if there are actually no listings
        no_results = container.find("section", class_="no-search-found")
        if no_results:
            print(f"❌ No {ROOM_TYPES[room]} listings found in {LOCATION.replace('-', ' ').title()}")
        else:
            print(f"❌ No {ROOM_TYPES[room]} listings found in {LOCATION.replace('-', ' ').title()}")
        return None
    
    # Filter listings to only show those from the specified location AND correct room type
    filtered_listings = []
    for listing in listings:
        # Get location from the card details
        location_elem = listing.find("div", class_="card-details")
        location_text = ""
        room_type_text = ""
        
        if location_elem:
            span = location_elem.find("span")
            if span:
                location_text = span.get_text(strip=True)
        
        # Get room type from card details
        card_details = listing.find_all("div", class_="card-details")
        for detail in card_details:
            span = detail.find("span")
            if span:
                text = span.get_text(strip=True)
                if "Type:" in text:
                    room_type_i = span.find("i")
                    if room_type_i:
                        room_type_text = room_type_i.get_text(strip=True).lower()
                        break
        
        # Check if this listing is from the specified location AND matches the requested room type
        location_match = LOCATION.replace('-', ' ').lower() in location_text.lower() or location_text.lower() in LOCATION.replace('-', ' ').lower()
        
        # Check room type match
        room_match = False
        if room == 1:
            room_match = "1 bedroom" in room_type_text or "studio" in room_type_text
        elif room == 2:
            room_match = "2 bedroom" in room_type_text or "2 room" in room_type_text
        elif room == 3:
            room_match = "3 bedroom" in room_type_text or "3 room" in room_type_text
        
        if location_match and room_match:
            filtered_listings.append(listing)

    if filtered_listings:
        result_lines = []
        for listing in filtered_listings:
            # Get building name from h3 tag
            title_elem = listing.find("h3")
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            # Get all card-details divs to find price and unit number
            card_details = listing.find_all("div", class_="card-details")
            price = "N/A"
            unit_no = "N/A"
            location = "N/A"
            
            for detail in card_details:
                span = detail.find("span")
                if span:
                    text = span.get_text(strip=True)
                    if "Price" in text:
                        price_i = span.find("i")
                        if price_i:
                            # Clean up the price text
                            price_text = price_i.get_text(strip=True)
                            price = price_text.replace('\n', '').replace('/', '').replace('Year', '').strip()
                    elif "Unit No." in text:
                        unit_i = span.find("i")
                        if unit_i:
                            unit_no = unit_i.get_text(strip=True)
                    elif not any(keyword in text for keyword in ["Price", "Unit No.", "Size", "Type", "Parking"]):
                        # This is likely the location
                        location = text
            
            listing_text = f"- {title} (Unit {unit_no}): {price} AED/Year - {location}"
            result_lines.append(listing_text)
        
        return {
            'room_type': ROOM_TYPES[room],
            'count': len(filtered_listings),
            'listings': result_lines
        }
    else:
        return None

def main():
    all_results = []
    
    for room in ROOM_TYPES:
        result = check_listings(room)
        
        if result:
            all_results.append(result)
        else:
            all_results.append({
                'room_type': ROOM_TYPES[room],
                'count': 0,
                'listings': []
            })
        
        # Add delay between requests (except for the last one)
        if room < max(ROOM_TYPES.keys()):
            time.sleep(10)
    
    # Print final results
    for result in all_results:
        print(f"\n🏠 {result['room_type']} Listings in {LOCATION.replace('-', ' ').title()}:")
        if result['count'] > 0:
            print(f"✅ {result['count']} listing(s) found!")
            for listing in result['listings']:
                print(listing)
        else:
            print("❌ No listings available in the specified location.")

if __name__ == "__main__":
    main()
