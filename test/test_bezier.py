import unittest

from graphviz2drawio.mx.bezier import (
    approximate_cubic_bezier_as_quadratic,
    subdivide_inflections,
)


class TestApproximateCubicBezierAsQuadratic(unittest.TestCase):
    def test_simple_curve_approximation(self):
        """Test basic conversion of a simple cubic Bezier to quadratic."""
        # A simple cubic curve
        p0 = complex(0, 0)
        c1 = complex(1, 2)
        c2 = complex(3, 2)
        p2 = complex(4, 0)

        result = approximate_cubic_bezier_as_quadratic(p0, c1, c2, p2)

        # Verify result is a quadratic Bezier (3 points)
        self.assertEqual(len(result), 3)
        # Start and end points should match
        self.assertEqual(result[0], p0)
        self.assertEqual(result[2], p2)
        # Control point should be somewhere reasonable
        self.assertTrue(isinstance(result[1], complex))

    def test_straight_line_approximation(self):
        """Test approximation of a cubic curve that's essentially a straight line."""
        p0 = complex(0, 0)
        c1 = complex(1, 0)
        c2 = complex(3, 0)
        p2 = complex(4, 0)

        result = approximate_cubic_bezier_as_quadratic(p0, c1, c2, p2)

        # For a straight line, the control point should be on the line
        self.assertAlmostEqual(result[1].imag, 0)
        self.assertTrue(0 < result[1].real < 4)

    def test_parallel_tangents_case(self):
        """Test the case where tangent lines are parallel."""
        # Set up a cubic with truly parallel tangents
        p0 = complex(0, 0)
        c1 = complex(1, 3)
        c2 = complex(3, -1)  # Make this (3, -1) to create parallel tangent vectors
        p2 = complex(4, 2)

        # Calculate tangent vectors to verify they're parallel
        tan_start = 3.0 * (c1 - p0)  # 3*(1+3j) = (3+9j)
        tan_end = 3.0 * (p2 - c2)  # 3*(4+2j - 3-1j) = 3*(1+3j) = (3+9j)

        # Verify tangents are parallel (same direction)
        self.assertEqual(tan_start.real * tan_end.imag, tan_start.imag * tan_end.real)

        result = approximate_cubic_bezier_as_quadratic(p0, c1, c2, p2)

        # Should fall back to averaging method
        expected_control = (c1 + c2) / 2
        self.assertEqual(result[1], expected_control)

    def test_complex_path_approximation(self):
        """Test approximation of a more complex cubic Bezier."""
        p0 = complex(0, 0)
        c1 = complex(0, 4)
        c2 = complex(4, 4)
        p2 = complex(4, 0)

        result = approximate_cubic_bezier_as_quadratic(p0, c1, c2, p2)

        # Verify basic properties
        self.assertEqual(result[0], p0)
        self.assertEqual(result[2], p2)
        # The control point should be somewhat near the center
        self.assertTrue(0 <= result[1].real <= 4)
        self.assertTrue(0 <= result[1].imag <= 4)

    def test_edge_case_with_control_points_at_endpoints(self):
        """Test when control points are at the endpoints."""
        p0 = complex(0, 0)
        c1 = p0  # Control point same as start
        c2 = complex(4, 0)  # Control point same as end
        p2 = complex(4, 0)

        result = approximate_cubic_bezier_as_quadratic(p0, c1, c2, p2)

        # Should still return a valid quadratic
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], p0)
        self.assertEqual(result[2], p2)


class TestSubdivideInflections(unittest.TestCase):
    def test_curve_with_no_inflections(self):
        """Test subdivision of a curve with no inflection points."""
        # Simple curve without inflections
        p0 = complex(0, 0)
        c1 = complex(1, 1)
        c2 = complex(2, 1)
        p3 = complex(3, 0)

        result = subdivide_inflections(p0, c1, c2, p3)

        # Should return a tuple with just one curve
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], (p0, c1, c2, p3))

    def test_curve_with_one_inflection(self):
        """Test subdivision of a curve with one inflection point."""
        # S-curve with one inflection
        p0 = complex(0, 0)
        c1 = complex(1, 2)
        c2 = complex(2, -2)
        p3 = complex(3, 0)

        result = subdivide_inflections(p0, c1, c2, p3)

        # Should return a tuple with two curves
        self.assertEqual(len(result), 2)
        # First curve should start at p0
        self.assertEqual(result[0][0], p0)
        # Second curve should end at p3
        self.assertEqual(result[1][3], p3)
        # The end of the first curve should match the start of the second
        self.assertEqual(result[0][3], result[1][0])

    def test_curve_with_two_inflections(self):
        """Test subdivision of a curve with two inflection points (loop)."""
        # Create a curve with a loop (has two inflections)
        p0 = complex(0, 0)
        c1 = complex(3, 3)
        c2 = complex(-3, 3)
        p3 = complex(0, 0)

        result = subdivide_inflections(p0, c1, c2, p3)

        # Should return a tuple with three curves
        self.assertEqual(len(result), 3)
        # Check that all three curves connect
        self.assertEqual(result[0][0], p0)
        self.assertEqual(result[0][3], result[1][0])
        self.assertEqual(result[1][3], result[2][0])
        self.assertEqual(result[2][3], p3)

    def test_almost_straight_curve(self):
        """Test an almost straight curve that might have numerical stability issues."""
        p0 = complex(0, 0)
        c1 = complex(1, 0.001)
        c2 = complex(2, -0.001)
        p3 = complex(3, 0)

        result = subdivide_inflections(p0, c1, c2, p3)

        # Verify the result is a valid tuple
        self.assertIsInstance(result, tuple)
        # First element should be a cubic Bezier
        self.assertEqual(len(result[0]), 4)

    def test_complex_s_curve(self):
        """Test a complex S-curve with potential inflection points."""
        p0 = complex(0, 0)
        c1 = complex(1, 3)
        c2 = complex(3, -3)
        p3 = complex(4, 0)

        result = subdivide_inflections(p0, c1, c2, p3)

        # Should have at least one subdivision
        self.assertTrue(len(result) >= 2)

        # All curves should connect properly
        for i in range(len(result) - 1):
            self.assertEqual(result[i][3], result[i + 1][0])

        # First and last points should match original
        self.assertEqual(result[0][0], p0)
        self.assertEqual(result[-1][3], p3)


if __name__ == "__main__":
    unittest.main()
