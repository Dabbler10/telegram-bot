from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    moder_chat_id: str
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()