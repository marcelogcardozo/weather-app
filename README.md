# Weather API Wrapper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FGuilhermeCAz%2Fshurl_django%2Fmain%2Fpyproject.toml&logo=python&label=Python)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-%2300C7B7?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Polars](https://img.shields.io/badge/Polars-%23E03C8A?logo=polars&logoColor=white)](https://pola.rs/)
[![Redis](https://img.shields.io/badge/Redis-%23DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Docker](https://img.shields.io/badge/Docker-%232496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

## Overview

This project is a weather API wrapper that fetches weather data for a specified city. It uses FastAPI for the web framework, Polars for data manipulation, and integrates with external APIs to get weather forecasts and location data.

## Features

- Fetch weather data for a city.
- Cache weather data to improve performance.
- Display weather data using a web interface.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/marcelogcardozo/weather-app.git
   cd weather-app
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Create a .env file with your API keys and preferred redis settings based on the provided [.env.example](.env.example) file.

1. Start the FastAPI server:

   ```bash
   fastapi run src/app/main.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:8000` to access the web interface.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License.
