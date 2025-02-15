import yfinance as yf

research = yf.Search("apple", include_research=True).research
print('debug')