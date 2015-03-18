
import sys
import os.path
import math

from myrmidon import Game, Entity
from myrmidon.consts import *
from pygame.locals import *


class Test(Entity):

    TEXT_OFFSET = 48
    description = ""

    def execute(self, position):
        self.x, self.y = position
        self.image = Application.G_WORD
        self.desc_obj = Game.write_text(self.x, self.y+self.TEXT_OFFSET, Application.F_MAIN, ALIGN_TOP,
                                        self.description)
        self.desc_obj.colour = (1, 1, 1)
        self._setup()
        while True:
            self._update()
            yield

    def _setup(self):
        pass

    def _update(self):
        pass


class TextTest(Test):

    text = None

    def _setup(self):
        self.image = None
        self.text = Game.write_text(self.x, self.y, Application.F_BIG, ALIGN_CENTER, "Test")


class TestNormal(Test):

    description = "Normal"


class TestImage(Test):

    description = "Image (switching)"

    def _setup(self):
        self.time = 0

    def _update(self):
        self.time += 1
        if (self.time//20) % 2 == 0:
            self.image = Application.G_WORD
        else:
            self.image = Application.G_J


class TestRotation(Test):

    description = "Rotating (clockwise)"

    def _update(self):
        self.rotation += 5


class TestScaling(Test):

    description = "Scaling (0.5 to 2.0)"

    def _update(self):
        if self.scale < 2.0:
            self.scale += 0.05
        else:
            self.scale = 0.5


class TestFlipHoriz(Test):

    description = "Flipped horizontal"

    def _setup(self):
        self.flip_horizontal = True


class TestFlipVert(Test):

    description = "Flipped vertical"

    def _setup(self):
        self.flip_vertical = True


class TestFlipBoth(Test):

    description = "Flipped both"

    def _setup(self):
        self.flip_horizontal = True
        self.flip_vertical = True


class TestAlpha(Test):

    description = "Alpha (0.0 to 1.0)"

    def _update(self):
        if self.alpha < 1.0:
            self.alpha += 0.02
        else:
            self.alpha = 0.0


class TestYellow(Test):

    description = "Colour (yellow)"

    def _setup(self):
        self.colour = (1.0, 1.0, 0.0)


class TestCyan(Test):

    description = "Colour (cyan)"

    def _setup(self):
        self.colour = (0.0, 1.0, 1.0)


class TestMagenta(Test):

    description = "Colour (magenta)"

    def _setup(self):
        self.colour = (1.0, 0.0, 1.0)


class TestZSort(Test):

    description = "Z-sorting (top left on top)"

    def _setup(self):
        self.image = None
        for i in range(3):
            e = Entity()
            e.image = Application.G_WORD
            e.x = self.x - 10 + i*10
            e.y = self.y - 10 + i*10
            e.z = i


class TestPosition(Test):

    description = "X and Y (circular motion)"

    def _setup(self):
        self.centre = self.x, self.y
        self.ang = 0

    def _update(self):
        self.ang += 0.1
        self.x = self.centre[0] + math.cos(self.ang) * 10
        self.y = self.centre[1] + math.sin(self.ang) * 10


class TestBlend(Test):

    description = "Blending"

    def _setup(self):
        self.image = None
        for i in range(2):
            e = Entity()
            e.image = Application.G_WORD
            e.x = self.x - 5 + i*10
            e.y = self.y - 5 + i*10
            e.blend = True


class TestHideShow(Test):

    description = "Show & Hide (hide shorter)"

    def _setup(self):
        self.time = 0
        self.hidden = False

    def _update(self):
        self.time += 1
        if self.time < 5 and not self.hidden:
            self.hide()
            self.hidden = True
        if self.time >= 5 and self.hidden:
            self.show()
            self.hidden = False
        self.time %= 30


class ChainLink(Entity):

    def execute(self, priority, previous):
        self.image = Application.G_WORD
        self.priority = priority
        self.previous = previous
        while True:
            self.rotation = self.previous.rotation
            self.x = self.previous.x + math.cos(math.radians(self.rotation)) * 30
            self.y = self.previous.y + math.sin(math.radians(self.rotation)) * 30
            yield


class TestPriority(Test):

    description = "Priority (lagging)"

    def _setup(self):
        self.image = None
        self.time = 0
        self.links = []
        for i in range(3):
            self.links.append(ChainLink(i, self.links[-1] if len(self.links) > 0 else self))

    def _update(self):
        self.time += 0.5
        self.rotation = 0+math.cos(self.time)*30


class TestImageSequence(Test):

    description = "Img Sequence (animating)"

    def _setup(self):
        self.time = 0
        self.image = Application.G_J

    def _update(self):
        self.time += 1
        self.image_seq = (self.time // 5) % 4


class TestDrawCentrePoint(Test):

    description = "Centre point (TL-BR)"

    def _setup(self):
        self.time = 0

    def _update(self):
        self.time = (self.time+1) % 30
        if self.time < 15 and self.centre_point != (0, 0):
            self.centre_point = (0, 0)
        elif self.time >= 15 and self.centre_point != (128, 64):
            self.centre_point = (128, 64)


class TestRotateCentrePoint(Test):

    description = "CP Rotation (cw around BR)"

    def _setup(self):
        self.centre_point = (128, 64)

    def _update(self):
        self.rotation += 5


class TestScaleCentrePoint(Test):

    description = "CP scale (around BR)"

    def _setup(self):
        self.centre_point = (128, 64)

    def _update(self):
        if self.scale < 2.0:
            self.scale += 0.05
        if self.scale >= 2.0:
            self.scale = 0.5


class TestFlipCentrePoint(Test):

    description = "CP flip (both around BR)"

    def _setup(self):
        self.centre_point = (128, 64)
        self.flip_horizontal = True
        self.flip_vertical = True


class StopperStarter(Entity):

    def execute(self, entity):
        self.time = 0
        self.stopped = False
        while True:
            self.time = (self.time + 1) % 30
            if self.time < 10 and not self.stopped:
                entity.stop_executing()
                self.stopped = True
            if self.time >= 10 and self.stopped:
                entity.start_executing()
                self.stopped = False
            yield


class TestStopExecuting(Test):

    description = "Stop (stop shorter)"

    def _setup(self):
        self.time = 0
        self.start_x, self.start_y = self.x, self.y
        StopperStarter(self)

    def _update(self):
        self.time += 1
        self.x, self.y = self.start_x + math.cos(self.time/10.0) * 20, self.start_y + math.sin(self.time/10.0) * 20


class TestClip(Test):

    description = "Clip ('urmid')"

    def _setup(self):
        self.clip = ((self.x-20, self.y-16), (63, 32))


class TestColourAndAlpha(Test):

    description = "Colour & Alpha (Y, 25%)"

    def _setup(self):
        self.colour = (1.0, 1.0, 0.0)
        self.alpha = 0.25


class TestTextPosition(TextTest):

    description = "Text position (circular)"

    def _setup(self):
        TextTest._setup(self)
        self.time = 0

    def _update(self):
        self.time += 0.1
        self.text.x = self.x + math.cos(self.time)*10
        self.text.y = self.y + math.sin(self.time)*10


class TestTextRotation(TextTest):

    """description = "Text rotation (clkws)"

    def _update(self):
        self.text.rotation += 0.1"""


class TestTextScaling(TextTest):

    """description = "Text scaling (0.5-2.0)"

    def _setup(self):
        TextTest._setup(self)
        self.text.scale = 0.5

    def _update(self):
        self.text.scale += 0.1
        if self.text.scale > 2.0:
            self.text.scale = 0.5"""


class TestTextXFlip(TextTest):

    description = "Text H flip"

    def _setup(self):
        TextTest._setup(self)
        self.text.flip_horizontal = True


class TestTextYFlip(TextTest):

    description = "Text V flip"

    def _setup(self):
        TextTest._setup(self)
        self.text.flip_vertical = True


class TestTextXAndYFlip(TextTest):

    description = "Text H&V flip"

    def _setup(self):
        TextTest._setup(self)
        self.text.flip_vertical = True
        self.text.flip_horizontal = True


class TestTextAlpha(TextTest):

    description = "Text alpha (0.0-1.0)"

    def _update(self):
        self.text.alpha += 0.025
        if self.text.alpha >= 1.0:
            self.text.alpha = 0.0


class TestTextYellow(TextTest):

    description = "Text colour (yellow)"

    def _setup(self):
        TextTest._setup(self)
        self.text.colour = (1.0, 1.0, 0.0)


class TestTextCyan(TextTest):

    description = "Text colour (cyan)"

    def _setup(self):
        TextTest._setup(self)
        self.text.colour = (0.0, 1.0, 1.0)


class TestTextMagenta(TextTest):

    description = "Text colour (magenta)"

    def _setup(self):
        TextTest._setup(self)
        self.text.colour = (1.0, 0.0, 1.0)


class TestTextBlend(TextTest):

    description = "Text blending"

    def _setup(self):
        TextTest._setup(self)
        self.text.destroy()
        t1 = Game.write_text(self.x-10, self.y-10, font=Application.F_BIG, text="test", alignment=ALIGN_CENTRE)
        t1.colour = (0.75, 0.75, 0.75)
        t1.blend = True
        t2 = Game.write_text(self.x+00, self.y+00, font=Application.F_BIG, text="test", alignment=ALIGN_CENTRE)
        t2.colour = (0.75, 0.75, 0.75)
        t2.blend = True
        t3 = Game.write_text(self.x+10, self.y+10, font=Application.F_BIG, text="test", alignment=ALIGN_CENTRE)
        t3.colour = (0.75, 0.75, 0.75)
        t3.blend = True


class TestTextShowAndHide(TextTest):

    description = "Text show & hide (hide shorter)"

    def _setup(self):
        TextTest._setup(self)
        self.time = 0.0
        self.hidden = False

    def _update(self):
        self.time = (self.time+1) % 30
        if self.time < 5 and not self.hidden:
            self.text.hide()
            self.hidden = True
        if self.time >= 5 and self.hidden:
            self.text.show()
            self.hidden = False


class TestTextCentrePoint(TextTest):

    description = "Text centre point (TL-BR)"

    def _setup(self):
        TextTest._setup(self)
        self.time = 0.0

    def _update(self):
        self.time = (self.time+1) % 30
        if self.time < 15 and self.text.centre_point != (0.0, 0.0):
            self.text.centre_point = (0.0, 0.0)
        if self.time >= 15 and self.text.centre_point != (100, 100):
            self.text.centre_point = (100, 100)


class TestTextClip(TextTest):

    description = "Text clipping ('es')"

    def _setup(self):
        TextTest._setup(self)
        self.text.clip = ((self.x-22, self.y-10), (40, 24))


class Application(Entity):

    G_WORD = None
    G_J = None
    F_MAIN = None

    def execute(self):
        self._load_media()
        self._create_tests(TestNormal, TestImage, TestRotation, TestScaling, TestFlipHoriz, TestFlipVert, TestFlipBoth,
                           TestAlpha, TestYellow, TestCyan, TestMagenta, TestZSort, TestPosition, TestBlend,
                           TestHideShow, TestPriority, TestImageSequence, TestDrawCentrePoint, TestRotateCentrePoint,
                           TestScaleCentrePoint, TestFlipCentrePoint, TestStopExecuting,
                           TestClip, TestColourAndAlpha, TestTextPosition, TestTextRotation, TestTextScaling,
                           TestTextXFlip, TestTextYFlip,
                           TestTextXAndYFlip, TestTextAlpha, TestTextYellow, TestTextCyan, TestTextMagenta,
                           TestTextBlend, TestTextShowAndHide, TestTextCentrePoint, TestTextClip)
        while True:
            if Game.keyboard_key_down(K_ESCAPE):
                sys.exit()
            yield

    def _load_media(self):
        Application.F_MAIN = Game.load_font(os.path.join("media", "comick_book_caps.ttf"), 8)
        Application.F_BIG = Game.load_font(os.path.join("media", "comick_book_caps.ttf"), 32)
        Application.G_WORD = Game.load_image(os.path.join("media", "word.png"))
        Application.G_J = Game.load_image(os.path.join("media", "j.png"), sequence=True, width=32)

    def _create_tests(self, *classes):
        for i, cls in enumerate(classes):
            y, x = divmod(i, 8)
            cls((64+128*x, 64+128*y))

Game.screen_resolution = (1024, 768)
Application()
