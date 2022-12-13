# Nero-Search-Engine-Project  
This is a search engine I developed for my Search Engine Technology class. It searches through a corpus of 36,804 json file documents from national park dataset and 4000 json documents from major league baseball dataset.  

The search engine can find single word queries, multiple words and phrases queries. 

# What queries to search?  
The project runs in two modes: Ranked Retrieval and Boolean Retrieval. It further gives the user to build a new index or query an existing one by passing the path to directory.  

### Ranked Retrieval ###  
Simply enter words separated by space as in google search bar.  Results are ranked by relevace to the query issued. Top 10 most relevant documents are returned.  
Sample query for ranked retrieval:  
+ fires in yosemite  

### Boolean Retrieval ###  
Enter words separated by space (AND), plus operator (+) (OR), enclosed in " " (phrase queries), enclosed in [ ] with NEAR operator.     
Sample queries for boolean retrieval:  
+ AND => coral reef  ---> returns documents containing coral AND reef.  
+ OR  => coral+reef  ---> returns documents containing coral OR reef but not both.  
+ " " => "national preserve" ---> returns documents containing the entire phrase "national preserve"  
+ NEAR => [tallgrass NEAR/3 preserve] ---> returns documents containing tallgrass and preserve separated by 3 or less words in the given order.  

# How to run the project? 
Run the termdocumentindexer.py file and follow the instructions on the terminal.   
Path => Give path to the corpus files (not corpus folder)  
