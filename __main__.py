from globals import *
import urllib.request

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

def createDatabase(movieList):
    nowShowing = initDatabase(movieList)
    print(nowShowing)

if __name__ == "__main__":
    movieList = getNowShowing()
    createDatabase(movieList)
