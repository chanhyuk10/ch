<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>로켓 중량 vs 최고 고도 시뮬레이터</title>
<style>
  :root{
    --bg: #0b1220;
    --panel: #121a2b;
    --panel-2: #0e1524;
    --grid: #223050;
    --border: #26314a;
    --text: #e9edf5;
    --muted: #8b96ad;
    --flame: #e2572b;
    --flame-dim: #7a3220;
    --sky: #43b7c4;
    --sky-dim: #235058;
    --warn: #e8b34a;
  }
  *{ box-sizing:border-box; }
  html,body{ margin:0; padding:0; }
  body{
    background:
      radial-gradient(1200px 600px at 15% -10%, #16213a 0%, transparent 60%),
      var(--bg);
    color:var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Pretendard", "Noto Sans KR", Roboto, sans-serif;
    line-height:1.55;
    min-height:100vh;
  }
  .mono{ font-family: "SF Mono","JetBrains Mono", Consolas, "Noto Sans Mono", monospace; }

  .wrap{ max-width:840px; margin:0 auto; padding:40px 20px 80px; }

  header.hero{ margin-bottom:36px; }
  header.hero h1{
    font-size:clamp(26px,4.2vw,38px);
    line-height:1.25;
    font-weight:700;
    letter-spacing:-0.01em;
    margin:0 0 14px;
  }
  header.hero p{
    color:var(--muted);
    font-size:15.5px;
    max-width:64ch;
    margin:0;
  }
  header.hero .engine-tag{
    display:inline-flex;
    align-items:center;
    gap:8px;
    margin-bottom:18px;
    padding:5px 12px;
    border:1px solid var(--border);
    border-radius:999px;
    font-size:12.5px;
    color:var(--muted);
  }
  header.hero .engine-tag .dot{
    width:7px;height:7px;border-radius:50%;
    background:var(--flame);
    box-shadow:0 0 8px var(--flame);
  }

  .panel{
    background: linear-gradient(180deg, var(--panel), var(--panel-2));
    border:1px solid var(--border);
    border-radius:10px;
    padding:24px;
    margin-bottom:22px;
    position:relative;
    overflow:hidden;
  }
  .panel::before{
    content:"";
    position:absolute; inset:0;
    background-image:
      linear-gradient(var(--grid) 1px, transparent 1px),
      linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 26px 26px;
    opacity:0.12;
    pointer-events:none;
  }
  .panel > *{ position:relative; }

  .panel h2{
    font-size:16.5px;
    font-weight:700;
    margin:0 0 6px;
    letter-spacing:-0.005em;
  }
  .panel .desc{
    color:var(--muted);
    font-size:13.5px;
    margin:0 0 18px;
    max-width:60ch;
  }

  .controls-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:14px;
    margin-bottom:14px;
  }
  @media (max-width:640px){
    .controls-grid{ grid-template-columns:1fr 1fr; }
  }
  .field label{
    display:block;
    font-size:12.5px;
    color:var(--muted);
    margin-bottom:6px;
  }
  .field input[type=number]{
    width:100%;
    background:#0a0f1c;
    border:1px solid var(--border);
    color:var(--text);
    border-radius:6px;
    padding:9px 10px;
    font-size:14px;
    font-family: "SF Mono","JetBrains Mono", Consolas, monospace;
  }
  .field input[type=number]:focus{
    outline:2px solid var(--flame);
    outline-offset:1px;
    border-color:var(--flame);
  }

  details.advanced{
    border-top:1px dashed var(--border);
    padding-top:14px;
    margin-top:4px;
  }
  details.advanced summary{
    cursor:pointer;
    color:var(--sky);
    font-size:13px;
    margin-bottom:12px;
  }
  details.advanced summary:focus-visible{ outline:2px solid var(--sky); }

  button#runBtn{
    background:var(--flame);
    color:#fff;
    border:none;
    border-radius:7px;
    padding:11px 20px;
    font-size:14.5px;
    font-weight:600;
    cursor:pointer;
    margin-top:6px;
  }
  button#runBtn:hover{ background:#c94a22; }
  button#runBtn:focus-visible{ outline:2px solid var(--sky); outline-offset:2px; }

  .stat-row{
    display:flex;
    flex-wrap:wrap;
    gap:10px 28px;
    margin-top:16px;
    padding-top:16px;
    border-top:1px solid var(--border);
  }
  .stat{ min-width:120px; }
  .stat .k{ font-size:11.5px; color:var(--muted); margin-bottom:3px; }
  .stat .v{ font-size:17px; font-weight:700; font-family:"SF Mono","JetBrains Mono",monospace; }
  .stat .v.flame{ color:var(--flame); }
  .stat .v.sky{ color:var(--sky); }

  canvas{ display:block; width:100%; height:auto; }

  .slider-row{ display:flex; align-items:center; gap:14px; margin-bottom:14px; }
  .slider-row input[type=range]{ flex:1; accent-color:var(--sky); }
  .slider-row .mass-label{
    font-family:"SF Mono","JetBrains Mono",monospace;
    font-size:14px;
    min-width:74px;
    text-align:right;
    color:var(--sky);
  }

  .eq{
    font-family:"SF Mono","JetBrains Mono", Consolas, monospace;
    font-size:14px;
    background:#0a0f1c;
    border-left:3px solid var(--flame);
    padding:12px 14px;
    border-radius:0 6px 6px 0;
    margin:0 0 10px;
    overflow-x:auto;
    white-space:nowrap;
  }
  .eq.sky{ border-left-color:var(--sky); }
  .eq-label{
    font-size:12px;
    color:var(--muted);
    margin:18px 0 6px;
  }
  .eq-label:first-child{ margin-top:0; }

  ul.assumptions{
    margin:14px 0 0;
    padding-left:20px;
    color:var(--muted);
    font-size:13.5px;
  }
  ul.assumptions li{ margin-bottom:6px; }

  footer{
    color:var(--muted);
    font-size:12.5px;
    text-align:center;
    margin-top:34px;
  }

  code.inline{
    font-family:"SF Mono","JetBrains Mono",monospace;
    background:#0a0f1c;
    border:1px solid var(--border);
    padding:1px 5px;
    border-radius:4px;
    font-size:0.92em;
  }
</style>
</head>
<body>
<div class="wrap">

  <header class="hero">
    <div class="engine-tag"><span class="dot"></span>N2O 하이브리드 엔진 · 연소시간 4.00s</div>
    <h1>로켓이 얼마나 가벼워야 더 높이 오를까?</h1>
    <p>같은 엔진이라도 로켓 총 중량에 따라 도달 고도는 크게 달라집니다. 아래에서 중량 구간을 지정하면, 주어진 추력 곡선과 일정한 항력 조건 아래 각 중량에서의 최고 고도(정점 고도)를 계산해 그래프로 보여줍니다.</p>
  </header>

  <section class="panel" id="thrustPanel">
    <h2>엔진 추력 곡선</h2>
    <p class="desc">시뮬레이션 전체에서 고정된 입력값입니다. 제공된 추력 곡선 그래프를 아래 수식으로 근사했습니다.</p>
    <canvas id="thrustChart"></canvas>
    <div class="stat-row" id="thrustStats"></div>
  </section>

  <section class="panel" id="controlsPanel">
    <h2>중량 구간 설정</h2>
    <p class="desc">최고 고도를 비교할 로켓 총 중량(질량)의 범위를 지정하세요.</p>
    <div class="controls-grid">
      <div class="field">
        <label for="massMin">최소 중량 (kg)</label>
        <input type="number" id="massMin" value="2" min="0.2" step="0.1">
      </div>
      <div class="field">
        <label for="massMax">최대 중량 (kg)</label>
        <input type="number" id="massMax" value="16" min="0.5" step="0.1">
      </div>
      <div class="field">
        <label for="massSteps">계산 지점 수</label>
        <input type="number" id="massSteps" value="29" min="5" max="200" step="1">
      </div>
    </div>

    <details class="advanced">
      <summary>고정 상수 조정 (항력계수 · 공기저항 · 추진제 질량 · 중력)</summary>
      <div class="controls-grid">
        <div class="field">
          <label for="cdInput">항력계수 C_d</label>
          <input type="number" id="cdInput" value="0.45" min="0.05" step="0.01">
        </div>
        <div class="field">
          <label for="diaInput">로켓 직경 (m)</label>
          <input type="number" id="diaInput" value="0.10" min="0.01" step="0.005">
        </div>
        <div class="field">
          <label for="rhoInput">공기밀도 ρ (kg/m³)</label>
          <input type="number" id="rhoInput" value="1.225" min="0.1" step="0.005">
        </div>
        <div class="field">
          <label for="gInput">중력가속도 g (m/s²)</label>
          <input type="number" id="gInput" value="9.81" min="1" step="0.01">
        </div>
        <div class="field">
          <label for="propInput">추진제(연료+산화제) 질량 (kg)</label>
          <input type="number" id="propInput" value="1.5" min="0" step="0.05">
        </div>
      </div>
      <p class="desc" style="margin:10px 0 0">추진제 질량은 엔진(그레인·산화제 탱크)에 고정된 값이라 가정해 모든 중량에서 동일하게 적용됩니다. 계산 중인 총 중량이 이 값보다 가벼우면 건조질량 50g로 자동 보정됩니다.</p>
    </details>

    <button id="runBtn">시뮬레이션 실행</button>
  </section>

  <section class="panel" id="sweepPanel">
    <h2>최고 고도 vs 로켓 중량</h2>
    <p class="desc">각 중량에서 발사부터 정점(속도 = 0)까지 적분해 얻은 최고 고도입니다.</p>
    <canvas id="sweepChart"></canvas>
    <div class="stat-row" id="sweepStats"></div>
  </section>

  <section class="panel" id="detailPanel">
    <h2>개별 궤적 살펴보기</h2>
    <p class="desc">중량을 하나 선택해 시간에 따른 고도 변화를 확인하세요.</p>
    <div class="slider-row">
      <input type="range" id="massPicker">
      <span class="mass-label mono" id="massPickerLabel">- kg</span>
    </div>
    <canvas id="trajChart"></canvas>
    <div class="stat-row" id="trajStats"></div>
    <p class="desc" style="margin:20px 0 6px">추진제 연소로 줄어드는 로켓 질량 m(t)입니다.</p>
    <canvas id="massChart"></canvas>
  </section>

  <section class="panel" id="mathPanel">
    <h2>사용된 수학 모델</h2>

    <div class="eq-label">1. 운동 방정식 (뉴턴 제2법칙, 수직 1차원)</div>
    <div class="eq">m(t) · dv/dt = F(t) − m(t)·g − D(v)</div>
    <p class="desc" style="margin-top:-6px">F(t)는 추력측정값(로드셀) 자체이므로 배기가스 운동량 효과가 이미 포함되어 있어, 질량이 시간에 따라 변해도 별도의 보정항 없이 이 식을 그대로 씁니다.</p>

    <div class="eq-label">2. 항력 (드래그)</div>
    <div class="eq sky">D(v) = ½ · ρ · C_d · A · v · |v|</div>
    <p class="desc" style="margin-top:-6px">v·|v| 형태로 써서 항력이 항상 속도의 반대 방향으로 작용하도록 부호를 유지합니다. A는 로켓 단면적 = π·(직경/2)².</p>

    <div class="eq-label">3. 고도</div>
    <div class="eq">dh/dt = v</div>

    <div class="eq-label">4. 추력 곡선 F(t) — 그래프를 근사한 구간 함수</div>
    <div class="eq flame">F(t) = 1454.6 × (t / 0.09)&nbsp;&nbsp;&nbsp;[0 ≤ t ≤ 0.09s]</div>
    <div class="eq flame">F(t) = 1097.3·e^(−1.453·(t−0.09)) + 357.3·e^(−0.405·(t−0.09))&nbsp;&nbsp;&nbsp;[0.09s &lt; t ≤ 4.00s]</div>
    <div class="eq flame">F(t) = 0&nbsp;&nbsp;&nbsp;[t &lt; 0 또는 t &gt; 4.00s]</div>

    <div class="eq-label">5. 질량 변화 (추진제 소모 반영)</div>
    <div class="eq sky">m(t) = m₀ − m_prop · [ ∫₀ᵗ F(τ)dτ / I_total ]&nbsp;&nbsp;&nbsp;[0 ≤ t ≤ 4.00s]</div>
    <div class="eq sky">m(t) = m₀ − m_prop&nbsp;&nbsp;&nbsp;[t &gt; 4.00s, 건조질량]</div>
    <p class="desc" style="margin-top:-6px">m₀는 발사 시 총 중량, m_prop은 추진제 질량, I_total은 F(t)의 총 임펄스입니다. 즉 추력이 강하게 나올 때 추진제도 그만큼 빠르게 소모된다고 가정합니다 (유효 배기속도 c = I_total / m_prop 일정 가정과 동일).</p>

    <div class="eq-label">6. 수치적분</div>
    <p class="desc" style="margin:0">4차 룽게-쿠타법(RK4), Δt = 0.002s로 상태벡터 (h, v)를 적분합니다. 상승 후 v가 0 밑으로 내려가는 시점(정점)까지 계산하고, 그때까지 기록된 최대 고도를 결과로 사용합니다.</p>

    <div class="eq-label">가정</div>
    <ul class="assumptions">
      <li>추진제는 F(t)의 누적 임펄스 비율에 비례해 소모된다고 가정합니다 (유효 배기속도 일정 가정). 연소 종료 후에는 건조질량(= 총 중량 − 추진제 질량)으로 고정됩니다.</li>
      <li>C_d, 단면적 A, 공기밀도 ρ는 고도에 관계없이 일정합니다.</li>
      <li>바람, 받음각, 발사각 없이 수직으로만 상승한다고 가정합니다.</li>
      <li>추력 곡선은 위 근사식을 따르며, 원본 그래프의 미세한 연소 진동은 매끄럽게 평균화했습니다.</li>
    </ul>
  </section>

  <footer>
    추력 곡선은 업로드된 이미지의 수치(첨두 추력 1454.6N, 총 임펄스 1471.6N·s, 연소시간 4.00s)를 바탕으로 근사한 모델이며, 실제 지상연소시험 데이터로 대체하면 더 정확한 결과를 얻을 수 있습니다.
  </footer>

</div>

<script>
(function(){
  "use strict";

  /* ---------------- 추력 모델 ---------------- */
  var T_PEAK = 0.09, F_PEAK = 1454.6, BURN_TIME = 4.00;
  var A1 = 1097.3, ALPHA1 = 1.453, B1 = 357.3, BETA1 = 0.405;

  function thrust(t){
    if (t < 0 || t > BURN_TIME) return 0;
    if (t <= T_PEAK) return F_PEAK * (t / T_PEAK);
    var tt = t - T_PEAK;
    return A1*Math.exp(-ALPHA1*tt) + B1*Math.exp(-BETA1*tt);
  }

  function computeThrustStats(){
    var dt = 0.001, impulse = 0, peak = 0, peakT = 0;
    for (var t = 0; t <= BURN_TIME; t += dt){
      var f = thrust(t);
      impulse += f * dt;
      if (f > peak){ peak = f; peakT = t; }
    }
    return { impulse: impulse, peak: peak, peakT: peakT };
  }

  /* ---------------- 누적 임펄스 테이블 (질량 변화 계산용) ---------------- */
  var CUM_TABLE = (function(){
    var dt = 0.002;
    var n = Math.ceil(BURN_TIME / dt) + 1;
    var vals = new Array(n);
    var acc = 0;
    vals[0] = 0;
    var tPrev = 0, fPrev = thrust(0);
    for (var i=1;i<n;i++){
      var tCur = Math.min(i*dt, BURN_TIME);
      var fCur = thrust(tCur);
      acc += (fPrev+fCur)/2 * (tCur-tPrev);
      vals[i] = acc;
      tPrev = tCur; fPrev = fCur;
    }
    return { dt: dt, vals: vals, total: acc };
  })();

  function cumImpulseAt(t){
    if (t <= 0) return 0;
    if (t >= BURN_TIME) return CUM_TABLE.total;
    var idx = t / CUM_TABLE.dt;
    var i0 = Math.floor(idx);
    var frac = idx - i0;
    var v0 = CUM_TABLE.vals[i0];
    var v1 = CUM_TABLE.vals[Math.min(i0+1, CUM_TABLE.vals.length-1)];
    return v0 + (v1-v0)*frac;
  }

  function massAt(t, m0, propMass){
    if (propMass <= 0) return m0;
    var dryMass = m0 - propMass;
    var frac = cumImpulseAt(t) / CUM_TABLE.total;
    var m = m0 - propMass*frac;
    if (m < dryMass) m = dryMass;
    return m;
  }

  /* ---------------- 물리 시뮬레이션 ---------------- */
  function simulate(mass, propMass, cd, area, rho, g){
    var dt = 0.002;
    var t = 0, h = 0, v = 0;
    var maxH = 0, maxV = 0, apogeeTime = 0;
    var traj = [];
    var sampleEvery = 0.02, nextSample = 0;
    var liftoff = false;
    var maxSimTime = 90;
    var safeProp = Math.min(Math.max(propMass,0), Math.max(mass - 0.05, 0));

    function deriv(tt, hh, vv){
      var f = thrust(tt);
      var mCur = Math.max(massAt(tt, mass, safeProp), 0.001);
      var drag = 0.5 * rho * cd * area * vv * Math.abs(vv);
      var a = (f - mCur*g - drag) / mCur;
      return [vv, a];
    }

    while (t < maxSimTime){
      if (t >= nextSample){
        traj.push({ t: t, h: h, v: v });
        nextSample += sampleEvery;
      }

      var k1 = deriv(t, h, v);
      var k2 = deriv(t + dt/2, h + dt/2*k1[0], v + dt/2*k1[1]);
      var k3 = deriv(t + dt/2, h + dt/2*k2[0], v + dt/2*k2[1]);
      var k4 = deriv(t + dt, h + dt*k3[0], v + dt*k3[1]);

      h = h + dt/6*(k1[0] + 2*k2[0] + 2*k3[0] + k4[0]);
      v = v + dt/6*(k1[1] + 2*k2[1] + 2*k3[1] + k4[1]);
      t += dt;

      if (h < 0){ h = 0; if (v < 0) v = 0; }
      if (!liftoff && h > 0.01) liftoff = true;
      if (h > maxH){ maxH = h; apogeeTime = t; }
      if (v > maxV) maxV = v;

      if (liftoff && v < 0) break;
      if (t > BURN_TIME && h <= 0) break;
    }
    traj.push({ t: t, h: h, v: v });

    return { apogee: maxH, apogeeTime: apogeeTime, maxV: maxV, traj: traj, liftoff: liftoff, launchMass: mass, propMass: safeProp, dryMass: mass - safeProp };
  }

  /* ---------------- 캔버스 차트 유틸 ---------------- */
  function setupHiDPI(canvas, cssW, cssH){
    var dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssH * dpr);
    canvas.style.width = cssW + "px";
    canvas.style.height = cssH + "px";
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return ctx;
  }

  function chartSize(canvas, aspect){
    var w = canvas.parentElement.clientWidth;
    return { w: w, h: Math.max(200, Math.round(w * aspect)) };
  }

  function niceNum(n){
    if (Math.abs(n) >= 1000) return (n/1000).toFixed(1) + "k";
    if (Math.abs(n) >= 10) return n.toFixed(0);
    return n.toFixed(2);
  }

  function drawLineChart(canvas, aspect, series, opts){
    var size = chartSize(canvas, aspect);
    var ctx = setupHiDPI(canvas, size.w, size.h);
    var W = size.w, H = size.h;
    var padL = 52, padR = 16, padT = 22, padB = 40;
    var plotW = W - padL - padR, plotH = H - padT - padB;

    var xs = [], ys = [];
    series.forEach(function(s){
      for (var i=0;i<s.x.length;i++){ xs.push(s.x[i]); ys.push(s.y[i]); }
    });
    var xmin = Math.min.apply(null, xs), xmax = Math.max.apply(null, xs);
    var ymin = Math.min(0, Math.min.apply(null, ys));
    var ymax = Math.max.apply(null, ys);
    if (xmin === xmax) xmax = xmin + 1;
    if (ymax === ymin) ymax = ymin + 1;
    ymax = ymax * 1.1;

    function xPix(x){ return padL + (x - xmin) / (xmax - xmin) * plotW; }
    function yPix(y){ return padT + plotH - (y - ymin) / (ymax - ymin) * plotH; }

    ctx.clearRect(0,0,W,H);

    ctx.strokeStyle = "#1c2740";
    ctx.fillStyle = "#7a869c";
    ctx.font = "11px sans-serif";
    ctx.lineWidth = 1;

    var nx = 6, ny = 5;
    for (var i=0;i<=nx;i++){
      var xv = xmin + (xmax-xmin)*i/nx;
      var px = xPix(xv);
      ctx.beginPath(); ctx.moveTo(px, padT); ctx.lineTo(px, padT+plotH); ctx.stroke();
      var lbl = niceNum(xv);
      ctx.fillText(lbl, px - ctx.measureText(lbl).width/2, padT+plotH+16);
    }
    for (var j=0;j<=ny;j++){
      var yv = ymin + (ymax-ymin)*j/ny;
      var py = yPix(yv);
      ctx.beginPath(); ctx.moveTo(padL, py); ctx.lineTo(padL+plotW, py); ctx.stroke();
      ctx.fillText(niceNum(yv), 6, py+4);
    }

    ctx.strokeStyle = "#3a4666";
    ctx.lineWidth = 1.3;
    ctx.beginPath();
    ctx.moveTo(padL, padT); ctx.lineTo(padL, padT+plotH); ctx.lineTo(padL+plotW, padT+plotH);
    ctx.stroke();

    if (opts.markerX !== undefined && opts.markerX !== null){
      var mx = xPix(opts.markerX);
      ctx.save();
      ctx.strokeStyle = "#e8b34a";
      ctx.setLineDash([4,4]);
      ctx.beginPath(); ctx.moveTo(mx, padT); ctx.lineTo(mx, padT+plotH); ctx.stroke();
      ctx.restore();
    }

    series.forEach(function(s){
      ctx.strokeStyle = s.color;
      ctx.fillStyle = s.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (var i=0;i<s.x.length;i++){
        var px2 = xPix(s.x[i]), py2 = yPix(s.y[i]);
        if (i===0) ctx.moveTo(px2, py2); else ctx.lineTo(px2, py2);
      }
      ctx.stroke();
      if (s.fill){
        ctx.lineTo(xPix(s.x[s.x.length-1]), yPix(ymin));
        ctx.lineTo(xPix(s.x[0]), yPix(ymin));
        ctx.closePath();
        ctx.globalAlpha = 0.14;
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      if (s.dots){
        for (var k=0;k<s.x.length;k++){
          ctx.beginPath();
          ctx.arc(xPix(s.x[k]), yPix(s.y[k]), 2.6, 0, Math.PI*2);
          ctx.fill();
        }
      }
    });

    if (opts.highlight){
      ctx.fillStyle = "#e8b34a";
      ctx.beginPath();
      ctx.arc(xPix(opts.highlight.x), yPix(opts.highlight.y), 4.5, 0, Math.PI*2);
      ctx.fill();
    }

    ctx.fillStyle = "#8b96ad";
    ctx.font = "11.5px sans-serif";
    if (opts.xLabel) ctx.fillText(opts.xLabel, padL + plotW/2 - ctx.measureText(opts.xLabel).width/2, H-6);
    if (opts.yLabel){
      ctx.save();
      ctx.translate(12, padT + plotH/2 + ctx.measureText(opts.yLabel).width/2);
      ctx.rotate(-Math.PI/2);
      ctx.fillText(opts.yLabel, 0, 0);
      ctx.restore();
    }
  }

  /* ---------------- 포맷 유틸 ---------------- */
  function fmtAlt(m){
    if (Math.abs(m) >= 1000) return (m/1000).toFixed(2) + " km";
    return m.toFixed(1) + " m";
  }
  function fmtT(t){ return t.toFixed(2) + " s"; }
  function fmtV(v){ return v.toFixed(1) + " m/s"; }
  function fmtN(n){ return n.toFixed(1) + " N"; }
  function fmtNs(n){ return n.toFixed(1) + " N·s"; }
  function fmtKg(m){ return m.toFixed(2) + " kg"; }

  /* ---------------- 상태 ---------------- */
  var lastSweep = null; // {masses, altitudes, bestIdx, cd, area, rho, g}
  var lastTraj = null;

  function readConsts(){
    return {
      cd: parseFloat(document.getElementById("cdInput").value) || 0.45,
      dia: parseFloat(document.getElementById("diaInput").value) || 0.10,
      rho: parseFloat(document.getElementById("rhoInput").value) || 1.225,
      g: parseFloat(document.getElementById("gInput").value) || 9.81,
      propMass: Math.max(0, parseFloat(document.getElementById("propInput").value) || 0)
    };
  }

  function drawThrustChart(){
    var ts = [], fs = [];
    for (var t=-0.1; t<=BURN_TIME+0.15; t+=0.01){
      ts.push(t); fs.push(thrust(t));
    }
    drawLineChart(document.getElementById("thrustChart"), 0.40,
      [{ x: ts, y: fs, color: "#e2572b", fill: true }],
      { xLabel: "연소 시간 (s)", yLabel: "추력 (N)" }
    );

    var st = computeThrustStats();
    var box = document.getElementById("thrustStats");
    box.innerHTML =
      '<div class="stat"><div class="k">모델 첨두 추력</div><div class="v flame">' + fmtN(st.peak) + '</div></div>' +
      '<div class="stat"><div class="k">모델 총 임펄스</div><div class="v flame">' + fmtNs(st.impulse) + '</div></div>' +
      '<div class="stat"><div class="k">연소 시간</div><div class="v">' + fmtT(BURN_TIME) + '</div></div>' +
      '<div class="stat"><div class="k">원본 그래프 값</div><div class="v" style="font-size:13px;color:#8b96ad">1454.6N · 1471.6N·s · 4.00s</div></div>';
  }

  function runSweep(){
    var massMin = Math.max(0.05, parseFloat(document.getElementById("massMin").value) || 2);
    var massMax = Math.max(massMin + 0.1, parseFloat(document.getElementById("massMax").value) || 16);
    var steps = Math.min(200, Math.max(5, Math.round(parseFloat(document.getElementById("massSteps").value) || 29)));

    var c = readConsts();
    var area = Math.PI * Math.pow(c.dia/2, 2);

    var masses = [], altitudes = [];
    var bestIdx = 0, bestAlt = -1;

    for (var i=0;i<steps;i++){
      var m = massMin + (massMax - massMin) * i/(steps-1);
      var res = simulate(m, c.propMass, c.cd, area, c.rho, c.g);
      masses.push(m);
      altitudes.push(res.apogee);
      if (res.apogee > bestAlt){ bestAlt = res.apogee; bestIdx = i; }
    }

    lastSweep = { masses: masses, altitudes: altitudes, bestIdx: bestIdx, cd: c.cd, area: area, rho: c.rho, g: c.g, propMass: c.propMass, massMin: massMin, massMax: massMax };

    drawSweepChart();
    updateSweepStats();
    setupPicker(massMin, massMax, masses[bestIdx]);
    runTrajectory(masses[bestIdx]);
  }

  function drawSweepChart(){
    if (!lastSweep) return;
    var markerX = lastTraj ? lastTraj.mass : null;
    drawLineChart(document.getElementById("sweepChart"), 0.44,
      [{ x: lastSweep.masses, y: lastSweep.altitudes, color: "#43b7c4", dots: true }],
      {
        xLabel: "로켓 중량 (kg)", yLabel: "최고 고도 (m)",
        markerX: markerX,
        highlight: { x: lastSweep.masses[lastSweep.bestIdx], y: lastSweep.altitudes[lastSweep.bestIdx] }
      }
    );
  }

  function updateSweepStats(){
    var box = document.getElementById("sweepStats");
    var bm = lastSweep.masses[lastSweep.bestIdx];
    var ba = lastSweep.altitudes[lastSweep.bestIdx];
    box.innerHTML =
      '<div class="stat"><div class="k">최고 고도 지점 중량</div><div class="v sky">' + fmtKg(bm) + '</div></div>' +
      '<div class="stat"><div class="k">해당 최고 고도</div><div class="v sky">' + fmtAlt(ba) + '</div></div>' +
      '<div class="stat"><div class="k">계산 지점 수</div><div class="v">' + lastSweep.masses.length + '</div></div>';
  }

  function setupPicker(min, max, initial){
    var picker = document.getElementById("massPicker");
    picker.min = min;
    picker.max = max;
    picker.step = Math.max(0.02, (max-min)/200);
    picker.value = initial;
  }

  function runTrajectory(mass){
    if (!lastSweep) return;
    var res = simulate(mass, lastSweep.propMass, lastSweep.cd, lastSweep.area, lastSweep.rho, lastSweep.g);
    lastTraj = { mass: mass, res: res };

    var ts = res.traj.map(function(p){ return p.t; });
    var hs = res.traj.map(function(p){ return p.h; });
    var ms = ts.map(function(tt){ return massAt(tt, res.launchMass, res.propMass); });

    drawLineChart(document.getElementById("trajChart"), 0.40,
      [{ x: ts, y: hs, color: "#e2572b", fill: true }],
      { xLabel: "시간 (s)", yLabel: "고도 (m)" }
    );
    drawLineChart(document.getElementById("massChart"), 0.28,
      [{ x: ts, y: ms, color: "#43b7c4", fill: true }],
      { xLabel: "시간 (s)", yLabel: "질량 (kg)" }
    );

    document.getElementById("massPickerLabel").textContent = fmtKg(mass);

    var box = document.getElementById("trajStats");
    box.innerHTML =
      '<div class="stat"><div class="k">최고 고도</div><div class="v flame">' + fmtAlt(res.apogee) + '</div></div>' +
      '<div class="stat"><div class="k">정점 도달 시각</div><div class="v">' + fmtT(res.apogeeTime) + '</div></div>' +
      '<div class="stat"><div class="k">최대 속도</div><div class="v">' + fmtV(res.maxV) + '</div></div>' +
      '<div class="stat"><div class="k">발사 질량 → 건조 질량</div><div class="v" style="font-size:14px">' + fmtKg(res.launchMass) + ' → ' + fmtKg(res.dryMass) + '</div></div>' +
      '<div class="stat"><div class="k">이륙 여부</div><div class="v" style="color:' + (res.liftoff ? '#43b7c4' : '#e2572b') + '">' + (res.liftoff ? '성공' : '실패 (추력 부족)') + '</div></div>';

    drawSweepChart();
  }

  /* ---------------- 이벤트 ---------------- */
  document.getElementById("runBtn").addEventListener("click", runSweep);
  document.getElementById("massPicker").addEventListener("input", function(){
    runTrajectory(parseFloat(this.value));
  });

  var resizeTimer = null;
  window.addEventListener("resize", function(){
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function(){
      drawThrustChart();
      if (lastSweep) drawSweepChart();
      if (lastTraj) runTrajectory(lastTraj.mass);
    }, 150);
  });

  /* ---------------- 초기 실행 ---------------- */
  drawThrustChart();
  runSweep();

})();
</script>
</body>
</html>
