from .field_config import FieldConfig

global field_config


def setup_field_config(data_root):
    global field_config
    field_config = FieldConfig(data_root)


def get_axis_label(field):
    if field_config is not None:
        return field_config.get_axis_label(field)
    else:
        raise ValueError('Field config is not set up yet, call config.setup_field_config first.')