import os
from configparser import ConfigParser


class FieldConfig:

    def __init__(self, data_root):
        self.field_config = ConfigParser()
        self.field_config.read(os.path.join(data_root, 'cfg', 'fields.ini'))

    def get_axis_label(self, field):
        label = self.field_config.get('axis label', field)
        if self.field_config.has_option('unit', field):
            label = label.format(unit=self.field_config.get('unit', field)[1:-1])

        return label[1:-1]
