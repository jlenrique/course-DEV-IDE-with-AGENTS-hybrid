"""Tool API client libraries.

Each client extends BaseAPIClient with tool-specific authentication,
endpoint mappings, and response parsing.
"""

from scripts.api_clients.base_client import (
    APIError,
    AuthenticationError,
    BaseAPIClient,
    RateLimitError,
)
from scripts.api_clients.botpress_client import BotpressClient
from scripts.api_clients.canvas_client import CanvasClient
from scripts.api_clients.descript_client import DescriptClient
from scripts.api_clients.elevenlabs_client import ElevenLabsClient
from scripts.api_clients.gamma_client import GammaClient
from scripts.api_clients.notion_client import NotionClient
from scripts.api_clients.panopto_client import PanoptoClient
from scripts.api_clients.qualtrics_client import QualtricsClient
from scripts.api_clients.wondercraft_client import WondercraftClient

__all__ = [
    "APIError",
    "AuthenticationError",
    "BaseAPIClient",
    "BotpressClient",
    "CanvasClient",
    "DescriptClient",
    "ElevenLabsClient",
    "GammaClient",
    "NotionClient",
    "PanoptoClient",
    "QualtricsClient",
    "RateLimitError",
    "WondercraftClient",
]
