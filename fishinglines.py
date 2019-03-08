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
lw=200 #line width
tw=320 #text width

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
    elements = ('Na23','Mg24','Ni60','Cu63','Sr88','Ba137')
    ranges=dict([[element,{'min':1e10,'max':-1.0}] for element in elements])
    #print fieldnames
    try:
        while True:
            line = (yield)
            #print line
            mycode=line[4]
            code=line[3]
            region=line[5]
            site=line[6]
            Na23=pinfloat(line[7])
            Mg24=pinfloat(line[8])
            Ni60=pinfloat(line[9])
            Cu63=pinfloat(line[10])
            Sr88=pinfloat(line[11])
            Ba137=pinfloat(line[12])
            if not fishlines.get(mycode,False):
                fishlines[mycode] = {'code':code,'region':region,'site':site,
                'Na23':[],'Mg24':[],'Ni60':[],'Cu63':[],'Sr88':[],'Ba137':[]}
                fishlist.append(mycode)
            fishlines[mycode]['Na23'].append(Na23)
            fishlines[mycode]['Mg24'].append(Mg24)
            fishlines[mycode]['Ni60'].append(Ni60)
            fishlines[mycode]['Cu63'].append(Cu63)
            fishlines[mycode]['Sr88'].append(Sr88)
            fishlines[mycode]['Ba137'].append(Ba137)
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
            labels.append({"across":0, "down":offset,"text":"%s %s %s" %(fish, fishlines[fish]['region'],fishlines[fish]['site'])})
            for e in elements:
                lines.append({"points":makeline(fishlines[fish][e],ranges[e]['min'],ranges[e]['max']), "across":across,"down":offset})
                across=across+lw
            offset = offset+lh
        template = JINJA_ENVIRONMENT.get_template('template.svg')
        values={"labels":labels, "lines":lines, "width":tw+lw*6, "height":offset}
        print template.render(values)

        

if __name__ == '__main__':
    readallcsvfiles('*.csv',
        fish() #output
        )
