from pathlib import Path


class InitConfig:
    def __init__(self, prelog_path: str, config_path: str, version: str):
        self.prelog_path: Path = Path(prelog_path)
        self.config_path: Path = Path(config_path)
        self.version: str = version

    @classmethod
    def default(cls):
        return cls("./log/init.log", "./config/config.yaml", "1.0 BETA")


INIT_CONFIG = InitConfig.default()
