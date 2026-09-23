"""Concept sizing, not vendor qualification. SI units except explicitly labelled."""
from pathlib import Path
import json
import math
import sys
import numpy as np
from scipy.optimize import root
import CoolProp
from CoolProp.CoolProp import PropsSI

OUT = Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(exist_ok=True)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
F, MH2, MO2 = 96485.33212, 0.00201588, 0.031998

def solve(cell_v=0.75, cathode_dp=15000., rad_dp=180., aux_fixed=100.,
          face_ua=1000., net=5000., hours=4.):
    # All are engineering assumptions, not fitted vendor curves.
    N, eta_dc, eta_h2, lam_air = 119, .96, .97, 2.2
    ambient, hot, cold = 308.15, 333.15, 328.15
    altitude = 4000.
    patm = 101325*(1-2.25577e-5*altitude)**5.25588
    rho_air = patm/(287.05*ambient)
    cp_air, cp_liq, rho_liq = 1006., 3300., 1060.
    face_speed, eta_fan, eta_pump, eta_blower = 3., .35, .30, .50
    def state(x):
        I, area, mdot_liq = x
        gross = N*cell_v*I
        h2react = N*I*MH2/(2*F)
        air = N*I*MO2/(4*F)/.232*lam_air
        # Isentropic compression estimate; maps and humidity not available.
        blower = air*cp_air*ambient*((1+cathode_dp/patm)**(.4/1.4)-1)/eta_blower
        v_air_rad = face_speed*area
        fan = rad_dp*v_air_rad/eta_fan
        qv = mdot_liq/rho_liq
        dp_liq = 80000*(qv/(20e-3/60))**2
        pump = qv*dp_liq/eta_pump
        # HHV thermoneutral heat; 15% allocated to gas/water enthalpy and surroundings.
        qreaction = N*I*(1.481-cell_v)
        qcool = .85*qreaction + pump
        ca, cl = rho_air*v_air_rad*cp_air, mdot_liq*cp_liq
        cmin, cmax = min(ca, cl), max(ca, cl)
        cr = cmin/cmax
        ntu = face_ua*area/cmin
        eps = (1-math.exp(-ntu*(1-cr)))/(1-cr*math.exp(-ntu*(1-cr)))
        qrad = .85*eps*cmin*(hot-ambient)  # assumed crossflow/layout correction
        return dict(current_a=I,stack_v=N*cell_v,gross_w=gross,
                    net_w=eta_dc*gross-blower-fan-pump-aux_fixed,
                    coolant_heat_w=qcool,radiator_heat_w=qrad,
                    reaction_heat_hhv_w=qreaction,
                    exhaust_and_other_heat_w=.15*qreaction,
                    dc_loss_w=(1-eta_dc)*gross,blower_w=blower,fan_w=fan,
                    pump_w=pump,fixed_aux_w=aux_fixed,
                    radiator_face_m2=area,radiator_air_m3h=v_air_rad*3600,
                    radiator_air_out_c=ambient-273.15+qrad/ca,
                    coolant_l_min=qv*60000,coolant_dp_pa=dp_liq,
                    coolant_head_m=dp_liq/(rho_liq*9.80665),
                    coolant_mdot=mdot_liq,air_g_s=air*1000,
                    air_inlet_m3h=air/rho_air*3600,
                    h2_reacted_kg_h=h2react*3600,
                    h2_fresh_kg_h=h2react/eta_h2*3600,
                    water_kg_h=N*I*0.01801528/(2*F)*3600,
                    altitude_m=altitude,ambient_pressure_pa=patm,
                    rho_air=rho_air,cell_voltage_assumption=cell_v,
                    face_ua_assumption_w_m2k=face_ua)
    def residual(x):
        s=state(x)
        return [(s["net_w"]-net)/5000,
                (s["radiator_heat_w"]-s["coolant_heat_w"])/5000,
                (x[2]*cp_liq*(hot-cold)-s["coolant_heat_w"])/5000]
    sol=root(residual,[65.,.4,.3])
    assert sol.success and np.all(sol.x>0), sol.message
    assert max(abs(np.array(residual(sol.x)))) < 1e-7
    s=state(sol.x)
    s["within_reference_stack_nameplate_only"] = bool(s["gross_w"] <= 7100 and s["current_a"] <= 80)
    s["altitude_and_cold_start_qualified"] = False
    s["max_residual_w"]=max(abs(np.array(residual(sol.x))))*5000
    # 35 MPa absolute at settled 15 C. Residual at -30 C, 2 MPa absolute.
    rho_fill=PropsSI("D","T",288.15,"P",35e6,"Hydrogen")
    rho_res=PropsSI("D","T",243.15,"P",2e6,"Hydrogen")
    startup_allowance=.03  # kg; budget assumption, not simulated
    loaded_usable=(s["h2_fresh_kg_h"]*hours+startup_allowance)/.90
    vol=loaded_usable/(rho_fill-rho_res)
    s.update(hours=hours,required_usable_h2_kg=loaded_usable,
             cylinder_internal_volume_l=vol*1000,
             rho_fill_kg_m3=rho_fill,rho_residual_kg_m3=rho_res,
             cold_full_pressure_mpa=PropsSI("P","T",243.15,"D",rho_fill,"Hydrogen")/1e6,
             warm_full_pressure_mpa=PropsSI("P","T",323.15,"D",rho_fill,"Hydrogen")/1e6)
    # Candidate purchased size, not a pressure vessel design.
    selected_l=math.ceil(vol*1000/10)*10
    s["selected_total_water_volume_l"]=selected_l
    s["selected_h2_full_kg"]=rho_fill*selected_l/1000
    s["selected_usable_h2_kg"]=(rho_fill-rho_res)*selected_l/1000
    s["v2_layout_80l_capacity_sufficient"] = bool(vol <= .08)
    # Twin capsule envelopes, assumed OD and radial/end allowance, never wall sizing.
    od=.32
    id_assumed=od-.04
    v_one=selected_l/2000
    lcyl=(v_one-math.pi*id_assumed**3/6)/(math.pi*id_assumed**2/4)
    s["bottle_envelope_od_m"]=od
    s["bottle_envelope_length_m"]=lcyl+id_assumed+.14
    s["radiator_core_width_m"]=math.sqrt(s["radiator_face_m2"]/1.2)
    s["radiator_core_height_m"]=1.2*s["radiator_core_width_m"]
    # Velocity sizing only; final line sizes need pressure drop and fittings checks.
    s["coolant_id_at_1p5ms_mm"]=math.sqrt(4*(s["coolant_l_min"]/60000)/(math.pi*1.5))*1000
    s["air_id_at_10ms_mm"]=math.sqrt(4*(s["air_inlet_m3h"]/3600)/(math.pi*10))*1000
    return s

cases={"baseline":solve(),"lower_voltage":solve(cell_v=.70),
       "higher_pressure_drop":solve(cathode_dp=30000,rad_dp=300),
       "weaker_radiator":solve(face_ua=700),
       "combined_adverse":solve(cell_v=.70,cathode_dp=30000,rad_dp=300,face_ua=700)}
result={"date":"2026-09-23","model":"conditional steady-state sizing, no cold-start proof",
        "CoolProp_version":CoolProp.__version__,"cases":cases}
(OUT/"solution.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
lines=["| 工况 | 毛功率 kW | 电流 A | 冷却热负荷 kW | 冷却 L/min | 散热器迎风 m² | 风量 m³/h | 氢耗 kg/h | 需瓶水容积 L |",
       "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
for n,s in cases.items():
    lines.append(f'| {n} | {s["gross_w"]/1000:.3f} | {s["current_a"]:.2f} | {s["coolant_heat_w"]/1000:.3f} | {s["coolant_l_min"]:.2f} | {s["radiator_face_m2"]:.3f} | {s["radiator_air_m3h"]:.0f} | {s["h2_fresh_kg_h"]:.3f} | {s["cylinder_internal_volume_l"]:.1f} |')
(OUT/"工况对比.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("\n".join(lines))
print(json.dumps(cases["baseline"],ensure_ascii=False,indent=2))
