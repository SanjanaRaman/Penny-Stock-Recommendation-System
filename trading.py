from firebase import firebase
import praw
import robin_stocks as r

reddit = praw.Reddit(client_id='fDXqnKGkSXIOAg',
                     client_secret='7MhjUMFoE7bDpIF-1KGuuHLhtRc',
                     user_agent='python:trading.py:v3.7.3 (by /u/sanjanaraman')

#check if title of reddit post consists of uppcase letters (indicating ticker symbol)
def upperwords(s):
    text = s.split()
    i = 0
    toprint = ""
    arrayoftickers = []
    while i < (len(text)):
        if text[i].isupper() == True:
            toprint = text[i]
            if (toprint[0] == "$" or toprint[0] == "“" ):
                toprint = toprint[1:]
            if (toprint[len(toprint)-1] == "." or toprint[len(toprint)-1] == "?" or toprint[len(toprint)-1] == "!" or toprint[len(toprint)-1] == "\""):
                toprint = toprint[:-1]
            if (len(toprint) < 2 or len(toprint) > 4):
                toprint = ""
            if (len(toprint)>0):
                return toprint
        i = i + 1
        toprint = ""

        #6. fix sentiment analyses


firebase = firebase.FirebaseApplication('https://tradingapp-4cbce.firebaseio.com/', None)

for submission in reddit.subreddit('robinhoodpennystocks').stream.submissions():
    #Get possible tickers from submission title
    potentialticker = upperwords(submission.title)
    if (potentialticker != None):
        #Test if potential ticker exists in RobinHood database
        try:
            r.stocks.get_name_by_symbol(potentialticker)
            ticker = potentialticker
            name = r.stocks.get_name_by_symbol(ticker)
            #Check if ticker exists in database, and if so pulls current rating from there
            try:
                temporarycount = firebase.get('/stocks', name)
                count = temporarycount.get('number', None)
            #Creates new rating system if ticker does not exist
            except:
                count = 0
            #Runs text sentiment analysis on submission title
            if (submission.title.__contains__("up")):
                count = count + 1;
            elif (submission.title.__contains__("down")):
                count = count - 1;
            #Runs text sentiment analysis on comments within a submission    
            for comment in submission.comments:
                if (comment.body.__contains__("up")):
                    count = count + 1;
                elif (comment.body.__contains__("down")):
                    count = count - 1;
            #Decide whether to buy, hold, or sell
            if (count == 0):
                rating = "HOLD"
            if (count > 0):
                rating = "BUY"
            if (count < 0):
                rating = "SELL"
            #Add new or updated rating to database
            firebase.put('/stocks', name, {'name': name, 'number': count, 'rating': rating, 'ticker': ticker})
        #Ticker does not exist in RobinHood
        except:
            potentialticker = ""
