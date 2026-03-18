import importlib.util
import os
import inspect, types


class Config:
    """
    Populated dynamically from a .py config file.
    Keys are lowercased, accessed as attributes: cfg.api_id

    Example config.py:
        import os
        API_ID   = int(os.environ["TELEGRAM_API_ID"])
        API_HASH = os.environ["TELEGRAM_API_HASH"]
        FOLDER_NAME = "Notes"
    """

    _SKIP = frozenset({"__builtins__", "__name__", "__doc__",
                       "__package__", "__loader__", "__spec__", "__file__"})

    def __init__(self, data: dict):
        object.__setattr__(self, "_data", {k.lower(): v for k, v in data.items()})

    def __getattr__(self, key: str):
        try:
            return self._data[key.lower()]
        except KeyError:
            raise AttributeError(f"Config has no attribute '{key}'")

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self._data.items())
        return f"Config({attrs})"

    def get(self, key: str, default=None):
        return self._data.get(key.lower(), default)

    def require(self, *keys: str):
        """Raise clearly if any expected key is missing."""
        missing = [k for k in keys if k.lower() not in self._data]
        if missing:
            raise ValueError(f"Config is missing required keys: {missing}")

    @classmethod
    def from_file(cls, path: str) -> "Config":
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        spec   = importlib.util.spec_from_file_location("_user_config", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        data = {
            k: v
            for k, v in vars(module).items()
            if not k.startswith("_")
               and k not in cls._SKIP
               and not isinstance(v, types.ModuleType)
        }
        return cls(data)



def add_cfg_argument(parser: argparse.ArgumentParser):
    caller_dir = os.path.dirname(os.path.abspath(inspect.stack()[1].filename))
    parser.add_argument(
        "-c", "--config",
        metavar="PATH",
        default=os.path.join(caller_dir, "cfg.py"),
        help="Path to config .py file (default: <caller dir>/cfg.py)",
    )