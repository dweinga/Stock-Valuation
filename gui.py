from tkinter import *
from stock_valuation import *
import webbrowser
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)


class AssumptionLine(object):
    def __init__(self, label_text, place, row=1, column=1):
        self.label = Label(place, text=f"{label_text}: ", background=background_color)
        self.label.grid(row=row, column=column)
        self.low_var = StringVar()
        self.low_entry = Entry(place, textvariable=self.low_var, width=4)
        self.low_entry.grid(row=row, column=column+1, padx=10)
        self.high_var = StringVar()
        self.high_entry = Entry(place, textvariable=self.high_var, width=4)
        self.high_entry.grid(row=row, column=column+2, padx=10)


def data_display_line(label_text, place, variable, row=1, column=1):
    """Create line to display data"""
    label = Label(place,
                  text=f"{label_text}: ", background=background_color)
    label.grid(row=row, column=column)
    var = Label(place, textvariable=variable, background=background_color)
    var.grid(row=row, column=column+1)


def plot(revenue, fcf_margin, netprofit_margin, years):
    revenue.reverse()
    fcf_margin.reverse()
    netprofit_margin.reverse()
    years.reverse()

    # the figure that will contain the plot
    fig = Figure(figsize=(4, 4), layout='constrained', facecolor=background_color)

    # adding the subplot
    ax1 = fig.add_subplot(3, 1, 1)
    ax2 = fig.add_subplot(3, 1, 2)
    ax3 = fig.add_subplot(3, 1, 3)

    ax1.sharex(ax3)

    # plotting the graph
    ax1.bar(years, revenue)
    ax2.bar(years, fcf_margin)
    ax3.bar(years, netprofit_margin)

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=mainWindow)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().grid(row=0, column=3, rowspan=4)
    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas,
                                   mainWindow,
                                   pack_toolbar=False)
    toolbar.update()

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().grid(row=0, column=3, padx=5)


def personal_api():
    # Callback function for link to free api web page
    def callback(url):
        webbrowser.open_new_tab(url)

    def but_func():
        with open("../personal_api.txt", 'w') as create_api_file:
            create_api_file.write(api_key.get())
        api_window.destroy()

    # Set up pop-up window
    api_window = Tk()
    api_window.geometry("300x150")
    # api_window.configure(background=background_color)
    api_window.title("API-key Required")
    api_window['padx'] = 10
    api_window['pady'] = 10

    # Content in window
    api_prompt_label = Label(api_window, text="Please enter your API-key.\nReceive an API key from:")
    api_prompt_label.pack()
    api_link = Label(api_window, text="https://www.alphavantage.co/support/#api-key",
                 font=('Helveticabold', 9), fg="blue", cursor="hand2")
    api_link.pack()
    api_link.bind("<Button-1>", lambda e: callback("https://www.alphavantage.co/support/#api-key"))
    api_key = StringVar(api_window)
    api_entry = Entry(api_window, textvariable=api_key)
    api_entry.pack()
    api_button = Button(api_window, text="OK", command=but_func)
    api_button.pack()
    return api_key


def create_stock_data():
    global stock
    try:
        with open("../personal_api.txt", 'r') as saved_api_file:
            api_key = saved_api_file.read()
    except FileNotFoundError:
        api_key = personal_api()
        with open("../personal_api.txt", 'w') as create_api_file:
            create_api_file.write(api_key.get())
    stock = StockData(ticker_var.get(), api_key)
    update_data_display(stock)


def update_data_display(stock):
    """Update the stock data display"""
    def display_market_cap(market_cap):
        """Helper function for displaying the market cap"""
        if (market_cap == "") or (market_cap <= 1000000):
            return market_cap
        elif market_cap > 1000000000:
            billions = market_cap / 1000000000
            return "{:.2f}B".format(billions)
        elif market_cap > 1000000:
            millions = market_cap / 1000000
            return "{:.2f}M".format(millions)

    pe_var.set(stock.overview["PERatio"])
    ps_var.set(stock.overview["PriceToSalesRatioTTM"])
    pb_var.set(stock.overview["PriceToBookRatio"])
    mc_var.set(display_market_cap(int(stock.overview["MarketCapitalization"])))
    # Data parsing
    revenue, fcf_margin, netprofit_margin, years = parse_statements(stock)

    plot(revenue, fcf_margin, netprofit_margin, years)


def analyze():
    """Function executed when the analyze button is pushed"""
    low_assumptions = Assumptions(yrs_variable.get(), float(rev_growth.low_var.get()),
                                  float(profit_margin.low_var.get()), float(fcf_margin.low_var.get()),
                                  float(p_e.low_var.get()), float(p_fcf.low_var.get()), float(desired_ror.low_var.get()))
    high_assumptions = Assumptions(yrs_variable.get(), float(rev_growth.high_var.get()),
                                   float(profit_margin.high_var.get()), float(fcf_margin.high_var.get()),
                                   float(p_e.high_var.get()), float(p_fcf.high_var.get()), float(desired_ror.high_var.get()))
    annual_revenue = int(stock.income_statement['annualReports'][0]['totalRevenue'])
    shares_outst = int(stock.overview["SharesOutstanding"])
    (low_intrinsic_fcf_val, low_intrinsic_profit_val) = low_assumptions.evaluate(annual_revenue, shares_outst)
    (high_intrinsic_fcf_val, high_intrinsic_profit_val) = high_assumptions.evaluate(annual_revenue, shares_outst)
    earnings_low_value.set("{:.2f} $".format(low_intrinsic_profit_val))
    earnings_high_value.set("{:.2f} $".format(high_intrinsic_profit_val))
    fcf_low_value.set("{:.2f} $".format(low_intrinsic_fcf_val))
    fcf_high_value.set("{:.2f} $".format(high_intrinsic_fcf_val))


# Set defaults for the UI
background_color = "gray"

# Initialize main tkinter window
mainWindow = Tk()

# Set up the dimensions and visuals
# of the main window
mainWindow.geometry("800x430")
mainWindow.configure(background=background_color)
mainWindow.title("Stock Initial Analysis")
mainWindow['padx'] = 10
mainWindow['pady'] = 10

# Symbol input and stock fundamental data frame
data_frame = Frame(mainWindow, relief="sunken", borderwidth=1, background=background_color)
data_frame.grid(row=0, column=0, sticky="ew", columnspan=3, rowspan=1)

# Input ticker symbol
ticker_label = Label(data_frame, text="Symbol: ", background=background_color)
ticker_label.grid(row=0, column=0)
ticker_var = StringVar(mainWindow)
ticker_entry = Entry(data_frame, textvariable=ticker_var, width=8)
ticker_entry.grid(row=0, column=1, columnspan=2, sticky="w", padx=5)
ticker_button = Button(data_frame, text="Get data", command=create_stock_data)
ticker_button.grid(row=0, column=3, pady=4)

# Stock fundamental data display
pe_var = StringVar(mainWindow)
data_display_line("P/E", data_frame, pe_var, 1, 0)
ps_var = StringVar(mainWindow)
data_display_line("P/S", data_frame, ps_var, 2, 0)
pb_var = StringVar(mainWindow)
data_display_line("P/B", data_frame, pb_var, 3, 0)
mc_var = StringVar(mainWindow)
data_display_line("Market Cap", data_frame, mc_var, 4, 0)

# Assumptions
assumptions_frame = LabelFrame(mainWindow, text="Valuation Assumptions",
                               relief="sunken", borderwidth=1, background=background_color)
assumptions_frame.grid(row=1, column=0, sticky="ew", columnspan=3, rowspan=1)

low_label = Label(assumptions_frame, text="Low", background=background_color)
low_label.grid(row=1, column=1)
high_label = Label(assumptions_frame, text="High", background=background_color)
high_label.grid(row=1, column=2)

OPTIONS = [1, 2, 3, 4, 5,
           6, 7, 8, 9, 10,
           11, 12, 13, 14, 15,
           16, 17, 18, 19, 20]
yrs_variable = IntVar(assumptions_frame)
yrs_variable.set(10) # default value
yrs_for_analysis_label = Label(assumptions_frame, text="Years of analysis: ", background=background_color)
yrs_for_analysis_label.grid(row=0, column=0)
yrs_for_analysis = OptionMenu(assumptions_frame, yrs_variable, *OPTIONS)
yrs_for_analysis.grid(row=0, column=1, columnspan=2)

rev_growth = AssumptionLine("Annual Revenue Growth", assumptions_frame, 2, 0)
profit_margin = AssumptionLine("Profit Margin", assumptions_frame, 3, 0)
fcf_margin = AssumptionLine("FCF Margin", assumptions_frame, 4, 0)
p_e = AssumptionLine("Future P/E", assumptions_frame, 5, 0)
p_fcf = AssumptionLine("Future P/FCF", assumptions_frame, 6, 0)
desired_ror = AssumptionLine("Desired ROR", assumptions_frame, 7, 0)

analyze_button = Button(mainWindow, text="Analyze", command=analyze)
analyze_button.grid(row=2, column=0, columnspan=3, sticky="ew", pady=4)

# Fair value presentation
fair_value_frame = LabelFrame(mainWindow, text="Fair Value",
                              relief="sunken", borderwidth=1, background=background_color)
fair_value_frame.grid(row=3, column=0, sticky="ew", columnspan=3, rowspan=1)

earnings_low_value = Variable(fair_value_frame)
earnings_low_value.set(0) # default value
earnings_high_value = Variable(fair_value_frame)
earnings_high_value.set(0) # default value
earnings_label = Label(fair_value_frame, text="Discounted Earnings: ", background=background_color)
earnings_label.grid(row=1, column=0)
earnings_low_label = Label(fair_value_frame, textvariable=earnings_low_value, background=background_color)
earnings_low_label.grid(row=1, column=1, sticky="ew")
earnings_high_label = Label(fair_value_frame, textvariable=earnings_high_value, background=background_color)
earnings_high_label.grid(row=1, column=2, sticky="ew")

fcf_low_value = Variable(fair_value_frame)
fcf_low_value.set(0) # default value
fcf_high_value = Variable(fair_value_frame)
fcf_high_value.set(0) # default value
fcf_label = Label(fair_value_frame, text="Discounted Cash Flow: ", background=background_color)
fcf_label.grid(row=2, column=0)
fcf_low_label = Label(fair_value_frame, textvariable=fcf_low_value, background=background_color)
fcf_low_label.grid(row=2, column=1, sticky="ew")
fcf_high_label = Label(fair_value_frame, textvariable=fcf_high_value, background=background_color)
fcf_high_label.grid(row=2, column=2, sticky="ew")

mainWindow.mainloop()
