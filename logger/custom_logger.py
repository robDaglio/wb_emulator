import logging
import os
import sys


class Logger:
    def __init__(
            self,
            name='default',
            log_level='INFO',
            log_to_stdout=True,
            log_to_file=False,
            file_mode='w+',
            log_file_name='app.log',
            log_file_path='logs',
            log_format='%(process)d - %(asctime)s - %(levelname)s - %(funcName)s: '
                       '%(message)s',
            date_format='%m-%d-%Y-%H:%M:%S',

    ):
        self.name = name
        self.log_level = log_level
        self.log_to_stdout = log_to_stdout
        self.log_to_file = log_to_file
        self.file_mode = file_mode
        self.date_fmt = date_format
        self.log_file_name = log_file_name
        self.log_file_path = log_file_path
        self.log_format = log_format

        self.create_log_dir()

    def create_log_dir(self):
        if not os.path.exists(self.log_file_path) and self.log_to_file:
            os.makedirs(self.log_file_path)

    @staticmethod
    def log_level_type(log_level):
        return log_level.upper() if isinstance(log_level, str) else log_level

    def get_logger(self):
        logger = logging.getLogger(self.name)
        try:
            logger.setLevel(logging.getLevelName(self.log_level.upper()))
        except Exception as e:
            logging.exception(e)

        if not logger.handlers:
            if self.log_to_file:
                log_path = os.path.join(self.log_file_path, self.log_file_name)
                file_handler = logging.FileHandler(log_path, self.file_mode, 'utf-8')
                file_handler.setFormatter(logging.Formatter(self.log_format))
                logger.addHandler(file_handler)

            if self.log_to_stdout:
                stream_handler = logging.StreamHandler(sys.stdout)
                stream_handler.setFormatter(logging.Formatter(self.log_format, self.date_fmt))
                logger.addHandler(stream_handler)

        return logger
