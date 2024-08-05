from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings to use. They can also be specified in a `.env` file."""

    model_config = SettingsConfigDict(env_file=".env")

    ftp_host: str
    """The host address of the FTP server."""
    ftp_port: int = 21
    """The port of the FTP server. Default is 21."""
    ftp_username: str
    """The username for the FTP server."""
    ftp_password: str
    """The password for the FTP server."""
    source_path: Path
    """The path to the source files that will be uploaded."""
    target_path: Path
    """The path on the FTP server where the files will be uploaded."""
