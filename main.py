import os
from flask import Flask, render_template, request, send_file
from io import BytesIO
from gmail import Gmail
from bill import ReadBill
from graph_plot import PatymentGraph

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        email = request.form["email"]
        subject = request.form["subject"]
        keyword = request.form["keyword"]
        currency = request.form["currency"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        # Path to your pre-uploaded credentials
        cred_path = "credentials.json"
        token_path = "token.json"

        # Gmail logic
        gmail_client = Gmail(
            address=email,
            subject=subject,
            key_word=keyword,
            result_num=36,
            date_range=[start_date, end_date]
        )
        gmail_client.credentials_file = cred_path
        gmail_client.token_file = token_path

        creds = gmail_client.authenticate()
        mail_data = gmail_client.search_mail(creds)

        if not mail_data:
            return "No matching emails found."

        bill_parser = ReadBill(mail_data)
        bill_dict = bill_parser.parser(currency)

        # Plot graph and send back as image
        graph = PatymentGraph(bill_dict, f"{start_date} to {end_date} - {currency}")
        image_io = BytesIO()
        graph.save_graph(image_io)
        image_io.seek(0)
        return send_file(image_io, mimetype='image/png', download_name='graph.png')

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
