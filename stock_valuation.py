# First you must receive an API key from https://www.alphavantage.co/support/#api-key
import requests
import json


class Assumptions(object):
    def __init__(self):
        percernt_to_decimal = lambda x: x/100 # Function to change percent input to decimal fraction
        self.years_of_analysis = get_int("No. of years for the analysis: ")
        self.rev_growth = percernt_to_decimal(get_int("Enter the estimated annual revenue growth [%]: "))
        self.profit_margin = percernt_to_decimal(get_int("Enter the estimated annual profit margin [%]: "))
        self.fcf_margin = percernt_to_decimal(get_int("Enter the estimated annual free cash flow margin [%]: "))
        self.p_e = get_int("Enter the terminal P/E multiple: ")
        self.p_fcf = get_int("Enter the terminal P/FCF multiple: ")
        self.desired_ror = percernt_to_decimal(get_int("Enter the desired rate of return (discount rate) [%]: "))

    def evaluate(self, revenue):
        """Evaluation of fair price based on the input assumptions"""
        dcf = 0  # Total cash flow over the analysis discounted to present value
        discounted_profit = 0  # Total net profit over the analysis discounted to present value
        discount_multiple = (1 + self.rev_growth)/(1 + self.desired_ror)
        for future_year in range(self.years_of_analysis):
            dcf += (revenue[0] * self.fcf_margin) * discount_multiple ** (future_year + 1)
            discounted_profit += (revenue[0] * self.profit_margin) * discount_multiple ** (future_year + 1)
        terminal_fcf_value = self.p_fcf * (revenue[0] * self.fcf_margin) * discount_multiple ** self.years_of_analysis
        terminal_prft_value = self.p_e * (revenue[0] * self.profit_margin) * discount_multiple ** self.years_of_analysis
        ev_fcf = dcf + terminal_fcf_value
        ev_profit = discounted_profit + terminal_prft_value
        intrinsic_fcf_val = ev_fcf / int(overview_data["SharesOutstanding"])
        intrinsic_profit_val = ev_profit / int(overview_data["SharesOutstanding"])
        print('*' * 80)
        print("Fair price (Free cash flow): {:.2f}".format(intrinsic_fcf_val))
        print("Fair price (net profit): {:.2f}".format(intrinsic_profit_val))


def fetch_data(data_type='INCOME_STATEMENT', ticker_symbol='IBM', api_key='demo'):
    """
    Get data in json format from file if exists otherwise from url at alphavantage.co
    and create file in directory.
    :return: json_data: 
    """
    filename = "{}_{}.json".format(ticker_symbol, data_type)
    try:
        with open(filename, 'r') as json_data_from_file:
            return json.load(json_data_from_file)
    except FileNotFoundError:
        json_data_source = \
            'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'\
            .format(data_type, ticker_symbol, api_key)
        r = requests.get(json_data_source)
        with open(filename, 'w') as dumpfile:
            json.dump(r.json(), dumpfile)
            print(f"{ticker_symbol}_{data_type} File created")
        return r.json()


def get_user_input():
    try:
        with open("personal_api.txt", 'r') as saved_api_file:
            api_key = saved_api_file.read()
    except FileNotFoundError:
        api_key = input("Enter your API key and press `Enter`: ")
        with open("personal_api.txt", 'w') as create_api_file:
            create_api_file.write(apikey)
    ticker = input("Enter ticker symbol or type `quit` to quit, then press `Enter`: ")
    return api_key, ticker


def get_int(prompt):
    while True:
        number = input(prompt)
        if number.isnumeric():
            return int(number)
        else:
            print("Enter a valid number, please try again.")


def single_attribute_list_creator(attribute, statement):
    annual_list = []
    for year in years:
        annual_list.append(int(statement[year][attribute]))
    return annual_list


def calculate_margins(bottom_line: list, top_line: list) -> list:
    margin = []
    for ii in range(len(bottom_line)):
        margin.append(bottom_line[ii]/top_line[ii])
    return margin


def present_historic_data(rev_list, fcf_margin, profit_margin, p_e):
    cagr_rev = []
    for j in range(1, len(rev_list)):
        cagr_rev.append("%.1f"%(((rev_list[0]/rev_list[j]) ** (1/j) - 1) * 100) + " %")
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
        print('*' * 80)
        if ticker.casefold() == 'quit':
            break
        income_data = fetch_data('INCOME_STATEMENT', ticker, apikey)
        balance_data = fetch_data('BALANCE_SHEET', ticker, apikey)
        cash_flow_data = fetch_data('CASH_FLOW', ticker, apikey)
        overview_data = fetch_data('OVERVIEW', ticker, apikey)

        # Create income and cash flow statement dictionary keys are years
        # - for each year a dictionary of the statement is stored
        annual_income_statement = {}
        annual_cash_flow_statement = {}
        years = []
        for index, report in enumerate(income_data['annualReports']):
            # print(data[list(data.keys())[1]][index])
            year = report['fiscalDateEnding'][:4]
            years.append(year)
            annual_income_statement[year] = report
            annual_cash_flow_statement[year] = cash_flow_data['annualReports'][index]

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

        present_historic_data(revenue_list, free_cash_flow_margin, net_income_margin, overview_data["PERatio"])

        # Get user assumptions and perform analysis
        valuation_assumptions = Assumptions()
        valuation_assumptions.evaluate(revenue_list)
