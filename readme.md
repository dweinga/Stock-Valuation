# Stock Valuation Program
# The Alpha Vantage API's used for this program have changed from free account to premium account! Therefore the program dosn't work.
## It can currently be used on demo mode only which is - the api key must be - "demo" and the only ticker symbol that will work is IBM.
## Overview
This program provides a tool for initial evaluation of a fair price for a stock based
on the previous year's financial data and assumptions of future revenue, earnings
and free cash flow.

## Using the Program
The program can be executed with a GUI by running the gui.py file or from the
terminal running stock_valuation.py.
### Use from Terminal/Command Line
The first time the program is executed it will prompt to enter your personal
API key. It should be obtained beforehand at:
[https://www.alphavantage.co/support/#api-key]().

After the first time, the API key will be saved in a text file and won't be requested again.
The Alpha Vantage free API key is limited to 5 requests per minute, the 
program makes 4 requests in each run, so you'll need to wait at least a minute between runs.

You will be prompt to type in a ticker symbol, then the program will present key financial 
data averaged over 1-5 years, Example:

-------------| 1 year | 2 year | 3 year | 4 year | 5 year |

Rev. Grwth| 33.7 % | 19.0 % | 11.0 % | 12.2 % |

Prft Mrgin| 26.1 % | 23.6 % | 22.9 % | 22.8 % | 22.4 % |

FCF Margin| 25.6 % | 26.3 % | 25.2 % | 24.9 % | 24.4 % |

Current P/E: 23.08

Then, you must enter assumptions as input (The years must be integer):
 * Number of years for the analysis
 * Expected annualized revenue growth over the amount of years you chose into the future
 * Average expected profit margin
 * Average expected free cash flow margin
 * The desired rate of return
 * A projected Price to Earnings ratio (P/E) at the end of the time of the analysis
 * A projected Price to Free Cash Flow ratio (P/FCF) at the end of the time of the analysis

The program will then calculate two fair price values, the first based on Free Cash Flow
and the second on the Net Profit.

The program will then start over prompting for a new ticker symbol or type 'quit' to end the program.

### GUI
The GUI runs the same analysis and is still under work.

On the first time it is executed, after entering a ticker symbol and pressing `get data`
a window will open where you must enter your API key.
*PRESS THE OK BUTTON ONLY WHEN THE API KEY IS ENTERED,
OTHERWISE A FAULTY FILE WILL BE CREATED.*

At the moment, some of the company key stats will show up but no historic data
is presented.
Next you will choose low (conservative) and high (optimistic) assumptions and press the analyze button.

The Alpha Vantage free API key is limited to 5 requests per minute.
The program makes 4 requests in each time you press the `get data`, so you'll need to wait at least a minute between runs.

## Current Drawbacks
A few problems that I hope to fix in the future:
* Error handling - specially when there is a mistake with the ticker symbol.
* The evaluation uses last recorded annual revenue and not TTM revenue.
