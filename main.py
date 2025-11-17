import os
from flask import Flask, request, render_template
from bill import ReadBill
from gmail import Gmail
from gmail_auth import GmailAuth
from graph_plot import PatymentGraph

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}'
SQLALCHEMY_TRACK_MODIFICATIONS = False


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email_address = request.form.get("email")
        subject = request.form.get("subject")
        keyword = request.form.get("keyword")
        currency = request.form.get("currency")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if not all([email_address, start_date, end_date, currency]):
            return "Missing required form fields.", 400

        try:
            auth = GmailAuth()
            service = auth.get_service()
            gmail_obj = Gmail(
                address=email_address,
                subject=subject,
                date_range=[start_date, end_date],
            )
            attachments = gmail_obj.search_mail(service)
            bill_obj = ReadBill(attachments, currency)
            bill_dict = bill_obj.parser(keyword)
            graph = PatymentGraph(bill_dict)
            graph.plot_graph()
            print("FINISH")

        except Exception as e:
            return f"Error: {str(e)}", 500

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5050)
