from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
import time
import math
import random

console = Console()

ASCII_SATELLITE = """
        ___                *
       / /\ \             *
      / /  \ \   ____    *
     /_/____\ \_/___/\\ *
     \\ \\   / /    \\/
      \\_\\_/_/    
"""

def show_intro():
    console.print(ASCII_SATELLITE, style="bold blue")
    console.print("[bold yellow]Welcome to Satellite Tracker v1[/bold yellow]\n")

def choose_location(default_lat, default_lon):
    console.print(f"\n 𖡡 Current location set: [green]{default_lat}, {default_lon}[/green]")
    choice = Prompt.ask("Want to use this location?", choices=["y", "n"], default="y")
    if choice == "y":
        return default_lat, default_lon
    else:
        # Validate latitude input
        while True:
            try:
                lat_input = Prompt.ask("enter the new Latitude", default=str(default_lat))
                lat = float(lat_input)
                if -90 <= lat <= 90:
                    break
                else:
                    console.print("[bold red]Latitude must be between -90 and 90 degrees![/bold red]")
            except ValueError:
                console.print("[bold red]Invalid input! Please enter a valid number for latitude.[/bold red]")
        
        # Validate longitude input
        while True:
            try:
                lon_input = Prompt.ask("enter the new Longitude", default=str(default_lon))
                lon = float(lon_input)
                if -180 <= lon <= 180:
                    break
                else:
                    console.print("[bold red]Longitude must be between -180 and 180 degrees![/bold red]")
            except ValueError:
                console.print("[bold red]Invalid input! Please enter a valid number for longitude.[/bold red]")
        
        return lat, lon

def show_categories(categories):
    table = Table(title="available categories")
    table.add_column("Number", justify="center")
    table.add_column("Category", style="cyan")
    for idx, cat in enumerate(categories, 1):
        table.add_row(str(idx), cat['name'])
    console.print(table)

    choice = Prompt.ask("\nchoose a category", choices=[str(i) for i in range(1, len(categories) + 1)])
    return categories[int(choice) - 1]['id']

# def radar_animation(duration=5):
#     console.print("\n[bold cyan]ativando radar...[/bold cyan]")
#     spinner = ['|', '/', '-', '\\']
#     start_time = time.time()
    
#     with Live(refresh_per_second=10) as live:
#         while (time.time() - start_time) < duration:
#             for frame in spinner:
#                 radar_display = Text(f"Radar Ativo: {frame}", style="bold green")
#                 live.update(radar_display)
#                 time.sleep(0.1)
def generate_radar_frame(angle, satellites):
    size = 21  # tamanho do radar (tem que ser ímpar?)
    center = size // 2
    display = ""

    for y in range(size):
        for x in range(size):
            dx = x - center
            dy = y - center
            distance = math.sqrt(dx**2 + dy**2)

            # Desenhar borda do radar
            if abs(distance - center + 1) < 1:
                display += "•"
            # Desenhar ponto central
            elif x == center and y == center:
                display += "[bold red]✹[/bold red]"
            # Desenhar linha do radar
            elif distance < center - 1 and abs(math.atan2(dy, dx) - math.radians(angle)) < 0.2:
                display += "[bold green]/[/bold green]"
            # Desenhar satélites captados
            elif (x, y) in satellites:
                display += "[yellow]•[/yellow]"
            else:
                display += " "
        display += "\n"
    return Panel(display, title="Radar", border_style="bold green") # primo gpt sempre na back xD

def radar_real(duration=10):
    console.print("\n[bold cyan]🛰︎ starting radar...[/bold cyan]")
    start_time = time.time()
    angle = 0

    size = 21
    center = size // 2
    num_sats = random.randint(5, 8)
    satellites = [(random.randint(0, size-1), random.randint(0, size-1)) for _ in range(num_sats)]

    with Live(refresh_per_second=15, screen=True) as live:
        while (time.time() - start_time) < duration:
            frame = generate_radar_frame(angle, satellites)
            live.update(frame)
            angle = (angle + 5) % 360  # gira o radar
            time.sleep(0.05)