
## RAG with Milvus and Groq

This project builds is focused to build a RAG application with **retrieval latency < 15ms**. 

It leverages binary quantization for efficient retrieval coupled with Groq's blazing fast inference speeds.

We use:

- LlamaIndex for orchestrating the RAG app.
- Milvus vectorDB for binary vector indexing and storage.
- Groq as the inference engine for MoonshotAI's Kimi K2.

## Setup and Installation

Ensure you have Python 3.11 or later installed on your system.

First, let’s install uv and set up our Python project and environment:
```bash
# MacOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Install dependencies**:

```bash
# Create a new directory for our project
uv init fastest-rag
cd fastest-rag

# Create virtual environment and activate it
uv venv
source .venv/bin/activate  # MacOS/Linux

.venv\Scripts\activate     # Windows

# Install dependencies
uv add pymilvus llama-index llama-index-embeddings-huggingface llama-index-llms-groq streamlit beam-client
```

**Setup Groq**:

Get an API key from [Groq](https://console.groq.com/) and set it in the `.env` file as follows:

```bash
GROQ_API_KEY=<YOUR_GROQ_API_KEY> 
```

**Run the app**:

  you can also run the app by running the following command:

   ```bash
   streamlit run app.py
   ```



