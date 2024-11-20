import datetime, pytz, os, stat , logging, sys
from functools import wraps
from collections import OrderedDict
from .variables import (
    cache_size,
    cache_enabled
)
import json
from hashlib import md5

def set_seed(seed_num):
    import random
    import numpy as np
    random.seed(seed_num)
    np.random.seed(seed_num)

def cache(cache_type):

    def decorator(func):
        func.cache = OrderedDict()

        @wraps(func)
        def wrapper(*args, **kwargs):


            if not cache_enabled:
                return func(*args, **kwargs)

            if cache_type == 'chatgpt_template_generate': # openai只通过template_file和prompt_parameters_values来取cache
                key = (kwargs.get('template_file'), md5(json.dumps(kwargs.get('prompt_parameter_values')).encode()).hexdigest(), kwargs.get('model'))

            elif cache_type == 'newspaper':
                key = (args[1]) # scrape_news_concurrent传参只能通过普通的方式传
            elif cache_type == 'bing_search': # bing只通过query来取cache
                key = (kwargs.get('query'))
            elif cache_type == 'chatgpt_chat_generate':
                key = (md5(json.dumps(kwargs.get('messages')).encode()).hexdigest(), kwargs.get('model'))
            else:
                if len(kwargs) == 0:
                    key = (args)
                else:
                    key = (args, tuple(sorted(kwargs.items())))

            if key in func.cache:
                value = func.cache[key]

                func.cache.move_to_end(key)  # 将访问的键移动到末尾，以更新其访问顺序
            else:
                value = func(*args, **kwargs)
                if value == None and cache_type == 'newspaper' :
                    return None # 如果爬取某个url失败，不将其存入cache中
                if cache_size is not None and len(func.cache) >= cache_size:
                    func.cache.popitem(last=False)  # 如果缓存已满，删除第一个插入的键值对
                func.cache[key] = value  # 添加新的键值对
            return value
        return wrapper
    return decorator

class CustomLogger:
    def __init__(self, parent_dir, file_name):
        self.parent_dir = parent_dir
        self.file_name = file_name
        self.logger = None
        self.file_handler = None

    def create_logger(self):
        file_path = f'{self.parent_dir}{os.sep}{self.file_name}'
        os.makedirs(self.parent_dir, exist_ok=True)
        with open(file_path, 'w+', encoding='utf-8') as f:
            pass  # 仅创建文件
        os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        logger = logging.getLogger('NewsAug')
        logger.setLevel(logging.INFO)

        self.file_handler = logging.FileHandler(file_path)
        self.file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)d : %(message)s')
        self.file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        class LogStream:
            def write(self, message):
                if message != '\n':  # 忽略换行符，避免无限递归
                    logger.info(message)

            def flush(self):
                pass

        sys.stdout = LogStream()

        def log_exception(exctype, value, tb):
            logger.error("Uncaught exception", exc_info=(exctype, value, tb))

        sys.excepthook = log_exception

        logger.addHandler(self.file_handler)
        logger.addHandler(console_handler)

        self.logger = logger
        return logger, self.file_handler

    def update_log_file(self, new_file_name):
        if self.file_handler:
            # 获取当前日志文件的路径
            current_log_file_path = self.file_handler.baseFilename
            # 创建新的日志文件路径

            new_file_parent_dir = os.path.dirname(new_file_name)
            os.makedirs(new_file_parent_dir, exist_ok=True)
            # 将当前日志文件的内容复制到新的日志文件
            with open(current_log_file_path, 'r', encoding='utf-8') as old_file:
                with open(new_file_name, 'w+', encoding='utf-8') as new_file:
                    new_file.write(old_file.read())
            # 从logger中移除旧的file_handler
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()
            # 删除旧的日志文件
            os.remove(current_log_file_path)

            # 创建新的file_handler
            self.file_handler = logging.FileHandler(new_file_name)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)d : %(message)s')
            self.file_handler.setFormatter(formatter)
            # 将新的file_handler添加到logger
            self.logger.addHandler(self.file_handler)

            # 更新file_name属性
            self.file_name = new_file_name



def get_current_time(format='%Y-%m-%d-%H-%M-%S', timezone='Asia/Shanghai'):
    now = datetime.datetime.now()
    timezone = pytz.timezone(timezone)
    now = now.astimezone(timezone)

    timestamp = now.strftime(format)
    return timestamp