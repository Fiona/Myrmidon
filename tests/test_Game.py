import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from myrmidon import Game


class GetDistanceTest(unittest.TestCase):

    def test_returns_correct_value_for_quadrant_1(self):
        self.assertAlmostEqual(5, Game.get_distance((2, 4), (5, 8)), 3)

    def test_returns_correct_value_for_quadrant_2(self):
        self.assertAlmostEqual(5, Game.get_distance((-2, 4), (-5, 8)), 3)

    def test_returns_correct_value_for_quadrant_3(self):
        self.assertAlmostEqual(5, Game.get_distance((-2, -4), (-5, -8)), 3)

    def test_returns_correct_value_for_quadrant_4(self):
        self.assertAlmostEqual(5, Game.get_distance((2, -4), (5, -8)), 3)

    def test_returns_correct_value_for_float_parameters(self):
        self.assertAlmostEqual(7.469, Game.get_distance((2.5, 3.2), (5.8, 9.9)), 3)

    def test_returns_zero_for_identical_points(self):
        self.assertEqual(0, Game.get_distance((1, 2), (1, 2)))


class MoveForwardTest(unittest.TestCase):

    def test_returns_correct_value_for_quadrant_1(self):
        result = Game.move_forward((4, 5), 10.0, 20)
        self.assertAlmostEqual(13.397, result[0], 3)
        self.assertAlmostEqual(8.420,  result[1], 3)

    def test_returns_correct_value_for_quadrant_2(self):
        result = Game.move_forward((4, 5), 10.0, 20+90)
        self.assertAlmostEqual(0.580,  result[0], 3)
        self.assertAlmostEqual(14.397, result[1], 3)

    def test_returns_correct_value_for_quadrant_3(self):
        result = Game.move_forward((4, 5), 10.0, 20+180)
        self.assertAlmostEqual(-5.397, result[0], 3)
        self.assertAlmostEqual( 1.580, result[1], 3)

    def test_returns_correct_value_for_quadrant_4(self):
        result = Game.move_forward((4, 5), 10.0, 20-90)
        self.assertAlmostEqual( 7.420, result[0], 3)
        self.assertAlmostEqual(-4.397, result[1], 3)

    def test_returns_correct_value_for_zero_distance(self):
        result = Game.move_forward((4, 5), 0, 20)
        self.assertEqual((4, 5), tuple(result))

    def test_returns_correct_value_for_negative_distance(self):
        result = Game.move_forward((4, 5), -10.0, 20)
        self.assertAlmostEqual(-5.397, result[0], 3)
        self.assertAlmostEqual( 1.580, result[1], 3)

    def test_returns_correct_value_for_non_normalised_angle(self):
        result = Game.move_forward((4, 5), 10.0, 380)
        self.assertAlmostEqual(13.397, result[0], 3)
        self.assertAlmostEqual(8.420,  result[1], 3)


class AngleBetweenPointsTest(unittest.TestCase):

    def test_returns_correct_value_for_quadrant_1(self):
        self.assertAlmostEqual(71.565, Game.angle_between_points((1, 2), (2, 5)), 3)

    def test_returns_correct_value_for_quadrant_2(self):
        self.assertAlmostEqual(135.000, Game.angle_between_points((1, 2), (-2, 5)), 3)

    def test_returns_correct_value_for_quadrant_3(self):
        self.assertAlmostEqual(246.801, Game.angle_between_points((1, 2), (-2, -5)), 3)

    def test_returns_correct_value_for_quadrant_4(self):
        self.assertAlmostEqual(278.13, Game.angle_between_points((1, 2), (2, -5)), 3)

    def test_returns_zero_for_identical_points(self):
        self.assertEqual(0, Game.angle_between_points((1, 2), (1, 2)))

    def test_returns_correct_value_when_second_directly_to_the_right_of_first(self):
        self.assertEqual(0, Game.angle_between_points((1, 2), (3, 2)))

    def test_returns_correct_value_when_second_directly_to_the_left_of_first(self):
        self.assertEqual(180, Game.angle_between_points((1, 2), (-2, 2)))

    def test_returns_correct_value_when_second_directly_below_first(self):
        self.assertEqual(90, Game.angle_between_points((1, 2), (1, 4)))

    def test_returns_correct_value_when_second_directly_above_first(self):
        self.assertEqual(270, Game.angle_between_points((1, 2), (1, -2)))


class NormaliseAngleTest(unittest.TestCase):

    def test_returns_correct_value_for_positive_under_360(self):
        self.assertEqual(45, Game.normalise_angle(45))

    def test_returns_correct_value_for_positive_over_360(self):
        self.assertEqual(10, Game.normalise_angle(370))

    def test_returns_correct_value_for_negative_over_minus_360(self):
        self.assertEqual(270, Game.normalise_angle(-90))

    def test_returns_correct_value_for_negative_under_minus_360(self):
        self.assertEqual(350, Game.normalise_angle(-370))

    def test_returns_zero_for_zero(self):
        self.assertEqual(0, Game.normalise_angle(0))

    def test_returns_zero_for_360(self):
        self.assertEqual(0, Game.normalise_angle(360))


class AngleDifferenceTest(unittest.TestCase):

    def test_returns_correct_value_when_difference_is_small_positive(self):
        self.assertEqual(20, Game.angle_difference(30, 50))

    def test_returns_correct_value_when_difference_is_small_negative(self):
        self.assertEqual(-20, Game.angle_difference(50, 30))

    def test_returns_correct_value_when_difference_is_positive_and_crosses_wrap(self):
        self.assertEqual(20, Game.angle_difference(350, 10))

    def test_returns_correct_value_when_difference_is_negative_and_crosses_wrap(self):
        self.assertEqual(-20, Game.angle_difference(10, 350))

    def test_returns_correct_value_when_difference_is_small_positive_but_angles_not_normalised(self):
        self.assertEqual(20, Game.angle_difference(-330, 410))

    def test_returns_correct_value_when_difference_is_small_negative_but_angles_not_normalised(self):
        self.assertEqual(-20, Game.angle_difference(410, -330))

    def test_returns_zero_when_angles_are_the_same(self):
        self.assertEqual(0, Game.angle_difference(45, 45))

    def test_returns_zero_when_non_normalised_angles_are_equivalent(self):
        self.assertEqual(0, Game.angle_difference(380, -340))


class NearAngleTest(unittest.TestCase):

    def test_returns_incremented_angle_when_further_away_than_increment_in_positive_direction(self):
        self.assertEqual(55, Game.near_angle(45, 135, 10))

    def test_returns_incremented_angle_when_further_away_than_increment_in_negative_direction(self):
        self.assertEqual(35, Game.near_angle(45, 15, 10))

    def test_returns_target_angle_when_closer_than_increment_in_positive_direction(self):
        self.assertEqual(135, Game.near_angle(130, 135, 10))

    def test_returns_target_angle_when_closer_than_increment_in_negative_direction(self):
        self.assertEqual(135, Game.near_angle(140, 135, 10))

    def test_returns_target_angle_when_at_target_angle(self):
        self.assertEqual(135, Game.near_angle(135, 135, 10))

    def test_returns_incremented_angle_when_segment_further_away_than_increment_in_pos_direction(self):
        self.assertEqual(55, Game.near_angle(45, 135, 10, 20))

    def test_returns_incremented_angle_when_segment_further_away_than_increment_in_neg_direction(self):
        self.assertEqual(110, Game.near_angle(120, 15, 10, 20))

    def test_returns_target_angle_when_segment_closer_than_increment_in_pos_direction(self):
        self.assertEqual(55, Game.near_angle(45, 55, 20, 5))

    def test_returns_target_angle_when_segment_closer_than_increment_in_neg_direction(self):
        self.assertEqual(30, Game.near_angle(45, 30, 20, 5))

    def test_returns_same_angle_when_within_target_segment(self):
        self.assertEqual(45, Game.near_angle(45, 30, 10, 20))

    def test_returns_incremented_angle_when_given_non_normalised_angles(self):
        self.assertEqual(50, Game.near_angle(-320, 420, 10))


class RotatePointTest(unittest.TestCase):

    def test_returns_correct_value_for_quadrant_1(self):
        result = Game.rotate_point(2, 3, 10)
        self.assertAlmostEqual(1.449, result[0], 3)
        self.assertAlmostEqual(3.302, result[1], 3)

    def test_returns_correct_value_for_quadrant_2(self):
        result = Game.rotate_point(2, 3, 100)
        self.assertAlmostEqual(-3.302, result[0], 3)
        self.assertAlmostEqual( 1.449, result[1], 3)

    def test_returns_correct_value_for_quadrant_3(self):
        result = Game.rotate_point(2, 3, 170)
        self.assertAlmostEqual(-2.491, result[0], 3)
        self.assertAlmostEqual(-2.607, result[1], 3)

    def test_returns_correct_value_for_quadrant_4(self):
        result = Game.rotate_point(2, 3, 280)
        self.assertAlmostEqual( 3.302, result[0], 3)
        self.assertAlmostEqual(-1.449, result[1], 3)

    def test_returns_origin_when_point_is_at_origin(self):
        result = Game.rotate_point(0, 0, 90)
        self.assertEqual(0, result[0])
        self.assertEqual(0, result[1])


class RotatePointAboutPointTest(unittest.TestCase):

    def test_returns_correct_value_for_quadrant_1(self):
        result = Game.rotate_point_about_point(2, 3, 10, 6, 7)
        self.assertAlmostEqual(2.755, result[0], 3)
        self.assertAlmostEqual(2.366, result[1], 3)

    def test_returns_correct_value_for_quadrant_2(self):
        result = Game.rotate_point_about_point(2, 3, 100, 6, 7)
        self.assertAlmostEqual(10.634, result[0], 3)
        self.assertAlmostEqual( 3.755, result[1], 3)

    def test_returns_correct_value_for_quadrant_3(self):
        result = Game.rotate_point_about_point(2, 3, 190, 6, 7)
        self.assertAlmostEqual( 9.245, result[0], 3)
        self.assertAlmostEqual(11.634, result[1], 3)

    def test_returns_correct_value_for_quadrant_4(self):
        result = Game.rotate_point_about_point(2, 3, 280, 6, 7)
        self.assertAlmostEqual( 1.366, result[0], 3)
        self.assertAlmostEqual(10.245, result[1], 3)

    def test_returns_pivot_point_when_same_as_given_point(self):
        result = Game.rotate_point_about_point(2, 3, 100, 2, 3)
        self.assertEqual(2, result[0])
        self.assertEqual(3, result[1])


class PointInRectangleTest(unittest.TestCase):

    def test_returns_true_when_point_inside_rectangle(self):
        self.assertTrue(Game.point_in_rectangle((5, 6), (-2, -3), (10, 12)))

    def test_returns_false_when_point_is_south_east_of_rectangle(self):
        self.assertFalse(Game.point_in_rectangle((11, 13), (-2, -3), (10, 12)))

    def test_returns_false_when_point_is_south_of_rectangle(self):
        self.assertFalse(Game.point_in_rectangle((0, 13), (-2, -3), (10, 12)))

    def test_returns_false_when_point_is_south_west_of_rectangle(self):
        self.assertFalse(Game.point_in_rectangle((-5, 13), (-2, -3), (10, 12)))

    def test_returns_false_when_point_is_west_of_rectangle(self):
        self.assertFalse(Game.point_in_rectangle((-5, 1), (-2, -3), (10, 12)))

    def test_returns_false_when_point_is_north_west_of_rectangle(self):
        self.assertFalse(Game.point_in_rectangle((-5, -5), (-2, -3), (10, 12)))

    def test_returns_false_when_point_is_north_of_rectangle(self):
        self.assertFalse(Game.point_in_rectangle((0, -5), (-2, -3), (10, 12)))

    def test_returns_false_when_point_is_north_east_of_rectangle(self):
        self.assertFalse(Game.point_in_rectangle((14, -5), (-2, -3), (10, 12)))

    def test_returns_false_when_point_is_east_of_rectangle(self):
        self.assertFalse(Game.point_in_rectangle((14, 1), (-2, -3), (10, 12)))

    def test_returns_false_when_point_on_top_edge(self):
        self.assertFalse(Game.point_in_rectangle((0, -3), (-2, -3), (10, 12)))

    def test_returns_false_when_point_on_left_edge(self):
        self.assertFalse(Game.point_in_rectangle((-2, 0), (-2, -3), (10, 12)))

    def test_returns_false_when_point_on_bottom_edge(self):
        self.assertFalse(Game.point_in_rectangle((0, 12), (-2, -3), (10, 12)))

    def test_returns_false_when_point_on_right_edge(self):
        self.assertFalse(Game.point_in_rectangle((10, 0), (-2, -3), (10, 12)))


class LerpTest(unittest.TestCase):

    def test_returns_correct_one_third_value(self):
        self.assertAlmostEqual(6.667, Game.lerp(5.0, 10.0, 1.0/3), 3)

    def test_returns_correct_two_thirds_value(self):
        self.assertAlmostEqual(8.333, Game.lerp(5.0, 10.0, 1.0/3*2), 3)

    def test_returns_correct_start_value(self):
        self.assertEqual(5.0, Game.lerp(5.0, 10.0, 0.0))

    def test_returns_correct_end_value(self):
        self.assertEqual(10.0, Game.lerp(5.0, 10.0, 1.0))


class SlerpTest(unittest.TestCase):

    def test_returns_correct_start_value(self):
        self.assertEqual(5.0, Game.slerp(5.0, 10.0, 0.0))

    def test_returns_correct_end_value(self):
        self.assertEqual(10.0, Game.slerp(5.0, 10.0, 1.0))

    def test_returns_correct_mid_value(self):
        self.assertEqual(7.5, Game.slerp(5.0, 10.0, 0.5))

    def test_doesnt_return_linear_value_for_one_third(self):
        self.assertNotAlmostEquals(6.667, Game.slerp(5.0, 10.0, 1.0/3), 3)

    def test_doesnt_return_linear_value_for_two_thirds(self):
        self.assertNotAlmostEquals(8.333, Game.slerp(5.0, 10.0, 1.0/3*2), 3)


class TimerTicksTest(unittest.TestCase):

    def test_returns_iterable(self):
        val = Game.timer_ticks(3)
        next(val)

    def test_iterator_throws_stop_after_given_number_of_iterations(self):
        val = Game.timer_ticks(3)
        next(val)
        next(val)
        next(val)
        with self.assertRaises(StopIteration):
            next(val)

    def test_iterator_returns_iterations_made_and_target_iterations(self):
        val = Game.timer_ticks(3)
        self.assertEqual((1,3), next(val))
        self.assertEqual((2,3), next(val))
        self.assertEqual((3,3), next(val))


class CollisionPointToRectangleTest(unittest.TestCase):

    class TestPoint(object):
        x, y = 0, 0
        def collision_point_calculate_point(self):
            return self.x,self.y

    class TestRect(object):
        x, y, w, h = 0, 0, 0, 0
        rotation = 0
        corners = (0,0),(0,0),(0,0),(0,0)
        def collision_rectangle_calculate_corners(self):
            return {'ul': self.corners[0], 'ur': self.corners[1], 'lr': self.corners[2], 'll': self.corners[3]}
        def collision_rectangle_size(self):
            return self.w,self.h

    def _unrotated_rect(self):
        r = CollisionPointToRectangleTest.TestRect()
        r.x, r.y = 4, 5
        r.w, r.h = 10, 11
        r.rotation = 0
        r.corners = (-1,-0.5),(9,-0.5),(9,10.5),(-1,10.5)
        return r

    def test_returns_true_when_point_inside_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = 5, 6
        r = self._unrotated_rect()
        self.assertTrue(Game.collision_point_to_rectangle(p, r))

    def test_returns_false_when_point_north_west_of_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = -3, -3
        r = self._unrotated_rect()
        self.assertFalse(Game.collision_point_to_rectangle(p, r))

    def test_returns_false_when_point_north_of_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = 6, -3
        r = self._unrotated_rect()
        self.assertFalse(Game.collision_point_to_rectangle(p, r))

    def test_returns_false_when_point_north_east_of_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = 11, -3
        r = self._unrotated_rect()
        self.assertFalse(Game.collision_point_to_rectangle(p, r))

    def test_returns_false_when_point_east_of_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = 11, 5
        r = self._unrotated_rect()
        self.assertFalse(Game.collision_point_to_rectangle(p, r))

    def test_returns_false_when_point_south_east_of_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = 11, 12
        r = self._unrotated_rect()
        self.assertFalse(Game.collision_point_to_rectangle(p, r))

    def test_returns_false_when_point_south_of_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = 5, 12
        r = self._unrotated_rect()
        self.assertFalse(Game.collision_point_to_rectangle(p, r))

    def test_returns_false_when_point_south_west_of_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = -3, 12
        r = self._unrotated_rect()
        self.assertFalse(Game.collision_point_to_rectangle(p, r))

    def test_returns_false_when_point_west_of_unrotated(self):
        p = CollisionPointToRectangleTest.TestPoint()
        p.x, p.y = -3, 5
        r = self._unrotated_rect()
        self.assertFalse(Game.collision_point_to_rectangle(p, r))


class CollisionPointToCircleTest(unittest.TestCase):

    class TestPoint(object):
        x, y = 0, 0
        def collision_point_calculate_point(self):
            return self.x,self.y

    class TestCircle(object):
        x, y = 0, 0
        rad = 0
        def collision_circle_calculate_radius(self):
            return self.rad

    def test_returns_true_when_at_same_position(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 3.0, 4.0
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertTrue(Game.collision_point_to_circle(p, c))

    def test_returns_true_when_in_radius_quadrant_1(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 3.6, 4.6
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertTrue(Game.collision_point_to_circle(p, c))

    def test_returns_true_when_in_radius_quadrant_2(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 2.4, 4.6
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertTrue(Game.collision_point_to_circle(p, c))

    def test_returns_true_when_in_radius_quadrant_3(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 2.4, 3.4
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertTrue(Game.collision_point_to_circle(p, c))

    def test_returns_true_when_in_radius_quadrant_4(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 3.6, 3.4
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertTrue(Game.collision_point_to_circle(p, c))

    def test_returns_false_when_outside_radius_quadrant_1(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 3.8, 4.8
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertFalse(Game.collision_point_to_circle(p, c))

    def test_returns_false_when_outside_radius_quadrant_2(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 2.2, 4.8
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertFalse(Game.collision_point_to_circle(p, c))

    def test_returns_false_when_outside_radius_quadrant_3(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 2.2, 3.2
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertFalse(Game.collision_point_to_circle(p, c))

    def test_returns_false_when_outside_radius_quadrant_4(self):
        p = CollisionPointToCircleTest.TestPoint()
        p.x, p.y = 3.8, 3.2
        c = CollisionPointToCircleTest.TestCircle()
        c.x, c.y, c.rad = 3.0, 4.0, 1.0
        self.assertFalse(Game.collision_point_to_circle(p, c))


class CollisionPointToPointTest(unittest.TestCase):

    class TestPoint(object):
        x, y = 0, 0
        def collision_point_calculate_point(self):
            return self.x,self.y

    def test_returns_false_when_points_are_not_the_same(self):
        p1 = CollisionPointToPointTest.TestPoint()
        p1.x, p1.y = 3.0, 4.0
        p2 = CollisionPointToPointTest.TestPoint()
        p2.x, p2.y = 3.5, 4.5
        self.assertFalse(Game.collision_point_to_point(p1, p2))

    def test_returns_false_when_points_are_different_but_same_x_val(self):
        p1 = CollisionPointToPointTest.TestPoint()
        p1.x, p1.y = 3.0, 4.0
        p2 = CollisionPointToPointTest.TestPoint()
        p2.x, p2.y = 3.0, 4.5
        self.assertFalse(Game.collision_point_to_point(p1, p2))

    def test_returns_false_when_points_are_different_but_same_y_val(self):
        p1 = CollisionPointToPointTest.TestPoint()
        p1.x, p1.y = 3.0, 4.0
        p2 = CollisionPointToPointTest.TestPoint()
        p2.x, p2.y = 3.5, 4.0
        self.assertFalse(Game.collision_point_to_point(p1, p2))

    def test_returns_true_when_points_are_the_same(self):
        p1 = CollisionPointToPointTest.TestPoint()
        p1.x, p1.y = 3.0, 4.0
        p2 = CollisionPointToPointTest.TestPoint()
        p2.x, p2.y = 3.0, 4.0
        self.assertTrue(Game.collision_point_to_point(p1, p2))


class HSVAToColourTest(unittest.TestCase):

    def _stub_colour(self, rgba):
        r, g, b, a = rgba
        return r/255.0, g/255.0, b/255.0, a/255.0

    @mock.patch("myrmidon.Game.engine")
    def test_returns_white_for_no_sat_and_full_val(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertEqual((1.0, 1.0, 1.0, 1.0), Game.hsva_to_colour(0, 0.0, 1.0, 255))

    @mock.patch("myrmidon.Game.engine")
    def test_returns_black_for_no_val(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertEqual((0.0, 0.0, 0.0, 1.0), Game.hsva_to_colour(0, 1.0, 0.0, 255))

    @mock.patch("myrmidon.Game.engine")
    def test_returns_red_for_hue_0(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertEqual((1.0, 0.0, 0.0, 1.0), Game.hsva_to_colour(0, 1.0, 1.0, 255))

    @mock.patch("myrmidon.Game.engine")
    def test_returns_green_for_hue_120(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertEqual((0.0, 1.0, 0.0, 1.0), Game.hsva_to_colour(120, 1.0, 1.0, 255))

    @mock.patch("myrmidon.Game.engine")
    def test_returns_blue_for_hue_240(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertEqual((0.0, 0.0, 1.0, 1.0), Game.hsva_to_colour(240, 1.0, 1.0, 255))

    @mock.patch("myrmidon.Game.engine")
    def test_returns_yellow_for_hue_60(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertEqual((1.0, 1.0, 0.0, 1.0), Game.hsva_to_colour(60, 1.0, 1.0, 255))

    @mock.patch("myrmidon.Game.engine")
    def test_returns_cyan_for_hue_180(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertEqual((0.0, 1.0, 1.0, 1.0), Game.hsva_to_colour(180, 1.0, 1.0, 255))

    @mock.patch("myrmidon.Game.engine")
    def test_returns_magenta_for_hue_300(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertEqual((1.0, 0.0, 1.0, 1.0), Game.hsva_to_colour(300, 1.0, 1.0, 255))

    @mock.patch("myrmidon.Game.engine")
    def test_lowering_val_lowers_appropriate_rgb_channels_uniformally(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        result = Game.hsva_to_colour(60, 1.0, 0.25, 255)
        self.assertAlmostEqual(0.25, result[0], 2)
        self.assertAlmostEqual(0.25, result[1], 2)
        self.assertAlmostEqual(0.0,  result[2], 2)
        self.assertEqual(1.0, result[3])

    @mock.patch("myrmidon.Game.engine")
    def test_lowering_saturation_increases_appropriate_rgb_channels_uniformally(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        result = Game.hsva_to_colour(60, 0.25, 1.0, 255)
        self.assertAlmostEqual(1.0,  result[0], 2)
        self.assertAlmostEqual(1.0,  result[1], 2)
        self.assertAlmostEqual(0.75, result[2], 2)
        self.assertEqual(1.0, result[3])

    @mock.patch("myrmidon.Game.engine")
    def test_returns_correct_alpha_value(self, engines):
        engines['gfx'].rgb_to_colour = self._stub_colour
        self.assertAlmostEqual(0.25, Game.hsva_to_colour(0, 1.0, 1.0, 64)[3], 2)
