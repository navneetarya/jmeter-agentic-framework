from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(Enum):
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "apikey"
    OAUTH2 = "oauth2"


@dataclass
class Parameter:
    name: str
    location: str  # query, header, path, body
    type: str
    required: bool = False
    default_value: Any = None
    description: str = ""
    enum_values: List[str] = field(default_factory=list)
    format: Optional[str] = None
    example: Any = None


@dataclass
class RequestBody:
    content_type: str
    schema: Dict[str, Any]
    required: bool = True
    examples: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Response:
    status_code: str
    description: str
    content_type: str
    schema: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class SecurityRequirement:
    type: AuthType
    name: str
    location: str = ""  # header, query, cookie
    scheme: str = ""  # bearer, basic
    flows: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EndpointInfo:
    path: str
    method: HttpMethod
    operation_id: str
    summary: str
    description: str
    tags: List[str] = field(default_factory=list)
    parameters: List[Parameter] = field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: List[Response] = field(default_factory=list)
    security: List[SecurityRequirement] = field(default_factory=list)
    deprecated: bool = False

    # JMeter-specific fields
    expected_response_codes: List[str] = field(default_factory=lambda: ["200"])
    response_assertions: List[str] = field(default_factory=list)
    headers_required: Dict[str, str] = field(default_factory=dict)


@dataclass
class SwaggerAnalysis:
    base_url: str
    title: str
    version: str
    description: str
    endpoints: List[EndpointInfo] = field(default_factory=list)
    global_security: List[SecurityRequirement] = field(default_factory=list)
    servers: List[str] = field(default_factory=list)