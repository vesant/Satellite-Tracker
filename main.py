from click import prompt
import requests
import time
from ascii_ui import show_intro, choose_location, show_categories, radar_real #, radar_animation
from notifier import send_notification
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from datetime import datetime, timezone
# if anything is in portuguese, let me know so i can assist you with that! (english is not my main language)

console = Console()

# === configs ===
API_KEY = 'xxxxxx-xxxxxx-xxxxxx-xxxx' # put your api from n2yo
DEFAULT_LAT = 1111 # put yours
DEFAULT_LON = -1111 # put yours

# === important functions ===
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
    response = requests.get(url)
    try:
        data = response.json()
        #print("DEBUG RESPONSE:", data)  # debug
        return data['above']
    except Exception as e:
        console.print(f"[bold red]error in API response: {e}[/bold red]")
        return []

def get_passes(satellite_id, lat, lon):
    url = f"https://api.n2yo.com/rest/v1/satellite/radiopasses/{satellite_id}/{lat}/{lon}/0/1/20/&apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['passes']
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
    for sat in satellites:
        table.add_row(sat['satname'], str(sat['satid']))
    console.print(table)

    selected_sat = Prompt.ask("\nenter the ID of the satellite you want to track")

    passes = get_passes(selected_sat, lat, lon)

    if passes:
        for p in passes:
            if p['maxEl'] < 20:
                continue  # skips passes with low elevation, comment if you need!

            start_time = utc_to_local(p['startUTC'])
            max_time = utc_to_local(p['maxUTC'])
            end_time = utc_to_local(p['endUTC'])

            console.print(f"\n🛰︎ Satélite: [cyan]{selected_sat}[/cyan]")
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
