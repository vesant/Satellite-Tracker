# Satellite Tracker v1

**Satellite Tracker** is a Python application that allows you to track satellites in real time with a radar-style animated terminal interface!

The project uses the [N2YO API](https://www.n2yo.com/api/) to fetch satellite data, and libraries like `rich`, `requests`, and `plyer` to create an interactive experience with local notifications.

## Features

- Choose a custom location for satellite observation.
- Display an animated ASCII radar in the terminal.
- List available satellite categories.
- Show visible satellites based on location and category.
- Track specific satellites and receive notifications when they are approaching.

## Installation

1. Clone this repository or download the files.

2. Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

3. **Configure your API key and default location:**

   - Copy the example configuration file:
     ```bash
     cp config.example.json config.json
     ```
   
   - Edit `config.json` and add your N2YO API key and default coordinates:
     ```json
     {
       "API_KEY": "your-n2yo-api-key-here",
       "DEFAULT_LAT": 40.0,
       "DEFAULT_LON": -8.0
     }
     ```
   
   - Get your free API key from [N2YO](https://www.n2yo.com/api/)

## How to use

Run this command in your terminal (inside the folder):

```bash
python main.py
```

**Note:** Make sure you have created the `config.json` file with your API key before running the application.
