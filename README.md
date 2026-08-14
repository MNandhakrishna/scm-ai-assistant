# SCM AI Assistant

An AI-powered Supply Chain Management assistant that allows users to interact with supply-chain data using natural language and voice.

The application combines deterministic Python-based SCM calculations with a LangGraph agent and Groq LLM to answer questions about inventory, demand, and restocking.

---

## Overview

Supply Chain Management involves coordinating inventory, demand, suppliers, warehouses, and replenishment decisions.

This project provides an AI assistant that can answer questions such as:

- Which products are currently low in stock?
- Which products actually need restocking?
- Which warehouse has the highest stock-gap risk?
- Which products have the highest demand forecast?
- What is the demand history for a particular SKU?

The system supports both text and voice-based interaction through a Streamlit interface.

---

## Business Problem

Supply-chain teams frequently need to inspect inventory and demand data to identify:

- Products below their reorder points
- Products that actually require replenishment
- Warehouses with significant inventory gaps
- Products with high demand forecasts
- Historical demand patterns

Traditional data analysis requires users to write SQL queries or manually inspect reports.

This project provides a natural-language interface over deterministic SCM tools so users can ask business questions without directly querying the underlying data.

---

## Solution

The application separates AI reasoning from business calculations.

The LLM is responsible for:

- Understanding the user's question
- Selecting the appropriate SCM tool
- Interpreting structured tool results
- Generating a natural-language response

The Python tools are responsible for:

- Reading SCM data
- Filtering inventory
- Calculating stock gaps
- Calculating replenishment requirements
- Returning demand statistics
- Generating restocking recommendations

This prevents the LLM from inventing business values or performing critical inventory calculations itself.

---

## Architecture

```text
                         ┌───────────────────────┐
                         │     Streamlit UI      │
                         │    Text + Voice       │
                         └───────────┬───────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      │                             │
                Text Question                 Audio Input
                      │                             │
                      │                       Groq Whisper
                      │                             │
                      └──────────────┬──────────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   SCM AI Assistant    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       LangGraph       │
                         │   Agent + Tool Calls  │
                         └───────────┬───────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
              Inventory          Demand           Restock
                Tools             Tools             Tools
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │   DuckDB    │
                              │ SCM Dataset │
                              └─────────────┘

                              Groq LLM
                                  │
                                  ▼
                           Final AI Response
````

---

## Key Features

### 1. Inventory Analysis

Identifies products whose inventory level is below their reorder point.

Business rule:

```text
Inventory_Level < Reorder_Point
```

The system reports:

* SKU
* Warehouse
* Supplier
* Inventory level
* Reorder point
* Stock gap

---

### 2. Demand Analysis

Provides:

* Product demand history
* Units sold
* Demand forecast
* Highest-demand products
* Warehouse-level demand summaries

---

### 3. Restocking Recommendations

Identifies products that actually require replenishment.

A product is considered to require restocking when:

```text
Recommended_Order_Quantity > 0
```

The system calculates and reports:

* Current inventory
* Demand forecast
* Supplier lead time
* Lead-time demand
* Safety stock
* Required inventory
* Recommended order quantity

Example:

```text
SKU_27
Current Inventory:       315
Required Inventory:      496
Recommended Order:       181
```

---

### 4. Warehouse Inventory Risk

The project currently uses **total stock gap** as the primary indicator of inventory risk.

```text
Stock Gap = Reorder Point - Inventory Level
```

The system does not currently calculate a formal composite inventory-risk score.

Therefore, the assistant distinguishes between:

* Stock-gap risk
* Demand forecast
* Average inventory

These metrics are not treated as interchangeable.

---

### 5. Natural Language AI Assistant

Users can ask questions using natural language.

Examples:

```text
Which products are currently low in stock?

Which products actually need restocking?

Which warehouse has the highest inventory risk?

Which products have the highest demand forecast?

What is the demand history for SKU_2?
```

---

### 6. Voice Assistant

The application supports voice-based SCM queries.

Workflow:

```text
Audio File
    ↓
Groq Whisper
    ↓
Speech-to-Text
    ↓
LangGraph
    ↓
SCM Tool
    ↓
Groq LLM
    ↓
SCM Response
```

Supported audio formats in the Streamlit application:

* `.m4a`
* `.wav`
* `.mp3`

---

### 7. Conversation Summary

The chatbot can generate a summary of the visible conversation, including:

* Key issues
* Inventory risks
* Restocking actions
* Demand insights

Internal tool calls are not treated as user conversation history.

---

### 8. Error Handling

The application includes controlled handling for:

* Missing API keys
* Missing audio files
* Audio transcription failures
* Groq API failures
* Oversized Groq requests
* SCM tool execution failures

Technical details are logged while users receive a controlled error message.

---

## Technology Stack

| Technology             | Purpose                               |
| ---------------------- | ------------------------------------- |
| Python                 | Application and SCM logic             |
| Pandas                 | Data processing                       |
| DuckDB                 | Local analytical database             |
| Groq                   | LLM and speech-to-text                |
| Llama 3.1 8B Instant   | SCM reasoning                         |
| Whisper Large V3 Turbo | Speech-to-text                        |
| LangGraph              | Agent workflow and tool orchestration |
| LangChain Core         | Message and agent abstractions        |
| Streamlit              | Web interface                         |
| Pytest                 | Automated testing                     |
| python-dotenv          | Environment variable management       |

---

## Project Structure

```text
scm_ai_assistant/
│
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   ├── supply_chain_dataset.csv
│   └── test_audio.m4a
│
├── tests/
│   ├── __init__.py
│   ├── test_inventory_tools.py
│   ├── test_demand_tools.py
│   ├── test_restock_tools.py
│   └── test_graph.py
│
└── src/
    │
    ├── agents/
    │   ├── graph.py
    │   ├── groq_test.py
    │   ├── groq_tools.py
    │   ├── scm_agent.py
    │   └── tool_definitions.py
    │
    ├── chatbot/
    │   ├── chat_assistant.py
    │   └── voice_assistant.py
    │
    ├── data/
    │   └── database.py
    │
    ├── speech/
    │   └── speech_to_text.py
    │
    ├── summarization/
    │   └── summarizer.py
    │
    ├── tools/
    │   ├── inventory_tools.py
    │   ├── demand_tools.py
    │   └── restock_tools.py
    │
    └── utils/
        └── logger.py
```

---

## Environment Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd scm_ai_assistant
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Then add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The `.env` file must not be committed to Git.

---

## Running the Application

Start the Streamlit application:

```powershell
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

---

## Running Individual Components

### Inventory tools

```powershell
python -m src.tools.inventory_tools
```

### Demand tools

```powershell
python -m src.tools.demand_tools
```

### Restocking tools

```powershell
python -m src.tools.restock_tools
```

### LangGraph SCM agent

```powershell
python -m src.agents.graph
```

### Text chatbot

```powershell
python -m src.chatbot.chat_assistant
```

### Voice assistant

```powershell
python -m src.chatbot.voice_assistant
```

---

## Testing

The project uses Pytest for automated testing.

Run the complete test suite:

```powershell
pytest -v
```

Current tests cover:

### Inventory

* Low-stock rule
* Result limits

### Demand

* SKU filtering
* Warehouse filtering
* Result limits
* Demand forecast ordering
* Demand summary

### Restocking

* Positive recommended order quantities
* Required inventory validation
* Recommended order quantity calculation

### LangGraph Integration

* Inventory questions
* Restocking questions
* Warehouse risk questions
* Tool selection and execution flow

---

## Example Output

Example restocking analysis:

```text
SKU_27
Warehouse: WH_4

Inventory Level: 315
Demand Forecast: 31
Supplier Lead Time: 14 days
Lead Time Demand: 434
Safety Stock: 62
Required Inventory: 496
Recommended Order Quantity: 181
```

The recommendation is calculated by the application rather than generated by the LLM.

---

## Design Principles

### Deterministic Business Logic

Inventory and replenishment calculations are implemented in Python tools.

The LLM does not determine:

* Inventory levels
* Reorder points
* Stock gaps
* Lead-time demand
* Safety stock
* Recommended order quantities

These values come from the SCM tools.

### Tool-Based AI

The LangGraph agent selects the appropriate tool based on the user's question.

```text
User Question
      ↓
LLM
      ↓
Tool Selection
      ↓
Python SCM Tool
      ↓
Structured Data
      ↓
LLM
      ↓
Natural Language Response
```

### Separation of Concepts

The application explicitly distinguishes:

```text
Low Stock
    ≠
Restocking Required
```

A product being below its reorder point does not automatically mean that the restocking calculation recommends an order.

---

## Current Limitations

* The application currently works with a local supply-chain dataset.
* The inventory-risk calculation is based on stock gap rather than a formal composite risk score.
* Voice input currently processes uploaded audio files.
* The application does not create or submit purchase orders.
* Supplier communication is not automated.
* The application does not currently use real-time streaming inventory data.
* The project is intended as an AI-assisted analytics application rather than a production procurement system.

---

## Future Enhancements

Potential future improvements include:

* Real-time inventory ingestion
* Production database integration
* Advanced inventory-risk scoring
* Supplier performance analysis
* Purchase-order generation
* Supplier lead-time monitoring
* Inventory anomaly detection
* Demand forecasting models
* Authentication and role-based access
* Cloud deployment
* Monitoring and observability
* Automated alerts for critical stock conditions

---

## Project Goal

The goal of this project is to demonstrate how traditional data engineering and supply-chain analytics can be combined with modern LLM-based agent architectures.

The system keeps critical business calculations deterministic while using AI to make supply-chain data accessible through natural-language and voice interfaces.

````