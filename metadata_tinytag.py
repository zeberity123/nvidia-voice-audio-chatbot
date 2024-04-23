from tinytag import TinyTag
tag = TinyTag.get('/some/music.mp3')
print('This track is by %s.' % tag.artist)
print('It is %f seconds long.' % tag.duration)
