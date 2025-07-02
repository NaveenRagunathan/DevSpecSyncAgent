from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
# from dotenv import load_dotenv # No longer needed if API key is directly provided or set via os.environ
import os
import json # Import json for parsing

# load_dotenv() # No longer needed

# Set your OpenRouter API key here or as an environment variable
# It's generally better to load this from an environment variable for security in production.
# For development, setting it directly here for convenience as per your request.
os.environ["OPENROUTER_API_KEY"] = api_key # Ensure it's in env for ChatOpenAI to pick up if not directly passed

class ProjectSpecOutput(BaseModel):
    problemGoal: str = Field(description="Clear articulation of what the app solves.")
    mvpScope: str = Field(description="What the minimum viable version should include.")
    dbSchema: str = Field(description="PostgreSQL tables & relationships, including table names, columns with types, and relationships.")
    apiRoutes: str = Field(description="FastAPI endpoint blueprints, including HTTP method, path, and a brief description.")
    langchainDesign: str = Field(description="Purpose, prompt shape, inputs/outputs for the LangChain agent.")
    frontendPlan: str = Field(description="Pages, components, forms, and visualizations for the frontend.")
    integrationTargets: str | None = Field(description="Integration targets like Stripe, Notion, Survey, etc., if applicable.")
    devRoadmap: str = Field(description="Week-by-week implementation guide.")

# Initialize ChatOpenAI with OpenRouter and Mistral 7B model
llm = ChatOpenAI(
    model_name="mistralai/mistral-7b-instruct",  # Using Mistral 7B model
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=api_key, # Use the variable directly
    max_tokens=2000, # Increased max_tokens to allow for longer JSON output
    temperature=0.7
)

# Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the DevSpec Synth Agent, an AI product engineer. Your task is to convert a raw product idea into a detailed, structured technical execution specification. Ensure all outputs are aligned with the following stack: Frontend: React + Tailwind, Backend: FastAPI (Python), AI Layer: LangChain + OpenAI (GPT-4/4o), Database: PostgreSQL + Prisma, Infra: Vercel/Railway + GitHub CI.

Output the complete technical specification as a **strictly valid JSON object** that adheres to the following schema. **Ensure no trailing commas, all property names are enclosed in double quotes, and the JSON is valid and complete, with all fields present and NOT empty.**

Here is the JSON schema to follow:
{schema_json}

Here is an example of a valid JSON output:
```json
{{
  "problemGoal": "To help users track and manage their daily tasks efficiently.",
  "mvpScope": "A web application allowing users to register, log in, add new tasks, mark tasks as complete, and delete tasks.",
  "dbSchema": "Users (id, username, password_hash, email); Tasks (id, user_id, description, is_completed, created_at)",
  "apiRoutes": "POST /auth/register, POST /auth/login, POST /tasks, GET /tasks, PUT /tasks/{{id}}, DELETE /tasks/{{id}}",
  "langchainDesign": "Purpose: To generate task descriptions based on user's high-level goals. Prompt shape: 'Expand on the goal: {{goal}} to create specific tasks.' Inputs: goal. Outputs: task descriptions.",
  "frontendPlan": "Pages: Login, Register, Dashboard. Components: TaskInputForm, TaskList, TaskItem. Forms: LoginForm, RegisterForm. Visualizations: none.",
  "integrationTargets": null,
  "devRoadmap": "Week 1: Setup project, auth, user model. Week 2: Task model, API. Week 3: Frontend UI, integrate API. Week 4: Testing, deployment."
}}
```
"""),
    ("human", "Generate a comprehensive technical execution spec for the following idea: {idea}"),
])

# Create the LangChain agent (without structured output)
chain = prompt | llm # Renamed from langchain_agent to chain

async def generate_spec(idea: str) -> ProjectSpecOutput:
    """Generates a technical specification using the LangChain agent."""
    # Get the JSON schema string from our Pydantic model
    schema_json = json.dumps(ProjectSpecOutput.schema(), indent=2)
    
    # Extract content from AIMessage object
    ai_message_response = await chain.ainvoke({"idea": idea, "schema_json": schema_json})
    response_str = ai_message_response.content
    
    # Clean the response string to extract only the JSON part
    cleaned_json_str = response_str.strip()
    if cleaned_json_str.startswith('```json') and cleaned_json_str.endswith('```'):
        cleaned_json_str = cleaned_json_str[len('```json'):-len('```')].strip()
    elif cleaned_json_str.startswith('```') and cleaned_json_str.endswith('```'):
        # Handle cases where the language hint might be missing (e.g., just ```) 
        cleaned_json_str = cleaned_json_str[len('```'):-len('```')].strip()

    # Parse the JSON string response into our Pydantic model
    try:
        return ProjectSpecOutput.parse_raw(cleaned_json_str)
    except Exception as e:
        # Handle cases where the LLM might not return perfect JSON or extra text
        print(f"Error parsing LLM response: {e}")
        print(f"Raw LLM response (cleaned): {cleaned_json_str}")
        # Fallback if initial stripping fails and there's still extraneous text
        try:
            json_start = cleaned_json_str.find('{')
            json_end = cleaned_json_str.rfind('}') + 1
            if json_start != -1 and json_end != -1 and json_end > json_start:
                final_json_str = cleaned_json_str[json_start:json_end]
                return ProjectSpecOutput.parse_raw(final_json_str)
            else:
                raise ValueError("Could not extract valid JSON from LLM response after cleaning.")
        except Exception as inner_e:
            raise ValueError(f"Failed to parse and extract JSON from LLM response: {inner_e}. Original error: {e}") 