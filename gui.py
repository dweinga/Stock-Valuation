from tkinter import *
from stock_valuation import *


class AssumptionLine(object):
    def __init__(self, label_text, place, row=1, column=1):
        self.label = Label(place, text=f"{label_text}: ", background="gray")
        self.label.grid(row=row, column=column)
        self.low_var = StringVar()
        self.low_entry = Entry(place, textvariable=self.low_var)
        self.low_entry.grid(row=row, column=column+1)
        self.high_var = StringVar()
        self.high_entry = Entry(place, textvariable=self.high_var)
        self.high_entry.grid(row=row, column=column+2)


def data_presentation(label_text, place, variable, row=1, column=1):
    label = Label(place, text=f"{label_text}: ", background="gray")
    label.grid(row=row, column=column)
    var = Label(place, textvariable=variable, background="gray")
    var.grid(row=row, column=column+1)


mainWindow = Tk()

# Set up the screen
mainWindow.geometry("640x480")
mainWindow.configure(background="gray")
mainWindow.title("Stock Valuation")
mainWindow['padx'] = 10
mainWindow['pady'] = 10

# Input ticker symbol
data_frame = Frame(mainWindow, relief="sunken", borderwidth=1, background="gray")
data_frame.grid(row=0, column=0, sticky="ew", columnspan=3, rowspan=1)

ticker_label = Label(data_frame, text="Symbol: ", background="gray")
ticker_label.grid(row=0, column=0)
ticker_var = StringVar(mainWindow)
ticker_entry = Entry(data_frame, textvariable=ticker_var)
ticker_entry.grid(row=0, column=1, columnspan=2, sticky="w")
ticker_button = Button(data_frame, text="Get data")
ticker_button.grid(row=0, column=3)

# Stock data
pe_var = StringVar(mainWindow)
data_presentation("P/E", data_frame, pe_var, 1, 0)
ps_var = StringVar(mainWindow)
data_presentation("P/S", data_frame, ps_var, 2, 0)
pfcf_var = StringVar(mainWindow)
data_presentation("P/FCF", data_frame, pfcf_var, 3, 0)
mc_var = StringVar(mainWindow)
data_presentation("Market Cap", data_frame, mc_var, 4, 0)

# Assumptions
assumptions_frame = LabelFrame(mainWindow, text="Valuation Assumptions",
                               relief="sunken", borderwidth=1, background="gray")
assumptions_frame.grid(row=2, column=0, sticky="ew", columnspan=3, rowspan=1)

low_label = Label(assumptions_frame, text="Low", background="gray")
low_label.grid(row=1, column=1)
high_label = Label(assumptions_frame, text="High", background="gray")
high_label.grid(row=1, column=2)

OPTIONS = [1, 2, 3, 4, 5,
           6, 7, 8, 9, 10,
           11, 12, 13, 14, 15]
yrs_variable = StringVar(assumptions_frame)
yrs_variable.set(10) # default value
yrs_for_analysis_label = Label(assumptions_frame, text="Years of analysis: ", background="gray")
yrs_for_analysis_label.grid(row=0, column=0)
yrs_for_analysis = OptionMenu(assumptions_frame, yrs_variable, *OPTIONS)
yrs_for_analysis.grid(row=0, column=1)

rev_growth = AssumptionLine("Annual Revenue Growth", assumptions_frame, 2, 0)
profit_margin = AssumptionLine("Profit Margin", assumptions_frame, 3, 0)
fcf_margin = AssumptionLine("FCF Margin", assumptions_frame, 4, 0)
p_e = AssumptionLine("Future P/E", assumptions_frame, 5, 0)
p_fcf = AssumptionLine("Future P/FCF", assumptions_frame, 6, 0)
desired_ror = AssumptionLine("Desired ROR", assumptions_frame, 7, 0)

analyze_button = Button(mainWindow, text="Analyze")
analyze_button.grid(row=3, column=0, columnspan=3, sticky="ew")

# Fair value presentation
fair_value_frame = LabelFrame(mainWindow, text="Fair Value",
                              relief="sunken", borderwidth=1, background="gray")
fair_value_frame.grid(row=4, column=0, sticky="ew", columnspan=3, rowspan=1)

earnings_low_value = Variable(fair_value_frame)
earnings_low_value.set(0) # default value
earnings_high_value = Variable(fair_value_frame)
earnings_high_value.set(0) # default value
earnings_label = Label(fair_value_frame, text="Discounted Earnings: ", background="gray")
earnings_label.grid(row=1, column=0)
earnings_low_label = Label(fair_value_frame, textvariable=earnings_low_value, background="gray")
earnings_low_label.grid(row=1, column=1, sticky="ew")
earnings_high_label = Label(fair_value_frame, textvariable=earnings_high_value, background="gray")
earnings_high_label.grid(row=1, column=2, sticky="ew")

fcf_low_value = Variable(fair_value_frame)
fcf_low_value.set(0) # default value
fcf_high_value = Variable(fair_value_frame)
fcf_high_value.set(0) # default value
fcf_label = Label(fair_value_frame, text="Discounted Cash Flow: ", background="gray")
fcf_label.grid(row=2, column=0)
fcf_low_label = Label(fair_value_frame, textvariable=fcf_low_value, background="gray")
fcf_low_label.grid(row=2, column=1, sticky="ew")
fcf_high_label = Label(fair_value_frame, textvariable=fcf_high_value, background="gray")
fcf_high_label.grid(row=2, column=2, sticky="ew")



mainWindow.mainloop()
