# ai_devops_mcp/server/context.py

from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class AppContext:
    def __init__(self) -> None:
        self._providers: dict[str, Any] = {}

    def register_provider(
        self,
        name: str,
        provider: Any,
    ) -> None:
        logger.info("Registering provider: %s", name)
        self._providers[name] = provider

    def get_provider(self, name: str) -> Optional[Any]:
        return self._providers.get(name)

    def has_provider(self, name: str) -> bool:
        return name in self._providers

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        
        provider = self.get_provider(name)
        if provider is None:
            raise AttributeError(
                f"Provider '{name}' not registered. "
                f"Available: {list(self._providers.keys())}"
            )
        return provider

    def close(self) -> None:
        logger.info("Closing all providers...")
        
        for name, provider in self._providers.items():
            try:
                if hasattr(provider, "close"):
                    provider.close()
                    logger.info("Provider '%s' closed", name)
            except Exception as exc:
                logger.error(
                    "Error closing provider '%s': %s",
                    name,
                    exc,
                )