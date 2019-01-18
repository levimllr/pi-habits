import time

from datetime import datetime

time = 1546804800
howmuch = 6
most = 6
utctopstsec = 28800

week = int(datetime.utcfromtimestamp(time-utctopstsec).strftime('%U'))
day = int(datetime.utcfromtimestamp(time-utctopstsec).strftime('%w'))
intensity = int(165*howmuch/most+90)

print('{}, {}, {}; {}, {}, {}'.format(time,howmuch,most,week,day,intensity))

# , {howmuch}, {most}; {week}, {day}, {intensity}
