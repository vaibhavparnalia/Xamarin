import urllib.request

page = urllib.request.urlopen('http://www.imdb.com/showtimes/location')
page_content = page.read()

with open("imdb.html", "wb") as file:
    file.write(page_content)
file.close()

movieId = []
with open("imdb.html", "r", encoding="utf8") as file:
    for line in iter(file):
        if "/showtimes/title/" in line:
            if "tt" in line:
                indexStart = line.index("tt")
                indexEnd = indexStart + line[indexStart:].index('/')
                if line[indexStart:indexEnd] not in movieId:
                    movieId.append(line[indexStart:indexEnd])
print(movieId)
print(len(movieId))
