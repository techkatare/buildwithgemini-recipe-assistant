# 🍳 Smart Recipe & Pantry Assistant

A conversational AI agent built with Google's Agent Development Kit (ADK) that helps home cooks discover custom recipes based on available pantry ingredients, manage household pantry inventory, calculate nutritional macros, generate dish photography and cooking videos, and render rich interactive UI components.

![Smart Recipe Assistant Demo](demo.gif)

---

## 🌟 Implemented Features & Architecture

### 🧠 Persistent Cross-Session Memory
- **Vertex AI Memory Bank**: Integrates `VertexAiMemoryBankService` on Reasoning Engine to automatically remember user dietary restrictions (e.g. vegan, gluten-free, nut allergies), spice preferences, and past pantry updates across sessions.
- **Preload Memory Tool**: Uses `PreloadMemoryTool` to inject relevant memory context into turns.

### 🗄️ Database Integration (Google Cloud Firestore)
- **`list_pantry_items`**: Retrieves all items currently stored in the household pantry collection.
- **`add_pantry_item`**: Adds or updates pantry inventory items with quantity, category, and optional expiration dates.
- **`search_recipes`**: Searches stored recipes filtered by ingredient keywords or dietary tags.
- **`add_recipe`**: Adds new custom recipes to the Firestore database.

### 🖼️ Generative Media Tools (Google Cloud Storage)
- **`generate_dish_image`**: Generates high-quality dish photography using `gemini-3.1-flash-lite-image` in the global region.
- **`generate_recipe_video`**: Generates short cinematic cooking demonstration videos using `gemini-omni-flash-preview` in the global region.
- **Artifact & Cloud Storage Integration**: Generated media is saved as ADK artifacts (visible in the ADK Playground) and stored in a public Google Cloud Storage bucket (`smart-recipe-media-...`).

### 🌐 Public API Tools
- **`fetch_online_recipes`**: Connects to TheMealDB public REST API to query real-world recipe ideas with ingredients, instructions, and thumbnails.

### ⚡ Code Execution & Data Analysis
- **Agent Engine Sandbox Code Executor**: Runs Python code safely within an isolated sandbox environment (`AgentEngineSandboxCodeExecutor`) for unit scaling, calorie counts, and macro calculations.

### 🎨 Agent-to-User Interface (A2UI v0.8)
- **A2UI Basic Catalog**: Uses `A2uiSchemaManager` (version 0.8) and `a2ui_callback` to build structured UI components (Cards, Columns, Rows, Text, Dividers, Images, and Icons) rendered seamlessly in the chat interface.

---

## 🚀 Setup & Local Execution

### Prerequisites
- Python 3.10+
- Google Cloud SDK (`gcloud`)
- `uv` package manager installed

### Installation

1. **Clone the repository and navigate to the project directory**:
   ```bash
   cd smart-recipe-assistant
   ```

2. **Install project dependencies**:
   ```bash
   uv sync
   ```

3. **Start the local ADK Agent Playground**:
   ```bash
   uv run adk web . --port 8080 --reload_agents
   ```
   *(Optionally append `--memory_service_uri=agentengine://<AGENT_ENGINE_ID>` when connecting to a remote Memory Bank instance).*

### Running the Frontend Proxy Locally

1. **Navigate to the `frontend/` directory**:
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set required environment variables**:
   ```bash
   export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<REGION>/reasoningEngines/<ENGINE_ID>"
   export AGENT_DIRECTORY="app"
   ```

4. **Start the FastAPI proxy server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

---

## 🛠️ Project Structure

```
.
├── app/
│   ├── agent.py              # Root agent definition, system prompt, callbacks & code executor
│   ├── tools.py              # Firestore, Cloud Storage, Imagen, Omni video, & REST API tools
│   ├── a2ui_utils.py         # A2UI v0.8 schema manager & model callback
│   └── app_utils/            # Agent application helpers
├── frontend/
│   ├── main.py               # FastAPI proxy forwarding chat requests via a2a-sdk
│   ├── Procfile              # Cloud Run entrypoint configuration
│   ├── requirements.txt      # Frontend proxy python requirements
│   └── static/
│       └── index.html        # Rebranded chat UI with example prompt pills
├── agents-cli-manifest.yaml  # Deployment manifest
├── deployment_metadata.json  # Reasoning Engine runtime metadata
├── demo.gif                  # Animated demo recording
└── README.md
```
