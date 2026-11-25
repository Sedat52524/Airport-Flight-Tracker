import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# Connected to live Aviationstack Flight API v1
BASE_URL = "https://api.aviationstack.com/v1"
API_KEY = os.getenv("AVIATIONSTACK_API_KEY", "YOUR_API_KEY_HERE")

# The 10 Swedish airports (Swedavia)
AIRPORTS = {
    "1": ("ARN", "Stockholm Arlanda Airport"),
    "2": ("GOT", "Göteborg Landvetter Airport"),
    "3": ("BMA", "Stockholm Bromma Airport"),
    "4": ("MMX", "Malmö Airport"),
    "5": ("LLA", "Luleå Airport"),
    "6": ("UME", "Umeå Airport"),
    "7": ("OSD", "Åre Östersund Airport"),
    "8": ("VBY", "Visby Airport"),
    "9": ("RNB", "Ronneby Airport"),
    "10": ("KRN", "Kiruna Airport")
}

SWEDISH_TZ = ZoneInfo("Europe/Stockholm")


def load_destinations():
    """Load city and country mapping strictly from cities_countries.json."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "cities_countries.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Error: Could not find '{file_path}'. Please create cities_countries.json.")
        return {}
    except json.JSONDecodeError as e:
        print(f"[!] Error: Invalid JSON syntax in cities_countries.json ({e}).")
        return {}


DESTINATIONS = load_destinations()


def to_swedish_time(iso_str):
    """Convert ISO timestamp from API to Swedish local time (CET/CEST)."""
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.astimezone(SWEDISH_TZ).strftime("%H:%M (%Y-%m-%d)")
    except ValueError:
        return iso_str


def select_airport():
    """Let the user choose one of the 10 Swedish airports."""
    print("\n--- Select Swedish Airport ---")
    for num, (iata, name) in AIRPORTS.items():
        print(f"  [{num}] {iata} - {name}")
    choice = input("Choose airport (1-10): ").strip()
    return AIRPORTS.get(choice, ("ARN", "Stockholm Arlanda Airport"))


def fetch_flights(iata, flight_type="arrivals"):
    """Fetch live arrivals or departures from Aviationstack API, max 50 flights."""
    today_str = datetime.now(SWEDISH_TZ).strftime("%Y-%m-%d")
    url = f"{BASE_URL}/flights"
    params = {
        "access_key": API_KEY,
        "limit": 50
    }
    if flight_type == "arrivals":
        params["arr_iata"] = iata
    else:
        params["dep_iata"] = iata

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            print(f"\n[!] API Error: {payload['error'].get('message', payload['error'])}\n")
            return
        flights = payload.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"\n[!] Request Error ({url}): {e}\n")
        return

    print("\n" + "=" * 95)
    print(f"LIVE {flight_type.upper()} AT {iata} ({today_str}) — Showing {len(flights)} flights")
    print("=" * 95)
    print(f"{'Flight':<10} {'From/To':<22} {'Country':<15} {'Status':<15} {'Term':<6} {'Baggage':<9} {'Scheduled (Local)'}")
    print("-" * 95)

    for f in flights:
        flight_info = f.get("flight") or {}
        fid = flight_info.get("iata") or flight_info.get("number") or "N/A"

        other_leg = (f.get("departure") if flight_type == "arrivals" else f.get("arrival")) or {}
        local_leg = (f.get("arrival") if flight_type == "arrivals" else f.get("departure")) or {}

        other_iata = other_leg.get("iata") or ""
        other_name = other_leg.get("airport") or other_iata or "Unknown"

        dest_info = DESTINATIONS.get(other_iata, {})
        country = dest_info.get("country") or other_leg.get("timezone", "").split("/")[0] or "International"

        status = (f.get("flight_status") or "scheduled").capitalize()
        terminal = local_leg.get("terminal") or "-"
        baggage = local_leg.get("baggage") or "-"

        sched_local = to_swedish_time(local_leg.get("scheduled"))
        est_local = to_swedish_time(local_leg.get("estimated"))

        time_display = sched_local if (est_local == "N/A" or est_local == sched_local) else f"{sched_local} (Est: {est_local[:5]})"
        print(f"{fid:<10} {other_name[:21]:<22} {country[:14]:<15} {status:<15} {str(terminal):<6} {str(baggage):<9} {time_display}")

    print("=" * 95 + "\n")


def search_flight_number():
    """Search for a specific live flight number via Aviationstack API."""
    flight_num = input("Enter flight IATA number (e.g., SK1420, LH804, DY4315): ").strip().upper()
    url = f"{BASE_URL}/flights"
    params = {"access_key": API_KEY, "flight_iata": flight_num, "limit": 5}

    print(f"\n[*] Searching live API for flight {flight_num}...")
    try:
        res = requests.get(url, params=params, timeout=15)
        res.raise_for_status()
        data = res.json().get("data", [])
        if data:
            print(f"[+] Found {len(data)} live match(es) for {flight_num}:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False) + "\n")
        else:
            print(f"[!] Flight '{flight_num}' was not found in active flights right now.\n")
    except requests.exceptions.RequestException as e:
        print(f"[!] API Error: {e}\n")


def query_endpoint():
    """Query active flights filtered by airport and status."""
    iata, _ = select_airport()
    url = f"{BASE_URL}/flights"
    params = {"access_key": API_KEY, "dep_iata": iata, "flight_status": "active", "limit": 5}
    print(f"\n[*] Querying active departures at {iata}...")

    try:
        res = requests.get(url, params=params, timeout=15)
        print(f"[+] HTTP Status Code: {res.status_code}")
        data = res.json().get("data", [])
        print(f"[+] Returned {len(data)} active flights. First match:")
        if data:
            print(json.dumps(data[0], indent=2, ensure_ascii=False) + "\n")
        else:
            print("    No flights currently airborne from this airport.\n")
    except requests.exceptions.RequestException as e:
        print(f"[!] Query Error: {e}\n")


def check_heartbeat():
    """Verify API connectivity and key validity."""
    url = f"{BASE_URL}/flights"
    params = {"access_key": API_KEY, "limit": 1}
    print(f"\n[*] Testing API Connectivity: {url}")

    try:
        res = requests.get(url, params=params, timeout=15)
        if res.status_code == 200 and "data" in res.json():
            print("[+] HTTP Status: 200 OK | Live Aviationstack API Connected & Key Valid!\n")
        else:
            print(f"[!] HTTP Status: {res.status_code} | Response: {res.text[:200]}\n")
    except requests.exceptions.RequestException as e:
        print(f"[!] Connection Failed: {e}\n")


def test_all_endpoints():
    """Run an automated health check across live Aviationstack query modes."""
    endpoints = [
        ("ARN Arrivals", {"access_key": API_KEY, "arr_iata": "ARN", "limit": 1}),
        ("GOT Departures", {"access_key": API_KEY, "dep_iata": "GOT", "limit": 1}),
        ("Active Query", {"access_key": API_KEY, "flight_status": "active", "limit": 1}),
        ("Heartbeat Check", {"access_key": API_KEY, "limit": 1})
    ]
    print("\n=== Testing Live Aviationstack Flight API Endpoints ===")
    for name, params in endpoints:
        try:
            res = requests.get(f"{BASE_URL}/flights", params=params, timeout=15)
            status_label = "200 OK" if (res.status_code == 200 and "data" in res.json()) else f"ERR {res.status_code}"
            print(f"  [{status_label}] {name:<18} -> {BASE_URL}/flights")
        except requests.exceptions.RequestException as e:
            print(f"  [ERR]    {name:<18} -> {e}")
    print("=======================================================\n")


def main():
    print("==========================================================")
    print("   SWEDISH AIRPORTS LIVE FLIGHT TRACKER (AVIATIONSTACK)   ")
    print(f"   Connected to: {BASE_URL}")
    print("==========================================================")

    while True:
        print("Main Menu (6 Options):")
        print("  [1] View Live Arrivals (10 Swedish Airports)")
        print("  [2] View Live Departures (10 Swedish Airports)")
        print("  [3] Search Flight Number")
        print("  [4] Query Endpoint (Active Flights)")
        print("  [5] Test Heartbeat / API Key")
        print("  [6] Test All 4 Endpoints")
        print("  [0] Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            iata, _ = select_airport()
            fetch_flights(iata, "arrivals")
        elif choice == "2":
            iata, _ = select_airport()
            fetch_flights(iata, "departures")
        elif choice == "3":
            search_flight_number()
        elif choice == "4":
            query_endpoint()
        elif choice == "5":
            check_heartbeat()
        elif choice == "6":
            test_all_endpoints()
        elif choice == "0":
            print("Exiting application. Goodbye!")
            break
        else:
            print("[!] Invalid choice. Please enter 0-6.\n")


if __name__ == "__main__":
    main()