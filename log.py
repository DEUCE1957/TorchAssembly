import logging, sys
from contextlib import redirect_stdout
from pathlib import Path
"""
Credit: @Aldo (Feb 20 2020)
Modified by: @deuce1957 (Jan 16 2021)
"""

def log_decor(name="default", log_dir=Path.cwd() / "logs", level=logging.INFO, overwrite=False, tolerate_errors=False):
    """
    Decorator Factory, allows arguments to be passed to wrapper.
    Example Use:
        @log_decor(name='test', log_dir=/path/to/log_dir, level=logging.DEBUG)
    name (str): Name of log file
    log_dir (path-like): Path to folder where log files should be stored
    level (int): Level of detail to log, values above INFO (20) will pipe all stdout (includes print statements) to log
         (NOTSET: 0, DEBUG: 10, INFO: 20, WARNING: 30, ERROR:40, CRITICAL:50).
    overwrite (bool): Whether to overwrite existing logfile.
    tolerate_errors (bool): Whether to halt program execution if an error is thrown.
    """
    def decorator(func):
        """Wraps logging around any passed function."""
        def wrapper(*args, **kwargs):
            logger = generate_logger(log_dir / f"{name}.log", level, overwrite)
            try:
                return func(*args, **kwargs) 
            except Exception as e:
                logger.exception(e) # Write error message to file
                if tolerate_errors:
                    return e
                else:
                    raise e
        return wrapper
    return decorator


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, level):
       self.logger = logger
       self.level = level
       self.linebuf = ''

    def write(self, buf):
       for line in buf.rstrip().splitlines():
          self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

def generate_logger(path, level, overwrite):
    """
    Create a logger object
    path (str): Path of the log file.
    level (int): Level of detail to log, values above INFO (20) will pipe all stdout (includes print statements) to log
         (NOTSET: 0, DEBUG: 10, INFO: 20, WARNING: 30, ERROR:40, CRITICAL:50).
    """
    # Create a logger and set the level.
    logger = logging.getLogger(path.name.split(".")[0])
    logger.setLevel(level)

    # Create file handler, log format and add the format to file handler
    file_handler = logging.FileHandler(path, mode="w" if overwrite else "a") # Will overwrite previous logfile!

    # See https://docs.python.org/3/library/logging.html#logrecord-attributes
    # for log format attributes.
    log_format = '%(levelname)s %(asctime)s %(message)s'
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    if level >= logging.INFO: # Redirect print statements to log!
        sys.stdout = StreamToLogger(logger, logging.INFO)
    return logger