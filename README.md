# UFC Stats Scraper
A Python-based web scraper that collects detailed UFC fight statistics from [ufcstats.com](http://ufcstats.com) and saves them to CSV files.

## Description
This project captures:
- Round-by-round fight statistics
- Fighter attributes and overall statistics
- Fight summaries including winner, method, round, and more

All data is up-to-date as of **16/04/2025**.

## Known issues
Currently, there's no automatic update functionality for:
- New fights
- New fighters added to the roster
- Updates to fighters' average stats after recent events

**Temporary solution**: Re-run the scripts after each UFC event.  
Note: `ufc_scraping.py` takes approximately **30 minutes** to run.

## libraries
- `requests`
- `BeautifulSoup`
- `pandas`
- `fake_useragent`
- `random`
- `time`
- `string`
- `concurrent.futures.ThreadPoolExecutor`

## Authors
**Joel Kennerley**  

 If you have any questions or would like to provide feedback you can email me at 
 joel_kennerley@hotmail.com

 
