import polars as pl

from src.scraper.locations_api import config


def get_locations() -> pl.DataFrame:
    def read_csv(file_name: str, columns: list[str]) -> pl.DataFrame:
        return pl.read_csv(config.get_csv_url(file_name), columns=columns)

    countries = read_csv('countries', ['id', 'iso2'])
    states = read_csv('states', ['id', 'name', 'country_id'])
    cities = read_csv('cities', ['name', 'state_id', 'latitude', 'longitude'])

    countries = countries.filter(pl.col('iso2') == 'BR')

    states_with_country_info = countries.join(
        states,
        left_on='id',
        right_on='country_id',
        how='inner',
    )

    cities_with_state_and_country_info = states_with_country_info.join(
        cities,
        left_on='id_right',
        right_on='state_id',
        how='inner',
    )

    cities_with_state_and_country_info = (
        cities_with_state_and_country_info.sort(
            ['name_right', 'name', 'iso2'],
        ).with_columns(
            (
                pl.col('name_right')
                + ','
                + pl.col('name')
                + ','
                + pl.col('iso2')
            ).alias('location'),
        )
    )

    return cities_with_state_and_country_info.select(
        ['location', 'latitude', 'longitude'],
    )
