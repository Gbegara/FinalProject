import streamlit as st
from multiapp import MultiApp
from Apps import MACD_analysis, Neural_network_model, OBV_analysis, Comparing_MACD_OBV # import your app modules here

app = MultiApp()
st.set_page_config(
     page_title="Crypto Analysis",
     page_icon="chart_with_upwards_trend")
st.markdown("""
# Price Predictor and Models to analyse Cryptos

This is a web to check how neural networks model predictor works on crpyto-currencies and you can also use analysis for any crypto in the world with two different models. The first model is MACD and the second one OVB. For both models there is a simulator of investment in order to find the strategy that best fits your needs.

""")
from PIL import Image
image = Image.open('crypto-image.png')
st.image(image)

# Add all your application here
app.add_app("MACD", MACD_analysis.app)
app.add_app("OBV", OBV_analysis.app)
app.add_app("Comparing MACD & OBV", Comparing_MACD_OBV.app)
app.add_app("Neural network model", Neural_network_model.app)

# The main app
app.run()





