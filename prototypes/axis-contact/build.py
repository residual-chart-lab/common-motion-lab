"""Generate standalone viewer, figure, and verify browser/Python agreement."""
import json
import os
from pathlib import Path
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import VARIANTS, simulate

root=Path(__file__).parent.resolve()
template=(root/'viewer-template.html').read_text()
(root/'index.html').write_text(template.replace('/* RUNTIME */',(root/'runtime.js').read_text()))
node=os.environ.get('CODEX_PRIMARY_RUNTIME_NODE','node')
script="const p=require('./runtime.js'); console.log(JSON.stringify(Object.fromEntries(Object.keys(p.variants).map(k=>[k,p.simulate(k).states.at(-1)]))));"
out=json.loads(subprocess.check_output([node,'-e',script],cwd=root,text=True))
err=0
for name,p in VARIANTS.items():
    _,states=simulate(p)
    err=max(err,float(np.max(np.abs(np.array(out[name])-states[-1]))))
assert err<1e-10,err
(root/'results'/'browser-equivalence.json').write_text(json.dumps({'status':'passed','max_endpoint_difference':err,'compared_variants':list(VARIANTS),'scope':'Numerical runtime equivalence; not visual browser QA'},indent=2)+'\n')

data=np.load(root/'results'/'trajectories.npz')
t=data['time']; colors=['#146f78','#bf7640','#7063a6']
fig,ax=plt.subplots(2,3,figsize=(13,7.3),facecolor='#f3f2ed')
for a in ax.flat:
    a.set_facecolor('#fffefa')
    a.spines[['top','right']].set_visible(False)
    a.grid(alpha=.12)
for a,name,title in zip(ax[0],['coupled','axis_off','readout_only'],['Coupled axis + reference','Axis coupling removed','Scale used only for display']):
    for j,col in enumerate(colors):
        z=data[name][:,j];R=np.exp(z[:,4]);a.plot(R*z[:,0],R*z[:,1],color=col,lw=1.3,label=f'Node {j+1}')
    a.set_aspect('equal',adjustable='datalim');a.set_title(title,fontsize=12);a.set_xlabel('scaled q₁');a.set_ylabel('scaled q₂')
for a,name,title in zip(ax[1],['coupled','axis_off','readout_only'],['Scale feeds later motion','Rotation without scale transport','A spiral is not enough']):
    for j,col in enumerate(colors):
        a.plot(t,data[name][:,j,4],color=col,lw=2,label=f'Node {j+1}')
    a.set_title(title,fontsize=12);a.set_xlabel('continuous time');a.set_ylabel('log scale s');a.set_ylim(-.12,3.8)
ax[1,0].legend(frameon=False,fontsize=9)
fig.suptitle('Present-contact prototype P0 — continuous local law, three preallocated nodes',fontsize=15,y=.985)
fig.text(.02,.015,'A constitutive axis-transport hypothesis. Future causality, fractal generation and learning gains are not established.',fontsize=10,color='#667578')
fig.tight_layout(rect=[0,.045,1,.96]);fig.savefig(root/'results'/'comparison.png',dpi=145);plt.close(fig)
print(json.dumps({'viewer':'index.html','figure':'results/comparison.png','browser_runtime_max_error':err}))
