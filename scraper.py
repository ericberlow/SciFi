from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import csv
import json
import lxml

def fetch_scifi_novels(page_num):
    print("Fetching top level page ", str(page_num))
    base_url = "http://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books"
    page_url = base_url + "?page=" + str(page_num)
    r = requests.get(page_url)
    soup = BeautifulSoup(r.content, "lxml")
    # Returns BeautifulSoup object for the first 
    return(soup)
    
# Extract list of book URL's from a single page from "Best Science Fiction & Fantasy Books" list
def parse_book_urls_from_page(current_page):
    current_page_books = current_page.find_all('a', attrs={'class': 'bookTitle'})
    
    # Parse the Goodreads book URL's and append to this list:
    current_page_book_links = []

    for book_a in current_page_books:
        link = book_a.get('href')
        full_link = "http://www.goodreads.com" + link
        current_page_book_links.append(full_link)
    # Returns list of book URLS.
    return(current_page_book_links)
    
# Helper function, used within parse_books()
def parse_genre_page(genre_url):
    r = requests.get(genre_url)
    soup = BeautifulSoup(r.content, "lxml")
    tagged_genres = soup.find_all('a', attrs={'class': 'mediumText actionLinkLite'})
    genre_names = []
    genre_urls = []
    for genre_html in tagged_genres:
        genre_name = genre_html.text
        genre_names.append(genre_name)
        genre_url = "http://www.goodreads.com" + genre_html['href']
        genre_urls.append(genre_url)
    genre_dict = {}
    genre_dict["names"] = genre_names
    genre_dict["urls"] = genre_urls
    return(genre_dict)

# To test a quick example using parse_genre_page(), uncomment the following code:
# parse_genre_page("https://www.goodreads.com/work/shelves/2422333")

# Fetch all of the interesting info for a <list> of book URLs.
def parse_books(book_urls):
    counter = 0
    num_books = len(book_urls)
    all_books_info = []
    time.sleep(2)
    for b_url in book_urls:
        final_book_info = {}
        # How many more books left?
        counter += 1
        print("Fetching Book ", str(counter), " of ", str(num_books))

        # Make request to the book page and parse using BeautifulSoup
        r = requests.get(b_url)
        soup = BeautifulSoup(r.content, "lxml")

        # Start grabbing stuff!
        # Book Title!
        title_soup = soup.find('h1', attrs={'id': 'bookTitle'})
        book_title = title_soup.text.replace("\n", "").replace("   ", "")

        # Number of total ratings (0-5 stars)! Strip new-line characters + extraneous whitespace
        num_ratings = soup.find('span', attrs={'class': "votes value-title"}).text.strip()
        # Convert '100,000' to 100000
        fmtd_num_ratings = num_ratings.replace(',', '')

        # Tagged Genres
        top_genres = {}
        tagged_genre_html = soup.find_all('a', attrs={'class': 'bookPageGenreLink__seeMoreLink'})
        if len(tagged_genre_html) > 0:
            tagged_genre_page_url = "http://www.goodreads.com" + tagged_genre_html[0].get('href')
            top_genres = parse_genre_page(tagged_genre_page_url)

        # Reviews
        # Number of total reviews. Strip new-line characters + extraneous whitespace
        num_reviews = soup.find('span', attrs={'class': "count value-title"}).text.strip()
        # Convert '100,000' to 100000
        fmtd_num_reviews = num_reviews.replace(',', '')

        # Reviews from the first page!
        book_reviews = []
        all_spans = soup.find('div', attrs={'id': 'bookReviews'}).find_all('span')

        for sp in all_spans:
            sp_id = sp.get('id')
            if sp_id and sp_id.startswith('freeText'):
                book_reviews.append(sp.text)
        ###########
                
        # Plot
        s = soup.find("div", {"id": "descriptionContainer"})
        
        plot = "NaN"
        if len(s.find_all("span")) == 1:
            plot = s.find_all("span")[0].text
        if len(s.find_all("span")) == 2:
            plot = s.find_all("span")[1].text

        # Author
        author = "NaN"
        author_block_one = soup.find("div", {"id": "aboutAuthor"})
        author_block_two = soup.find("a", class_="authorName")
        
        if author_block_one:
            author = author_block_one.find("div").text.lstrip("About").lstrip()
        if author_block_two:
            author = author_block_two.text

        # Published
        publisher_block = soup.find_all("div", class_="row")

        publisher_text = "NaN"
        if len(publisher_block) > 1:
            publisher_text = publisher_block[1].text.replace("\n", "").replace("  ", "")
        elif len(publisher_block) == 1:
            publisher_text = publisher_block[0].text.replace("\n", "").replace("  ", "")
        
        book_info = {}
        book_info["url"] = b_url
        book_info["plot"] = plot
        book_info["author"] = author
        book_info["published"] = publisher_text
        
        ###########
        book_info["ratings"] = {}
        # Add number of user ratings (0-5 stars)
        book_info["ratings"]["number"] = fmtd_num_ratings
        book_info["reviews"] = {}
        # Add number of reviews
        book_info["reviews"]["number"] = fmtd_num_reviews
        # Add list of reviews
        book_info["reviews"]["list_of_reviews"] = book_reviews
        # Add genres
        book_info["genres"] = top_genres
        
        ##########
        book_info["url"] = b_url
        book_info["plot"] = plot
        book_info["author"] = author
        book_info["published"] = publisher_text
        ##########

        # Assign nested dictionary containing the book's info to the final dict to return.
        final_book_info[book_title] = book_info
        
        # Add to the final dictionary to be converted to JSON and dumped out to a file.
        all_books_info.append(final_book_info)
        
    return(all_books_info)

## Glue Code To Download All The Data
for i in range(0,63):
    page_soup = fetch_scifi_novels(i)
    page_links = parse_book_urls_from_page(page_soup)
    final_results = parse_books(page_links)
    filename = "page_" + str(i) + ".json"

    with open(filename, "w") as f:
        json.dump(final_results, f, indent=2)
        
import os, json
## Data count dictionary

counts = {
    "url": 0,
    "plot": 0,
    "author": 0,
    "published": 0,
    "ratings": 0,
    "reviews": 0,
    "genres": 0
}

for i in range(0, 64):
    data = json.load(open('page_' + str(i) + '.json'))
    for book in data:
        book_key = list(book.keys())[0]
        book_key_list = book[book_key].keys()
        for deep_key in book_key_list:
            if book[book_key][deep_key] != "NaN":
                counts[deep_key] += 1