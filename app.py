import streamlit as st # for overall GUI
from streamlit_calendar import calendar # to show calendar
from dateutil.relativedelta import relativedelta # for addition to dates
import datetime
import os # for extracting environment variable
from urllib.request import urlopen # for getting data from FMP API
import json # for parsing data from FMP API




tickers = ['ABNB','AMD','CEG','AMZN','AMGN','AEP','CDW','CCEP',
          'ADI','MDB','DASH','ROP','ANSS','SPLK','AAPL','AMAT',
          'GEHC','ASML','TEAM','ADSK','ADP','AZN','BKR','AVGO',
          'BIIB','BKNG','CDNS','ADBE','CHTR','CPRT','CSGP','CRWD',
          'CTAS','CSCO','CMCSA','COST','CSX','CTSH','DDOG','DXCM',
          'FANG','DLTR','EA','ON','EXC','TTD','FAST','GFS','META',
          'FI','FTNT','GILD','GOOG','GOOGL','HON','ILMN','INTC',
          'INTU','ISRG','MRVL','IDXX','KDP','KLAC','KHC','LRCX',
          'LULU','MELI','MAR','MCHP','MDLZ','MRNA','MNST','MSFT',
          'MU','NFLX','NVDA','NXPI','ODFL','ORLY','PCAR','PANW',
          'PAYX','PDD','PYPL','PEP','QCOM','REGN','ROST','SIRI',
          'SBUX','SNPS','TSLA','TXN','TMUS','VRSK','VRTX','WBA',
          'WBD','WDAY','XEL','ZS'
        ]


# For parsing data from API from JSON to a Python Dictionary
def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

# Get FMP API stored as environment variable
apiKey = st.secrets['FMP_KEY']

# Financialmodelingprep (FMP) api base url
base_url = "https://financialmodelingprep.com/api/v3/"


# Get today's date and add 3 months to it
# Convert both today's date and the 3 months later date to strings (for input into API endpoint URL later)
# This is the date range within which we want to get our earnings dates 
today = datetime.datetime.today()
today_string = today.strftime('%Y-%m-%d')
start_string_past = (today + relativedelta(months=-3)).strftime('%Y-%m-%d')

start_string = (today + relativedelta(months=-1)).strftime('%Y-%m-%d')
future_string = (today + relativedelta(months=3)).strftime('%Y-%m-%d')

# This is the full API endpoint to get the earnings dates from today to 6 months after
url = f"{base_url}earning_calendar?from={start_string}&to={future_string}&apikey={apiKey}"


url2 = f"{base_url}earning_calendar?from={start_string_past}&to={today_string}&apikey={apiKey}"

# This decorator ensures that the call to the FMP API will only run once at the start of this app
# The data returned will be cached after the function runs
# Without this decorator, the API will be called each time you click something in the streamlit app
@st.cache_resource
def get_earnings_dates(url):
    events = get_jsonparsed_data(url)
    return events


@st.cache_resource
def get_transcripts(url):
    events = get_jsonparsed_data(url)
    return events


events = get_earnings_dates(url)

#events2 = get_earnings_dates(url2)


#events = events + events2

transcripts_data=[]
with st.sidebar:
    st.title("Earnings Calendar")
    st.header("Generate Transcripts")
   
    
    # For users to enter tickers of interest
    single_ticker = st.text_area('Enter Ticker to View Transcipt History', 
                                value = "")
    
    transcript_year = st.number_input("What Year?", value= 2023)


    st.write('')
    if st.button('Run'):
        # Call the get_jsonparsed_data function
        transcripts_url = f"https://financialmodelingprep.com/api/v4/batch_earning_call_transcript/{single_ticker}?&year={transcript_year}&apikey={apiKey}"


        transcripts_data = get_transcripts(transcripts_url)
        # Display the JSON data
        
    
    st.write('')


   
# Parse user input into a list
#tickers_string = tickers.replace(' ', '')
#tickers = tickers_string.split(',')

# Converts the parsed json from FMP API into a list of events to be passed into streamlit_calendar
calendar_events = []
for event in events:
    if event['symbol'] in tickers:
        #print(event)
        calendar_event = {}
        calendar_event['title'] = event['symbol'] + ":" + str(event["epsEstimated"])
        if event['time'] == 'bmo': # before market opens, add sunrise symbol
            calendar_event['title'] = '☀ ' + calendar_event['title']
        elif event['time'] == 'amc': # after market closes, add sunset symbol
            calendar_event['title'] = '🌅 '   + calendar_event['title']     
        calendar_event['start'] = event['date']
        calendar_events.append(calendar_event)

st.header("Earnings Calendar")


calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridWeek,dayGridMonth,listMonth",
        },
        #"initialDate": today.strftime('%Y-%m-%d'),
        "initialView": "dayGridMonth"
    }
    

custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""


calendar = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)

st.header("Transcripts")

st.json(transcripts_data, expanded= False)