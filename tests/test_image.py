from unittest import TestCase

from pyimgproxy import ImgProxy


class ImageProcessingTestCase(TestCase):
    def setUp(self):
        self.imgproxy = ImgProxy(
            url="https://example.org/thumbnail",
            key="1" * 16,
            salt="2" * 16,
        )
        self.image = self.imgproxy.image(source_url="demo.png")
        return super().setUp()

    def test_source_url(self):
        image = self.image.source_url(source_url="another_image.png")

        self.assertNotEqual(id(self.image), id(image))
        self.assertEqual(image._source_url, "another_image.png")

    def test_add_option(self):
        image = self.image.add_option("demo", 1, None, 2, None, 3, None)

        self.assertNotEqual(id(self.image), id(image))
        self.assertEqual(image.options, ["demo:1::2::3"])

    def test_resize(self):
        image = self.image.resize(
            resizing_type="fill",
            width=640,
            height=480,
            enlarge=True,
            extend=True,
            gravity_type="we",
            x_offset=0.1,
            y_offset=0.2,
        )

        self.assertEqual(image.options, ["resize:fill:640:480:True:True:we:0.1:0.2"])

    def test_size(self):
        image = self.image.size(
            width=640,
            height=480,
            enlarge=True,
            extend=True,
            gravity_type="we",
            x_offset=0.1,
            y_offset=0.2,
        )

        self.assertEqual(image.options, ["size:640:480:True:True:we:0.1:0.2"])

    def test_resizing_type(self):
        image = self.image.resizing_type(resizing_type="fill")

        self.assertEqual(image.options, ["resizing_type:fill"])

    def test_resizing_algorithm(self):
        image = self.image.resizing_algorithm(resizing_algorithm="nearest")

        self.assertEqual(image.options, ["resizing_algorithm:nearest"])

    def test_width(self):
        image = self.image.width(width=100)

        self.assertEqual(image.options, ["width:100"])

    def test_height(self):
        image = self.image.height(height=100)

        self.assertEqual(image.options, ["height:100"])

    def test_min_width(self):
        image = self.image.min_width(width=100)

        self.assertEqual(image.options, ["min-width:100"])

    def test_min_height(self):
        image = self.image.min_height(height=100)

        self.assertEqual(image.options, ["min-height:100"])

    def test_zoom(self):
        image = self.image.zoom(x=1.1, y=1.2)

        self.assertEqual(image.options, ["zoom:1.1:1.2"])

    def test_dpr(self):
        image = self.image.dpr(dpr=2)

        self.assertEqual(image.options, ["dpr:2"])

    def test_enlarge(self):
        image = self.image.enlarge(enlarge=True)

        self.assertEqual(image.options, ["enlarge:True"])

    def test_extend(self):
        image = self.image.extend(
            extend=True,
            gravity_type="we",
            x_offset=0.1,
            y_offset=0.2,
        )

        self.assertEqual(image.options, ["extend:True:we:0.1:0.2"])

    def test_extend_aspect_ratio(self):
        image = self.image.extend_aspect_ratio(
            extend=True,
            gravity_type="we",
            x_offset=0.1,
            y_offset=0.2,
        )

        self.assertEqual(image.options, ["extend_aspect_ratio:True:we:0.1:0.2"])

    def test_gravity(self):
        image = self.image.gravity(
            gravity_type="we",
            x_offset=0.1,
            y_offset=0.2,
        )

        self.assertEqual(image.options, ["gravity:we:0.1:0.2"])

    def test_crop(self):
        image = self.image.crop(
            width=640,
            height=480,
            gravity_type="we",
            x_offset=0.1,
            y_offset=0.2,
        )

        self.assertEqual(image.options, ["crop:640:480:we:0.1:0.2"])

    def test_trim(self):
        image = self.image.trim(
            threshold=0.1,
            color="abcdef",
            equal_hor=True,
            equal_ver=True,
        )

        self.assertEqual(image.options, ["trim:0.1:abcdef:True:True"])

    def test_padding(self):
        image = self.image.padding(
            top=10,
            right=20,
            bottom=30,
            left=40,
        )

        self.assertEqual(image.options, ["padding:10:20:30:40"])

    def test_auto_rotate(self):
        image = self.image.auto_rotate(auto_rotate=True)

        self.assertEqual(image.options, ["auto_rotate:True"])

    def test_rotate(self):
        image = self.image.rotate(angle=180)

        self.assertEqual(image.options, ["rotate:180"])

    def test_background_hex_color(self):
        image = self.image.background(hex_color="abcdef")

        self.assertEqual(image.options, ["background:abcdef"])

    def test_background_rgb(self):
        image = self.image.background(red=50, green=150, blue=250)

        self.assertEqual(image.options, ["background:50:150:250"])

    def test_background_alpha(self):
        image = self.image.background_alpha(alpha=0.1)

        self.assertEqual(image.options, ["background_alpha:0.1"])

    def test_adjust(self):
        image = self.image.adjust(brightness=128, contrast=0.1, saturation=0.2)

        self.assertEqual(image.options, ["adjust:128:0.1:0.2"])

    def test_brightness(self):
        image = self.image.brightness(brightness=128)

        self.assertEqual(image.options, ["brightness:128"])

    def test_contrast(self):
        image = self.image.contrast(contrast=0.1)

        self.assertEqual(image.options, ["contrast:0.1"])

    def test_saturation(self):
        image = self.image.saturation(saturation=0.1)

        self.assertEqual(image.options, ["saturation:0.1"])

    def test_blur(self):
        image = self.image.blur(sigma=0.5)

        self.assertEqual(image.options, ["blur:0.5"])

    def test_sharpen(self):
        image = self.image.sharpen(sigma=0.5)

        self.assertEqual(image.options, ["sharpen:0.5"])

    def test_pixelate(self):
        image = self.image.pixelate(size=5)

        self.assertEqual(image.options, ["pixelate:5"])

    def test_unsharp_masking(self):
        image = self.image.unsharp_masking(mode="always", weight=2, divider=20.5)

        self.assertEqual(image.options, ["unsharp_masking:always:2:20.5"])

    def test_blur_detections(self):
        image = self.image.blur_detections(sigma=0.5, class_names=["one", "two", "three"])

        self.assertEqual(image.options, ["blur_detections:0.5:one:two:three"])

    def test_blur_detections_empty(self):
        image = self.image.blur_detections(sigma=0.5)

        self.assertEqual(image.options, ["blur_detections:0.5"])

    def test_draw_detections(self):
        image = self.image.draw_detections(draw=True, class_names=["one", "two", "three"])

        self.assertEqual(image.options, ["draw_detections:True:one:two:three"])

    def test_draw_detections_empty(self):
        image = self.image.draw_detections(draw=True)

        self.assertEqual(image.options, ["draw_detections:True"])


class ImageTestCase(TestCase):
    def test_repr(self):
        imgproxy = ImgProxy(
            url="https://example.org/thumbnail",
            key="1" * 16,
            salt="2" * 16,
        )
        image = imgproxy.image("demo.png")

        self.assertEqual(repr(image), "<Image demo.png>")

    def test_url_standard(self):
        imgproxy = ImgProxy(
            url="https://example.org/thumbnail",
            key="1" * 16,
            salt="2" * 16,
        )
        image = imgproxy.image("demo.png").size(width=640, height=480)

        self.assertEqual(
            image.url,
            (
                "https://example.org/"
                "thumbnail/muzV--3ARhtX_iCFwE_kLkzvohwQIJLZloJpBBg7MkQ/size:640:480/plain/demo.png"
            ),
        )

    def test_url_no_options(self):
        imgproxy = ImgProxy(
            url="https://example.org/thumbnail",
            key="1" * 16,
            salt="2" * 16,
        )
        image = imgproxy.image("demo.png")

        self.assertEqual(
            image.url,
            (
                "https://example.org/"
                "thumbnail/qHrDO4lTysklvMcR1YNDeupe94JCjzzSA0rdEgfq2rc/plain/demo.png"
            ),
        )

    def test_url_needs_quoting(self):
        imgproxy = ImgProxy(
            url="https://example.org/thumbnail",
            key="1" * 16,
            salt="2" * 16,
        )
        image = imgproxy.image("demo.png?hello=world")

        self.assertEqual(
            image.url,
            (
                "https://example.org/"
                "thumbnail/Mr9iFZTtzF7OS2NYKYdzmcG_pWk4ffjIUbe4FyobHnM/ZGVtby5wbmc_aGVsbG89d29ybGQ"
            ),
        )

    def test_url_no_key_or_salt(self):
        imgproxy = ImgProxy(url="https://example.org/thumbnail")
        image = imgproxy.image("demo.png").size(width=640, height=480)

        self.assertEqual(
            image.url,
            "https://example.org/thumbnail/size:640:480/plain/demo.png",
        )
