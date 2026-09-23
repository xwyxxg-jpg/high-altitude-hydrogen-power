"""Fixed-hardware -30 C sensitivity. No validated cold-stack or fan model."""
import json
import math
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares, brentq
from scipy.integrate import solve_ivp
import CoolProp
from CoolProp.CoolProp import PropsSI

sys.stdout.reconfigure(encoding="utf-8")
OUT=Path(__file__).resolve().parents[1]/"results"
base=json.loads((OUT/"solution.json").read_text(encoding="utf-8"))["cases"]["baseline"]
A=base["radiator_face_m2"]
PAMB=base["ambient_pressure_pa"]
RHO0=base["rho_air"]
CPAIR=1006.
F=96485.33212
N=119

def warm_stack(ambient_c, shell_ua=0., trace_w=0., inlet_target_c=None, fan_floor=0.):
    """Keep fixed radiator area; solve I, face air speed, warm coolant mass flow."""
    ta=ambient_c+273.15
    rho=PAMB/(287.05*ta)
    def state(x):
        current,speed,mc=x
        gross=N*.75*current
        air=N*current*.031998/(4*F)/.232*2.2
        # Same assumed fixed required pressure rise and overall efficiency as V2.
        isen_r=(1+15000/PAMB)**(.4/1.4)-1
        blower=air*CPAIR*ta*isen_r/.5
        # Assumption: same efficiency for power and discharge-temperature estimate.
        compressor_out=ta+blower/(air*CPAIR)
        intake_heat=0. if inlet_target_c is None else max(
            0.,air*CPAIR*(inlet_target_c+273.15-compressor_out))
        qv=mc/1060
        dp=80000*(qv/(20e-3/60))**2
        pump=qv*dp/.3
        va=speed*A
        rad_dp=180*(rho/RHO0)*(speed/3)**2
        fan_ideal=rad_dp*va/.35
        # Explicit electrical allowance; not a measured minimum stable fan operating point.
        fan=max(fan_ideal,fan_floor)
        loss=shell_ua*(57.5-ambient_c)
        qreact=N*current*(1.481-.75)
        coolant=.85*qreact+pump
        radiator_required=coolant-loss-intake_heat
        ca,cl=rho*va*CPAIR,mc*3300
        cmin,cmax=min(ca,cl),max(ca,cl)
        cr=cmin/cmax
        # Heat transfer sensitivity only; not a measured low-speed radiator curve.
        ua=1000*A*((rho*speed)/(RHO0*3))**.7
        ntu=ua/cmin
        e=(1-math.exp(-ntu*(1-cr)))/(1-cr*math.exp(-ntu*(1-cr)))
        heat=.85*e*cmin*25 if ambient_c==35 else .85*e*cmin*(60-ambient_c)
        net=.96*gross-blower-fan-pump-100-trace_w
        fresh=N*current*.00201588/(2*F)/.97*3600
        return dict(ambient_c=ambient_c,current_a=current,stack_gross_w=gross,
                    net_w=net,air_g_s=air*1000,air_inlet_m3h=air/rho*3600,
                    blower_w=blower,compressor_outlet_c=compressor_out-273.15,
                    radiator_face_m2=A,radiator_face_speed_ms=speed,
                    radiator_air_m3h=va*3600,radiator_dp_pa=rad_dp,fan_w=fan,
                    fan_ideal_w=fan_ideal,fan_budget_floor_w=fan_floor,
                    coolant_l_min=qv*60000,pump_w=pump,coolant_dp_pa=dp,
                    stack_coolant_heat_w=coolant,radiator_required_w=radiator_required,
                    radiator_actual_w=heat,shell_heat_loss_w=loss,
                    intake_preheat_from_coolant_w=intake_heat,trace_electric_w=trace_w,
                    h2_kg_h=fresh,air_density=rho,
                    radiator_air_out_c=ambient_c+heat/ca,
                    assumptions=dict(shell_ua_w_k=shell_ua,
                                     inlet_target_c=inlet_target_c),
                    feasible_real_fan_not_verified=True)
    def res(x):
        s=state(x)
        return [(s["net_w"]-5000)/5000,
                (s["radiator_actual_w"]-s["radiator_required_w"])/5000,
                (x[2]*3300*5-s["stack_coolant_heat_w"])/5000]
    r=least_squares(res,[65.,3. if ambient_c==35 else .5,.3],
                    bounds=([1,.001,.001],[120,10,2]),
                    xtol=1e-12,ftol=1e-12,gtol=1e-12)
    assert r.success and max(abs(np.array(res(r.x))))<1e-7
    s=state(r.x)
    s["max_residual_w"]=max(abs(np.array(res(r.x))))*5000
    return s

warm={"plus35_reproduction":warm_stack(35),
      "minus30_air_only":warm_stack(-30),
      "minus30_insulated":warm_stack(-30,3,100,5,50),
      "minus30_fan100":warm_stack(-30,3,100,5,100),
      "minus30_trace500":warm_stack(-30,3,500,5,50),
      "minus30_loss10":warm_stack(-30,10,100,5,50),
      "minus30_loss20":warm_stack(-30,20,100,5,50)}
assert abs(warm["plus35_reproduction"]["stack_gross_w"]-base["gross_w"])<.001

FLUID="INCOMP::MEG-50%" # mass fraction; property surrogate, not an approved stack coolant
def props(t):
    k=t+273.15
    return dict(temperature_c=t,
                rho=PropsSI("D","T",k,"P",200000,FLUID),
                cp=PropsSI("C","T",k,"P",200000,FLUID),
                mu=PropsSI("V","T",k,"P",200000,FLUID))
ref=props(57.5)
D,L=.016,6.
VREF=20e-3/60
def pipe_loss(q,p):
    velocity=q/(math.pi*D**2/4)
    re=p["rho"]*velocity*D/p["mu"]
    # Churchill smooth-pipe correlation, continuous through transition.
    aa=(2.457*math.log(1/((7/re)**.9)))**16
    bb=(37530/re)**16
    ff=8*((8/re)**12+1/(aa+bb)**1.5)**(1/12)
    return ff*L/D*p["rho"]*velocity**2/2,re
extra_ref=80000-pipe_loss(VREF,ref)[0]
assert extra_ref>0
hydraulics=[]
for t in [-30,-20,0,20,57.5]:
    p=props(t)
    def dp(q,viscous_share):
        ratio=q/VREF
        other=extra_ref*(viscous_share*(p["mu"]/ref["mu"])*ratio+
                        (1-viscous_share)*(p["rho"]/ref["rho"])*ratio**2)
        return pipe_loss(q,p)[0]+other
    for share in [0.,.5,1.]:
        flow=brentq(lambda q:dp(q,share)-80000,1e-9,.002)
        hydraulics.append(dict(**p,unknown_component_viscous_share=share,
                               mu_ratio_to_57p5=p["mu"]/ref["mu"],
                               dp_at_20lmin_pa=dp(VREF,share),
                               reynolds_at_20lmin=pipe_loss(VREF,p)[1],
                               flow_at_fixed_80kpa_l_min=flow*60000,
                               electric_w_if_force_20lmin=VREF*dp(VREF,share)/.3))

rho_fill=PropsSI("D","T",288.15,"P",35e6,"Hydrogen")
gas=[]
for t in [35,15,-30]:
    residual=PropsSI("D","T",t+273.15,"P",2e6,"Hydrogen")
    gas.append(dict(temperature_c=t,
                    full_pressure_mpa=PropsSI("P","T",t+273.15,"D",rho_fill,"Hydrogen")/1e6,
                    full_mass_80l_kg=rho_fill*.08,residual_mass_80l_kg=residual*.08,
                    usable_mass_80l_kg=(rho_fill-residual)*.08))

# ODE with externally prescribed constant heating; no FC electrochemistry or latent heat.
thermal=[]
for capacity_kj_k in [5,20,70]:
    for ua in [3,10]:
        c=capacity_kj_k*1000
        qneed=30*ua/(1-math.exp(-ua*120/c))
        for q in [1000,5000,10000]:
            integ=solve_ivp(lambda t,y:[(q-ua*(y[0]+30))/c],
                            [0,120],[-30],rtol=1e-10,atol=1e-11)
            exact=-30+q/ua*(1-math.exp(-ua*120/c))
            assert abs(integ.y[0,-1]-exact)<1e-6
            thermal.append(dict(capacity_kj_k=capacity_kj_k,ua_w_k=ua,
                                input_heat_w=q,temp_120_c=float(integ.y[0,-1]),
                                required_heat_to_zero_120_w=qneed))

result=dict(date="2026-09-23",scope="fixed-hardware conditional warm-stack calculation and cold-start budgets",
            warm_stack_cases=warm,coolant_surrogate=FLUID,
            coolant_freeze_c=PropsSI("T_freeze","T",300,"P",200000,FLUID)-273.15,
            hydraulic_cases=hydraulics,gas_temperature_cases=gas,
            startup_thermal_cases=thermal,CoolProp_version=CoolProp.__version__)
(OUT/"minus30_solution.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
for name,s in warm.items():
    print(name, {k:round(s[k],3) for k in ["stack_gross_w","current_a","blower_w","fan_w",
           "radiator_face_speed_ms","radiator_air_m3h","radiator_required_w","coolant_l_min",
           "pump_w","h2_kg_h","air_density","air_inlet_m3h","compressor_outlet_c",
           "intake_preheat_from_coolant_w"]})
print("Hydraulics -30",json.dumps(hydraulics[:3],ensure_ascii=False))
print("Gas",json.dumps(gas,ensure_ascii=False))
print("Required heat",[(x["capacity_kj_k"],x["ua_w_k"],round(x["required_heat_to_zero_120_w"],1))
                       for x in thermal if x["input_heat_w"]==1000])
