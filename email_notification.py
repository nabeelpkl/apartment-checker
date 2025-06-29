import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

# Email configuration
SMTP_SERVER = "smtp.gmail.com"  # Change if using different provider
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # Replace with your email
SENDER_PASSWORD = "your-app-password"  # Replace with your app password
RECIPIENT_EMAIL = "recipient@example.com"  # Replace with recipient email

# Apartment search configuration
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
    """Check apartment listings for a specific room type"""
    params = {
        "sortfield": "Price",
        "order": "Asc",
        "location": LOCATION,
        "room": room,
        "view": "grid"
    }

    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
        if response.status_code != 200:
            return f"❌ Failed to fetch listings for {ROOM_TYPES[room]} (Status: {response.status_code})"

        soup = BeautifulSoup(response.text, "html.parser")
        
        container = soup.find("div", class_="all-units-section cs_search_card search-content")
        if not container:
            return f"⚠️ Could not find listings container for {ROOM_TYPES[room]}"

        # Check if there's a "no search found" message
        no_results = container.find("section", class_="no-search-found")
        if no_results:
            return f"❌ No {ROOM_TYPES[room]} listings found in {LOCATION.replace('-', ' ').title()}"

        listings = container.find_all("section", class_="all-units-cards")
        
        # Filter listings to only show those from the specified location
        filtered_listings = []
        for listing in listings:
            location_elem = listing.find("div", class_="card-details")
            if location_elem:
                span = location_elem.find("span")
                if span:
                    location_text = span.get_text(strip=True)
                    if LOCATION.replace('-', ' ').lower() in location_text.lower() or location_text.lower() in LOCATION.replace('-', ' ').lower():
                        filtered_listings.append(listing)

        if not filtered_listings:
            return f"❌ No {ROOM_TYPES[room]} listings available in {LOCATION.replace('-', ' ').title()}"

        # Build listing details
        result = f"🏠 {ROOM_TYPES[room]} Listings in {LOCATION.replace('-', ' ').title()}:\n"
        result += f"✅ {len(filtered_listings)} listing(s) found!\n\n"
        
        for listing in filtered_listings:
            title_elem = listing.find("h3")
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
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
                        location = text
            
            result += f"• {title} (Unit {unit_no}): {price} AED/Year - {location}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error checking {ROOM_TYPES[room]} listings: {str(e)}"

def send_email(subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {RECIPIENT_EMAIL}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

def main():
    """Main function to check listings and send email"""
    print(f"🔍 Checking apartment availability at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check all room types
    all_results = []
    for room in ROOM_TYPES:
        result = check_listings(room)
        all_results.append(result)
        print(result)
        print("-" * 50)
    
    # Prepare email content
    email_body = f"""Apartment Availability Check - {datetime.now().strftime('%Y-%m-%d')}

Location: {LOCATION.replace('-', ' ').title()}
Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*50}

"""
    
    email_body += "\n\n".join(all_results)
    
    email_body += f"""

{'='*50}
This is an automated check from your apartment availability script.
"""
    
    # Send email
    subject = f"🏠 Apartment Availability - {LOCATION.replace('-', ' ').title()} - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, email_body)

if __name__ == "__main__":
    main() 