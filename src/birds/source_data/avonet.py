import os
import pandas as pd
from birds.settings import load_settings


class DataTables:
    """
    # Downloaded from https://opentraits.org/datasets/avonet
    # https://figshare.com/s/b990722d72a26b5bfead
    """
    def __init__(self):
        self.__settings = load_settings()

    @property
    def bird_tree(self) -> pd.DataFrame:
        path = os.path.join(self.__settings.avonet_base_path, 'TraitData', 'AVONET3_BirdTree.xlsx')
        return pd.read_excel(path,  sheet_name='AVONET3_BirdTree')
