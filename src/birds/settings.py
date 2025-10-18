import os
import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict



def get_relative_path(target_path):
    """Determine the relative path from the current working directory to the target path."""
    target_abs = os.path.abspath(target_path)
    current_abs = os.path.abspath(os.getcwd())

    relative_path = os.path.relpath(target_abs, current_abs)    
    return relative_path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding='utf-8',
        env_file=dotenv.find_dotenv(),
        env_prefix='mads_birds_',
        extra='ignore',
    )

    env: str
    version: str

    augmented_data_base_path: str = (
        '/workspaces/mads-siads-696-fall-2025-birds-at-risk/notebooks/data/augmented_data'
    )

    nabbp_base_path: str = (
        '/workspaces/mads-siads-696-fall-2025-birds-at-risk/notebooks/data/source_data/NABBP-2025'
    )

    redlist_species_data_path: str = (
        '/workspaces/mads-siads-696-fall-2025-birds-at-risk/notebooks/data/source_data/redlist_species_data'
    )

    # added data model storage path
    model_path: str = (
        '/workspaces/mads-siads-696-fall-2025-birds-at-risk/notebooks/data/models'
    )

    @property
    def nabbp_lookups_path(self) -> str:
        return os.path.join(self.nabbp_base_path, 'NABBP_lookups_2025')

    @property
    def nabbp_data_path(self) -> str:
        return os.path.join(self.nabbp_base_path, 'grpdata')

    @property
    def augmented_band_agg(self) -> str:
        return os.path.join(self.augmented_data_base_path, 'band_agg')
    
    @property
    def augmented_atrisk_events(self) -> str:
        return os.path.join(self.augmented_data_base_path, 'at_risk_events')

def load_settings() -> Settings:
    return Settings()
