from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    
    bot_token: SecretStr
    official_chat : SecretStr
    api_id : SecretStr
    api_hash : SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()