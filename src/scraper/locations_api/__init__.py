import polars as pl


def get_locations() -> pl.DataFrame:
    countries = pl.read_csv(
        "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/csv/countries.csv",
        columns=["id", "iso2"],
    )
    states = pl.read_csv(
        "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/csv/states.csv",
        columns=["id", "name", "country_id"],
    )
    cities = pl.read_csv(
        "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/csv/cities.csv",
        columns=["name", "state_id", "latitude", "longitude"],
    )

    countries = countries.filter(pl.col("iso2") == "BR")

    states_by_country = countries.join(
        states, left_on="id", right_on="country_id", how="inner"
    )

    cities_by_states_by_countries = states_by_country.join(
        cities, left_on="id_right", right_on="state_id", how="inner"
    )

    cities_by_states_by_countries = cities_by_states_by_countries.sort(
        ["name_right", "name", "iso2"]
    )

    cities_by_states_by_countries = cities_by_states_by_countries.with_columns(
        (pl.col("name_right") + "," + pl.col("name") + "," + pl.col("iso2")).alias(
            "location"
        )
    )

    df_cities = cities_by_states_by_countries.select(
        ["location", "latitude", "longitude"]
    )

    return df_cities
