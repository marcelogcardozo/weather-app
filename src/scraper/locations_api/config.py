BASE_CSV_URL = 'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/csv/'


def get_csv_url(file: str) -> str:
    return f'{BASE_CSV_URL}{file}.csv'
