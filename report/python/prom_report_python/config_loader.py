import yaml
import os

def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    # 环境变量覆盖密码
    if os.getenv('EMAIL_PASSWORD'):
        cfg['email']['password'] = os.getenv('EMAIL_PASSWORD')
    return cfg

config = load_config()
