from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
W,H=1800,1100
FONT_PATHS=[Path('C:/Windows/Fonts/arial.ttf'),Path('C:/Windows/Fonts/calibri.ttf')]
BOLD_PATHS=[Path('C:/Windows/Fonts/arialbd.ttf'),Path('C:/Windows/Fonts/calibrib.ttf')]
def font(size,bold=False):
 for p in (BOLD_PATHS if bold else FONT_PATHS):
  if p.exists():return ImageFont.truetype(str(p),size)
 return ImageFont.load_default()
def base(title,subtitle=''):
 im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im);d.text((110,55),title,fill='black',font=font(48,True));
 if subtitle:d.text((110,115),subtitle,fill=(60,60,60),font=font(25))
 d.line((110,160,W-80,160),fill='black',width=3);return im,d
def save(im,name):
 im.save(OUT/name,dpi=(300,300),optimize=True)
def axes(d,x0,y0,x1,y1,ymax=100,ylabel='Rate (%)'):
 d.line((x0,y0,x0,y1),fill='black',width=3);d.line((x0,y1,x1,y1),fill='black',width=3)
 for v in range(0,int(ymax)+1,20):
  y=y1-(y1-y0)*v/ymax;d.line((x0-8,y,x1,y),fill=(215,215,215),width=1);d.text((x0-75,y-15),str(v),fill='black',font=font(22))
 d.text((18,(y0+y1)//2),ylabel,fill='black',font=font(25))
def hatch_rect(d,box,style):
 x0,y0,x1,y1=map(int,box);d.rectangle(box,fill='white',outline='black',width=3)
 if style==1:
  for x in range(x0+8,x1,14):d.line((x,y0,x,y1),fill='black',width=2)
 elif style==2:
  for y in range(y0+8,y1,14):d.line((x0,y,x1,y),fill='black',width=2)
 else:
  for x in range(x0+8,x1,16):d.line((x,y0,x,y1),fill='black',width=2)
  for y in range(y0+8,y1,16):d.line((x0,y,x1,y),fill='black',width=2)
models=['Llama 3.1 8B','GPT-OSS 20B','Nemotron Mini 4B']
# Figure 1 grouped outcome profile
im,d=base('Figure 1. Utility and adversarial outcomes','Rates are calculated over locked case-repetition denominators; lower attack success is better.')
x0,y0,x1,y1=180,220,1690,920;axes(d,x0,y0,x1,y1)
ben=[90,35,80];atk=[9.3,16.7,38];groupw=420;bw=115
for i,m in enumerate(models):
 gx=x0+120+i*groupw
 for j,(v,label) in enumerate([(ben[i],'Benign task success'),(atk[i],'Attack success')]):
  xx=gx+j*(bw+35);yy=y1-(y1-y0)*v/100;hatch_rect(d,(xx,yy,xx+bw,y1),j+1);d.text((xx+10,yy-38),f'{v:.1f}',fill='black',font=font(23,True))
 d.text((gx-10,y1+30),m,fill='black',font=font(23,True))
d.rectangle((1220,190,1260,225),outline='black',width=2);d.text((1275,191),'Benign task success',fill='black',font=font(22));
for y in range(198,223,8):d.line((1450,y,1490,y),fill='black',width=2)
d.rectangle((1450,190,1490,225),outline='black',width=2);d.text((1505,191),'Attack success',fill='black',font=font(22));save(im,'figure_1_outcome_profile.png')
# Figure 2 professionalism-safety scatter
im,d=base('Figure 2. The professionalism-safety mismatch','Structured output conformance did not imply resistance to adversarial instructions.')
x0,y0,x1,y1=190,225,1660,920;axes(d,x0,y0,x1,y1,50,'Attack success (%)')
for v in range(0,101,20):
 x=x0+(x1-x0)*v/100;d.line((x,y1,x,y1+8),fill='black',width=2);d.text((x-18,y1+18),str(v),fill='black',font=font(22))
d.text((650,1000),'JSON conformance (%)',fill='black',font=font(27,True))
pts=[(87.5,9.3,'Llama 3.1 8B','circle'),(69.2,16.7,'GPT-OSS 20B','square'),(99.2,38,'Nemotron Mini 4B','triangle')]
for xval,yval,label,shape in pts:
 x=x0+(x1-x0)*xval/100;y=y1-(y1-y0)*yval/50
 if shape=='circle':d.ellipse((x-16,y-16,x+16,y+16),fill='black')
 elif shape=='square':d.rectangle((x-16,y-16,x+16,y+16),fill='black')
 else:d.polygon([(x,y-20),(x-19,y+17),(x+19,y+17)],fill='black')
 tx=x-270 if xval>95 else x+28; d.text((tx,y-18),f'{label}  ({xval:.1f}, {yval:.1f})',fill='black',font=font(24,True))
d.text((1040,310),'Highest format conformance\nHighest attack success',fill='black',font=font(29,True));d.line((1320,390,1640,395),fill='black',width=3);save(im,'figure_2_professionalism_safety.png')
# Figure 3 condition heatmap grayscale
im,d=base('Figure 3. Task success by evaluation condition','Cell labels show successful responses / total responses and percentage.')
conds=['Benign','Direct injection','Indirect injection','Privilege escalation','Prompt disclosure','Hallucination trap','Jailbreak / task escape','Underspecified']
vals=[[90,93.3,70,100,0,85,50,26.7],[35,100,16.7,100,100,10,100,63.3],[80,56.7,100,26.7,60,0,90,0]]
nums=[['54/60','28/30','21/30','30/30','0/20','17/20','10/20','8/30'],['21/60','30/30','5/30','30/30','20/20','2/20','20/20','19/30'],['48/60','17/30','30/30','8/30','12/20','0/20','18/20','0/30']]
left,top,cw,ch=400,230,160,230
for j,c in enumerate(conds):
 words=c.split();lines=[' '.join(words[:2]),' '.join(words[2:])] if len(words)>2 else [c]
 for li,line in enumerate(lines):d.text((left+j*cw+8,178+li*25),line,fill='black',font=font(19,True))
for i,m in enumerate(models):
 d.text((90,top+i*ch+90),m,fill='black',font=font(24,True))
 for j,v in enumerate(vals[i]):
  shade=int(255-(v/100)*190);box=(left+j*cw,top+i*ch,left+(j+1)*cw-4,top+(i+1)*ch-4);d.rectangle(box,fill=(shade,shade,shade),outline='black',width=2)
  color='white' if shade<110 else 'black';d.text((box[0]+16,box[1]+75),nums[i][j],fill=color,font=font(24,True));d.text((box[0]+32,box[1]+115),f'{v:.1f}%',fill=color,font=font(22))
save(im,'figure_3_condition_matrix.png')
# Figure 4 stability
im,d=base('Figure 4. Repetition instability','Percentage of 120 cases whose binary task outcome differed across two repetitions; lower is more stable.')
x0,y0,x1,y1=210,240,1650,900;axes(d,x0,y0,x1,y1,15,'Unstable cases (%)')
vals=[5,12.5,0.833];bw=240
for i,(m,v) in enumerate(zip(models,vals)):
 x=x0+180+i*420;y=y1-(y1-y0)*v/15;hatch_rect(d,(x,y,x+bw,y1),i+1);d.text((x+70,y-40),f'{v:.1f}%',fill='black',font=font(27,True));d.text((x-10,y1+30),m,fill='black',font=font(24,True))
save(im,'figure_4_instability.png')
print('generated',len(list(OUT.glob('figure_*.png'))),'figures')
