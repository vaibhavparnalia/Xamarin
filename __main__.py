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
        if tag == "time" and "birthDate" in attrs[1][1]:
            self.parsedAttrs['birthDate'] = attrs[0][1]

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
    YYYY, MM, DD = int(YYYY), int(MM), int(DD)
    if MM>0 and DD>0:
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

def printMovieInfoDetailed(nowShowing):
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
        print("    Cast List:")
        for cast in movie.cast:
            if cast[1]:
                print("        {}: {}".format(cast[0], convertDate(cast[1])))
    """
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
        print("    Cast List:")
        for cast in nowShowing[i].cast:
            if cast[1]:
                print("        {}: {}".format(cast[0], convertDate(cast[1])))
                """

def getCastInfo(nameID):
    imdb = "http://www.imdb.com"
    #print("  Querying castID {}".format(nameID))
    parser = MyHTMLParser()
    page_content = HTMLResponse(imdb + "/name/" + nameID + "/")
    with open("html_cache/"+nameID+".html", "wb") as file:
        file.write(page_content)
    file.close()

    with open("html_cache/"+nameID+".html", "r", encoding='utf8') as file:
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
    print("  Querying all credited casts..please wait..")
    imdb = "http://www.imdb.com"
    page_content = HTMLResponse(moviePageURL+movieID+fullcreditsExtn)
    cast = []

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
                #age = getCastInfo(nameID)
                #print(name, age)
            elif parseBreaker_uncreditedCast in line:
                break
    return cast

def movie_setParameters(nowShowing):
    print("Found {} movies in theaters..".format(len(nowShowing)))
    #print([movie.id for movie in nowShowing])

    for movie in nowShowing:
        print("Querying movie# {}".format(movie.id))
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

    printMovieInfoDetailed(nowShowing)
    return nowShowing
    
def createDatabase(movieList):
    nowShowing = initDatabase(movieList)
    nowShowing = movie_setParameters(nowShowing)
    return nowShowing

if __name__ == "__main__":
    #movieList = getNowShowing()
    #createDatabase(movieList)

    """Testing small list of movies, no parsing nowShowingURL"""
    movieList = ['tt2713180', 'tt0816692']
    nowShowing = createDatabase(movieList)
    #getAllCreditedCasts('tt2713180')
