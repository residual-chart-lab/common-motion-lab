/* Independent browser arithmetic circuit. No epochs, cycle counters or resets. */
(function (root) {
  const defaults = {axis:1, reference_rate:1.2, transport:.08, angular_rate:1,
    reference_feedback:.2, scale_feedback:.25, regularizer:.2,
    recruitment_scale:.7, freeze_reference:false, readout_only:false, exact_transport:false};
  const variants = {coupled:{}, axis_off:{axis:0}, reference_frozen:{freeze_reference:true},
    readout_only:{readout_only:true}, axis_reversed:{axis:-1}, exact_transport:{exact_transport:true}};
  function initial(nodes=3, delta=0) {
    return Array.from({length:nodes}, (_, i)=>[1,0,1,i===0?delta:0,0]);
  }
  function rhs(z,p) {
    return z.map(([x,y,rx,ry,s],i)=> {
      const ps=i ? z[i-1][4] : 0;
      const g=i===0?1:p.readout_only?0:ps*ps/(p.recruitment_scale**2+ps*ps);
      const w=p.angular_rate+p.reference_feedback*(rx*y-ry*x)+(p.readout_only?0:p.scale_feedback*Math.tanh(s));
      const dx=p.freeze_reference?0:g*p.reference_rate*(x-rx);
      const dy=p.freeze_reference?0:g*p.reference_rate*(y-ry);
      const sweep=p.exact_transport?rx*dx+ry*dy:rx*dy-ry*dx;
      return [-g*w*y,g*w*x,dx,dy,p.axis*p.transport*sweep/(p.regularizer+rx*rx+ry*ry)];
    });
  }
  function add(z,k,h) {return z.map((r,i)=>r.map((v,j)=>v+h*k[i][j]));}
  function step(z,p,h) {
    const a=rhs(z,p),b=rhs(add(z,a,h/2),p),c=rhs(add(z,b,h/2),p),d=rhs(add(z,c,h),p);
    return z.map((r,i)=>r.map((v,j)=>v+h*(a[i][j]+2*b[i][j]+2*c[i][j]+d[i][j])/6));
  }
  function simulate(name='coupled',delta=0,duration=50,dt=.02) {
    const p={...defaults,...variants[name]};
    let z=initial(3,delta); const time=[0], states=[z];
    for(let i=0;i<Math.round(duration/dt);i++) {
      z=step(z,p,dt);
      if((i+1)%5===0 || i+1===Math.round(duration/dt)) {time.push((i+1)*dt);states.push(z);}
    }
    return {time,states,p};
  }
  const api={defaults,variants,initial,rhs,step,simulate};
  if(typeof module!=='undefined' && module.exports) module.exports=api;
  else root.AxisPrototype=api;
})(globalThis);
