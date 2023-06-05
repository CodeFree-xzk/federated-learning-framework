import yaml


def get_args():
    with open('../config/config.yaml', 'r', encoding='utf8') as file:
        args = yaml.safe_load(file)
    return args
