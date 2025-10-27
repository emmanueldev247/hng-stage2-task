from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    ENV: str = Field(default="development")
    PORT: int = Field(default=8012)

    DATABASE_URL: str = Field(default="sqlite:///./data.db")
    EXTERNAL_COUNTRIES_URL: str = Field(default="https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies")
    EXTERNAL_RATES_URL: str = Field(default="https://open.er-api.com/v6/latest/USD")
    EXTERNAL_TIMEOUT: int = Field(default=10)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
