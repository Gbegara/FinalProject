import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader as web
import yfinance as yf 
import math

def app():
    st.title('Neural network prediction')
    df = web.DataReader("ETH-USD", data_source="yahoo", start="2021-03-22", end="2022-04-22")
    st.subheader('Price of ETH from 22/03/21 to 22/04/2022')
    fig= plt.figure(figsize=(16,8))
    plt.title("Ethereum Closing Price ($)")
    plt.plot(df["Close"])
    plt.xlabel("Date", fontsize = 18)
    plt.ylabel("Close Price USD ($)", fontsize = 18)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    df.index = pd.to_datetime(df.index)
    
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    #train_series = scaler.fit_transform(train_series)
    df['Close'] = scaler.fit_transform(df[['Close']])
    
    train_data = df.query('Date <  "2022-01-22"').reset_index(drop = False) 
    test_data  = df.query('Date >= "2022-01-22"').reset_index(drop = False)
    
    X_train = train_data.Date
    y_train = train_data['Close']

    X_test = test_data.Date
    y_test = test_data['Close']

    n_features = 1

    train_series = y_train.values.reshape((len(y_train), n_features))
    test_series  = y_test.values.reshape((len(y_test), n_features))
    
    
    from keras.preprocessing.sequence import TimeseriesGenerator

    look_back = 20

    train_generator = TimeseriesGenerator(train_series, train_series,
                                          length        = look_back, 
                                          sampling_rate = 1,
                                          stride        = 1,
                                          batch_size    = 10)

    test_generator = TimeseriesGenerator(test_series, test_series,
                                          length        = look_back, 
                                          sampling_rate = 1,
                                          stride        = 1,
                                          batch_size    = 10)
    from keras.models import Sequential
    from keras.layers import Dense
    from keras.layers import LSTM

    n_neurons  = 4
    model = Sequential()
    model.add(LSTM(n_neurons, input_shape=(look_back, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse');

    model.fit(train_generator,epochs=300, verbose=0);
    
    test_predictions  = model.predict(test_generator)
    st.subheader('Price predictions of ETH from 22/03/21 to 22/04/2022')
    fig= plt.figure(figsize=(20,6))
    plt.plot(test_data.Date, test_data['Close'], c='orange',label='true values')
    plt.plot(X_test[20:],test_predictions, lw=3, c='r',linestyle = '-', label='predictions')
    plt.legend(loc="lower left")
    plt.xlabel("date", fontsize=16)
    plt.ylabel("Close price (EUR) (escaled)", fontsize=16)
    plt.title("ETH Closing value", fontsize=16)
    st.pyplot(fig)
    
    n_days = 20
    last_n_days = len(test_data)-n_days
    st.subheader('Looking close into it (20 days)')
    fig= plt.figure(figsize=(15,5))
    plt.plot(test_data.Date[last_n_days:], test_data['Close'][last_n_days:], c='orange',marker='o',label='true values')
    plt.plot(X_test[last_n_days:],test_predictions[last_n_days-20:],lw=1, c='r', marker='o', label='predictions')
    plt.legend(loc="upper left")
    plt.xlabel("date", fontsize=16)
    plt.ylabel("Close price (EUR) (escaled)", fontsize=16)
    plt.title("ETH Closing value", fontsize=16)

    # shade in the days for better visualization
    date2 = df.tail(1).index.item()
    date1 = date2 - pd.Timedelta(days=n_days+7) # days added for weekends etc.
    for i in pd.date_range(date1, date2, periods=n_days+8):
        # shade in 0.6 of each day
        plt.axvspan(i,i+pd.Timedelta(days=0.6), facecolor='lightgrey', alpha=0.2)
    st.pyplot(fig)
    
    
    
    extrapolation = list()
    seed_batch    = y_test[:look_back].values.reshape((1,look_back, n_features))
    current_batch = seed_batch

    for i in range(len(test_data)):
        predicted_value = model.predict(current_batch)[0]
        extrapolation.append(predicted_value) 
        current_batch = np.append(current_batch[:,1:,:],[[predicted_value]],axis=1)
        
    st.subheader('Using predicted values')
    fig= plt.figure(figsize=(20,5))
    plt.plot(test_data.Date, test_data['Close'], c='orange',label='true values')
    plt.plot(X_test[20:],extrapolation[20:], lw=3, c='r',linestyle = '-', label='predictions')
    plt.legend(loc="lower left")
    plt.xlabel("date", fontsize=16)
    plt.ylabel("Close price (EUR) (scaled)", fontsize=16)
    plt.title("ETH Closing value", fontsize=16)
    st.pyplot(fig)
        
    

    

    






