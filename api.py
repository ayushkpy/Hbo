import requests as r
import time 

def check(cc):
    try:
        num,mm,yy,cvc = cc.split('|')
        if "20" not in yy:
            yy = f"20{yy}"
        check = r.get(f"https://darkboyccapi.onrender.com/key=dark/cc={num}|{mm}|{yy}|{cvc}") 
        return check.json()
    except:
        return("Error While Checking")                  
        
def braintree_auth(cc):
    time.sleep(3)
    response = check(cc)
    if response['status'] == "Approved":
        return "Approved ✅"
    elif response['status'] == "Declined":
        return "Your card was declined"
    else:
        return "Error While Checking"                  