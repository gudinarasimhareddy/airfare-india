from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import random

router = APIRouter(prefix="/tourist-plans", tags=["Tourist Plans & Packages"])

TOURIST_PACKAGES = [
    {
        "id": "tour-goa-3d",
        "destination": "GOI",
        "city_name": "Goa (Sun, Sand & Portuguese Heritage)",
        "package_title": "Goa Coastal Escapade & Sunset Cruise",
        "duration": "3 Days / 2 Nights",
        "hero_image": "/assets/images/destination_mumbai.jpg",
        "tagline": "Golden beaches, UNESCO churches of Old Goa, and private Mandovi river cruise.",
        "flight": {
            "airline": "IndiGo",
            "flight_no": "6E 531",
            "type": "Non-Stop Return Flight Included",
            "baggage": "7kg Cabin + 15kg Checked Baggage Included",
            "seat_pitch": "30\" Standard Recline"
        },
        "hotel": {
            "name": "Radisson Resort & Spa Candolim",
            "rating": "4.5 / 5 ★★★★☆",
            "room_type": "Deluxe Pool-View Room",
            "amenities": ["Daily Buffet Breakfast", "Swimming Pool & Spa Access", "Free High-Speed Wi-Fi", "Welcome Drink"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Arrival, Latin Quarter & Sunset Cruise",
                "details": "Airport pickup in private AC sedan. Check-in and relax. Afternoon walking tour of colorful Fontainhas (Latin Quarter). Evening 1-hour Mandovi River sunset cruise with Goan folk music."
            },
            {
                "day": "Day 2",
                "title": "North Goa Beaches & 17th-Century Fort Aguada",
                "details": "Breakfast at resort. Visit 17th-century Fort Aguada & Sinquerim lighthouse. Afternoon beach leisure and water sports at Calangute/Baga. Candlelight seafood dinner at coastal shack."
            },
            {
                "day": "Day 3",
                "title": "Old Goa UNESCO Basilica & Departure",
                "details": "Buffet breakfast. Visit Basilica of Bom Jesus and Sé Cathedral in Old Goa. Souvenir shopping at Panaji municipal market. Private transfer back to Goa Airport for flight home."
            }
        ],
        "pricing": {
            "price_without_offers": 14500,
            "price_with_offers": 10999,
            "savings": 3501,
            "discount_pct": 24,
            "applied_promo": "AIRXTOUR",
            "promo_label": "Promo Code AIRXTOUR Applied (Flat ₹3,501 OFF)"
        },
        "inclusions": ["Return Flight Tickets", "4-Star Resort 2 Nights", "Daily Breakfast", "Airport Transfers", "Sunset Cruise & Sightseeing"],
        "exclusions": ["Personal water sports fees", "Lunch & Alcoholic beverages"]
    },
    {
        "id": "tour-jaipur-3d",
        "destination": "JAI",
        "city_name": "Jaipur (The Royal Pink City)",
        "package_title": "Royal Rajasthan Heritage & Fortresses",
        "duration": "3 Days / 2 Nights",
        "hero_image": "/assets/images/destination_delhi.jpg",
        "tagline": "Amber Fort mirror halls, Hawa Mahal, stepwells, and royal Rajasthani banquet.",
        "flight": {
            "airline": "Air India",
            "flight_no": "AI 491",
            "type": "Direct Return Flight Included",
            "baggage": "7kg Cabin + 20kg Checked Baggage Included",
            "seat_pitch": "32\" Extra Legroom + Free Hot Meals"
        },
        "hotel": {
            "name": "ITC Rajputana Luxury Collection",
            "rating": "4.8 / 5 ★★★★★",
            "room_type": "Heritage Royal Room",
            "amenities": ["Royal Rajasthani Thali Dinner", "Complimentary Breakfast", "Kaya Kalp Spa Voucher", "Courtyard Folk Music"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Pink City Palaces & Johari Bazaar",
                "details": "Airport pickup. Check-in at ITC Rajputana. Visit iconic Hawa Mahal in afternoon golden light and astronomical instruments at Jantar Mantar. Evening street shopping in Johari Bazaar."
            },
            {
                "day": "Day 2",
                "title": "Amber Fort Mirror Palace & Nahargarh Sunset",
                "details": "Ascent to majestic Amber Fort with Sheesh Mahal (Mirror Palace). Explore Panna Meena ka Kund geometric stepwell. Sunset tea at Nahargarh Fort overlooking pink city lights."
            },
            {
                "day": "Day 3",
                "title": "Block Printing Artisan Tour & Departure",
                "details": "Breakfast. Visit Sanganer hand-block printing workshop and blue pottery center. Visit Jal Mahal (Water Palace). Transfer to Jaipur Airport for return flight."
            }
        ],
        "pricing": {
            "price_without_offers": 13900,
            "price_with_offers": 9899,
            "savings": 4001,
            "discount_pct": 29,
            "applied_promo": "ROYALJAIPUR",
            "promo_label": "Promo Code ROYALJAIPUR Applied (Save ₹4,001)"
        },
        "inclusions": ["Return Flight Tickets", "5-Star Heritage Hotel", "Daily Breakfast & 1 Royal Dinner", "All Monument Entry Passes", "AC Chauffeur Transport"],
        "exclusions": ["Camera fees", "Personal shopping"]
    },
    {
        "id": "tour-mumbai-3d",
        "destination": "BOM",
        "city_name": "Mumbai (City of Dreams)",
        "package_title": "Colonial Heritage, Marine Drive & Elephanta",
        "duration": "3 Days / 2 Nights",
        "hero_image": "/assets/images/destination_mumbai.jpg",
        "tagline": "Gateway of India, Marine Drive sunset, rock-cut caves, and Bandra Sea Link.",
        "flight": {
            "airline": "Akasa Air",
            "flight_no": "QP 1102",
            "type": "Direct Morning Flight",
            "baggage": "7kg Cabin + 15kg Checked Baggage Included",
            "seat_pitch": "30.5\" Modern USB Power"
        },
        "hotel": {
            "name": "The Taj Mahal Tower / Trident Nariman Point",
            "rating": "4.7 / 5 ★★★★★",
            "room_type": "Sea-View Premier Room",
            "amenities": ["Harbor-View Breakfast", "Infinity Pool", "24hr Fitness Studio", "Complimentary High Tea"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Gateway of India & Queen's Necklace Walk",
                "details": "Arrival at BOM T2. Private AC transfer to South Mumbai hotel. Afternoon heritage walk through Fort and Kala Ghoda art precinct. Sunset stroll on Marine Drive followed by street dining at Chowpatty."
            },
            {
                "day": "Day 2",
                "title": "Elephanta Caves & Bandra-Worli Sea Link",
                "details": "Morning ferry from Gateway of India to 5th-century Elephanta Island rock-cut temple caves. Afternoon drive across Bandra-Worli Sea Link to Bandstand and seaside cafés."
            },
            {
                "day": "Day 3",
                "title": "Dharavi Artisans, Crawford Market & Departure",
                "details": "Breakfast. Visit Crawford Market and Dhobi Ghat. Irani chai & bun maska at Britannia & Co. Evening transfer to airport for departure."
            }
        ],
        "pricing": {
            "price_without_offers": 16200,
            "price_with_offers": 12499,
            "savings": 3701,
            "discount_pct": 23,
            "applied_promo": "MUMBAIFLY",
            "promo_label": "Promo Code MUMBAIFLY Applied (Save ₹3,701)"
        },
        "inclusions": ["Direct Flight Tickets", "5-Star Harbor-View Hotel", "Daily Breakfast", "Elephanta Ferry Tickets", "Private Airport Transfers"],
        "exclusions": ["Lunch and personal expenses"]
    },
    {
        "id": "tour-blr-3d",
        "destination": "BLR",
        "city_name": "Bengaluru (Garden City & Tech Capital)",
        "package_title": "Bengaluru Brewpubs, Palaces & Botanical Bliss",
        "duration": "3 Days / 2 Nights",
        "hero_image": "/assets/images/destination_delhi.jpg",
        "tagline": "Lalbagh Glass House, Bangalore Palace, authentic Benne Dosa, and Indiranagar craft beer.",
        "flight": {
            "airline": "IndiGo",
            "flight_no": "6E 404",
            "type": "Direct Flight",
            "baggage": "7kg Cabin + 15kg Checked Baggage Included",
            "seat_pitch": "30\" Value Pitch"
        },
        "hotel": {
            "name": "The Leela Palace Bengaluru",
            "rating": "4.9 / 5 ★★★★★",
            "room_type": "Royal Deluxe Garden Room",
            "amenities": ["Gourmet Breakfast", "Spa Steam & Sauna", "Welcome Silk Scarf", "Evening Classical Flute Concert"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Botanical Heritage & Legendary Benne Dosa",
                "details": "Arrival at BLR Airport. Chauffeur pickup to hotel. Morning walk at Lalbagh Botanical Garden and Glass House. Authentic Benne Dosa and filter kaapi at Vidyarthi Bhavan. Tour of Bangalore Palace."
            },
            {
                "day": "Day 2",
                "title": "Science, Art & Craft Beer Tasting Tour",
                "details": "Breakfast. Visvesvaraya Industrial & Technological Museum and Cubbon Park trails. Evening craft beer & sourdough pizza crawl in Indiranagar & Koramangala microbreweries (Toit / Windmills)."
            },
            {
                "day": "Day 3",
                "title": "Spiritual Shrines & Departure",
                "details": "Breakfast. Visit ISKCON Temple and Bull Temple Basavanagudi. Handicraft shopping at Cauvery Arts Emporium. Private AC transfer back to Kempegowda Airport."
            }
        ],
        "pricing": {
            "price_without_offers": 15800,
            "price_with_offers": 11950,
            "savings": 3850,
            "discount_pct": 24,
            "applied_promo": "BLRSAVINGS",
            "promo_label": "Promo Code BLRSAVINGS Applied (Save ₹3,850)"
        },
        "inclusions": ["Direct Flight Tickets", "Luxury Palace Hotel 2 Nights", "Daily Breakfast", "Sightseeing Cab", "Airport Transfers"],
        "exclusions": ["Brewery drink tabs", "Personal tips"]
    },
    {
        "id": "tour-delhi-3d",
        "destination": "DEL",
        "city_name": "Delhi (Capital Heritage & Culinary Trail)",
        "package_title": "Grand Monuments, Mughal Flavors & Dilli Haat",
        "duration": "3 Days / 2 Nights",
        "hero_image": "/assets/images/hero_aviation.jpg",
        "tagline": "Red Fort, Qutub Minar, Chandni Chowk street feast, and India Gate evening stroll.",
        "flight": {
            "airline": "Air India Express",
            "flight_no": "IX 144",
            "type": "Direct Flight",
            "baggage": "7kg Cabin + 15kg Checked Baggage Included",
            "seat_pitch": "30\" Pitch"
        },
        "hotel": {
            "name": "The Claridges New Delhi",
            "rating": "4.7 / 5 ★★★★★",
            "room_type": "Heritage Heritage Room",
            "amenities": ["Buffet Breakfast", "Lutyens Garden Access", "Pick-and-Drop Luxury Cab", "Evening High Tea"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Old Delhi Culinary Trail & Red Fort",
                "details": "Morning arrival at IGI Airport. Check-in at The Claridges. Cycle rickshaw food safari in Chandni Chowk, Paranthe Wali Gali, and Karim's kebabs. Visit UNESCO Red Fort and Jama Masjid."
            },
            {
                "day": "Day 2",
                "title": "Qutub Minar, Humayun's Tomb & India Gate",
                "details": "Breakfast. Visit soaring Qutub Minar and Humayun's Tomb gardens. Sunset walk along Kartavya Path and illuminated India Gate memorial."
            },
            {
                "day": "Day 3",
                "title": "Akshardham Temple & Dilli Haat Crafts",
                "details": "Breakfast. Visit peaceful Akshardham temple complex and cultural boat ride. Artisanal crafts shopping at Dilli Haat INA. Transfer to Airport for return flight."
            }
        ],
        "pricing": {
            "price_without_offers": 14900,
            "price_with_offers": 11200,
            "savings": 3700,
            "discount_pct": 25,
            "applied_promo": "DELHIESCAPE",
            "promo_label": "Promo Code DELHIESCAPE Applied (Save ₹3,700)"
        },
        "inclusions": ["Return Flight Tickets", "5-Star Heritage Hotel", "Daily Breakfast", "Chauffeur AC Cab", "Monument Entry"],
        "exclusions": ["Personal meals outside hotel"]
    },
    {
        "id": "tour-kolkata-3d",
        "destination": "CCU",
        "city_name": "Kolkata (The City of Joy & Classical Arts)",
        "package_title": "Victoria Memorial, Hooghly Ferry & Sweet Delights",
        "duration": "3 Days / 2 Nights",
        "hero_image": "/assets/images/destination_mumbai.jpg",
        "tagline": "Howrah Bridge, Victoria Memorial, clay artisans of Kumartuli, and authentic Mishti Doi.",
        "flight": {
            "airline": "SpiceJet",
            "flight_no": "SG 822",
            "type": "Direct Return Flight",
            "baggage": "7kg Cabin + 15kg Checked Baggage Included",
            "seat_pitch": "29.5\" Pitch"
        },
        "hotel": {
            "name": "The Oberoi Grand Kolkata",
            "rating": "4.8 / 5 ★★★★★",
            "room_type": "Classic Heritage Room",
            "amenities": ["Gourmet Breakfast", "Colonial Courtyard Pool", "Traditional Bengali High Tea", "Spa Credit"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "White Marble Majesty & Sunset Ferry",
                "details": "Airport pickup. Check-in at Grand Dame Oberoi. Tour Victoria Memorial and gardens. Authentic Bengali lunch at 6 Ballygunge Place. Sunset ferry on the Hooghly overlooking Howrah Bridge."
            },
            {
                "day": "Day 2",
                "title": "Potters' Colony, College Street & Park Street Jazz",
                "details": "Breakfast. Visit Kumartuli idol-sculpting lanes. Coffee and intellectual discussions at Indian Coffee House, College Street. Evening dinner and live jazz music on Park Street (Peter Cat Chelo Kebab)."
            },
            {
                "day": "Day 3",
                "title": "Dakshineswar Temple, Sweets & Departure",
                "details": "Breakfast. Visit Dakshineswar Kali Temple & boat to Belur Math. Authentic sweet sampling (KC Das Sandesh & Mishti Doi). Transfer to Netaji Subhash Airport."
            }
        ],
        "pricing": {
            "price_without_offers": 13800,
            "price_with_offers": 10250,
            "savings": 3550,
            "discount_pct": 26,
            "applied_promo": "KOLKATADEAL",
            "promo_label": "Promo Code KOLKATADEAL Applied (Save ₹3,550)"
        },
        "inclusions": ["Return Flights", "5-Star Oberoi Hotel 2 Nights", "Daily Breakfast", "AC Private Transport", "Hooghly Ferry Passes"],
        "exclusions": ["Personal meals & shopping"]
    },
    {
        "id": "tour-kerala-4d",
        "destination": "COK",
        "city_name": "Kerala (God's Own Country & Backwaters)",
        "package_title": "Kerala Backwaters, Houseboat & Tea Gardens",
        "duration": "4 Days / 3 Nights",
        "hero_image": "/assets/images/destination_mumbai.jpg",
        "tagline": "Alleppey luxury houseboat cruise, Munnar misty tea estates, and authentic Ayurvedic wellness.",
        "flight": {
            "airline": "IndiGo",
            "flight_no": "6E 561",
            "type": "Direct Return Flight Included",
            "baggage": "7kg Cabin + 15kg Checked Baggage Included",
            "seat_pitch": "30\" Value Pitch"
        },
        "hotel": {
            "name": "Kumarakom Lake Resort & Munnar Fragrant Nature",
            "rating": "4.9 / 5 ★★★★★",
            "room_type": "Meandering Pool Heritage Villa",
            "amenities": ["Daily Buffet Breakfast & Dinner", "1-Night AC Houseboat Stay", "Ayurvedic Massage Session", "Spice Plantation Tour"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Cochin Arrival & Drive to Munnar Tea Hills",
                "details": "Arrival at Kochi Airport (COK). Scenic drive past Cheeyappara Waterfalls to Munnar tea plantations. Evening stroll through spice markets."
            },
            {
                "day": "Day 2",
                "title": "Eravikulam National Park & Mattupetty Dam",
                "details": "Breakfast. Visit Eravikulam National Park (home to Nilgiri Tahr) and Tata Tea Museum. Boat ride at Mattupetty Lake."
            },
            {
                "day": "Day 3",
                "title": "Alleppey Backwaters Houseboat Cruise",
                "details": "Drive to Alleppey. Board traditional Kerala houseboat. Cruise along palm-fringed canals with freshly prepared Karimeen fish lunch."
            },
            {
                "day": "Day 4",
                "title": "Fort Kochi Chinese Fishing Nets & Departure",
                "details": "Morning checkout. Tour historic Fort Kochi and Chinese fishing nets. Private transfer to Cochin International Airport."
            }
        ],
        "pricing": {
            "price_without_offers": 18500,
            "price_with_offers": 13999,
            "savings": 4501,
            "discount_pct": 24,
            "applied_promo": "KERALAFLY",
            "promo_label": "Promo Code KERALAFLY Applied (Save ₹4,501)"
        },
        "inclusions": ["Return Flight Tickets", "Houseboat + Luxury Resort", "All Meals on Houseboat", "Chauffeur Transport", "Spice Tour"],
        "exclusions": ["Personal Ayurvedic treatments outside package"]
    },
    {
        "id": "tour-kashmir-4d",
        "destination": "SXR",
        "city_name": "Kashmir (Paradise on Earth)",
        "package_title": "Dal Lake Shikara, Mughal Gardens & Gulmarg Gondola",
        "duration": "4 Days / 3 Nights",
        "hero_image": "/assets/images/hero_aviation.jpg",
        "tagline": "Stay in luxury Dal Lake houseboat, ride the Gulmarg Gondola, and savor traditional Wazwan.",
        "flight": {
            "airline": "Air India",
            "flight_no": "AI 825",
            "type": "Direct Return Flight",
            "baggage": "7kg Cabin + 20kg Checked Baggage Included",
            "seat_pitch": "32\" Hot Meals Included"
        },
        "hotel": {
            "name": "Mascot Houseboats Dal Lake & The Khyber Gulmarg",
            "rating": "4.9 / 5 ★★★★★",
            "room_type": "Cedar Wood Suite & Pine View Room",
            "amenities": ["Daily Kashmiri Breakfast & Wazwan", "Private Shikara Ride", "Heated Rooms", "Traditional Kehwa Welcome"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Srinagar Arrival & Romantic Shikara Ride",
                "details": "Arrival at Sheikh ul-Alam Airport (SXR). Check-in to luxury houseboat on Dal Lake. Sunset Shikara ride across floating lotus gardens and Char Chinar."
            },
            {
                "day": "Day 2",
                "title": "Gulmarg Snow Peaks & Gondola Ride",
                "details": "Drive to snow-clad Gulmarg. Ride Phase 1 & 2 Gondola up to Apharwat Peak (13,780 ft). Skiing and snow activities. Return to Srinagar."
            },
            {
                "day": "Day 3",
                "title": "Mughal Gardens & Old City Saffron Bazaar",
                "details": "Tour Shalimar Bagh, Nishat Bagh, and Chashme Shahi terraced gardens. Saffron and Pashmina shopping in Lal Chowk."
            },
            {
                "day": "Day 4",
                "title": "Pari Mahal Panorama & Airport Drop",
                "details": "Morning visit to Pari Mahal overlooking Dal Lake. Authentic Kehwa tea and dry fruits sampling. Transfer to Srinagar Airport."
            }
        ],
        "pricing": {
            "price_without_offers": 21500,
            "price_with_offers": 16499,
            "savings": 5001,
            "discount_pct": 23,
            "applied_promo": "KASHMIRPARADISE",
            "promo_label": "Promo Code KASHMIRPARADISE Applied (Save ₹5,001)"
        },
        "inclusions": ["Return Flights", "Dal Lake Houseboat + Hotel", "Daily Breakfast & Dinner", "Shikara Ride", "All Tolls & AC Cab"],
        "exclusions": ["Gondola Phase 2 ticket", "Pony rides"]
    },
    {
        "id": "tour-manali-4d",
        "destination": "IXC",
        "city_name": "Manali (Himalayan Adventure & Pine Valleys)",
        "package_title": "Solang Adventure, Rohtang Pass & Old Manali Cafes",
        "duration": "4 Days / 3 Nights",
        "hero_image": "/assets/images/destination_delhi.jpg",
        "tagline": "Solang paragliding, snow vistas at Atal Tunnel, apple orchards, and live acoustic music.",
        "flight": {
            "airline": "Alliance Air",
            "flight_no": "9I 803",
            "type": "Direct Return Flight to Chandigarh/Kullu",
            "baggage": "7kg Cabin + 15kg Checked Baggage Included",
            "seat_pitch": "30\" Legroom"
        },
        "hotel": {
            "name": "The Himalayan Castle & Spa Manali",
            "rating": "4.8 / 5 ★★★★★",
            "room_type": "Victorian Mountain View Suite",
            "amenities": ["Daily Mountain Breakfast", "Bonfire Evening with Guitarist", "Apple Cider Welcome Drink", "Spa Credit"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Chandigarh Landing & Scenic Beas River Drive",
                "details": "Flight arrival at IXC. Scenic private cab drive through Mandi and Kullu along Beas River. Check-in at Victorian castle resort in Manali."
            },
            {
                "day": "Day 2",
                "title": "Solang Valley Paragliding & Atal Tunnel Sissu",
                "details": "Thrilling adventure day in Solang Valley (paragliding & quad biking). Drive through engineering marvel Atal Tunnel to Lahaul valley (Sissu waterfall)."
            },
            {
                "day": "Day 3",
                "title": "Hadimba Temple, Jogini Falls & Old Manali Cafes",
                "details": "Morning walk to 16th-century cedar Hadimba Temple and hike to Jogini Waterfall. Evening café hopping in bohemian Old Manali."
            },
            {
                "day": "Day 4",
                "title": "Naggar Castle & Return Flight",
                "details": "Visit historic Naggar Castle and Roerich Art Gallery. Return drive to Chandigarh Airport for flight back."
            }
        ],
        "pricing": {
            "price_without_offers": 17200,
            "price_with_offers": 12850,
            "savings": 4350,
            "discount_pct": 25,
            "applied_promo": "HIMALAYAN",
            "promo_label": "Promo Code HIMALAYAN Applied (Save ₹4,350)"
        },
        "inclusions": ["Return Flight Tickets", "Luxury Resort 3 Nights", "Daily Breakfast & Dinner", "AC Innova Chauffeur", "Solang Excursion"],
        "exclusions": ["Paragliding equipment fees", "Rohtang special permit"]
    },
    {
        "id": "tour-andaman-4d",
        "destination": "IXZ",
        "city_name": "Andaman & Nicobar Islands (Tropical Emerald Coast)",
        "package_title": "Havelock Radhanagar Beach, Scuba & Cellular Jail",
        "duration": "4 Days / 3 Nights",
        "hero_image": "/assets/images/destination_mumbai.jpg",
        "tagline": "Asia's best Radhanagar Beach, crystal clear scuba diving at Elephant Beach, and Cellular Jail sound & light show.",
        "flight": {
            "airline": "IndiGo",
            "flight_no": "6E 292",
            "type": "Direct Return Flight Included",
            "baggage": "7kg Cabin + 15kg Checked Baggage Included",
            "seat_pitch": "30\" Standard Pitch"
        },
        "hotel": {
            "name": "Taj Exotica Resort & Symphony Palms Beach Resort",
            "rating": "4.9 / 5 ★★★★★",
            "room_type": "Beachfront Villa",
            "amenities": ["Gourmet Island Breakfast", "Makruzz Catamaran Cruise Ferry", "Private Beach Access", "Snorkeling Voucher"]
        },
        "itinerary": [
            {
                "day": "Day 1",
                "title": "Port Blair Arrival & Cellular Jail Memorial",
                "details": "Arrival at Veer Savarkar Airport (IXZ). Check-in and relax. Visit National Memorial Cellular Jail. Evening moving Sound & Light history show."
            },
            {
                "day": "Day 2",
                "title": "Premium Catamaran to Havelock & Radhanagar Sunset",
                "details": "High-speed Makruzz catamaran cruise to Havelock Island (Swaraj Dweep). Afternoon relaxation and breathtaking sunset at world-famous Radhanagar Beach (Beach No. 7)."
            },
            {
                "day": "Day 3",
                "title": "Elephant Beach Coral Reef Snorkeling & Scuba",
                "details": "Speedboat to Elephant Beach for vibrant coral reef snorkeling and scuba diving with certified PADI instructors. Afternoon kayak in mangroves."
            },
            {
                "day": "Day 4",
                "title": "Corbyn's Cove Beach & Departure",
                "details": "Morning ferry back to Port Blair. Quick coconut water stop at palm-lined Corbyn's Cove. Transfer to Port Blair Airport."
            }
        ],
        "pricing": {
            "price_without_offers": 24800,
            "price_with_offers": 18900,
            "savings": 5900,
            "discount_pct": 24,
            "applied_promo": "ISLANDANDAMAN",
            "promo_label": "Promo Code ISLANDANDAMAN Applied (Save ₹5,900)"
        },
        "inclusions": ["Return Flight Tickets", "Beachfront Resorts 3 Nights", "Daily Buffet Breakfast", "Makruzz High-Speed Ferry", "Airport & Jetty Transfers"],
        "exclusions": ["Scuba diving video package", "Personal watercraft rental"]
    }
]

def _normalize_plan(p: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(p)
    item["title"] = p.get("package_title", p.get("title", "Holiday Package"))
    item["image_url"] = p.get("hero_image", p.get("image_url", "/assets/images/destination_mumbai.jpg"))
    item["destination"] = p.get("destination", "DEL")
    
    # Normalize flight
    flight = dict(p.get("flight", {}))
    if "carrier" not in flight:
        flight["carrier"] = flight.get("airline", "IndiGo")
    if "sector" not in flight:
        flight["sector"] = f"{flight.get('type', 'Return Flights')} ({flight.get('flight_no', '')})"
    item["flight"] = flight

    # Normalize hotel rating
    hotel = dict(p.get("hotel", {}))
    if isinstance(hotel.get("rating"), str):
        try:
            hotel["rating_num"] = float(hotel["rating"].split("/")[0].strip())
        except Exception:
            hotel["rating_num"] = 4.5
    item["hotel"] = hotel
    return item

class BookTouristPlanRequest(BaseModel):
    plan_id: str
    traveler_name: Optional[str] = None
    passenger_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    contact: Optional[str] = None
    travel_date: str
    passengers_count: Optional[int] = 1
    pax_count: Optional[int] = 1
    promo_code: Optional[str] = None
    payment_order_id: Optional[str] = None
    payment_id: Optional[str] = None

@router.get("")
def list_tourist_plans(destination: Optional[str] = Query(None, description="Filter by airport destination code")):
    """List all tourist travel packages with flight tickets, hotels, itineraries, and side-by-side offer prices."""
    normalized = [_normalize_plan(p) for p in TOURIST_PACKAGES]
    if destination:
        dest_upper = destination.upper().strip()
        filtered = [
            p for p in normalized 
            if p["destination"] == dest_upper or dest_upper in p.get("city_name", "").upper()
        ]
        return {"total": len(filtered), "plans": filtered, "packages": filtered}
    return {"total": len(normalized), "plans": normalized, "packages": normalized}

@router.get("/{plan_id}")
def get_tourist_plan(plan_id: str):
    """Retrieve detailed tourist package specification."""
    plan = next((p for p in TOURIST_PACKAGES if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Tourist package '{plan_id}' not found.")
    return _normalize_plan(plan)

@router.post("/calculate-quote")
def calculate_plan_quote(req: BookTouristPlanRequest):
    """Calculates authoritative server-side price breakdown for package booking."""
    plan = next((p for p in TOURIST_PACKAGES if p["id"] == req.plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Tourist package '{req.plan_id}' not found.")
    pax = max(1, min(req.pax_count or req.passengers_count or 1, 9))
    base_unit = plan["pricing"]["price_without_offers"]
    offer_unit = plan["pricing"]["price_with_offers"]
    package_savings_unit = plan["pricing"]["savings"]
    base_total = base_unit * pax
    discount = package_savings_unit * pax
    promo_applied = plan["pricing"].get("applied_promo", "OFFER_RATE")

    if req.promo_code:
        code = req.promo_code.upper().strip()
        if code == "AIRX500":
            discount += 500
            promo_applied += " + AIRX500"
        elif code == "FESTIVE1000":
            discount += 1000
            promo_applied += " + FESTIVE1000"
        elif code == "STUDENT":
            discount += 600
            promo_applied += " + STUDENT"

    final_payable = max(100, base_total - discount)
    return {
        "plan_id": plan["id"],
        "plan_title": plan.get("package_title") or plan.get("title"),
        "city_name": plan["city_name"],
        "pax_count": pax,
        "base_total": base_total,
        "package_offer_total": offer_unit * pax,
        "discount": discount,
        "promo_applied": promo_applied,
        "final_payable": final_payable,
        "currency": "INR",
        "inclusions": plan["inclusions"]
    }

@router.post("/book")
def book_tourist_plan(req: BookTouristPlanRequest):
    """
    Enforces that a tourist package booking MUST have a verified payment before confirmation.
    Unverified or unpaid requests are rejected with HTTP 402.
    """
    plan = next((p for p in TOURIST_PACKAGES if p["id"] == req.plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Tourist package '{req.plan_id}' not found.")

    if not req.payment_order_id:
        raise HTTPException(
            status_code=402,
            detail="Payment Required: Unpaid bookings cannot be confirmed. Please create a payment order via POST /api/v1/payments/create-order and complete verification at /api/v1/payments/verify."
        )

    # Verify that the payment order exists and is verified/captured in SQLite DB
    from backend.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM payments WHERE order_id = ? AND status IN ('SUCCESS', 'CAPTURED')",
        (req.payment_order_id,)
    )
    payment_row = cursor.fetchone()
    
    if not payment_row:
        conn.close()
        raise HTTPException(
            status_code=402,
            detail=f"Payment for order '{req.payment_order_id}' has not been completed or verified."
        )
    
    # Retrieve confirmed booking
    cursor.execute("SELECT * FROM bookings WHERE payment_order_id = ?", (req.payment_order_id,))
    booking_row = cursor.fetchone()
    conn.close()

    if booking_row:
        b = dict(booking_row)
        return {
            "status": "confirmed",
            "booking_reference": b.get("pnr") or b["booking_id"],
            "booking_id": b["booking_id"],
            "plan_title": plan.get("package_title") or plan.get("title"),
            "destination": plan["city_name"],
            "traveler_name": b.get("traveler_name"),
            "travel_date": b.get("travel_date"),
            "pax_count": b.get("pax_count"),
            "amount_paid": b.get("amount"),
            "payment_id": b.get("payment_id"),
            "payment_order_id": b.get("payment_order_id"),
            "message": f"Booking confirmed for {b.get('traveler_name')} under PNR {b.get('pnr')}."
        }
    
    raise HTTPException(status_code=404, detail="Associated booking record not found.")


