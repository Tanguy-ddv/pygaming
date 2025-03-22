import unittest
import pygaming as pgg

class TestAnchor1D(unittest.TestCase):
    """Testing of Anchor1D."""

    def test_init(self):
        """Test the initialization of the anchors."""
        self.assertIsInstance(pgg.anchors.CENTER._value, float, msg="The stored value should be a float")
        self.assertIsInstance(pgg.anchors.CENTER, pgg.anchors.Anchor1D, msg="The defined constants should be of type Anchor1D")
        with self.assertRaises(ValueError, msg="7 shouldn't be an acceptable argument for Anchor1D"):
            pgg.anchors.Anchor1D(7)
        with self.assertRaises(ValueError, msg="'aaa' shouldn't be an acceptable argument for Anchor1D"):
            pgg.anchors.Anchor1D('aaa')
        with self.assertRaises(ValueError, msg="-0.5 shouldn't be an acceptable argument for Anchor1D"):
            pgg.anchors.Anchor1D(-0.5)
        with self.assertRaises(ValueError, msg="[0.7] shouldn't be an acceptable argument for Anchor1D"):
            pgg.anchors.Anchor1D([0.7])
        self.assertEqual(pgg.anchors.Anchor1D(0.3), 0.3, "An Anchor1d should be comparable with a float")
        self.assertEqual(pgg.anchors.Anchor1D(pgg.anchors.Anchor1D(0.6)), 0.6, "An Anchor1d should be comparable with a float")
        self.assertEqual(pgg.anchors.LEFT, pgg.anchors.Anchor1D(0.), "LEFT is supposed to be Anchor1D(0.)")
        self.assertNotEqual(pgg.anchors.LEFT, None, "LEFT is supposed to be different than None)")
        self.assertNotEqual(pgg.anchors.LEFT, (0.,), "LEFT is supposed to be different than (0.,)")

    
    def test_math(self):
        """Test the mathematical functions related to the anchors1D."""
        self.assertLess(pgg.anchors.LEFT, pgg.anchors.RIGHT, "LEFT should be < RIGHT as LEFT <=> 0 and RIGHT <=> 1")
        self.assertLessEqual(pgg.anchors.LEFT, pgg.anchors.TOP, "TOP and LEFT are both <=> 0, so LEFT <= TOP.")
        self.assertLessEqual(pgg.anchors.TOP, pgg.anchors.LEFT, "TOP and LEFT are both <=> 0, so TOP <= LEF.")
        self.assertGreater(pgg.anchors.Anchor1D(0.5), pgg.anchors.BACK, "BACK <=> 0 so Anchor1D(0.5) should be greater.")
        self.assertGreaterEqual(pgg.anchors.Anchor1D(0.8), pgg.anchors.Anchor1D(0.80), "Anchor1D(0.8) >= Anchor1D(0.8)")
        with self.assertRaises(TypeError, msg="Anchor1D shouldn't be comparable with strings"):
            pgg.anchors.LEFT > 'aaaa'
        with self.assertRaises(TypeError, msg="Anchor1D shouldn't be comparable with strings"):
            pgg.anchors.LEFT > [0, 1]
        with self.assertRaises(TypeError, msg="Anchor1D shouldn't be comparable with strings"):
            pgg.anchors.LEFT > (1, 0.5)
        with self.assertRaises(TypeError, msg="Anchor1D shouldn't be comparable with an integer."):
            pgg.anchors.LEFT > 10,
        self.assertGreater(pgg.anchors.TOP, -0.5, "Any negative float should be less than an anchor.")
        self.assertLess(pgg.anchors.TOP, 4., "Any float > 1 should be greatear than an anchor.")
        x, y, width, height = 10, 15, 20, 50
        self.assertEqual(x + pgg.anchors.LEFT*width, 10, "Multiplying by an Anchor1D should be the same as multiplying by a float.")
        self.assertEqual(y + pgg.anchors.BOTTOM*height, 65, "Multiplying by an Anchor1D should be the same as multiplying by a float.")
        self.assertEqual(y + pgg.anchors.CENTER*height, 40, "Multiplying by an Anchor1D should be the same as multiplying by a float.")
        self.assertEqual(y + height*pgg.anchors.CENTER, 40, "Multiplying by an Anchor1D should be the same as multiplying by a float.")

    def test_strings(self):
        """Test the proper naming of the anchors."""
        self.assertEqual(str(pgg.anchors.LEFT), "Anchor1D.LEFT", "The naming is wrong.")
        self.assertEqual(repr(pgg.anchors.CENTER), "Anchor1D.CENTER", "The naming is wrong.")
        self.assertEqual(str(pgg.anchors.Anchor1D(0.4)), "Anchor1D(0.4)", "The naming is wrong.")
        self.assertEqual(str(pgg.anchors.Anchor1D(0.4, name="ZeroDotFour")), "Anchor1D.ZeroDotFour", "The naming is wrong.")

class TestAnchor2D(unittest.TestCase):
    """Testing of Anchor2D."""

    def test_init(self):
        """Test the initialization of the anchors."""
        self.assertIsInstance(pgg.anchors.CENTER_LEFT._anchorx, float, msg="The stored value should be a float")
        self.assertIsInstance(pgg.anchors.CENTER_CENTER, pgg.anchors.Anchor2D, msg="The defined constants should be of type Anchor1D")
        with self.assertRaises(ValueError, msg="(5, 5) shouldn't be an acceptable argument for Anchor2D"):
            pgg.anchors.Anchor2D(5, 5)
        with self.assertRaises(ValueError, msg="5 shouldn't be an acceptable argument for Anchor2D"):
            pgg.anchors.Anchor2D(5)
        with self.assertRaises(ValueError, msg="'aaa' shouldn't be an acceptable argument for Anchor2D"):
            pgg.anchors.Anchor2D('aaa')
        with self.assertRaises(ValueError, msg="[0, 1.5] shouldn't be an acceptable argument for Anchor2D"):
            pgg.anchors.Anchor2D([0, 1.5])
        with self.assertRaises(ValueError, msg="(-0.7, 0.7) shouldn't be an acceptable argument for Anchor2D"):
            pgg.anchors.Anchor2D((-0.7, 0.7))
        self.assertEqual(
            pgg.anchors.Anchor2D(1., 0.),
            pgg.anchors.Anchor2D((1., 0.)),
            "Instanciating with a tuple should be the same as instanciating with 2 arguments"
        )
        self.assertEqual(
            pgg.anchors.Anchor2D(1., 0., "ZeroOne"),
            pgg.anchors.Anchor2D((1., 0.)),
            "The presence of a name shouldn't change the equality of two anchors.")
        self.assertEqual(pgg.anchors.Anchor2D(1., 0., "ZeroOne"), pgg.anchors.Anchor2D(
            (pgg.anchors.Anchor1D(1.), pgg.anchors.Anchor1D(0.))
        ),
        "Anchor2D should be instanciable with Anchor1D"
        )
        self.assertEqual(pgg.anchors.TOP_LEFT, (0., 0.), "a Anchor2D should be equal to the tuple with same values.")
        self.assertEqual(pgg.anchors.CENTER_RIGHT, (1., 0.5), "a Anchor2D should be equal to the tuple with same values.")
        self.assertNotEqual(pgg.anchors.TOP_CENTER, (0., 0.), "Anchor2D object shouldn't be equal to tuple with different values.")
        self.assertNotEqual(pgg.anchors.TOP_CENTER, None, "Anchor2D object shouldn't be equal to object that are neither tuple nor Anchor2D")
        self.assertNotEqual(pgg.anchors.TOP_CENTER, 0., "Anchor2D object shouldn't be equal to object that are neither tuple nor Anchor2D")
        self.assertEqual(
            pgg.anchors.TOP_CENTER, pgg.anchors.Anchor2D(pgg.anchors.CENTER, pgg.anchors.TOP),
            "TOP_CENTER should be equalt to Anchor2D(CENTER, TOP)"
        )
    
    def test_iter(self):
        """Test the iteration and subscription on anchors1D."""
        self.assertEqual(pgg.anchors.TOP_CENTER[0], 0.5, "Anchor2D should be subscriptable and return the x value for the first index.")
        self.assertEqual(pgg.anchors.TOP_CENTER[1], 0., "Anchor2D should be subscriptable and return the y value for the second index.")
        self.assertEqual(pgg.anchors.TOP_CENTER[-1], 0., "Anchor2D should be subscriptable and return the y value for the index equal to -1.")
        with self.assertRaises(IndexError, msg="Anchor2D should be subscriptable by only 1, 0, and -1"):
            pgg.anchors.CENTER_CENTER[3]
        with self.assertRaises(IndexError, msg="Anchor2D should be subscriptable by only 1, 0, and -1"):
            pgg.anchors.CENTER_CENTER['index']
        self.assertEqual(len(tuple(pgg.anchors.BOTTOM_CENTER)), 2, "Calling tuple() on an Anchor2d should lead to a tuple of length 2.")
        self.assertIsInstance(tuple(pgg.anchors.BOTTOM_CENTER)[0], float, "Calling tuple() on an Anchor2d should lead to a tuple containing floats.")
        self.assertEqual(tuple(pgg.anchors.BOTTOM_CENTER)[1], 1., "Calling tuple() on an Anchor2d should lead to a tuple containing the indiviual values")
    
    def test_strings(self):
        """test the string representation of the anchors."""
        self.assertEqual(str(pgg.anchors.BOTTOM_CENTER), 'Anchor2D.BOTTOM_CENTER', "The naming is wrong.")
        self.assertEqual(str(pgg.anchors.Anchor2D(0.5, 0.3, "DOT_FIVE_DOT_THREE")), "Anchor2D.DOT_FIVE_DOT_THREE", "The naming is wrong.")
        self.assertEqual(str(pgg.anchors.Anchor2D(0.5, 0.3)), "Anchor2D(0.5, 0.3)", "The naming is wrong.")
        self.assertEqual(repr(pgg.anchors.Anchor2D(0.5, 0.3)), "Anchor2D(0.5, 0.3)", "The naming is wrong.")
