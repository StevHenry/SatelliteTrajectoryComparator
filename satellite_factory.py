import matplotlib.pyplot as plt

from satellite_movement import *


def ray_2(previous_point) -> float:
    """ Differential equation for ray
        :param previous_point: Previous SatellitePoint needed to calculate the equation
        :type previous_point SatellitePoint
        :return: result of the equation in a float
    """
    return (-alpha / (previous_point.ray ** 2)) + previous_point.ray * (previous_point.theta1 ** 2)


def theta_2(previous_point) -> float:
    """ Differential equation for theta
        :param previous_point: Previous SatellitePoint needed to calculate the equation
        :type previous_point SatellitePoint
        :return: result of the equation in a float
    """
    return (-2 * previous_point.ray1 * previous_point.theta1) / previous_point.ray


def create_graph(factor, movement):
    """
    :param factor: initial speed factor contained in [0.8, 1.2]
    :param movement: SatelliteMovement whose graph is based on
    :type factor: float
    :type movement: SatelliteMovement
    :return:
    """
    fig, axes = plt.subplots(2, 2)
    flat_axes = axes.flat[:]
    graph_parameters = msg["graph"]["plots"]
    flat_axes[0].set_title(graph_parameters["euler"]["column_name"])
    flat_axes[1].set_title(graph_parameters["odeint"]["column_name"])
    flat_axes[0].set(ylabel=graph_parameters["r_graph"])
    flat_axes[2].set(ylabel=graph_parameters["theta_graph"])

    graph_parameters = msg["graph"]["parameters"]
    text = (graph_parameters["initial_speed"] + "\n" +
            graph_parameters["euler_step"] + "\n" +
            graph_parameters["euler_time"] + "\n" +
            graph_parameters["odeint_points"] + "\n" +
            graph_parameters["odeint_time"]
            ).format(str(factor)[:3], movement.euler_step, movement.euler_calculation_time,
                     movement.points_count, movement.odeint_calculation_time)

    font = graph_parameters["fontsize"]
    fig.text(0.01, 0.5, text, fontsize=font)
    fig.text(0.5, 0.01, "Authors: " + ", ".join(msg["authors"]), fontsize=font, withdash=True)
    fig.suptitle(msg["graph"]["title"])
    fig.canvas.set_window_title(msg["graph"]["frame_name"])
    plt.get_current_fig_manager().window.state("zoomed")
    return fig, flat_axes


def calculate_error(value_list, real_value_list) -> float:
    """
    :param value_list: list of real values
    :param real_value_list: list of theoric values
    :type value_list: list or tuple
    :type real_value_list: list or tuple
    :return: mean percentage of relative difference
    """
    error_value = 0
    for a in range(len(value_list)):
        error_value = (abs(real_value_list[a] - value_list[a]) / real_value_list[a]) + error_value
    return (error_value / len(value_list)) * 100


def calculate_with_graph():
    for k in range(5):
        factor = (0.8 + k / 10)
        angular_speed = factor * v_0 / (earth_ray + altitude)

        # Initialize objects and launch process
        initial_point = SatellitePoint(0, earth_ray + altitude, 0, 0, angular_speed)
        movement = SatelliteMovement(initial_point, ray_2, theta_2, 30000, 10)

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
        plots_parameters = msg["graph"]["plots"]
        fig, graphs = create_graph(factor, movement)
        graphs[0].plot(time_euler, ray_euler, 'b', label=plots_parameters["euler"]["ray"])
        graphs[0].plot(time_euler, real_ray_euler, 'c+', label=plots_parameters["euler"]["real_ray"])
        graphs[2].plot(time_euler, theta_euler, 'r', label=plots_parameters["euler"]["theta"])

        graphs[1].plot(time_odeint, ray_odeint, 'k', label=plots_parameters["odeint"]["ray"])
        graphs[1].plot(time_odeint, real_ray_odeint, 'g+', label=plots_parameters["odeint"]["real_ray"])
        graphs[3].plot(time_odeint, theta_odeint, 'm', label=plots_parameters["odeint"]["theta"])

        for ax in graphs:
            ax.legend()
        plt.show()


def calculate_without_graph(euler_path="results/euler.txt", odeint_path="results/odeint.txt"):
    euler_file = open(euler_path, 'w')
    odeint_file = open(odeint_path, 'w')
    start_time = time.time_ns()
    for h in range(5):
        for k in range(5):
            factor = (0.8 + k / 10)
            angular_speed = factor * v_0 / (earth_ray + altitude)

            # Initialize objects and launch process
            initial_point = SatellitePoint(0, earth_ray + altitude, 0, 0, angular_speed)
            movement = SatelliteMovement(initial_point, ray_2, theta_2, 3000, 10 ** (h - 2))

            # Get euler values to display
            movement.calculate_points_euler()
            ray_euler = movement.get_attribute_list("ray")
            movement.calculate_points_real_solution()
            real_ray_euler = movement.get_attribute_list("ray")

            # pas; speed_factor; erreur; calculation_time; collision
            euler_file.write(msg["output_format"].format(10 ** (h - 2),
                                                         str(factor)[:3],
                                                         calculate_error(ray_euler, real_ray_euler),
                                                         movement.euler_calculation_time,
                                                         movement.points[-1].collision_check(prints=False)))
            euler_file.write("\n")
            # Get odeint values to display
            movement.calculate_points_odeint()
            ray_odeint = movement.get_attribute_list("ray")
            movement.calculate_points_real_solution()
            real_ray_odeint = movement.get_attribute_list("ray")

            # pas; speed_factor; erreur; calculation_time; collision
            odeint_file.write(msg["output_format"].format(10 ** (h - 2), str(factor)[:3],
                                                          calculate_error(ray_odeint, real_ray_odeint),
                                                          movement.odeint_calculation_time,
                                                          movement.points[-1].collision_check(prints=False)))
            odeint_file.write("\n")
            logger.debug("Calculation for %s * V0 with a step of %0.2f finished", str(factor)[:3], 10 ** (h - 2))
        euler_file.write("\n")
        odeint_file.write("\n")
        logger.debug("Calculation with a step of %0.2f finished", 10 ** (h - 2))
    final_time = (time.time_ns() - start_time) / 10 ** 9
    euler_file.write("Total calculation time: {}s".format(final_time))
    odeint_file.write("Total calculation time: {}s".format(final_time))
    euler_file.close()
    odeint_file.close()
    logger.info("Calculation finished!")
    logger.info("Total calculation time: %d s", final_time)
