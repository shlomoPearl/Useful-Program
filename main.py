from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from bill import ReadBill
from gmail import Gmail
from gmail_auth import GmailAuth
from graph_plot import PatymentGraph

app = FastAPI()
templates = Jinja2Templates(directory="templates")


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
async def index_post(
        email: str = Form(...),
        subject: str = Form(None),
        keyword: str = Form(None),
        currency: str = Form(...),
        start_date: str = Form(...),
        end_date: str = Form(...)
):
    if not all([email, start_date, end_date, currency]):
        raise HTTPException(status_code=400, detail="Missing required form fields.")
    try:
        auth = GmailAuth()
        creds = auth.load_token()
        if not creds:
            return RedirectResponse("/auth/login", status_code=303)
        auth.initialize_service()
        service = auth.get_service()
        gmail_obj = Gmail(
            address=email,
            subject=subject,
            date_range=[start_date, end_date],
        )
        attachments = gmail_obj.search_mail(service)
        bill_obj = ReadBill(attachments, currency)
        bill_dict = bill_obj.parser(keyword)
        graph = PatymentGraph(bill_dict)
        graph.plot_graph()
        return {"status": "finished"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/login")
async def login():
    auth = GmailAuth()
    flow = auth.create_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
async def auth_callback(code: str, state: str = None):
    auth = GmailAuth()
    try:
        auth.exchange_code(code, state)
        return RedirectResponse("/", status_code=303)

    except Exception as e:
        return f"Error: {str(e)}"