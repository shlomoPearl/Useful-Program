import matplotlib.pyplot as plt


def plot(bill_map, title, x_title):
    month_list = list(bill_map.keys())
    bill_list = list(bill_map.values())
    fig = plt.figure(figsize=(10, 5))
    # creating the bar plot
    plt.bar(month_list, bill_list)
    plt.xlabel(x_title)
    plt.ylabel("\u20AA")
    plt.title(title)
    plt.show()

