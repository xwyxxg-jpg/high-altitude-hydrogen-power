# 来源与检索记录

检索日期：2026-09-09。联网来源只用于技术依据、型号核查和专利初筛；专利状态、权利要求范围、FTO和认证必须在冻结设计前由专业机构复核。

## 本地项目来源

`PROJECT_CONTEXT.md`：当前有效路线、55节初值、冷启动状态、风险与图纸要求。

`新系统架构图.pdf`：四固态床、双气瓶、两液路、氢/空气伴热、液-液换热器的主框架。

`challenge_week1_requirements.md`：题目硬指标与评分要求。

`高寒地区氢能移动电源_物理要求与参数验证汇总.md`：空气流量、换热器热负荷、母线电流、氢耗和质量冲突的核算。

`初步调研2.md`、`tifemn_physical_parameter_comparison.md`、`storage_cooling_solution_survey.md`：路线比较、TiFe-Mn参数、低温与材料文献线索。

`初步检测阈值与传感器清单.md`、`deliverables/启动与正常工作控制流程模拟.md`、`LOW_VOLTAGE_ARCHITECTURE_V21_HANDOFF.md`：传感器、状态机、低压电气和安全链。

`氢气换热器技术需求-V1.0.xlsx`、`水泵技术需求_V1.0(1).xlsx`：前期接口需求；因其部分数据为大功率系统，本次没有直接照搬。

## 论文与题录

1. Barale et al., “TiFe0.85Mn0.05 alloy produced at industrial level for a hydrogen storage plant”, arXiv:2202.12753, https://arxiv.org/abs/2202.12753。全文已保存research/web/barale_full.pdf。
2. Dematteis et al., “Fundamental hydrogen storage properties of TiFe-alloy with partial substitution of Fe and Mn”, arXiv:2012.00354, https://arxiv.org/abs/2012.00354。全文已保存research/web/dematteis_full.pdf。
3. Dreistadt et al., “An Effective Activation Method for Industrially Produced TiFeMn Powder for Hydrogen Storage”, arXiv:2205.09429, https://arxiv.org/abs/2205.09429。
4. Luo & Jiao, “Cold start of proton exchange membrane fuel cell”, DOI:10.1016/j.pecs.2017.10.003。
5. Lototskyy et al., “The use of metal hydrides in fuel cell applications”, DOI:10.1016/j.pnsc.2017.01.008。
6. “Experimental study on rapid cold start-up performance of PEMFC system”, DOI:10.1016/j.ijhydene.2023.01.364。
7. “Cold start performance analysis of PEMFC with different assisted heating strategies”, DOI:10.1016/j.csite.2025.106178。
8. “Numerical analysis and structural optimization of PEMFC cold-start performance”, DOI:10.1016/j.renene.2026.126270。
9. “3D numerical study of hydrogen storage in nano-enhanced metal hydride reactor with branching type fins”, DOI:10.1016/j.icheatmasstransfer.2025.110301。
10. “Numerical modeling study of hydrogen absorption process in metal hydride hydrogen storage reactors with spiral fins”, DOI:10.1016/j.icheatmasstransfer.2025.109972。

## 专利初筛

* US 12,385,676, “Metal hydride heat exchanger and method of use”, FFI IONIX IP, 页面日期2025-08-12，公开文本：https://www.freepatentsonline.com/12385676.html。
* US 11,566,853, “Metal hydride heat exchanger and method of use”, Xergy Inc.，公开文本：https://www.freepatentsonline.com/11566853.html。
* US 8,636,836, “Finned heat exchangers for metal hydride storage systems”，FPO检索结果。
* US 8,778,063, “Coiled and microchannel heat exchangers for metal hydride storage systems”，FPO检索结果。
* US 12,347,900, “Cold start control method and system for fuel cell vehicles”, Hyundai/Kia, 页面日期2025-07-01，公开文本：https://www.freepatentsonline.com/12347900.html。
* US 2025/0201877 A1, “Cold start control method of fuel cell stack and cold start system of fuel cell stack”, Hyundai/Kia, 页面日期2025-06-19，公开文本：https://www.freepatentsonline.com/y2025/0201877.html。

## 厂商页面与数据表

* Celeroton TurboCell CTi-110x：https://www.celeroton-turbocell.com/en/home/；数据表PDF已保存research/web/datasheet_cti.pdf。
* WIKA MH-3-HY：https://www.wika.com/en-en/mh_3_hy.WIKA。
* Toshiba SCiB 20Ah-HP：https://www.global.toshiba/ww/products-solutions/battery/scib/product-next/product/cell/combination.html。
* Analog Devices LTC6806：https://www.analog.com/en/products/ltc6806.html。
* TI BQ76952：https://www.ti.com/product/BQ76952。
* Sensirion SFM3003-300-CL：https://sensirion.com/products/catalog/SFM3003-300-CL。
* TI TCAN1042HGV-Q1：https://www.ti.com/product/TCAN1042HGV-Q1。
* AD7124-8：https://www.analog.com/en/products/ad7124-8.html。
* H2scan HY-ALERTA 5000 series：https://h2scan.com/products/hy-alerta-500/。

所有网页原文/JSON/状态码保存在`research/web`。检索失败、403、404或页面需要登录的记录保留原样，不能当作已核实的规格。
