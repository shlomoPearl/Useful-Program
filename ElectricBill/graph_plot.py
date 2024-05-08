from datetime import datetime
import matplotlib.pyplot as plt

class PatymentGraph:
    def __init__(self, bill_dict, title='Payment account graph'):
        self.bill_dict = bill_dict
        self.title = title

    def plot_graph(self):
        dates = [datetime.strptime(date, '%m/%Y') for date in self.bill_dict.keys()]
        sorted_dates = sorted(dates)
        sorted_dates_lst = [date.strftime('%m/%Y') for date in sorted_dates]
        # Get corresponding values in the sorted order
        values = [self.bill_dict[date] for date in sorted_dates_lst]

        for i, value in enumerate(values):
            plt.text(i, value + 5, str(value), ha='center', fontsize=8)
        plt.bar(sorted_dates_lst, values)
        plt.xticks(rotation=40)  # Rotate the x-axis labels for better readability
        plt.xlabel('Date')
        plt.ylabel('Paid')
        plt.title(self.title)
        plt.grid(False)
        plt.show()

