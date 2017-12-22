# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2013-2017: SCS Software

# #####  NOTE: Based on SCS Game engine code #####

from mathutils import Vector


def set_direction(forward):
    """Compute the (yaw, pitch, roll) from forward pointing vector.
    Note that the resulting roll is always zero as it cannot be encoded in a 3D vector without additional info.

    :param forward: forward vector
    :type forward: tuple
    :return:
    :rtype:
    """
    import math

    # The "epsilon" was chosen quite randomly.
    # Ought be quite safe - just a safety net against degenerate forward vectors.
    epsilon = 0.0001

    def length(vec):
        return math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])

    def v_clamp(num, minimum, maximum):
        if num < minimum:
            return minimum
        if num > maximum:
            return maximum
        return num

    # Is the forward vector degenerate? Produce "no-rotation" result.
    length = length(forward)
    if length < epsilon:
        pitch = 0.0
        roll = 0.0
        yaw = 0.0
        return pitch, roll, yaw

    # We do not produce any roll, as documented.
    roll = 0.0

    # Compute the pitch directly - arcsin(Y), taking Y component of normalized forward vector.
    pitch = math.degrees(math.asin(v_clamp(forward[1] / length, -1.0, 1.0)))

    # Is the @a forward vector (almost) in the XY plane?
    # Compute the yaw angle directly.
    if math.fabs(forward[2]) < epsilon:
        if forward[0] < 0.0:
            yaw = 90.0
            return pitch, roll, yaw
        if forward[0] > 0.0:
            yaw = 270.0
            return pitch, roll, yaw
        yaw = 0.0
        return pitch, roll, yaw

    # Compute the azimuthal angle.
    # We "realing" the coordinate space -
    # the forward direction will be treated like a virtual "X" axis,
    # the west pointing direction like a virtual "Y" axis.
    # Simple arctan of "X"/"Y" will produce correct azimuthal angle for vectors in positive "X" halfspace.
    # Because we already covered the XY plane above,
    # we know that the "Y" component is never zero (or close to zero).
    # The negative "X" halfspace angles computed by using the arctan function are by 180 degrees off,
    # so we have to adjust for that.
    # After all that, we positive "X" halfspace angles are in the (-90,90) range,
    # and the negative "X" halfpsace angles are in the (90,270) range.
    # Apparently, we must normalize the range (-90,0) to (270,360).
    #
    # The code is quite complex, unfortunately.

    angle = math.degrees(math.atan(forward[0] / forward[2]))
    if forward[2] < 0.0:
        if angle < 0.0:
            angle_bound = 360.0
        else:
            angle_bound = 0.0
        yaw = angle + angle_bound
    else:
        yaw = angle + 180.0

    return pitch, roll, yaw


def compute_bernstein(float_t):
    """Evaluate the cubic Bernstein polynomials at given parameter
    and return the bernstein polynomial coefficients..

    :param float_t:
    :type float_t: float
    """
    q = 1.0 - float_t
    f1 = q * q * q
    f2 = 3.0 * float_t * q * q
    f3 = 3.0 * float_t * float_t * q
    f4 = float_t * float_t * float_t
    return f1, f2, f3, f4


def compute_bernstein_dt(float_t):
    """Evaluate the (first) derivative of cubic Bernstein polynomials at given parameter.

    :param float_t:
    :type float_t: float
    """

    b_dt_0 = (-3.0, 9.0, -9.0, 3.0)
    b_dt_1 = (6.0, -12.0, 6.0, 0.0)
    b_dt_2 = (-3.0, 3.0, 0.0, 0.0)

    f1 = (b_dt_0[0] * float_t + b_dt_1[0]) * float_t + b_dt_2[0]
    f2 = (b_dt_0[1] * float_t + b_dt_1[1]) * float_t + b_dt_2[1]
    f3 = (b_dt_0[2] * float_t + b_dt_1[2]) * float_t + b_dt_2[2]
    f4 = (b_dt_0[3] * float_t + b_dt_1[3]) * float_t + b_dt_2[3]

    return f1, f2, f3, f4


def evaluate_bezier_curve(vec1, vec2, vec3, vec4, float_t):
    """Evaluate the cubic Bezier curve at given parameter point
    and return the point generated by given bezier curve and parameter point "float_t".
    Standard Bezier curve is a linear combination of control points (vec1, vec2, vec3, vec4),
    weighted by factors obtained from cubic Bernstein polynomials evaluated at point (float_t).

    :param vec1:
    :type vec1: tuple | mathutils.Vector
    :param vec2:
    :type vec2: tuple | mathutils.Vector
    :param vec3:
    :type vec3: tuple | mathutils.Vector
    :param vec4:
    :type vec4: tuple | mathutils.Vector
    :param float_t:
    :type float_t: float
    :return:
    :rtype: mathutils.Vector
    """

    c = compute_bernstein(float_t)
    f1 = c[0] * vec1[0] + c[1] * vec2[0] + c[2] * vec3[0] + c[3] * vec4[0]
    f2 = c[0] * vec1[1] + c[1] * vec2[1] + c[2] * vec3[1] + c[3] * vec4[1]
    f3 = c[0] * vec1[2] + c[1] * vec2[2] + c[2] * vec3[2] + c[3] * vec4[2]
    return Vector((f1, f2, f3))


def evaluate_bezier_curve_dt(vec1, vec2, vec3, vec4, float_t):
    """Evaluate the cubic Bezier curve at given parameter point
    and return the point generated by given bezier curve and parameter point "float_t".
    Standard Bezier curve is a linear combination of control points (vec1, vec2, vec3, vec4),
    weighted by factors obtained from cubic Bernstein polynomials evaluated at point (float_t).

    :param vec1:
    :type vec1: tuple | mathutils.Vector
    :param vec2:
    :type vec2: tuple | mathutils.Vector
    :param vec3:
    :type vec3: tuple | mathutils.Vector
    :param vec4:
    :type vec4: tuple | mathutils.Vector
    :param float_t:
    :type float_t: float
    :return:
    :rtype: mathutils.Vector
    """

    c = compute_bernstein_dt(float_t)
    f1 = c[0] * vec1[0] + c[1] * vec2[0] + c[2] * vec3[0] + c[3] * vec4[0]
    f2 = c[0] * vec1[1] + c[1] * vec2[1] + c[2] * vec3[1] + c[3] * vec4[1]
    f3 = c[0] * vec1[2] + c[1] * vec2[2] + c[2] * vec3[2] + c[3] * vec4[2]
    return Vector((f1, f2, f3))


def smooth_curve_position(point1, tang1, point2, tang2, coef):
    """Smooth continuous curve helper based on piecewise cubic bezier curves
    designed for waypoint navigation.

    Feed the function with two waypoint positions (point1 and point2), and the tangential vectors
    in those positions (tang1 and tang2). The coef parameter can range from 0.0 to 1.0. As
    the coef grows (with time in the system), the function generates appropriate positions and
    tangentials along a bezier curve passing through those two waypoints.

    Once coef is getting past 1.0, it is time for you to generate a new waypoint and direction,
    and once "decrement coef by 1.0" when adding a new curve segment, copy the values from
    <point2, tang2> into <point1, tang1>. This way you will insure the next curve segment will not
    only be continuous, but also that the transition will be smooth.

    Note that the length of the tangential vectors affects the curvature of the segments!
    Usually, you will want the length of the tangential vectors to be in 10's of percentage
    points of the length of the <point2-point1> vector.

    :param point1: position of the starting waypoint
    :type point1: mathutils.Vector
    :param tang1: tangential vector (direction vector) at the starting waypoint
    :type tang1: mathutils.Vector
    :param point2: position of the ending waypoint
    :type point2: mathutils.Vector
    :param tang2: tangential vector (direction vector) at the ending waypoint
    :type tang2: mathutils.Vector
    :param coef: coefficient ranging from 0.0 to 1.0 suggesting how far from start to end to generate a point
    :type coef: float
    :return:
    :rtype: mathutils.Vector
    """
    pp1 = point1
    pp2 = point1 + tang1
    pp3 = point2 - tang2
    pp4 = point2

    # Compute position along the Bezier curve.
    pos = evaluate_bezier_curve(pp1, pp2, pp3, pp4, coef)

    # Compute appropriate tangential vector along the curve.
    return pos


def smooth_curve_tangent(point1, tang1, point2, tang2, coef):
    """Smooth continuous curve helper based on piecewise cubic bezier curves
    designed for waypoint navigation which computes appropriate tangential vector along the curve.

    Feed the function with two waypoint positions (point1 and point2), and the tangential vectors
    in those positions (tang1 and tang2). The coef parameter can range from 0.0 to 1.0. As
    the coef grows (with time in the system), the function generates appropriate positions and
    tangentials along a bezier curve passing through those two waypoints.

    :param point1: position of the starting waypoint
    :type point1: mathutils.Vector
    :param tang1: tangential vector (direction vector) at the starting waypoint
    :type tang1: mathutils.Vector
    :param point2: position of the ending waypoint
    :type point2: mathutils.Vector
    :param tang2: tangential vector (direction vector) at the ending waypoint
    :type tang2: mathutils.Vector
    :param coef: coefficient ranging from 0.0 to 1.0 suggesting how far from start to end to generate a point
    :type coef: float
    :return:
    :rtype: mathutils.Vector
    """
    pp1 = point1
    pp2 = point1 + tang1
    pp3 = point2 - tang2
    pp4 = point2

    # Compute position along the Bezier curve.
    direction = evaluate_bezier_curve_dt(pp1, pp2, pp3, pp4, coef)

    # Compute appropriate tangential vector along the curve.
    return direction


def compute_smooth_curve_length(point1, tang1, point2, tang2, measure_steps):
    """Takes two points in space and their tangents and returns length of the curve as a float.
    The accuracy of measuring can be controlled by "measure_steps" parameter.

    :param point1: position of the starting waypoint
    :type point1: mathutils.Vector
    :param tang1: tangential vector (direction vector) at the starting waypoint
    :type tang1: mathutils.Vector
    :param point2: position of the ending waypoint
    :type point2: mathutils.Vector
    :param tang2: tangential vector (direction vector) at the ending waypoint
    :type tang2: mathutils.Vector
    :param measure_steps:
    :type measure_steps: int
    :return:
    :rtype: float
    """
    step_size = 1.0 / float(measure_steps)
    coef = step_size
    lenth = 0.0
    start_pos = point1
    for ii in range(measure_steps):
        cpos = smooth_curve_position(point1, tang1, point2, tang2, coef)
        le = start_pos - cpos
        lenth += le.length
        start_pos = cpos
        coef += step_size
    return lenth


def compute_curve(point1, tang1, point2, tang2, curve_steps):
    """Compute curve points and return it as dictionary.
    Points are storred in the list by the key "curve_points".

    :param point1: start curve position
    :type point1: mathutils.Vector
    :param tang1: start curve rotation
    :type tang1: mathutils.Vector
    :param point2: end curve position
    :type point2:  mathutils.Vector
    :param tang2: end curve rotation
    :type tang2: mathutils.Vector
    :param curve_steps: number of curve segments to calculate
    :type curve_steps: int
    :return: dictionary with one entry of curve points as list
    :rtype: dict[str, list]
    """

    le = compute_smooth_curve_length(point1, tang1, point2, tang2, 300)
    curve_data = {'curve_points': []}

    for segment in range(curve_steps):
        coef = float(segment / curve_steps)
        # print('coef: %s' % coef)
        pos = smooth_curve_position(point1, tang1 * (le / 3), point2, tang2 * (le / 3), coef)
        # print('pos: %s' % str(pos))
        curve_data['curve_points'].append(pos)
        # points['point ' + str(coef)] = Vector(pos)
    curve_data['curve_points'].append(point2)  # last point
    return curve_data


def curves_intersect(curve1_p1, curve1_t1, curve1_p2, curve1_t2, length1,
                     curve2_p1, curve2_t1, curve2_p2, curve2_t2, length2, part_count=10):
    """Calculates first intersection point between two curves.

    NOTE: what about the multiple intersection points?

    :param curve1_p1: start point of 1st curve
    :type curve1_p1: mathutils.Vector
    :param curve1_t1: rotation of start point of 1st curve
    :type curve1_t1: mathutils.Vector
    :param curve1_p2: end point of 1st curve
    :type curve1_p2: mathutils.Vector
    :param curve1_t2: rotation of end point of 1st curve
    :type curve1_t2: mathutils.Vector
    :param length1: length of 1st curve
    :type length1: float
    :param curve2_p1: start point of 2nd curve
    :type curve2_p1: mathutils.Vector
    :param curve2_t1: rotation of start point of 2nd curve
    :type curve2_t1: mathutils.Vector
    :param curve2_p2: end point of 2nd curve
    :type curve2_p2: mathutils.Vector
    :param curve2_t2: rotation of end point of 2nd curve
    :type curve2_t2: mathutils.Vector
    :type length2: float
    :param part_count: number of segments for curve to be calculated
    :type part_count: int
    :return: intersection point and position coefs where on curves that happend or None if not found
    :rtype: (mathutils.Vector, float, float) | (None, int, int)
    """

    if curve1_p1 == curve2_p1:
        return curve1_p1, 0, 0

    if curve1_p2 == curve2_p2:
        return curve1_p2, 1, 1

    step1 = length1 / part_count
    step2 = length2 / part_count

    pos1 = 0
    epsilon = 0.01

    for i in range(part_count):

        start1 = smooth_curve_position(curve1_p1, curve1_t1, curve1_p2, curve1_t2, pos1 / length1)
        end1 = smooth_curve_position(curve1_p1, curve1_t1, curve1_p2, curve1_t2, (pos1 + step1) / length1)

        pos2 = 0
        for j in range(part_count):

            start2 = smooth_curve_position(curve2_p1, curve2_t1, curve2_p2, curve2_t2, pos2 / length2)
            end2 = smooth_curve_position(curve2_p1, curve2_t1, curve2_p2, curve2_t2, (pos2 + step2) / length2)

            denom = ((end2[2] - start2[2]) * (end1[0] - start1[0])) - ((end2[0] - start2[0]) * (end1[2] - start1[2]))
            nume_a = ((end2[0] - start2[0]) * (start1[2] - start2[2])) - ((end2[2] - start2[2]) * (start1[0] - start2[0]))
            nume_b = ((end1[0] - start1[0]) * (start1[2] - start2[2])) - ((end1[2] - start1[2]) * (start1[0] - start2[0]))

            if abs(denom) < epsilon:
                continue

            mu_a = nume_a / denom
            mu_b = nume_b / denom
            if 0 <= mu_a <= 1 and 0 <= mu_b <= 1:

                if (mu_a < epsilon and i == 0) or (mu_b < epsilon and j == 0):
                    return None, -1, -1
                if (mu_a > 1 - epsilon and i == part_count - 1) or (mu_b > 1 - epsilon and j == part_count - 1):
                    return None, -1, -1

                curve_intersect = Vector((0, 0, 0))
                curve_intersect.x = start1[0] + mu_a * (end1[0] - start1[0])
                curve_intersect.y = (start1[1] + end1[1] + start2[1] + end2[1]) / 4.0
                curve_intersect.z = start1[2] + mu_a * (end1[2] - start1[2])

                return curve_intersect, pos1 / length1, pos2 / length2

            pos2 += step2

        pos1 += step1

    return None, -1, -1
