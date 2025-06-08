from flask import Flask, request, render_template, send_file
import tempfile
import os
from gmail import Gmail
from bill import ReadBill
from graph_plot import PatymentGraph
import io
import matplotlib.pyplot as plt

app = Flask(__name__)


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
            gmail_obj = Gmail(
                address=email_address,
                subject=subject,
                date_range=[start_date, end_date],
            )
            # gmail_obj.credentials = credentials_path
            creds = gmail_obj.authenticate()
            attachments = gmail_obj.search_mail(creds)

            bill_obj = ReadBill(attachments, currency)
            bill_dict = bill_obj.parser(keyword)
            graph = PatymentGraph(bill_dict)
            # plt.figure(figsize=(10, 6))
            graph.plot_graph()
            # img_bytes = io.BytesIO()
            # plt.savefig(img_bytes, format='png')
            # img_bytes.seek(0)
            # plt.close()
            print("FINISH")

        except Exception as e:
            return f"Error: {str(e)}", 500

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5050)
