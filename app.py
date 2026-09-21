"""
로켓 중량 vs 최고 고도 시뮬레이터 (Streamlit)
------------------------------------------------
같은 엔진(추력-시간 곡선)에서 로켓 총 중량을 바꿔가며 발사~정점까지 수직 1차원
운동방정식을 수치적분해, 중량에 따라 달라지는 최고 고도를 계산/시각화합니다.

실행:
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="로켓 중량 vs 최고 고도 시뮬레이터", page_icon="🚀", layout="wide")

# ---------------- 엔진 추력 모델 (업로드된 그래프를 근사) ----------------
T_PEAK = 0.09
F_PEAK = 1454.6
BURN_TIME = 4.00
A1, ALPHA1 = 1097.3, 1.453
B1, BETA1 = 357.3, 0.405


def thrust(t: float) -> float:
    """추력-시간 곡선 F(t). 실측 그래프(첨두 1454.6N, 총 임펄스 1471.6N·s,
    연소시간 4.00s)를 근사한 구간함수."""
    if t < 0 or t > BURN_TIME:
        return 0.0
    if t <= T_PEAK:
        return F_PEAK * (t / T_PEAK)
    tt = t - T_PEAK
    return A1 * math.exp(-ALPHA1 * tt) + B1 * math.exp(-BETA1 * tt)


@st.cache_data(show_spinner=False)
def build_cum_impulse_table(dt: float = 0.002):
    """추진제 소모(질량 변화) 계산에 쓸 누적 임펄스 테이블. F(t)는 고정이므로 캐시."""
    n = int(math.ceil(BURN_TIME / dt)) + 1
    ts = np.array([min(i * dt, BURN_TIME) for i in range(n)])
    fs = np.array([thrust(t) for t in ts])
    incr = np.zeros(n)
    incr[1:] = (fs[1:] + fs[:-1]) / 2 * np.diff(ts)
    cum = np.cumsum(incr)
    return ts, cum


def cum_impulse_at(t, ts, cum):
    if t <= 0:
        return 0.0
    if t >= BURN_TIME:
        return float(cum[-1])
    return float(np.interp(t, ts, cum))


def mass_at(t, m0, prop_mass, ts, cum):
    if prop_mass <= 0:
        return m0
    dry_mass = m0 - prop_mass
    frac = cum_impulse_at(t, ts, cum) / cum[-1]
    m = m0 - prop_mass * frac
    return max(m, dry_mass)


def simulate(mass, prop_mass, cd, area, rho, g, ts, cum,
             dt=0.002, max_sim_time=90.0, sample_every=0.02):
    """뉴턴 운동방정식 m·dv/dt = F(t) - m·g - D(v)를 RK4로 적분."""
    t, h, v = 0.0, 0.0, 0.0
    max_h, max_v, apogee_time = 0.0, 0.0, 0.0
    liftoff = False
    safe_prop = min(max(prop_mass, 0.0), max(mass - 0.05, 0.0))
    traj_t, traj_h, traj_v = [], [], []
    next_sample = 0.0

    def deriv(tt, hh, vv):
        f = thrust(tt)
        m_cur = max(mass_at(tt, mass, safe_prop, ts, cum), 1e-3)
        drag = 0.5 * rho * cd * area * vv * abs(vv)
        a = (f - m_cur * g - drag) / m_cur
        return vv, a

    while t < max_sim_time:
        if t >= next_sample:
            traj_t.append(t); traj_h.append(h); traj_v.append(v)
            next_sample += sample_every

        k1 = deriv(t, h, v)
        k2 = deriv(t + dt / 2, h + dt / 2 * k1[0], v + dt / 2 * k1[1])
        k3 = deriv(t + dt / 2, h + dt / 2 * k2[0], v + dt / 2 * k2[1])
        k4 = deriv(t + dt, h + dt * k3[0], v + dt * k3[1])

        h += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        v += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        t += dt

        if h < 0:
            h = 0.0
            if v < 0:
                v = 0.0
        if not liftoff and h > 0.01:
            liftoff = True
        if h > max_h:
            max_h, apogee_time = h, t
        if v > max_v:
            max_v = v

        if liftoff and v < 0:
            break
        if t > BURN_TIME and h <= 0:
            break

    traj_t.append(t); traj_h.append(h); traj_v.append(v)

    return {
        "apogee": max_h, "apogee_time": apogee_time, "max_v": max_v,
        "liftoff": liftoff, "launch_mass": mass, "prop_mass": safe_prop,
        "dry_mass": mass - safe_prop,
        "traj": pd.DataFrame({"t": traj_t, "h": traj_h, "v": traj_v}),
    }


@st.cache_data(show_spinner=False)
def run_sweep(mass_min, mass_max, steps, cd, dia, rho, g, prop_mass):
    ts, cum = build_cum_impulse_table()
    area = math.pi * (dia / 2) ** 2
    masses = np.linspace(mass_min, mass_max, steps)
    altitudes = np.array([
        simulate(m, prop_mass, cd, area, rho, g, ts, cum)["apogee"] for m in masses
    ])
    return masses, altitudes


@st.cache_data(show_spinner=False)
def run_single(mass, cd, dia, rho, g, prop_mass):
    ts, cum = build_cum_impulse_table()
    area = math.pi * (dia / 2) ** 2
    res = simulate(mass, prop_mass, cd, area, rho, g, ts, cum)
    res["traj"]["m"] = [mass_at(tt, res["launch_mass"], res["prop_mass"], ts, cum) for tt in res["traj"]["t"]]
    return res


def line_fig(x, y, color, x_title, y_title, fill=True):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", fill="tozeroy" if fill else None,
                              line=dict(color=color, width=2)))
    fig.update_layout(height=310, margin=dict(l=10, r=10, t=10, b=10),
                       xaxis_title=x_title, yaxis_title=y_title,
                       paper_bgcolor="rgba(0,0,0,0)", template="plotly_white")
    return fig


# ---------------- UI ----------------
st.title("🚀 로켓이 얼마나 가벼워야 더 높이 오를까?")
st.caption("하이브리드 엔진 · 연소시간 4.00s")
st.write(
    "같은 엔진이라도 로켓 총 중량에 따라 도달 고도는 크게 달라집니다. "
    "아래에서 중량 구간을 지정하면, 주어진 추력 곡선과 일정한 항력 조건 아래 "
    "각 중량에서의 최고 고도(정점 고도)를 계산해 그래프로 보여줍니다."
)

with st.sidebar:
    st.header("중량 구간 설정")
    mass_min = st.number_input("최소 중량 (kg)", min_value=0.05, value=2.0, step=0.1)
    mass_max = st.number_input("최대 중량 (kg)", min_value=0.1, value=16.0, step=0.1)
    if mass_max <= mass_min:
        mass_max = mass_min + 0.1
    steps = st.slider("계산 지점 수", min_value=5, max_value=100, value=29)

    st.divider()
    success_alt = st.number_input(
        "미션 성공 기준 고도 (m)", min_value=1.0, value=50.0, step=5.0,
        help="이 고도 이상 도달해야 성공으로 표시합니다.",
    )

    with st.expander("고정 상수 조정 (항력계수 · 공기밀도 · 추진제 질량 · 중력)"):
        cd = st.number_input("항력계수 C_d", min_value=0.05, value=0.45, step=0.01)
        dia = st.number_input("로켓 직경 (m)", min_value=0.01, value=0.10, step=0.005, format="%.3f")
        rho = st.number_input("공기밀도 ρ (kg/m³)", min_value=0.1, value=1.225, step=0.005)
        g = st.number_input("중력가속도 g (m/s²)", min_value=1.0, value=9.81, step=0.01)
        prop_mass = st.number_input("추진제(연료+산화제) 질량 (kg)", min_value=0.0, value=1.5, step=0.05)
        st.caption(
            "추진제 질량은 엔진(그레인·산화제 탱크)에 고정된 값이라 가정해 모든 중량에서 동일하게 "
            "적용됩니다. 계산 중인 총 중량이 이 값보다 가벼우면 건조질량 50g로 자동 보정됩니다."
        )

# ---------- 1. 엔진 추력 곡선 ----------
st.subheader("엔진 추력 곡선")
st.caption("시뮬레이션 전체에서 고정된 입력값입니다. 제공된 추력 곡선 그래프를 근사식으로 재현했습니다.")

t_grid = np.arange(-0.1, BURN_TIME + 0.15, 0.01)
f_grid = np.array([thrust(t) for t in t_grid])
st.plotly_chart(line_fig(t_grid, f_grid, "#e2572b", "연소 시간 (s)", "추력 (N)"), use_container_width=True)

ts0, cum0 = build_cum_impulse_table()
c1, c2, c3, c4 = st.columns(4)
c1.metric("모델 첨두 추력", f"{f_grid.max():.1f} N")
c2.metric("모델 총 임펄스", f"{cum0[-1]:.1f} N·s")
c3.metric("연소 시간", f"{BURN_TIME:.2f} s")
c4.metric("원본 그래프 값", "1454.6N · 1471.6N·s · 4.00s")

# ---------- 2. 최고 고도 vs 로켓 중량 ----------
st.subheader("최고 고도 vs 로켓 중량")
st.caption("각 중량에서 발사부터 정점(속도 = 0)까지 적분해 얻은 최고 고도입니다.")

with st.spinner("중량 구간을 스캔하는 중..."):
    masses, altitudes = run_sweep(mass_min, mass_max, steps, cd, dia, rho, g, prop_mass)

best_idx = int(np.argmax(altitudes))
success_mask = altitudes >= success_alt

fig_sweep = go.Figure()
fig_sweep.add_trace(go.Scatter(x=masses, y=altitudes, mode="lines", line=dict(color="#adb5bd", width=1.5),
                                showlegend=False))
fig_sweep.add_trace(go.Scatter(x=masses[success_mask], y=altitudes[success_mask], mode="markers",
                                marker=dict(size=7, color="#2f9e44"), name=f"성공 (≥{success_alt:.0f}m)"))
fig_sweep.add_trace(go.Scatter(x=masses[~success_mask], y=altitudes[~success_mask], mode="markers",
                                marker=dict(size=7, color="#e03131"), name=f"실패 (<{success_alt:.0f}m)"))
fig_sweep.add_trace(go.Scatter(x=[masses[best_idx]], y=[altitudes[best_idx]], mode="markers",
                                marker=dict(size=13, color="#e8b34a", symbol="star"), name="최고 지점"))
fig_sweep.add_hline(y=success_alt, line_dash="dot", line_color="#868e96",
                     annotation_text=f"성공 기준 {success_alt:.0f}m", annotation_position="top left")
fig_sweep.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10),
                         xaxis_title="로켓 중량 (kg)", yaxis_title="최고 고도 (m)",
                         paper_bgcolor="rgba(0,0,0,0)", template="plotly_white")
st.plotly_chart(fig_sweep, use_container_width=True)

s1, s2, s3, s4 = st.columns(4)
s1.metric("최고 고도 지점 중량", f"{masses[best_idx]:.2f} kg")
alt_disp = f"{altitudes[best_idx]:.1f} m" if altitudes[best_idx] < 1000 else f"{altitudes[best_idx] / 1000:.2f} km"
s2.metric("해당 최고 고도", alt_disp)
if success_mask.any():
    s3.metric("성공 중량 범위", f"{masses[success_mask].min():.2f} ~ {masses[success_mask].max():.2f} kg")
else:
    s3.metric("성공 중량 범위", "없음")
s4.metric("성공 / 전체 지점", f"{int(success_mask.sum())} / {len(masses)}")

# ---------- 3. 개별 궤적 ----------
st.subheader("개별 궤적 살펴보기")
st.caption("중량을 하나 선택해 시간에 따른 고도 변화를 확인하세요.")

pick_mass = st.slider(
    "로켓 중량 (kg)",
    min_value=float(masses.min()), max_value=float(masses.max()),
    value=float(masses[best_idx]),
    step=max(0.02, float((masses.max() - masses.min()) / 200)),
)

with st.spinner("궤적 계산 중..."):
    res = run_single(pick_mass, cd, dia, rho, g, prop_mass)
traj = res["traj"]

if res["apogee"] >= success_alt:
    st.success(f"✅ 미션 성공 — 최고 고도 {res['apogee']:.1f} m (기준 {success_alt:.0f} m 이상)")
else:
    st.error(f"❌ 미션 실패 — 최고 고도 {res['apogee']:.1f} m (기준 {success_alt:.0f} m 미달)")

colA, colB = st.columns(2)
with colA:
    st.plotly_chart(line_fig(traj["t"], traj["h"], "#e2572b", "시간 (s)", "고도 (m)"), use_container_width=True)
with colB:
    st.plotly_chart(line_fig(traj["t"], traj["m"], "#43b7c4", "시간 (s)", "질량 (kg)"), use_container_width=True)

d1, d2, d3, d4, d5 = st.columns(5)
d1.metric("최고 고도", f"{res['apogee']:.1f} m")
d2.metric("정점 도달 시각", f"{res['apogee_time']:.2f} s")
d3.metric("최대 속도", f"{res['max_v']:.1f} m/s")
d4.metric("발사→건조 질량", f"{res['launch_mass']:.2f}→{res['dry_mass']:.2f} kg")
d5.metric("이륙 여부", "성공" if res["liftoff"] else "실패")

# ---------- 4. 수학 모델 ----------
st.subheader("사용된 수학 모델")

st.markdown("**1. 운동 방정식 (뉴턴 제2법칙, 수직 1차원)**")
st.latex(r"m(t)\,\frac{dv}{dt} = F(t) - m(t)\,g - D(v)")
st.caption("F(t)는 추력측정값(로드셀) 자체이므로 배기가스 운동량 효과가 이미 포함되어 있어, "
           "질량이 시간에 따라 변해도 별도의 보정항 없이 이 식을 그대로 씁니다.")

st.markdown("**2. 항력 (드래그)**")
st.latex(r"D(v) = \frac{1}{2}\,\rho\,C_d\,A\,v\,|v|")
st.caption("v·|v| 형태로 써서 항력이 항상 속도의 반대 방향으로 작용하도록 부호를 유지합니다. "
           "A는 로켓 단면적 = π·(직경/2)²이며, C_d·ρ·A 모두 비행 내내 일정하다고 가정합니다.")

st.markdown("**3. 고도**")
st.latex(r"\frac{dh}{dt} = v")

st.markdown("**4. 추력 곡선 F(t) — 그래프를 근사한 구간함수**")
st.latex(r"""
F(t)=\begin{cases}
1454.6 \times \dfrac{t}{0.09} & 0 \le t \le 0.09\text{s}\\[6pt]
1097.3\,e^{-1.453(t-0.09)} + 357.3\,e^{-0.405(t-0.09)} & 0.09\text{s} < t \le 4.00\text{s}\\[6pt]
0 & \text{그 외}
\end{cases}
""")

st.markdown("**5. 질량 변화 (추진제 소모 반영)**")
st.latex(r"m(t) = m_0 - m_{prop}\cdot\dfrac{\int_0^t F(\tau)\,d\tau}{I_{total}} \quad (0 \le t \le 4.00\text{s})")
st.latex(r"m(t) = m_0 - m_{prop} \quad (t > 4.00\text{s, 건조질량})")
st.caption("m₀는 발사 시 총 중량, m_prop은 추진제 질량, I_total은 F(t)의 총 임펄스입니다. "
           "추력이 강하게 나올 때 추진제도 그만큼 빠르게 소모된다고 가정합니다 "
           "(유효 배기속도 c = I_total / m_prop 일정 가정과 동일).")

st.markdown("**6. 수치적분**")
st.write("4차 룽게-쿠타법(RK4), Δt = 0.002s로 상태벡터 (h, v)를 적분합니다. "
         "상승 후 v가 0 밑으로 내려가는 시점(정점)까지 계산하고, 그때까지 기록된 최대 고도를 결과로 사용합니다.")

st.markdown("**가정**")
st.markdown(
    "- 추진제는 F(t)의 누적 임펄스 비율에 비례해 소모된다고 가정합니다(유효 배기속도 일정 가정). "
    "연소 종료 후에는 건조질량(= 총 중량 − 추진제 질량)으로 고정됩니다.\n"
    "- C_d, 단면적 A, 공기밀도 ρ는 고도에 관계없이 일정합니다.\n"
    "- 바람, 받음각, 발사각 없이 수직으로만 상승한다고 가정합니다.\n"
    "- 추력 곡선은 위 근사식을 따르며, 원본 그래프의 미세한 연소 진동은 매끄럽게 평균화했습니다."
)

st.divider()
st.caption(
    "추력 곡선은 업로드된 이미지의 수치(첨두 추력 1454.6N, 총 임펄스 1471.6N·s, 연소시간 4.00s)를 "
    "바탕으로 근사한 모델이며, 실제 지상연소시험 데이터로 대체하면 더 정확한 결과를 얻을 수 있습니다."
)
