import yaml


def get_yaml_data(yaml_file_path):
    with open(yaml_file_path) as f:
        yaml_data = yaml.safe_load(f)
    return yaml_data

