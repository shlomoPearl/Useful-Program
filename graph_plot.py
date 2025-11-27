import plotly.graph_objs as go
import plotly.io as pio


def get_html_graph(bill_dict):
    dates = list(bill_dict.keys())
    values = list(bill_dict.values())

    fig = go.Figure(data=[go.Bar(x=dates, y=values, text=values, textposition='auto')])
    fig.update_layout(
        title="Payment Over Time",
        xaxis_title="Date",
        yaxis_title="Amount Paid",
        template="plotly_white"
    )
    return fig.to_html(config={"displayModeBar": False})
