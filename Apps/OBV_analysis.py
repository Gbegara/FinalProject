import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader as web
import yfinance as yf 
import math
import streamlit as st
import datetime

def app():

    st.title('Crypto OBV Analysis')


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
    fig = plt.figure(figsize=(12.2, 4.5))
    plt.plot(df["Close"], label = "Close")
    plt.title("Close Price")
    plt.xlabel("Date", fontsize = 18)
    plt.ylabel("Price USD", fontsize = 18)
    st.pyplot(fig)

    OBV = []
    OBV.append(0)

    #Loop through the data set from the second row (index1) to the end of the data set
    for i in range(1, len(df.Close)):
        if df.Close[i] > df.Close[i-1]:
            OBV.append(OBV[-1] + df.Volume[i])
        elif df.Close[i] < df.Close[i-1]:
            OBV.append(OBV[-1] - df.Volume[i])
        else:
            OBV.append(OBV[-1])
    #Store the OBV and the Exponential Moving Average into new columns
    df["OBV"] = OBV
    df["OBV_EMA"] = df["OBV"].ewm(span=20).mean()


    st.subheader(f'OVB and signal for {crypto1} over time')
    fig=plt.figure(figsize=(12.2, 4.5))
    plt.plot(df["OBV"], label = "OBV", color = "orange")
    plt.plot(df["OBV_EMA"], label = "OBV_EMA", color = "purple")
    plt.title("OBV")
    plt.xlabel("Date", fontsize = 18)
    plt.xticks(rotation = 45)
    st.pyplot(fig)


    def buy_sell(signal, col1, col2):
        sigPriceBuy = []
        sigPriceSell = []
        flag = -1
        #Loop through the lenght of the data set
        for i in range(0, len(signal)):
            #IF OBV > OBV_EMA then Buy
            if signal[col1][i] > signal[col2][i] and flag != 1:
                sigPriceBuy.append(signal["Close"][i])
                sigPriceSell.append(np.nan)
                flag = 1
            #If OBV < OBV_EMA then sell
            elif signal[col1][i] < signal[col2][i] and flag != 0:
                sigPriceSell.append(signal["Close"][i])
                sigPriceBuy.append(np.nan)
                flag = 0
            else:
                sigPriceSell.append(np.nan)
                sigPriceBuy.append(np.nan)
        return (sigPriceBuy, sigPriceSell)

    x = buy_sell(df, "OBV", "OBV_EMA")
    df["Buy_Signal_Price"] = x[0]
    df["Sell_Signal_Price"] = x[1]

    st.subheader(f'Buy and sell calls for {crypto1} over time')
    fig= plt.figure(figsize=(12.2, 4.5))
    plt.plot(df["Close"], label = "Close", alpha = 0.35)
    plt.scatter(df.index, df["Buy_Signal_Price"], label = "Buy Signal", marker =  "^", alpha = 1, color = "green")
    plt.scatter(df.index, df["Sell_Signal_Price"], label = "Sell Signal", marker = "v", alpha = 1, color = "red")
    plt.title(f"{crypto1} Buy and Sell Signals")
    plt.xlabel("Date", fontsize = 18)
    plt.ylabel("Price USD", fontsize = 18)
    plt.legend(loc = "upper left")
    st.pyplot(fig)


    measure = df[["Buy_Signal_Price", "Sell_Signal_Price"]]
    measure["Buy_0"] = measure["Buy_Signal_Price"].fillna(0)
    measure["Sell_0"] = measure["Sell_Signal_Price"]. fillna(0)
    measure.drop("Buy_Signal_Price", axis = 1, inplace=True)
    measure.drop("Sell_Signal_Price", axis = 1, inplace=True)
    
    money = invest_money
    shares = invest_money/df["Close"][0]
    for i in range(0, (len(measure["Buy_0"] + 1))):
        if measure["Buy_0"][i] == 0 and measure["Sell_0"][i] == 0:
            pass
        elif measure["Buy_0"][i] != 0:
            shares = money/measure["Buy_0"][i]
        elif measure["Sell_0"][i] != 0:
            money = shares*measure["Sell_0"][i]
    print(f"Final {money} $ if a sell was the last movement")
    print(f"Final {shares} shares if a buy was the last movement")
    
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
    OBV_profit = round((final_money-invest_money),2)

    st.header(f'Results using OBV model on {crypto1}.')
    col1, col2= st.columns(2)
    col1.metric(label="Final money using OBV", value= (str(final_money)+' $') , delta= (str(OBV_profit)+' $'))
    col2.metric(label="Percentage of win/loss OBV", value= (str(round_percentage)+' %'))

    st.header('Results by holding.')
    col1, col2, col3= st.columns(3)
    col1.metric(label=f"Amount of {crypto1} bought", value= shares_r )
    col2.metric(label="Final money by holding", value= (str(profit_r)+' $') , delta= (str(hold_profit)+' $'))
    col3.metric(label="Percentage of win/loss holding", value= (str(real_profitability_r)+' %'))




