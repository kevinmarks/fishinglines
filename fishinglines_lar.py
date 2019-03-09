# fishinglines.py
#
# A pipeline to mung fish measurements into sparklines
from coroutines import *
import json
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


#  0 Spot No,
#  1 Spot No,
#  2 Source file,
#  3 Fish code,
#  4 My code,
#  5 Region,
#  6 My site,
#  7 Na23_ppm,
#  8 Mg24_ppm,
#  9 Ni60_ppm,
# 10 Cu63_ppm,
# 11 Sr88_ppm,
# 12 Ba137_ppm

lh=20 #line height
lw=160 #line width
tw=80 #text width

def pinfloat(value):
    try:
        return float(value)
    except:
        return None
def makeline(points,min,max):
    line=[]
    #print points,min,max
    for i in range(0,len(points)):
        x=i*10;
        v= points[i]
        if v:
            y = lh*(v-min)/(max-min)
            line.append("%.1f,%.5f" %(x,y))
    return " ".join(line)
        
@coroutine
def fish():
    fishlines={}
    line = (yield)
    fieldnames = line
    fishlist=[]
    #elements = {'Na23':7,'Mg24':8,'Ni60':9,'Cu63':10,'Sr88':11,'Ba137':12}
    elements = {'Na23':3,'Mg24':4,'Ni61':5,'Cu63':6,'Rb85':7,'Sr88':8,'Ba137':9}
    ranges=dict([[element,{'min':1e10,'max':-1.0}] for element in elements])
    #print fieldnames
    try:
        while True:
            line = (yield)
            #print line
            mycode=line[1]
#             code=line[3]
#             region=line[5]
#             site=line[6]
            if not fishlines.get(mycode,False):
                fishlines[mycode] = {} #{'code':code,'region':region,'site':site}
                for e in elements:
                    fishlines[mycode][e]=[]
                fishlist.append(mycode)
            for e in elements:
                fishlines[mycode][e].append(pinfloat(line[elements[e]]))
            for e in elements:
                if fishlines[mycode][e][-1]:
                    ranges[e]['max']=max(ranges[e]['max'],fishlines[mycode][e][-1])
                    ranges[e]['min']=min(ranges[e]['min'],fishlines[mycode][e][-1])
    except GeneratorExit:
        offset=lh;
        lines=[]
        labels=[]
        across = tw+lw/3
        for e in elements:
            labels.append({"across":across,"down":offset,"text": e})
            across= across+lw
        offset = offset+lh
        for fish in fishlist:
            across=tw
            labels.append({"across":0, "down":offset,"text":fish})
            for e in elements:
                lines.append({"points":makeline(fishlines[fish][e],ranges[e]['min'],ranges[e]['max']), "across":across,"down":offset})
                across=across+lw
            offset = offset+lh
        template = JINJA_ENVIRONMENT.get_template('template.svg')
        values={"labels":labels, "lines":lines, "width":tw+lw*6, "height":offset}
        print template.render(values)

        

if __name__ == '__main__':
    readallcsvfiles('lar.csv',
        fish() #output
        )
