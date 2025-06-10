from agent import InputInterpreterAgent
import json


def main():
    # Initialize the agent
    agent = InputInterpreterAgent()

    # Process Swagger URL
    swagger_url = "https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json"

    try:
        # Get detailed analysis
        analysis = agent.process_swagger_url(swagger_url)

        # Get summary for next agent
        summary = agent.get_endpoint_summary()

        # Print results
        print("\n" + "=" * 50)
        print("ENDPOINT SUMMARY")
        print("=" * 50)
        print(json.dumps(summary, indent=2))

        # Get detailed export
        detailed_export = agent.export_detailed_analysis()

        print(f"\n📊 Analysis Complete:")
        print(f"   • API: {analysis.title} v{analysis.version}")
        print(f"   • Base URL: {analysis.base_url}")
        print(f"   • Endpoints: {len(analysis.endpoints)}")
        print(f"   • Authentication: {len(analysis.global_security)} methods")

        # Show sample endpoint details
        if analysis.endpoints:
            sample_endpoint = analysis.endpoints[0]
            print(f"\n🔍 Sample Endpoint Details:")
            print(f"   • Path: {sample_endpoint.path}")
            print(f"   • Method: {sample_endpoint.method.value}")
            print(f"   • Required Headers: {sample_endpoint.headers_required}")
            print(f"   • Response Assertions: {sample_endpoint.response_assertions}")
            print(f"   • Expected Codes: {sample_endpoint.expected_response_codes}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()