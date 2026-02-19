import traceback
import logging
from PySide6.QtCore import QRunnable, Slot, Signal, QObject

logger = logging.getLogger("airingdeck.worker")

class WorkerSignals(QObject):
    """ 
    Defines the signals available from a running worker thread.
    """
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)

class Worker(QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as exc:
            fn_name = getattr(self.fn, "__name__", self.fn.__class__.__name__)
            logger.error("Worker '%s' failed", fn_name, exc_info=True)
            self.signals.error.emit((type(exc), exc, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
