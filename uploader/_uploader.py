import datetime as dtm
import logging
from collections.abc import Collection
from pathlib import Path

import aioftp
from aiorem import AbstractResourceManager

from uploader._settings import Settings

_LOGGER = logging.getLogger(__name__)


class AkaDressenUploader(AbstractResourceManager):
    LATEST_PREFIX: str = "latest_"

    def __init__(self, settings: Settings | None = None):
        self.settings: Settings = (
            settings if settings else Settings()  # type: ignore[reportCallIssue]
        )
        self.ftp_client: aioftp.Client = aioftp.Client()

    async def acquire_resources(self) -> None:
        """Initialize the Uploader by establishing the FTP connection"""
        await self.ftp_client.connect(host=self.settings.ftp_host, port=self.settings.ftp_port)
        await self.ftp_client.login(
            user=self.settings.ftp_username, password=self.settings.ftp_password
        )
        _LOGGER.debug("Connected to FTP server")

    async def release_resources_on_error(self) -> None:
        """Shutdown the Uploader by terminating the FTP connection"""
        self.ftp_client.close()
        _LOGGER.debug("Disconnected from FTP server")

    async def release_resources(self) -> None:
        """Shutdown the Uploader by terminating the FTP connection"""
        await self.ftp_client.quit()
        _LOGGER.debug("Disconnected from FTP server")

    @staticmethod
    def parse_modify_date(date: str) -> dtm.datetime:
        """Parse the date string returned by the FTP server"""
        return dtm.datetime.strptime(date, "%Y%m%d%H%M%S").replace(tzinfo=dtm.UTC)

    async def list_files(self) -> Collection[tuple[Path, dtm.datetime]]:
        """List all files in the target directory"""
        out = set()
        async for path, info in self.ftp_client.list(self.settings.target_path.as_posix()):
            if info.get("type") != "file":
                continue
            out.add((Path(path), self.parse_modify_date(info["modify"])))

        return out

    async def move_latest_files(self) -> None:
        """Renames all files that start with the prefix ``latest_``. They will instead be
        prefixed with their modification date in the format ``YYYYMMDD``.
        """
        for path, date in await self.list_files():
            if not path.name.startswith(self.LATEST_PREFIX):
                _LOGGER.debug("Skipping %s, not relevant for renaming", path)
                continue

            new_name = path.with_name(
                f"{date:%Y%m%d}_{path.name.removeprefix(self.LATEST_PREFIX)}"
            )
            _LOGGER.info("Renaming %s to %s", path, new_name)
            await self.ftp_client.rename(path.as_posix(), new_name.as_posix())

    async def upload_files(self) -> None:
        """Uploads all files from the source directory to the target directory. All will be
        prefixed with ``latest_``."""
        for path in self.settings.source_path.iterdir():
            if not path.is_file():
                continue

            _LOGGER.info("Uploading %s", path)
            await self.ftp_client.upload(path.as_posix(), self.settings.target_path.as_posix())

            uploaded_name = self.settings.target_path.joinpath(path.name)

            new_name = uploaded_name.with_name(self.LATEST_PREFIX + uploaded_name.name)
            # special case: Rename "Mitglieder.csv" to "Akadressen_CSV.csv"
            if new_name.name == self.LATEST_PREFIX + "Mitglieder.csv":
                new_name = new_name.with_name(self.LATEST_PREFIX + "Akadressen_CSV.csv")

            _LOGGER.info("Renaming %s to %s", uploaded_name, new_name)
            await self.ftp_client.rename(uploaded_name.as_posix(), new_name.as_posix())

    async def do_akadressen_upload(self):
        """Rename the current AkaDressen files and upload the new ones."""
        _LOGGER.info("Starting AkaDressen upload")
        _LOGGER.info("Moving latest files")
        await self.move_latest_files()
        _LOGGER.info("Uploading new files")
        await self.upload_files()
