from dotenv import load_dotenv, find_dotenv
import os
import re
import pandas as pd
from pymongo import MongoClient
import requests as req
from bs4 import BeautifulSoup
import streamlit as st

load_dotenv(find_dotenv())

pw = os.environ.get("MONGODB_PW")
uri = f"mongodb+srv://rabbanikhan2001:{pw}@propertypulse.sb5xc.mongodb.net/propertypulse_db"
client = MongoClient(uri)

db = client["propertypulse_db"]
collection = db["properties"]

st.title('Auction Parser')

cities = ["Manchester", "Birmingham"]
selected_city = st.selectbox('Select a town', cities)
base_url = "https://www.auctionhouse.co.uk"
target_url = f"/{selected_city}/auction/search-results" if selected_city != "All" else "/auction/search-results"

response = req.get(base_url + target_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    st.write(f'Count db documents: {collection.count_documents({})}')

    results = []
    
    properties = soup.find_all('div', class_='lot-search-result')
    for p in properties:
        info = p.find('div', class_='summary-info-wrapper')
        if info:
            lot_info = info.find_all('p')
            if len(lot_info) >= 2:
                lot_details = lot_info[0].get_text(strip=True)
                address = lot_info[1].get_text(strip=True)
                
        price_div = p.find_all('div', class_='lotbg-residential')
        for p in price_div:
            price = p.get_text(strip=True)
            if "£" in price and re.search(r'\d', price):
                numeric_price = re.sub(r'[^\d,]', '', price)

        # link_tag = p.find_all('a')
        # for l in link_tag:
        #     if l and 'href' in l.attrs:
        #         if 'https:' in l['href']:
        #             property_link = l['href']
        #         else:
        #             property_link = base_url + l['href']

        property_info = {
            "title": lot_details,
            "address": address,
            "price": numeric_price,
            # "href_url": property_link
        }
        
        collection.insert_one(property_info)
        results.append(property_info)
                

    # df = pd.DataFrame(results)
    # st.dataframe(df)
    st.write(results)

else:
    st.error(f'Error status code: {response.status_code}')



# TEMPLATE
# <div class="col-sm-12 col-md-8 col-lg-6 text-center lot-search-result">
# <a class="home-lot-wrapper-link" href="/manchester/auction/lot/132840" target="" title="View property details">
# <div class="lot-search-wrapper grid-item">
# <div class="image-wrapper">
# <img alt="Property for Auction in Manchester - 3 Cheadle Street, Manchester, M11 1AG" class="lot-image" loading="lazy" src="/lot-image/686026"/>
# <div class="image-sticker lotbg-residential">
# 						Lot 1
# 					</div>
# </div>
# <div class="lotbg-residential text-white grid-view-guide">
# 				Sold £137,000
# 			</div>
# <div class="summary-info-wrapper">
# <p>2 Bed Terraced House</p>
# <p>3 Cheadle Street, Manchester, M11 1AG</p>
# </div>
# </div>
# </a>
# </div>