import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
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
    if response.status_code != 200:
        print(f"❌ Failed to fetch listings for {ROOM_TYPES[room]} (Status: {response.status_code})")
        return

    # Save HTML for debugging
    with open(f"debug_response_{room}.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"📄 Saved HTML response to debug_response_{room}.html")

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Listings appear inside a div with class 'all-units-section cs_search_card search-content'
    container = soup.find("div", class_="all-units-section cs_search_card search-content")
    if not container:
        print(f"⚠️ Could not find listings container for {ROOM_TYPES[room]}. The page structure may have changed.")
        return

    # Check if there's a "no search found" message
    no_results = container.find("section", class_="no-search-found")
    if no_results:
        print(f"❌ No {ROOM_TYPES[room]} listings found in {LOCATION.replace('-', ' ').title()}")
        return

    listings = container.find_all("section", class_="all-units-cards")
    
    # Filter listings to only show those from the specified location
    filtered_listings = []
    for listing in listings:
        # Get location from the card details
        location_elem = listing.find("div", class_="card-details")
        if location_elem:
            span = location_elem.find("span")
            if span:
                location_text = span.get_text(strip=True)
                # Check if this listing is from the specified location
                # Convert location names to a comparable format
                if LOCATION.replace('-', ' ').lower() in location_text.lower() or location_text.lower() in LOCATION.replace('-', ' ').lower():
                    filtered_listings.append(listing)

    print(f"\n🏠 {ROOM_TYPES[room]} Listings in {LOCATION.replace('-', ' ').title()}:")
    if filtered_listings:
        print(f"✅ {len(filtered_listings)} listing(s) found!")
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
                            price = price_i.get_text(strip=True)
                    elif "Unit No." in text:
                        unit_i = span.find("i")
                        if unit_i:
                            unit_no = unit_i.get_text(strip=True)
                    elif not any(keyword in text for keyword in ["Price", "Unit No.", "Size", "Type", "Parking"]):
                        # This is likely the location
                        location = text
            
            print(f"- {title} (Unit {unit_no}): {price} AED/Year - {location}")
    else:
        print("❌ No listings available in the specified location.")

if __name__ == "__main__":
    for room in ROOM_TYPES:
        check_listings(room)
