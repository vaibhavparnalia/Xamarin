from globals import *
import urllib.request
from html.parser import HTMLParser

##TODO
#Check the HTML_cache before querying :)

class MyHTMLParser(HTMLParser):
    def __init__(self):
        #http://stackoverflow.com/questions/3276040/how-can-i-use-the-python-htmlparser-library-to-extract-data-from-a-specific-div
        HTMLParser.__init__(self)
        self.parsedAttrs = None

    def handle_starttag(self, tag, attrs):
        self.parsedAttrs = attrs
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        pass
    def handle_comment(self, data):
        pass

class movie:
    def __init__(self, imdbID):
        self.id = imdbID
        self.title = ""
        self.runTime = None
        self.genre = ""
        self.releaseDate = ""
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

def movie_setParameters(nowShowing):
    print("Found {} movies in theaters..".format(len(nowShowing)))
    parser = MyHTMLParser()
    #print([movie.id for movie in nowShowing])

    for movie in nowShowing:
        print("Querying {}".format(movie.id))
        page_content = HTMLResponse(moviePageURL+movie.id)

        with open("html_cache/"+movie.id+".html", "wb") as file:
            file.write(page_content)
        file.close()

        with open("html_cache/"+movie.id+".html", "r", encoding='utf8') as file:
            for line in iter(file):
                if "og:title" in line:
                    parser.feed(line)
                    for key, value in parser.parsedAttrs:
                        if key == "content":
                            movie.title = value
                            break

    for i in range(0, len(nowShowing)):
        if len(nowShowing) < 10:
            print("{}. {}".format(i+1, nowShowing[i].title))
        elif len(nowShowing) < 100:
            print("{:2d}. {}".format(i+1, nowShowing[i].title))
        else:
            print("{:3d}. {}".format(i+1, nowShowing[i].title))


def createDatabase(movieList):
    nowShowing = initDatabase(movieList)
    movie_setParameters(nowShowing)

if __name__ == "__main__":
    movieList = getNowShowing()
    createDatabase(movieList)

    """Testing small list of movies, no parsing nowShowingURL"""
    #movieList = ['tt2713180', 'tt0816692']
    #createDatabase(movieList)
