import os
import pandas as pd

from birds.settings import load_settings


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

