from pathlib import Path
import json, math, collections
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
SCORES=[json.loads(x) for x in (ROOT/'outputs/scored_cases.jsonl').read_text(encoding='utf8').splitlines() if x.strip()]
MODELS=['meta/llama-3.1-8b-instruct','openai/gpt-oss-20b','nvidia/nemotron-mini-4b-instruct']
LABELS=['Llama 3.1 8B','GPT-OSS 20B','Nemotron Mini 4B']
COLORS=['#2563EB','#7C3AED','#F97316']
HATCHES=['','','']
plt.rcParams.update({'font.family':'Arial','font.size':10,'axes.titlesize':18,'axes.titleweight':'bold','axes.labelsize':11,'axes.labelweight':'bold','axes.edgecolor':'#222222','axes.linewidth':0.8,'xtick.color':'#222222','ytick.color':'#222222','text.color':'#111111','figure.facecolor':'#F8FAFC','axes.facecolor':'#FFFFFF','savefig.facecolor':'#F8FAFC','savefig.bbox':'tight'})

def rate(model,key,flt=lambda x:True):
 a=[x for x in SCORES if x['model']==model and flt(x)];k=sum(bool(x[key]) for x in a);return 100*k/len(a),k,len(a)
def wilson(k,n,z=1.95996398454):
 p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return 100*(c-h),100*(c+h)
def finish(fig,name):
 fig.text(0.01,0.005,'DataAgent-SafeBench | JRS/2026/039 | Locked pilot: 120 cases, 3 models, 2 repetitions',fontsize=7.5,color='#555555')
 fig.savefig(OUT/f'{name}.png',dpi=320)
 fig.savefig(OUT/f'{name}.pdf')
 fig.savefig(OUT/f'{name}.svg')
 plt.close(fig)
def clean(ax):
 ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#E3E3E3',linewidth=.8);ax.set_axisbelow(True)

# 1: Grouped bars with Wilson intervals
metrics=[('Benign task success','task_success',lambda x:x['condition']=='benign'),('Attack success','attack_success',lambda x:x['condition'] not in ('benign','underspecified'))]
vals=np.zeros((3,2));los=np.zeros_like(vals);his=np.zeros_like(vals)
for i,m in enumerate(MODELS):
 for j,(_,key,flt) in enumerate(metrics):
  v,k,n=rate(m,key,flt);lo,hi=wilson(k,n);vals[i,j]=v;los[i,j]=v-lo;his[i,j]=hi-v
fig,ax=plt.subplots(figsize=(10.8,6.5));x=np.arange(3);w=.29
for j,(title,_,_) in enumerate(metrics):
 bars=ax.bar(x+(j-.5)*w,vals[:,j],w,yerr=np.vstack([los[:,j],his[:,j]]),capsize=4,color=['#14B8A6','#F97316'][j],edgecolor='white',linewidth=1.2,hatch=['',''][j],label=title,error_kw={'elinewidth':1,'capthick':1})
 for b,v in zip(bars,vals[:,j]):ax.text(b.get_x()+b.get_width()/2,b.get_height()+6.5,f'{v:.1f}%',ha='center',va='bottom',fontsize=10,fontweight='bold')
ax.set_title('Utility and adversarial outcomes',loc='left',pad=18);ax.text(0,1.01,'Error bars show Wilson 95% confidence intervals. Lower attack success is better.',transform=ax.transAxes,color='#555555',fontsize=9)
ax.set_ylabel('Rate');ax.set_ylim(0,112);ax.yaxis.set_major_formatter(PercentFormatter());ax.set_xticks(x,LABELS,fontweight='bold');ax.legend(frameon=False,ncols=2,loc='upper center',bbox_to_anchor=(.56,.99));clean(ax);fig.tight_layout(rect=(0,0.03,1,1));finish(fig,'figure_1_outcome_profile')

# 2: professionalism vs safety scatter
conf=[rate(m,'json_conformant')[0] for m in MODELS];attack=[rate(m,'attack_success',lambda x:x['condition'] not in ('benign','underspecified'))[0] for m in MODELS]
fig,ax=plt.subplots(figsize=(10.8,6.6));ax.axvspan(90,101,color='#DBEAFE',alpha=.45,zorder=0);ax.axhspan(25,50,color='#FFEDD5',alpha=.5,zorder=0)
for i,(xv,yv) in enumerate(zip(conf,attack)):
 ax.scatter(xv,yv,s=210,marker=['o','s','^'][i],facecolor=COLORS[i],edgecolor='white',linewidth=1.1,zorder=3)
 offsets=[(-180,-8),(-145,18),(-195,16)]
 ax.annotate(f'{LABELS[i]}\n{xv:.1f}% format | {yv:.1f}% attack',(xv,yv),xytext=offsets[i],textcoords='offset points',fontsize=9.5,fontweight='bold',bbox={'boxstyle':'round,pad=.35','fc':'white','ec':COLORS[i],'alpha':.96},arrowprops={'arrowstyle':'-','color':COLORS[i],'lw':1.2})
ax.text(91.0,46.0,'High polish  +  high risk',fontsize=11,fontweight='bold',color='#C2410C',ha='center',bbox={'boxstyle':'round,pad=.4','fc':'#FFF7ED','ec':'#FDBA74'})
ax.set_title('The professionalism–safety mismatch',loc='left',pad=18);ax.text(0,1.01,'A polished response format did not guarantee adversarial resilience.',transform=ax.transAxes,color='#555555',fontsize=9)
ax.set_xlabel('Structured-output conformance');ax.set_ylabel('Attack-success rate');ax.set_xlim(55,102);ax.set_ylim(0,50);ax.xaxis.set_major_formatter(PercentFormatter());ax.yaxis.set_major_formatter(PercentFormatter());ax.xaxis.set_major_locator(MultipleLocator(10));ax.yaxis.set_major_locator(MultipleLocator(10));clean(ax);fig.tight_layout(rect=(0,0.03,1,1));finish(fig,'figure_2_professionalism_safety')

# 3: task-success matrix
conditions=[('benign','Benign'),('direct_injection','Direct\ninjection'),('indirect_injection','Indirect\ninjection'),('privilege_escalation','Privilege\nescalation'),('prompt_disclosure','Prompt\ndisclosure'),('hallucination_trap','Hallucination\ntrap'),('jailbreak_task_escape','Jailbreak /\ntask escape'),('underspecified','Under-\nspecified')]
mat=np.zeros((3,len(conditions)));nums=[]
for i,m in enumerate(MODELS):
 row=[]
 for j,(cond,_) in enumerate(conditions):
  v,k,n=rate(m,'task_success',lambda x,c=cond:x['condition']==c);mat[i,j]=v;row.append((k,n))
 nums.append(row)
fig,ax=plt.subplots(figsize=(13.5,5.6));im=ax.imshow(mat,cmap='YlGnBu',vmin=0,vmax=100,aspect='auto')
for i in range(3):
 for j in range(len(conditions)):
  color='white' if mat[i,j]>=62 else '#0F172A';k,n=nums[i][j];ax.text(j,i-.08,f'{mat[i,j]:.1f}%',ha='center',va='center',color=color,fontweight='bold',fontsize=10);ax.text(j,i+.18,f'{k}/{n}',ha='center',va='center',color=color,fontsize=8)
ax.set_xticks(range(len(conditions)),[x[1] for x in conditions],fontweight='bold');ax.xaxis.tick_top();ax.tick_params(axis='x',length=0,pad=10);ax.set_yticks(range(3),LABELS,fontweight='bold');ax.tick_params(axis='y',length=0,pad=10)
for x in np.arange(-.5,len(conditions),1):ax.axvline(x,color='white',lw=2)
for y in np.arange(-.5,3,1):ax.axhline(y,color='white',lw=2)
ax.set_title('Task-success fingerprints differ sharply by condition',loc='left',pad=52);ax.text(0,1.13,'Dark cells indicate higher task success; labels show percentage and successful responses / denominator.',transform=ax.transAxes,color='#555555',fontsize=9)
cbar=fig.colorbar(im,ax=ax,fraction=.018,pad=.02);cbar.ax.yaxis.set_major_formatter(PercentFormatter());cbar.set_label('Task success',fontweight='bold');fig.tight_layout(rect=(0,0.04,1,1));finish(fig,'figure_3_condition_matrix')

# 4: attack success by adversarial condition
attack_conds=[('direct_injection','Direct injection'),('indirect_injection','Indirect injection'),('privilege_escalation','Privilege escalation'),('prompt_disclosure','Prompt disclosure'),('hallucination_trap','Hallucination trap'),('jailbreak_task_escape','Jailbreak / task escape')]
fig,axes=plt.subplots(1,3,figsize=(14,5.8),sharey=True)
for i,(m,label) in enumerate(zip(MODELS,LABELS)):
 v=[]
 for cond,_ in attack_conds:v.append(rate(m,'attack_success',lambda x,c=cond:x['condition']==c)[0])
 ax=axes[i];y=np.arange(len(attack_conds));bars=ax.barh(y,v,color=COLORS[i],edgecolor='white',hatch=HATCHES[i],height=.62)
 for b,val in zip(bars,v):ax.text(min(val+2,96),b.get_y()+b.get_height()/2,f'{val:.1f}%',va='center',fontsize=9,fontweight='bold',color='black')
 ax.set_title(label,fontsize=13,pad=10);ax.set_xlim(0,105);ax.xaxis.set_major_formatter(PercentFormatter());ax.xaxis.set_major_locator(MultipleLocator(20));ax.grid(axis='x',color='#E3E3E3');ax.set_axisbelow(True);ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
 if i==0:ax.set_yticks(y,[x[1] for x in attack_conds],fontweight='bold')
 else:ax.tick_params(labelleft=False)
 ax.invert_yaxis();ax.set_xlabel('Attack success')
fig.suptitle('Where each model failed',x=.06,y=.99,ha='left',fontsize=18,fontweight='bold');fig.text(.06,.925,'Condition-level attack-success rates reveal distinct vulnerability profiles.',color='#555555',fontsize=9);fig.tight_layout(rect=(0,0.04,1,.92),w_pad=2);finish(fig,'figure_4_failure_fingerprints')

# 5: repetition instability
inst=[]
for m in MODELS:
 d=collections.defaultdict(list)
 for s in SCORES:
  if s['model']==m:d[s['case_id']].append(bool(s['task_success']))
 inst.append(100*sum(len(set(v))>1 for v in d.values())/len(d))
fig,ax=plt.subplots(figsize=(9.5,5.8));bars=ax.bar(np.arange(3),inst,width=.52,color=COLORS,edgecolor='white',hatch=HATCHES,linewidth=1.2)
for b,v in zip(bars,inst):ax.text(b.get_x()+b.get_width()/2,v+.55,f'{v:.1f}%',ha='center',fontweight='bold',fontsize=11)
ax.set_title('Outcome stability across repeated runs',loc='left',pad=18);ax.text(0,1.01,'Share of 120 cases whose binary task-success outcome changed across two repetitions.',transform=ax.transAxes,color='#555555',fontsize=9);ax.set_ylabel('Unstable cases');ax.set_ylim(0,15);ax.yaxis.set_major_formatter(PercentFormatter());ax.set_xticks(range(3),LABELS,fontweight='bold');clean(ax);fig.tight_layout(rect=(0,0.03,1,1));finish(fig,'figure_5_instability')
print('Generated five publication figures in PNG, PDF, and SVG formats.')
