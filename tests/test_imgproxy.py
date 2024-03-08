import os
from unittest import TestCase, mock

from pyimgproxy import ImgProxy
from pyimgproxy.exceptions import ConfigurationError
from pyimgproxy.image import Image


class ImgProxyTestCase(TestCase):
    def test_repr(self):
        imgproxy = ImgProxy(url="https://example.org/thumbnail")

        self.assertEqual(repr(imgproxy), "<ImgProxy https://example.org/thumbnail>")

    def test_full_settings(self):
        imgproxy = ImgProxy(
            url="https://example.org/thumbnail",
            key="1" * 16,
            salt="2" * 16,
            encryption_key="3" * 16,
        )

        self.assertEqual(imgproxy.url, "https://example.org/thumbnail")
        self.assertEqual(imgproxy.key, b"\x11" * 8)
        self.assertEqual(imgproxy.salt, b"\x22" * 8)
        self.assertEqual(imgproxy.encryption_key, b"\x33" * 8)

    @mock.patch.dict(
        os.environ,
        {
            "IMGPROXY_URL": "https://example.org/thumbnail",
            "IMGPROXY_KEY": "1111111111111111",
            "IMGPROXY_SALT": "2222222222222222",
            "IMGPROXY_SOURCE_URL_ENCRYPTION_KEY": "3333333333333333",
        },
    )
    def test_environment_settings(self):
        imgproxy = ImgProxy()

        self.assertEqual(imgproxy.url, "https://example.org/thumbnail")
        self.assertEqual(imgproxy.key, b"\x11" * 8)
        self.assertEqual(imgproxy.salt, b"\x22" * 8)
        self.assertEqual(imgproxy.encryption_key, b"\x33" * 8)

    def test_no_url(self):
        with self.assertRaises(ConfigurationError, msg="ImgProxy URL not set"):
            _imgproxy = ImgProxy()

    def test_image(self):
        imgproxy = ImgProxy(url="https://example.org/thumbnail")

        image = imgproxy.image("demo.png")

        self.assertIsInstance(image, Image)
        self.assertEqual(image.imgproxy, imgproxy)
        self.assertEqual(image._source_url, "demo.png")
