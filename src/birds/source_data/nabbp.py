import os
import pandas as pd
import polars as pl

from typing import Union
from birds.settings import load_settings



class DataTables:
    SCHEMA = pl.Schema({
        'band': pl.Utf8,
        'original_band': pl.Utf8, 
        'other_bands': pl.Utf8,
        'event_type': pl.Utf8,
        'event_date': pl.Utf8,
        'event_day': pl.Int32,
        'event_month': pl.Int32,
        'event_year': pl.Int32,
        'iso_country': pl.Utf8,
        'iso_subdivision': pl.Utf8,
        'lat_dd': pl.Float64,
        'lon_dd': pl.Float64,
        'coordinates_precision_code': pl.Utf8,
        'band_type_code': pl.Utf8,
        'species_name': pl.Utf8,
        'species_id': pl.Int32,
        'bird_status': pl.Utf8,
        'extra_info_code': pl.Utf8,
        'age_code': pl.Utf8,
        'sex_code': pl.Utf8,
        'permit': pl.Utf8,
        'band_status_code': pl.Utf8,
        'how_obtained_code': pl.Utf8,
        'who_obtained_code': pl.Utf8,
        'reporting_method': pl.Utf8,
        'present_condition': pl.Utf8,
        'min_age_at_enc': pl.Float64,
        'record_source': pl.Utf8,
        'record_id': pl.Utf8
    })

    def __init__(self):
        self.__settings = load_settings()
        self.__species_df = None

    @property
    def species_index(self) -> pd.DataFrame:
        if self.__species_df is None:
            self.__species_df = pd.read_csv(os.path.join(self.__settings.augmented_data_base_path, 'nabbp_file_species_index.csv'), header=0)
        return self.__species_df

    def load_data_by_species_names(self, names: list[str], columns: list[str] = None, 
                                   materialize: bool = False) -> Union[pl.LazyFrame, pl.DataFrame]:
        """Selects the appropriate NABBP data files based on species names and loads the data.
        """
        species_df = self.species_index[self.species_index['SPECIES_NAME'].isin(names)]

        species_ids = species_df['species_id'].unique().tolist()
        file_paths = [
            os.path.join(self.__settings.nabbp_data_path, f"NABBP_2025_grp{suffix}.csv.gz")
            for suffix in species_df['grp_table_suffix'].unique().tolist()
        ]
        
        print(f"Species IDs: {species_ids}")
        print("Loading data from files:")
        for path in file_paths:
            print(f"\t - {path}")

        lazy_frame = (
             pl.scan_csv(source=file_paths, low_memory=True, schema=self.SCHEMA)
                .filter(pl.col('species_id').is_in(species_ids))
        )

        if columns is not None:
            lazy_frame = lazy_frame.select(columns)

        if materialize:
            return lazy_frame.collect().to_pandas()
        
        return lazy_frame


class LookupTables:
    def __init__(self):
        self.__settings = load_settings()
        self.nabbp_lookups_path = self.__settings.nabbp_lookups_path
    
    def __read_lookup_table(self, filename: str) -> pd.DataFrame:
        return pd.read_csv(os.path.join(self.nabbp_lookups_path, filename), header=0)
    
    @property
    def age(self) -> pd.DataFrame:
        return self.__read_lookup_table('age.csv')

    @property
    def band_status(self) -> pd.DataFrame:
        return self.__read_lookup_table('band_status.csv')

    @property
    def band_type(self) -> pd.DataFrame:
        return self.__read_lookup_table('band_type.csv')

    @property
    def bird_status(self) -> pd.DataFrame:
        return self.__read_lookup_table('bird_status.csv')

    @property
    def coordinates_precision(self) -> pd.DataFrame:
        return self.__read_lookup_table('coordinates_precision.csv')

    @property
    def country_state(self) -> pd.DataFrame:
        return self.__read_lookup_table('country_state.csv')

    @property
    def event_type(self) -> pd.DataFrame:
        return self.__read_lookup_table('event_type.csv')

    @property
    def extra_info(self) -> pd.DataFrame:
        return self.__read_lookup_table('extra_info.csv')

    @property
    def how_obtained(self) -> pd.DataFrame:
        return self.__read_lookup_table('how_obtained.csv')

    @property
    def inexact_dates(self) -> pd.DataFrame:
        return self.__read_lookup_table('inexact_dates.csv')

    @property
    def present_condition(self) -> pd.DataFrame:
        return self.__read_lookup_table('present_condition.csv')

    @property
    def record_source(self) -> pd.DataFrame:
        return self.__read_lookup_table('record_source.csv')

    @property
    def reporting_method(self) -> pd.DataFrame:
        return self.__read_lookup_table('reporting_method.csv')

    @property
    def sex(self) -> pd.DataFrame:
        return self.__read_lookup_table('sex.csv')

    @property
    def species(self) -> pd.DataFrame:
        return self.__read_lookup_table('species.csv')

    @property
    def who_obtained(self) -> pd.DataFrame:
        return self.__read_lookup_table('who_obtained.csv')

