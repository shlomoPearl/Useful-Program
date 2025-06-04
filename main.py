import bill
import gmail
import graph_plot

address_search = "gviyarevava@revava.co.il"


def main():
    g = gmail.Gmail(address_search, subject='ועד מקומי רבבה', result_num=12,
                    date_range=["01/01/2023", "31/12/2023"])  ## actual need this date_range - [01/02/2023,31/01/2024]
    g_auth = g.authenticate()
    g_search = g.search_mail(g_auth)
    print(len(g_search))
    b = bill.ReadBill(g_search)
    bill_parse = b.parser('חשמל')
    print(bill_parse)
    g = graph_plot.PatymentGraph(bill_parse, '2023 Electric-Bill Graph')
    g.plot_graph()



if __name__ == '__main__':
    main()
