import requests
import yaml
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from models.endpoint_model import *


class SwaggerParser:
    def __init__(self):
        self.spec_data = None
        self.base_url = ""

    def fetch_spec(self, swagger_url: str) -> Dict[str, Any]:
        """Fetch Swagger specification from URL"""
        try:
            response = requests.get(swagger_url, timeout=30)
            response.raise_for_status()

            # Determine if JSON or YAML
            content_type = response.headers.get('content-type', '').lower()

            if 'json' in content_type:
                self.spec_data = response.json()
            else:
                # Try YAML parsing
                self.spec_data = yaml.safe_load(response.text)

            return self.spec_data

        except Exception as e:
            raise Exception(f"Failed to fetch Swagger spec: {str(e)}")

    def parse_servers(self, spec: Dict[str, Any]) -> List[str]:
        """Extract server URLs"""
        servers = []

        # OpenAPI 3.x
        if 'servers' in spec:
            for server in spec['servers']:
                servers.append(server.get('url', ''))

        # Swagger 2.x
        elif 'host' in spec:
            scheme = spec.get('schemes', ['https'])[0]
            host = spec['host']
            base_path = spec.get('basePath', '')
            servers.append(f"{scheme}://{host}{base_path}")

        return servers

    def parse_security_definitions(self, spec: Dict[str, Any]) -> List[SecurityRequirement]:
        """Parse global security definitions"""
        securities = []

        # OpenAPI 3.x
        if 'components' in spec and 'securitySchemes' in spec['components']:
            for name, scheme in spec['components']['securitySchemes'].items():
                sec_req = self._parse_security_scheme(name, scheme)
                if sec_req:
                    securities.append(sec_req)

        # Swagger 2.x
        elif 'securityDefinitions' in spec:
            for name, scheme in spec['securityDefinitions'].items():
                sec_req = self._parse_security_scheme(name, scheme)
                if sec_req:
                    securities.append(sec_req)

        return securities

    def _parse_security_scheme(self, name: str, scheme: Dict[str, Any]) -> Optional[SecurityRequirement]:
        """Parse individual security scheme"""
        scheme_type = scheme.get('type', '').lower()

        if scheme_type == 'apikey':
            return SecurityRequirement(
                type=AuthType.API_KEY,
                name=name,
                location=scheme.get('in', 'header'),
                scheme=scheme.get('name', name)
            )
        elif scheme_type == 'http':
            auth_scheme = scheme.get('scheme', '').lower()
            if auth_scheme == 'bearer':
                return SecurityRequirement(
                    type=AuthType.BEARER,
                    name=name,
                    scheme='bearer'
                )
            elif auth_scheme == 'basic':
                return SecurityRequirement(
                    type=AuthType.BASIC,
                    name=name,
                    scheme='basic'
                )
        elif scheme_type == 'oauth2':
            return SecurityRequirement(
                type=AuthType.OAUTH2,
                name=name,
                flows=scheme.get('flows', {})
            )

        return None

    def parse_parameters(self, params: List[Dict[str, Any]]) -> List[Parameter]:
        """Parse endpoint parameters"""
        parameters = []

        for param in params:
            param_obj = Parameter(
                name=param.get('name', ''),
                location=param.get('in', 'query'),
                type=param.get('type', param.get('schema', {}).get('type', 'string')),
                required=param.get('required', False),
                description=param.get('description', ''),
                example=param.get('example'),
                default_value=param.get('default')
            )

            # Handle enum values
            if 'enum' in param:
                param_obj.enum_values = param['enum']
            elif 'schema' in param and 'enum' in param['schema']:
                param_obj.enum_values = param['schema']['enum']

            parameters.append(param_obj)

        return parameters

    def parse_request_body(self, request_body: Dict[str, Any]) -> Optional[RequestBody]:
        """Parse request body definition"""
        if not request_body:
            return None

        content = request_body.get('content', {})

        # Get first content type (usually application/json)
        content_type = list(content.keys())[0] if content else 'application/json'

        if content_type in content:
            schema = content[content_type].get('schema', {})
            examples = content[content_type].get('examples', {})

            return RequestBody(
                content_type=content_type,
                schema=schema,
                required=request_body.get('required', True),
                examples=examples
            )

        return None

    def parse_responses(self, responses: Dict[str, Any]) -> List[Response]:
        """Parse response definitions"""
        response_list = []

        for status_code, response_def in responses.items():
            content = response_def.get('content', {})

            # Handle multiple content types
            for content_type, content_def in content.items():
                response_obj = Response(
                    status_code=status_code,
                    description=response_def.get('description', ''),
                    content_type=content_type,
                    schema=content_def.get('schema', {}),
                    headers=response_def.get('headers', {})
                )
                response_list.append(response_obj)

            # If no content, create basic response
            if not content:
                response_obj = Response(
                    status_code=status_code,
                    description=response_def.get('description', ''),
                    content_type='text/plain'
                )
                response_list.append(response_obj)

        return response_list