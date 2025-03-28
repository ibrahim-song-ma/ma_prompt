# Agent Prompt Validation System

This system implements a multi-agent validation framework using DeepSeek as the base model. It includes:

1. Configurable LLM setup
2. Multi-agent communication stimulation
3. Role-specific agents:
   - Supervisor Agent (Project Manager)
   - Metadata Engineer Agent (Data Governance Engineer)
   - Data Calibration Agent (Data Calibrator)
   - Data Development Agent (Data Engineer)

## Setup

```bash
pip install -r requirements.txt
```

## Configuration

Create a `config.py` file with:

```
DEEPSEEK_API_KEY=your_api_key_here
```