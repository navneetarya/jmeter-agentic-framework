from typing import Dict, Any, List
from parsers.swagger_parser import SwaggerParser
from parsers.schema_analyzer import SchemaAnalyzer
from models.endpoint_model import *


class InputInterpreterAgent:
    def __init__(self):
        self.parser = SwaggerParser()
        self.analyzer = SchemaAnalyzer()
        self.analysis_result = None

    def process_swagger_url(self, swagger_url: str) -> SwaggerAnalysis:
        """Main method to process Swagger URL and return analysis"""

        print(f"🔍 Fetching Swagger specification from: {swagger_url}")

        # Step 1: Fetch and parse spec
        spec_data = self.parser.fetch_spec(swagger_url)

        # Step 2: Extract basic info
        analysis = SwaggerAnalysis(
            base_url="",
            title=spec_data.get('info', {}).get('title', 'API'),
            version=spec_data.get('info', {}).get('version', '1.0'),
            description=spec_data.get('info', {}).get('description', '')
        )

        # Step 3: Parse servers
        analysis.servers = self.parser.parse_servers(spec_data)
        if analysis.servers:
            analysis.base_url = analysis.servers[0]

        # Step 4: Parse global security
        analysis.global_security = self.parser.parse_security_definitions(spec_data)

        # Step 5: Parse endpoints
        analysis.endpoints = self._parse_all_endpoints(spec_data)

        # Step 6: Enhance with JMeter-specific analysis
        for i, endpoint in enumerate(analysis.endpoints):
            analysis.endpoints[i] = self.analyzer.analyze_endpoint_requirements(endpoint)

        self.analysis_result = analysis
        print(f"✅ Successfully analyzed {len(analysis.endpoints)} endpoints")

        return analysis

    def _parse_all_endpoints(self, spec_data: Dict[str, Any]) -> List[EndpointInfo]:
        """Parse all endpoints from the specification"""
        endpoints = []
        paths = spec_data.get('paths', {})

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in [m.value for m in HttpMethod]:
                    endpoint = self._parse_single_endpoint(path, method.upper(), operation)
                    if endpoint:
                        endpoints.append(endpoint)

        return endpoints

    def _parse_single_endpoint(self, path: str, method: str, operation: Dict[str, Any]) -> EndpointInfo:
        """Parse a single endpoint operation"""

        endpoint = EndpointInfo(
            path=path,
            method=HttpMethod(method),
            operation_id=operation.get('operationId', f"{method}_{path}".replace('/', '_')),
            summary=operation.get('summary', ''),
            description=operation.get('description', ''),
            tags=operation.get('tags', []),
            deprecated=operation.get('deprecated', False)
        )

        # Parse parameters
        if 'parameters' in operation:
            endpoint.parameters = self.parser.parse_parameters(operation['parameters'])

        # Parse request body
        if 'requestBody' in operation:
            endpoint.request_body = self.parser.parse_request_body(operation['requestBody'])

        # Parse responses
        if 'responses' in operation:
            endpoint.responses = self.parser.parse_responses(operation['responses'])

        # Parse security (endpoint-specific)
        if 'security' in operation:
            endpoint.security = self._parse_endpoint_security(operation['security'])

        return endpoint

    def _parse_endpoint_security(self, security: List[Dict[str, Any]]) -> List[SecurityRequirement]:
        """Parse endpoint-specific security requirements"""
        # Simplified - would need to reference global security definitions
        return []

    def get_endpoint_summary(self) -> Dict[str, Any]:
        """Get a summary of all endpoints for the next agent"""
        if not self.analysis_result:
            return {}

        summary = {
            'api_info': {
                'title': self.analysis_result.title,
                'version': self.analysis_result.version,
                'base_url': self.analysis_result.base_url,
                'total_endpoints': len(self.analysis_result.endpoints)
            },
            'endpoints': []
        }

        for endpoint in self.analysis_result.endpoints:
            endpoint_summary = {
                'path': endpoint.path,
                'method': endpoint.method.value,
                'operation_id': endpoint.operation_id,
                'summary': endpoint.summary,
                'required_params': [p.name for p in endpoint.parameters if p.required],
                'auth_required': len(endpoint.security) > 0,
                'request_body_required': endpoint.request_body is not None,
                'expected_response_codes': endpoint.expected_response_codes,
                'headers_required': endpoint.headers_required,
                'response_assertions': endpoint.response_assertions
            }
            summary['endpoints'].append(endpoint_summary)

        return summary

    def export_detailed_analysis(self) -> Dict[str, Any]:
        """Export complete analysis for downstream agents"""
        if not self.analysis_result:
            return {}

        return {
            'swagger_analysis': self.analysis_result,
            'endpoint_count': len(self.analysis_result.endpoints),
            'authentication_methods': [sec.type.value for sec in self.analysis_result.global_security],
            'content_types': list(set([
                ep.request_body.content_type for ep in self.analysis_result.endpoints
                if ep.request_body
            ])),
            'sample_data': {
                ep.operation_id: self.analyzer.generate_sample_data(ep)
                for ep in self.analysis_result.endpoints
            }
        }