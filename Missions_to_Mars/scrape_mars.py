# Start mongodb with this command before running this code: 
# mongod --config /usr/local/etc/mongod.conf

from splinter import Browser
from bs4 import BeautifulSoup as bs
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import time


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_mars_news():
    browser = init_browser()

    # Visit https://mars.nasa.gov/news/
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    # Give time for dynamic content to load
    time.sleep(10)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")
    #DEBUG print(soup.prettify())
    #DEBUG list(soup.children)

    # Get the title
    scrape_title = soup.find(class_='content_title')
    title = scrape_title.find_all('a')[0].text

    # Get the teaser
    scrape_teaser = soup.find('div', class_='article_teaser_body')
    teaser = scrape_teaser.get_text()

    # Store data in a dictionary
    mars_news = {
        "title": title,
        "teaser": teaser
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_news


# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_news")

# Route to render mars_news.html template using data from Mongo
@app.route("/")
def home():

    # Find one record of data from the mongo database
    #destination_data = mongo.db.collection.find_one()
    mars_news = mongo.db.collection.find_one()

    # Return template and data
    blah = ''
    return render_template("index.html", mars_news=mars_news, blah=blah)

# Route that will trigger the mars_news function
@app.route("/scrape")

def scrape():

    # Run the mars_news function
    mars_news_data = scrape_mars_news()

    # Update the Mongo database using update and upsert=True
    mongo.db.collection.update({}, mars_news_data, upsert=True)

    # Redirect back to home page
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)

