import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader as web
import yfinance as yf 
import math
import streamlit as st
import datetime

def app():

    st.title('Crypto MACD Analysis')


    st.write('Select the dates you want to analyse:')
    start_date = st.date_input('Start date')
    end_date = st.date_input('End date')
    if start_date < end_date:
        st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
    else:
        st.error('Error: End date must fall after start date.')

    start= start_date
    end = end_date

    data = {'Full name': ['Bitcoin', 'Ethereum', 'Tether', 'USD Coin', 'Binance Coin', 'XRP', 'Binance USD', 'Cardano', 'Solana', 'HEX', 'Dogecoin', 'Polkadot', 'Wrapped TRON', 'Wrapped Bitcoin', 'TRON', 'Avalanche', 'Lido stETH', 'Dai', 'SHIBA INU', 'Polygon', 'Litecoin', 'UNUS SED LEO', 'Crypto.com Coin', 'yOUcash', 'NEAR Protocol'],
            'Abbreviations': ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP','BUSD', 'ADA', 'SOL', 'HEX', 'DOGE', 'DOT', 'WTRX', 'WBTC', 'TRX', 'AVAX' , 'STETH', 'DAI', 'SHIB', 'MATIC', 'LTC', 'LEO', 'CRO', 'YOUC', 'NEAR']}
    acro = pd.DataFrame(data)

    input_ = st.text_input('Enter crypto Ticker', 'ETH')
    crypto = input_+'-USD'
    crypto1 = input_


    if st.button('Display crypto abbreviations'):
         st.dataframe(acro)
    st.write('To check any crypto abreviation that work in this page go to: https://finance.yahoo.com/cryptocurrencies/?count=100&offset=0')       

    invest_money = st.number_input('How much would you like to invest?', step=1000)
    st.write('Your current investment is: ', invest_money)

    df = web.DataReader(crypto, data_source="yahoo", start= start, end= end)

    st.subheader(f'Closing price ($) for {crypto1} over time')
    fig= plt.figure(figsize=(16,8))
    plt.plot(df["Close"])
    plt.xlabel("Date", fontsize = 18)
    plt.ylabel("Close Price USD ($)", fontsize = 18)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    #Calculate the MACD and signal line indicators
    #Calculate the short term exponential moving average (EMA)
    shortEMA = df.Close.ewm(span=12, adjust=False).mean() #Twelve periods
    #Calculate the long term exponential moving average (EMA)
    longEMA = df.Close.ewm(span=26, adjust=False).mean()
    #Calculate the MACD line 
    MACD = shortEMA - longEMA
    #Calculate the signal line
    signal = MACD.ewm(span=9, adjust=False).mean()


    st.subheader(f'MACD and signal for {crypto1} over time')
    fig = plt.figure(figsize = (12.2, 4.5))
    plt.plot(df.index, MACD, label=f"{crypto1} MACD", color = "red")
    plt.plot(df.index, signal, label="Signal Line", color = "blue")
    plt.legend(loc="upper left")
    plt.xticks(rotation = 45)
    st.pyplot(fig)

    df["MACD"] = MACD
    df["Signal Line"] = signal

    def buy_sell(signal):
        Buy = []
        Sell = []
        flag = -1

        for i in range(0, len(signal)):
            if signal["MACD"][i] > signal["Signal Line"][i]:
                Sell.append(np.nan)
                if flag != 1:
                    Buy.append(signal["Close"][i])
                    flag = 1
                else:
                    Buy.append(np.nan)
            elif signal["MACD"][i] < signal["Signal Line"][i]:
                Buy.append(np.nan)
                if flag != 0:
                    Sell.append(signal["Close"][i])
                    flag = 0
                else:
                    Sell.append(np.nan)

            else: 
                Sell.append(np.nan)
                Buy.append(np.nan)

        return (Buy, Sell)

    a = buy_sell(df)
    df["Buy_Signal_Price"] = a[0]
    df["Sell_Signal_Price"] = a[1]

    st.subheader(f'Buy and sell calls for {crypto1} over time')
    fig = plt.figure(figsize = (12.2, 4.5))
    plt.scatter(df.index, df["Buy_Signal_Price"], color="green", label = "Buy", marker = "^", alpha = 1)
    plt.scatter(df.index, df["Sell_Signal_Price"], color="red", label = "Sell", marker = "v", alpha = 1)
    plt.plot(df["Close"], label = "Close Price", alpha = 0.35)
    plt.title("Close Price Buy Sell Signals")
    plt.xlabel("Date")
    plt.ylabel("Close Price USD ($)")
    plt.legend(loc = "upper left")
    plt.xticks(rotation = 45)
    st.pyplot(fig)


    measure = df[["Buy_Signal_Price", "Sell_Signal_Price"]]

    measure["Buy_0"] = measure["Buy_Signal_Price"].fillna(0)
    measure["Sell_0"] = measure["Sell_Signal_Price"]. fillna(0)

    money = invest_money
    shares = invest_money/df["Close"][0]
    for i in range(0, (len(measure["Buy_0"] + 1))):
        if measure["Buy_0"][i] == 0 and measure["Sell_0"][i] == 0:
            pass
        elif measure["Buy_0"][i] != 0:
            shares = money/measure["Buy_0"][i]
        elif measure["Sell_0"][i] != 0:
            money = shares*measure["Sell_0"][i]
        #We find if the last movement is a sell or a purchase
    for i in range(0, (len(measure["Buy_0"] + 1))):
        if measure["Buy_0"][i] != 0:
            counter_buy = i
        if measure["Sell_0"][i] != 0:
            counter_sell = i
    #We calculate the money    
    if counter_sell > counter_buy:
        final_money = money
    else:
        final_money = shares*(df["Close"][-1])
    #We calculate the percentaje of profitability
    percentage = ((final_money/invest_money) - 1)*100
    round_percentage = round(percentage, 2)
    real_profitability = ((df["Close"][-1]/df["Close"][0]) - 1)*100 
    real_profitability_r = round(real_profitability,2)
    shares1= invest_money/df["Close"][0]
    shares_r = round(shares1, 2)
    profit= shares1* df["Close"][-1]
    profit_r = round(profit,2)
    hold_profit = round((profit_r-invest_money),2)
    final_money= round(final_money,2)
    MACD_profit = round((final_money-invest_money),2)

    st.header('Results using MACD model.')
    col1, col2= st.columns(2)
    col1.metric(label="Final money using MACD", value= (str(final_money)+' $') , delta= (str(MACD_profit)+' $'))
    col2.metric(label="Percentage of win/loss MACD", value= (str(round_percentage)+' %'))

    st.header('Results by holding.')
    col1, col2, col3= st.columns(3)
    col1.metric(label=f"Amount of {crypto1} bought", value= shares_r )
    col2.metric(label="Final money by holding", value= (str(profit_r)+' $') , delta= (str(hold_profit)+' $'))
    col3.metric(label="Percentage of win/loss holding", value= (str(real_profitability_r)+' %'))




