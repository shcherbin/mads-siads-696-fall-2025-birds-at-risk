import pandas as pd
from birds.source_data.nabbp import DataTables
from birds.source_data.iucn import IUCNDataTables
from birds.settings import load_settings


settings = load_settings()
print(settings)


def combine_nabbp_index_redlist():
    nabbp = DataTables()
    redlist = IUCNDataTables()

    nabbp_index_df = nabbp.species_index
    redlist_df = redlist.assessments

    redlist_df = redlist_df[['scientificName','redlistCategory','rationale', 'habitat', 'threats']]

    nabbp = nabbp_index_df.copy()
    redlist = redlist_df.copy()

    nabbp['lower_sci_name'] = nabbp['SCI_NAME'].str.lower()
    redlist['lower_scientific_name'] = redlist['scientificName'].str.lower()
    combined_df = pd.merge(nabbp, redlist, how='left', left_on='lower_sci_name', right_on='lower_scientific_name')
    combined_df = combined_df.drop(columns=['lower_sci_name', 'lower_scientific_name', 'scientificName'])

    
    # if redlistCategory is 'Least Concern' set 'atRisk' to False
    combined_df['atRisk'] = combined_df['redlistCategory'].apply(lambda x: False if x == 'Least Concern' else None)
    # if redlistCateogory is not NaN and not 'Least Concern' set 'atRisk' to True
    combined_df['atRisk'] = combined_df.apply(lambda row: True if pd.notna(row['redlistCategory']) and row['redlistCategory'] != 'Least Concern' else row['atRisk'], axis=1)
    return combined_df



if __name__ == "__main__":
    combined_df = combine_nabbp_index_redlist()
    combined_df.to_csv('../../notebooks/data/augmented_data/nabbp_file_species_index_redlist.csv', index=False)