from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from pydantic_settings import BaseSettings
from dotenv import load_dotenv # No longer needed if API key is directly provided or set via os.environ
import os
import json # Import json for parsing

load_dotenv() # No longer needed

# Define Settings class for environment variables
class Settings(BaseSettings):
    openrouter_api_key: str
    database_url: str | None = None # Add database_url as an optional field

    class Config:
        env_file = ".env"

settings = Settings() # Instantiate settings

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
    model_name="openai/gpt-4.1-nano",  # Changed model to Google: Gemini 2.5 Pro
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=settings.openrouter_api_key, # Use the variable directly
    max_tokens=4096, # Increased max_tokens to allow for longer JSON output
    temperature=0.7
).with_structured_output(ProjectSpecOutput) # Apply structured output directly to the LLM

# Define the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are the DevSpec Synth Agent, an elite AI technical product architect.

Your role is to transform product ideas into strategic, technically thoughtful execution blueprints — not just boilerplate.

You are expected to:
- Ask yourself: what are the user goals? What's the domain context?
- Propose *smart defaults* based on best practices, not just basic CRUD patterns.
- Make opinionated design choices — tech stack, LangChain agent roles, API shapes, integrations.
- If AI is involved, define *how* it augments the workflow with clear user and system flows.
- The output must reflect deep architectural thinking and real-world product design awareness.

Stack: React + Tailwind, FastAPI, LangChain + OpenAI, PostgreSQL + Prisma, Vercel/Railway.

Return ONLY a valid JSON object adhering to the following schema...


Output the complete technical specification as a **strictly valid JSON object** that adheres to the following schema. **Ensure no trailing commas, all property names are enclosed in double quotes, and the JSON is valid and complete, with all fields present and NOT empty.**

Do NOT include any markdown syntax like ```json or explanations. ONLY return a valid JSON object. No commentary or prefaces.
Double-check that all keys in the JSON object are present and correctly named, and values are non-empty (use null if needed).

Here is the JSON schema to follow:
{schema_json}

Here are some examples of valid JSON outputs:
{{
  "problemGoal": "To help users track and manage their daily tasks efficiently.",
  "mvpScope": "A web application allowing users to register, log in, add new tasks, mark tasks as complete, and delete tasks.",
  "dbSchema": "Users (id, username, password_hash, email); Tasks (id, user_id, description, is_completed, created_at)",
  "apiRoutes": "POST /auth/register, POST /auth/login, POST /tasks, GET /tasks, PUT /tasks/{{id}}, DELETE /tasks/{{id}}",
  "langchainDesign": "Purpose: To generate task descriptions based on user's high-level goals. Prompt shape: 'Expand on the goal: {{goal}} to create specific tasks.' Inputs: goal. Outputs: task descriptions.",
  "frontendPlan": "Pages: Login, Register, Dashboard. Components: TaskInputForm, TaskList, TaskItem. Forms: LoginForm, RegisterForm. Visualizations: none.",
  "integrationTargets": null,
  "devRoadmap": "Week 1: Setup project, auth, user model. Week 2: Task model, API. Week 3: Frontend UI, integrate API. Week 4: Testing, deployment."
}},
{{
  "problemGoal": "To enable users to manage project tasks and track payments seamlessly.",
  "mvpScope": "A web application with user authentication, task creation, project management features, and Stripe integration for payment processing, plus Notion integration for documentation.",
  "dbSchema": "Users (id, username, email, password_hash); Projects (id, user_id, name, description); Tasks (id, project_id, description, status, due_date); Payments (id, user_id, amount, date, status, stripe_charge_id)",
  "apiRoutes": "POST /auth/register, POST /auth/login, POST /projects, GET /projects, POST /projects/{{id}}/tasks, GET /projects/{{id}}/tasks, POST /payments/stripe_webhook, GET /payments",
  "langchainDesign": "Purpose: To assist users in generating project descriptions from high-level goals. Prompt shape: 'Elaborate on the project goal: {{goal}} to create a detailed project description.' Inputs: goal. Outputs: detailed project description.",
  "frontendPlan": "Pages: Login, Register, Project Dashboard, Task List, Payment History. Components: ProjectForm, TaskForm, PaymentStatus. Forms: LoginForm, RegisterForm, ProjectForm. Visualizations: Task status charts.",
  "integrationTargets": "Stripe, Notion",
  "devRoadmap": "Week 1: Setup project, auth, user/project models. Week 2: Task model, Stripe integration (webhook). Week 3: Notion API integration for documentation, API routes for projects/tasks/payments. Week 4: Frontend UI for project/task management, payment history, testing, deployment."
}},
{{
  "problemGoal": "To provide a simple way for users to store and retrieve personal notes.",
  "mvpScope": "A web application allowing users to register, log in, create, view, edit, and delete text-based notes. No advanced AI features beyond basic text processing.",
  "dbSchema": "Users (id, username, password_hash, email); Notes (id, user_id, title, content, created_at, updated_at)",
  "apiRoutes": "POST /auth/register, POST /auth/login, POST /notes, GET /notes, GET /notes/{{id}}, PUT /notes/{{id}}, DELETE /notes/{{id}}",
  "langchainDesign": "Purpose: None. The application does not leverage LangChain for complex AI functionalities beyond simple note storage and retrieval.",
  "frontendPlan": "Pages: Login, Register, Notes List, Create Note, Edit Note. Components: NoteCard, NoteForm. Forms: LoginForm, RegisterForm, NoteForm. Visualizations: none.",
  "integrationTargets": null,
  "devRoadmap": "Week 1: Setup project, auth, user model. Week 2: Note model, API. Week 3: Frontend UI, integrate API. Week 4: Testing, deployment."
}},
{{
  "problemGoal": "To expose an API for managing a product catalog.",
  "mvpScope": "A backend service providing API endpoints for CRUD operations on products (add, view, update, delete). No frontend component is required for the MVP.",
  "dbSchema": "Products (id, name, description, price, stock, created_at, updated_at)",
  "apiRoutes": "POST /products, GET /products, GET /products/{{id}}, PUT /products/{{id}}, DELETE /products/{{id}}",
  "langchainDesign": "Purpose: None. This is a backend-only service without an AI layer.",
  "frontendPlan": "Not applicable for MVP. This is a backend-only service.",
  "integrationTargets": null,
  "devRoadmap": "Week 1: Setup project, product model, database. Week 2: Implement CRUD API endpoints. Week 3: Add basic authentication/authorization, testing. Week 4: Deployment setup."
}}
"""),
    ("human", "Generate a comprehensive technical execution spec for the following idea: {idea}"),
])

# Create the LangChain agent (without fallbacks as requested)
chain = prompt | llm

async def generate_spec(idea: str) -> ProjectSpecOutput:
    """Generates a technical specification using the LangChain agent."""
    # Get the JSON schema string from our Pydantic model
    # This part of the prompt is still useful for guiding the LLM, even if structured_output is used
    schema_json = ProjectSpecOutput.schema_json(indent=2)
    
    # The chain now directly returns ProjectSpecOutput due to with_structured_output
    return await chain.ainvoke({"idea": idea, "schema_json": schema_json}) 