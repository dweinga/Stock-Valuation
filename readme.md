# Stock Valuation Program
## Overview
This program is a simple program to evaluate a fair price for a stock based
on the previous year's financial data and assumptions of future revenue, earnings
and free cash flow.

## Using the Program
On the first time you run the program it will prompt you to enter your personal
API key. It should be obtained beforehand at:
https://www.alphavantage.co/support/#api-key.
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

Then, you must enter assumptions as input (all in whole numbers [int]):
 * Number of years for the analysis
 * Expected annualized revenue growth over the amount of years you chose into the future
 * Average expected profit margin
 * Average expected free cash flow margin
 * The desired rate of return
 * A projected Price to Earnings ratio (P/E) at the end of the time of the analysis
 * A projected Price to Free Cash Flow ratio (P/FCF) at the end of the time of the analysis

The program will then calculate two fair price values, the first based on Free Cash Flow
and the second on the Net Profit.

The program will start over prompting for a new ticker symbol or type 'quit' to end the program.

## Current pitfalls
A few problems that I hope to fix in the future:
* Error handling - specially when there is a mistake with the ticker symbol.
+ Input must be `int` numbers for the assumptions.
* Hopefully, at some point, create a UI.