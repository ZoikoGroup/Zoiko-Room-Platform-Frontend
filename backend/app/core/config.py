from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://zoiko:zoiko@localhost:5432/zoiko_rooms"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    cors_origins: str = "http://localhost:3000"
    cookie_secure: bool = False

    seed_admin_email: str = "admin@zoikorooms.com"
    seed_admin_password: str = "change-this-password"

    public_api_url: str = "http://localhost:8000"
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 8

    # USER identity documents are never served through the public /uploads static
    # route -- they live in their own directory that main.py never mounts.
    identity_upload_dir: str = "secure_uploads/identity"
    identity_document_max_size_mb: int = 10

    frontend_url: str = "http://localhost:3000"
    password_reset_token_expire_minutes: int = 30

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
