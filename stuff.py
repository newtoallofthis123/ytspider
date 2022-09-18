import requests
import string
from datetime import datetime, date
import json

def hash_gen_engine():
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    whole =  lower + upper + digits
    hash_string = random.sample(whole, 8)
    hash = "".join(hash_string)
    return hash

def time_cal():
    current_t = datetime.now()
    current_date = str(date.today())
    current_t_f = current_t.strftime("%H:%M:%S")
    timeAnddate = (f'{current_t_f} {current_date}')
    return timeAnddate

def ran_quote():
    quotes_page = json.loads(requests.get("https://api.quotable.io/random").content)
    quote_list = [quotes_page["content"], quotes_page["author"]]
    return quote_list

def ran_fact():
    fact_page = json.loads(requests.get("https://useless-facts.sameerkumar.website/api").content)
    fact = fact_page["data"]
    return fact

def tinyurl(url):
    tinyurl_page = str(requests.get(f'https://tinyurl.com/api-create.php?url={url}').content).replace("b'", "").replace("'", "")
    return tinyurl_page