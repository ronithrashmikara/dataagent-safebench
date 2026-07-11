from pathlib import Path
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle
from matplotlib.ticker import MultipleLocator, PercentFormatter
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
# Exact locked values
points=[('GPT-OSS 20B',69.2,16.7,'#74558D','s'),('Llama 3.1 8B',87.5,9.3,'#235789','o'),('Nemotron Mini 4B',99.2,38.0,'#D3543C','^')]
plt.rcParams.update({'font.family':'Georgia','axes.edgecolor':'#463D34','axes.labelcolor':'#29241F','xtick.color':'#463D34','ytick.color':'#463D34'})
fig,ax=plt.subplots(figsize=(16,9),facecolor='#F2E8CF');ax.set_facecolor('#F7F0DE')
# restrained seigaiha-inspired corner arcs
for ox,oy in [(0.02,.82),(.82,.04)]:
 for row in range(3):
  for col in range(5):
   cx=ox+col*.045+(row%2)*.022;cy=oy+row*.045
   for rad in (.035,.025,.015):ax.add_patch(Arc((cx,cy),rad*2,rad*2,angle=0,theta1=0,theta2=180,transform=ax.transAxes,color='#8DA0A6',lw=.45,alpha=.18,zorder=0))
# subtle high-polish/high-risk zone
ax.axvspan(90,101,color='#DCE7E4',alpha=.42,zorder=0);ax.axhspan(25,50,color='#E8C8B8',alpha=.24,zorder=0)
for name,x,y,color,marker in points:
 ax.scatter(x,y,s=290,marker=marker,color=color,edgecolor='#F7F0DE',linewidth=2.2,zorder=4)
positions={'GPT-OSS 20B':(-165,32),'Llama 3.1 8B':(-175,-54),'Nemotron Mini 4B':(-240,52)}
for name,x,y,color,marker in points:
 ax.annotate(f'{name}\n{x:.1f}% format  |  {y:.1f}% attack',(x,y),xytext=positions[name],textcoords='offset points',fontsize=11,fontweight='bold',color='#27221D',bbox={'boxstyle':'round,pad=.55','fc':'#FFF9EA','ec':color,'lw':1.3,'alpha':.97},arrowprops={'arrowstyle':'-','color':color,'lw':1.35})
ax.text(94.0,32.5,'HIGH POLISH  ·  HIGH RISK',ha='center',fontsize=11,fontweight='bold',color='#A33627',bbox={'boxstyle':'round,pad=.45','fc':'#F9E3D8','ec':'#D3543C','lw':1.1})
ax.set_xlim(55,102);ax.set_ylim(0,50);ax.xaxis.set_major_locator(MultipleLocator(10));ax.yaxis.set_major_locator(MultipleLocator(10));ax.xaxis.set_major_formatter(PercentFormatter());ax.yaxis.set_major_formatter(PercentFormatter())
ax.grid(color='#91887A',alpha=.22,linewidth=.75);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False);ax.spines[['left','bottom']].set_linewidth(1.3)
ax.set_xlabel('Structured-output conformance',fontsize=13,fontweight='bold',labelpad=12);ax.set_ylabel('Attack-success rate',fontsize=13,fontweight='bold',labelpad=12)
fig.text(.07,.925,'The professionalism–safety mismatch',fontsize=28,fontweight='bold',color='#1C2E3D',fontfamily='Georgia')
fig.text(.07,.884,'A polished response format did not guarantee adversarial resilience.',fontsize=14,color='#5B5147',fontfamily='Georgia')
fig.text(.07,.055,'DataAgent-SafeBench   |   JRS/2026/039   |   120 cases · 3 models · 2 repetitions',fontsize=9,color='#685E52')
# hanko-inspired research seal
seal=Circle((.92,.085),.034,transform=fig.transFigure,facecolor='none',edgecolor='#B84335',lw=2.1);fig.patches.append(seal);fig.text(.92,.085,'SAFE\nBENCH',ha='center',va='center',fontsize=7.5,fontweight='bold',color='#B84335')
fig.subplots_adjust(left=.08,right=.965,bottom=.14,top=.84)
base=OUT/'figure_2_professionalism_safety_washi_base.png';fig.savefig(base,dpi=300,facecolor='#F2E8CF');fig.savefig(OUT/'figure_2_professionalism_safety_washi.pdf',facecolor='#F2E8CF');plt.close(fig)
# Add subtle fibrous washi texture without altering chart geometry or labels
im=Image.open(base).convert('RGB');overlay=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(overlay);rng=random.Random(20260711)
for _ in range(9500):
 x=rng.randrange(im.width);y=rng.randrange(im.height);length=rng.randint(2,18);shade=rng.choice([(110,90,65,9),(255,255,255,12),(95,110,105,7)])
 d.line((x,y,x+length,y+rng.choice([-1,0,1])),fill=shade,width=1)
for _ in range(1100):
 x=rng.randrange(im.width);y=rng.randrange(im.height);r=rng.choice([1,1,2]);d.ellipse((x-r,y-r,x+r,y+r),fill=(105,85,62,10))
overlay=overlay.filter(ImageFilter.GaussianBlur(.25));out=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');out.save(OUT/'figure_2_professionalism_safety_washi.png',dpi=(300,300),quality=96)
base.unlink(missing_ok=True)
print(OUT/'figure_2_professionalism_safety_washi.png')


