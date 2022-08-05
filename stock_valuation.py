"""Before running the program you must receive an API key from
 https://www.alphavantage.co/support/#api-key"""
import requests


class Assumptions(object):
    def __init__(self, years_of_analysis, rev_growth, profit_margin, fcf_margin, p_e, p_fcf, desired_ror):
        def percent_to_decimal(x):
            """Helper function to change percent input to decimal fraction"""
            return x/100

        self.years_of_analysis = years_of_analysis
        self.rev_growth = percent_to_decimal(rev_growth)
        self.profit_margin = percent_to_decimal(profit_margin)
        self.fcf_margin = percent_to_decimal(fcf_margin)
        self.p_e = p_e
        self.p_fcf = p_fcf
        self.desired_ror = percent_to_decimal(desired_ror)

    def evaluate(self,   revenue, shares):
        """Evaluation of fair stock price based on the input assumptions"""
        dcf = 0  # Total cash flow over the analysis discounted to present value
        discounted_profit = 0  # Total net profit over the analysis discounted to present value
        discount_multiple = (1 + self.rev_growth)/(1 + self.desired_ror)
        for future_year in range(self.years_of_analysis):
            dcf += (revenue * self.fcf_margin) * discount_multiple ** (future_year + 1)
            discounted_profit += (revenue * self.profit_margin) * discount_multiple ** (future_year + 1)
        terminal_fcf_value = self.p_fcf * (revenue * self.fcf_margin) * discount_multiple ** self.years_of_analysis
        terminal_prft_value = self.p_e * (revenue * self.profit_margin) * discount_multiple ** self.years_of_analysis
        ev_fcf = dcf + terminal_fcf_value
        ev_profit = discounted_profit + terminal_prft_value
        intrinsic_fcf = ev_fcf / shares
        intrinsic_profit = ev_profit / shares
        return intrinsic_fcf, intrinsic_profit


def print_fair_price(intrinsic_fcf, intrinsic_profit):
    print('*' * 80)
    print("Fair price (Free cash flow): {:.2f}".format(intrinsic_fcf))
    print("Fair price (net profit): {:.2f}".format(intrinsic_profit))


class StockData(object):
    def __init__(self, ticker_symbol='IBM', api='demo'):
        self.symbol = ticker_symbol
        self.income_statement = fetch_data('INCOME_STATEMENT', ticker_symbol, api)
        self.balance_sheet = fetch_data('BALANCE_SHEET', ticker_symbol, api)
        self.cash_flow = fetch_data('CASH_FLOW', ticker_symbol, api)
        self.overview = fetch_data('OVERVIEW', ticker_symbol, api)
        # self.currency = self.overview['Currency']

    def trailingTM(self):
        qurterly = [[q_report['reportedCurrency'], q_report['totalRevenue']] for q_report in self.income_statement['quarterlyReports']]
        print(qurterly)

        if qurterly[0][0] != 'USD':
            url = 'https://api.exchangerate.host/convert?from={0}&to=USD'.format(qurterly[0][0])
            response = requests.get(url)
            data = response.json()
            print(data)


def fetch_data(data_type='INCOME_STATEMENT', ticker_symbol='IBM', api_key='demo'):
    """
    Get data in json format from url at alphavantage.co.
    :return: json_data:
    """
    url = 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'
    json_data_source = url.format(data_type, ticker_symbol, api_key)
    requested_data = requests.get(json_data_source)
    return requested_data.json()


def get_api():
    try:
        with open("../personal_api.txt", 'r') as saved_api_file:
            api_key = saved_api_file.read()
    except FileNotFoundError:
        api_key = input("Enter your API key and press `Enter`: ")
        with open("../personal_api.txt", 'w') as create_api_file:
            create_api_file.write(api_key)
    return api_key


def get_user_input():
    api_key = get_api()
    ticker = input("Enter ticker symbol or type `quit` to quit, then press `Enter`: ")
    return api_key, ticker


def get_assumptions():
    years_of_analysis = get_int("No. of years for the analysis: ")
    rev_growth = get_number("Enter the estimated annual revenue growth [%]: ")
    profit_margin = get_number("Enter the estimated annual profit margin [%]: ")
    fcf_margin = get_number("Enter the estimated annual free cash flow margin [%]: ")
    p_e = get_number("Enter the terminal P/E multiple: ")
    p_fcf = get_number("Enter the terminal P/FCF multiple: ")
    desired_ror = get_number("Enter the desired rate of return (discount rate) [%]: ")
    return [years_of_analysis, rev_growth, profit_margin, fcf_margin, p_e, p_fcf, desired_ror]


def get_int(prompt):
    while True:
        number = input(prompt)
        if number.isnumeric():
            return int(number)
        else:
            print("Enter a valid whole number, please try again.")


def get_number(prompt):
    while True:
        number = input(prompt)
        try:
            return float(number)
        except ValueError:
            print("Enter a valid number, please try again.")


def single_attribute_list_creator(attribute, statement):
    annual_list = []
    for year in years:
        annual_list.append(int(statement[year][attribute]))
    return annual_list


def calculate_margins(bottom_line: list, top_line: list) -> list:
    """"""
    margin = [bottom_line[ii]/top_line[ii] for ii in range(len(bottom_line))]
    return margin


def present_historic_data(rev_list, fcf_margin, profit_margin, p_e):
    cagr_rev = []
    for j in range(1, len(rev_list)):
        cagr_rev.append("%.1f" % (((rev_list[0]/rev_list[j]) ** (1/j) - 1) * 100) + " %")
    avg_fcf_margin = []
    sum_fcf_margin = 0
    avg_profit_margin = []
    sum_profit_margin = 0
    for j in range(len(fcf_margin)):
        sum_fcf_margin += fcf_margin[j]
        avg_fcf_margin.append("%.1f" % (sum_fcf_margin/(j + 1) * 100) + " %")
        sum_profit_margin += profit_margin[j]
        avg_profit_margin.append("%.1f" % (sum_profit_margin/(j + 1) * 100) + " %")

    # Print the data in table
    headers = ["Rev. Grwth|", "Prft Mrgin|", "FCF Margin|"]
    content = [cagr_rev, avg_profit_margin, avg_fcf_margin]
    print('*' * 80)
    print("----------| 1 year | 2 year | 3 year | 4 year | 5 year |")
    for row, header in enumerate(headers):
        print(header, end='')
        for item in content[row]:
            print(f" {item} ", end='|')
        print()
    print(f"Current P/E: {p_e}")
    print('*' * 80)


if __name__ == "__main__":
    while True:
        apikey, ticker = get_user_input()
        if ticker.casefold() == 'quit':
            break
        stock = StockData(ticker, apikey)
        # stock.trailingTM()

        # Create income and cash flow statement dictionary keys are years
        # - for each year a dictionary of the statement is stored
        annual_income_statement = {}
        annual_cash_flow_statement = {}
        years = []
        for index, report in enumerate(stock.income_statement['annualReports']):
            # print(data[list(data.keys())[1]][index])
            year = report['fiscalDateEnding'][:4]
            years.append(year)
            annual_income_statement[year] = report
            annual_cash_flow_statement[year] = stock.cash_flow['annualReports'][index]

        revenue_list = single_attribute_list_creator('totalRevenue', annual_income_statement)
        net_income_list = single_attribute_list_creator('netIncome', annual_income_statement)
        net_income_margin = calculate_margins(net_income_list, revenue_list)

        # Free cash flow calculation
        free_cash_flow_list = []
        operating_cash_flow_list = single_attribute_list_creator('operatingCashflow', annual_cash_flow_statement)
        capital_expenditures_list = single_attribute_list_creator('capitalExpenditures', annual_cash_flow_statement)
        for i in range(len(operating_cash_flow_list)):
            free_cash_flow_list.append(operating_cash_flow_list[i] - capital_expenditures_list[i])
        free_cash_flow_margin = calculate_margins(free_cash_flow_list, revenue_list)

        present_historic_data(revenue_list, free_cash_flow_margin, net_income_margin, stock.overview["PERatio"])

        # Get user assumptions and perform analysis
        [years_of_analysis, rev_growth, profit_margin, fcf_margin, p_e, p_fcf, desired_ror] = get_assumptions()
        valuation_assumptions = Assumptions(years_of_analysis, rev_growth, profit_margin, fcf_margin, p_e, p_fcf, desired_ror)
        shares_outstanding = int(stock.overview["SharesOutstanding"])
        (intrinsic_fcf_val, intrinsic_profit_val) = valuation_assumptions.evaluate(revenue_list[0], shares_outstanding)
        print_fair_price(intrinsic_fcf_val, intrinsic_profit_val)
