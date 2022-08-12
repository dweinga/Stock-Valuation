"""Before running the program you must receive an API key from
 https://www.alphavantage.co/support/#api-key"""
import requests
import numpy as np


class Assumptions(object):
    def __init__(self, yrs_of_analysis, rev_grwth, prft_margin, fcf_mrgn, pe, pfcf, ror):
        def percent_to_decimal(x):
            """Helper function to change percent input to decimal fraction"""
            return x/100

        self.years_of_analysis = yrs_of_analysis
        self.rev_growth = percent_to_decimal(rev_grwth)
        self.profit_margin = percent_to_decimal(prft_margin)
        self.fcf_margin = percent_to_decimal(fcf_mrgn)
        self.p_e = pe
        self.p_fcf = pfcf
        self.desired_ror = percent_to_decimal(ror)

    def evaluate(self, revenue, shares):
        """Evaluation of fair stock price based on the input assumptions"""
        discount_multiple = (1 + self.rev_growth)/(1 + self.desired_ror)
        yrs = np.arange(self.years_of_analysis) + np.ones(self.years_of_analysis)
        dcf_arr = (revenue * self.fcf_margin) * discount_multiple ** yrs
        dcf = dcf_arr.sum()
        discounted_profit_arr = (revenue * self.profit_margin) * discount_multiple ** yrs
        discounted_profit = discounted_profit_arr.sum()
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

    def trailing_twelve_months(self):
        qurterly = [[q_report['reportedCurrency'], q_report['totalRevenue']]
                    for q_report in self.income_statement['quarterlyReports']]
        print(qurterly)

        if qurterly[0][0] != 'USD':
            url = 'https://api.exchangerate.host/convert?from={0}&to=USD'.format(qurterly[0][0])
            response = requests.get(url)
            currency_data = response.json()
            print(currency_data)


def fetch_data(data_type='INCOME_STATEMENT', ticker_symbol='IBM', api_key='demo'):
    """
    Get data in json format from url at alphavantage.co.
    :return: json_data:
    """
    url = 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'
    json_data_source = url.format(data_type, ticker_symbol, api_key)
    requested_data = requests.get(json_data_source)
    return requested_data.json()


def get_api() -> str:
    try:
        with open("../personal_api.txt", 'r') as saved_api_file:
            api_key = saved_api_file.read()
    except FileNotFoundError:
        api_key = input("Enter your API key and press `Enter`: ")
        with open("../personal_api.txt", 'w') as create_api_file:
            create_api_file.write(api_key)
    return api_key


def get_user_input() -> (str, str):
    api_key = get_api()
    tikr = input("Enter ticker symbol or type `quit` to quit, then press `Enter`: ")
    return api_key, tikr


def get_assumptions() -> (int, float, float, float, float, float, float):
    yrs_of_analysis = get_int("No. of years for the analysis: ")
    rev_grwth = get_number("Enter the estimated annual revenue growth [%]: ")
    profit_marg = get_number("Enter the estimated annual profit margin [%]: ")
    fcf_marg = get_number("Enter the estimated annual free cash flow margin [%]: ")
    pe_ratio = get_number("Enter the terminal P/E multiple: ")
    p_to_fcf = get_number("Enter the terminal P/FCF multiple: ")
    dror = get_number("Enter the desired rate of return (discount rate) [%]: ")
    return [yrs_of_analysis, rev_grwth, profit_marg, fcf_marg, pe_ratio, p_to_fcf, dror]


def get_int(prompt: str) -> int:
    while True:
        number = input(prompt)
        if number.isnumeric():
            return int(number)
        else:
            print("Enter a valid whole number, please try again.")


def get_number(prompt: str) -> float:
    while True:
        number = input(prompt)
        try:
            return float(number)
        except ValueError:
            print("Enter a valid number, please try again.")


def single_attribute_list_generator(attribute: str, statement: dict, years: list) -> list:
    annual_list = [(int(statement[yr][attribute])) for yr in years]
    return annual_list


def calculate_margins(bottom_line: list, top_line: list) -> list:
    """"""
    margin = [bottom_line[ii]/top_line[ii] for ii in range(len(bottom_line))]
    return margin


def parse_statements(stock):
    # Create income and cash flow statement dictionary keys are years
    # - for each year a dictionary of the statement is stored
    annual_income_statement = {}
    annual_cash_flow_statement = {}
    years = []
    for index, report in enumerate(stock.income_statement['annualReports']):
        year = report['fiscalDateEnding'][:4]
        years.append(year)
        annual_income_statement[year] = report
        annual_cash_flow_statement[year] = stock.cash_flow['annualReports'][index]

    revenue_list = single_attribute_list_generator('totalRevenue',
                                                   annual_income_statement,
                                                   years)
    net_profit_list = single_attribute_list_generator('netIncome',
                                                      annual_income_statement,
                                                      years)
    net_profit_margin = calculate_margins(net_profit_list,
                                          revenue_list)

    # Free cash flow calculation
    operating_cash_flow_list = single_attribute_list_generator('operatingCashflow',
                                                               annual_cash_flow_statement,
                                                               years)
    capital_expenditures_list = single_attribute_list_generator('capitalExpenditures',
                                                                annual_cash_flow_statement,
                                                                years)
    free_cash_flow_list = [(operating_cash_flow_list[i] - capital_expenditures_list[i])
                           for i in range(len(operating_cash_flow_list))]
    free_cash_flow_margin = calculate_margins(free_cash_flow_list,
                                              revenue_list)
    return revenue_list, net_profit_margin, free_cash_flow_margin, years


def display_historic_data(rev_list, fcf_mrgn, prft_margin, pe):
    cagr_rev = []
    for j in range(1, len(rev_list)):
        cagr_rev.append("%.1f" % (((rev_list[0]/rev_list[j]) ** (1/j) - 1) * 100) + " %")
    avg_fcf_margin = []
    sum_fcf_margin = 0
    avg_profit_margin = []
    sum_profit_margin = 0
    for j in range(len(fcf_mrgn)):
        sum_fcf_margin += fcf_mrgn[j]
        avg_fcf_margin.append("%.1f" % (sum_fcf_margin/(j + 1) * 100) + " %")
        sum_profit_margin += prft_margin[j]
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
    print(f"Current P/E: {pe}")
    print('*' * 80)


if __name__ == "__main__":
    while True:
        apikey, ticker = get_user_input()
        if ticker.casefold() == 'quit':
            break
        stock = StockData(ticker, apikey)
        # stock.trailingTM()

        # Data parsing
        revenue_list, free_cash_flow_margin, net_profit_margin, years = parse_statements(stock)

        # Arrange and display parsed data
        display_historic_data(revenue_list,
                              free_cash_flow_margin,
                              net_profit_margin,
                              stock.overview["PERatio"])

        # Get user assumptions and perform analysis
        [years_of_analysis, rev_growth, profit_margin, fcf_margin, p_e, p_fcf, desired_ror] = get_assumptions()
        valuation_assumptions = Assumptions(years_of_analysis,
                                            rev_growth,
                                            profit_margin,
                                            fcf_margin,
                                            p_e,
                                            p_fcf,
                                            desired_ror)
        shares_outstanding = int(stock.overview["SharesOutstanding"])
        (intrinsic_fcf_val, intrinsic_profit_val) = valuation_assumptions.evaluate(revenue_list[0],
                                                                                   shares_outstanding)
        print_fair_price(intrinsic_fcf_val, intrinsic_profit_val)
