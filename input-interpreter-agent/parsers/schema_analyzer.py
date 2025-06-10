from typing import Dict, Any, List, Tuple
from models.endpoint_model import EndpointInfo, Parameter


class SchemaAnalyzer:

    def analyze_endpoint_requirements(self, endpoint: EndpointInfo) -> EndpointInfo:
        """Analyze endpoint and enhance with JMeter-specific requirements"""

        # Determine required headers
        endpoint.headers_required = self._extract_required_headers(endpoint)

        # Generate response assertions
        endpoint.response_assertions = self._generate_response_assertions(endpoint)

        # Set expected response codes
        endpoint.expected_response_codes = self._extract_expected_codes(endpoint)

        return endpoint

    def _extract_required_headers(self, endpoint: EndpointInfo) -> Dict[str, str]:
        """Extract headers required for the endpoint"""
        headers = {}

        # Content-Type header for POST/PUT/PATCH
        if endpoint.method.value in ['POST', 'PUT', 'PATCH'] and endpoint.request_body:
            headers['Content-Type'] = endpoint.request_body.content_type

        # Accept header based on response content types
        if endpoint.responses:
            content_types = [r.content_type for r in endpoint.responses if r.content_type]
            if content_types:
                headers['Accept'] = content_types[0]

        # Headers from parameters
        for param in endpoint.parameters:
            if param.location == 'header' and param.required:
                headers[param.name] = f"${{{param.name}}}"  # JMeter variable format

        return headers

    def _generate_response_assertions(self, endpoint: EndpointInfo) -> List[str]:
        """Generate response assertions for JMeter"""
        assertions = []

        # Status code assertions
        success_codes = [r.status_code for r in endpoint.responses
                         if r.status_code.startswith('2')]
        if success_codes:
            assertions.append(f"Response Code: {','.join(success_codes)}")

        # Content type assertions
        content_types = list(set([r.content_type for r in endpoint.responses
                                  if r.content_type and r.status_code.startswith('2')]))
        if content_types:
            assertions.append(f"Content-Type: {content_types[0]}")

        # Schema-based assertions for JSON responses
        for response in endpoint.responses:
            if (response.content_type == 'application/json' and
                    response.status_code.startswith('2') and
                    response.schema):

                required_fields = response.schema.get('required', [])
                if required_fields:
                    for field in required_fields[:3]:  # Limit to top 3 fields
                        assertions.append(f"JSON Path: $.{field}")

        return assertions

    def _extract_expected_codes(self, endpoint: EndpointInfo) -> List[str]:
        """Extract expected response codes"""
        codes = []

        for response in endpoint.responses:
            if response.status_code.startswith('2'):  # Success codes
                codes.append(response.status_code)

        return codes if codes else ['200']

    def generate_sample_data(self, endpoint: EndpointInfo) -> Dict[str, Any]:
        """Generate sample test data for the endpoint"""
        sample_data = {}

        # Path parameters
        path_params = [p for p in endpoint.parameters if p.location == 'path']
        for param in path_params:
            sample_data[param.name] = self._generate_sample_value(param)

        # Query parameters
        query_params = [p for p in endpoint.parameters if p.location == 'query']
        for param in query_params:
            sample_data[param.name] = self._generate_sample_value(param)

        # Request body
        if endpoint.request_body and endpoint.request_body.schema:
            sample_data['request_body'] = self._generate_sample_from_schema(
                endpoint.request_body.schema
            )

        return sample_data

    def _generate_sample_value(self, param: Parameter) -> Any:
        """Generate sample value for a parameter"""
        if param.example is not None:
            return param.example

        if param.default_value is not None:
            return param.default_value

        if param.enum_values:
            return param.enum_values[0]

        # Type-based defaults
        type_defaults = {
            'string': 'sample_string',
            'integer': 1,
            'number': 1.0,
            'boolean': True,
            'array': [],
            'object': {}
        }

        return type_defaults.get(param.type, 'sample_value')

    def _generate_sample_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sample data from JSON schema"""
        if schema.get('type') != 'object':
            return {}

        sample = {}
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        for prop_name, prop_schema in properties.items():
            if prop_name in required:  # Only required fields for now
                sample[prop_name] = self._generate_value_from_schema(prop_schema)

        return sample

    def _generate_value_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Generate value from property schema"""
        schema_type = schema.get('type', 'string')

        if 'example' in schema:
            return schema['example']

        if 'enum' in schema:
            return schema['enum'][0]

        type_generators = {
            'string': lambda: 'sample_string',
            'integer': lambda: 1,
            'number': lambda: 1.0,
            'boolean': lambda: True,
            'array': lambda: [],
            'object': lambda: {}
        }

        return type_generators.get(schema_type, lambda: 'sample_value')()