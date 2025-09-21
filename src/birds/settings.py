import os
import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding='utf-8',
        env_file=dotenv.find_dotenv(),
        env_prefix='mads_birds_',
        extra='ignore',
    )

    env: str
    version: str

    nabbp_base_path: str = (
        '/workspaces/mads-siads-696-fall-2025-birds-at-risk/notebooks/data/source_data/NABBP-2025'
    )

    @property
    def nabbp_lookups_path(self) -> str:
        return os.path.join(self.nabbp_base_path, 'NABBP_lookups_2025')

    @property
    def nabbp_data_path(self) -> str:
        return os.path.join(self.nabbp_base_path, 'grpdata')



def load_settings() -> Settings:
    return Settings()
