import os
import sys
import time
import datetime
import urllib.request
from globals import *
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        #http://stackoverflow.com/questions/3276040/how-can-i-use-the-python-htmlparser-library-to-extract-data-from-a-specific-div
        HTMLParser.__init__(self)
        self.scanData = 0
        self.recData = []
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
        if tag == "time" and "birthDate" in attrs[1][1]:
            self.parsedAttrs['birthDate'] = attrs[0][1]
        if tag == "span" and "location-display" in attrs[0][1]:
            self.scanData = 1

    def handle_endtag(self, tag):
        #print("End tag  :", tag)
        pass
    def handle_data(self, data):
        #print("Data     :", data)
        if self.scanData:
            self.recData.append(data)
        self.scanData = 0
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

#http://stackoverflow.com/questions/11325019/output-on-the-console-and-file-using-python
class Tee(object):
    def __init__(self, *fileName):
        self.file = fileName
    def write(self, obj):
        for f in self.file:
            f.write(obj)

def HTMLResponse(url):
    try:
        page = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        print(e.strerror)
    return page.read()

def filterMovieID(fileName, method):
    movieID = []
    if method == "getNowShowing":
        with open(fileName, "r", encoding="utf8") as file:
            for line in iter(file):
                if "/showtimes/title/" in line:
                    if "tt" in line:
                        indexStart = line.index("tt")
                        indexEnd = indexStart + line[indexStart:].index('/')
                        if line[indexStart:indexEnd] not in movieID:
                            movieID.append(line[indexStart:indexEnd])
                if "location-display" in line:
                    parser = MyHTMLParser()
                    parser.feed(line)
            print("{} movies currently running in {} within 30 miles\n".format(len(movieID), parser.recData[0]))
    elif method == "getTopTen":
        with open(fileName, "r", encoding="utf8") as file:
            startRecord = False
            for line in iter(file):
                if parseStarter_boxOfficeTopTen in line:
                    startRecord = True
                if startRecord and "?ref_=inth_ov_i" in line:
                    if "tt" in line:
                        indexStart = line.index("tt")
                        indexEnd = indexStart + line[indexStart:].index('/')
                        if line[indexStart:indexEnd] not in movieID:
                            movieID.append(line[indexStart:indexEnd])
            print("Box Office - Top Ten Movies\n")
    return movieID
    
def cacheCheck(path, fileName):
    #print(os.path.join(path, fileName))
    if os.path.isfile(os.path.join(path, fileName)) : return True

def getNowShowing():
    page_content = HTMLResponse(nowShowingURL)
    with open("html_cache/now_showing.html", "wb") as file:
        file.write(page_content)
    file.close()

    return filterMovieID("html_cache/now_showing.html", "getNowShowing")

def getTopTen():
    page_content = HTMLResponse(topTenURL)
    with open("html_cache/top_ten.html", "wb") as file:
        file.write(page_content)
    file.close()

    return filterMovieID("html_cache/top_ten.html", "getTopTen")    

def initDatabase(movieList):
    nowShowing = []
    [nowShowing.append(movie(movieID)) for movieID in movieList]
    return nowShowing

def convertDate(myDate):
    YYYY, MM, DD = (myDate.split("-"))
    YYYY, MM, DD = int(YYYY), int(MM), int(DD)
    if MM>0 and DD>0 and YYYY>0:
        return datetime.date(YYYY, MM, DD).strftime("%d %B %Y")
    else:
        if YYYY:
            return str(YYYY)
        else:
            return myDate

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

def getCastAverageAge(castList, releaseDate):
    totalAge = 0
    castNum = 0
    if releaseDate:
        releaseYear = releaseDate.split("-")[0]
        if len(releaseYear) == 4:
            releaseYear = int(releaseYear)
        else:
            return 0
    for cast in castList:
        if cast[1]:
            year = cast[1].split('-')[0]
            if year:
                if int(year) > 0:
                    age = releaseYear - int(year)
                    #print("{}:{} year".format(cast[0], age))
                    castNum += 1
                    totalAge += age
    if castNum:
        return totalAge//castNum
    else:
        return 0

def printMovieInfoDetailed(nowShowing):
    #stdout = sys.stdout
    #sys.stdout = open('output.txt', 'w')

    f = open('output.txt', 'w')
    stdout = sys.stdout
    sys.stdout = Tee(sys.stdout, f)

    print("\n")
    for counter, movie in enumerate(nowShowing):
        if len(nowShowing) < 10:
            print("{}. {}".format(counter+1, movie.title))
        elif len(nowShowing) < 100:
            print("{:2d}. {}".format(counter+1, movie.title))
        else:
            print("{:3d}. {}".format(counter+1, movie.title))
        if movie.runTime:
            print("    RunTime: {} mins".format(movie.runTime))
        else:
            print("    RunTime: N/A")
        print("    Genre: ", end="")
        genreStr = getGenreStr(movie.genre)
        print("{}".format(genreStr))
        dateStr = convertDate(movie.releaseDate)
        print("    Date Released: {}".format(dateStr))
        averageCastAge = getCastAverageAge(movie.cast, movie.releaseDate)
        if averageCastAge:
            print("    Cast Average Age(when released): {} years".format(averageCastAge))
        else:
            print("    Cast Average Age: N/A")
        if len(movie.cast):
            print("    Cast List:")
        for cast in movie.cast:
            if cast[1]:
                print("        {:<20s}: {:<20s}".format(cast[0], convertDate(cast[1])))
    sys.stdout = stdout

def getCastInfo(nameID):
    imdb = "http://www.imdb.com"
    
    if not cacheCheck(os.path.join("html_cache", "cast"), str(nameID)+str(".html")):
        print("  Querying cast# {}".format(nameID))
        page_content = HTMLResponse(imdb + "/name/" + nameID + "/")
        with open("html_cache/cast/"+nameID+".html", "wb") as file:
            file.write(page_content)
        file.close()

    with open("html_cache/cast/"+nameID+".html", "r", encoding='utf8') as file:
        parser = MyHTMLParser()
        for line in iter(file):
            if "og:title" in line:
                parser.feed(line)
            if "birthDate" in line:
                parser.feed(line)
                break
            if parseBreaker_birthDate in line:
                break
    if "title" in parser.parsedAttrs:
        name = parser.parsedAttrs["title"]
    if "birthDate" in parser.parsedAttrs:
        birthDate = parser.parsedAttrs["birthDate"]
    else:
        birthDate = None
    return (name, birthDate)

def getAllCreditedCasts(movieID):
    #print(moviePageURL+movieID+fullcreditsExtn)
    imdb = "http://www.imdb.com"
    cast = []

    if not cacheCheck("html_cache", str(movieID)+str("_full_credits.html")):
        print("  Querying credited casts not in cache..")
        page_content = HTMLResponse(moviePageURL+movieID+fullcreditsExtn)

        with open("html_cache/"+movieID+"_full_credits.html", "wb") as file:
            file.write(page_content)
        file.close()

    with open("html_cache/"+movieID+"_full_credits.html", "r", encoding='utf8') as file:
        parser = MyHTMLParser()
        parsingOn = False
        for line in iter(file):
            if "?ref_=ttfc_fc_cl_i" in line:
                #I prefer to do this in single line
                nameID = (line[line.index("name")+5:line.index("name")+5+line[line.index("name")+5:].index("/")])
                cast.append(getCastInfo(nameID))
            elif parseBreaker_uncreditedCast in line:
                break
            elif parseBreaker_characterPage in line:
                break
    return cast

def movie_setParameters(nowShowing):
    #print([movie.id for movie in nowShowing])

    for counter, movie in enumerate(nowShowing):
        if not cacheCheck("html_cache", str(movie.id)+str(".html")):
            print("Querying movie({}/{})# {}".format(counter+1, len(nowShowing), movie.id))
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
                        break

            movie.title = parser.parsedAttrs['title']          
            if 'dateTime' in parser.parsedAttrs: 
                movie.runTime = getRunTime(parser.parsedAttrs['dateTime'])
            if 'genre' in parser.parsedAttrs:
                for genreType in parser.parsedAttrs['genre']:
                    movie.genre.append(genreType[genreType.index("genre")+6:genreType.index("?")])
            if 'datePublished' in parser.parsedAttrs:
                movie.releaseDate = parser.parsedAttrs['datePublished']

        movie.cast = getAllCreditedCasts(movie.id)

    
    return nowShowing
    
def createDatabase(movieList):
    nowShowing = initDatabase(movieList)
    nowShowing = movie_setParameters(nowShowing)
    return nowShowing

if __name__ == "__main__":
    if not os.path.exists("html_cache"):
        os.mkdir("html_cache")
    if not os.path.exists("html_cache/cast"):
        os.mkdir("html_cache/cast")

    while True:
        try:
            whatMovies = int(input("1. Top Ten Movie\n2. All Now Showing Nearby\n"))
            if whatMovies == 1 or whatMovies ==2:
                break
            else:
                print("Please input a valid choice..")
        except ValueError: print("Please input a valid choice..")
    startTime = time.time()
    if whatMovies == 1:
        movieList = getTopTen()
    else:
        movieList = getNowShowing()
    nowShowing = createDatabase(movieList)
    endTime = time.time()
    printMovieInfoDetailed(nowShowing)

    """Testing small list of movies, skip parsing nowShowingURL"""
    #movieList = ['tt2713180']
    #nowShowing = createDatabase(movieList)
    #getAllCreditedCasts('tt2713180')
    """--------------------------------------------------------"""

    print("Result generated in {:.2f} seconds".format(endTime-startTime))