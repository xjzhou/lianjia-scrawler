# coding: utf-8

import logging
import logging.handlers
from logging import *
from datetime import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

rht = logging.handlers.TimedRotatingFileHandler("my.log", 'D')
fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s", "%Y-%m-%d %H:%M:%S")
rht.setFormatter(fmt)
logger.addHandler(rht)
