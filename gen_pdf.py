from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Flowable,Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from scraper import scrape
from io import BytesIO
import PIL
import sys
import requests
from bs4 import BeautifulSoup as bs

base_url = "http://random-art.org/"
proxies = {

}

def scrape(s,e,popularity=False):
    payload = {
        'page':'',
        'sort':'time'
    }
    if popularity:
        payload['sort']='popularity'
    img_list = []
    count = 1
    for n,i in enumerate(range(s,e+1)):
        print("[x] Page " + str(n+1))
        payload['page']=str(i)
        r = requests.get(base_url,payload,proxies=proxies).content
        soup = bs(r,'html.parser')
        tags = soup.findAll(attrs={'class':'image'})
        for tag in tags:
            _img = tag.find('img')
            img={}
            img['count']= count
            img['src']=_img.get('src').replace('small','large')
            img['alt']=_img.get('alt')
            img_list.append(img)
            count+=1
    return img_list

img_list = scrape(1,20,True)
list_size = len(img_list)
print("[x]Total Images Scraped : ",list_size)
#Downloading the images into a folder
print('[x]Downloading Images')
for img in img_list:
    sys.stdout.write('\r')
    percent = img['count']*100/list_size
    url = base_url+img['src']
    r = requests.get(url,proxies=proxies)
    image = PIL.Image.open(BytesIO(r.content))
    image.save('images\\'+str(img['count'])+".jpg",format='JPEG')
    sys.stdout.write("%d%%"%percent)
    sys.stdout.flush()


pdfmetrics.registerFont(TTFont('consolas', 'unifont-9.0.01.ttf'))
doc = SimpleDocTemplate("test.pdf",pagesize=A4,
                        rightMargin=40,leftMargin=40,
                        topMargin=40,bottomMargin=18)
styles = getSampleStyleSheet()
styleH = styles['Heading1']
styleN = styles['Normal']


print('[x]Building pdf')
Story=[]
Story.append(Paragraph("<font size=30 name='consolas'><b>random-art</b></font>",styleH))
Story.append(Spacer(1,10)) 
Story.append(Paragraph('''<font name='consolas'>
                            The pictures in this gallery are made by a computer program.
                            The program accepts the name of a picture and uses it as a seed
                            from which a picture is generated randomly.
                            The same name always yields the same picture.
                        </font>'''
            ,styleN))
Story.append(Spacer(1,10))            
Story.append(Paragraph('''<font name='consolas'>
                            The author of the random art program is 
                            <font color='blue'><b>Andrej Bauer</b></font>.
                        </font>'''
            ,styleN))
Story.append(Spacer(1,20))
Story.append(Paragraph("<font name='consolas'><b>catalogue</b></font>",styleH))
Story.append(Spacer(1,10)) 
print("Building Table")
for i in range(0,list_size,3):
    tbl_data=[
        [Image("images\\"+str(img_list[i]['count'])+".jpg",1.5*inch,1.5*inch),
         Image("images\\"+str(img_list[i+1]['count'])+".jpg",1.5*inch,1.5*inch),
         Image("images\\"+str(img_list[i+2]['count'])+".jpg",1.5*inch,1.5*inch)
        ],
        [
         Paragraph('''<font name='consolas'>%s</font>''' % img_list[i]['alt'],styleN),
         Paragraph('''<font name='consolas'>%s</font>''' % img_list[i+1]['alt'],styleN),
         Paragraph('''<font name='consolas'>%s</font>''' % img_list[i+2]['alt'],styleN)
        ]
    ]
    Story.append(Table(tbl_data,colWidths=[2.2*inch,2.2*inch,2.2*inch]))
    Story.append(Spacer(1,12))


doc.build(Story)


