import os
import re
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.services.research import search_company
from app.services.summary import summarize_company
from app.services.pdf_generator import generate_pdf

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Company Research Agent")

app = FastAPI(
    title=APP_NAME,
    description="An AI-powered company research and PDF brief generator.",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

templates = Jinja2Templates(directory="app/templates")


class ResearchRequest(BaseModel):
    company_name: str


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": APP_NAME}
    )


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/research")
def research_company_endpoint(request: ResearchRequest):

    company_name = request.company_name.strip()

    # Check invalid input before web searching.
    if not company_name:
        raise HTTPException(
            status_code=400,
            detail="Please enter a company name."
        )

    if not re.search(r"[a-zA-Z]", company_name):
        raise HTTPException(
            status_code=400,
            detail="Invalid company name. Please enter a valid name."
        )

    if len(re.sub(r"[^a-zA-Z0-9]", "", company_name)) < 3:
        raise HTTPException(
            status_code=400,
            detail="Company name is too short. Enter at least 3 characters."
        )

    try:
        # Step 1: Search and validate the company.
        results = search_company(company_name)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No relevant results found for '{company_name}'."
            )

        # Step 2: Generate the AI summary.
        summary = summarize_company(company_name, results)

        if not summary or not summary.strip():
            raise ValueError("The AI could not generate a summary.")

        # Step 3: Generate the PDF.
        pdf_path = generate_pdf(
            company_name,
            summary,
            results
        )

        if not os.path.isfile(pdf_path):
            raise FileNotFoundError("PDF generation failed.")

        # Step 4: Return the PDF.
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(pdf_path)
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:
        print("RESEARCH ERROR:", str(exc))
        traceback.print_exc()

        raise HTTPException(
            status_code=502,
            detail="Research generation failed. Please try again."
        )
