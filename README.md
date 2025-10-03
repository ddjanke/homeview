# HomeView - Family Home Management System

A touch-friendly web application designed for Raspberry Pi Zero W that helps families manage their daily schedules, chores, todos, and weather information.

## Features

- **📅 Calendar**: Weekly calendar view with Google Calendar integration
- **🧹 Chores**: Grid-based chore tracking with hold-to-complete safety
- **✅ Todos**: Priority-based task management with Google Sheets sync
- **🌤️ Weather**: Current conditions and 5-day forecast
- **📱 Touch-Friendly**: Optimized for large touch screens
- **🔒 Safety**: Hold-to-complete interactions prevent accidental touches

## 🚀 Quick Start

### GitHub Repository

This project is available on GitHub for easy cloning and collaboration:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/homeview.git
cd homeview

# Follow the setup instructions below
```

### Prerequisites

- Python 3.8+
- Raspberry Pi Zero W (or any Linux system)
- Google account for Calendar and Sheets integration
- OpenWeatherMap API key for weather data

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd homeview
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google API credentials**
   ```bash
   # Copy the example file
   cp credentials/google_credentials.json.example credentials/google_credentials.json
   
   # Edit with your Google API credentials
   nano credentials/google_credentials.json
   ```

4. **Set up Weather API**
   ```bash
   # Copy the example file
   cp credentials/weather_config.json.example credentials/weather_config.json
   
   # Edit with your OpenWeatherMap API key and location
   nano credentials/weather_config.json
   ```

5. **Set environment variables (optional)**
   ```bash
   export WEATHER_API_KEY="your_openweathermap_api_key"
   export WEATHER_LAT="40.7128"
   export WEATHER_LON="-74.0060"
   export WEATHER_CITY="New York"
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Configuration

### Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API and Google Sheets API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON file
6. Place it in `credentials/google_credentials.json`

### Google Sheets Setup

1. Create a new Google Sheet
2. Name the first sheet "Chores" with columns:
   - A: Name
   - B: Assigned To
   - C: Frequency (daily/weekly/monthly)
   - D: Day of Week (Su/M/Tu/W/Th/F/Sa)
   - E: Completed (TRUE/FALSE)

3. Create a second sheet "Todos" with columns:
   - A: Title
   - B: Description
   - C: Priority (1-10)
   - D: Due Date (YYYY-MM-DD)
   - E: Completed (TRUE/FALSE)

4. Share the sheet with your Google account
5. Note the Sheet ID from the URL

### Weather API Setup

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Update `credentials/weather_config.json` with your API key and location

## Usage

### Navigation

- Use the tab navigation at the top to switch between features
- All interactions are touch-friendly for large screens

### Calendar

- View your weekly schedule
- Navigate between weeks using arrow buttons
- Events are color-coded by category
- Current day is highlighted

### Chores

- View chores organized by person
- Hold the "Hold to Update" button and tap chores to mark complete
- Completed chores move to the end of the list
- Use "Sync from Sheets" to update from Google Sheets
- Use "Reset for Today" to reset daily chores

### Todos

- View todos sorted by priority (highest first)
- Hold the "Hold to Update" button and tap todos to mark complete
- Add new todos using the "Add Todo" button
- Edit todos by clicking the edit icon
- Delete todos by clicking the trash icon

### Weather

- View current weather conditions
- See 5-day forecast
- Check for weather alerts
- Use "Refresh" to update data

## Safety Features

### Hold-to-Complete

To prevent accidental touches, both chores and todos require:
1. Hold down the "Hold to Update" button
2. Tap the item you want to complete
3. Visual feedback shows progress
4. Item is marked complete when hold duration is reached

## Raspberry Pi Optimization

The application is optimized for Raspberry Pi Zero W:

- **Memory Usage**: < 200MB RAM
- **CPU Usage**: Minimal background processing
- **Storage**: < 100MB application footprint
- **Load Time**: < 3 seconds initial page load
- **Responsiveness**: < 500ms for user interactions

## Development

### Project Structure

```
homeview/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Flask route handlers
│   ├── services/        # External API integrations
│   ├── static/          # CSS, JS, images
│   └── templates/       # HTML templates
├── credentials/         # API credentials
├── config.py           # Configuration
├── run.py              # Application entry point
└── requirements.txt    # Python dependencies
```

### Running in Development

```bash
python run.py
```

### Running in Production

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 1 -b 0.0.0.0:5000 run:app
```

### Creating a System Service

Create `/etc/systemd/system/homeview.service`:

```ini
[Unit]
Description=HomeView Web App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/homeview
ExecStart=/usr/local/bin/gunicorn -w 1 -b 0.0.0.0:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable homeview
sudo systemctl start homeview
```

## Troubleshooting

### Common Issues

1. **Google API Authentication**
   - Ensure credentials file is properly formatted
   - Check that APIs are enabled in Google Cloud Console
   - Verify OAuth scopes are correct

2. **Weather API Issues**
   - Verify API key is valid
   - Check location coordinates are correct
   - Ensure internet connection is working

3. **Database Issues**
   - Check file permissions on SQLite database
   - Ensure sufficient disk space
   - Verify database file is not corrupted

4. **Performance Issues**
   - Monitor memory usage with `htop`
   - Check CPU usage during operations
   - Ensure adequate cooling for Raspberry Pi

### Logs

Check application logs for errors:

```bash
# If running with systemd
sudo journalctl -u homeview -f

# If running manually
python run.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review the requirements document
- Open an issue on GitHub

---

**HomeView** - Making family management simple and touch-friendly! 🏠✨
