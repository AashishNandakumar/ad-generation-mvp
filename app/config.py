from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TAVILY_API_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_SESSION_TOKEN: str
    AWS_REGION: str
    TOGETHER_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
