# coding: utf-8
from logging import getLogger
from util import initialize_logger, initialize_messages_config

if __name__ == "__main__":
    # Logger configuration
    initialize_logger()
    getLogger('matplotlib').disabled = True
    getLogger('matplotlib.font_manager').disabled = True
    getLogger('matplotlib.pyplot').disabled = True

    # Messages configuration
    initialize_messages_config()

    import satellite_factory
    # Launch calculations
    satellite_factory.calculate()

    getLogger("ChuckNorris").warning("Chuck Norris n'attrape pas le coronavirus, c'est lui qui l'infecte")
