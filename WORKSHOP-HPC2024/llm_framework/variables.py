import os

from jinja2 import Environment, FileSystemLoader, select_autoescape, StrictUndefined
import yaml

web_proxy = {
    "http": os.environ.get('http_proxy'),
    "https": os.environ.get('https_proxy')
}
debug=True
cache_enabled = True # 控制是否打开cache（bing和chatgpt）
cache_size = None # None for unlimited cache

article_max_len = 5000

jinja_environment = Environment(
    loader=FileSystemLoader(['./', './llm_framework/', './llm_framework/prompts/']),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
    line_comment_prefix="#",
    undefined=StrictUndefined,
)
system_start = "<|system_start|>"
system_end = "<|system_end|>"
user_start = "<|user_start|>"
user_end = "<|user_end|>"
assistant_start = "<|assistant_start|>"
assistant_end = "<|assistant_end|>"

news_splitter = '\n'
output_less_NEI=True

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
with open(os.path.join(parent_dir, "config.yaml"), "r") as config_file:
    config = yaml.safe_load(config_file)
    openai_config = config['openai']
    bing_config = config['bing']
    scraper_config = config['scraper']

inference_cost_per_1000_tokens = {
    "gpt-35-turbo": (0.0005, 0.00015),
    "gpt-35-turbo-16k":(0.015, 0.02),
    "gpt-35-turbo-instruct":(0.0075, 0.01),
    "gpt-4-preview":(0.05, 0.15),
    "gpt-4o":(0.005, 0.015),
    "gpt-4o-mini":(0.00015, 0.0006),
    "gpt-4-turbo": (0.01, 0.03), 
    "gpt-4o-2024-08-06": (0.0025, 0.01), 
    "gpt-4-turbo-2024-04-09": (0.01, 0.03), 
    "gpt-4-0125-preview": (0.01, 0.03), 
}

from .utils import CustomLogger, get_current_time
logger_instance = CustomLogger('logs', f'{get_current_time()}.log')
logger, file_handler = logger_instance.create_logger()
info, error = logger.info, logger.error