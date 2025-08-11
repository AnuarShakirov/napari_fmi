__version__ = "0.0.1"

from .widget_main import FMIProcessor

import matplotlib.pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

__all__ = ["FMIProcessor"]
