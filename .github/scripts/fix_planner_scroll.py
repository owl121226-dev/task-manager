from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = "function render(){renderHead();"
new = "function render(){const previousSchedule=document.querySelector('.scheduleWrap'),previousUnplanned=document.querySelector('.unplannedBox'),scheduleScroll=previousSchedule?previousSchedule.scrollTop:null,unplannedScroll=previousUnplanned?previousUnplanned.scrollTop:null;renderHead();"
if old not in s:
    raise SystemExit('render start anchor missing')
s = s.replace(old, new, 1)

old = "if(todayMode){renderTodayPlanner(list);return}"
new = "if(todayMode){renderTodayPlanner(list);const nextSchedule=document.querySelector('.scheduleWrap'),nextUnplanned=document.querySelector('.unplannedBox');if(nextSchedule&&scheduleScroll!==null)nextSchedule.scrollTop=scheduleScroll;if(nextUnplanned&&unplannedScroll!==null)nextUnplanned.scrollTop=unplannedScroll;return}"
if old not in s:
    raise SystemExit('today render anchor missing')
s = s.replace(old, new, 1)

old = "setTimeout(()=>{const c=document.querySelector(`.scheduleCard[data-id=\"${t.id}\"]`);c?.scrollIntoView({block:'center',behavior:'smooth'})},30)"
new = "setTimeout(()=>{const c=document.querySelector(`.scheduleCard[data-id=\"${t.id}\"]`),sw=document.querySelector('.scheduleWrap');if(c&&sw)sw.scrollTo({top:Math.max(0,c.offsetTop-sw.clientHeight/2+c.offsetHeight/2),behavior:'smooth'})},30)"
if old not in s:
    raise SystemExit('placement scroll anchor missing')
s = s.replace(old, new, 1)

pattern = r"function enablePlannerDrag\(handle,card,t\)\{.*?\}\nfunction enablePlannerResize"
replacement = """function enablePlannerDrag(handle,card,t){handle.onpointerdown=e=>{e.preventDefault();e.stopPropagation();const p=getTodayPlan(t,true),duration=Math.max(15,Number(p.duration)||60),scroller=card.closest('.scheduleWrap'),grid=card.parentElement,grabOffset=e.clientY-card.getBoundingClientRect().top;let pointerY=e.clientY,active=true,raf=0,lastM=timeToMinutes(p.time)??PLAN_START;handle.setPointerCapture(e.pointerId);card.style.zIndex='20';const update=()=>{const gr=grid.getBoundingClientRect(),topPx=pointerY-gr.top-grabOffset,raw=PLAN_START+topPx/PLAN_HOUR_PX*60,m=Math.max(PLAN_START,Math.min(PLAN_END-duration,snap15(raw)));lastM=m;card.style.top=`${plannerY(m)}px`};const tick=()=>{if(!active)return;if(scroller){const r=scroller.getBoundingClientRect(),edge=Math.min(90,Math.max(50,r.height*.16));let speed=0;if(pointerY<r.top+edge){const q=Math.max(0,Math.min(1,(r.top+edge-pointerY)/edge));speed=-(3+17*q)}else if(pointerY>r.bottom-edge){const q=Math.max(0,Math.min(1,(pointerY-(r.bottom-edge))/edge));speed=3+17*q}if(speed){const before=scroller.scrollTop,max=Math.max(0,scroller.scrollHeight-scroller.clientHeight);scroller.scrollTop=Math.max(0,Math.min(max,before+speed));if(scroller.scrollTop!==before)update()}}raf=requestAnimationFrame(tick)};const move=ev=>{pointerY=ev.clientY;update()};const up=ev=>{active=false;if(raf)cancelAnimationFrame(raf);try{handle.releasePointerCapture?.(ev.pointerId)}catch(_){}handle.removeEventListener('pointermove',move);handle.removeEventListener('pointerup',up);handle.removeEventListener('pointercancel',up);p.time=minutesToTime(lastM);save();render()};update();raf=requestAnimationFrame(tick);handle.addEventListener('pointermove',move);handle.addEventListener('pointerup',up);handle.addEventListener('pointercancel',up)}}
function enablePlannerResize"""
s, n = re.subn(pattern, replacement, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'enablePlannerDrag replacement count={n}')

assert "KEY='task-manager-v1'" in s
p.write_text(s, encoding='utf-8')

m = re.search(r'<script>([\s\S]*?)</script>', s)
assert m
Path('/tmp/app.js').write_text(m.group(1), encoding='utf-8')
