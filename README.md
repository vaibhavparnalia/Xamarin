Xamarin
=======
Written in Python 3.4.2

Search online for a list of Now Showing movies.
Returns the movie info, casts and their average age.

Each time it queries a movie/cast, it saves the html on the filer.

Benchmark/movie:
  If movie is not on the filer, query takes about 30-40 seconds which includes querying about 30 credited casts.
  If the movie is on the filer, the result takes ~0.15 seconds to generate

Changes in source(IMDb/..):
	Important things are stored in global.py. Developer should put as many thing as possible here, for easy debug when the source data format changes.
	There is no SOAP service used here, but if we use those, we should still have HTML parsing as backup and inform to upgrade the SOAP query

TODO:
	Using SOAP servies to get the celebrity data and also keep parsing IMDb HTML as secondary
		Pros:
      Easy parsing
      More stable with change in website
      Maybe faster
    Cons:
      Less reliable(downtime, discontinuation)
      
  Saving the cast info(Name/DOB) in dictionaries in json.dumps
    Pros:
      Saves disk space(Querying 60 movies had 1600 unique casts and hence html files)
      Faster than opening the html and querying
      
Usage:
  Run __main__.py
