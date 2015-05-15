import os
import sys
import random

from myrmidon import Game, Entity
from myrmidon.consts import *
from pygame.locals import *


class TestEntity(Entity):
    def execute(self, window):
        self.window = window
        self.x = (Game.screen_resolution[0] / 2) + random.randint(-200, 200)
        self.y = (Game.screen_resolution[1] / 2) + random.randint(-200, 200)        
        self.image = self.window.I_MYRMIDON
        while True:
            yield
            

class BenchmarkTest(Entity):
    name = "A Benchmark Test"
    num_test_entities = 20
    test_length = 5
    
    def execute(self, window):
        self.window = window
        self.text = Game.write_text(
            Game.screen_resolution[0] / 2, 100,
            self.window.F_BENCHMARK_NAME, ALIGN_CENTER, self.name
            )
        self.average_execution_time = 0.0
        self.average_render_time = 0.0
        self.test_entities = []
        for entity_num in range(self.num_test_entities):
            self.create_single_test_entity()
        self.switch_state("run_test")

    def run_test(self):
        self.execution_times = []
        self.render_times = []
        # Run the test for as long as we should, updating entities
        # where appropriate
        for i in range(self.test_length * Game.target_fps):
            for entity in self.test_entities:
                self.update_entity(entity)
            yield
            self.execution_times.append(Game.frame_execution_time)
            self.render_times.append(Game.frame_render_time)
        # Calculate average execution and render times
        self.average_execution_time = sum(self.execution_times) / len(self.execution_times)
        self.average_render_time = sum(self.render_times) / len(self.render_times)        
        
    def create_single_test_entity(self):
        """Override this in tests, but make sure the base method is called,
        it will return the created entity so you can alter the parameters."""
        self.test_entities.append(TestEntity(self.window))
        return self.test_entities[-1]

    def update_entity(self, entity):
        """Override this to update an entity's parameters frame to frame"""
        pass

    def on_exit(self):
        for x in self.test_entities:
            x.destroy()
        self.text.destroy()


class StaticEntityTest(BenchmarkTest):
    name = "Static Entities"


class TintedStaticEntityTest(BenchmarkTest):
    name = "Tinted Static Entities"
    def create_single_test_entity(self):
        entity = BenchmarkTest.create_single_test_entity(self)
        entity.colour = Game.rgb_to_colour(*[random.randint(50, 200) for i in range(3)])


class MovingEntityTest(BenchmarkTest):
    name = "Moving Entities"
    def create_single_test_entity(self):
        entity = BenchmarkTest.create_single_test_entity(self)
        entity.x_amount = random.choice([-5, 5])
        entity.y_amount = random.choice([-5, 5])
        
    def update_entity(self, entity):
        entity.x += entity.x_amount
        entity.y += entity.y_amount
        if entity.x > Game.screen_resolution[0]:
            entity.x = 0
        if entity.x < 0:
            entity.x = Game.screen_resolution[0]
        if entity.y > Game.screen_resolution[1]:
            entity.y = 0
        if entity.y < 0:
            entity.y = Game.screen_resolution[1]


class RotatingEntityTest(BenchmarkTest):
    name = "Rotating Entities"
    def create_single_test_entity(self):
        entity = BenchmarkTest.create_single_test_entity(self)
        entity.rot_amount = random.choice([-7, 7])
        
    def update_entity(self, entity):
        entity.rotation += entity.rot_amount


class ScalingEntityTest(BenchmarkTest):
    name = "Scaling Entities"
    def create_single_test_entity(self):
        entity = BenchmarkTest.create_single_test_entity(self)
        entity.scale_amount = random.choice([-.2, .24])
        
    def update_entity(self, entity):
        entity.scale += entity.scale_amount
        if entity.scale < .5 or entity.scale > 3.0:
            entity.scale_amount = -entity.scale_amount
        

class Application(Entity):
    tests = [StaticEntityTest, TintedStaticEntityTest, MovingEntityTest,
             RotatingEntityTest, ScalingEntityTest,]
    
    def execute(self):
        self.load_media()
        self.current_test = None
        for test_num, test in enumerate(self.tests):
            # Wait a second for the system to even out
            for i in range(30):
                yield
            # Run the test till it's finished            
            self.current_test = test(self)
            print("Running test {0}/{1}: {2}".format(test_num + 1, len(self.tests), self.current_test.name))
            while self.current_test.is_alive():
                yield
            print("Average execution time: {0:.4f}".format(self.current_test.average_execution_time))
            print("Average render time: {0:.4f}".format(self.current_test.average_render_time))
            print("-------------------------------")
        sys.exit()

    def load_media(self):
        self.I_MYRMIDON = Game.load_image(os.path.join("media", "word.png"))
        self.F_BENCHMARK_NAME = Game.load_font(os.path.join("media", "comick_book_caps.ttf"), 30)
        
        
Game.screen_resolution = (1024, 768)
Game.full_screen = False
#Game.define_engine(*(["kivy"] * 4))
Application()
