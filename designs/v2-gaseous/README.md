# V2：纯气态储氢5 kW电源计算

日期：2026-09-23。此目录包含原创设计记录、可复算Python模型与生成结果。当前为带假设的概念计算，未证明采购电堆的高原/低温能力，未完成V2实际CAD或台架验证。

## 阅读顺序

1. [第二版设计](第二版设计.md)：目标、未知量、闭合方程、基准结果、容量、部件尺寸占位与敏感性。
2. [−30℃补充计算](第二版设计_负30度补充计算.md)：暖堆稳态、冷却液黏度/压降、气瓶温压与启动预算。
3. [来源与限制](SOURCES.md)：采购数据时间、物性工具与公开范围。

## 复算

从仓库根目录执行，建议使用Python 3.12独立虚拟环境：

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r designs/v2-gaseous/requirements.txt
python -X utf8 designs/v2-gaseous/models/solve_v2.py
python -X utf8 designs/v2-gaseous/models/solve_minus30.py
python -X utf8 designs/v2-gaseous/models/verify_results.py
```

必须先运行`solve_v2.py`，因为负30℃模型读取它生成的基准硬件参数。脚本按自身位置写入本目录`results/`，不会修改历史概念计算。

发布时验证环境：Python 3.12，NumPy 2.4.3，SciPy 1.17.1，CoolProp 8.0.0。

## 输出与覆盖范围

| 文件 | 内容 |
|---|---|
| `results/solution.json` | 5组稳态设计条件；包括参考堆额定能力与80 L气瓶容量检查 |
| `results/工况对比.md` | 稳态设计结果表 |
| `results/minus30_solution.json` | 7组暖堆工况、15组水力情景、18组启动热量情景和3组气瓶温度 |

脚本内包含求解残差与启动ODE/解析解检查；`verify_results.py`进一步核对电/热平衡、原工况复现、固定面积、气瓶质量守恒和不可行标记。这些只能验证实现自洽，不能代替实验标定。

−30℃环境下暖堆需要约5.72 kW毛功率是条件性结果，依赖50 W风机预算和100 W伴热等假设。它不代表−30℃冷堆能直接输出功率，也不意味着散热器可以缩小。原R12图纸和模型属于历史双储氢路线，不是本目录的三维验证。
