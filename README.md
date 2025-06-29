# 🏠 Apartment Availability Checker

Automatically checks for apartment availability on the WASL website in Muhaisnah Fourth, Dubai.

## Features

- ✅ **Automated daily checks** at 5:30 PM
- ✅ **Cloud-based** - runs on GitHub Actions (free)
- ✅ **No laptop required** - works 24/7
- ✅ **Checks all room types** (1, 2, and 3-bedroom)
- ✅ **Location filtering** - only shows properties in Muhaisnah Fourth

## How It Works

1. **GitHub Actions** runs the script daily at 5:30 PM
2. **Scrapes** the WASL website for apartment listings
3. **Filters** results to show only Muhaisnah Fourth properties
4. **Reports** findings in the GitHub Actions summary

## Setup Instructions

### 1. Create GitHub Repository
```bash
# Create a new repository on GitHub
# Then push this code to it
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/apartment-checker.git
git push -u origin main
```

### 2. Enable GitHub Actions
- Go to your repository on GitHub
- Click on "Actions" tab
- The workflow will automatically start running

### 3. View Results
- Check the "Actions" tab daily after 5:30 PM
- Click on the latest workflow run to see results
- You'll see a summary of available apartments

## Manual Trigger
You can also run the check manually:
- Go to "Actions" tab
- Click "Apartment Availability Checker"
- Click "Run workflow"

## Customization

To change the location or room types, edit `apartments.py`:
```python
LOCATION = "your-location-here"  # Change location
ROOM_TYPES = {1: "1-Bedroom", 2: "2-Bedroom", 3: "3-Bedroom"}  # Modify room types
```

## Current Results

The script checks for:
- **1-Bedroom apartments** in Muhaisnah Fourth
- **2-Bedroom apartments** in Muhaisnah Fourth  
- **3-Bedroom apartments** in Muhaisnah Fourth

## Files

- `apartments.py` - Main script that checks apartment availability
- `.github/workflows/apartment_checker.yml` - GitHub Actions workflow
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Cost

**Completely FREE!** GitHub Actions provides 2000 minutes/month for free, which is more than enough for daily checks. 