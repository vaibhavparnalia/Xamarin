from globals import *
import datetime
import urllib.request
from html.parser import HTMLParser

##TODO
#Check the HTML_cache before querying :)

class MyHTMLParser(HTMLParser):
    def __init__(self):
        #http://stackoverflow.com/questions/3276040/how-can-i-use-the-python-htmlparser-library-to-extract-data-from-a-specific-div
        HTMLParser.__init__(self)
        self.parsedAttrs = {}
        self.parsedAttrs["genre"] = []

    def handle_starttag(self, tag, attrs):
        #print("Start tag:", tag)
        #for attr in attrs:
        #    print("     attr:", attr)
        if tag == "time":
            #self.parsedAttrs.append(("dateTime", attrs[1][1]))
            self.parsedAttrs["dateTime"] = attrs[1][1]
        if tag == "a" and "genre" in attrs[0][1]:
            #self.parsedAttrs.append(("genre", attrs[0][1]))
            self.parsedAttrs["genre"].append(attrs[0][1])
        if tag == "meta" and "datePublished" in attrs[0][1]:
            #self.parsedAttrs.append(('datePublished', attrs[1][1]))
            self.parsedAttrs["datePublished"] = attrs[1][1]
        if tag == "meta" and "og:title" in attrs[0][1]:
            #self.parsedAttrs.append(('title', attrs[1][1]))
            self.parsedAttrs['title'] = attrs[1][1]

    def handle_endtag(self, tag):
        #print("End tag  :", tag)
        pass
    def handle_data(self, data):
        #print("Data     :", data)
        pass
    def handle_comment(self, data):
        #print("Comment  :", data)
        pass

class movie:
    def __init__(self, imdbID):
        self.id = imdbID
        self.title = ""
        self.runTime = "00000000"
        self.genre = []
        self.releaseDate = "0000-01-01"
        self.cast = []
        
def HTMLResponse(url):
    page = urllib.request.urlopen(url)
    return page.read()

def filterMovieID(file):
    movieID = []
    with open(file, "r", encoding="utf8") as file:
        for line in iter(file):
            if "/showtimes/title/" in line:
                if "tt" in line:
                    indexStart = line.index("tt")
                    indexEnd = indexStart + line[indexStart:].index('/')
                    if line[indexStart:indexEnd] not in movieID:
                        movieID.append(line[indexStart:indexEnd])
    return movieID
    
def getNowShowing():
    page_content = HTMLResponse(nowShowingURL)
    
    with open("html_cache/now_showing.html", "wb") as file:
        file.write(page_content)
    file.close()
    return filterMovieID("html_cache/now_showing.html")

def initDatabase(movieList):
    nowShowing = []
    [nowShowing.append(movie(movieID)) for movieID in movieList]
    return nowShowing

def convertDate(myDate):
    return datetime.date(int(myDate.split("-")[0]), int(myDate.split("-")[1]), int(myDate.split("-")[2])).strftime("%d %B %Y")

def getGenreStr(genreList):
    genreStr = ""
    for genreType in genreList:
        genreStr = genreStr + genreType + ", "
    return genreStr[:-2]

def printMovieInfoDetailed(nowShowing):
    for i in range(0, len(nowShowing)):
        if len(nowShowing) < 10:
            print("{}. {}".format(i+1, nowShowing[i].title))
            print("    RunTime: {}".format(nowShowing[i].runTime[2:]))
            print("    Genre: ", end="")
            genreStr = getGenreStr(nowShowing[i].genre)
            print("{}".format(genreStr))
            dateStr = convertDate(nowShowing[i].releaseDate)
            print("    Date Released: {}".format(dateStr))

        elif len(nowShowing) < 100:
            print("{:2d}. {}".format(i+1, nowShowing[i].title))
            print("    RunTime: {}".format(nowShowing[i].runTime[2:]))
            print("    Genre: ", end="")
            genreStr = getGenreStr(nowShowing[i].genre)
            print("{}".format(genreStr))
            dateStr = convertDate(nowShowing[i].releaseDate)
            print("    Date Released: {}".format(dateStr))
                      
        else:
            print("{:3d}. {}".format(i+1, nowShowing[i].title))
            print("    RunTime: {}".format(nowShowing[i].runTime[2:]))
            print("    Genre: ", end="")
            genreStr = getGenreStr(nowShowing[i].genre)
            print("{}".format(genreStr))
            dateStr = convertDate(nowShowing[i].releaseDate)
            print("    Date Released: {}".format(dateStr))

def movie_setParameters(nowShowing):
    print("Found {} movies in theaters..".format(len(nowShowing)))
    #print([movie.id for movie in nowShowing])

    for movie in nowShowing:
        print("Querying {}".format(movie.id))
        page_content = HTMLResponse(moviePageURL+movie.id)

        with open("html_cache/"+movie.id+".html", "wb") as file:
            file.write(page_content)
        file.close()

        with open("html_cache/"+movie.id+".html", "r", encoding='utf8') as file:
            parser = MyHTMLParser()
            parsingOn = False
            for line in iter(file):
                if "og:title" in line:
                    parser.feed(line)
                if "class=\"infobar\"" in line:
                    parsingOn = True
                if parsingOn:
                    parser.feed(line)
                    if "</div>" in line:
                        #print(parser.parsedAttrs)
                        parsingOn = False
            movie.title = parser.parsedAttrs['title']
##TODO
# Neat Solution?          
            if 'dateTime' in parser.parsedAttrs: 
                movie.runTime = parser.parsedAttrs['dateTime']
            for genreType in parser.parsedAttrs['genre']:
                movie.genre.append(genreType[genreType.index("genre")+6:genreType.index("?")])
            movie.releaseDate = parser.parsedAttrs['datePublished']

    printMovieInfoDetailed(nowShowing)         


def createDatabase(movieList):
    nowShowing = initDatabase(movieList)
    movie_setParameters(nowShowing)

if __name__ == "__main__":
    movieList = getNowShowing()
    createDatabase(movieList)

    """Testing small list of movies, no parsing nowShowingURL"""
    #movieList = ['tt2713180', 'tt0816692']
    #createDatabase(movieList)
