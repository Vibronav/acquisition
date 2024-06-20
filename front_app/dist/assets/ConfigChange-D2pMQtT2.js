import{g as W,a as G,s as F,c as L,_ as f,r as R,u as q,b as A,d as fe,f as De,j as e,e as z,h as E,F as Ne,T as P,L as He,i as Oe,k as ve,l as Ue,S as Be,I as Ve,m as We,O as J,n as D,o as N,p as I,q as V,t as Ge,P as x,R as g,M as m,v as Je,B as Ke,w as Qe,x as oe,y as Xe}from"./index-qVJxkeRn.js";import{I as je,L as ie,a as le,C as de,b as ce,d as Ye}from"./DeleteOutline-DSnZOb7p.js";function Ze(t){return G("MuiFormHelperText",t)}const ue=W("MuiFormHelperText",["root","error","disabled","sizeSmall","sizeMedium","contained","focused","filled","required"]);var pe;const et=["children","className","component","disabled","error","filled","focused","margin","required","variant"],tt=t=>{const{classes:s,contained:n,size:a,disabled:r,error:i,filled:d,focused:h,required:u}=t,c={root:["root",r&&"disabled",i&&"error",a&&`size${L(a)}`,n&&"contained",h&&"focused",d&&"filled",u&&"required"]};return E(c,Ze,s)},st=F("p",{name:"MuiFormHelperText",slot:"Root",overridesResolver:(t,s)=>{const{ownerState:n}=t;return[s.root,n.size&&s[`size${L(n.size)}`],n.contained&&s.contained,n.filled&&s.filled]}})(({theme:t,ownerState:s})=>f({color:(t.vars||t).palette.text.secondary},t.typography.caption,{textAlign:"left",marginTop:3,marginRight:0,marginBottom:0,marginLeft:0,[`&.${ue.disabled}`]:{color:(t.vars||t).palette.text.disabled},[`&.${ue.error}`]:{color:(t.vars||t).palette.error.main}},s.size==="small"&&{marginTop:4},s.contained&&{marginLeft:14,marginRight:14})),nt=R.forwardRef(function(s,n){const a=q({props:s,name:"MuiFormHelperText"}),{children:r,className:i,component:d="p"}=a,h=A(a,et),u=fe(),c=De({props:a,muiFormControl:u,states:["variant","size","disabled","error","filled","focused","required"]}),j=f({},a,{component:d,contained:c.variant==="filled"||c.variant==="outlined",variant:c.variant,size:c.size,disabled:c.disabled,error:c.error,filled:c.filled,focused:c.focused,required:c.required}),y=tt(j);return e.jsx(st,f({as:d,ownerState:j,className:z(y.root,i),ref:n},h,{children:r===" "?pe||(pe=e.jsx("span",{className:"notranslate",children:"​"})):r}))});function at(t){return G("MuiInputAdornment",t)}const me=W("MuiInputAdornment",["root","filled","standard","outlined","positionStart","positionEnd","disablePointerEvents","hiddenLabel","sizeSmall"]);var xe;const rt=["children","className","component","disablePointerEvents","disableTypography","position","variant"],ot=(t,s)=>{const{ownerState:n}=t;return[s.root,s[`position${L(n.position)}`],n.disablePointerEvents===!0&&s.disablePointerEvents,s[n.variant]]},it=t=>{const{classes:s,disablePointerEvents:n,hiddenLabel:a,position:r,size:i,variant:d}=t,h={root:["root",n&&"disablePointerEvents",r&&`position${L(r)}`,d,a&&"hiddenLabel",i&&`size${L(i)}`]};return E(h,at,s)},lt=F("div",{name:"MuiInputAdornment",slot:"Root",overridesResolver:ot})(({theme:t,ownerState:s})=>f({display:"flex",height:"0.01em",maxHeight:"2em",alignItems:"center",whiteSpace:"nowrap",color:(t.vars||t).palette.action.active},s.variant==="filled"&&{[`&.${me.positionStart}&:not(.${me.hiddenLabel})`]:{marginTop:16}},s.position==="start"&&{marginRight:8},s.position==="end"&&{marginLeft:8},s.disablePointerEvents===!0&&{pointerEvents:"none"})),be=R.forwardRef(function(s,n){const a=q({props:s,name:"MuiInputAdornment"}),{children:r,className:i,component:d="div",disablePointerEvents:h=!1,disableTypography:u=!1,position:c,variant:j}=a,y=A(a,rt),C=fe()||{};let w=j;j&&C.variant,C&&!w&&(w=C.variant);const o=f({},a,{hiddenLabel:C.hiddenLabel,size:C.size,disablePointerEvents:h,position:c,variant:w}),p=it(o);return e.jsx(Ne.Provider,{value:null,children:e.jsx(lt,f({as:d,ownerState:o,className:z(p.root,i),ref:n},y,{children:typeof r=="string"&&!u?e.jsx(P,{color:"text.secondary",children:r}):e.jsxs(R.Fragment,{children:[c==="start"?xe||(xe=e.jsx("span",{className:"notranslate",children:"​"})):null,r]})}))})}),dt=["className"],ct=t=>{const{alignItems:s,classes:n}=t;return E({root:["root",s==="flex-start"&&"alignItemsFlexStart"]},Oe,n)},ut=F("div",{name:"MuiListItemIcon",slot:"Root",overridesResolver:(t,s)=>{const{ownerState:n}=t;return[s.root,n.alignItems==="flex-start"&&s.alignItemsFlexStart]}})(({theme:t,ownerState:s})=>f({minWidth:56,color:(t.vars||t).palette.action.active,flexShrink:0,display:"inline-flex"},s.alignItems==="flex-start"&&{marginTop:8})),he=R.forwardRef(function(s,n){const a=q({props:s,name:"MuiListItemIcon"}),{className:r}=a,i=A(a,dt),d=R.useContext(He),h=f({},a,{alignItems:d.alignItems}),u=ct(h);return e.jsx(ut,f({className:z(u.root,r),ownerState:h,ref:n},i))});function pt(t){return G("MuiTextField",t)}W("MuiTextField",["root"]);const mt=["autoComplete","autoFocus","children","className","color","defaultValue","disabled","error","FormHelperTextProps","fullWidth","helperText","id","InputLabelProps","inputProps","InputProps","inputRef","label","maxRows","minRows","multiline","name","onBlur","onChange","onFocus","placeholder","required","rows","select","SelectProps","type","value","variant"],xt={standard:Ve,filled:We,outlined:J},ht=t=>{const{classes:s}=t;return E({root:["root"]},pt,s)},ft=F(ve,{name:"MuiTextField",slot:"Root",overridesResolver:(t,s)=>s.root})({}),T=R.forwardRef(function(s,n){const a=q({props:s,name:"MuiTextField"}),{autoComplete:r,autoFocus:i=!1,children:d,className:h,color:u="primary",defaultValue:c,disabled:j=!1,error:y=!1,FormHelperTextProps:C,fullWidth:w=!1,helperText:o,id:p,InputLabelProps:v,inputProps:_,InputProps:l,inputRef:S,label:b,maxRows:H,minRows:_e,multiline:ee=!1,name:Te,onBlur:Pe,onChange:ke,onFocus:Le,placeholder:$e,required:te=!1,rows:Fe,select:O=!1,SelectProps:U,type:qe,value:se,variant:$="outlined"}=a,Ae=A(a,mt),ne=f({},a,{autoFocus:i,color:u,disabled:j,error:y,fullWidth:w,multiline:ee,required:te,select:O,variant:$}),ze=ht(ne),k={};$==="outlined"&&(v&&typeof v.shrink<"u"&&(k.notched=v.shrink),k.label=b),O&&((!U||!U.native)&&(k.id=void 0),k["aria-describedby"]=void 0);const M=Ue(p),B=o&&M?`${M}-helper-text`:void 0,ae=b&&M?`${M}-label`:void 0,Ee=xt[$],re=e.jsx(Ee,f({"aria-describedby":B,autoComplete:r,autoFocus:i,defaultValue:c,fullWidth:w,multiline:ee,name:Te,rows:Fe,maxRows:H,minRows:_e,type:qe,value:se,id:M,inputRef:S,onBlur:Pe,onChange:ke,onFocus:Le,placeholder:$e,inputProps:_},k,l));return e.jsxs(ft,f({className:z(ze.root,h),disabled:j,error:y,fullWidth:w,ref:n,required:te,color:u,variant:$,ownerState:ne},Ae,{children:[b!=null&&b!==""&&e.jsx(je,f({htmlFor:M,id:ae},v,{children:b})),O?e.jsx(Be,f({"aria-describedby":B,id:M,labelId:ae,value:se,input:re},U,{children:d})):re,o&&e.jsx(nt,f({id:B},C,{children:o}))]}))});var K={},vt=N;Object.defineProperty(K,"__esModule",{value:!0});var Ie=K.default=void 0,jt=vt(D()),bt=e;Ie=K.default=(0,jt.default)((0,bt.jsx)("path",{d:"M12 5V2L8 6l4 4V7c3.31 0 6 2.69 6 6 0 2.97-2.17 5.43-5 5.91v2.02c3.95-.49 7-3.85 7-7.93 0-4.42-3.58-8-8-8m-6 8c0-1.65.67-3.15 1.76-4.24L6.34 7.34C4.9 8.79 4 10.79 4 13c0 4.08 3.05 7.44 7 7.93v-2.02c-2.83-.48-5-2.94-5-5.91"}),"RestartAlt");var Q={},It=N;Object.defineProperty(Q,"__esModule",{value:!0});var ge=Q.default=void 0,gt=It(D()),Ct=e;ge=Q.default=(0,gt.default)((0,Ct.jsx)("path",{d:"M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5M12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5m0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3"}),"Visibility");var X={},wt=N;Object.defineProperty(X,"__esModule",{value:!0});var Ce=X.default=void 0,Rt=wt(D()),yt=e;Ce=X.default=(0,Rt.default)((0,yt.jsx)("path",{d:"M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7M2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2m4.31-.78 3.15 3.15.02-.16c0-1.66-1.34-3-3-3z"}),"VisibilityOff");var Y={},St=N;Object.defineProperty(Y,"__esModule",{value:!0});var we=Y.default=void 0,Mt=St(D()),_t=e;we=Y.default=(0,Mt.default)((0,_t.jsx)("path",{d:"M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z"}),"Add");const Re=({title:t,addPrompt:s,defaultItems:n,addedItems:a,setAddedItems:r,checkedItems:i,setCheckedItems:d,height:h})=>{const[u,c]=R.useState(""),j=o=>()=>{const p=i.indexOf(o),v=[...i];p===-1?v.push(o):v.splice(p,1),d(v)},y=o=>{c(o.target.value)},C=()=>{u&&!a.includes(u)&&(r(o=>[...o,u]),c(""))},w=o=>{r(p=>p.filter(v=>v!==o)),d(p=>p.filter(v=>v!==o))};return e.jsxs(I,{sx:{width:"100%",gap:2},children:[e.jsx(P,{variant:"h6",children:t}),e.jsxs(ve,{children:[e.jsx(je,{children:s}),e.jsx(J,{endAdornment:e.jsx(be,{position:"end",children:e.jsx(V,{onClick:C,edge:"end",sx:{"&:hover":{backgroundColor:"#f0f0f0"}},children:e.jsx(we,{sx:{color:"secondary.main"}})})}),label:`${s}`,value:u,onChange:y})]}),e.jsxs(Ge,{sx:{width:"100%",maxHeight:{height:h},overflow:"auto",bgcolor:"background.paper",borderRadius:2},children:[n.map(o=>{const p=`checkbox-list-label-${o}`;return e.jsx(ie,{disablePadding:!0,children:e.jsxs(le,{role:void 0,onClick:j(o),dense:!0,children:[e.jsx(he,{children:e.jsx(de,{edge:"start",checked:i.indexOf(o)!==-1,tabIndex:-1,disableRipple:!0,inputProps:{"aria-labelledby":p}})}),e.jsx(ce,{id:p,primary:o})]})},o)}),a.map(o=>{const p=`checkbox-list-label-${o}`;return e.jsx(ie,{secondaryAction:e.jsx(V,{edge:"end","aria-label":"delete",onClick:()=>w(o),sx:{"&:hover":{backgroundColor:"#f0f0f0"}},children:e.jsx(Ye,{sx:{color:"secondary.main"}})}),disablePadding:!0,children:e.jsxs(le,{role:void 0,onClick:j(o),dense:!0,children:[e.jsx(he,{children:e.jsx(de,{edge:"start",checked:i.indexOf(o)!==-1,tabIndex:-1,disableRipple:!0,inputProps:{"aria-labelledby":p}})}),e.jsx(ce,{id:p,primary:o})]})},o)})]})]})};Re.propTypes={title:x.string.isRequired,addPrompt:x.string.isRequired,defaultItems:x.array.isRequired,addedItems:x.array.isRequired,setAddedItems:x.func.isRequired,checkedItems:x.array.isRequired,setCheckedItems:x.func.isRequired,height:x.number};const Z=Re;function ye({config:t,setConfig:s}){const[n,a]=g.useState(t.chosen_lab_checks),[r,i]=g.useState(t.new_lab_checks);return g.useEffect(()=>{a(t.chosen_lab_checks)},[t]),g.useEffect(()=>{s(d=>({...d,chosen_lab_checks:n,new_lab_checks:r}))},[n,r,s]),e.jsx(I,{sx:{width:"100%"},children:e.jsx(Z,{title:e.jsx(m,{id:"beforeMessurments"}),addPrompt:e.jsx(m,{id:"addTask"}),defaultItems:t.lab_checks,addedItems:r,setAddedItems:i,checkedItems:n,setCheckedItems:a,height:220})})}ye.propTypes={config:x.object.isRequired,setConfig:x.func.isRequired};function Se({config:t,setConfig:s}){const[n,a]=g.useState(t.chosenMaterials),[r,i]=g.useState(t.newMaterials);return g.useEffect(()=>{a(t.chosenMaterials),i(t.newMaterials)},[t]),g.useEffect(()=>{s(d=>({...d,chosenMaterials:n,newMaterials:r}))},[n,r,s]),e.jsx(I,{sx:{width:"100%"},children:e.jsx(Z,{title:e.jsx(m,{id:"material"}),addPrompt:e.jsx(m,{id:"addMaterial"}),defaultItems:t.defaultMaterials,addedItems:r,setAddedItems:i,checkedItems:n,setCheckedItems:a,height:430})})}Se.propTypes={config:x.object.isRequired,setConfig:x.func.isRequired};function Me({config:t,setConfig:s}){const[n,a]=g.useState(t.chosenSpeeds),[r,i]=g.useState(t.newSpeeds);return g.useEffect(()=>{a(t.chosenSpeeds),i(t.newSpeeds)},[t]),g.useEffect(()=>{s(d=>({...d,chosenSpeeds:n,newSpeeds:r}))},[n,r,s]),e.jsx(I,{sx:{width:"100%"},children:e.jsx(Z,{title:e.jsx(m,{id:"speed"}),addPrompt:e.jsx(m,{id:"addSpeed"}),defaultItems:t.defaultSpeeds,addedItems:r,setAddedItems:i,checkedItems:n,setCheckedItems:a})})}Me.propTypes={config:x.object.isRequired,setConfig:x.func.isRequired};Tt.propTypes={config:x.object.isRequired,setConfig:x.func.isRequired,handleReset:x.func.isRequired};function Tt({config:t,setConfig:s,handleReset:n}){const[a,r]=R.useState(!1),[i,d]=R.useState(!1),h=sessionStorage.getItem("commentConfig")||"",[u,c]=R.useState(h),j=Je(),y=l=>{s(S=>({...S,username:l.target.value}))},C=()=>d(l=>!l),w=l=>{l.preventDefault()},o=()=>{const l=t.username.indexOf("_")!==-1||t.username.length===0||t.username.indexOf(" ")!==-1;r(l),l||j(Xe.Camera)},p=l=>{const S=l.target.value;s(b=>({...b,local_dir:S}))},v=l=>{const S=l.target.value;s(b=>({...b,remote_dir:S}))},_=(l,S)=>{const b=[...t.connection];b[l]=S,s(H=>({...H,connection:b}))};return R.useEffect(()=>{sessionStorage.setItem("commentConfig",u)},[u]),e.jsxs(Ke,{children:[e.jsx(I,{direction:"row",gap:4,sx:{marginTop:5,width:"100%"},children:e.jsxs(I,{direction:"row",gap:4,sx:{width:"100%"},children:[e.jsxs(I,{gap:2,sx:{width:"100%"},children:[e.jsxs(I,{gap:2,children:[e.jsx(P,{variant:"h6",children:e.jsx(m,{id:"username"})}),e.jsx(T,{error:a,helperText:a?"Incorrect entry.":"",value:t.username,onChange:y})]}),e.jsxs(I,{gap:2,sx:{width:"100%"},children:[e.jsx(P,{variant:"h6",children:e.jsx(m,{id:"connection"})}),e.jsx(T,{label:e.jsx(m,{id:"Device"}),value:t.connection[0],onChange:l=>_(0,l.target.value)}),e.jsx(T,{label:e.jsx(m,{id:"Port"}),value:t.connection[1],onChange:l=>_(1,l.target.value)}),e.jsx(T,{label:e.jsx(m,{id:"Device name"}),value:t.connection[2],onChange:l=>_(2,l.target.value)}),e.jsx(J,{id:"outlined-adornment-password",type:i?"text":"password",endAdornment:e.jsx(be,{position:"end",children:e.jsx(V,{"aria-label":"toggle password visibility",onClick:C,onMouseDown:w,edge:"end",children:i?e.jsx(Ce,{}):e.jsx(ge,{})})}),label:"Password",value:t.connection[3],onChange:l=>_(3,l.target.value)}),e.jsxs(P,{variant:"h6",children:[e.jsx(m,{id:"comment"}),e.jsx(Qe,{style:{width:"100%"},value:u,minRows:4,maxRows:10,onChange:()=>{c(event.target.value)}})]})]})]}),e.jsxs(I,{gap:4,sx:{width:"100%"},children:[e.jsxs(I,{gap:2,sx:{width:"100%"},children:[e.jsx(P,{variant:"h6",children:e.jsx(m,{id:"saveDir"})}),e.jsx(T,{label:e.jsx(m,{id:"LocalDir"}),value:t.local_dir,onChange:p}),e.jsx(T,{label:e.jsx(m,{id:"RemoteDir"}),value:t.remote_dir,onChange:v})]}),e.jsx(ye,{config:t,setConfig:s})]}),e.jsx(Se,{config:t,setConfig:s}),e.jsx(Me,{config:t,setConfig:s})]})}),e.jsxs(I,{sx:{width:"100%",alignItems:"end",marginTop:5,gap:1,justifyContent:"flex-end"},direction:"row",children:[e.jsxs(oe,{onClick:n,variant:"contained",children:[e.jsx(Ie,{}),e.jsx(m,{id:"resetButton"})]}),e.jsx(oe,{onClick:o,variant:"contained",disabled:t.username==null||t.chosenMaterials.length==0||t.chosenSpeeds.length==0,children:e.jsx(m,{id:"saveButton"})})]})]})}export{Tt as default};
