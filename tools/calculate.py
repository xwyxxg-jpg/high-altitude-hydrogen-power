"""Concept-level balances and uncalibrated thermal sensitivity, SI units."""
from pathlib import Path
import json
import math
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')
OUT = Path(__file__).resolve().parents[1] / 'calculations'
OUT.mkdir(parents=True, exist_ok=True)
F, R = 96485.33212, 8.314462618
N, I, v, eta, utilization = 70, 156, 0.65, 0.96, 0.98
n = N * I / (2 * F)
gross = N * I * v
consumed = n * 2.01588e-3
feed = consumed / utilization
air = N * I / (4 * F) / 0.2095 * 0.028965 * 2.5
result = {
    'classification': 'calculated estimates, not validated hardware performance',
    'stack_cells': N, 'current_A': I, 'gross_W': gross,
    'net_W_aux1300': gross * eta - 1300,
    'net_W_after_6pct_voltage_loss_aux1300': gross * .94 * eta - 1300,
    'old55_net_W_aux1300': 55 * I * v * eta - 1300,
    'H2_reacted_kg_h': consumed * 3600,
    'H2_fed_kg_h': feed * 3600,
    'H2_fed_NL_min_0C_1atm': n / utilization * 22.41397 * 60,
    'water_kg_h': n * .01801528 * 3600,
    'air_g_s_lambda2_5': air * 1000,
    'air_NL_min_0C_1atm': air / .028965 * 22.41397 * 60,
    'stack_heat_LHV_W': n * 241826 - gross,
    'stack_heat_HHV_W': n * 285830 - gross,
    'bed_desorption_heat_W': n / utilization * 31200,
    'main_loop_heat_W_at30Lmin_delta5': 30 / 60 * 1.07 * 3400 * 5,
    'secondary_heat_W_at15Lmin_delta6': 15 / 60 * 1.07 * 3400 * 6,
    'battery_20s2p_Wh': 20 * 2 * 20 * 2.3,
    'battery_cell_mass_kg': 40 * .545,
    'battery_usable_cold_Wh_assumed': 20 * 2 * 20 * 2.3 * .60 * .60 * .94,
    'startup_120s_Wh_at9kW': 9000 * 120 / 3600,
    'module_alloy_kg': 60,
    'total_alloy_kg': 240,
    'bed_working_H2_kg_assuming_1wtpct_90pct_delivery': 240 * .01 * .90,
}
# Gas inventory is based on fill temperature, not pressure held fixed after cold soak.
V, pfull, Tfill, Z = .0136, 35e6, 288.15, 1.22
gas_full = pfull * V * .00201588 / (Z * R * Tfill)
gas_res = 2e6 * V * .00201588 / (1.02 * R * 243.15)
result.update({'gas_inventory_full_kg': gas_full,
               'gas_inventory_usable_kg': gas_full - gas_res,
               'gas_only_bridge_min_full_current': (gas_full - gas_res) / feed / 60,
               'total_usable_H2_kg': 2.16 + gas_full - gas_res,
               'five_hour_H2_kg': feed * 5 * 3600,
               'five_hour_after_startup_H2_kg': feed * (5 * 3600 + 120)})
result['runtime_h_with_10pct_operational_reserve'] = result['total_usable_H2_kg'] * .9 / (feed * 3600)
altitudes = []
for h in (0, 2000, 4000, 5000):
    p = 101325 * (1 - 2.25577e-5 * h)**5.25588
    for Tc in (-30, 20):
        T = Tc + 273.15
        density = p / (287.05 * T)
        pr = (p + 25000) / p
        shaft = air * 1005 * T * (pr**(0.4/1.4)-1) / .55
        altitudes.append({'altitude_m': h, 'ambient_C': Tc, 'ambient_kPaA': p/1000,
                          'air_m3_h': air/density*3600, 'compressor_pressure_ratio': pr,
                          'compressor_electrical_W_55pct_overall_eff': shaft})
result['altitude_cases'] = altitudes
result['PCT_extrapolation'] = [
    {'temperature_C': Tc,
     'industrial_mean_barA': math.exp(110/R-31200/R/(Tc+273.15)),
     'lab_s6_plateau1_barA': math.exp(103/R-30600/R/(Tc+273.15))}
    for Tc in (-30, 10, 25, 40, 50, 55, 60)]

# Four separately switched beds; isothermal-node model; imposed available heat.
# Desorption is a heat sink only, not a calibrated kinetic/PCT prediction.
def bed_model(UA, C=45000, max_heat=5000, dt=.5):
    T = [-30.] * 4
    ready = [None] * 4
    series = []
    minimum_feeding_temperature = 1e9
    energy, sensible, losses, reaction = 0., 0., 0., 0.
    for step in range(int(120*60/dt)):
        t = step * dt
        available = max_heat if t >= 180 else 0.
        feeding = next((i for i in range(4) if ready[i] is not None), None)
        qrx = [0.] * 4
        if feeding is not None:
            qrx[feeding] = result['bed_desorption_heat_W']
        heating = [0.] * 4
        for k in ([feeding] if feeding is not None else []) + [i for i in range(4) if i != feeding]:
            target = 55 if ready[k] is not None else 53
            qneed = qrx[k] + 1.5*(T[k]+30) + max(0., (target-T[k])) * C/dt
            heating[k] = max(0., min(available, UA*(63-T[k]), qneed))
            available -= heating[k]
            if available <= 0:
                break
        for k in range(4):
            qloss = 1.5 * (T[k] + 30)
            dE = (heating[k]-qrx[k]-qloss)*dt
            T[k] += dE/C
            energy += heating[k]*dt
            losses += qloss*dt
            reaction += qrx[k]*dt
            sensible += dE
            if T[k] >= 52 and ready[k] is None:
                ready[k] = t
        if feeding is not None:
            minimum_feeding_temperature = min(minimum_feeding_temperature, T[feeding])
        if step % 20 == 0:
            series.append([t/60] + T[:])
        if all(x is not None for x in ready):
            break
    return {'UA_W_K_per_bed': UA, 'heat_capacity_J_K_per_bed': C,
            'ready_min': [r/60 if r is not None else None for r in ready],
            'minimum_feeding_temperature_C': minimum_feeding_temperature,
            'thermal_supply_screen_pass': minimum_feeding_temperature >= 52,
            'residual_J': energy-sensible-losses-reaction,
            'series': series}
beds = [bed_model(ua) for ua in (100, 200, 300)]
result['bed_sensitivity'] = [{k:v for k,v in b.items() if k != 'series'} for b in beds]
result['stack_thermal_screen'] = [
    {'C_kJ_K': C, 'net_heat_kW': heat,
     'time_to_15C_s_plus14s_selfcheck_plus10s_stable': C*45/heat+24,
     'scope': 'necessary energy-only screen; excludes ice blockage, hydration and voltage recovery'}
    for C in (12,18,24) for heat in (4,6,8)]
assert abs(result['stack_heat_HHV_W'] + gross - n*285830) < 1e-8
assert all(abs(b['residual_J']) < 1 for b in beds)
assert result['gas_inventory_usable_kg'] > 0
(OUT / 'parameters.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'bed_model.json').write_text(json.dumps(beds), encoding='utf-8')
plt.rcParams.update({'font.family':'Microsoft YaHei', 'axes.unicode_minus':False, 'font.size':10})
fig, ax = plt.subplots(figsize=(9,4.2), layout='constrained')
for j in range(4):
    ax.plot([r[0] for r in beds[2]['series']], [r[j+1] for r in beds[2]['series']], label=f'储氢罐 {j+1}')
ax.axhline(52,color='#777777',linestyle='--',linewidth=1,label='温度门槛 52℃')
ax.set(xlabel='启动后时间 / min',ylabel='集中参数床温 / ℃',title='分罐预热估算：UA=300 W/K，单罐热容45 kJ/K，总可用热5 kW')
ax.legend(ncol=3,fontsize=9); ax.grid(alpha=.2)
fig.savefig(OUT/'bed_warmup.png',dpi=180);plt.close(fig)
fig, ax = plt.subplots(figsize=(9,4.2),layout='constrained')
temps=list(range(-30,66))
ax.semilogy(temps,[math.exp(103/R-30600/R/(x+273.15)) for x in temps],label='实验室 s6 第一平台外推')
ax.semilogy(temps,[math.exp(110/R-31200/R/(x+273.15)) for x in temps],label='工业材料平均参数外推')
ax.axhline(2.7,color='#c0392b',linestyle='--',label='供氢资格压力初值 2.7 barA')
ax.set(xlabel='床温 / ℃',ylabel='平衡压力 / barA',title='Van’t Hoff 外推只用于筛选，不能代替完整 PCT 与动力学试验')
ax.grid(alpha=.2);ax.legend(fontsize=9)
fig.savefig(OUT/'pct_screen.png',dpi=180);plt.close(fig)
print(json.dumps(result, ensure_ascii=False, indent=2))
