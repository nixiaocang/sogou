#!/usr/local/bin/python
# -*- coding:utf-8 -*-

import os
import logging
import logging.config
import traceback
from util.config import Configuration
log_path = Configuration().get('global', 'log_path')
conf_file = os.path.join(os.getenv('CONF'), 'logging.conf')
logging.config.fileConfig(conf_file, defaults = {'log_path': log_path})

def runtime_logger():
    return logging.getLogger('runtime')

def print_stack():
    runtime_logger().info(traceback.format_exc().replace("\n", "####"))
