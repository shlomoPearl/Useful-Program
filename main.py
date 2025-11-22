from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
from bill import ReadBill
from gmail import Gmail
from gmail_auth import GmailAuth
from graph_plot import PatymentGraph

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, os.getenv("KEY"))


class FormData(BaseModel):
    email: str
    subject: str | None = None
    keyword: str | None = None
    currency: str
    start_date: str
    end_date: str


@app.get("/", response_class=HTMLResponse)
async def index_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
async def handle_form(request: Request,
                      email: str = Form(...),
                      subject: str = Form(None),
                      keyword: str = Form(None),
                      currency: str = Form(...),
                      start_date: str = Form(...),
                      end_date: str = Form(...)):
    if not all([email, start_date, end_date, currency]):
        raise HTTPException(status_code=400, detail="Missing required form fields.")
    try:
        auth = GmailAuth()
        creds = auth.load_token()
        if not creds:
            request.session["data_form"] = {
                "email": email,
                "subject": subject,
                "keyword": keyword,
                "currency": currency,
                "start_date": start_date,
                "end_date": end_date,
            }
            return RedirectResponse("/auth/login", status_code=303)
        return await process_flow(auth, {
            "email": email,
            "subject": subject,
            "keyword": keyword,
            "currency": currency,
            "start_date": start_date,
            "end_date": end_date,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/login")
async def login_redirect(request: Request):
    auth = GmailAuth()
    flow = auth.create_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    request.session["oauth_state"] = state
    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
async def auth_callback(request: Request, code: str, state: str = None):
    saved_state = request.session.get("oauth_state")
    if not saved_state or saved_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state.")
    auth = GmailAuth()
    try:
        auth.exchange_code(code, state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth Error: {str(e)}")
    form_data = request.session.pop("data_form", None)
    if not form_data:
        raise HTTPException(status_code=400, detail="Unauthorized callback.")
    return await process_flow(auth, form_data)


async def process_flow(auth: GmailAuth, data: dict):
    try:
        # auth.initialize_service()
        service = auth.get_service()
        gmail_client = Gmail(
            address=data["email"],
            subject=data.get("subject"),
            date_range=[data["start_date"], data["end_date"]],
        )
        attachments = gmail_client.search_mail(service)
        bill_reader = ReadBill(attachments, data["currency"])
        bill_dict = bill_reader.parser(data.get("keyword"))
        graph = PatymentGraph(bill_dict)
        graph.plot_graph()
        return {"status": "finished"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
