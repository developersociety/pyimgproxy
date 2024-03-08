import os

from .exceptions import ConfigurationError
from .image import Image


class ImgProxy:
    def __init__(
        self,
        url: str = "",
        key: str = "",
        salt: str = "",
        encryption_key: str = "",
    ) -> None:
        self.url = url or os.environ.get("IMGPROXY_URL", "")
        self.key = bytes.fromhex(key or os.environ.get("IMGPROXY_KEY", ""))
        self.salt = bytes.fromhex(salt or os.environ.get("IMGPROXY_SALT", ""))
        self.encryption_key = bytes.fromhex(
            encryption_key or os.environ.get("IMGPROXY_SOURCE_URL_ENCRYPTION_KEY", "")
        )

        if not self.url:
            raise ConfigurationError("ImgProxy URL not set")

    def __repr__(self) -> str:
        return f"<ImgProxy {self.url}>"

    def image(self, source_url: str) -> Image:
        return Image(imgproxy=self, source_url=source_url)
