# Project Documentation: Reverse Engineering Live Airport Flight Boards

## Project Overview
This project was developed as part of the **APL Project 2026: Reverse Engineer a Result**. The objective was to reverse-engineer how airport arrival and departure boards operate behind the scenes using live REST APIs, identify limitations in raw flight API outputs, and build a structured Python command-line application (`Airport.py`) enriched with local destination data (`cities_countries.json`).

---

## Phase 1: Research Phase (Pre-study)
* **Information Gathering:** We analyzed how Swedish airport flight boards structure live traffic data across 10 major airports (ARN, GOT, BMA, MMX, LLA, UME, OSD, VBY, RNB, and KRN) and studied RESTful flight data architectures (arrivals, departures, active flight queries, and API health checks).
* **Choice of Tools and Technologies:** We selected **Python 3.12** using `requests` for HTTP GET requests, `json` and `os` for reading local destination data, and `datetime` / `zoneinfo` for timezone conversions. We used **Visual Studio Code** for development, **OBS Studio** for screen recording, and **Git/GitHub** for version control.
* **Project Planning:** We broke the task down into clear stages:
  1. Design an interactive CLI menu supporting 10 Swedish airports and multiple live flight query modes.
  2. Limit large flight lists to 50 upcoming/recent flights per query for terminal readability.
  3. Build a local JSON file (`cities_countries.json`) mapping IATA airport codes to cities and countries to enrich raw API responses.
  4. Convert UTC timestamps into Swedish local time (`Europe/Stockholm`).
* **Problems and Solutions during Research:**
  * *Problem:* Raw flight API responses return UTC timestamps and lack clean, human-readable country mappings for every destination IATA code.
  * *Solution:* We created a supplementary JSON dataset (`cities_countries.json`) to map airport codes to full country names and planned automatic conversion to Swedish local time (`CET/CEST`).

---

## Phase 2: Implementation (Execution)
* **How the Work Started:** We set up our project workspace (`Reverse_engineering/Airport`) with `cities_countries.json` and `Airport.py`. When Swedavia's developer portal was unavailable for registering a subscription key, we migrated our live HTTP client to **Aviationstack Flight API v1** (`https://api.aviationstack.com/v1/flights`) using a registered API access key, enabling real-time arrivals and departures for all 10 Swedish airports.
* **Project Structure:** The codebase is organized into two core files and modular functions:
  * `cities_countries.json`: External JSON database mapping 20 Swedish and international IATA codes to cities and countries.
  * `load_destinations()`: Loads country/city metadata strictly from `cities_countries.json` with explicit error handling for missing or malformed JSON files.
  * `to_swedish_time()`: Converts ISO UTC strings from the API into Swedish local time (`CET/CEST`).
  * `fetch_flights()`: Sends HTTP GET requests to `https://api.aviationstack.com/v1/flights` filtered by arrival (`arr_iata`) or departure (`dep_iata`) airport, limits output to 50 rows, and formats terminal, baggage claim, and delay estimates.
  * `search_flight_number()`, `query_endpoint()`, `check_heartbeat()`, and `test_all_endpoints()`: Implements flight IATA search, active flight filtering, API key verification, and multi-endpoint health checks.
  * `main()`: Runs an interactive `while True` CLI loop with 6 menu options plus exit.
* **Development of Features:** First, we built the interactive airport selector and tabular display for live arrivals and departures. Next, we added flight number lookup (`flight_iata`), active airborne flight queries (`flight_status=active`), API key connectivity checks, and an automated health check across four query modes.
* **Problems and Solutions during Implementation:**
  * *Problem 1 (External API Portal Unavailable):* Swedavia's developer portal was offline when we tried to generate a live API key.
    * *Solution:* Integrated **Aviationstack Flight API v1** (`https://api.aviationstack.com/v1/flights`) with an environment-backed API key (`AVIATIONSTACK_API_KEY`) to retrieve live real-time flight data for all 10 Swedish airports.
  * *Problem 2 (VS Code Execution Path Bug & Missing `tzdata`):* Folder names with spaces caused `[Errno 22] Invalid argument` in VS Code, and Windows lacked the IANA timezone database for `ZoneInfo("Europe/Stockholm")`.
    * *Solution:* Renamed folders using underscores (`Reverse_engineering/Airport`) and installed `tzdata` via `pip install tzdata`.
  * *Problem 3 (JSON File Path & Country Lookup):* Running the script from a parent folder broke relative paths to `cities_countries.json`.
    * *Solution:* Resolved the JSON path dynamically using `os.path.dirname(os.path.abspath(__file__))` so all 20 airport codes map cleanly to their countries.

---

## Phase 3: Completion & Improvements
* **Finalizing the Project:** We verified all 6 menu options in `Airport.py`, ensuring every flight row displays flight IATA ID, route, country, status, terminal, baggage belt, and both scheduled and estimated Swedish local times.
* **Testing the Complete Solution:** We tested airport selection (1–10), live arrival/departure boards, flight number searches, active flight queries, API connectivity checks, and invalid menu inputs.
* **Improvements and Optimization:** Compared to raw JSON feeds, our application improves readability by grouping data into aligned columns, translating UTC timestamps into local Swedish time, capping output at 50 flights, and enriching routes with country names from `cities_countries.json`.
* **Problems and Solutions during Completion:**
  * *Problem:* Missing fields in live API payloads (such as unassigned terminals, baggage belts, or estimated times) could cause `NoneType` formatting errors.
  * *Solution:* Added safe dictionary fallbacks (`or "-"`, `if not iso_str: return "N/A"`) and API error payload handling (`if "error" in payload:`).

---

## Phase 4: Summary of Problems & Solutions
* **Problem 1: Swedavia developer portal offline (no live API key available)**
  * *Solution:* Migrated the live HTTP integration to **Aviationstack Flight API v1** (`https://api.aviationstack.com/v1/flights`) using a free API access key while keeping all 10 Swedish airports.
* **Problem 2: Missing external packages (`requests` and `tzdata`) and spaces in folder paths**
  * *Solution:* Installed `requests` and `tzdata` via `pip` and renamed project folders to `Reverse_engineering/Airport`.
* **Problem 3: Relative file path issues with `cities_countries.json` and `None` fields in live JSON data**
  * *Solution:* Used `os.path.abspath(__file__)` to locate `cities_countries.json` reliably and added defensive fallbacks for missing terminal, baggage, and timestamp values.
* **Problem 4: Raw UTC timestamps and large JSON payloads**
  * *Solution:* Converted all timestamps to `Europe/Stockholm` local time and capped results at 50 flights per request.

---

## Conclusion
This project successfully reverse-engineered the data flow and structure of live airport flight boards into a functional, well-structured Python application. Through this process, we learned how to integrate real-time REST APIs, enrich external API responses with custom JSON datasets, handle timezone conversions across operating systems, and debug real-world environment and path issues. In the future, the project could be expanded with a web-based dashboard and live airline delay notifications.