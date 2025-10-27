from click import prompt
import requests
import time
import json
import os
from ascii_ui import show_intro, choose_location, show_categories, radar_real #, radar_animation
from notifier import send_notification
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from datetime import datetime, timezone
from requests.exceptions import Timeout, HTTPError, RequestException
# if anything is in portuguese, let me know so i can assist you with that! (english is not my main language)

console = Console()

# === configs ===
def load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('API_KEY'), config.get('DEFAULT_LAT'), config.get('DEFAULT_LON')
    except FileNotFoundError:
        console.print("[bold red]Error: config.json not found![/bold red]")
        console.print("Please create a config.json file based on config.example.json")
        exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error: Invalid JSON in config.json: {e}[/bold red]")
        exit(1)

API_KEY, DEFAULT_LAT, DEFAULT_LON = load_config()

# === important functions ===
def make_api_request(url, timeout=10):
    """
    Utility function to make API requests with proper error handling.
    
    Args:
        url: The URL to request
        timeout: Timeout in seconds (default: 10)
    
    Returns:
        Response JSON data or None if error occurred
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raises HTTPError for bad status codes
        return response.json()
    except Timeout:
        console.print("[bold red]Error: Request timed out. Please check your internet connection.[/bold red]")
        return None
    except HTTPError as e:
        console.print(f"[bold red]Error: HTTP {e.response.status_code} - {e.response.reason}[/bold red]")
        return None
    except RequestException as e:
        console.print(f"[bold red]Error: Request failed - {e}[/bold red]")
        return None
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error: Invalid JSON response - {e}[/bold red]")
        return None

def utc_to_local(utc_timestamp):
    return datetime.fromtimestamp(utc_timestamp).astimezone() # convert to your local timezone

def get_categories():
    return [
        {'id': 3, 'name': 'Weather Satellites'},
        {'id': 18, 'name': 'Amateur Radio'},
        {'id': 6, 'name': 'Earth Observation'},
        {'id': 1, 'name': 'ISS & Space Stations'},
    ]

def get_satellites_above(lat, lon, category_id):
    search_radius = 90  # degree of search in the sky (best: 90°)
    altitude = 0        # observer altitude (above sea level)

    url = f"https://api.n2yo.com/rest/v1/satellite/above/{lat}/{lon}/{altitude}/{search_radius}/{category_id}/&apiKey={API_KEY}"
    data = make_api_request(url)
    
    if data and 'above' in data:
        return data['above']
    else:
        return []

def get_passes(satellite_id, lat, lon):
    url = f"https://api.n2yo.com/rest/v1/satellite/radiopasses/{satellite_id}/{lat}/{lon}/0/1/20/&apiKey={API_KEY}"
    data = make_api_request(url)
    
    if data and 'passes' in data:
        return data['passes']
    else:
        return []

def main():
    show_intro()
    lat, lon = choose_location(DEFAULT_LAT, DEFAULT_LON)

    #radar_animation(2)
    radar_real(5) # 10sec

    categories = get_categories()
    category_id = show_categories(categories)

    console.print("\n🔍︎ searching for satellites...")
    satellites = get_satellites_above(lat, lon, category_id)

    if not satellites:
        console.print("[bold red]no satellite found![/bold red]")
        return

    table = Table(title="Visible satellites:")
    table.add_column("Name")
    table.add_column("ID")
    
    # Store valid satellite IDs for validation
    valid_sat_ids = []
    for sat in satellites:
        table.add_row(sat['satname'], str(sat['satid']))
        valid_sat_ids.append(str(sat['satid']))
    console.print(table)

    # Validate satellite ID input
    while True:
        selected_sat = Prompt.ask("\nenter the ID of the satellite you want to track")
        if selected_sat in valid_sat_ids:
            break
        else:
            console.print(f"[bold red]Invalid satellite ID! Please choose from the list above.[/bold red]")

    passes = get_passes(selected_sat, lat, lon)

    if passes:
        for p in passes:
            if p['maxEl'] < 20:
                continue  # skips passes with low elevation, comment if you need!

            start_time = utc_to_local(p['startUTC'])
            max_time = utc_to_local(p['maxUTC'])
            end_time = utc_to_local(p['endUTC'])

            console.print(f"\n🛰︎ Satellite: [cyan]{selected_sat}[/cyan]")
            console.print(f"⏱︎ Beginning: [green]{start_time.strftime('%Y-%m-%d %H:%M:%S')}[/green] | ⚠︎ Maximum: {max_time.strftime('%Y-%m-%d %H:%M:%S')} | ☹ End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

            seconds_until_start = p['startUTC'] - int(time.time())
            if 0 < seconds_until_start <= 600:
                send_notification(f"Satellite {selected_sat} is approaching!",
                                f"Will pass at {start_time}")

    else:
        console.print("[bold red]no pass found for this satellite.[/bold red]")

# main
if __name__ == "__main__":
    main()
