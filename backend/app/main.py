from typing import Dict

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.services import index_services, conversation_services
from app.core.entities import common
from app.config.settings import DEBUG

app = FastAPI(
    title="Avatar",
    docs_url="/",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1
    },  # Hides Schemas Menu in DocsF
    debug=DEBUG,
)

# Variables
origins = ["*"]

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check
@app.get("/health", status_code=200, include_in_schema=False)
def health_check() -> Dict[str, str]:
    """This is the health check endpoint"""
    return {"status": "ok"}


@app.post(
    "/index-website",
    status_code=status.HTTP_201_CREATED,
    summary="Scrape company website and index it in MongoDB Vector DB",
)
async def index_website(
    input: common.IndexWebsiteInput,
) -> None:
    index_services.scrape_and_index_website(
        company_name=input.company_name, urls=input.urls
    )


@app.post(
    "/get-answer",
    summary="Get answer",
)
async def get_answer(
    input: common.GetAnswerInput,
) -> common.GetAnswerOutput:
    response = conversation_services.get_answer_with_retrieval(
        company_name=input.company_name, query=input.query
    )
    return common.GetAnswerOutput(response=response)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=DEBUG, access_log=False)
