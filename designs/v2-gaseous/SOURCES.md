# 参数来源与公开范围

## 参考采购平台

H-WCS-SP-7K产品页面在2026-09-21本地调研中记录为119节、200 cm²活性面积、80 A、约90 V、7.1 kW、242×200×550 mm、约28 kg。公开运行环境5～35℃；测试65℃、常压、阴阳极100%RH。

来源：[Fuel Cell Store H-WCS-SP-7K产品页](https://www.fuelcellstore.com/fuel-cell-stacks/h-wcs-sp-7k-water-cooled-7kw-pemfc-stack)。

2026-09-23模型沿用该日期的参数摘记，不表示重新确认供货或厂家保证4000 m、−30℃和本模型工作点。原页面还存在名义/峰值/额定口径及取整问题，必须索取当前正式数据表。此次不公开第三方网页全文和完整手册。

## 物性与数值工具

- [CoolProp Hydrogen](https://coolprop.org/fluid_properties/fluids/Hydrogen.html)：气体密度和温压使用实际安装的`Hydrogen`后端，版本保存在JSON。
- [CoolProp不可压缩流体文档](https://coolprop.org/fluid_properties/Incompressibles.html)：低温物性示例使用`INCOMP::MEG-50%`。50%为质量分数，不能直接等同于50%体积分数或某电堆获准冷却液。
- [SciPy root](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root.html)、[least_squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html)、[solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)：方程与瞬态求解工具；软件使用不代表物理模型经过实验验证。

## 工程假设

单节0.75/0.70 V、97%新鲜氢利用率、散热器迎风UA系数、风机效率、液路阻力、85%冷却液热分配、低温风机功率预算、伴热与保温参数均为模型假设。不是采购保证值。

高压瓶参考充装状态为15℃、35 MPa绝压；温变压力用于容量/状态研究，不能代替认证瓶的充装温度补偿和最高允许压力规定。尺寸表中明确区分供应商历史尺寸、计算值和占位预算。
