import matplotlib.pyplot as plt

class PatymentGraph:
    def __init__(self, bill_dict):
        self.bill_dict = bill_dict

    def plot_graph(self):
        dates = list(self.bill_dict.keys())
        values = list(self.bill_dict.values())
        plt.bar(dates, values)
        plt.xticks(rotation=45)  # Rotate the x-axis labels for better readability
        plt.xlabel('Date')
        plt.ylabel('Paid')
        plt.title('Payment account graph')
        plt.grid(False)
        plt.show()

