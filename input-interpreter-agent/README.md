

# JMeter Agentic Framework

An AIpowered system for automated JMeter performance test script generation from Swagger/OpenAPI specifications.

## Project Structure

- \`input-interpreter-agent/\` - First agent: Parses Swagger specs and extracts endpoint details
- (More agents to be added)

## Current Status

✅ Input Interpreter Agent - Complete
🔄 Data Mapping Agent - In Progress
⏳ Script Builder Agent - Planned
⏳ Validator Agent - Planned

## Quick Start


cd input-interpreter-agent
python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt
python example_usage.py


## Testing


python -m pytest tests/ -v
