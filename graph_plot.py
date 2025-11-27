import plotly.graph_objs as go
import plotly.io as pio

config = {"displayModeBar": False, "staticPlot": True}


class GraphPlot:
    def __init__(self, bill_dict, title="Payment Graph"):
        self.config = config
        self.dates = list(bill_dict.keys())
        self.values = list(bill_dict.values())
        self.title = title

    def get_html_graph(self):
        dates = self.dates
        values = self.values
        fig = go.Figure(data=[go.Bar(x=dates, y=values, text=values, textposition='outside')])
        fig.update_layout(
            title=self.title,
            xaxis_title="Date",
            yaxis_title="Amount",
            template="plotly_white"
        )
        return fig.to_html(config=config)

    def download_by_f(self, format_d: str):
        dates = self.dates
        values = self.values
        fig = go.Figure(data=[go.Bar(x=dates, y=values, text=values, textposition='outside')])
        fig.update_layout(
            title=self.title,
            xaxis_title="Date",
            yaxis_title="Amount",
            template="plotly_white"
        )
        d_bytes = pio.to_image(fig, format=format_d)
        return d_bytes
