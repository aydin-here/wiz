try:
    import yaml

    YAML_AVAILABLE = True
except Exception:
    YAML_AVAILABLE = False

from errors import WizError


class YamlModule:

    def __init__(self):

        if not YAML_AVAILABLE:
            return

        self.functions = {
            "parse": self.parse,
            "load": self.parse,
            "dump": self.dump,
            "stringify": self.dump,
        }

    def _check(self):
        if not YAML_AVAILABLE:
            raise WizError("The 'yaml' module requires pyyaml.")

    def parse(self, text):
        self._check()
        return yaml.safe_load(text)

    def dump(self, data, indent=2, sort=False):
        self._check()
        return yaml.dump(
            data,
            indent=int(indent),
            sort_keys=bool(sort),
            default_flow_style=False
        ).rstrip()