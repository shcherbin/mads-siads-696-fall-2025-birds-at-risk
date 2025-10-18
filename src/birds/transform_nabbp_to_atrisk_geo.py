import os
import glob
import pandas as pd
import numpy as np
import polars as pl


from birds.source_data.nabbp import LookupTables
from birds.settings import load_settings, get_relative_path
from birds.transform_nabbp_to_band_agg import get_nabbp_data_files,load_nabbp_data, write_parquet_file

settings = load_settings()
lookup = LookupTables()


nabbp_data_path = get_relative_path(settings.nabbp_data_path)
augmented_data_path =get_relative_path(settings.augmented_data_base_path)
dest_data_path = get_relative_path(settings.augmented_atrisk_events)

print(f'dest_data_path: {dest_data_path}')
print(f'source_data_path: {nabbp_data_path}')
print(f'augmented_data_path: {augmented_data_path}')



def load_atrisk_index():
    
    df = pd.read_csv(f'{augmented_data_path}/nabbp_file_species_index_redlist.csv')
    return df




def clean_atrisk_data(df: pd.DataFrame) -> pd.DataFrame:
    # remove null atrisk
    df = df.dropna(subset=['atRisk'])

    # narrow to columns of interest
    df = df[['species_id','atRisk']]
    return df




def clean_napbbp_data(df: pl.DataFrame) -> pl.DataFrame:
    # remove any rows without lat/lon
    df = df.filter(pl.col('lat_dd').is_not_null() & pl.col('lon_dd').is_not_null())

    # remove any rows without species_id
    df = df.filter(pl.col('species_id').is_not_null())

    # narrow to columns of interest
    df = df.select(['species_id','lat_dd','lon_dd','event_year','event_type']) #,'event_type','iso_country','iso_subdivision'

    # narrow to event_year >= 2020
    #df = df.filter(pl.col('event_year') >= 2020)

    # filter to only event_type = 'E' - making events more random based on banding reports 
    df = df.filter(pl.col('event_type') == 'E')

    # remove rows with 0 lat or 0 lon
    df = df.filter((pl.col('lat_dd') != 0) & (pl.col('lon_dd') != 0))
    return df



def join_nabbp_with_atrisk(nabbp_df: pl.DataFrame, species_df: pd.DataFrame) -> pl.DataFrame:
    # convert species_df to polars
    species_pl_df = pl.from_pandas(species_df)

    # join on species_id
    joined_df = nabbp_df.join(species_pl_df, on='species_id', how='inner')

    return joined_df




def process_nabbp_data(file_ids=None):
    """
    To limit the number of files and data processed:
    specify file ids with 2 digit string ex '01','02'
    if None, process all files.
    """

    species_df = load_atrisk_index()
    species_df = clean_atrisk_data(species_df)

    all_files = get_nabbp_data_files()

    if file_ids:
        files = [f for f in all_files if any(f"NABBP_2025_grp_{fid}.csv.gz" in f for fid in file_ids)]
    else:
        files = all_files

    for file in files:
        print(f"Processing file: {file}")
        df = load_nabbp_data(file)
        df = clean_napbbp_data(df)
        df = join_nabbp_with_atrisk(df, species_df)

        print(f'\trows: {df.shape[0]}, atRiskRows: {df.filter(pl.col("atRisk")==True).shape[0]}, notAtRiskRows: {df.filter(pl.col("atRisk")==False).shape[0]}, species: {df.select(pl.col("species_id").n_unique()).item()}\n')

        dest_file = os.path.join(dest_data_path, f"atrisk_{os.path.basename(file).replace('.csv.gz','.parquet')}")
        write_parquet_file(df, dest_file)
        #return df
    return 

if __name__ == "__main__":
    process_nabbp_data(file_ids=None)