# -*- coding: utf-8 -*-

import json
import yaml


def dict_to_yamlfile(data, filepath):
    if not isinstance(data, dict):
        raise ValueError("转换yaml的数据不为json")

    yaml.safe_dump(data=yaml.load(json.dumps(data)),
                   stream=open(filepath, 'w'),
                   default_flow_style=False)
