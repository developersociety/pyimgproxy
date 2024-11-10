import base64
import hashlib
import hmac
import re
from functools import cached_property
from typing import TYPE_CHECKING, Any, Optional, Union, overload

if TYPE_CHECKING:
    from .imgproxy import ImgProxy


class Image:
    url_escape_regex = re.compile(r"[@?% ]|[^\x00-\x7F]")

    def __init__(self, imgproxy: "ImgProxy", source_url: str) -> None:
        self.imgproxy = imgproxy
        self._source_url = source_url
        self.options: list[str] = []

    def __repr__(self) -> str:
        return f"<Image {self._source_url}>"

    def source_url(self, source_url: str) -> "Image":
        """
        Updates the source URL used for imgproxy to fetch.
        """
        new_image = Image(imgproxy=self.imgproxy, source_url=source_url)
        new_image.options = self.options.copy()
        return new_image

    def add_option(self, option_name: str, *args: Any) -> "Image":
        """
        Add an image processing option, returning a new Image.

        This method is used internally by all other image processing methods, but can also be used
        to add options directly.
        """
        option_list = [option_name, *args]
        # Remove any trailing None values
        while option_list and option_list[-1] is None:
            option_list.pop()
        # Replace remaining None values with empty strings, and convert all other values to strings
        option_string = [str(x) if x is not None else "" for x in option_list]
        new_option = ":".join(option_string)
        new_options_list = [*self.options, new_option]
        new_image = Image(imgproxy=self.imgproxy, source_url=self._source_url)
        new_image.options = new_options_list
        return new_image

    def resize(
        self,
        resizing_type: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        enlarge: Optional[bool] = None,
        extend: Optional[bool] = None,
        gravity_type: Optional[str] = None,
        x_offset: Optional[Union[int, float]] = None,
        y_offset: Optional[Union[int, float]] = None,
    ) -> "Image":
        """
        This is a meta-option that defines the resizing type, width, height, enlarge, and extend.
        All arguments are optional and can be omitted to use their default values.
        """
        return self.add_option(
            "resize",
            resizing_type,
            width,
            height,
            enlarge,
            extend,
            gravity_type,
            x_offset,
            y_offset,
        )

    def size(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        enlarge: Optional[bool] = None,
        extend: Optional[bool] = None,
        gravity_type: Optional[str] = None,
        x_offset: Optional[Union[int, float]] = None,
        y_offset: Optional[Union[int, float]] = None,
    ) -> "Image":
        """
        This is a meta-option that defines the width, height, enlarge, and extend. All arguments
        are optional and can be omitted to use their default values.
        """
        return self.add_option(
            "size", width, height, enlarge, extend, gravity_type, x_offset, y_offset
        )

    def resizing_type(self, resizing_type: str) -> "Image":
        """
        Defines how imgproxy will resize the source image. Supported resizing types are:

        - `fit`: resizes the image while keeping aspect ratio to fit a given size.
        - `fill`: resizes the image while keeping aspect ratio to fill a given size and crops
          projecting parts.
        - `fill-down`: the same as `fill`, but if the resized image is smaller than the requested
          size, imgproxy will crop the result to keep the requested aspect ratio.
        - `force`: resizes the image without keeping the aspect ratio.
        - `auto`: if both source and resulting dimensions have the same orientation (portrait or
          landscape), imgproxy will use `fill`. Otherwise, it will use `fit`.

        Default: `fit`
        """
        return self.add_option("resizing_type", resizing_type)

    def resizing_algorithm(self, resizing_algorithm: str) -> "Image":
        """
        Defines the algorithm that imgproxy will use for resizing. Supported algorithms are
        `nearest`, `linear`, `cubic`, `lanczos2`, and `lanczos3`.

        Default: `lanczos3`
        """
        return self.add_option("resizing_algorithm", resizing_algorithm)

    def width(self, width: int) -> "Image":
        """
        Defines the width of the resulting image. When set to `0`, imgproxy will calculate width
        using the defined height and source aspect ratio. When set to `0` and resizing type is
        `force`, imgproxy will keep the original width.

        Default: `0`
        """
        return self.add_option("width", width)

    def height(self, height: int) -> "Image":
        """
        Defines the height of the resulting image. When set to `0`, imgproxy will calculate
        resulting height using the defined width and source aspect ratio. When set to `0` and
        resizing type is `force`, imgproxy will keep the original height.

        Default: `0`
        """
        return self.add_option("height", height)

    def min_width(self, width: int) -> "Image":
        """
        Defines the minimum width of the resulting image.

        When both `width` and `min-width` are set, the final image will be cropped according to
        `width`, so use this combination with care.

        Default: `0`
        """
        return self.add_option("min-width", width)

    def min_height(self, height: int) -> "Image":
        """
        Defines the minimum height of the resulting image.

        When both `height` and `min-height` are set, the final image will be cropped according to
        `height`, so use this combination with care.

        Default: `0`
        """
        return self.add_option("min-height", height)

    def zoom(self, x: Union[int, float], y: Optional[Union[int, float]] = None) -> "Image":
        """
        When set, imgproxy will multiply the image dimensions according to these factors. The
        values must be greater than 0.

        Can be combined with `width` and `height` options. In this case, imgproxy calculates scale
        factors for the provided size and then multiplies it with the provided zoom factors.

        Unlike the `dpr` option, the `zoom` option doesn't affect gravities offsets, watermark
        offsets, and paddings.

        Default: `1`
        """
        return self.add_option("zoom", x, y)

    def dpr(self, dpr: Union[int, float]) -> "Image":
        """
        When set, imgproxy will multiply the image dimensions according to this factor for HiDPI
        (Retina) devices. The value must be greater than 0.

        The `dpr` option affects gravities offsets, watermark offsets, and paddings to make the
        resulting image structures with and without the `dpr` option applied match.

        Default: `1`
        """
        return self.add_option("dpr", dpr)

    def enlarge(self, enlarge: bool = False) -> "Image":
        """
        When set to `True`, imgproxy will enlarge the image if it is smaller than the given size.

        Default: `False`
        """
        return self.add_option("enlarge", enlarge)

    def extend(
        self,
        extend: Optional[bool] = None,
        gravity_type: Optional[str] = None,
        x_offset: Optional[Union[int, float]] = None,
        y_offset: Optional[Union[int, float]] = None,
    ) -> "Image":
        """
        - When extend is set to `True`, imgproxy will extend the image if it is smaller than the
          given size.
        - `gravity_type` (optional) accepts the same values as the gravity option, except `sm`.
          When `gravity` is not set, imgproxy will use `ce` gravity without offsets.

        Default: `false:ce:0:0`
        """
        return self.add_option("extend", extend, gravity_type, x_offset, y_offset)

    def extend_aspect_ratio(
        self,
        extend: Optional[bool] = None,
        gravity_type: Optional[str] = None,
        x_offset: Optional[Union[int, float]] = None,
        y_offset: Optional[Union[int, float]] = None,
    ) -> "Image":
        """
        - When extend is set to `True`, imgproxy will extend the image to the requested aspect
          ratio.
        - `gravity_type` (optional) accepts the same values as the gravity option, except `sm`.
          When `gravity_type` is not set, imgproxy will use `ce` gravity without offsets.

        Default: `false:ce:0:0`
        """
        return self.add_option("extend_aspect_ratio", extend, gravity_type, x_offset, y_offset)

    def gravity(
        self,
        gravity_type: Optional[str] = None,
        x_offset: Optional[Union[int, float]] = None,
        y_offset: Optional[Union[int, float]] = None,
    ) -> "Image":
        """
        When imgproxy needs to cut some parts of the image, it is guided by the gravity option.

        - `gravity_type` - specifies the gravity type. Available values:
            - `no`: north (top edge)
            - `so`: south (bottom edge)
            - `ea`: east (right edge)
            - `we`: west (left edge)
            - `noea`: north-east (top-right corner)
            - `nowe`: north-west (top-left corner)
            - `soea`: south-east (bottom-right corner)
            - `sowe`: south-west (bottom-left corner)
            - `ce`: center
        - `x_offset`, `y_offset` - (optional) specifies the gravity offset along the X and Y axes:
            - When `x_offset` or `y_offset` is greater than or equal to `1`, imgproxy treats it as
              an absolute value.
            - When `x_offset` or `y_offset` is less than `1`, imgproxy treats it as a relative
              value.

        Default: `ce:0:0`
        """
        return self.add_option("gravity", gravity_type, x_offset, y_offset)

    def crop(
        self,
        width: Optional[Union[int, float]] = None,
        height: Optional[Union[int, float]] = None,
        gravity_type: Optional[str] = None,
        x_offset: Optional[Union[int, float]] = None,
        y_offset: Optional[Union[int, float]] = None,
    ) -> "Image":
        """
        Defines an area of the image to be processed (crop before resize).

        - `width` and `height` define the size of the area:
            - When `width` or `height` is greater than or equal to `1`, imgproxy treats it as an
              absolute value.
            - When `width` or `height` is less than `1`, imgproxy treats it as a relative value.
            - When `width` or `height` is set to `0`, imgproxy will use the full width/height of
              the source image.
        - `gravity_type` (optional) accepts the same values as the gravity option. When
          `gravity_type` is not set, imgproxy will use the value of the gravity option.
        """
        return self.add_option("crop", width, height, gravity_type, x_offset, y_offset)

    def trim(
        self,
        threshold: Optional[Union[int, float]] = None,
        color: Optional[str] = None,
        equal_hor: Optional[bool] = None,
        equal_ver: Optional[bool] = None,
    ) -> "Image":
        """
        Removes surrounding background.

        - `threshold` - color similarity tolerance.
        - `color` - (optional) a hex-coded value of the color that needs to be cut off.
        - `equal_hor` - (optional) set to `True`, imgproxy will cut only equal parts from left and
          right sides. That means that if 10px of background can be cut off from the left and 5px
          from the right, then 5px will be cut off from both sides. For example, this can be useful
          if objects on your images are centered but have non-symmetrical shadow.
        - `equal_ver` - (optional) acts like `equal_hor` but for top/bottom sides.
        """
        return self.add_option("trim", threshold, color, equal_hor, equal_ver)

    def padding(
        self,
        top: int,
        right: Optional[int] = None,
        bottom: Optional[int] = None,
        left: Optional[int] = None,
    ) -> "Image":
        """
        Defines padding size using CSS-style syntax. All arguments are optional but at least one
        dimension must be set. Padded space is filled according to the background option.

            top - top padding (and for all other sides if they haven't been explicitly set)
            right - right padding (and left if it hasn't been explicitly set)
            bottom - bottom padding
            left - left padding
        """
        return self.add_option("padding", top, right, bottom, left)

    def auto_rotate(self, auto_rotate: bool) -> "Image":
        """
        When set to `True`, imgproxy will automatically rotate images based on the EXIF Orientation
        parameter (if available in the image meta data). The orientation tag will be removed from
        the image in all cases. Normally this is controlled by the IMGPROXY_AUTO_ROTATE
        configuration but this procesing option allows the configuration to be set for each
        request.
        """
        return self.add_option("auto_rotate", auto_rotate)

    def rotate(self, angle: int) -> "Image":
        """
        Rotates the image on the specified angle. The orientation from the image metadata is
        applied before the rotation unless autorotation is disabled.

        Only `0`, `90`, `180`, `270`, etc., degree angles are supported.

        Default: `0`
        """
        return self.add_option("rotate", angle)

    @overload
    def background(self, *, hex_color: str) -> "Image": ...

    @overload
    def background(self, *, red: int, green: int, blue: int) -> "Image": ...

    def background(
        self,
        *,
        red: Optional[int] = None,
        green: Optional[int] = None,
        blue: Optional[int] = None,
        hex_color: Optional[str] = None,
    ) -> "Image":
        """
        When set, imgproxy will fill the resulting image background with the specified color.
        `red`, `green`, and `blue` are the channel values of the background color (0-255).
        `hex_color` is a hex-coded value of the color. Useful when you convert an image with
        alpha-channel to JPEG.

        Default: disabled
        """
        if hex_color is not None:
            return self.add_option("background", hex_color)

        return self.add_option("background", red, green, blue)

    def background_alpha(self, alpha: Union[int, float]) -> "Image":
        """
        Adds an alpha channel to `background`. The value of `alpha` is a positive floating point
        number between `0` and `1`.

        Default: `1`
        """
        return self.add_option("background_alpha", alpha)

    def adjust(
        self,
        brightness: Optional[int] = None,
        contrast: Optional[Union[int, float]] = None,
        saturation: Optional[Union[int, float]] = None,
    ) -> "Image":
        """
        This is a meta-option that defines the brightness, contrast, and saturation. All arguments
        are optional and can be omitted to use their default values.
        """
        return self.add_option("adjust", brightness, contrast, saturation)

    def brightness(self, brightness: int) -> "Image":
        """
        When set, imgproxy will adjust brightness of the resulting image. `brightness` is an
        integer number ranging from `-255` to `255`.

        Default: `0`
        """
        return self.add_option("brightness", brightness)

    def contrast(self, contrast: Union[int, float]) -> "Image":
        """
        When set, imgproxy will adjust the contrast of the resulting image. `contrast` is a
        positive floating point number, where a value of `1` leaves the contrast unchanged.

        Default: `1`
        """
        return self.add_option("contrast", contrast)

    def saturation(self, saturation: Union[int, float]) -> "Image":
        """
        When set, imgproxy will adjust saturation of the resulting image. `saturation` is a
        positive floating-point number, where a value of `1` leaves the saturation unchanged.

        Default: `1`
        """
        return self.add_option("saturation", saturation)

    def blur(self, sigma: Union[int, float]) -> "Image":
        """
        When set, imgproxy will apply a gaussian blur filter to the resulting image. The value of
        `sigma` defines the size of the mask imgproxy will use.

        Default: disabled
        """
        return self.add_option("blur", sigma)

    def sharpen(self, sigma: Union[int, float]) -> "Image":
        """
        When set, imgproxy will apply the sharpen filter to the resulting image. The value of
        `sigma` defines the size of the mask imgproxy will use.

        As an approximate guideline, use 0.5 sigma for 4 pixels/mm (display resolution), 1.0 for
        12 pixels/mm and 1.5 for 16 pixels/mm (300 dpi == 12 pixels/mm).

        Default: disabled
        """
        return self.add_option("sharpen", sigma)

    def pixelate(self, size: int) -> "Image":
        """
        When set, imgproxy will apply the pixelate filter to the resulting image. The value of
        `size` defines individual pixel size.

        Default: disabled
        """
        return self.add_option("pixelate", size)

    def unsharp_masking(
        self,
        mode: Optional[str] = None,
        weight: Optional[Union[int, float]] = None,
        divider: Optional[Union[int, float]] = None,
    ) -> "Image":
        """
        Allows redefining unsharp masking options. All arguments have the same meaning as Unsharp
        masking configs. All arguments are optional and can be omitted.
        """
        return self.add_option("unsharp_masking", mode, weight, divider)

    def blur_detections(
        self, sigma: Union[int, float], class_names: Optional[list[str]] = None
    ) -> "Image":
        """
        imgproxy detects objects of the provided classes and blurs them. If class names are
        omitted, imgproxy blurs all the detected objects.

        The value of `sigma` defines the size of the mask imgproxy will use.
        """
        if class_names is None:
            class_names = []
        return self.add_option("blur_detections", sigma, *class_names)

    def draw_detections(self, draw: bool, class_names: Optional[list[str]] = None) -> "Image":
        """
        When draw is set to `True`, imgproxy detects objects of the provided classes and draws
        their bounding boxes. If class names are omitted, imgproxy draws the bounding boxes of all
        the detected objects.
        """
        if class_names is None:
            class_names = []
        return self.add_option("draw_detections", draw, *class_names)

    def gradient(self) -> "Image":
        raise NotImplementedError

    def watermark(self) -> "Image":
        raise NotImplementedError

    def watermark_url(self) -> "Image":
        raise NotImplementedError

    def watermark_text(self) -> "Image":
        raise NotImplementedError

    def watermark_size(self) -> "Image":
        raise NotImplementedError

    def watermark_shadow(self) -> "Image":
        raise NotImplementedError

    def style(self) -> "Image":
        raise NotImplementedError

    def strip_metadata(self, strip_metadata: bool = False) -> "Image":
        """
        When set to `True`, imgproxy will strip the metadata (EXIF, IPTC, etc.) on JPEG and WebP
        output images. This is normally controlled by the `IMGPROXY_STRIP_METADATA` configuration
        but this processing option allows the configuration to be set for each request.
        """
        return self.add_option("strip_metadata", strip_metadata)

    def keep_copyright(self, keep_copyright: bool = False) -> "Image":
        """
        When set to `True`, imgproxy will not remove copyright info while stripping metadata. This
        is normally controlled by the `IMGPROXY_KEEP_COPYRIGHT` configuration but this processing
        option allows the configuration to be set for each request.
        """
        return self.add_option("keep_copyright", keep_copyright)

    def dpi(self) -> "Image":
        raise NotImplementedError

    def strip_color_profile(self, strip_color_profile: bool = False) -> "Image":
        """
        When set to `True`, imgproxy will transform the embedded color profile (ICC) to sRGB and
        remove it from the image. Otherwise, imgproxy will try to keep it as is. This is normally
        controlled by the `IMGPROXY_STRIP_COLOR_PROFILE` configuration but this processing option
        allows the configuration to be set for each request.
        """
        return self.add_option("strip_color_profile", strip_color_profile)

    def enforce_thumbnail(self, enforce_thumbnail: bool = False) -> "Image":
        """
        When set to `True` and the source image has an embedded thumbnail, imgproxy will always
        use the embedded thumbnail instead of the main image. Currently, only thumbnails embedded
        in heic and avif are supported. This is normally controlled by the
        `IMGPROXY_ENFORCE_THUMBNAIL` configuration but this processing option allows the
        configuration to be set for each request.
        """
        return self.add_option("enforce_thumbnail", enforce_thumbnail)

    def quality(self, quality: int) -> "Image":
        """
        Redefines quality of the resulting image, as a percentage. When set to `0`, quality is
        assumed based on `IMGPROXY_QUALITY` and `format_quality`.

        Default: `0`
        """
        return self.add_option("quality", quality)

    def format_quality(self) -> "Image":
        raise NotImplementedError

    def autoquality(self) -> "Image":
        raise NotImplementedError

    def max_bytes(self) -> "Image":
        raise NotImplementedError

    def jpeg_options(self) -> "Image":
        raise NotImplementedError

    def png_options(self) -> "Image":
        raise NotImplementedError

    def webp_options(self) -> "Image":
        raise NotImplementedError

    def format(self, extension: str) -> "Image":
        """
        Specifies the resulting image format. Alias for the extension part of the URL.

        Default: `jpg`
        """
        return self.add_option("format", extension)

    def page(self, page: int) -> "Image":
        """
        When a source image supports pagination (PDF, TIFF) or animation (GIF, WebP), this option
        allows specifying the page to use. Page numeration starts from zero.

        If both the source and the resulting image formats support animation, imgproxy will ignore
        this option and use all the source image pages. Use the `disable_animation` option to make
        imgproxy treat all images as not animated.

        Default: `0`
        """
        return self.add_option("page", page)

    def pages(self, pages: int) -> "Image":
        """
        When a source image supports pagination (PDF, TIFF) or animation (GIF, WebP), this option
        allows specifying the number of pages to use. The pages will be stacked vertically and
        left-aligned.

        If both the source and the resulting image formats support animation, imgproxy will ignore
        this option and use all the source image pages. Use the `disable_animation` option to make
        imgproxy treat all images as not animated.

        Default: `1`
        """
        return self.add_option("pages", pages)

    def disable_animation(self, disable: bool) -> "Image":
        """
        When set to `True`, imgproxy will treat all images as not animated. Use the `page` and the
        `pages` options to specify which frames imgproxy should use.

        Default: `False`
        """
        return self.add_option("disable_animation", disable)

    def video_thumbnail_second(self) -> "Image":
        raise NotImplementedError

    def video_thumbnail_keyframes(self) -> "Image":
        raise NotImplementedError

    def video_thumbnail_tile(self) -> "Image":
        raise NotImplementedError

    def fallback_image_url(self) -> "Image":
        raise NotImplementedError

    def skip_processing(self) -> "Image":
        raise NotImplementedError

    def raw(self, raw: bool) -> "Image":
        """
        When set to `True`, imgproxy will respond with a raw unprocessed, and unchecked source
        image. There are some differences between `raw` and `skip_processing` options:

        - While the `skip_processing` option has some conditions to skip the processing, the `raw`
          option allows to skip processing no matter what
        - With the `raw` option set, imgproxy doesn't check the source image's type, resolution,
          and file size. Basically, the `raw` option allows streaming of any file type
        - With the `raw` option set, imgproxy won't download the whole image to the memory.
          Instead, it will stream the source image directly to the response lowering memory usage
        - The requests with the `raw` option set are not limited by the IMGPROXY_WORKERS config

        Default: `False`
        """
        return self.add_option("raw", raw)

    def cachebuster(self, string: str) -> "Image":
        """
        Cache buster doesn't affect image processing but its changing allows for bypassing the
        CDN, proxy server and browser cache. Useful when you have changed some things that are not
        reflected in the URL, like image quality settings, presets, or watermark data.

        It's highly recommended to prefer the `cachebuster` option over a URL query string because
        that option can be properly signed.

        Default: empty
        """
        return self.add_option("cachebuster", string)

    def expires(self) -> "Image":
        raise NotImplementedError

    def filename(self) -> "Image":
        raise NotImplementedError

    def return_attachment(self, return_attachment: bool) -> "Image":
        """
        When set to `True`, imgproxy will return `attachment` in the `Content-Disposition` header,
        and the browser will open a 'Save as' dialog. This is normally controlled by the
        `IMGPROXY_RETURN_ATTACHMENT` configuration but this processing option allows the
        configuration to be set for each request.
        """
        return self.add_option("return_attachment", return_attachment)

    def preset(self) -> "Image":
        raise NotImplementedError

    def hashsum(self) -> "Image":
        raise NotImplementedError

    def max_src_resolution(self, resolution: int) -> "Image":
        """
        Allows redefining `IMGPROXY_MAX_SRC_RESOLUTION` config.

        Since this option allows redefining a security restriction, its usage is not allowed
        unless the `IMGPROXY_ALLOW_SECURITY_OPTIONS` config is set to true.
        """
        return self.add_option("max_src_resolution", resolution)

    def max_src_file_size(self, size: int) -> "Image":
        """
        Allows redefining `IMGPROXY_MAX_SRC_FILE_SIZE` config.

        Since this option allows redefining a security restriction, its usage is not allowed
        unless the `IMGPROXY_ALLOW_SECURITY_OPTIONS` config is set to true.
        """
        return self.add_option("max_src_file_size", size)

    def max_animation_frames(self, size: int) -> "Image":
        """
        Allows redefining `IMGPROXY_MAX_ANIMATION_FRAMES` config.

        Since this option allows redefining a security restriction, its usage is not allowed
        unless the `IMGPROXY_ALLOW_SECURITY_OPTIONS` config is set to true.
        """
        return self.add_option("max_animation_frames", size)

    def max_animation_frame_resolution(self, size: int) -> "Image":
        """
        Allows redefining `IMGPROXY_MAX_ANIMATION_FRAME_RESOLUTION` config.

        Since this option allows redefining a security restriction, its usage is not allowed
        unless the `IMGPROXY_ALLOW_SECURITY_OPTIONS` config is set to true.
        """
        return self.add_option("max_animation_frame_resolution", size)

    def _source_url_needs_encoding(self) -> bool:
        """
        Return a boolean if a source URL needs encoding with base64.
        """
        if self.url_escape_regex.search(self._source_url):
            return True
        return False

    @cached_property
    def url(self) -> str:
        options_path = "/".join(self.options)

        # Prefix the path with / - only if processing options are given (or the URL will be
        # invalid)
        if options_path:
            options_path = f"/{options_path}"

        options_path_bytes = options_path.encode()

        if self._source_url_needs_encoding():
            image_path = b"/" + base64.urlsafe_b64encode(self._source_url.encode()).rstrip(b"=")
        else:
            image_path = f"/plain/{self._source_url}".encode()

        if self.imgproxy.key and self.imgproxy.salt and True:
            unsigned_path = options_path_bytes + image_path
            digest = hmac.new(
                key=self.imgproxy.key,
                msg=self.imgproxy.salt + unsigned_path,
                digestmod=hashlib.sha256,
            ).digest()
            signature = base64.urlsafe_b64encode(digest).rstrip(b"=")

            full_path = (b"/" + signature + unsigned_path).decode()
        else:
            # No signature checking - the signature part may contain anything
            full_path = (options_path_bytes + image_path).decode()

        return f"{self.imgproxy.url}{full_path}"
