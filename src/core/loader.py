import importlib
import pkgutil
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class CommandLoader:
    @staticmethod
    async def load_commands(commands_package: str = "commands") -> None:
        """Load all command modules from the specified package
        
        Args:
            commands_package: The package containing command modules
        """
        try:
            # Import the commands package
            package = importlib.import_module(commands_package)
            package_path = Path(package.__file__).parent

            # Load all modules in the package
            for module_info in pkgutil.iter_modules([str(package_path)]):
                try:
                    importlib.import_module(f"{commands_package}.{module_info.name}")
                    logger.info(f"Loaded commands from {module_info.name}")
                except Exception as e:
                    logger.error(f"Failed to load commands from {module_info.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load commands package: {e}") 