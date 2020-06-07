import time
from logging import getLogger

from numpy import cos
from scipy.integrate import odeint

from util import messages as msg

logger = getLogger(__name__)

"""Constants: """
earth_mass = 5.97 * (10 ** 24)  # kg
earth_ray = 6.6356 * (10 ** 6)  # m
gravitation_constant = 6.674 * (10 ** (-11))  # m/kg/s^2
altitude = 705 * (10 ** 3)  # m
v_0 = 7365  # m/s
alpha = gravitation_constant * earth_mass


class SatellitePoint:
    def __init__(self, t, ray, ray1, theta, theta1):
        """
        Object containing data about a point
        :param t: t value
        :param ray: r(t) value
        :param ray1: r'(t) value
        :param theta: theta(t) value
        :param theta1: theta'(t) value
        :type t: float
        :type ray: float
        :type ray1: float
        :type theta: float
        :type theta1: float
        """
        self.t = t
        self.ray = ray
        self.ray1 = ray1
        self.theta = theta
        self.theta1 = theta1

    def to_array(self) -> tuple:
        """ Returns a tuple of the ordered values (t, r(t), r'(t), theta(t), theta'(t)) """
        return (self.t, self.ray, self.ray1, self.theta, self.theta1)

    def get_speed(self) -> float:
        """
        :return the speed value for this point (vector norm)
        """
        return (self.ray1 ** 2 + (self.ray * self.theta1) ** 2) ** (1 / 2)

    def collision_check(self, prints=True) -> bool:
        """ Check wheter the position collides earth. Logs messages if positive"""
        if self.ray <= earth_ray:
            if prints:
                logger.info(msg["collision"].format(str(self.t)))
                logger.info(msg["satellite_speed"].format(str(self.get_speed())))
            return True
        return False


class SatelliteMovement:
    def __init__(self, initial_satellite_point, ray_diff_eq, theta_diff_eq, right_bound, euler_step):
        """
        :param initial_satellite_point: Default movement settings
        :param ray_diff_eq: Differential equation shape: r''(t) = f(t,r(t),r'(t),theta(t),theta'(t))
            -> example: f= lambda t,r,r',theta,theta': 3*t+r+r'-theta+theta'
        :param theta_diff_eq: Differential equation shape: theta''(t) = f(t,r(t),r'(t),theta(t),theta'(t))
            -> example: f= lambda t,r,r',theta,theta': 3*t+r+r'-theta+theta'
        :param right_bound: Last time value of approximation, left_bound is implicit : t0 value in the initial_point
        :param euler_step: Euler step value
        :type initial_satellite_point: SatellitePoint
        :type ray_diff_eq: function
        :type theta_diff_eq: function
        :type right_bound: float
        :type euler_step: float
        """
        self.initial_satellite_point = initial_satellite_point
        self.points = [initial_satellite_point]
        self.ray_diff_eq = ray_diff_eq
        self.theta_diff_eq = theta_diff_eq
        self.right_bound = right_bound
        self.euler_step = euler_step
        self.points_count = int((right_bound - self.initial_satellite_point.t) // euler_step)
        self.euler_calculation_time = 0
        self.odeint_calculation_time = 0

    def next_point_euler(self, previous_point) -> SatellitePoint:
        """Calculates the next approached points.
            Based on the discredit
            :param previous_point collection of the previous point values (t,r(t),r'(t),theta(t),theta'(t))
            :type previous_point SatellitePoint
            :return: couple of new point's values, similar shape to previous_couple parameter
        """
        new_t = previous_point.t + self.euler_step
        new_ray = previous_point.ray + self.euler_step * previous_point.ray1  # With r
        new_theta = previous_point.theta + self.euler_step * previous_point.theta1  # With theta
        new_ray1 = previous_point.ray1 + self.euler_step * self.ray_diff_eq(previous_point)  # With r'
        new_theta1 = previous_point.theta1 + self.euler_step * self.theta_diff_eq(previous_point)  # With theta'
        return SatellitePoint(new_t, new_ray, new_ray1, new_theta, new_theta1)

    def get_attribute_list(self, attribute_name) -> list:
        """
        :param attribute_name: selected attribute (=Variable name) > ex: "t" -> point.t.
            Type "speed" for speeds list
        :type attribute_name: string
        :return: the calculated values for the specified attribute
        """

        attribute_list = []
        for point in self.points:
            switcher = {"t": point.t, "ray": point.ray, "ray1": point.ray1, "theta": point.theta,
                        "theta1": point.theta1, "speed": point.get_speed()}
            attribute_list.append(switcher.get(attribute_name))
        return attribute_list

    def clean_points_list(self) -> None:
        """ Clears the points list by keeping the first element """
        self.points.clear()
        self.points.append(self.initial_satellite_point)

    def calculate_points_euler(self):
        """ Updates the points list with euler method """
        # Make sure the list only contains the first SatellitePoint
        self.clean_points_list()
        start_time = time.time_ns()

        # Calculate and add to list the new points
        for i in range(self.points_count):
            new_point = self.next_point_euler(self.points[i])
            self.points.append(new_point)

            # Earth collision check
            if new_point.collision_check():
                break
        spent_time = time.time_ns() - start_time
        self.euler_calculation_time = spent_time / 10**6

    def calculate_points_odeint(self):
        """ Updates the points list with scipy.integrate.odeint method """
        # Make sure the list only contains the first SatellitePoint
        self.clean_points_list()
        start_time = time.time_ns()

        # Specific Odeint equation method
        def equations(elements, time_value):
            ray, ray1, theta, theta1 = elements
            point = SatellitePoint(time_value, ray, ray1, theta, theta1)
            return ray1, self.ray_diff_eq(point), theta1, self.theta_diff_eq(point)

        # t values
        t_list = [self.euler_step * i for i in range(self.points_count + 1)]

        # Other values gotten by odeint method
        ray_list, ray1_list, theta_list, theta1_list = \
            odeint(equations, self.initial_satellite_point.to_array()[1:], t_list).T

        # Add points to the points list
        for k in range(len(t_list)):
            new_point = SatellitePoint(t_list[k], ray_list[k], ray1_list[k], theta_list[k], theta1_list[k])
            self.points.append(new_point)

            # Earth collision check
            if new_point.collision_check():
                break
        spent_time = time.time_ns() - start_time
        self.odeint_calculation_time = spent_time / 10**6

    def calculate_points_real_solution(self):
        """ Updates the points list with real ray values (Real solution)"""
        # Make sure the list only contains the first SatellitePoint
        if len(self.points) <= 1:
            logger.warning("Can't get real solution, no previous point has been calculated !")
            return

        p = (self.initial_satellite_point.theta1 * self.initial_satellite_point.ray ** 2) ** 2 / alpha
        e = p / self.initial_satellite_point.ray - 1
        for point in self.points:
            new_ray = p / (1 + e * cos(point.theta))
            point.ray = new_ray
