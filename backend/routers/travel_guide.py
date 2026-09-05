from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/travel-guide", tags=["Travel Guide & Passenger Rules"])

DESTINATIONS_DATA = {
    "DEL": {
        "code": "DEL",
        "name": "Delhi (National Capital Region)",
        "airport": "Indira Gandhi International Airport (DEL)",
        "tagline": "The Historic & Political Heart of India",
        "best_time_to_visit": "October to March (12°C – 24°C, pleasant weather)",
        "flight_cost_benchmark": "₹3,900 – ₹5,400",
        "recommended_days": "3 to 4 Days",
        "airport_transit": {
            "metro": "Delhi Metro Airport Express connects T3/T2 to New Delhi Railway Station in 19 minutes (₹60).",
            "cabs": "Prepaid Uber, Ola, and BluSmart EV pickup hubs at multi-level parking (₹400–₹750 to central Delhi).",
            "buses": "DTC Delhi Airport Express electric AC buses run 24x7 to ISBT Kashmiri Gate and Connaught Place."
        },
        "itinerary_3d": [
            {
                "day": "Day 1: Mughal Heritage & Old Delhi Soul",
                "activities": [
                    "Morning: Explore Red Fort (Lal Qila) and take a rickshaw ride through vibrant Chandni Chowk.",
                    "Afternoon: Savor authentic kebabs & parathas at Karim's and Paranthe Wali Gali, visit Jama Masjid.",
                    "Evening: Sunset stroll at India Gate and Kartavya Path with illuminated war memorials."
                ]
            },
            {
                "day": "Day 2: Architectural Wonders & Craft Bazars",
                "activities": [
                    "Morning: Marvel at the soaring 73m Qutub Minar and iron pillar.",
                    "Afternoon: Visit Humayun's Tomb (UNESCO world heritage precursor to the Taj Mahal) and Lotus Temple.",
                    "Evening: Open-air artisanal shopping and state cuisine dining at Dilli Haat INA."
                ]
            },
            {
                "day": "Day 3: Modern Culture, Spiritual Grandeur & Shopping",
                "activities": [
                    "Morning: Experience serenity and boat ride at the monumental Swaminarayan Akshardham Temple.",
                    "Afternoon: Colonial architecture, café culture, and bookstores at Connaught Place.",
                    "Evening: Hauz Khas Village lakeside sunset, art galleries, and dinner overlooking the historic reservoir."
                ]
            }
        ],
        "top_attractions": ["Red Fort", "Qutub Minar", "Humayun's Tomb", "Akshardham", "India Gate", "Chandni Chowk", "Lotus Temple"],
        "local_foods": ["Chole Bhature", "Old Delhi Nihari", "Butter Chicken (Moti Mahal)", "Gol Gappe", "Daulat ki Chaat"]
    },
    "BOM": {
        "code": "BOM",
        "name": "Mumbai (Maharashtra)",
        "airport": "Chhatrapati Shivaji Maharaj International Airport (BOM)",
        "tagline": "The City of Dreams & Coastal Financial Capital",
        "best_time_to_visit": "November to February (22°C – 30°C, cooler coastal breeze)",
        "flight_cost_benchmark": "₹3,800 – ₹5,100",
        "recommended_days": "3 to 5 Days",
        "airport_transit": {
            "metro": "Mumbai Metro Line 3 (Aqua Line) connects T2 to BKC and South Mumbai.",
            "cabs": "Black-and-yellow metered taxis and app-based Uber/Ola from dedicated T2/T1 zones (₹500–₹850 to South Bombay).",
            "auto": "Auto-rickshaws available from Terminal 1 (Domestic) for western suburbs."
        },
        "itinerary_3d": [
            {
                "day": "Day 1: Colonial Grandeur & Marine Drive Sunset",
                "activities": [
                    "Morning: Gateway of India and harbor views, breakfast at the historic Leopold Café.",
                    "Afternoon: Chhatrapati Shivaji Maharaj Vastu Sangrahalaya (CSMVS Museum) and Fort heritage precinct.",
                    "Evening: Queen's Necklace walk along Marine Drive and sunset at Girgaon Chowpatty with Pav Bhaji."
                ]
            },
            {
                "day": "Day 2: Coastal Monoliths & Bollywood Vibe",
                "activities": [
                    "Morning: Ferry ride from Gateway of India to 5th-century rock-cut Elephanta Caves.",
                    "Afternoon: Visit Haji Ali Dargah situated on an islet in the Arabian Sea.",
                    "Evening: Bandra Bandstand, Bandra-Worli Sea Link scenic drive, and sea-facing dinner."
                ]
            },
            {
                "day": "Day 3: Markets, Street Food & Art Districts",
                "activities": [
                    "Morning: Crawford Market and Sassoon Docks lively morning buzz.",
                    "Afternoon: Art galleries at Kala Ghoda and Irani chai with bun maska at Britannia & Co.",
                    "Evening: Juhu Beach street food festival and nightlife in Lower Parel."
                ]
            }
        ],
        "top_attractions": ["Gateway of India", "Marine Drive", "Elephanta Caves", "Bandra-Worli Sea Link", "Chhatrapati Shivaji Terminus", "Kala Ghoda"],
        "local_foods": ["Vada Pav", "Pav Bhaji", "Bombay Duck fry", "Bhel Puri", "Irani Chai & Bun Maska", "Kulfi Falooda"]
    },
    "BLR": {
        "code": "BLR",
        "name": "Bengaluru (Karnataka)",
        "airport": "Kempegowda International Airport (BLR)",
        "tagline": "India's Silicon Valley & Garden City",
        "best_time_to_visit": "September to March (18°C – 28°C, year-round moderate climate)",
        "flight_cost_benchmark": "₹4,200 – ₹5,600",
        "recommended_days": "3 to 4 Days",
        "airport_transit": {
            "bus": "BMTC Vayu Vajra Volvo AC luxury buses (KIAS series) run 24/7 across city routes (₹250–₹350).",
            "cabs": "Dedicated Uber/Ola zones and KSTDC prepaid airport cabs (₹900–₹1,400 to city center).",
            "train": "Suburban MEMU train services connect KIA halt station to Bangalore City (SBC)."
        },
        "itinerary_3d": [
            {
                "day": "Day 1: Heritage Gardens & Palace Architecture",
                "activities": [
                    "Morning: Morning walk amidst rare tropical trees at Lalbagh Botanical Garden and Glass House.",
                    "Afternoon: Authentic South Indian filter coffee and Benne Dosa at Vidyarthi Bhavan or CTR.",
                    "Evening: Tour Bangalore Palace and take in the neo-Dravidian architecture of Vidhana Soudha."
                ]
            },
            {
                "day": "Day 2: Tech Culture, Brewpubs & Craft Beer",
                "activities": [
                    "Morning: Science and space wonders at Visvesvaraya Museum and Cubbon Park shaded trails.",
                    "Afternoon: Art gallery visits at National Gallery of Modern Art (NGMA).",
                    "Evening: World-famous microbreweries in Indiranagar and Koramangala (Toit, Windmills Craftworks)."
                ]
            },
            {
                "day": "Day 3: Spiritual Enclaves & Art Bazars",
                "activities": [
                    "Morning: ISKCON Temple Rajajinagar and Bull Temple in Basavanagudi.",
                    "Afternoon: Commercial Street shopping and handicrafts at Cauvery Emporium.",
                    "Evening: Sunset dining in Whitefield or rooftop lounges in UB City."
                ]
            }
        ],
        "top_attractions": ["Lalbagh Botanical Garden", "Cubbon Park", "Bangalore Palace", "Vidhana Soudha", "UB City", "Indiranagar 100ft Rd"],
        "local_foods": ["Benne Masala Dosa", "Filter Coffee", "Bisi Bele Bath", "Mangalore Ghee Roast", "Craft Beer", "Mysore Pak"]
    },
    "GOI": {
        "code": "GOI",
        "name": "Goa (Dabolim & Mopa)",
        "airport": "Goa Dabolim Airport (GOI) / Manohar International Mopa (GOX)",
        "tagline": "Sun-Kissed Beaches, Portuguese Baroque & Coastal Bliss",
        "best_time_to_visit": "October to April (24°C – 32°C, lively beach shacks & water sports)",
        "flight_cost_benchmark": "₹3,400 – ₹5,800",
        "recommended_days": "4 to 6 Days",
        "airport_transit": {
            "cabs": "GoaMiles official taxi app and prepaid airport counter (₹1,000–₹1,800 depending on North/South Goa).",
            "bus": "Kadamba Transport Corporation electric AC buses connect Mopa/Dabolim to Panaji, Calangute, and Margao (₹150–₹250).",
            "rentals": "Self-drive cars and scooters available for pickup outside arrival terminal."
        },
        "itinerary_3d": [
            {
                "day": "Day 1: Portuguese Latin Quarter & Sunset Cruise",
                "activities": [
                    "Morning: Arrive and check-in. Stroll through brightly colored villas of Fontainhas (Panaji Latin Quarter).",
                    "Afternoon: UNESCO-listed Basilica of Bom Jesus and Sé Cathedral in Old Goa.",
                    "Evening: Mandovi River sunset cruise or seafood dinner at Fisherman's Wharf."
                ]
            },
            {
                "day": "Day 2: Coastal Vibrancy & Fort Vistas",
                "activities": [
                    "Morning: Panoramic Arabian Sea views at 17th-century Fort Aguada and Sinquerim Beach.",
                    "Afternoon: Water sports (parasailing, jet-ski) at Calangute and Baga beaches.",
                    "Evening: Sunset vibes and live acoustic music at beach clubs in Anjuna or Vagator."
                ]
            },
            {
                "day": "Day 3: Serene South Goa Sands & Spice Plantation",
                "activities": [
                    "Morning: Guided tour, traditional Goan buffet, and elephant sighting at Sahakari Spice Farm.",
                    "Afternoon: Pristine white sands and peaceful turquoise waters of Palolem and Agonda Beach.",
                    "Evening: Candlelight beach shack dinner enjoying fresh Goan Fish Curry and Bebinca."
                ]
            }
        ],
        "top_attractions": ["Basilica of Bom Jesus", "Fort Aguada", "Palolem Beach", "Fontainhas", "Dudhsagar Falls", "Anjuna Flea Market"],
        "local_foods": ["Goan Fish Curry Rice", "Pork Vindaloo / Chicken Xacuti", "Bebinca", "Prawn Balchão", "Feni Cocktail"]
    },
    "HYD": {
        "code": "HYD",
        "name": "Hyderabad (Telangana)",
        "airport": "Rajiv Gandhi International Airport (HYD)",
        "tagline": "City of Pearls, Nizami Grandeur & Biryani Royalty",
        "best_time_to_visit": "October to March (15°C – 28°C)",
        "flight_cost_benchmark": "₹3,600 – ₹4,800",
        "recommended_days": "3 to 4 Days",
        "airport_transit": {
            "bus": "Pushpak Airport Liner AC luxury buses connect HYD airport to Secunderabad, Gachibowli, and Hitech City 24x7 (₹200–₹300).",
            "cabs": "Dedicated Uber, Ola, and Meru airport zones (₹600–₹1,100 to central city/cyberabad)."
        },
        "itinerary_3d": [
            {
                "day": "Day 1: Nizami Palaces & The Majestic Charminar",
                "activities": [
                    "Morning: Charminar monument, climb the spiral staircase and browse the bustling Laad Bazaar for pearl bangles.",
                    "Afternoon: Royal splendor of Chowmahalla Palace and lunch of authentic Hyderabadi Dum Biryani at Shadab or Paradise.",
                    "Evening: Sunset walk around Hussain Sagar Lake and Buddha Statue with illuminated Lumbini Park laser show."
                ]
            },
            {
                "day": "Day 2: Acoustic Marvels & Royal Tombs",
                "activities": [
                    "Morning: Explore the 11km acoustic fort fortress of Golconda Fort (clap sound travels 1km to the citadel).",
                    "Afternoon: Qutb Shahi Tombs heritage park with restored domes.",
                    "Evening: Irani Chai with Osmania biscuits at Nimrah Café overlooking Charminar."
                ]
            },
            {
                "day": "Day 3: Cinema Royalty & High-Tech Hubs",
                "activities": [
                    "Morning: Full-day cinematic excursion to Ramoji Film City (World's largest film studio complex).",
                    "Evening: Modern upscale dining in Jubilee Hills and Durgam Cheruvu cable-stayed bridge view."
                ]
            }
        ],
        "top_attractions": ["Charminar", "Golconda Fort", "Chowmahalla Palace", "Ramoji Film City", "Hussain Sagar Lake", "Salar Jung Museum"],
        "local_foods": ["Hyderabadi Dum Biryani", "Mirchi ka Salan", "Double ka Meetha", "Haleem (seasonal)", "Irani Chai & Osmania Biscuits"]
    },
    "CCU": {
        "code": "CCU",
        "name": "Kolkata (West Bengal)",
        "airport": "Netaji Subhash Chandra Bose International Airport (CCU)",
        "tagline": "The City of Joy, Literary Capital & Colonial Charm",
        "best_time_to_visit": "October to March (14°C – 27°C, Festive Durga Puja season)",
        "flight_cost_benchmark": "₹4,100 – ₹5,400",
        "recommended_days": "3 to 4 Days",
        "airport_transit": {
            "metro": "Kolkata Metro Line 6 (Orange Line) connection under expansion to airport.",
            "cabs": "Prepaid Yellow Taxis and app-based Uber/Ola counters (₹350–₹600 to Park Street / Esplanade).",
            "bus": "WBTC AC Volvo buses to Howrah, Garia, and Esplanade (₹80–₹120)."
        },
        "itinerary_3d": [
            {
                "day": "Day 1: Colonial Grandeur & Sunset Over the Hooghly",
                "activities": [
                    "Morning: White marble majesty of Victoria Memorial and gardens.",
                    "Afternoon: St. Paul's Cathedral and iconic Bengali lunch at 6 Ballygunge Place (Kolkata fish fry & Chingri Malai Curry).",
                    "Evening: Sunset ferry ride across Hooghly River overlooking the engineering wonder Howrah Bridge."
                ]
            },
            {
                "day": "Day 2: Literature, Coffeehouse Intellect & Potters",
                "activities": [
                    "Morning: Historic College Street (Boi Para), coffee and debates at the legendary Indian Coffee House.",
                    "Afternoon: Clay idol making artisans at Kumartuli workshop lanes.",
                    "Evening: Stroll along Park Street with live jazz music and dinner at Peter Cat (famous Chelo Kebab)."
                ]
            },
            {
                "day": "Day 3: Spiritual Enclaves & Sweet Indulgence",
                "activities": [
                    "Morning: Dakshineswar Kali Temple and peaceful boat ride across to Belur Math (Ramakrishna Mission HQ).",
                    "Afternoon: Science City exploration and Mother House.",
                    "Evening: Indulge in authentic Rasgulla, Sandesh, and Mishti Doi at KC Das and Balaram Mullick."
                ]
            }
        ],
        "top_attractions": ["Victoria Memorial", "Howrah Bridge", "Dakshineswar Temple", "Indian Museum", "Kumartuli", "Park Street"],
        "local_foods": ["Kolkata Biryani (with potato)", "Chingri Malai Curry", "Kathi Rolls (Nizam's)", "Mishti Doi", "Chelo Kebab", "Rasgulla"]
    },
    "MAA": {
        "code": "MAA",
        "name": "Chennai (Tamil Nadu)",
        "airport": "Chennai International Airport (MAA)",
        "tagline": "Gateway to South India, Classical Arts & Marina Breezes",
        "best_time_to_visit": "November to February (21°C – 29°C)",
        "flight_cost_benchmark": "₹4,200 – ₹5,300",
        "recommended_days": "3 to 4 Days",
        "airport_transit": {
            "metro": "Chennai Metro Blue Line connects directly inside Airport Terminal to Central Station in 35 mins (₹40).",
            "cabs": "Dedicated app cab pickup points and Fast Track prepaid taxis (₹400–₹700 to city center)."
        },
        "itinerary_3d": [
            {
                "day": "Day 1: Dravidian Temples & Marina Beach Waves",
                "activities": [
                    "Morning: Kapaleeshwarar Temple in Mylapore, towering gopuram architecture and morning chants.",
                    "Afternoon: Filter coffee and traditional Thali lunch served on banana leaf at Saravana Bhavan.",
                    "Evening: Walk along Marina Beach (world's 2nd longest natural urban beach) and enjoy fried sundal and fish fry."
                ]
            },
            {
                "day": "Day 2: Shore Temples Excursion to Mahabalipuram",
                "activities": [
                    "Morning: Scenic East Coast Road (ECR) drive to UNESCO-listed Shore Temple & Pancha Rathas.",
                    "Afternoon: Marvel at Arjuna's Penance rock relief and beachside seafood lunch.",
                    "Evening: Return to Chennai via Cholamandal Artists' Village."
                ]
            },
            {
                "day": "Day 3: Colonial Roots & Cultural Revival",
                "activities": [
                    "Morning: Fort St. George (oldest English fort in India) and Government Museum at Egmore.",
                    "Afternoon: Silk sari shopping at T. Nagar and Kalakshetra Foundation cultural heritage.",
                    "Evening: Sunset at Besant Nagar (Elliot's Beach) with café hopping."
                ]
            }
        ],
        "top_attractions": ["Kapaleeshwarar Temple", "Marina Beach", "Mahabalipuram Shore Temple", "San Thome Cathedral", "Fort St. George"],
        "local_foods": ["Crispy Ghee Podi Dosa", "Filter Kaapi", "Chettinad Chicken", "Idli & Vada with 4 Chutneys", "Sundal", "Jigarthanda"]
    },
    "JAI": {
        "code": "JAI",
        "name": "Jaipur (Rajasthan)",
        "airport": "Jaipur International Airport (JAI)",
        "tagline": "The Pink City of Fortresses, Royal Palaces & Jewel Bazars",
        "best_time_to_visit": "October to March (10°C – 26°C)",
        "flight_cost_benchmark": "₹2,500 – ₹4,200",
        "recommended_days": "3 to 4 Days",
        "airport_transit": {
            "cabs": "Prepaid airport taxis and Uber/Ola (₹300–₹500 to walled Pink City).",
            "bus": "Jaipur Low Floor AC bus Route 3B connects airport to railway station."
        },
        "itinerary_3d": [
            {
                "day": "Day 1: The Walled Pink City & Palaces",
                "activities": [
                    "Morning: Iconic honeycomb façade of Hawa Mahal (Palace of Winds) in morning light.",
                    "Afternoon: City Palace museum and astronomical instruments at Jantar Mantar (UNESCO).",
                    "Evening: Traditional Rajasthani Thali (Dal Baati Churma) at Laxmi Mishthan Bhandar (LMB) in Johari Bazaar."
                ]
            },
            {
                "day": "Day 2: Royal Hilltop Fortresses & Mirror Halls",
                "activities": [
                    "Morning: Ascent to Amber Fort (Sheesh Mahal mirror mosaics and Maota Lake view).",
                    "Afternoon: Jaigarh Fort (home to Jaivana, world's largest wheeled cannon) and scenic Jal Mahal.",
                    "Evening: Golden hour sunset drinks at Nahargarh Fort overlooking the illuminated Jaipur skyline."
                ]
            },
            {
                "day": "Day 3: Block Printing, Blue Pottery & Stepwells",
                "activities": [
                    "Morning: Marvel at the geometric steps of Panna Meena ka Kund stepwell.",
                    "Afternoon: Traditional block printing workshop in Sanganer and blue pottery shopping.",
                    "Evening: Cultural folk dance, puppet show, and royal dining at Chokhi Dhani."
                ]
            }
        ],
        "top_attractions": ["Hawa Mahal", "Amber Fort", "City Palace", "Nahargarh Fort", "Jantar Mantar", "Jal Mahal", "Johari Bazaar"],
        "local_foods": ["Dal Baati Churma", "Laal Maas", "Pyaaz Kachori (Rawat Mishthan)", "Ghewar", "Ker Sangri", "Mawa Kachori"]
    }
}

DGCA_GUIDELINES = {
    "passenger_charter": {
        "title": "DGCA Passenger Rights & Cancellation Charter (CAR Section 3, Series M, Part IV)",
        "summary": "Mandatory aviation regulations issued by the Directorate General of Civil Aviation, Government of India, protecting domestic and international passengers.",
        "key_rights": [
            {
                "topic": "24-Hour Zero Penalty Look-in Window",
                "rule": "Passengers have the legal right to cancel or amend tickets without any cancellation charge within 24 hours of booking, provided travel date is at least 7 days ahead for domestic flights.",
                "compensation": "100% full refund with ZERO airline penalty."
            },
            {
                "topic": "Flight Delays (>2 Hours)",
                "rule": "If a domestic flight is delayed by >2 hours, the airline must provide free refreshments/meals. If delayed >24 hours or overnight, airline must provide free hotel accommodation and ground transfers.",
                "compensation": "Passenger can opt for immediate 100% full refund or free rebooking without fee."
            },
            {
                "topic": "Flight Cancellations (<24 Hours Notice)",
                "rule": "If an airline cancels a flight without at least 24 hours advance notification or causes a missed connecting flight booked on the same PNR.",
                "compensation": "Full ticket refund + statutory compensation up to ₹10,000 (₹5,000 for block time <1 hr; ₹7,500 for block time 1–2 hrs; ₹10,000 for block time >2 hrs)."
            },
            {
                "topic": "Denied Boarding (Overbooking)",
                "rule": "If a passenger holding a confirmed ticket is involuntarily denied boarding due to commercial overbooking.",
                "compensation": "Alternative flight within 1 hr OR up to 400% of booked one-way basic fare + fuel surcharge (capped at ₹20,000) + full ticket refund."
            },
            {
                "topic": "Refund SLA Timelines",
                "rule": "Mandatory turnaround time for issuing passenger ticket refunds.",
                "compensation": "Credit Card: Within 7 working days. UPI / Debit Card / NetBanking: Within 3 working days. Cash: Immediate."
            }
        ]
    },
    "baggage_matrix": [
        {
            "airline": "IndiGo",
            "cabin_allowance": "7 kg (1 piece + laptop bag)",
            "checked_allowance": "15 kg (1 piece)",
            "student_baggage": "+10 kg free (Total 25 kg)",
            "excess_rate_per_kg": "₹550 / kg",
            "prebook_excess_slab": "₹1,900 for 5kg slab"
        },
        {
            "airline": "Air India",
            "cabin_allowance": "7 kg (1 piece + personal item)",
            "checked_allowance": "15 kg – 25 kg (depending on fare brand: Classic 15kg, Flex 25kg)",
            "student_baggage": "+10 kg free (Total 25 kg)",
            "excess_rate_per_kg": "₹500 / kg",
            "prebook_excess_slab": "₹1,800 for 5kg slab"
        },
        {
            "airline": "Akasa Air",
            "cabin_allowance": "7 kg (1 piece + handbag)",
            "checked_allowance": "15 kg (1 piece)",
            "student_baggage": "+10 kg free (Total 25 kg)",
            "excess_rate_per_kg": "₹525 / kg",
            "prebook_excess_slab": "₹1,850 for 5kg slab"
        },
        {
            "airline": "SpiceJet",
            "cabin_allowance": "7 kg (1 piece)",
            "checked_allowance": "15 kg (1 piece)",
            "student_baggage": "+10 kg free (Total 25 kg)",
            "excess_rate_per_kg": "₹550 / kg",
            "prebook_excess_slab": "₹1,950 for 5kg slab"
        },
        {
            "airline": "Air India Express",
            "cabin_allowance": "7 kg (1 piece)",
            "checked_allowance": "15 kg (Xpress BIZ: 25kg)",
            "student_baggage": "+10 kg free (Total 25 kg)",
            "excess_rate_per_kg": "₹500 / kg",
            "prebook_excess_slab": "₹1,800 for 5kg slab"
        }
    ],
    "digiyatra": {
        "title": "DigiYatra Biometric Smart Airport Entry",
        "description": "Facial recognition-based digital boarding initiative by Ministry of Civil Aviation (MoCA) for seamless, contactless, paperless terminal entry.",
        "how_it_works": [
            "Step 1: Download the official DigiYatra app on iOS or Android.",
            "Step 2: Link Aadhaar credentials via DigiLocker and capture live selfie.",
            "Step 3: Scan boarding pass 24 hours prior to flight departure.",
            "Step 4: At airport e-gate, scan face to enter terminal in under 15 seconds (bypassing manual CISF ID queues)."
        ],
        "airports_supported": ["DEL", "BOM", "BLR", "HYD", "CCU", "MAA", "PNQ", "GOI", "JAI", "VNS", "IXC", "LKO"]
    },
    "security_regulations": [
        {
            "item": "Power Banks & Portable Lithium Batteries",
            "status": "Cabin Baggage ONLY",
            "rule": "Strictly prohibited in checked luggage due to fire safety (BCAS norm). Maximum capacity 100Wh to 160Wh with airline approval."
        },
        {
            "item": "Liquids, Aerosols & Gels (LAGs)",
            "status": "Permitted with limits",
            "rule": "Containers up to 100ml in transparent resealable bag. Duty-free purchases permitted in sealed tamper-evident bags (STEBs)."
        },
        {
            "item": "Electronic Cigarettes & Vapes",
            "status": "Completely BANNED in India",
            "rule": "Under Prohibition of Electronic Cigarettes Act (PECA) 2019, possession, transport, and carriage in cabin or checked baggage is illegal."
        },
        {
            "item": "Dry Coconut (Copra) & Matchboxes",
            "status": "Strictly Prohibited",
            "rule": "Copra is flammable; safety matches prohibited in checked bags (1 small box permitted on person)."
        }
    ]
}

@router.get("/destinations")
def get_all_destinations():
    """Retrieve list of curated travel guide destinations."""
    summary_list = []
    for code, data in DESTINATIONS_DATA.items():
        summary_list.append({
            "code": code,
            "name": data["name"],
            "airport": data["airport"],
            "tagline": data["tagline"],
            "best_time_to_visit": data["best_time_to_visit"],
            "flight_cost_benchmark": data["flight_cost_benchmark"],
            "recommended_days": data["recommended_days"],
            "top_attractions": data["top_attractions"]
        })
    return {"total": len(summary_list), "destinations": summary_list}

@router.get("/destination/{code}")
def get_destination_detail(code: str):
    """Retrieve detailed travel itinerary and transit guide for a city."""
    code_upper = code.upper().strip()
    if code_upper not in DESTINATIONS_DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Travel guide for airport code '{code_upper}' not found. Available: {list(DESTINATIONS_DATA.keys())}"
        )
    return DESTINATIONS_DATA[code_upper]

@router.get("/guidelines")
def get_guidelines():
    """Retrieve official DGCA passenger rights charter, baggage matrix, and security rules."""
    return DGCA_GUIDELINES
