import unittest
import pygaming as pgg
from pygame import Vector2

class TestAnchor(unittest.TestCase):
    """Testing of anchors."""

    def test_init(self):
        self.assertEqual(pgg.anchors.LEFT, pgg.anchors.CENTER_LEFT)
        self.assertEqual(pgg.anchors.Anchor(0., 0.), pgg.anchors.TOP_LEFT)
        self.assertEqual(pgg.anchors.Anchor((1., 1.)), pgg.anchors.BOTTOM_RIGHT)
        with self.assertRaises(ValueError, msg="Anchor must have more than 1 float argument."):
            pgg.anchors.Anchor(0.5)
        with self.assertRaises(ValueError, msg="Anchor argument can be a sequence only if its length is 2."):
            pgg.anchors.Anchor((1., 0.5, 0.3))

        self.assertEqual(pgg.anchors.Anchor(Vector2(0.5, 0.5)), pgg.anchors.Anchor.CENTER)
        self.assertIs(pgg.anchors.Anchor(0.5, 1), pgg.anchors.Anchor.BOTTOM_CENTER,
                      "Instanciating an anchor with arguments corresponding to an already existing anchor should return it.")
        with self.assertRaises(ValueError, msg="Anchors cannot be instanciated with a string."):
            pgg.anchors.Anchor('mmm')
        with self.assertRaises(ValueError, msg="Anchor cannot be instanciated with floats that are not within [0, 1]."):
            pgg.anchors.Anchor(1.5, -10.)
    
    def test_maths(self):
        self.assertEqual(pgg.anchors.BOTTOM_RIGHT/2, pgg.anchors.CENTER,
            "dividing an anchor by something should return an Anchor with divided components."
        )
        self.assertEqual(pgg.anchors.CENTER*2, pgg.anchors.BOTTOM_RIGHT,
            "multiplying an anchor by something should return an Anchor with multiplied components."
        )
        with self.assertRaises(ValueError, msg="Cannot multiply an anchor such that it becomes out of [0, 1] * [0, 1]"):
            x = pgg.anchors.BOTTOM_RIGHT*2
        
        self.assertEqual(pgg.anchors.TOP_LEFT + pgg.anchors.CENTER, pgg.anchors.CENTER)
        self.assertEqual(pgg.anchors.LEFT + pgg.anchors.CENTER, pgg.anchors.BOTTOM)
        with self.assertRaises(ValueError, msg="Cannot add anchors such that it becomes out of [0, 1] * [0, 1]"):
            x = pgg.anchors.Anchor(0.8, 0.8) + pgg.anchors.Anchor(0.3, 0.3)

        self.assertEqual(pgg.anchors.midpoint(pgg.anchors.TOP, pgg.anchors.BOTTOM), pgg.anchors.CENTER, 'The midpoint of two anchors is wrong.')
        self.assertEqual(pgg.anchors.barycenter(
            [pgg.anchors.TOP_LEFT, pgg.anchors.BOTTOM_RIGHT], [3, 1]),
            pgg.anchors.Anchor(0.25, 0.25),
            'The barycenter of two anchors is wrong.'
        )
    
        self.assertEqual(pgg.anchors.TOP[0], 0.5, 'subscripting with 0 should return the x coordinate')
        self.assertEqual(pgg.anchors.BOTTOM[1], 1, 'subscripting with 1 should return the y coordinate')
        self.assertEqual(pgg.anchors.CENTER['x'], 0.5, "subscripting with x should return the x coordinate")
        self.assertEqual(pgg.anchors.CENTER['y'], 0.5, "subscripting with y should return the y coordinate")
        self.assertEqual(pgg.anchors.CENTER.x, 0.5, "The x property should return the x coordinate.")
        with self.assertRaises(IndexError, msg="2  shouldn't be a acceptable index."):
            pgg.anchors.TOP_CENTER[2]
        with self.assertRaises(IndexError, msg="xy shouldn't be a acceptable index."):
            pgg.anchors.TOP_CENTER['xy']