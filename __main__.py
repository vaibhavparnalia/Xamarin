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
            self.parsedAttrs["dateTime"] = attrs[1][1]
        if tag == "a" and "genre" in attrs[0][1]:
            self.parsedAttrs["genre"].append(attrs[0][1])
        if tag == "meta" and "datePublished" in attrs[0][1]:
            self.parsedAttrs["datePublished"] = attrs[1][1]
        if tag == "meta" and "og:title" in attrs[0][1]:
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
        self.runTime = 0
        self.genre = []
        self.releaseDate = 0
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
    YYYY, MM, DD = (myDate.split("-"))
    return datetime.date(int(YYYY), int(MM), int(DD)).strftime("%d %B %Y")

def getGenreStr(genreList):
    genreStr = ""
    for genreType in genreList:
        genreStr = genreStr + genreType + ", "
    return genreStr[:-2]

def getRunTime(runTime):
    if runTime:
        for char in runTime:
            if char.isdigit():
                indexStart = runTime.index(char)
                break
        for char in runTime[indexStart:]:
            if char.isalpha():
                indexEnd = indexStart + runTime[indexStart:].index(char)
        return int(runTime[indexStart:indexEnd])

def printMovieInfoDetailed(nowShowing):

    for i in range(0, len(nowShowing)):
        if len(nowShowing) < 10:
            print("{}. {}".format(i+1, nowShowing[i].title))
        elif len(nowShowing) < 100:
            print("{:2d}. {}".format(i+1, nowShowing[i].title))
        else:
            print("{:3d}. {}".format(i+1, nowShowing[i].title))
        if nowShowing[i].runTime:
            print("    RunTime: {} mins".format(nowShowing[i].runTime))
        else:
            print("    RunTime: N/A")
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
                #Parses movie title
                if "og:title" in line:
                    parser.feed(line)
                #Parses other data

                if "class=\"infobar\"" in line:
                    parsingOn = True
                if parsingOn:
                    parser.feed(line)
                    if "</div>" in line:
                        parsingOn = False

            movie.title = parser.parsedAttrs['title']          
            if 'dateTime' in parser.parsedAttrs: 
                movie.runTime = getRunTime(parser.parsedAttrs['dateTime'])
            if 'genre' in parser.parsedAttrs:
                for genreType in parser.parsedAttrs['genre']:
                    movie.genre.append(genreType[genreType.index("genre")+6:genreType.index("?")])
            if 'datePublished' in parser.parsedAttrs:
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
