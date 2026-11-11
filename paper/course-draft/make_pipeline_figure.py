"""Draw the study design as a vector PDF; no model/API calls required."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
root=Path(__file__).resolve().parent
# Portable fallback: standard Helvetica when macOS Arial is unavailable.
font=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
bold=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
regular='Helvetica'; strong='Helvetica-Bold'
if font.exists() and bold.exists():
    pdfmetrics.registerFont(TTFont('FigureArial',str(font)))
    pdfmetrics.registerFont(TTFont('FigureArialBold',str(bold)))
    regular='FigureArial'; strong='FigureArialBold'
W,H=452,166
c=canvas.Canvas(str(root/'pipeline_design.pdf'),pagesize=(W,H))
c.setTitle('Decision-guided tutoring: proposed design and controlled test')
c.setAuthor('EDUC 6181 research group')
ink=HexColor('#20272d'); line=HexColor('#68717a'); pale=HexColor('#f0f2f3')
def text(x,y,s,size=8.6,bold=False,center=False):
    c.setFillColor(ink);c.setFont(strong if bold else regular,size)
    (c.drawCentredString if center else c.drawString)(x,y,s)
def box(x,y,w,h,lines,fill=white):
    c.setFillColor(fill);c.setStrokeColor(line);c.setLineWidth(.6)
    c.roundRect(x,y,w,h,4,stroke=1,fill=1)
    start=y+h/2+((len(lines)-1)*10)/2-3
    for i,s in enumerate(lines):text(x+w/2,start-i*10,s,8.5,center=True)
def arrow(x1,y1,x2,y2):
    c.setStrokeColor(line);c.setFillColor(line);c.setLineWidth(.8)
    c.line(x1,y1,x2-4,y2)
    path=c.beginPath();path.moveTo(x2,y2);path.lineTo(x2-5,y2+2.5);path.lineTo(x2-5,y2-2.5);path.close()
    c.drawPath(path,fill=1,stroke=0)
text(0,155,'SELF-CHOICE: ONE MODEL CHOOSES AND WRITES',8.5,True)
box(0,116,88,30,['Conversation','so far'])
box(124,116,202,30,['Qwen receives both instruction sets,','chooses an approach, and writes'])
box(362,116,90,30,['Tutor reply'])
arrow(89,131,123,131);arrow(327,131,361,131)
text(0,100,'PROPOSED DESIGN: SEPARATE THE TEACHING CHOICE FROM THE REPLY',8.5,True)
box(0,60,88,30,['Conversation','so far'])
box(108,60,112,30,['Jev or Decisions','Choose scaffold / rigor'],pale)
box(240,60,100,30,['Selected teaching','instructions'],pale)
box(360,60,92,30,['Qwen writes','the tutor reply'])
for a,b in [(89,107),(221,239),(341,359)]:arrow(a,75,b,75)
text(0,44,'Qwen also receives the full conversation, not just the selected instruction.',8.5)
c.setFillColor(pale);c.roundRect(0,0,W,33,3,fill=1,stroke=0)
text(8,22,'CONTROLLED TEST',8.2,True)
text(103,22,'520 moments × 3 Qwen replies: self-choice, scaffold-guided, rigor-guided.',8.2)
text(8,9,'Saved decisions select the matching guided reply; fixed controls reuse one branch for every moment.',8.2)
c.save()
print(root/'pipeline_design.pdf')
