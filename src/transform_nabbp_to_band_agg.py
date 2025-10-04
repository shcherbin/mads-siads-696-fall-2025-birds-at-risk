## Convert raw NABBP data to band-level aggregated format 
## counting the number of encounters, the days between first and last encounter,
## and the distance between the first and last encounter

import os, glob
import polars as pl
from birds.settings import load_settings, get_relative_path


settings = load_settings()
nabbp_data_path = get_relative_path(settings.nabbp_data_path)
dest_data_path = get_relative_path(settings.augmented_band_agg)
print (f'Source NABBP data path: {nabbp_data_path}')
print (f'Destination path for agg parquet files: {dest_data_path}')


def get_nabbp_data_files():
    nabbp_data_path = get_relative_path(settings.nabbp_data_path)
    files = glob.glob(os.path.join(nabbp_data_path, '*.csv.gz'))
    files = sorted(files)
    return files


def load_nabbp_data(file_path: str) -> pl.DataFrame: #pl.LazyFrame:

    df = pl.read_csv(
        file_path,
        has_header=True,
        ignore_errors=True,
        try_parse_dates=True,
        infer_schema_length=1000,
        null_values=["", "NA", "NaN"],
        schema_overrides={
        },
    )
    return df



def clean_nappb_data(df: pl.DataFrame) -> pl.DataFrame:
    # convert event_date to date
    df = df.with_columns(
        pl.col("event_date").str.strptime(pl.Date, format="%m/%d/%Y", strict=False).alias("event_date"),
    )

    # remove rows with null event_date
    df = df.filter(pl.col("event_date").is_not_null())

    return df




def aggregate_band_data(df: pl.DataFrame) -> pl.DataFrame:
    # aggregate by band: number of events (encounters), number of days between banding and last event (encounter)
    # exclude columns in agg which were mostly null
        

    banding_df = df.filter(pl.col('event_type')=='B')[[
        'record_id','band','event_date', 'species_id', 'iso_country', 
        'iso_subdivision', 'band_type_code', 'bird_status', 'age_code', 
        'sex_code', 'event_type', 'band_status_code','extra_info_code',
        'lat_dd','lon_dd','coordinates_precision_code','permit',
        'record_source',
        ]]
    
    banding_df = banding_df.rename({
        'record_id':'banding_record_id',
        'band':'banding_band', 
        'event_date':'banding_date',
        'species_id':'banding_species_id',
        'iso_country':'banding_iso_country',
        'iso_subdivision':'banding_iso_subdivision',
        'band_type_code':'banding_band_type_code',
        'bird_status':'banding_bird_status',
        'age_code':'banding_age_code',
        'sex_code':'banding_sex_code',
        'event_type':'banding_event_type',
        'band_status_code':'banding_band_status_code',
        'extra_info_code':'banding_extra_info_code',
        'lat_dd':'banding_lat_dd',
        'lon_dd':'banding_lon_dd',
        'coordinates_precision_code':'banding_coordinates_precision_code',
        'permit':'banding_permit',
        'record_source':'banding_record_source',
        })


    # determine max event_type='E' event_date by band for last encounter
    last_event_df = df.filter(pl.col('event_type')=='E').group_by(["band"]).agg([
        pl.len().alias("num_events"),
        pl.max("event_date").alias("last_event_date"),
    ])

    # join event df back to df on band and last_event_date = date to add columns how_obtained_code, who_obtained_code,reporting_method
    last_event_df_full = last_event_df.join(df, 
                                            left_on=['band','last_event_date'], 
                                            right_on=['band','event_date'], 
                                            how='left').select([
        'band','num_events','last_event_date', 'how_obtained_code', 
        'who_obtained_code','reporting_method', 'present_condition',
        'lat_dd','lon_dd','iso_country','iso_subdivision'
    ])
    last_event_df_full = last_event_df_full.rename({
        'band':'last_band',
        'num_events':'num_events',
        'how_obtained_code':'last_how_obtained_code',
        'who_obtained_code':'last_who_obtained_code',
        'reporting_method':'last_reporting_method',
        'present_condition':'last_present_condition',
        'lat_dd':'last_lat_dd', 'lon_dd':'last_lon_dd',
        'iso_country':'last_iso_country',
        'iso_subdivision':'last_iso_subdivision'
    })

    # join banding and last event data
    agg_df = banding_df.join(last_event_df_full, left_on='banding_band', right_on='last_band', how='inner')

    # add new column event_days_span = last_event_date - banding_date
    agg_df = agg_df.with_columns(
        (pl.col("last_event_date") - pl.col("banding_date")).dt.total_days().cast(pl.Int64).alias("event_days_span")
    )
    
    return agg_df




def clean_agg_data(df: pl.DataFrame) -> pl.DataFrame:
    # remove rows with null banding_band
    df = df.filter(pl.col("banding_band").is_not_null())

    # remove rows with null banding_date
    df = df.filter(pl.col("banding_date").is_not_null())

    # remove rows with null last_event_date
    df = df.filter(pl.col("last_event_date").is_not_null())

    # remove rows where last_event_date is before banding_date
    df = df.filter(pl.col("last_event_date") >= pl.col("banding_date"))

    # remove rows where event_days_span is negative (data error)
    df = df.filter(pl.col("event_days_span") >= 0)


    # clean nulls
    df = df.with_columns(
        pl.col('banding_iso_country').fill_null('UNK'),
        pl.col('last_iso_country').fill_null('UNK'),
        pl.col('banding_iso_subdivision').fill_null('UNK'),
        pl.col('last_iso_subdivision').fill_null('UNK'),
        pl.col('banding_band_type_code').fill_null('9999'),
        pl.col("banding_band_status_code").fill_null("UNK"),
        pl.col("last_how_obtained_code").fill_null(9999).cast(pl.Int64),
        pl.col("last_who_obtained_code").fill_null(20).cast(pl.Int64),
        pl.col("last_reporting_method").fill_null(0).cast(pl.Int64),
        pl.col("last_present_condition").fill_null(0).cast(pl.Int64),
        pl.col("banding_bird_status").fill_null("9999"),
        pl.col("banding_extra_info_code").fill_null("99"),
        pl.col("banding_sex_code").fill_null("0"),
        pl.col("last_lat_dd").fill_null(pl.col("banding_lat_dd")),
        pl.col("last_lon_dd").fill_null(pl.col("banding_lon_dd")),
    )

    # explicitly set data type on all columns
    df = df.with_columns(
        pl.col("banding_record_id").cast(pl.Int64),
        pl.col("banding_band").cast(pl.Utf8),
        pl.col("banding_date").cast(pl.Date),
        pl.col("banding_species_id").cast(pl.Int64),
        pl.col("banding_iso_country").cast(pl.Utf8),
        pl.col("banding_iso_subdivision").cast(pl.Utf8),
        pl.col("banding_band_type_code").cast(pl.Utf8),
        pl.col("banding_bird_status").cast(pl.Utf8),
        pl.col("banding_age_code").cast(pl.Utf8),
        pl.col("banding_sex_code").cast(pl.Utf8),
        pl.col("banding_event_type").cast(pl.Utf8),
        pl.col("banding_band_status_code").cast(pl.Utf8),
        pl.col("banding_extra_info_code").cast(pl.Utf8),
        pl.col("banding_lat_dd").cast(pl.Float64),
        pl.col("banding_lon_dd").cast(pl.Float64),
        pl.col("banding_coordinates_precision_code").cast(pl.Utf8),
        pl.col("banding_permit").cast(pl.Utf8),
        pl.col("banding_record_source").cast(pl.Utf8),
        pl.col("num_events").cast(pl.Int64),
        pl.col("last_event_date").cast(pl.Date),
        pl.col("last_how_obtained_code").cast(pl.Int64),
        pl.col("last_who_obtained_code").cast(pl.Int64),
        pl.col("last_reporting_method").cast(pl.Int64),
        pl.col("last_present_condition").cast(pl.Int64),
        pl.col("last_lat_dd").cast(pl.Float64),
        pl.col("last_lon_dd").cast(pl.Float64),
        pl.col("last_iso_country").cast(pl.Utf8),
        pl.col("last_iso_subdivision").cast(pl.Utf8),
        pl.col("event_days_span").cast(pl.Int64),
    )
    return df



def add_distance(df): 
    import polars as pl
    
    # adapted from: https://community.esri.com/t5/coordinate-reference-systems-blog/distance-on-a-sphere-the-haversine-formula/ba-p/902128
    df = df.with_columns(
        # Convert to radians
        lat1=pl.col('banding_lat_dd') * pl.lit(3.141592653589793 / 180),
        lon1=pl.col('banding_lon_dd') * pl.lit(3.141592653589793 / 180),
        lat2=pl.col('last_lat_dd') * pl.lit(3.141592653589793 / 180),
        lon2=pl.col('last_lon_dd') * pl.lit(3.141592653589793 / 180),
    ).with_columns(
        # Calculate haversine
        dlat=(pl.col('lat2') - pl.col('lat1')),
        dlon=(pl.col('lon2') - pl.col('lon1')),
    ).with_columns(
        a=(
            (pl.col('dlat') / 2).sin().pow(2) +
            pl.col('lat1').cos() * pl.col('lat2').cos() * (pl.col('dlon') / 2).sin().pow(2)
        )
    ).with_columns(
        first_to_last_km=2 * 6371 * (pl.col('a').sqrt().arcsin())
    ).drop(['lat1', 'lon1', 'lat2', 'lon2', 'dlat', 'dlon', 'a'])
    
    return df


def write_parquet_file(df: pl.DataFrame, file_path: str):
    df.write_parquet(
        file_path,
        compression="snappy",
        use_pyarrow=True,
        statistics=True,
    )


def agg_nabbp_data(file_ids=None):
    """
    To limit the number of files and data processed:
    specify file ids with 2 digit string ex '01','02'
    if None, process all files.
    """
    all_files = get_nabbp_data_files()

    if file_ids:
        files = [f for f in all_files if any(f"NABBP_2025_grp_{fid}.csv.gz" in f for fid in file_ids)]
    else:
        files = all_files

    for file in files:
        print(f"Processing file: {file}")
        df = load_nabbp_data(file)
        df = clean_nappb_data(df)
        df = aggregate_band_data(df)
        df = clean_agg_data(df)
        df = add_distance(df)
    
        dest_file = os.path.join(dest_data_path, f"nabbp_band_agg_{os.path.basename(file).replace('.csv.gz','.parquet')}")
        write_parquet_file(df, dest_file)
    

if __name__ == "__main__":
    # to limit the number of files and data processed, specify file ids with 2 digit string ex '01','02'
    # if None, process all files.
    
    file_ids = None
    #file_ids = ['01','02','03','04','05','06','07','08','09','10']
    #file_ids = ['01']
    agg_nabbp_data(file_ids)