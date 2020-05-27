import matplotlib.pyplot as plt

from satellite_movement import *


def ray_2(previous_point):
    """ Differential equation for ray
    :param previous_point: Previous SatellitePoint needed to calculate the equation
    :type previous_point SatellitePoint
    """
    return (-alpha / (previous_point.ray ** 2)) + previous_point.ray * (previous_point.theta1 ** 2)


def theta_2(previous_point) -> float:
    """ Differential equation for theta
    :param previous_point: Previous SatellitePoint needed to calculate the equation
    :type previous_point SatellitePoint
    """
    return (-2 * previous_point.ray1 * previous_point.theta1) / previous_point.ray


def calculate():
    for k in range(5):
        factor = (0.8 + k / 10)
        speed = factor * v_0 / (earth_ray + altitude)

        # Initialize objects and launch process
        initial_point = SatellitePoint(0, earth_ray + altitude, 0, 0, speed)
        movement = SatelliteMovement(initial_point, ray_2, theta_2, 30000, 50)

        # Get euler values to display
        movement.calculate_points_euler()
        time_euler = movement.get_attribute_list("t")
        ray_euler = movement.get_attribute_list("ray")
        theta_euler = movement.get_attribute_list("theta")
        movement.calculate_points_real_solution()
        real_ray_euler = movement.get_attribute_list("ray")

        # Get odeint values to display
        movement.calculate_points_odeint()
        time_odeint = movement.get_attribute_list("t")
        ray_odeint = movement.get_attribute_list("ray")
        theta_odeint = movement.get_attribute_list("theta")
        movement.calculate_points_real_solution()
        real_ray_odeint = movement.get_attribute_list("ray")

        # Trace
        fig, axes = plt.subplots(2, 2)
        axes.flat[0].set_title(msg["euler_column"])
        axes.flat[0].set(ylabel=msg["r_graph"])
        axes[0, 0].plot(time_euler, ray_euler, 'b', label="Euler ray")
        axes[0, 0].plot(time_euler, real_ray_euler, 'c+', label="Real ray")
        axes[1, 0].plot(time_euler, theta_euler, 'r', label="Euler theta")

        axes.flat[1].set_title(msg["odeint_column"])
        axes.flat[2].set(ylabel=msg["theta_graph"])
        axes[0, 1].plot(time_odeint, ray_odeint, 'k', label="Odeint ray")
        axes[0, 1].plot(time_odeint, real_ray_odeint, 'g+', label="Real ray")
        axes[1, 1].plot(time_odeint, theta_odeint, 'm', label="Odeint theta")

        fig.suptitle(msg["plots_title"].replace("%factor%", str(factor)))
        fig.legend()
        fig.canvas.set_window_title(msg["frame_name"])
        plt.show()
