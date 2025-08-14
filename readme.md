# OLX Parser

OLX Real Estate Parser

## Architecture

```bash
src/
├── core/                   # Core business logic and configuration
│   ├── config.py           # Application configuration and constants
│   ├── models.py           # Pydantic data models with full typing
│   └── app_factory.py      # Dependency injection factory
├── services/               # Business logic services
│   ├── olx_service.py      # Main OLX scraping logic
│   ├── telegram_service.py # Telegram bot messaging
│   └── image_service.py    # Image processing and collages
├── adapters/               # External service adapters
│   └── database.py         # Database interface and SQLite implementation
└── utils/                  # Utility functions
    └── logging_utils.py    # Logging configuration
```

## Installation

1. **Clone and setup the project:**

   ```bash
   cd olx-parser
   python -m venv env
   env\Scripts\activate  # Windows
   # source env/bin/activate  # Linux/Mac
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Telegram bot:**
   - Update `src/core/config.py` with your bot token and channel ID
   - Or set environment variables (recommended for production)

## Usage

## Configuration

Key configuration options in `src/core/config.py`:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHANNEL_ID`: Target channel ID
- `SCHEDULER_INTERVAL_MINUTES`: Scraping frequency
- `SEARCH_PARAMS`: OLX search criteria

```py
SEARCH_PARAMS = {
      "offset": 0,
      "limit": 50,          # Number of results per page
      "category_id": 1147,  # Real estate category
      "region_id": 5,       # Tashkent region
      "district_id": 26,    # Tashkent district
      "city_id": 5,         # Tashkent city
      "distance": 10,       # Search radius in km
      "currency": "UYE",    # Currency for prices
      "sort_by": "created_at:desc",
      "filter_float_price:from": 100,  # Minimum price
      "filter_float_price:to": 400,    # Maximum price
      "filter_float_number_of_rooms:from": 1,  # Minimum number of rooms
      "filter_float_number_of_rooms:to": 6,    # Maximum number of rooms
      "filter_refiners": "",
  }
```

### Run the application

```bash
python app.py
```

## Contributing

### Development commands

```bash
# Type checking
mypy src/

# Code formatting
black src/
isort src/
```
