from contextlib import asynccontextmanager
from fastapi import FastAPI
from prisma_client import Prisma
from app.langchain_agent import generate_spec, ProjectSpecOutput
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import HTTPException


# Pydantic model for request body
class IdeaInput(BaseModel):
    idea: str

db = Prisma()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello DevSpec Synth Agent!"}


@app.post("/generate-spec")
async def generate_technical_spec(input_data: IdeaInput):
    """Generates a comprehensive technical execution spec from a product idea."""
    try:
    # Access the idea from the input_data object
    idea = input_data.idea

    # Generate the spec using the LangChain agent
    spec_output = await generate_spec(idea)

    # Save the generated spec to the database
    saved_spec = await db.projectspec.create(
        data={
            "problemGoal": spec_output.problemGoal,
            "mvpScope": spec_output.mvpScope,
            "dbSchema": spec_output.dbSchema,
            "apiRoutes": spec_output.apiRoutes,
            "langchainDesign": spec_output.langchainDesign,
            "frontendPlan": spec_output.frontendPlan,
            "integrationTargets": spec_output.integrationTargets,
            "devRoadmap": spec_output.devRoadmap,
        }
    )

        # Convert datetime objects to strings for JSON serialization
        saved_spec_dict = saved_spec.dict()
        saved_spec_dict["createdAt"] = saved_spec_dict["createdAt"].isoformat() if saved_spec_dict["createdAt"] else None
        saved_spec_dict["updatedAt"] = saved_spec_dict["updatedAt"].isoformat() if saved_spec_dict["updatedAt"] else None

        return JSONResponse(content=saved_spec_dict)
    except Exception as e:
        import traceback
        print("Error in /generate-spec:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
