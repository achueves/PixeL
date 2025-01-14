import io
import PIL
import asyncio
import aiohttp
import traceback
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class Io:

    def __init__(self):
        pass

    @staticmethod
    def draw(size: Tuple, color: str = None):
        color = 0x36393f if color is None else color
        new_image = Image.new("RGB", size, color=color)
        buff = io.BytesIO()
        new_image.save(buff, 'png')
        buff.seek(0)
        return buff


class Canvas:

    def __init__(self, size: Tuple, color: str = None):
        color = 0x36393f if color is None else color
        size = size if len(size) >= 2 else None
        card = Image.new("RGB", size, color=color)
        buff = io.BytesIO()
        card.save(buff, 'png')
        buff.seek(0)
        self.width = size[0]
        self.height = size[1]
        self.output = buff

    def set_background(self, fp, blur: bool = False):
        canvas = Image.open(self.output)
        size = canvas.size
        bg = Image.open(fp).convert('RGB')
        _bg = bg.resize(size)
        if blur:
            buff = io.BytesIO()
            _bg_blur = _bg.filter(ImageFilter.BLUR)
            _bg_blur.save(buff, 'png')
            buff.seek(0)
            self.output = buff
        else:
            buff = io.BytesIO()
            _bg.save(buff, 'png')
            buff.seek(0)
            self.output = buff

    def add_image(self, fp, resize: Tuple = None, crop: Tuple = None, position: Tuple = None):
        img = Image.open(fp)
        canvas = Image.open(self.output)
        if resize is not None and crop is None:
            auto_align = ((self.width - resize[0]) // 2, (self.height - resize[1]) // 2)
            manual_align = position
            offset = auto_align if position is None else manual_align
            _img = img.resize(resize, resample=0)
            Image.Image.paste(canvas, _img, offset)
            buff = io.BytesIO()
            canvas.save(buff, 'png')
            buff.seek(0)
            self.output = buff
        elif crop is not None and resize is None:
            _img = img.crop(crop)
            dim = _img.size
            auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
            manual_align = position
            offset = auto_align if position is None else manual_align
            Image.Image.paste(canvas, _img, offset)
            buff = io.BytesIO()
            canvas.save(buff, 'png')
            buff.seek(0)
            self.output = buff
        elif crop is None and resize is None:
            size = img.size
            auto_align = ((self.width - size[0]) // 2, (self.height - size[1]) // 2)
            manual_align = (position[0], position[1])
            offset = auto_align if position is None else manual_align
            Image.Image.paste(canvas, img, offset)
            buff = io.BytesIO()
            canvas.save(buff, 'png')
            buff.seek(0)
            self.output = buff
        else:
            raise Exception('Use either Resize or Crop')

    def add_round_image(self, fp, resize: Tuple = None, crop: Tuple = None, position: Tuple = None):
        canvas = Image.open(self.output)
        img = Image.open(fp)
        if resize is not None and crop is None:
            main = img.resize(resize)
            mask = Image.new("L", main.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.pieslice(((0, 0), main.size), 0, 360, fill=255, outline="white")
            dim = main.size
            auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
            manual_align = position
            offset = auto_align if position is None else manual_align
            canvas.paste(main, offset, mask)
            buff = io.BytesIO()
            canvas.save(buff, 'png')
            buff.seek(0)
            self.output = buff
        elif crop is not None and resize is None:
            main = img.crop(crop)
            mask = Image.new("L", main.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.pieslice(((0, 0), main.size), 0, 360, fill=255, outline="white")
            dim = main.size
            auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
            manual_align = position
            offset = auto_align if position is None else manual_align
            canvas.paste(main, offset, mask)
            buff = io.BytesIO()
            canvas.save(buff, 'png')
            buff.seek(0)
            self.output = buff
        elif crop is None and resize is None:
            main = img
            mask = Image.new("L", main.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.pieslice(((0, 0), main.size), 0, 360, fill=255, outline="white")
            dim = main.size
            auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
            manual_align = position
            offset = auto_align if position is None else manual_align
            canvas.paste(main, offset, mask)
            buff = io.BytesIO()
            canvas.save(buff, 'png')
            buff.seek(0)
            self.output = buff
        else:
            raise RuntimeError('Use either Resize or Crop')

    def add_text(self, text: str, auto_align: bool, size: float = None, color: str = None, position: Tuple = None):
        canvas = Image.open(self.output)
        draw = ImageDraw.Draw(canvas)
        text = text
        size = 20 if size is None else size
        color = 'white' if color is None else color
        font = ImageFont.truetype(font='bot/extras/sans.ttf', size=size)
        text_width, text_height = draw.textsize(text, font=font)

        def align(auto: bool, pos):
            if auto is True and pos is None:
                return (self.width - text_width) // 2, (self.height - text_height) // 2

            elif auto is True and pos is not None:
                return (self.width - text_width) // 2, position[1]

            elif auto is False and pos is None:
                return (self.width - text_width) // 2, (self.height - text_height) // 2

            elif auto is False and pos is not None:
                return pos
        draw.text(align(auto_align, position), text, fill=color, font=font)
        buff = io.BytesIO()
        canvas.save(buff, 'png')
        buff.seek(0)
        self.output = buff
