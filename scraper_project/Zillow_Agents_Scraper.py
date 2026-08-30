"""
Zillow Real Estate Agent Scraper
=================================
Scrapes agent/broker details from all cities in Alabama & Illinois.

Requirements:
    pip install seleniumbase

Usage:
    python Zillow_Agents_Scraper.py

Output:
    zillow_agents_data.csv (single file, appended incrementally)

Notes:
    - Uses SeleniumBase UC mode for anti-detection + auto-CAPTCHA solving
    - Saves progress after every batch; safe to stop (Ctrl+C) and restart
    - Browser must remain VISIBLE (not minimized) for CAPTCHA auto-solver
    - Do NOT lock your screen while running - the solver needs mouse control
"""

import csv
import json
import os
import re
import time
import random
import traceback

try:
    from seleniumbase import SB
except ImportError:
    print("=" * 60)
    print("  SeleniumBase is required. Install it with:")
    print("    pip install seleniumbase")
    print("=" * 60)
    exit(1)


# -------------------------------------------------------------
# CONFIGURATION - Edit these as needed
# -------------------------------------------------------------

STATES_TO_SCRAPE = {
    "Alabama": "al",
    "Illinois": "il",
}

OUTPUT_FILE = "zillow_agents_data.csv"
STATE_FILE = "zillow_scraper_state.json"
BASE_URL = "https://www.zillow.com/professionals/real-estate-agent-reviews"

MAX_PAGES_PER_CITY = None   # None = scrape ALL pages. Set to e.g. 3 for testing.
BATCH_SAVE_SIZE = 20        # Save to CSV every N agents (within a city)

CSV_HEADERS = [
    "Agent Name",
    "Office/Realty",
    "Sales Last 12 Months",
    "Total Sales",
    "Mobile Phone",
    "Office Phone",
    "Email",
    "Location",
    "Service Areas",
    "Website",
    "Zillow Profile URL",
]

# Delay ranges in seconds - randomized to look human.
# We have optimized these for speed, but if Zillow starts throwing 
# constant CAPTCHAs, you may need to increase them.
DELAY_BETWEEN_PAGES = (1.5, 3.0)
DELAY_BETWEEN_PROFILES = (1.5, 3.5)
DELAY_AFTER_CAPTCHA_CHECK = (1, 2)


# -------------------------------------------------------------
# CITY LISTS - Comprehensive lists for each state
# Add or remove cities as needed. The scraper will gracefully
# skip any city that Zillow doesn't have agents for.
# -------------------------------------------------------------

CITIES = {
    "ak": [
        "Anchorage", "Fairbanks", "Juneau", "Eagle River", "Badger",
        "Knik-Fairview", "College", "Wasilla", "Sitka", "Lakes",
        "Ketchikan", "Tanaina", "Kalifornsky", "Kenai", "Meadow Lakes",
        "Palmer", "Elmendorf Air Force Base", "Bethel", "Kodiak", "Sterling",
        "Gateway", "Homer", "Farmers Loop", "Fishhook", "Soldotna",
        "Nikiski", "Unalaska", "Utqiagvik", "Dutch Harbor", "Valdez",
        "Nome", "Big Lake", "Kotzebue", "Butte", "Petersburg",
        "Seward", "Eielson Air Force Base", "Ester", "Dillingham", "Wrangell",
        "Deltana", "Girdwood", "Houston", "Cordova", "North Pole",
        "Prudhoe Bay", "Willow", "Ridgeway", "Bear Creek", "Fritz Creek",
        "Anchor Point", "Haines", "Lazy Mountain", "Sutton-Alpine", "Metlakatla",
        "Cohoe", "Kodiak Station", "Susitna North", "Tok", "Craig",
        "Skagway", "Hooper Bay", "Diamond Ridge", "Funny River", "Salcha",
        "Sand Point", "Akutan", "Farm Loop", "Healy", "Chevak",
        "King Cove",
    ],
    "al": [
        "Huntsville", "Birmingham", "Montgomery", "Mobile", "Tuscaloosa",
        "Hoover", "Dothan", "Auburn", "Decatur", "Madison",
        "Florence", "Phenix City", "Gadsden", "East Florence", "Prattville",
        "Vestavia Hills", "Alabaster", "Opelika", "Enterprise", "Bessemer",
        "Homewood", "Athens", "Daphne", "Northport", "Dixiana",
        "Pelham", "Prichard", "Anniston", "Albertville", "Oxford",
        "Trussville", "Mountain Brook", "Selma", "Troy", "Fairhope",
        "Helena", "Tillmans Corner", "Foley", "Center Point", "Hueytown",
        "Talladega", "Cullman", "Millbrook", "Scottsboro", "Ozark",
        "Alexander City", "Hartselle", "Fort Payne", "Jasper", "Saraland",
        "Gardendale", "Muscle Shoals", "Pell City", "Calera", "Sylacauga",
        "Eufaula", "Moody", "Irondale", "Jacksonville", "Chelsea",
        "Leeds", "Gulf Shores", "Fairfield", "Saks", "Pleasant Grove",
        "Forestdale", "Atmore", "Russellville", "Boaz", "Clay",
        "Rainbow City", "Valley", "Bay Minette", "Sheffield", "Andalusia",
        "Fultondale", "Clanton", "Tuskegee", "Meadowbrook", "Southside",
        "Tuscumbia", "Guntersville", "Arab", "Pike Road", "Spanish Fort",
        "Wetumpka", "Lake Purdy", "Greenville", "Pinson", "Demopolis",
        "Hamilton", "Brook Highland", "Opp", "Montevallo", "Oneonta",
        "Lincoln", "Lanett", "Danville", "Tarrant", "Satsuma",
    ],
    "ar": [
        "Little Rock", "Fort Smith", "Fayetteville", "Springdale", "Jonesboro",
        "North Little Rock", "Conway", "Rogers", "Pine Bluff", "Bentonville",
        "Hot Springs", "Benton", "Sherwood", "Texarkana", "Russellville",
        "Jacksonville", "Bella Vista", "Paragould", "Cabot", "West Memphis",
        "Searcy", "Van Buren", "Bryant", "El Dorado", "Maumelle",
        "Siloam Springs", "Blytheville", "Forrest City", "Harrison", "Hot Springs Village",
        "Mountain Home", "Marion", "Centerton", "Magnolia", "Camden",
        "Helena-West Helena", "Malvern", "Arkadelphia", "Batesville", "Hope",
        "Monticello", "Clarksville", "Greenwood", "Stuttgart", "Lowell",
        "Wynne", "Beebe", "Newport", "West Helena", "Osceola",
        "Heber Springs", "Trumann", "East End", "Morrilton", "De Queen",
        "Farmington", "Pocahontas", "Warren", "Mena", "Alma",
        "Helena", "Berryville", "Greenbrier", "Pea Ridge", "Crossett",
        "Prairie Grove", "White Hall", "Sheridan", "Barling", "Ward",
        "Piney", "Walnut Ridge", "Dardanelle", "Cherokee Village", "Haskell",
        "Ashdown", "Nashville", "Vilonia", "Dumas", "Lonoke",
        "Fordyce", "McGehee", "Booneville", "Shannon Hills", "Rockwell",
        "Marianna", "Manila", "Piggott", "Johnson", "Ozark",
        "Landmark", "Gibson", "Paris", "Waldron", "Gentry",
        "Austin", "De Witt", "Gravette", "Corning", "Prescott",
    ],
    "az": [
        "Phoenix", "Tucson", "Mesa", "Chandler", "Gilbert",
        "Glendale", "Scottsdale", "Maryvale", "Peoria", "Tempe",
        "Deer Valley", "Tempe Junction", "Surprise", "Alhambra", "Yuma",
        "Ahwatukee Foothills", "San Tan Valley", "Avondale", "Goodyear", "Flagstaff",
        "Casas Adobes", "Central City", "Encanto", "Lake Havasu City", "Casa Grande",
        "Buckeye", "Catalina Foothills", "Maricopa", "Oro Valley", "Sierra Vista",
        "Prescott Valley", "Prescott", "Marana", "Bullhead City", "Apache Junction",
        "Sun City", "Queen Creek", "El Mirage", "San Luis", "Florence",
        "Kingman", "Drexel Heights", "Fortuna Foothills", "Sahuarita", "Sun City West",
        "Fountain Hills", "Anthem", "Green Valley", "Nogales", "Rio Rico",
        "Eloy", "Tanque Verde", "Douglas", "Flowing Wells", "Payson",
        "Somerton", "New River", "Sierra Vista Southeast", "Sun Lakes", "Paradise Valley",
        "Saddlebrooke", "Coolidge", "Tucson Estates", "New Kingman-Butler", "Cottonwood",
        "Verde Village", "West Sedona", "Camp Verde", "Chino Valley", "Show Low",
        "Arizona City", "Sedona", "Vail", "Gold Camp", "Gold Canyon",
        "Safford", "Winslow", "Picture Rocks", "Valencia West", "Tuba City",
        "Golden Valley", "Catalina", "Page", "Globe", "Tolleson",
        "Wickenburg", "Big Park", "Youngtown", "Guadalupe", "Village of Oak Creek (Big Park)",
        "Avra Valley", "Laveen", "South Tucson", "Corona de Tucson", "Snowflake",
        "Three Points", "Litchfield Park", "Williamson", "Summit", "Cave Creek",
    ],
    "ca": [
        "Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno",
        "Sacramento", "Long Beach", "Oakland", "Bakersfield", "Anaheim",
        "Riverside", "Santa Ana", "Stockton", "Chula Vista", "Irvine",
        "Fremont", "San Bernardino", "Fontana", "Modesto", "Oxnard",
        "Moreno Valley", "Huntington Beach", "Glendale", "Santa Clarita", "Santa Rosa",
        "Oceanside", "Garden Grove", "Rancho Cucamonga", "Ontario", "Hollywood",
        "Elk Grove", "Corona", "Lancaster", "Palmdale", "Hayward",
        "Salinas", "Sunnyvale", "Pomona", "Escondido", "Valencia",
        "Torrance", "Pasadena", "Orange", "Fullerton", "Van Nuys",
        "Roseville", "Visalia", "Thousand Oaks", "Concord", "Simi Valley",
        "East Los Angeles", "Santa Clara", "Koreatown", "Victorville", "Vallejo",
        "Chico", "Berkeley", "El Monte", "Carlsbad", "Downey",
        "Costa Mesa", "Fairfield", "Inglewood", "Antioch", "Temecula",
        "Murrieta", "Richmond", "West Covina", "Norwalk", "Daly City",
        "Burbank", "Santa Maria", "Universal City", "Clovis", "El Cajon",
        "San Mateo", "Rialto", "Vista", "Chinatown", "Compton",
        "Mission Viejo", "Vacaville", "Ventura", "South Gate", "Hesperia",
        "Carson", "Santa Monica", "San Marcos", "Boyle Heights", "Arden-Arcade",
        "Westminster", "Santa Barbara", "Redding", "San Leandro", "Hawthorne",
        "Livermore", "Indio", "Whittier", "Menifee", "Newport Beach",
    ],
    "co": [
        "Denver", "Colorado Springs", "Aurora", "Fort Collins", "Lakewood",
        "Thornton", "Westminster", "Arvada", "Centennial", "Pueblo",
        "Greeley", "Boulder", "Highlands Ranch", "Longmont", "Loveland",
        "Broomfield", "Grand Junction", "Castle Rock", "Commerce City", "Parker",
        "Littleton", "Southglenn", "Northglenn", "Brighton", "Dakota Ridge",
        "Englewood", "Security-Widefield", "Windsor", "Ken Caryl", "Wheat Ridge",
        "Pueblo West", "Fountain", "Lafayette", "Castlewood", "Columbine",
        "Erie", "Evans", "Louisville", "Golden", "Clifton",
        "Montrose", "Sherrelwood", "Durango", "Cañon City", "Cimarron Hills",
        "Greenwood Village", "Johnstown", "Welby", "Sterling", "Fort Carson",
        "Lone Tree", "Black Forest", "Superior", "Fruita", "Steamboat Springs",
        "Federal Heights", "Firestone", "Frederick", "Fort Morgan", "Berkley",
        "Cherry Creek", "The Pinery", "Castle Pines North", "Edwards", "Glenwood Springs",
        "Alamosa", "Rifle", "Gunbarrel", "Roxborough Park", "Evergreen",
        "Stonegate", "Craig", "Delta", "Woodmoor", "Cortez",
        "Redlands", "Trinidad", "Bailey", "Fort Lupton", "Wellington",
        "Derby", "Fruitvale", "Lamar", "Woodland Park", "Applewood",
        "La Junta", "Gypsum", "Stratmoor", "Aspen", "Orchard Mesa",
        "Air Force Academy", "Eagle", "Carbondale", "Gleneagle", "Cherry Hills Village",
        "Avon", "Monument", "Milliken", "Estes Park", "Twin Lakes",
    ],
    "ct": [
        "Bridgeport", "New Haven", "Stamford", "North Stamford", "Hartford",
        "Waterbury", "Norwalk", "Danbury", "East Norwalk", "New Britain",
        "West Hartford", "Bristol", "Meriden", "Hamden", "Fairfield",
        "West Haven", "Milford", "Stratford", "City of Milford (balance)", "East Hartford",
        "Middletown", "Enfield", "Southington", "Shelton", "Norwich",
        "Trumbull", "West Torrington", "Torrington", "Glastonbury", "Naugatuck",
        "Manchester", "Newington", "Cheshire", "Branford", "East Haven",
        "Windsor", "New London", "Wethersfield", "Mansfield City", "Westport",
        "Farmington", "South Windsor", "North Haven", "Windham", "Guilford",
        "Bloomfield", "Darien", "Montville Center", "Southbury", "New Canaan",
        "Waterford", "Madison", "Avon", "Ansonia", "Wallingford Center",
        "Wilton", "Willimantic", "Wallingford", "Plainville", "Killingly Center",
        "Wolcott", "Seymour", "Plainfield", "Storrs", "Ledyard",
        "Tolland", "Ellington", "North Branford", "New Fairfield", "Orange",
        "Cromwell", "Greenwich", "Derby", "Windsor Locks", "Plymouth",
        "Stafford", "Oxford", "Winchester Center", "Old Saybrook", "Woodbury",
        "Bethel", "Prospect", "Thompson", "Woodbridge", "Hebron",
        "Groton", "Oakville", "East Haddam", "Conning Towers-Nautilus Park", "Thompsonville",
        "Kensington", "Riverside", "Winsted", "Southwood Acres", "Ridgefield",
        "Easton", "Rockville", "Glastonbury Center", "Putnam", "Middlebury",
    ],
    "dc": [
        "Washington", "Downtown DC", "Columbia Heights", "Mount Pleasant", "Central 14th Street / Spring Road",
        "Northwest One", "Dupont Circle", "Foggy Bottom", "Mount Vernon Triangle", "H Street NE",
        "Pleasant Plains", "NoMa", "Petworth", "Capitol Riverfront", "Park View",
        "Golden Triangle", "Shaw", "Brightwood", "Adams Morgan", "Kennedy Street",
        "Southwest Waterfront", "Capitol Hill", "Barracks Row", "Union Market", "Georgetown",
        "Anacostia", "Colorado Triangle", "Brentwood Village", "The Wharf", "Central 14th Street / WMATA Northern Bus Barn",
        "Van Ness", "Benning Road", "Hillcrest", "Deanwood", "Woodley Park",
        "Cleveland Park", "Bellevue", "Chevy Chase", "Riggs Park", "Benning",
        "Lincoln Heights", "Brookland", "The Parks At Walter Reed", "Congress Heights", "Glover Park",
        "Georgia Avenue / Walter Reed", "Kenilworth", "Capitol Gateway", "Woodridge", "Fort Lincoln",
        "Tenleytown", "Ivy City", "Pennsylvania Avenue SE", "Bloomingdale", "Barry Farms",
    ],
    "de": [
        "Wilmington", "Dover", "Newark", "Middletown", "Bear",
        "Brookside", "Glasgow", "Hockessin", "Smyrna", "Pike Creek Valley",
        "Milford", "Claymont", "North Star", "Pike Creek", "Wilmington Manor",
        "Seaford", "Georgetown", "Elsmere", "Edgemoor", "New Castle",
        "Millsboro", "Laurel", "Nassau", "Harrington", "Camden",
        "Highland Acres", "Dover Base Housing", "Rising Sun-Lebanon", "Clayton", "Lewes",
        "Milton", "Riverview", "Selbyville", "Greenville", "Woodside East",
        "Bridgeville", "Townsend", "Ocean View", "Long Neck", "Kent Acres",
        "Delaware City", "Delmar", "Rodney Village", "Wyoming", "Rehoboth Beach",
        "Cheswold", "Felton", "Blades", "Bellefonte", "Bethany Beach",
        "Greenwood", "Newport",
    ],
    "fl": [
        "Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg",
        "Hialeah", "Tallahassee", "Fort Lauderdale", "Cape Coral", "Pembroke Pines",
        "Port Saint Lucie", "Hollywood", "Gainesville", "Miramar", "Coral Springs",
        "West Palm Beach", "Palm Bay", "Clearwater", "Miami Gardens", "Pompano Beach",
        "Lakeland", "Brandon", "Davie", "Spring Hill", "Boca Raton",
        "Plantation", "Miami Beach", "Deltona", "Lehigh Acres", "Melbourne",
        "Sunrise", "Palm Coast", "Largo", "Homestead", "Kendall",
        "Deerfield Beach", "Town 'n' Country", "Alafaya", "Doral", "Fort Myers",
        "Boynton Beach", "Daytona Beach", "Lauderhill", "Riverview", "Weston",
        "Kissimmee", "Delray Beach", "Tamarac", "Carol City", "Jupiter",
        "Wellington", "North Miami", "North Port", "West Hollywood", "Pine Hills",
        "Port Orange", "Fountainebleau", "Coconut Creek", "Ocala", "Sanford",
        "Palm Harbor", "Margate", "Kendale Lakes", "Tamiami", "Sarasota",
        "Bradenton", "Port Charlotte", "Allapattah", "East Pensacola Heights", "Pensacola",
        "Little Havana", "Poinciana", "Palm Beach Gardens", "Bonita Springs", "Pinellas Park",
        "The Villages", "Coral Gables", "The Hammocks", "Flagami", "Apopka",
        "Country Club", "Cutler Bay", "Titusville", "Fort Pierce", "Oakland Park",
        "Wesley Chapel", "North Miami Beach", "North Lauderdale", "Ocoee", "Altamonte Springs",
        "University", "Ormond Beach", "Carrollwood Village", "Winter Garden", "St. Johns",
        "Hallandale Beach", "North Fort Myers", "Princeton", "The Acreage", "Oviedo",
    ],
    "ga": [
        "Atlanta", "Columbus", "Savannah", "Athens", "South Fulton",
        "Sandy Springs", "Roswell", "Macon", "Johns Creek", "Albany",
        "Warner Robins", "Alpharetta", "Marietta", "Smyrna", "Valdosta",
        "Brookhaven", "Stonecrest", "Dunwoody", "Augusta", "Peachtree Corners",
        "Gainesville", "Milton", "Newnan", "Mableton", "Rome",
        "Martinez", "East Point", "Peachtree City", "Dalton", "Kennesaw",
        "Hinesville", "Redan", "Douglasville", "Statesboro", "Lawrenceville",
        "Woodstock", "LaGrange", "Duluth", "Evans", "Chamblee",
        "Stockbridge", "Tucker", "Carrollton", "Canton", "McDonough",
        "Griffin", "Pooler", "Candler-McAfee", "Acworth", "Decatur",
        "Sugar Hill", "Union City", "Cartersville", "Snellville", "Forest Park",
        "North Druid Hills", "Milledgeville", "Thomasville", "Suwanee", "St. Marys",
        "Fayetteville", "Tifton", "North Decatur", "Norcross", "Kingsland",
        "Calhoun", "Dublin", "Brunswick", "Americus", "Riverdale",
        "Conyers", "Lithia Springs", "Perry", "Winder", "Belvedere Park",
        "Wilmington Island", "Villa Rica", "Powder Springs", "College Park", "Druid Hills",
        "Moultrie", "Waycross", "Fairburn", "Covington", "Saint Simon Mills",
        "Buford", "Monroe", "Grovetown", "Saint Simons Island", "Dallas",
        "Lilburn", "Bainbridge", "Clarkston", "Richmond Hill", "Georgetown",
        "Douglas", "Mountain Park", "Cusseta", "Loganville", "Cordele",
    ],
    "hi": [
        "Honolulu", "East Honolulu", "Pearl City", "Waiau-Pacific Palisades", "Makakilo / Kapolei / Honokai Hale",
        "Kalihi-Palama", "Hilo", "Joint Base Pearl Harbor Hickam", "Aliamanu / Salt Lakes / Foster Village", "Kailua",
        "Waipahu", "ʻEwa Gentry-West Loch", "Kaneohe", "Makiki / Lower Punchbowl / Tantalus", "Hawai‘i Kai",
        "Airport", "McCully - Moiliili", "Mililani Town", "Kahului", "Liliha - Kapalama",
        "Mō‘ili‘ili", "Manoa", "‘Ewa Gentry", "Wahiawā-Whitmore", "ʻEwa Beach-Iroquois Point",
        "Mililani Mauka", "Makakilo-Makaīwa Hills-Kunia", "Kīhei", "Kaimukī", "Kalihi Valley",
        "Schofield-Wheeler", "Waikīkī", "Diamond Head / Kapahulu / Saint Louis Heights", "Niu Valley", "Ala Moana - Kakaʻako",
        "Makakilo", "Mililani Mauka / Launani Valley", "Wahiawā", "‘Ewa Beach", "Schofield Barracks",
        "Nuuanu - Punchbowl", "Kuliouou - Kalani Iki", "Koolauloa", "Kapolei Villages", "Makakilo City",
        "Wailuku", "Kapolei", "Royal Kunia", "Hālawa", "Waimalu",
        "Hālawa Heights", "Waianae", "Nānākuli", "Palolo", "Downtown",
        "Kailua-Kona", "Lahaina", "Waipio", "Hawaiian Paradise Park", "Village Park",
        "Kapa‘a", "Kakaʻako", "Kalaoa", "Marine Corps Base Hawaii - MCBH", "Mā‘ili",
        "Moanalua", "Mākaha-Kaʻena", "‘Aiea", "Haiku-Pauwela", "Waimea",
        "Waihee-Waiehu", "‘Āhuimanu", "Haʻikū", "Hōlualoa", "Ocean Pointe",
        "Mākaha", "Ford Island", "Pukalani", "Napili-Honokowai", "Makawao",
        "Moanalua Valley", "Pacific Palisades", "Hickam Field", "ʻEwa Villages-Honouliuli", "Camp H.M. Smith",
        "Lihue", "Kula", "Spreckelsville", "Keolu Hills", "Lā‘ie",
        "‘Ewa Villages", "Kekaha-Waimea", "Wailea", "Kuli‘ou‘ou", "Wailea-Makena",
        "Ala Moana", "Waipi‘o Acres", "West Loch Estates", "‘Aiea Heights", "Waimanalo",
    ],
    "ia": [
        "Des Moines", "Cedar Rapids", "Davenport", "Sioux City", "Iowa City",
        "Waterloo", "Ames", "West Des Moines", "Council Bluffs", "Dubuque",
        "Ankeny", "Urbandale", "Cedar Falls", "Marion", "Bettendorf",
        "Marshalltown", "Mason City", "Clinton", "Burlington", "Fort Dodge",
        "Ottumwa", "Muscatine", "Johnston", "Coralville", "Waukee",
        "Altoona", "North Liberty", "Indianola", "Clive", "Newton",
        "Boone", "Oskaloosa", "Spencer", "Storm Lake", "Fort Madison",
        "Grimes", "Keokuk", "Pella", "Norwalk", "Waverly",
        "Carroll", "Fairfield", "Le Mars", "Pleasant Hill", "Grinnell",
        "Mount Pleasant", "Denison", "Perry", "Decorah", "Creston",
        "Webster City", "Clear Lake", "Sioux Center", "Charles City", "Washington",
        "Knoxville", "Hiawatha", "Atlantic", "Nevada", "Eldridge",
        "Orange City", "Oelwein", "Independence", "Estherville", "Maquoketa",
        "Centerville", "Red Oak", "Algona", "Anamosa", "Clarinda",
        "Centerville", "Asbury", "Glenwood", "De Witt", "Iowa Falls",
        "Winterset", "Vinton", "Sheldon", "Manchester", "Cherokee",
        "Shenandoah", "Spirit Lake", "Harlan", "Bondurant", "Osceola",
        "Windsor Heights", "Evansdale", "Humboldt", "Sergeant Bluff", "Mount Vernon",
        "Camanche", "Polk City", "Hampton", "Adel", "Chariton",
        "Dyersville", "Jefferson", "Carlisle", "Forest City", "Le Claire",
    ],
    "id": [
        "Boise", "Meridian", "Nampa", "Idaho Falls", "Pocatello",
        "Caldwell", "Coeur d'Alene", "Twin Falls", "Lewiston", "Lewiston Orchards",
        "Post Falls", "Rexburg", "Moscow", "Eagle", "Conda",
        "Kuna", "Ammon", "Chubbuck", "Hayden", "Mountain Home",
        "Blackfoot", "Garden City", "Jerome", "Burley", "Hailey",
        "Sandpoint", "Star", "Rathdrum", "Payette", "Middleton",
        "Emmett", "Rupert", "Weiser", "Preston", "Fruitland",
        "Shelley", "American Falls", "Buhl", "Rigby", "Lincoln",
        "Kimberly", "Saint Anthony", "Gooding", "Heyburn", "Fort Hall",
        "Grangeville", "McCall", "Orofino", "Salmon", "Soda Springs",
        "Wendell", "Ketchum", "Filer", "Homedale", "Bonners Ferry",
        "Montpelier", "Saint Maries", "Dalton Gardens", "Bellevue", "Hidden Spring",
        "Spirit Lake", "Parma", "Kellogg", "Iona", "Malad City",
        "Victor", "Aberdeen", "Priest River", "Driggs", "Wilder",
        "Pinehurst", "Osburn", "New Plymouth", "Shoshone", "Sun Valley",
        "Sugar City", "Marsing", "Moreland", "Kamiah", "Hansen",
        "Glenns Ferry", "Paul", "Lapwai", "Ponderay", "Ucon",
        "Tyhee", "Ashton", "Challis", "Plummer", "Cascade",
        "Arco", "Council", "Wallace", "Dubois", "Paris",
        "Idaho City", "Nezperce", "Fairfield", "Murphy",
    ],
    "il": [
        "Chicago", "Aurora", "Rockford", "Joliet", "Naperville",
        "Peoria", "Springfield", "North Peoria", "Elgin", "Waukegan",
        "West Town", "Champaign", "Near North Side", "Cicero", "Belmont Cragin",
        "Bloomington", "Arlington Heights", "Evanston", "Schaumburg", "Bolingbrook",
        "South Lawndale", "Logan Square", "Decatur", "West Ridge", "Palatine",
        "Lincoln Park", "Portage Park", "Skokie", "Des Plaines", "Orland Park",
        "Tinley Park", "Oak Lawn", "Irving Park", "Berwyn", "Chicago Lawn",
        "Uptown", "Edgewater", "Mount Prospect", "Rogers Park", "Normal",
        "Wheaton", "Oak Park", "Hoffman Estates", "Albany Park", "South Shore",
        "Downers Grove", "Glenview", "Elmhurst", "Auburn Gresham", "Brighton Park",
        "Lombard", "DeKalb", "Ashburn", "Moline", "Plainfield",
        "Urbana", "Belleville", "Bartlett", "Buffalo Grove", "Gage Park",
        "New City", "Quincy", "Lincoln Square", "Streamwood", "Crystal Lake",
        "Carol Stream", "Avondale", "Romeoville", "Rock Island", "Carpentersville",
        "Hanover Park", "Wheeling", "Park Ridge", "Addison", "Calumet City",
        "North Lawndale", "North Center", "Lower West Side", "Glendale Heights", "Oswego",
        "Bridgeport", "Northbrook", "Chicago Loop", "Woodridge", "Elk Grove Village",
        "Pekin", "St. Charles", "West Lawn", "Greater Grand Crossing", "West Englewood",
        "Danville", "Mundelein", "Chatham", "Galesburg", "Gurnee",
        "Algonquin", "Chicago Heights", "Niles", "Highland Park", "North Chicago",
    ],
    "in": [
        "Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel",
        "Bloomington", "Hammond", "Gary", "Fishers", "Lafayette",
        "Muncie", "Terre Haute", "Noblesville", "Kokomo", "Greenwood",
        "Anderson", "Elkhart", "Mishawaka", "Lawrence", "Jeffersonville",
        "Columbus", "West Lafayette", "Portage", "Westfield", "New Albany",
        "Richmond", "Merrillville", "Goshen", "Valparaiso", "Michigan City",
        "Plainfield", "Granger", "Marion", "Crown Point", "Schererville",
        "East Chicago", "Hobart", "Zionsville", "Brownsburg", "Franklin",
        "Munster", "Highland", "La Porte", "Clarksville", "Greenfield",
        "Fairfield Heights", "Seymour", "Shelbyville", "Vincennes", "Logansport",
        "New Castle", "Huntington", "Broad Ripple", "Avon", "Griffith",
        "Frankfort", "Dyer", "Crawfordsville", "Lebanon", "New Haven",
        "Jasper", "Saint John", "Beech Grove", "Warsaw", "Chesterton",
        "Bedford", "Connersville", "Auburn", "North Madison", "Speedway",
        "Washington", "Lake Station", "Madison", "Cedar Lake", "Greensburg",
        "Martinsville", "Yorktown", "Peru", "Greencastle", "Wabash",
        "Plymouth", "Bluffton", "Kendallville", "Otis", "Mooresville",
        "Danville", "Decatur", "Lowell", "Columbia City", "Sellersburg",
        "Angola", "Princeton", "Elwood", "Brazil", "Charlestown",
        "Tell City", "Mount Vernon", "Lakes of the Four Seasons", "Bargersville", "Nappanee",
    ],
    "ks": [
        "Wichita", "Overland Park", "Kansas City", "Olathe", "Topeka",
        "Lawrence", "Shawnee", "Manhattan", "Lenexa", "Salina",
        "Hutchinson", "Leavenworth", "Leawood", "Dodge City", "Garden City",
        "Emporia", "Junction City", "Derby", "Prairie Village", "Hays",
        "Gardner", "Liberal", "Pittsburg", "Newton", "Great Bend",
        "McPherson", "El Dorado", "Andover", "Ottawa", "Winfield",
        "Arkansas City", "Lansing", "Merriam", "Haysville", "Atchison",
        "Parsons", "Coffeyville", "Mission", "Augusta", "Chanute",
        "Independence", "Wellington", "Fort Scott", "Fort Riley North", "Park City",
        "Bonner Springs", "Valley Center", "Pratt", "Roeland Park", "Abilene",
        "Eudora", "Mulvane", "Ulysses", "De Soto", "Spring Hill",
        "Paola", "Iola", "Colby", "Basehor", "Tonganoxie",
        "Concordia", "Goddard", "Baldwin City", "Wamego", "Russell",
        "Goodland", "Edwardsville", "Maize", "Clay Center", "Osawatomie",
        "Louisburg", "Clay Center", "Baxter Springs", "Rose Hill", "Fairway",
        "Larned", "Hugoton", "Bellaire", "Scott City", "Hesston",
        "Beloit", "Lyons", "Mission Hills", "Frontenac", "Lindsborg",
        "Marysville", "Holton", "Garnett", "Columbus", "Hiawatha",
        "Kingman", "Ellsworth", "Galena", "Hillsboro", "Osage City",
        "Norton", "Girard", "Saint Marys", "Hoisington", "Burlington",
    ],
    "ky": [
        "Louisville", "Lexington", "Lexington-Fayette", "Meads", "Bowling Green",
        "Owensboro", "Covington", "Richmond", "Georgetown", "Florence",
        "Hopkinsville", "Nicholasville", "Elizabethtown", "Henderson", "Frankfort",
        "Jeffersontown", "Independence", "Pleasure Ridge Park", "Paducah", "Valley Station",
        "Radcliff", "Ashland", "Newburg", "Madisonville", "Murray",
        "Erlanger", "Winchester", "Fern Creek", "Saint Matthews", "Okolona",
        "Danville", "Fort Thomas", "Burlington", "Shively", "Newport",
        "Shelbyville", "Highview", "Berea", "Glasgow", "Mount Washington",
        "Fort Campbell North", "Bardstown", "Shepherdsville", "Somerset", "Lyndon",
        "Campbellsville", "Lawrenceburg", "Middlesboro", "Fort Knox", "Mayfield",
        "Paris", "Saint Dennis", "Versailles", "Oakbrook", "Alexandria",
        "Maysville", "Franklin", "Edgewood", "La Grange", "Elsmere",
        "Harrodsburg", "Fort Mitchell", "Fairdale", "London", "Hillview",
        "Oak Grove", "Francisville", "Middletown", "Morehead", "Villa Hills",
        "Oak Grove", "Corbin", "Flatwoods", "Buechel", "Mount Sterling",
        "Highland Heights", "Russellville", "Morehead", "Pikeville", "Leitchfield",
        "Taylor Mill", "Cynthiana", "Knottsville", "Wilmore", "Princeton",
        "Cold Spring", "Monticello", "Hebron", "Bellevue", "Central City",
        "Buckner", "Union", "Fort Wright", "Vine Grove", "Lebanon",
        "Douglass Hills", "Dayton", "Hazard", "Williamsburg", "Prospect",
    ],
    "la": [
        "New Orleans", "Baton Rouge", "Shreveport", "Metairie Terrace", "Metairie",
        "Lafayette", "Lake Charles", "Bossier City", "Kenner", "Monroe",
        "Alexandria", "Houma", "Marrero", "New Iberia", "Laplace",
        "Central", "Slidell", "Prairieville", "Terrytown", "Ruston",
        "Hammond", "Harvey", "Sulphur", "Bayou Cane", "Shenandoah",
        "Natchitoches", "Gretna", "Chalmette", "Opelousas", "Zachary",
        "Estelle", "Thibodaux", "Pineville", "Bayou Boeuf", "Grand Bayou Mobile Home Park",
        "Baker", "River Ridge", "Crowley", "West Monroe", "Minden",
        "Belle Chasse", "Abbeville", "Mandeville", "Luling", "Woodmere",
        "Youngsville", "Bogalusa", "Morgan City", "Moss Bluff", "Destrehan",
        "Claiborne", "Broussard", "Jefferson", "DeRidder", "Bastrop",
        "Gonzales", "Gardere", "Eunice", "Timberlane", "Raceland",
        "Jennings", "Denham Springs", "Waggaman", "Covington", "Merrydale",
        "Reserve", "Harahan", "Fort Polk South", "Scott", "Lacombe",
        "Carencro", "Westwego", "Breaux Bridge", "Oak Hills Place", "Saint Rose",
        "Rayne", "Prien", "Donaldsonville", "Oakdale", "Bridge City",
        "Galliano", "Larose", "Franklin", "Ville Platte", "Village Saint George",
        "Ponchatoula", "Eden Isle", "Tallulah", "Old Jefferson", "Plaquemine",
        "Schriever", "Saint Gabriel", "Leesville", "Walker", "Red Chute",
        "Inniswold", "Saint Martinville", "Patterson", "Cut Off", "Meraux",
    ],
    "ma": [
        "Boston", "South Boston", "Worcester", "Springfield", "Lowell",
        "Cambridge", "New Bedford", "Dorchester", "Brockton", "Fall River",
        "Quincy", "Lynn", "Newton", "Somerville", "Lawrence",
        "Framingham", "Framingham Center", "Waltham", "Haverhill", "Malden",
        "Brookline", "Medford", "Taunton", "Chicopee", "North Chicopee",
        "Weymouth", "Revere", "Peabody", "Methuen", "South Peabody",
        "Barnstable", "Everett", "Brighton", "Attleboro", "Pittsfield",
        "East Boston", "Salem", "Arlington", "Westfield", "Leominster",
        "Beverly", "Holyoke", "Fitchburg", "Beverly Cove", "Billerica",
        "Amherst", "Marlborough", "Woburn", "Chelsea", "Fenway/Kenmore",
        "Jamaica Plain", "Braintree", "Mattapan", "Chelmsford", "Shrewsbury",
        "Natick", "Randolph", "Watertown", "Hyde Park", "Lexington",
        "Franklin", "West Roxbury", "Ashmont", "Gloucester", "Tewksbury",
        "Needham", "Dracut", "Allston", "Agawam", "Norwood",
        "Northampton", "North Andover", "Melrose", "Wellesley", "West Springfield",
        "Roslindale", "Milton", "Stoughton", "Saugus", "Danvers",
        "Yarmouth", "Milford", "Wakefield", "Reading", "Belmont",
        "Dedham", "Burlington", "Chestnut Hill", "Easton", "Mansfield",
        "Middleborough", "Wilmington", "Ludlow", "Canton", "Westford",
        "Stoneham", "Winchester", "Acton", "Charlestown", "Gardner",
    ],
    "md": [
        "Baltimore", "Columbia", "Germantown", "Silver Spring", "Frederick",
        "Waldorf", "Glen Burnie", "Gaithersburg", "Rockville", "Ellicott City",
        "Dundalk", "Bethesda", "Bowie", "Towson", "South Bel Air",
        "Aspen Hill", "Wheaton", "Bel Air South", "Gwynn Oak", "Potomac",
        "Severn", "North Bethesda", "Catonsville", "Annapolis", "Hagerstown",
        "Essex", "Hanover", "Woodlawn", "Severna Park", "Odenton",
        "Saint Charles", "Clinton", "Oxon Hill-Glassmanor", "North Bel Air", "Olney",
        "Suitland-Silver Hill", "Chillum", "St. Charles", "Salisbury", "Randallstown",
        "College Park", "Montgomery Village", "Pikesville", "Parkville", "Owings Mills",
        "Bel Air North", "Eldersburg", "Carney", "South Gate", "Milford Mill",
        "West Elkridge", "Perry Hall", "Crofton", "Laurel", "South Laurel",
        "Reisterstown", "Suitland", "Edgewood", "Lochearn", "Middle River",
        "North Potomac", "Scaggsville", "Pasadena", "Greenbelt", "Hunt Valley",
        "Fort Washington", "Fairland", "Ilchester", "Arnold", "Landover",
        "Cockeysville", "Arbutus", "Cumberland", "Lake Shore", "Green Haven",
        "Rosedale", "Camp Springs", "Langley Park", "Greater Upper Marlboro", "Westminster",
        "Hyattsville", "Ballenger Creek", "Lanham-Seabrook", "Calverton", "Oxon Hill",
        "Takoma Park", "White Oak", "Glassmanor", "Seabrook", "Redland",
        "Frankford", "Beltsville", "Ferndale", "Easton", "Hillcrest Heights",
        "Maryland City", "Parole", "Lutherville-Timonium", "Elkton", "Elkridge",
    ],
    "me": [
        "Portland", "Lewiston", "Bangor", "West Scarborough", "South Portland",
        "South Portland Gardens", "Auburn", "Biddeford", "Sanford", "Saco",
        "Augusta", "Westbrook", "Waterville", "Brunswick", "York Beach",
        "Wells Beach Station", "Orono", "Lisbon", "North Bath", "Brewer",
        "Presque Isle", "Old Orchard Beach", "Bath", "Buxton", "Ellsworth",
        "Caribou", "Winslow", "Old Town", "Waterboro", "South Berwick",
        "Rockland", "Gorham", "Belfast", "Eliot", "Skowhegan",
        "Topsham", "Yarmouth", "Gardiner", "Turner", "Lebanon",
        "New Gloucester", "Poland", "Harpswell Center", "Kennebunk", "Paris",
        "Houlton", "Jay", "Hermon", "North Windham", "Sabattus",
        "Raymond", "Hollis Center", "Kittery", "South Sanford", "Millinocket",
        "Scarborough", "Hampden", "Farmington", "China", "Greene Village",
        "Rumford", "Vassalboro", "Lisbon Falls", "Warren", "Monmouth",
        "Orrington", "Sidney", "Arundel", "Camden", "South Eliot",
        "Limington", "Rockport", "Springvale", "Pittsfield", "Belgrade",
        "Boothbay", "Lake Arrowhead", "York Harbor", "Calais", "Madawaska",
        "Madawaska", "Holden", "Woolwich", "Bucksport", "Lincoln",
        "Bristol", "Norway", "Saint George", "Chelsea", "Benton",
        "Winthrop", "Pittston", "Fairfield", "Madison", "Oakland",
        "Alfred", "Cape Neddick", "Manchester", "Bar Harbor", "Dover-Foxcroft",
    ],
    "mi": [
        "Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor",
        "Lansing", "Clinton Township", "Flint", "Dearborn", "Livonia",
        "Canton", "Troy", "Westland", "Farmington Hills", "Kalamazoo",
        "Waterford", "Wyoming", "Shelby", "Rochester Hills", "Southfield",
        "West Bloomfield Township", "Taylor", "Pontiac", "Saint Clair Shores", "Royal Oak",
        "Novi", "Dearborn Heights", "Battle Creek", "Kentwood", "Redford",
        "Saginaw", "East Lansing", "Portage", "Roseville", "Midland",
        "Muskegon", "Lincoln Park", "Bay City", "Holland", "Jackson",
        "Eastpointe", "Madison Heights", "Oak Park", "Port Huron", "Southgate",
        "Burton", "Allen Park", "Garden City", "Mount Pleasant", "Forest Hills",
        "Wyandotte", "Saginaw Township North", "Inkster", "Walker", "Norton Shores",
        "Holt", "Waverly", "Romulus", "Auburn Hills", "Hamtramck",
        "Okemos", "Marquette", "Birmingham", "Adrian", "Ferndale",
        "Monroe", "Ypsilanti", "Haslett", "Trenton", "Allendale",
        "Wayne", "Hazel Park", "Jenison", "Mount Clemens", "Grandville",
        "Grosse Pointe Woods", "Berkley", "Traverse City", "Owosso", "Fraser",
        "Northview", "Cutlerville", "Harper Woods", "Sault Ste. Marie", "Wixom",
        "Rochester", "Woodhaven", "New Baltimore", "Escanaba", "Riverview",
        "Clawson", "South Lyon", "Fenton", "Ionia", "Grosse Ile",
        "Niles", "East Grand Rapids", "Grosse Pointe Park", "Grand Haven", "Highland Park",
    ],
    "mn": [
        "Minneapolis", "Saint Paul", "Rochester", "Bloomington", "Duluth",
        "Brooklyn Park", "Plymouth", "Maple Grove", "Woodbury", "Eagan",
        "Saint Cloud", "Eden Prairie", "West Coon Rapids", "Coon Rapids", "Blaine",
        "Burnsville", "Lakeville", "Minnetonka", "Apple Valley", "Edina",
        "Minnetonka Mills", "Saint Louis Park", "Moorhead", "Mankato", "Maplewood",
        "Shakopee", "Richfield", "Cottage Grove", "Roseville", "Inver Grove Heights",
        "Andover", "Brooklyn Center", "Savage", "Longfellow Community", "Oakdale",
        "Fridley", "Winona", "Shoreview", "Ramsey", "Owatonna",
        "Chanhassen", "Prior Lake", "White Bear Lake", "Chaska", "Austin",
        "Elk River", "Champlin", "Faribault", "Rosemount", "Crystal",
        "Farmington", "Hastings", "New Brighton", "Golden Valley", "Lino Lakes",
        "New Hope", "Northfield", "South Saint Paul", "Columbia Heights", "Willmar",
        "Forest Lake", "West Saint Paul", "Stillwater", "Albert Lea", "Hopkins",
        "Anoka", "Sartell", "Red Wing", "Saint Michael", "Hibbing",
        "Ham Lake", "Buffalo", "Otsego", "Bemidji", "Robbinsdale",
        "Hugo", "Hutchinson", "Marshall", "North Mankato", "Sauk Rapids",
        "Brainerd", "New Ulm", "Monticello", "Fergus Falls", "Vadnais Heights",
        "Worthington", "Mounds View", "Rogers", "Cloquet", "Waconia",
        "Alexandria", "East Bethel", "North Saint Paul", "Mendota Heights", "Saint Peter",
        "Grand Rapids", "Big Lake", "Little Canada", "Fairmont", "North Branch",
    ],
    "mo": [
        "Kansas City", "St. Louis", "Springfield", "Columbia", "Independence",
        "East Independence", "Lee's Summit", "O'Fallon", "Saint Joseph", "Saint Charles",
        "Blue Springs", "Saint Peters", "Florissant", "Joplin", "Chesterfield",
        "Jefferson City", "Cape Girardeau", "Oakville", "Wildwood", "Wentzville",
        "University City", "Ballwin", "Liberty", "Raytown", "Mehlville",
        "Kirkwood", "Maryland Heights", "Gladstone", "Hazelwood", "Grandview",
        "Webster Groves", "Belton", "Sedalia", "Arnold", "Ferguson",
        "Nixa", "Raymore", "Affton", "Rolla", "Warrensburg",
        "Spanish Lake", "Old Jamestown", "Ozark", "Creve Coeur", "Manchester",
        "Farmington", "Hannibal", "Kirksville", "Poplar Bluff", "Lemay",
        "Sikeston", "Concord", "Republic", "Overland", "Clayton",
        "Fort Leonard Wood", "Jackson", "Jennings", "Lebanon", "Lake Saint Louis",
        "Carthage", "Washington", "Moberly", "Grain Valley", "Marshall",
        "Saint Ann", "Fulton", "Dardenne Prairie", "West Plains", "Neosho",
        "Festus", "Crestwood", "Maryville", "Bridgeton", "Mexico",
        "Troy", "Excelsior Springs", "Branson", "Webb City", "Town and Country",
        "Union", "Bellefontaine Neighbors", "Bolivar", "Kennett", "Eureka",
        "Harrisonville", "Cameron", "Chillicothe", "Kearney", "Ellisville",
        "Smithville", "Berkeley", "Monett", "Clinton", "Park Hills",
        "Murphy", "Ladue", "Des Peres", "Sunset Hills", "Richmond Heights",
    ],
    "ms": [
        "Jackson", "Gulfport", "West Gulfport", "Southaven", "Hattiesburg",
        "Biloxi", "Meridian", "Olive Branch", "Tupelo", "Greenville",
        "Horn Lake", "Pearl", "Madison", "Starkville", "Clinton",
        "Ridgeland", "Brandon", "Columbus", "Vicksburg", "Oxford",
        "Pascagoula", "Laurel", "Gautier", "Ocean Springs", "Clarksdale",
        "Long Beach", "Hernando", "Greenwood", "Natchez", "Corinth",
        "Canton", "Moss Point", "Carriere", "Grenada", "McComb",
        "Brookhaven", "Cleveland", "Byram", "D'Iberville", "Yazoo City",
        "West Point", "Petal", "Picayune", "Indianola", "Bay Saint Louis",
        "New Albany", "Booneville", "Flowood", "Diamondhead", "Senatobia",
        "Holly Springs", "Saint Martin", "Holly Springs", "Philadelphia", "Batesville",
        "Kosciusko", "Gulf Hills", "Richland", "Amory", "Waveland",
        "Louisville", "Columbia", "Latimer", "Pontotoc", "West Hattiesburg",
        "Vancleave", "Gulf Park Estates", "Forest", "Pass Christian", "Aberdeen",
        "Ripley", "Saltillo", "Waynesboro", "Crystal Springs", "Carthage",
        "Ellisville", "Wiggins", "Winona", "Magee", "Florence",
        "University", "Leland", "Fulton", "Hazlehurst", "Escatawpa",
        "Pearl River", "Houston", "Tutwiler", "Morton", "Beechwood",
        "Lynchburg", "Water Valley", "Newton", "Baldwyn", "New Hope",
        "Hickory Hills", "Nicholson", "Verona", "Lucedale", "Iuka",
    ],
    "mt": [
        "Billings", "Missoula", "Great Falls", "Bozeman", "Butte",
        "Helena", "Kalispell", "Havre", "Anaconda", "Miles City",
        "Helena Valley Southeast", "Belgrade", "Helena Valley West Central", "Evergreen", "Livingston",
        "Whitefish", "Laurel", "Sidney", "Lockwood", "Lewistown",
        "Glendive", "Orchard Homes", "Columbia Falls", "Polson", "Hamilton",
        "Bigfork", "Dillon", "Lolo", "Hardin", "Helena Valley Northwest",
        "Malmstrom Air Force Base", "Glasgow", "Shelby", "Four Corners", "Cut Bank",
        "Warm Springs", "Helena Valley Northeast", "Deer Lodge", "Wolf Point", "Montana City",
        "Lakeside", "Libby", "Conrad", "North Browning", "Colstrip",
        "Big Sky", "Pablo", "Red Lodge", "East Missoula", "East Helena",
        "Lame Deer", "Columbus", "Baker", "Ronan", "Malta",
        "Townsend", "West Glendive", "Three Forks", "Plentywood", "Stevensville",
        "Forsyth", "Roundup", "Frenchtown", "South Browning", "Choteau",
        "Bonner-West Riverside", "Clancy", "Seeley Lake", "Big Timber", "Helena West Side",
        "Manhattan", "Sun Prairie", "Crow Agency", "Fort Benton", "West Yellowstone",
        "Thompson Falls", "Fort Belknap Agency", "Chinook", "Boulder", "Absarokee",
        "Somers", "Whitehall", "Eureka", "Clinton", "Plains",
        "Scobey", "Browning", "Lincoln", "Harlowton", "White Sulphur Springs",
        "Philipsburg", "Chester", "Superior", "Wibaux", "Circle",
        "Terry", "Broadus", "Jordan", "Stanford", "Ekalaka",
    ],
    "nc": [
        "Charlotte", "Raleigh", "West Raleigh", "Greensboro", "Durham",
        "Winston-Salem", "Fayetteville", "Cary", "Wilmington", "High Point",
        "Asheville", "Greenville", "Concord", "Gastonia", "Jacksonville",
        "Chapel Hill", "Rocky Mount", "Huntersville", "Burlington", "Wilson",
        "Kannapolis", "Apex", "Hickory", "Wake Forest", "Indian Trail",
        "Mooresville", "Goldsboro", "Monroe", "Salisbury", "Holly Springs",
        "Matthews", "New Bern", "Fort Bragg", "Sanford", "Cornelius",
        "Garner", "Thomasville", "Statesville", "Asheboro", "Mint Hill",
        "Fuquay-Varina", "Morrisville", "Kernersville", "Lumberton", "Kinston",
        "Carrboro", "Havelock", "Shelby", "Clemmons", "Lexington",
        "Clayton", "Boone", "Elizabeth City", "Leland", "Lenoir",
        "Morganton", "Hope Mills", "Albemarle", "Pinehurst", "Laurinburg",
        "Eden", "Roanoke Rapids", "Henderson", "Stallings", "Masonboro",
        "Graham", "Harrisburg", "Knightdale", "Murraysville", "Mount Holly",
        "Reidsville", "Hendersonville", "Mebane", "Lewisville", "Southern Pines",
        "Waxhaw", "Piney Green", "Spring Lake", "Newton", "Davidson",
        "Smithfield", "Archdale", "Tarboro", "Lincolnton", "Summerfield",
        "Kings Mountain", "Belmont", "Weddington", "Mount Airy", "Elon",
        "Waynesville", "Washington", "Dunn", "Winterville", "Morehead City",
        "Rockingham", "Myrtle Grove", "Clinton", "Saint Stephens", "Oxford",
    ],
    "nd": [
        "Fargo", "Bismarck", "Grand Forks", "Minot", "West Fargo",
        "Williston", "Dickinson", "Mandan", "Jamestown", "Wahpeton",
        "Devils Lake", "Watford City", "Valley City", "Minot Air Force Base", "Grafton",
        "Lincoln", "Beulah", "Rugby", "Stanley", "Horace",
        "Casselton", "New Town", "Hazen", "Grand Forks Air Force Base", "Bottineau",
        "Lisbon", "Belcourt", "Carrington", "Mayville", "Oakes",
        "Langdon", "Harvey", "Bowman", "Tioga", "Hillsboro",
        "Garrison", "Crosby", "New Rockford", "Park River", "Surrey",
        "Rolla", "Larimore", "Washburn", "Ellendale", "Parshall",
        "Velva", "Hettinger", "Killdeer", "Cavalier", "Fort Totten",
        "Shell Valley", "Burlington", "Cando", "Beach", "Kenmare",
        "Belfield", "Linton", "Thompson", "Cooperstown", "Mohall",
        "Mott", "Napoleon", "Ashley", "Steele", "Lakota",
        "Center", "Towner", "Forman", "Fessenden", "Finley",
        "Bowbells", "McClusky", "Stanton", "Carson", "Minnewaukan",
        "Fort Yates", "Medora", "Sheldon", "Manning", "Amidon",
    ],
    "ne": [
        "Omaha", "Lincoln", "Bellevue", "Grand Island", "Kearney",
        "Fremont", "Hastings", "Norfolk", "North Platte", "Columbus",
        "Papillion", "La Vista", "Scottsbluff", "South Sioux City", "Beatrice",
        "Chalco", "Lexington", "Alliance", "Gering", "Elkhorn",
        "Blair", "York", "McCook", "Nebraska City", "Hillsborough",
        "Seward", "Crete", "Sidney", "Plattsmouth", "Schuyler",
        "Ralston", "Chadron", "Wayne", "Holdrege", "Gretna",
        "Offutt Air Force Base", "Ogallala", "Wahoo", "Aurora", "Falls City",
        "Cozad", "Fairbury", "Waverly", "O'Neill", "Broken Bow",
        "Gothenburg", "West Point", "Auburn", "Minden", "Central City",
        "David City", "Valentine", "Ashland", "Kimball", "Madison",
        "Saint Paul", "Geneva", "Valley", "Milford", "Hickman",
        "Ord", "Imperial", "Syracuse", "Dakota City", "Superior",
        "Gibbon", "Wilber", "Pierce", "Tekamah", "Bennington",
        "Mitchell", "Ainsworth", "Tecumseh", "Albion", "Springfield",
        "Hebron", "Gordon", "Neligh", "Bridgeport", "Stanton",
        "Hartington", "Sutton", "Wymore", "Wakefield", "Ravenna",
        "Wood River", "Sutherland", "Fullerton", "Arlington", "Atkinson",
        "North Bend", "Plainview", "Yutan", "Burwell", "Oakland",
        "Battle Creek", "Wisner", "Louisville", "Terrytown", "Bayard",
    ],
    "nh": [
        "Manchester", "Nashua", "Concord", "East Concord", "Derry Village",
        "Dover", "Rochester", "Salem", "Merrimack", "Keene",
        "Derry", "Portsmouth", "Bedford", "Laconia", "Lebanon",
        "Windham", "Claremont", "Pelham", "Somersworth", "Londonderry",
        "Durham", "Hampton", "Berlin", "Exeter", "Milford",
        "Seabrook", "Hampstead", "Hanover", "Weare", "Franklin",
        "Barrington", "Bow Bog", "Litchfield", "Plaistow", "Gilford",
        "Hollis", "Pembroke", "Hudson", "Swanzey", "Stratham Station",
        "Atkinson", "Kingston", "Rindge", "Sandown", "Hopkinton",
        "South Hooksett", "Suncook", "Newmarket", "New Ipswich", "Rye",
        "Chester", "Auburn", "Northfield", "Moultonborough", "New Boston",
        "Pinardville", "Newport", "North Hampton", "Wakefield", "Ossipee",
        "Brookline", "Epsom", "Barnstead", "Danville", "Haverhill",
        "Newton", "Lee", "Plymouth", "Littleton", "Candia",
        "Deerfield", "East Merrimack", "Hooksett", "Nottingham", "Boscawen",
        "Farmington", "Northwood", "Strafford", "Chesterfield", "Fremont",
        "Tilton", "Greenland", "Brentwood", "Gilmanton", "Sunapee",
        "Goffstown", "Peterborough", "Tilton-Northfield", "Raymond", "Wolfeboro",
        "Rollinsford", "Jaffrey", "Sanbornton", "Tamworth", "Northumberland",
        "Chichester", "New Durham", "North Conway", "Grantham", "Tuftonboro",
    ],
    "nj": [
        "Newark", "Jersey City", "Paterson", "Elizabeth", "Edison",
        "Trenton", "Toms River", "Clifton", "Camden", "Brick",
        "Passaic", "Cherry Hill", "Union City", "Bayonne", "Middletown",
        "East Orange", "North Bergen", "Irvington", "Vineland", "South Vineland",
        "Wayne", "New Brunswick", "Union", "Piscataway", "Jackson",
        "Lakewood", "Hoboken", "West New York", "Perth Amboy", "Plainfield",
        "Parsippany", "Bloomfield", "East Brunswick", "West Orange", "Sayreville",
        "Hackensack", "Bridgewater", "North Brunswick", "Sicklerville", "Sayreville Junction",
        "Kearny", "Linden", "Mount Laurel", "Marlboro", "Teaneck",
        "Montclair", "Atlantic City", "Hillsborough", "Sewell", "Belleville",
        "Fort Lee", "Ewing", "Pennsauken", "Orange", "Fair Lawn",
        "Garfield", "Willingboro", "Long Branch", "Westfield", "Princeton",
        "Rahway", "Englewood", "Millville", "Livingston", "Bergenfield",
        "Nutley", "Paramus", "West Milford", "Mercerville-Hamilton Square", "Randolph",
        "Ridgewood", "Bridgeton", "Maplewood", "Cliffside Park", "Lodi",
        "Vincentown", "South Plainfield", "Carteret", "Mahwah", "Old Bridge",
        "Scotch Plains", "South Old Bridge", "Cranford", "Hillside", "North Plainfield",
        "Somerset", "Summit", "Roselle", "Basking Ridge", "Pleasantville",
        "Palisades Park", "Bayville", "Elmwood Park", "Millburn", "Lyndhurst",
        "Sparta", "Woodbridge", "Glassboro", "Secaucus", "Maple Shade",
    ],
    "nm": [
        "Albuquerque", "Las Cruces", "Enchanted Hills", "Rio Rancho", "Santa Fe",
        "Roswell", "Farmington", "South Valley", "Clovis", "Hobbs",
        "Alamogordo", "Carlsbad", "Gallup", "Sunland Park", "Los Lunas",
        "Chaparral", "Deming", "Las Vegas", "Artesia", "Los Alamos",
        "Portales", "Lovington", "North Valley", "Española", "Silver City",
        "Anthony", "Grants", "Bernalillo", "Socorro", "Corrales",
        "Shiprock", "Kirtland", "Ruidoso", "Bloomfield", "Belen",
        "Zuni Pueblo", "Raton", "Aztec", "Eldorado at Santa Fe", "Truth or Consequences",
        "Los Ranchos de Albuquerque", "Lee Acres", "Lee Acres", "Taos", "White Rock",
        "Los Chavez", "Tucumcari", "Placitas", "Rio Communities", "Meadow Lake",
        "El Cerro Mission", "Santa Teresa", "Paradise Hills", "University Park", "Bosque Farms",
        "La Cienega", "Edgewood", "Peralta", "Milan", "Vado",
        "Sandia Heights", "Chimayo", "Eunice", "Holloman Air Force Base", "El Cerro",
        "Tularosa", "Agua Fria", "West Hammond", "Clayton", "Dulce",
        "Santa Teresa", "Santa Rosa", "Ruidoso Downs", "Lordsburg", "Ranchos de Taos",
        "Jarales", "Santo Domingo Pueblo", "San Felipe Pueblo", "Crownpoint", "Bayard",
        "Cannon Air Force Base", "Jal", "Valencia", "Flora Vista", "San Ysidro",
        "Navajo", "Pojoaque", "Mesilla", "Tome", "Thoreau",
        "Nambe", "Moriarty", "Jemez Pueblo", "Arroyo Seco", "La Mesilla",
        "Questa", "Radium Springs", "La Luz", "Waterflow", "Upper Fruitland",
    ],
    "nv": [
        "Las Vegas", "Henderson", "Reno", "North Las Vegas", "Paradise",
        "Sunrise Manor", "Spring Valley", "Enterprise", "Sparks", "Carson City",
        "Whitney", "Pahrump", "Winchester", "Summerlin South", "Elko",
        "Fernley", "Sun Valley", "Mesquite", "Boulder City", "Spanish Springs",
        "Spring Creek", "Gardnerville Ranchos", "Dayton", "Incline Village", "Cold Springs",
        "Fallon", "Winnemucca", "Laughlin", "Moapa Valley", "Johnson Lane",
        "Gardnerville", "Indian Hills", "Silver Springs", "Lemmon Valley", "West Wendover",
        "Ely", "Battle Mountain", "Hawthorne", "Nellis Air Force Base", "Yerington",
        "Minden", "Tonopah", "Carlin", "Kingsbury", "Sandy Valley",
        "Lovelock", "Stagecoach", "Smith Valley", "Golden Valley", "Topaz Ranch Estates",
        "East Valley", "Verdi", "Bunkerville", "Mogul", "Wells",
        "Jackpot", "McGill", "Caliente", "Alamo", "Smith",
        "Moapa Town", "Beatty", "Pioche", "Virginia City", "Eureka",
        "Goldfield",
    ],
    "ny": [
        "New York City", "Brooklyn", "Queens", "Manhattan", "The Bronx",
        "Staten Island", "Buffalo", "Upper West Side", "Jamaica", "Rochester",
        "Yonkers", "East Flatbush", "East New York", "Washington Heights", "Astoria",
        "Borough Park", "Syracuse", "Sunset Park", "Sheepshead Bay", "Amherst",
        "Harlem", "East Harlem", "Elmhurst", "Bushwick", "Gravesend",
        "Corona", "Albany", "Richmond Hill", "Fordham", "West Albany",
        "Flatbush", "Chinatown", "Canarsie", "Greenburgh", "New Rochelle",
        "South Ozone Park", "Cheektowaga", "Kings Bridge", "Brownsville", "Ridgewood",
        "Mount Vernon", "Forest Hills", "Jackson Heights", "Bayside", "Parkchester",
        "Schenectady", "Park Slope", "Flatlands", "East Village", "Utica",
        "Financial District", "Brentwood", "Bensonhurst", "Coney Island", "White Plains",
        "Clay", "Morningside Heights", "Hempstead", "Cypress Hills", "Ozone Park",
        "Briarwood", "Wakefield", "Queens Village", "Levittown", "Irondequoit",
        "Mott Haven", "Troy", "Sunnyside", "Niagara Falls", "Maspeth",
        "Binghamton", "Hell's Kitchen", "West Seneca", "Rego Park", "Freeport",
        "West Babylon", "Henrietta", "Woodside", "Hicksville", "Morris Heights",
        "Far Rockaway", "Kensington", "Coram", "Manhattan Valley", "East Meadow",
        "Valley Stream", "Kew Gardens Hills", "Whitestone", "Clifton Park", "Brighton",
        "Woodhaven", "Commack", "Greenpoint", "Central Islip", "Dyker Heights",
        "Glendale", "Throgs Neck", "New City", "Long Beach", "Elmont",
    ],
    "oh": [
        "Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron",
        "Dayton", "Parma", "Canton", "Youngstown", "Lorain",
        "Hamilton", "Springfield", "Kettering", "Elyria", "Lakewood",
        "Cuyahoga Falls", "Middletown", "Newark", "Euclid", "Mentor",
        "Mansfield", "Beavercreek", "Dublin", "Cleveland Heights", "Strongsville",
        "Fairfield", "Findlay", "Warren", "Lancaster", "Grove City",
        "Westerville", "Huber Heights", "Delaware", "Lima", "Reynoldsburg",
        "Marion", "Boardman", "Upper Arlington", "Stow", "Brunswick",
        "Gahanna", "Collinwood", "Hilliard", "Fairborn", "Mason",
        "North Ridgeville", "Westlake", "Massillon", "North Olmsted", "Bowling Green",
        "North Royalton", "Kent", "Austintown", "Garfield Heights", "Shaker Heights",
        "Wooster", "Medina", "Barberton", "Xenia", "Green",
        "Troy", "Zanesville", "Sandusky", "Athens", "Riverside",
        "Trotwood", "Centerville", "Glenville", "Avon Lake", "Solon",
        "Marysville", "Maple Heights", "Willoughby", "Avon", "Hudson",
        "Oxford", "Alliance", "Wadsworth", "South Euclid", "Chillicothe",
        "Perrysburg", "Sidney", "Piqua", "Lebanon", "Portsmouth",
        "Rocky River", "Ashland", "Parma Heights", "Oregon", "Miamisburg",
        "Norwood", "Painesville", "Pickerington", "Broadview Heights", "White Oak",
        "Sylvania", "Berea", "Twinsburg", "Mayfield Heights", "Brook Park",
    ],
    "ok": [
        "Oklahoma City", "Tulsa", "Norman", "Broken Arrow", "Lawton",
        "Edmond", "Moore", "Midwest City", "Enid", "Stillwater",
        "Muskogee", "Bartlesville", "Owasso", "Shawnee", "Yukon",
        "Ardmore", "Ponca City", "Bixby", "Duncan", "Del City",
        "Jenks", "Sapulpa", "Mustang", "Sand Springs", "Bethany",
        "Altus", "Claremore", "El Reno", "McAlester", "Ada",
        "Durant", "Tahlequah", "Chickasha", "Miami", "Glenpool",
        "Woodward", "Elk City", "Okmulgee", "Choctaw", "Weatherford",
        "Guymon", "Guthrie", "Warr Acres", "Clinton", "Coweta",
        "Pryor Creek", "Newcastle", "The Village", "Poteau", "Wagoner",
        "Pryor", "Sallisaw", "Blanchard", "Skiatook", "Cushing",
        "Seminole", "Catoosa", "Piedmont", "Idabel", "Blackwell",
        "Tuttle", "Grove", "Anadarko", "Noble", "Tecumseh",
        "Collinsville", "Purcell", "Pauls Valley", "Harrah", "Henryetta",
        "Holdenville", "Vinita", "Hugo", "Lone Grove", "Alva",
        "Perry", "Sulphur", "Kingfisher", "Sayre", "McLoud",
        "Marlow", "Verdigris", "Bristow", "Slaughterville", "Broken Bow",
        "Fort Gibson", "Pocola", "Spencer", "Stilwell", "Madill",
        "Park Hill", "Nichols Hills", "Nowata", "Frederick", "Hobart",
        "Pawhuska", "Roland", "Hominy", "Dewey", "Wewoka",
    ],
    "or": [
        "Portland", "Eugene", "Salem", "Gresham", "Hillsboro",
        "Beaverton", "Bend", "Medford", "Springfield", "Corvallis",
        "Albany", "Tigard", "Aloha", "Lake Oswego", "Keizer",
        "Grants Pass", "Oregon City", "McMinnville", "Redmond", "Tualatin",
        "West Linn", "Woodburn", "Forest Grove", "Newberg", "Wilsonville",
        "Roseburg", "Klamath Falls", "Ashland", "Milwaukie", "Bethany",
        "Lents", "Hayesville", "Sherwood", "Altamont", "Happy Valley",
        "Central Point", "Canby", "Hermiston", "Pendleton", "Troutdale",
        "Oak Grove", "Lebanon", "Coos Bay", "Four Corners", "The Dalles",
        "Dallas", "Cedar Mill", "Oatfield", "La Grande", "Saint Helens",
        "Agate Beach", "Cornelius", "Gladstone", "Oak Hills", "Ontario",
        "Damascus", "Sandy", "Newport", "Monmouth", "Cottage Grove",
        "Silverton", "Baker City", "North Bend", "Astoria", "Prineville",
        "Rockcreek", "Fairview", "Sweet Home", "Independence", "Molalla",
        "Eagle Point", "Florence", "Lincoln City", "Cedar Hills", "West Haven-Sylvan",
        "White City", "Stayton", "Sutherlin", "Hood River", "Green",
        "Jennings Lodge", "Milton-Freewater", "Umatilla", "Kenton", "North Portland",
        "Scappoose", "Clackamas", "Garden Home-Whitford", "Madras", "West Slope",
        "Seaside", "Brookings", "Talent", "Sheridan", "West Haven",
        "Roseburg North", "Raleigh Hills", "Junction City", "Winston", "Warrenton",
    ],
    "pa": [
        "Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading",
        "Scranton", "Bethlehem", "Bensalem", "Lancaster", "Center City",
        "Abington", "Levittown", "Havertown", "Harrisburg", "Wharton",
        "Whitman", "Oxford Circle", "Altoona", "Penn Hills", "York",
        "State College", "Wilkes-Barre", "Olney", "West Oak Lane", "Norristown",
        "Chester", "Cobbs Creek", "Somerton", "Mount Lebanon", "Bustleton",
        "Overbrook", "Bethel Park", "Wayne", "Radnor", "Williamsport",
        "Monroeville", "Cranberry Township", "Holmesburg", "Drexel Hill", "Port Richmond",
        "Plum", "Back Mountain", "Easton", "Pennsport", "Rhawnhurst",
        "Lebanon", "Whitehall Township", "Hazleton", "Lawndale", "Frankford",
        "Springfield", "Pottstown", "New Castle", "Logan", "Rittenhouse",
        "Allison Park", "Wissinoming", "Chambersburg", "Murrysville", "West Mifflin",
        "Haddington", "Johnstown", "King of Prussia", "West Chester", "Baldwin",
        "Hartranft", "Fox Chase", "Kingsessing", "McKeesport", "Upper Saint Clair",
        "Carlisle", "East Mount Airy", "Limerick", "Tacony", "Hunting Park",
        "Juniata Park", "University City", "Nicetown-Tioga", "Elmwood", "Point Breeze",
        "Parkwood Manor", "Phoenixville", "Lansdale", "Lower Moyamensing", "Fishtown",
        "Hermitage", "Strawberry Mansion", "Wilkinsburg", "Willow Grove", "Hanover",
        "Fullerton", "Horsham", "Grays Ferry", "Ogontz", "West Norriton",
        "Bloomsburg", "Greensburg", "Franklin Park", "Hershey", "Allegheny West",
    ],
    "ri": [
        "Providence", "Warwick", "Cranston", "Pawtucket", "East Providence",
        "Woonsocket", "Coventry", "Cumberland", "North Providence", "South Kingstown",
        "West Warwick", "Johnston", "North Kingstown", "Newport", "Bristol",
        "Smithfield", "Lincoln", "Central Falls", "Westerly", "Portsmouth",
        "Middletown", "Barrington", "Narragansett", "East Greenwich", "Newport East",
        "Valley Falls", "Warren", "North Smithfield", "North Scituate", "Greenville",
        "Wakefield-Peacedale", "Charlestown", "Hopkinton", "Cumberland Hill", "Tiverton",
        "Kingston", "Exeter", "West Greenwich", "Jamestown", "Foster",
        "Pascoag", "Narragansett Pier", "Chepachet", "Hope Valley", "Harrisville",
        "Ashaway", "Bradford", "Melville", "New Shoreham",
    ],
    "sc": [
        "Columbia", "Charleston", "North Charleston", "Mount Pleasant", "Rock Hill",
        "Greenville", "Summerville", "Sumter", "Goose Creek", "Hilton Head Island",
        "Florence", "Spartanburg", "Hilton Head", "Myrtle Beach", "Aiken",
        "Greer", "Anderson", "Mauldin", "Greenwood", "North Augusta",
        "Taylors", "Saint Andrews", "Conway", "Easley", "Simpsonville",
        "Wade Hampton", "Lexington", "Socastee", "Hanahan", "Bluffton",
        "West Columbia", "North Myrtle Beach", "Clemson", "Seven Oaks", "Berea",
        "Gantt", "Five Forks", "Dentsville", "Ladson", "Fort Mill",
        "Cayce", "Orangeburg", "Beaufort", "Red Hill", "Red Hill",
        "Gaffney", "Port Royal", "Irmo", "Parker", "Forest Acres",
        "Newberry", "Oak Grove", "Moncks Corner", "Red Bank", "Tega Cay",
        "Woodfield", "Garden City", "Laurens", "Georgetown", "Little River",
        "Lancaster", "Lake Wylie", "Clinton", "Bennettsville", "Fountain Inn",
        "Seneca", "Sangaree", "Boiling Springs", "Oak Grove", "Union",
        "York", "Sans Souci", "Hartsville", "Powdersville", "Murrells Inlet",
        "Lugoff", "Camden", "Burton", "Lake City", "Marion",
        "Dillon", "Welcome", "Centerville", "Valley Falls", "Homeland Park",
        "Darlington", "James Island", "Laurel Bay", "Belvedere", "Cheraw",
        "Clover", "Chester", "Lake Murray of Richland", "Batesburg-Leesville", "Hardeeville",
        "Centerville", "Walterboro", "Abbeville", "Central", "Piedmont",
    ],
    "sd": [
        "Sioux Falls", "Rapid City", "Aberdeen", "Brookings", "Watertown",
        "Mitchell", "Yankton", "Pierre", "Huron", "Spearfish",
        "Vermillion", "Brandon", "Box Elder", "Rapid Valley", "Ellsworth Air Force Base",
        "Madison", "Sturgis", "Belle Fourche", "Harrisburg", "Tea",
        "Dell Rapids", "Hot Springs", "Mobridge", "Canton", "Pine Ridge",
        "Milbank", "Hartford", "Lead", "Blackhawk", "Winner",
        "North Sioux City", "Dakota Dunes", "Colonial Pine Hills", "Sisseton", "Chamberlain",
        "Redfield", "Flandreau", "North Spearfish", "Lennox", "Summerset",
        "Fort Pierre", "Elk Point", "Beresford", "North Eagle Butte", "Springfield",
        "Custer", "Volga", "Webster", "Wagner", "Rosebud",
        "Groton", "Parkston", "Miller", "Crooks", "Salem",
        "Eagle Butte", "Oglala", "Freeman", "Fort Thompson", "Clear Lake",
        "Platte", "Deadwood", "Gregory", "Britton", "Lemmon",
        "Mission", "Garretson", "Gettysburg", "Baltic", "De Smet",
        "Porcupine", "Martin", "Clark", "Tyndall", "Parker",
        "Ipswich", "Wessington Springs", "Lake Andes", "Howard", "Highmore",
        "Philip", "Faulkton", "Plankinton", "Kadoka", "Armour",
        "Woonsocket", "Onida", "Selby", "Alexandria", "Burke",
        "White River", "Dupree", "Timber Lake", "Murdo", "Leola",
        "Hayti", "Buffalo", "Bison", "Kennebec", "McIntosh",
    ],
    "tn": [
        "Nashville", "New South Memphis", "Memphis", "Knoxville", "Chattanooga",
        "Clarksville", "Murfreesboro", "East Chattanooga", "Franklin", "Cordova",
        "Jackson", "Johnson City", "Bartlett", "Hendersonville", "Kingsport",
        "Collierville", "Smyrna", "Cleveland", "Brentwood", "Germantown",
        "Hermitage", "Columbia", "Spring Hill", "La Vergne", "Gallatin",
        "Cookeville", "Mount Juliet", "Brentwood Estates", "Lebanon", "Morristown",
        "Oak Ridge", "Maryville", "Bristol", "Ellendale", "Farragut",
        "Shelbyville", "East Ridge", "Tullahoma", "Goodlettsville", "Springfield",
        "Dyersburg", "Sevierville", "Dickson", "East Brainerd", "Greeneville",
        "Elizabethton", "McMinnville", "Athens", "Soddy-Daisy", "Middle Valley",
        "Lakeland", "Portland", "Red Bank", "Arlington", "Lewisburg",
        "Crossville", "White House", "Millington", "Martin", "Seymour",
        "Collegedale", "Union City", "Lawrenceburg", "Manchester", "Paris",
        "Clinton", "Bloomingdale", "Brownsville", "Christiana", "Chuckey",
        "Alcoa", "Lenoir City", "Atoka", "Covington", "Winchester",
        "Signal Mountain", "Jefferson City", "Fairview", "Humboldt", "Ripley",
        "Lexington", "Milan", "Harrison", "Pulaski", "Oakland",
        "LaFollette", "Dayton", "Fayetteville", "Savannah", "Fairfield Glade",
        "Nolensville", "Colonial Heights", "South Cleveland", "Newport", "Greenbrier",
        "Church Hill", "Millersville", "Green Hill", "Henderson", "Harriman",
    ],
    "tx": [
        "Houston", "San Antonio", "Dallas", "Fort Worth", "Austin",
        "El Paso", "Arlington", "Corpus Christi", "Plano", "Laredo",
        "Lubbock", "Garland", "Irving", "Cypress", "Amarillo",
        "Grand Prairie", "Brownsville", "McKinney", "Frisco", "Pasadena",
        "Mesquite", "Killeen", "McAllen", "Carrollton", "Midland",
        "Waco", "Denton", "Abilene", "Round Rock", "Beaumont",
        "Odessa", "Richardson", "Pearland", "College Station", "Wichita Falls",
        "Lewisville", "Tyler", "San Angelo", "Alief", "League City",
        "Allen", "The Woodlands", "Sugar Land", "Edinburg", "Mission",
        "Longview", "Bryan", "Pharr", "Baytown", "Missouri City",
        "Temple", "Flower Mound", "New Braunfels", "North Richland Hills", "Conroe",
        "Victoria", "Cedar Park", "Atascocita", "Harlingen", "Celina",
        "Mansfield", "Georgetown", "San Marcos", "Rowlett", "Leander",
        "Pflugerville", "Port Arthur", "Spring", "Euless", "University of Texas",
        "DeSoto", "Grapevine", "The Trails of Frisco", "Galveston", "Bedford",
        "Cedar Hill", "Texas City", "Wylie", "Keller", "Haltom City",
        "Burleson", "Schertz", "Rockwall", "The Colony", "Coppell",
        "Huntsville", "Sherman", "Duncanville", "Weslaco", "Hurst",
        "Lancaster", "Friendswood", "Little Elm", "Channelview", "Texarkana",
        "San Juan", "Mission Bend", "Lufkin", "Del Rio", "Kyle",
    ],
    "ut": [
        "Salt Lake City", "West Valley City", "Provo", "West Jordan", "Orem",
        "Sandy Hills", "Sandy", "Ogden", "Layton", "Saint George",
        "South Jordan", "Millcreek", "Taylorsville", "Lehi", "Logan",
        "Murray", "Draper", "Bountiful", "Riverton", "Pleasant Grove",
        "Roy", "Spanish Fork", "South Jordan Heights", "Kearns", "Cottonwood Heights",
        "Tooele", "Midvale", "Springville", "Holladay", "Herriman",
        "Clearfield", "Kaysville", "Cedar City", "American Fork", "Syracuse",
        "Eagle Mountain", "Magna", "Saratoga Springs", "South Salt Lake", "Washington",
        "Farmington", "Clinton", "East Millcreek", "North Salt Lake", "Payson",
        "Brigham City", "North Ogden", "Highland", "South Ogden", "Centerville",
        "Hurricane", "West Haven", "Oquirrh", "Woods Cross", "Vernal",
        "Bluffdale", "Lindon", "Smithfield", "Santaquin", "West Point",
        "Cedar Hills", "Alpine", "North Logan", "Canyon Rim", "Grantsville",
        "Pleasant View", "Mapleton", "Heber City", "Washington Terrace", "Riverdale",
        "Price", "Little Cottonwood Creek Valley", "Tremonton", "Hooper", "Park City",
        "Hyrum", "Ivins", "Summit Park", "Richfield", "Salem",
        "Providence", "Roosevelt", "South Weber", "Ephraim", "Santa Clara",
        "Mount Olympus", "Farr West", "Nibley", "Plain City", "Enoch",
        "Harrisville", "Fruit Heights", "Snyderville", "Nephi", "West Bountiful",
        "White City", "Moab", "Sunset", "Stansbury park", "Perry",
    ],
    "va": [
        "Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Arlington",
        "Newport News", "Alexandria", "East Hampton", "Hampton", "Roanoke",
        "Portsmouth Heights", "Portsmouth", "Suffolk", "South Suffolk", "Lynchburg",
        "Centreville", "Dale City", "West Lynchburg", "Reston", "Harrisonburg",
        "Leesburg", "McLean", "Charlottesville", "Tuckahoe", "Blacksburg",
        "Ashburn", "Danville", "Manassas", "Lake Ridge", "Burke",
        "Annandale", "Mechanicsville", "Linton Hall", "Oakton", "Oak Hill",
        "Petersburg", "Springfield", "West Falls Church", "Fredericksburg", "Sterling",
        "Winchester", "Salem", "Cave Spring", "Short Pump", "Herndon",
        "Staunton", "South Riding", "Fairfax", "Baileys Crossroads", "Chantilly",
        "Lincolnia", "West Springfield", "Hopewell", "Christiansburg", "Waynesboro",
        "Chester", "Woodlawn", "Rose Hill", "Tysons", "Montclair",
        "Lorton", "Midlothian", "Meadowbrook", "Franconia", "Colonial Heights",
        "Culpeper", "Radford", "Idylwood", "Bristol", "Laurel",
        "Vienna", "Bon Air", "Buckhall", "Sudley", "Wolf Trap",
        "Fort Hunt", "Cherry Hill", "Hybla Valley", "Manassas Park", "Highland Springs",
        "Great Falls", "Merrifield", "Front Royal", "Williamsburg", "Bull Run",
        "East Highland Park", "Glen Allen", "Hollins", "Groveton", "Falls Church",
        "Martinsville", "Kings Park West", "Brandermill", "Newington", "Mount Vernon",
        "Broadlands", "Timberlake", "Poquoson", "Fairfax Station", "Dranesville",
    ],
    "vt": [
        "Burlington", "South Burlington", "Colchester", "Rutland", "Essex Junction",
        "Hartford", "Bennington", "Barre", "Williston", "Montpelier",
        "St Johnsbury", "Brattleboro", "Winooski", "Saint Albans", "Middlebury (village)",
        "Saint Johnsbury", "Morristown", "Lyndon", "Rockingham", "Newport",
        "Hinesburg", "Stowe", "Springfield", "Charlotte", "Pownal",
        "Bellows Falls", "Chester", "Ferrisburgh", "West Brattleboro", "Vergennes",
        "Clarendon", "Swanton", "White River Junction", "White River Junction VA Medical Center", "Fair Haven",
        "Manchester Center", "Northfield", "Windsor", "Morrisville", "Bristol",
        "West Rutland", "Randolph", "Milton", "Waterbury", "Middlesex",
        "Starksboro", "Londonderry", "Wilder", "Moretown", "Brandon",
        "North Bennington", "Poultney", "Castleton", "Johnson", "Dover",
        "Pawlet", "Addison", "Richford", "Hardwick", "Jericho",
        "Enosburg Falls", "Danby", "Lunenburg", "Lincoln", "Chelsea",
        "Chittenden", "Mount Holly", "South Barre", "Bridport", "Arlington",
        "Townshend", "Montgomery", "Lyndonville", "Williamstown", "Salisbury",
        "Leicester", "Washington", "Mendon", "Jamaica", "Woodstock",
        "North Hero", "Hyde Park", "Guildhall", "Newfane",
    ],
    "wa": [
        "Seattle", "Tri-Cities", "Spokane", "Tacoma", "Vancouver",
        "Bellevue", "Kent", "Everett", "Renton", "Federal Way",
        "Spokane Valley", "Yakima", "Kirkland", "Bellingham", "Kennewick",
        "Auburn", "Pasco", "Marysville", "Redmond", "Lakewood",
        "Olympia", "Shoreline", "Richland", "South Hill", "Sammamish",
        "Burien", "Lacey", "City of Sammamish", "Bothell", "Edmonds",
        "Puyallup", "Bremerton", "Lynnwood", "Longview", "Issaquah",
        "Parkland", "Mount Vernon", "West Lake Sammamish", "Wenatchee", "University Place",
        "Pullman", "Walla Walla", "Des Moines", "Lake Stevens", "East Hill-Meridian",
        "SeaTac", "Spanaway", "North Creek", "Opportunity", "Maple Valley",
        "Mercer Island", "Bainbridge Island", "Graham", "Picnic Point-North Lynnwood", "Inglewood-Finn Hill",
        "Oak Harbor", "Cottage Lake", "Moses Lake", "Kenmore", "Camas",
        "Mukilteo", "West Lake Stevens", "Mountlake Terrace", "Silver Firs", "Eastmont",
        "Mill Creek", "Tukwila", "Bonney Lake", "Salmon Creek", "Orchards",
        "Port Angeles", "Hazel Dell", "Battle Ground", "Silverdale", "Covington",
        "Tumwater", "Fairwood", "Ellensburg", "Columbia City", "Arlington",
        "Union Hill-Novelty Hill", "Frederickson", "Five Corners", "Anacortes", "Monroe",
        "Centralia", "Bothell West", "Sunnyside", "Aberdeen", "Mill Creek East",
        "Bryn Mawr-Skyway", "Martha Lake", "Washougal", "Elk Plain", "Camano",
        "West Richland", "East Wenatchee", "Port Orchard", "Lynden", "White Center",
    ],
    "wi": [
        "Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine",
        "Appleton", "Waukesha", "Eau Claire", "Oshkosh", "Janesville",
        "West Allis", "La Crosse", "North La Crosse", "Sheboygan", "Wauwatosa",
        "Fond du Lac", "New Berlin", "Wausau", "Brookfield", "Greenfield",
        "Beloit", "Franklin", "Menomonee Falls", "Oak Creek", "Manitowoc",
        "Sun Prairie", "West Bend", "Fitchburg", "Stevens Point", "Superior",
        "Mount Pleasant", "Neenah", "Muskego", "De Pere", "Caledonia",
        "Watertown", "Mequon", "South Milwaukee", "Pleasant Prairie", "Germantown",
        "Howard", "Middleton", "Marshfield", "Onalaska", "Cudahy",
        "Wisconsin Rapids", "Menasha", "Ashwaubenon", "Beaver Dam", "Oconomowoc",
        "Menomonie", "Kaukauna", "Bellevue", "River Falls", "Weston",
        "Whitewater", "Hartford", "Greendale", "Whitefish Bay", "Chippewa Falls",
        "Allouez", "Hudson", "Shorewood", "Waunakee", "Stoughton",
        "Glendale", "Platteville", "Verona", "Fort Atkinson", "Plover",
        "Suamico", "Baraboo", "Brown Deer", "Port Washington", "Richfield",
        "Grafton", "Cedarburg", "Salem", "Waupun", "Two Rivers",
        "Little Chute", "Marinette", "Monroe", "Sussex", "Burlington",
        "Portage", "Oregon", "Elkhorn", "Sparta", "Holmen",
        "Reedsburg", "Somers", "Saint Francis", "Tomah", "Merrill",
        "Hartland", "Shawano", "Sturgeon Bay", "DeForest", "New Richmond",
    ],
    "wv": [
        "Huntington", "Charleston", "Parkersburg", "Morgantown", "Wheeling",
        "Weirton Heights", "Weirton", "Fairmont", "Martinsburg", "Beckley",
        "Clarksburg", "Teays Valley", "South Charleston", "Saint Albans", "Vienna",
        "Bluefield", "Cross Lanes", "Moundsville", "Bridgeport", "Oak Hill",
        "Cheat Lake", "Dunbar", "Elkins", "Nitro", "Pea Ridge",
        "Hurricane", "Princeton", "Charles Town", "Augusta", "Buckhannon",
        "Keyser", "New Martinsville", "Brookhaven", "Grafton", "Ranson",
        "Point Pleasant", "Westover", "Weston", "Barboursville", "Sissonville",
        "Lewisburg", "Ravenswood", "Summersville", "Shannondale", "Pinch",
        "Philippi", "Ripley", "Pleasant Valley", "Blennerhassett", "Kenova",
        "Culloden", "Williamson", "Shady Spring", "Williamstown", "Kingwood",
        "Inwood", "Madison", "Fayetteville", "Follansbee", "Wellsburg",
        "Crab Orchard", "Milton", "Hooverson Heights", "Bethlehem", "Granville",
        "Hinton", "Petersburg", "Paden City", "Chester", "Moorefield",
        "White Sulphur Springs", "Bethlehem", "Winfield", "Craigsville", "Spencer",
        "Bluewell", "Shinnston", "Shepherdstown", "Mannington", "Bradley",
        "Star City", "Richwood", "Welch", "Mineral Wells", "Belington",
        "Daniels", "Saint Marys", "McMechen", "Coal City", "Mount Gay-Shamrock",
        "Harrisville", "Romney", "Stonewood", "Ronceverte", "Alum Creek",
        "Fairlea", "Mallory", "Logan", "Rand", "Montgomery",
    ],
    "wy": [
        "Cheyenne", "Casper", "Gillette", "Laramie", "Rock Springs",
        "Sheridan", "Green River", "Evanston", "Riverton", "Jackson",
        "Cody", "Rawlins", "Lander", "Torrington", "Douglas",
        "Powell", "Ranchettes", "Worland", "Buffalo", "South Greeley",
        "Mills", "Wheatland", "Fox Farm-College", "Newcastle", "Thermopolis",
        "Evansville", "Bar Nunn", "Kemmerer", "Glenrock", "Lovell",
        "North Rock Springs", "Lyman", "Afton", "Pinedale", "Greybull",
        "Wright", "Moose Wilson Road", "Fort Washakie", "South Park", "Saratoga",
        "Antelope Valley-Crestview", "Arapahoe", "Lusk", "Ethete", "Star Valley Ranch",
        "Wilson", "Sleepy Hollow", "Basin", "Mountain View", "Sundance",
        "Guernsey", "Hoback", "Pine Bluffs", "Upton", "Marbleton",
        "Rafter J Ranch", "Moorcroft",
    ],
}


# -------------------------------------------------------------
# RESUME STATE MANAGEMENT
# -------------------------------------------------------------

def load_progress():
    """Load scraping progress from the state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"completed_cities": []}


def save_progress(progress):
    """Save scraping progress to the state file."""
    with open(STATE_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def get_scraped_urls():
    """Load set of profile URLs already in the CSV (for deduplication/resume)."""
    urls = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("Zillow Profile URL"):
                        urls.add(row["Zillow Profile URL"])
        except Exception:
            pass
    return urls

SKIPPED_FILE = "zillow_skipped_urls.txt"

def get_skipped_urls():
    """Load set of profile URLs that were skipped due to <5 sales."""
    urls = set()
    if os.path.exists(SKIPPED_FILE):
        try:
            with open(SKIPPED_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        urls.add(line.strip())
        except Exception:
            pass
    return urls

def save_skipped_url(url):
    """Save a skipped profile URL to the skipped file."""
    try:
        with open(SKIPPED_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")
    except Exception:
        pass


# -------------------------------------------------------------
# CSV OUTPUT
# -------------------------------------------------------------

def save_batch_to_csv(records):
    """Append a batch of records to the output CSV file."""
    if not records:
        return

    file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerows(records)

    print(f"  [SAVED] Saved {len(records)} records to {OUTPUT_FILE}")


# -------------------------------------------------------------
# URL SLUGIFICATION
# -------------------------------------------------------------

def slugify_city(city_name, state_abbr):
    """Convert 'Gulf Shores' + 'al' -> 'gulf-shores-al' for Zillow URLs."""
    slug = city_name.lower().strip()
    slug = re.sub(r"['\.]", "", slug)           # Remove apostrophes, dots
    slug = re.sub(r"[^a-z0-9]+", "-", slug)     # Non-alphanumeric -> hyphen
    slug = slug.strip("-")
    return f"{slug}-{state_abbr}"


# -------------------------------------------------------------
# CAPTCHA DETECTION & SOLVING
# -------------------------------------------------------------

CAPTCHA_INDICATORS = [
    "px-captcha", "press & hold", "press and hold",
    "human verification", "challenge-platform",
    "are you a robot", "verify you are human",
]


def has_captcha(sb):
    """Check if the current page shows a CAPTCHA challenge."""
    try:
        src = sb.get_page_source().lower()
        return any(ind in src for ind in CAPTCHA_INDICATORS)
    except Exception:
        return False


def solve_captcha(sb):
    """
    Attempt to auto-solve CAPTCHA using SeleniumBase, then
    fall back to waiting for manual intervention.
    """
    if not has_captcha(sb):
        return

    print("  [CAPTCHA] CAPTCHA detected! Attempting auto-solve...")

    # Attempt 1: SeleniumBase built-in solvers (uses pyautogui internally)
    for method_name in ["uc_gui_handle_captcha", "uc_gui_click_captcha"]:
        try:
            method = getattr(sb, method_name, None)
            if method:
                method()
                time.sleep(random.uniform(*DELAY_AFTER_CAPTCHA_CHECK))
                if not has_captcha(sb):
                    print("  [OK] CAPTCHA auto-solved!")
                    return
        except Exception as e:
            print(f"  [WARNING] {method_name} failed: {e}")

    # Attempt 2: Wait for manual intervention
    print("  [WAIT] Auto-solve didn't work.")
    print("     Please solve the CAPTCHA manually in the browser window.")
    print("     Waiting up to 120 seconds...")

    for i in range(24):  # 24 x 5s = 120s
        time.sleep(5)
        if not has_captcha(sb):
            print("  [OK] CAPTCHA solved (manual)!")
            return
        if (i + 1) % 6 == 0:
            print(f"     Still waiting... ({(i + 1) * 5}s)")

    print("  [ERROR] CAPTCHA not solved within 120 seconds. Continuing anyway...")


def safe_open(sb, url, max_retries=3):
    """Navigate to a URL with retry logic and CAPTCHA handling."""
    for attempt in range(max_retries):
        try:
            # Use UC reconnect for stealth; fall back to regular open
            try:
                sb.uc_open_with_reconnect(url, reconnect_time=5)
            except (AttributeError, TypeError):
                sb.open(url)

            time.sleep(random.uniform(2, 4))
            solve_captcha(sb)

            # Check for server errors
            try:
                title = (sb.get_title() or "").lower()
            except Exception:
                title = ""
            if "502" in title or "504" in title or "bad gateway" in title:
                raise Exception("Server returned 502/504")

            return True

        except Exception as e:
            if attempt < max_retries - 1:
                wait = 20 * (attempt + 1)
                print(f"  [WARNING] Error loading {url}: {e}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [ERROR] Failed to load {url} after {max_retries} retries.")
                return False


# -------------------------------------------------------------
# LISTING PAGE SCRAPING
# -------------------------------------------------------------

def collect_profile_urls(sb):
    """Extract all agent profile URLs from the current listing page."""
    urls = []
    try:
        links = sb.find_elements("a[href*='/profile/']")
        for link in links:
            href = link.get_attribute("href")
            if href and "/profile/" in href:
                if not href.startswith("http"):
                    href = "https://www.zillow.com" + href
                # Normalize: remove trailing query params and fragments
                href = href.split("?")[0].split("#")[0]
                if href not in urls:
                    urls.append(href)
    except Exception as e:
        print(f"    [WARNING] Error collecting profile URLs: {e}")
    return urls


def detect_max_page(sb):
    """Detect the highest pagination page number on the current page."""
    max_page = 1
    
    # Let page settle so pagination component can render
    import time
    time.sleep(1)
    
    try:
        # Method 1: Look directly at the text inside the Pagination nav element
        for selector in ["nav[class*='Pagination']", "nav[class*='aginat']", "[class*='Pagination']", "[aria-label*='Page']", "nav a"]:
            try:
                elements = sb.find_elements(selector)
                for el in elements:
                    # The pagination component usually has text like "1\n2\n3\n4\n5"
                    text = (el.text or "").strip()
                    if text:
                        # Extract all numbers from the text block
                        numbers = re.findall(r'\b\d+\b', text)
                        for num in numbers:
                            max_page = max(max_page, int(num))
                    
                    # Also fallback to checking hrefs just in case it's an a-tag based layout
                    href = el.get_attribute("href") or ""
                    m = re.search(r'(?:/(\d+)_p/?|\?page=(\d+))', href)
                    if m:
                        val = m.group(1) or m.group(2)
                        max_page = max(max_page, int(val))
            except Exception:
                continue

        # Method 2: Check page source for pagination patterns
        try:
            src = sb.get_page_source()
            for m in re.finditer(r'(?:/(\d+)_p/?|\?page=(\d+))', src):
                val = m.group(1) or m.group(2)
                max_page = max(max_page, int(val))
        except Exception:
            pass

    except Exception:
        pass
    return max_page


# -------------------------------------------------------------
# AGENT PROFILE SCRAPING
# -------------------------------------------------------------

def scrape_profile(sb, url, location):
    """
    Visit an individual agent's Zillow profile page and extract all details.
    Returns a dict with all CSV fields, or None on failure.
    """
    if not safe_open(sb, url):
        return None

    # Wait for the name heading to appear
    try:
        sb.wait_for_element("h1", timeout=15)
    except Exception:
        print(f"    [WARNING] Profile page didn't load: {url}")
        return None

    # We have removed the scrolling logic entirely. 
    # Testing confirmed that Name, Sales, and Phones are loaded immediately in the DOM.
    # This saves ~4 seconds per agent.
    time.sleep(random.uniform(0.5, 1.5))

    # Initialize record
    agent = dict.fromkeys(CSV_HEADERS, "")
    agent["Zillow Profile URL"] = url
    agent["Location"] = location

    # Get the full visible page text for regex extraction
    page_text = ""
    try:
        page_text = sb.get_text("body")
    except Exception:
        pass

    # -- 1. Agent Name --
    try:
        agent["Agent Name"] = sb.get_text("h1").strip()
    except Exception:
        pass

    # -- 2. Office / Realty Name --
    # Zillow shows the office/brokerage right below the agent name (see screenshot)
    # e.g., "FULTON GRACE REALTY"
    for sel in [
        "[class*='office' i]", "[class*='brokerage' i]", "[class*='company' i]",
        "[data-testid*='office']", "[data-testid*='brokerage']",
        "[class*='Office']", "[class*='Brokerage']",
    ]:
        try:
            if sb.is_element_visible(sel):
                text = sb.get_text(sel).strip()
                if text and len(text) < 200 and text != agent["Agent Name"]:
                    agent["Office/Realty"] = text.split("\n")[0].strip()
                    break
        except Exception:
            continue

    # Fallback: Zillow DOM structure traversal
    if not agent["Office/Realty"]:
        try:
            # The h1 (name) is in a div. The next sibling div contains the office info.
            h1_parent = sb.find_element("h1").find_element("xpath", "..")
            next_sibling = h1_parent.find_element("xpath", "following-sibling::div")
            
            if next_sibling:
                lines = [line.strip() for line in next_sibling.text.split("\n") if line.strip()]
                for line in lines:
                    # Ignore badges like "Zillow Premier Agent"
                    if "premier agent" not in line.lower() and "more about" not in line.lower():
                        agent["Office/Realty"] = line
                        break
        except Exception:
            pass

    # -- 3. Sales Last 12 Months --
    m = re.search(
        r'(\d[\d,]*)\s+(?:team\s+)?sales?\s+last\s+12\s+months',
        page_text, re.IGNORECASE
    )
    if m:
        agent["Sales Last 12 Months"] = m.group(1).replace(",", "")

    # -- 4. Total Sales --
    m = re.search(r'(\d[\d,]*)\s+total\s+sales', page_text, re.IGNORECASE)
    if m:
        agent["Total Sales"] = m.group(1).replace(",", "")

    # -- 5. Phone Numbers --
    mobile_phones = []
    office_phones = []
    
    try:
        # Find all tel links
        for link in sb.find_elements("a[href^='tel:']"):
            ph = (link.text or "").strip()
            if not ph:
                ph = (link.get_attribute("href") or "").replace("tel:", "").strip()
            
            if not ph:
                continue
                
            # Try to determine if it's office or mobile by inspecting parent HTML for icons
            try:
                parent = link.find_element("xpath", "..")
                parent_html = parent.get_attribute("outerHTML").lower()
                
                # Zillow's office (building) icon uses SVG rects for windows, or a specific path starting with M24
                if "<rect" in parent_html or "m24 2h8" in parent_html:
                    if ph not in office_phones:
                        office_phones.append(ph)
                else:
                    if ph not in mobile_phones:
                        mobile_phones.append(ph)
            except Exception:
                # If we can't tell, assume mobile/direct
                if ph not in mobile_phones:
                    mobile_phones.append(ph)
                    
    except Exception:
        pass
        
    # Regex fallback if no links found
    if not mobile_phones and not office_phones:
        found_phones = list(dict.fromkeys(
            re.findall(r'\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}', page_text)
        ))
        mobile_phones = found_phones
        
    agent["Mobile Phone"] = "; ".join(mobile_phones)
    agent["Office Phone"] = "; ".join(office_phones)

    # -- 6. Email --
    emails = []
    # Method A: <a href="mailto:..."> links (most reliable)
    try:
        for link in sb.find_elements("a[href^='mailto:']"):
            em = (link.get_attribute("href") or "").replace("mailto:", "").split("?")[0].strip()
            if em and "@" in em and em.lower() not in [e.lower() for e in emails]:
                emails.append(em)
    except Exception:
        pass
    # Method B: Regex fallback
    if not emails:
        found = re.findall(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', page_text)
        emails = [e for e in found
                  if "zillow" not in e.lower() and "zillowgroup" not in e.lower()]
    agent["Email"] = "; ".join(emails)

    # -- 7. Service Areas --
    service = ""
    for sel in [
        "[class*='service-area' i]", "[class*='ServiceArea' i]",
        "[data-testid*='service']", "[class*='serviceArea' i]",
    ]:
        try:
            if sb.is_element_visible(sel):
                text = sb.get_text(sel).strip()
                # Remove the "Service areas (N)" header text
                text = re.sub(r'^Service\s+areas?\s*\(?\d*\)?\s*', '', text, flags=re.I)
                if text:
                    # Convert newlines to comma-separated
                    service = ", ".join(line.strip() for line in text.split("\n") if line.strip())
                    break
        except Exception:
            continue
    # Fallback: regex from page text
    if not service:
        m = re.search(
            r'Service\s+areas?\s*\(?\d*\)?\s*\n([\s\S]*?)(?:\n\s*\n|Team\s+reviews|Team\s+sales|$)',
            page_text, re.IGNORECASE
        )
        if m:
            raw = m.group(1).strip()
            service = ", ".join(line.strip() for line in raw.split("\n") if line.strip())
    agent["Service Areas"] = service

    # -- 8. Website --
    # Strictly look for explicit website links/buttons only.
    # Removed aggressive fallback to avoid scraping ads or random sponsored links.
    for sel in [
        "a[data-testid*='website']", "a[class*='website' i]",
        "[class*='website' i] a", "a[aria-label*='website' i]",
        "a[title*='website' i]"
    ]:
        try:
            if sb.is_element_visible(sel):
                href = sb.get_attribute(sel, "href")
                if href and "zillow.com" not in href.lower():
                    agent["Website"] = href
                    break
        except Exception:
            continue

    return agent


# -------------------------------------------------------------
# OPTIONAL: DISCOVER EXTRA CITIES FROM ZILLOW'S STATE PAGE
# -------------------------------------------------------------

def discover_extra_cities(sb, state_abbr):
    """
    Try navigating to the state-level Zillow page to discover
    additional cities we might have missed in the hardcoded list.
    """
    extra = []
    try:
        state_url = f"{BASE_URL}/{state_abbr}/"
        if safe_open(sb, state_url):
            time.sleep(3)
            links = sb.find_elements(
                f"a[href*='/professionals/real-estate-agent-reviews/'][href*='-{state_abbr}/']"
            )
            for link in links:
                href = link.get_attribute("href") or ""
                m = re.search(
                    r'/real-estate-agent-reviews/(.+)-' + re.escape(state_abbr) + r'/?$',
                    href
                )
                if m:
                    city_name = m.group(1).replace("-", " ").title()
                    if city_name and city_name not in extra:
                        extra.append(city_name)
            if extra:
                print(f"    [SEARCH] Discovered {len(extra)} additional cities from Zillow")
    except Exception:
        pass
    return extra


# -------------------------------------------------------------
# MAIN ORCHESTRATOR
# -------------------------------------------------------------


def get_all_cities_for_state(state_abbr):
    print(f"  [+] Loading curated list of major cities for {state_abbr.upper()}...")
    cities = list(CITIES.get(state_abbr.lower(), []))
    if not cities:
        pass
    else:
        print(f"  [+] Loaded {len(cities)} major cities in {state_abbr.upper()}!")
    return cities

def main():
    print("=" * 70)
    print("  ZILLOW REAL ESTATE AGENT SCRAPER")
    print("=" * 70)
    print()
    print("  [WARNING]  Keep the browser window VISIBLE (not minimized).")
    print("     The CAPTCHA solver needs to control the mouse cursor.")
    print("     You can use other windows, just don't minimize the browser.")
    print()

    progress = load_progress()
    scraped_urls = get_scraped_urls()
    skipped_urls = get_skipped_urls()
    known_urls = scraped_urls.union(skipped_urls)
    completed = progress.get("completed_cities", [])

    print(f"  Already scraped: {len(scraped_urls)} agents in CSV")
    print(f"  Already skipped (<5 sales): {len(skipped_urls)} agents")
    print(f"  Completed cities: {len(completed)}")
    print()

    
    # INTERACTIVE PROMPT
    state_abbr = input("  Enter State Abbreviation to scrape (e.g., AL, IL, TX): ").strip().lower()
    if not state_abbr:
        print("  Invalid state abbreviation. Exiting.")
        return
        
    state_name = input("  Enter State Full Name (e.g., Alabama, Illinois): ").strip().title()
    if not state_name:
        state_name = state_abbr.upper()
        
    with SB(uc=True, headed=True, chromium_arg="--disable-gpu") as sb:

        STATES_TO_SCRAPE_DYNAMIC = {state_name: state_abbr}
        
        for state_name, state_abbr in STATES_TO_SCRAPE_DYNAMIC.items():
            cities = get_all_cities_for_state(state_abbr)
            if not cities:
                print(f"\n  [!] No curated list found for {state_abbr.upper()}.")
                print(f"  [+] Falling back to searching the entire state on Zillow: {state_name}")
                cities = [state_name]

            print(f"\n{'=' * 70}")
            print(f"  STATE: {state_name} ({state_abbr.upper()}) - {len(cities)} cities")
            print(f"{'=' * 70}")

            # Try to discover additional cities from Zillow
            extra = discover_extra_cities(sb, state_abbr)
            for c in extra:
                if c not in cities:
                    cities.append(c)
            if extra:
                print(f"  Total cities (including discovered): {len(cities)}")

            state_agent_count = 0

            for city_idx, city in enumerate(cities):
                city_key = f"{city}, {state_abbr.upper()}"

                # Skip already-completed cities
                if city_key in completed:
                    print(f"\n  [SKIP]  [{city_idx + 1}/{len(cities)}] "
                          f"Skipping {city_key} (already done)")
                    continue

                print(f"\n  [CITY]  [{city_idx + 1}/{len(cities)}] {city_key}")
                print(f"  {'-' * 50}")

                city_slug = slugify_city(city, state_abbr)
                city_base_url = f"{BASE_URL}/{city_slug}/"

                # -- Phase 1: Collect profile URLs from all listing pages --
                all_profile_urls = []
                page = 1

                while True:
                    if MAX_PAGES_PER_CITY and page > MAX_PAGES_PER_CITY:
                        break

                    page_url = city_base_url if page == 1 else f"{city_base_url}?page={page}"
                    print(f"    [PAGE] Listing page {page}: {page_url}")

                    if not safe_open(sb, page_url):
                        if page == 1:
                            print(f"    [WARNING] Could not load listing for {city_key}")
                        break

                    time.sleep(random.uniform(*DELAY_BETWEEN_PAGES))

                    # Scroll down to trigger lazy-loading of agent cards
                    try:
                        sb.execute_script(
                            f"window.scrollTo(0, {random.randint(600, 1200)});"
                        )
                        time.sleep(random.uniform(0.5, 1.0))
                        sb.execute_script(
                            "window.scrollTo(0, document.body.scrollHeight);"
                        )
                        time.sleep(random.uniform(0.5, 1.0))
                    except Exception:
                        pass

                    urls = collect_profile_urls(sb)

                    if not urls:
                        if page == 1:
                            print(f"    [WARNING] No agents found for {city_key}")
                        else:
                            print(f"    [OK] End of listings at page {page}")
                        break

                    print(f"    Found {len(urls)} agent profiles")
                    all_profile_urls.extend(urls)

                    # Detect last page from pagination
                    max_pg = detect_max_page(sb)
                    if page >= max_pg:
                        print(f"    [OK] Last page reached ({page}/{max_pg})")
                        break

                    page += 1

                # Deduplicate and filter out already-scraped agents
                all_profile_urls = list(dict.fromkeys(all_profile_urls))
                new_urls = [u for u in all_profile_urls if u not in known_urls]

                if not all_profile_urls:
                    # Mark city done even if no agents (don't retry on resume)
                    completed.append(city_key)
                    save_progress({"completed_cities": completed})
                    continue

                print(
                    f"\n    [STATS] Total: {len(all_profile_urls)} profiles, "
                    f"{len(new_urls)} new to scrape"
                )

                # -- Phase 2: Visit each profile page --
                batch = []
                location_str = f"{city}, {state_abbr.upper()}"

                for i, prof_url in enumerate(new_urls):
                    print(f"    [AGENT] [{i + 1}/{len(new_urls)}] ", end="")

                    try:
                        record = scrape_profile(sb, prof_url, location_str)
                        if record:
                            sales_str = record.get("Sales Last 12 Months", "")
                            try:
                                sales_num = int(sales_str) if sales_str else 0
                            except:
                                sales_num = 0
                                
                            if sales_num > 3:
                                batch.append(record)
                                known_urls.add(prof_url)
                                name = record.get("Agent Name", "?")
                                office = record.get("Office/Realty", "")
                                print(f"[OK] {name} ({sales_num} sales)" + (f" | {office}" if office else ""))
                            else:
                                print(f"[SKIP] 3 or fewer sales ({sales_num} sales)")
                                save_skipped_url(prof_url)
                                known_urls.add(prof_url)
                        else:
                            print(f"[WARNING] Skipped (no data - will retry on resume)")
                    except Exception as e:
                        print(f"[ERROR] Error: {e}")

                    # Incremental save every BATCH_SAVE_SIZE agents
                    if len(batch) >= BATCH_SAVE_SIZE:
                        save_batch_to_csv(batch)
                        state_agent_count += len(batch)
                        batch = []

                    time.sleep(random.uniform(*DELAY_BETWEEN_PROFILES))

                # Save any remaining records in the batch
                if batch:
                    save_batch_to_csv(batch)
                    state_agent_count += len(batch)

                # Mark this city as completed
                completed.append(city_key)
                save_progress({"completed_cities": completed})
                print(f"    [OK] {city_key} complete!")

            print(f"\n  [STATS] {state_name} done! "
                  f"{state_agent_count} new agents scraped this run.")

    # Final summary
    final_count = 0
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            final_count = sum(1 for _ in f) - 1  # minus header

    print(f"\n{'=' * 70}")
    print(f"  SCRAPING COMPLETE!")
    print(f"  Total agents in CSV: {max(final_count, 0)}")
    print(f"  Output file: {OUTPUT_FILE}")
    print(f"  To reset progress and re-scrape, delete: {STATE_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
