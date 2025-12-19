from pydantic import BaseModel  
from pathlib import Path
import logging
import yaml

log = logging.getLogger(__file__)




class Config(BaseModel):
    """Настройка приложения."""

    @classmethod
    def read_config(cls) -> "Config":
        """Чтение конфигурации из YAML файла."""
        cfg_path = Path(__file__).parent.parent.parent / "config.yaml"

        try:
            cfg_path.exists()
        except (OSError, ValueError) as exc:
            log.exception('Файл с настрйоками приложения не обнаружен. Завершаем приложение.')
            raise exc

        config_path = (
            Path(__file__).parent.parent.parent.parent / 'config.yaml'
        )
        with Path(config_path).open(encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return Config(**config)

        

settings = Config()