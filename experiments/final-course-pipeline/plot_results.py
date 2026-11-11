import json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=pathlib.Path(__file__).resolve().parent;R=json.loads((H/'results.json').read_text());assert R['status']=='complete'
keys=['self_detailed','jev_directed','decisions_directed','always_scaffolding','always_rigor','teacher_directed']
labels=['Self-choice','Jev\npolicy','Decisions\npolicy','Always\nscaffold','Always\nrigor','Assigned-label\ndiagnostic']
plt.rcParams.update({'font.family':'serif','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(6.4,2.7));x=list(range(len(keys)));w=.37
for offset,scope,color,hatch,label in [(-w/2,'all_520','#444444',None,'All 520 moments'),(w/2,'strict_math_346','#bdbdbd','//','Strict matched math frame (346)')]:
 vals=[100*R['scopes'][scope]['conditions'][k]['rate'] for k in keys];bars=ax.bar([i+offset for i in x],vals,w,label=label,color=color,hatch=hatch,edgecolor='black',linewidth=.5)
 for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+1.1,f'{v:.1f}',ha='center',va='bottom',fontsize=7)
ax.set_ylim(0,105);ax.set_ylabel('Automated first-reply pass (%)');ax.set_xticks(x,labels);ax.legend(loc='upper left',frameon=False,ncols=2,fontsize=8);ax.set_axisbelow(True);ax.yaxis.grid(True,color='#dddddd',linewidth=.5);fig.tight_layout();fig.savefig(H/'First Reply Results.pdf',bbox_inches='tight');fig.savefig(H/'First Reply Results.png',dpi=220,bbox_inches='tight')
lines=['\\begin{tabular}{lrr}','\\toprule','Policy & All 520 & Matched math 346 \\\\','\\midrule']
for k,label in zip(keys,labels):
 a=R['scopes']['all_520']['conditions'][k];b=R['scopes']['strict_math_346']['conditions'][k];lines.append(f"{label.replace(chr(10),' ')} & {a['pass']}/{a['n']} ({100*a['rate']:.1f}\\%) & {b['pass']}/{b['n']} ({100*b['rate']:.1f}\\%) \\\\")
lines+=['\\bottomrule','\\end{tabular}'];(H/'paper-results-table.tex').write_text('\n'.join(lines)+'\n')
print('Wrote scientific figure and LaTeX results table')
