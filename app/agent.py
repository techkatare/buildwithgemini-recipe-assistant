# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from app.a2ui_utils import a2ui_callback

from app.tools import (
    add_pantry_item,
    add_recipe,
    fetch_online_recipes,
    generate_dish_image,
    generate_recipe_video,
    list_pantry_items,
    search_recipes,
)

# Load Agent Engine resource name from deployment_metadata.json
agent_engine_resource_name = None
metadata_path = Path(__file__).resolve().parent.parent / "deployment_metadata.json"
if metadata_path.exists():
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            agent_engine_resource_name = metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

# Created active sandbox environment under Agent Engine
sandbox_resource_name = (
    "projects/333301554637/locations/us-east1/reasoningEngines/4695277489440686080/sandboxEnvironments/714330714333511680"
)

code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=sandbox_resource_name,
    agent_engine_resource_name=agent_engine_resource_name,
)

# Initialize Memory Bank service for Agent Engine deployment
memory_service = VertexAiMemoryBankService(
    project="qwiklabs-gcp-01-e1fa088249da",
    location="us-east1",
    agent_engine_id="4695277489440686080",
)

async def auto_save_memory_callback(callback_context: CallbackContext):
    """Save session conversation events to Memory Bank after each turn."""
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None

# Build A2UI v0.8 system prompt using A2uiSchemaManager and BasicCatalog
catalog_config = BasicCatalog().get_config("0.8")
a2ui_manager = A2uiSchemaManager(version="0.8", catalogs=[catalog_config])
base_role_description = (
    "You are the Smart Recipe & Pantry Assistant. You help home cooks manage their "
    "pantry inventory and discover recipes based on available ingredients and dietary preferences. "
    "Use your function tools to view or update pantry items, search local or online recipes, "
    "add new recipes, generate dish photography visuals, and generate short recipe video demonstrations when requested. "
    "Use your memory to remember user dietary preferences and past conversation details across sessions. "
    "You can also run Python code calculations and data analysis safely using your Agent Engine code execution sandbox."
)
system_instruction = a2ui_manager.generate_system_prompt(role_description=base_role_description)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=system_instruction,
    tools=[
        list_pantry_items,
        add_pantry_item,
        search_recipes,
        add_recipe,
        generate_dish_image,
        generate_recipe_video,
        fetch_online_recipes,
        PreloadMemoryTool(),
    ],
    after_agent_callback=auto_save_memory_callback,
    after_model_callback=a2ui_callback,
    code_executor=code_executor,
)

app = App(
    root_agent=root_agent,
    name="app",
)

