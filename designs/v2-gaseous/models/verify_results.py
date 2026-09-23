"""Validate generated outputs; no hardware qualification is implied."""
import json
import math
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "results"
v2 = json.loads((out / "solution.json").read_text(encoding="utf-8"))
cold = json.loads((out / "minus30_solution.json").read_text(encoding="utf-8"))
cases = v2["cases"]
assert len(cases) == 5
for case in cases.values():
    assert abs(case["net_w"] - 5000) < .001
    assert case["max_residual_w"] < .001
    assert abs(case["radiator_heat_w"] - case["coolant_heat_w"]) < .001
assert not cases["combined_adverse"]["within_reference_stack_nameplate_only"]
assert not cases["combined_adverse"]["v2_layout_80l_capacity_sufficient"]

warm = cold["warm_stack_cases"]
assert len(warm) == 7
assert abs(warm["plus35_reproduction"]["stack_gross_w"] - cases["baseline"]["gross_w"]) < .001
for case in warm.values():
    assert abs(case["net_w"] - 5000) < .001
    assert case["max_residual_w"] < .001
    assert abs(case["radiator_face_m2"] - cases["baseline"]["radiator_face_m2"]) < 1e-10
    assert abs(case["radiator_actual_w"] - case["radiator_required_w"]) < .001
    assert abs(case["stack_coolant_heat_w"] - case["radiator_required_w"]
               - case["shell_heat_loss_w"] - case["intake_preheat_from_coolant_w"]) < .001
assert len(cold["hydraulic_cases"]) == 15
assert all(c["flow_at_fixed_80kpa_l_min"] > 0 for c in cold["hydraulic_cases"])
assert len(cold["startup_thermal_cases"]) == 18
for case in cold["startup_thermal_cases"]:
    capacity = case["capacity_kj_k"] * 1000
    ua = case["ua_w_k"]
    expected = -30 + case["input_heat_w"] / ua * (1 - math.exp(-ua * 120 / capacity))
    assert abs(expected - case["temp_120_c"]) < 1e-6
gas = cold["gas_temperature_cases"]
assert len(gas) == 3
assert max(c["full_mass_80l_kg"] for c in gas) - min(c["full_mass_80l_kg"] for c in gas) < 1e-12
print("PASS: steady balances, fixed radiator, +35 C reproduction, startup ODE, bottle mass and infeasible flags")
