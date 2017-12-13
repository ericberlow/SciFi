# SciFi
Create network of sci fi novels linked by shared concepts mentioned in the reviews.  

SciFi novels - Title, metadata, and text of all reviews/comments were scraped from Good Reads by Srini Kadamti.

Dictionary of important concepts and search terms to map onto those concepts was created by Bethanie Maples.

The tag enhancement and network generation was done with Tag2Network created by Rich Williams: https://github.com/foodwebster/tag2network 

Tag2Network adds tags from a dictionary by searching through the text of all reviews/comments for search terms in the dictionary and adds the mapped concepts as a tag if present. Then novels are then  linked if they share similar keyword sets. 
