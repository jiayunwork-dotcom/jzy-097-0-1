# Knife-Edge Diffraction Service

单刃障碍绕射内核，仅经 HTTP 提供。根据链路几何与频率计算菲涅尔–基尔霍夫
绕射参数 `v`、第一菲涅尔区半径、余隙与附加绕射损耗，并给出是否通视的判定。
不做自由空间链路预算，附加损耗绝不套用自由空间损耗公式。

## 模型定义（钉死）

- `h`：障碍相对收发直视线的超出高度 [m]。**高出直视线为正（遮挡），低于为负（通视）**。
- `d1` / `d2`：障碍到发射端 / 接收端的水平距离 [m]，必须为正。
- `λ = c / f`：波长由频率换算，`f` 必须为正。
- 菲涅尔参数：`v = h · √(2·(d1+d2) / (λ·d1·d2))`
- 第一菲涅尔区半径（障碍处）：`r1 = √(λ·d1·d2 / (d1+d2))`
- 余隙：`clearance = −h`（正表示直视线越过障碍），并给出 `clearance / r1`。
- 附加损耗（ITU-R P.526 风格近似，标准库手写）：
  - `v ≤ −0.78`：`J(v) = 0 dB`（余隙充足，不硬加 6 dB）
  - `v > −0.78`：`J(v) = 6.9 + 20·log10(√((v−0.1)² + 1) + v − 0.1)`
  - 因此 `v = 0`（障碍擦着直视线）时损耗约 6 dB。

关键关系（均有测试把守）：`h = 0` → `v = 0` 且损耗 ≈ 6 dB；只加高障碍损耗单调
上升；同一几何下频率加倍 `v` 乘 `√2`；`d1 = d2` 且 `h` 为足够大负值时损耗趋零。

## 模块划分

| 模块 | 职责 |
| --- | --- |
| `app/geometry.py` | 链路几何、波长、余隙、输入物理校验 |
| `app/fresnel.py` | 菲涅尔参数 `v`、第一菲涅尔区半径 |
| `app/loss.py` | 附加损耗近似式 `J(v)` |
| `app/evaluator.py` | 组合上述结果（参数视图 / 损耗视图） |
| `app/batch.py` | 批量调度：逐条独立计算、失败隔离、保序 |
| `app/schemas.py` | HTTP 输入输出模型 |
| `app/presets.py` | 预置算例（山脊略微遮挡，损耗 > 6 dB） |
| `app/main.py` | FastAPI 接口层 |

## 接口

服务固定监听 **8080** 端口。

- `GET /health` — 健康检查
- `POST /api/v1/diffraction/parameters` — 输入几何与频率，返回 `v`、余隙、第一菲涅尔区半径
- `POST /api/v1/diffraction/loss` — 同样输入，额外返回附加损耗 `loss_db` 与是否通视 `los`
- `POST /api/v1/diffraction/batch` — 一组链路一次算完，各条结果独立、失败互不影响
- `GET /api/v1/presets/ridge` — 预置算例：山脊略微遮挡（损耗 > 6 dB）

请求体（单条）：

```json
{"h_m": 10.0, "d1_m": 2000.0, "d2_m": 3000.0, "frequency_hz": 900000000}
```

距离或频率不为正时返回带原因的错误 JSON：

```json
{"error": "invalid_geometry", "reason": "d1_m must be positive, got -5.0"}
```

示例：

```bash
curl -s -X POST localhost:8080/api/v1/diffraction/loss \
  -H 'Content-Type: application/json' \
  -d '{"h_m": 10.0, "d1_m": 2000.0, "d2_m": 3000.0, "frequency_hz": 900e6}'

curl -s -X POST localhost:8080/api/v1/diffraction/batch \
  -H 'Content-Type: application/json' \
  -d '{"links": [
        {"id": "ridge", "h_m": 10, "d1_m": 2000, "d2_m": 3000, "frequency_hz": 900e6},
        {"id": "clear", "h_m": -50, "d1_m": 1000, "d2_m": 1000, "frequency_hz": 1e9}
      ]}'
```

## 运行

Docker（Python 3.12）：

```bash
docker build -t knife-edge .
docker run --rm -p 8080:8080 knife-edge
```

本地（Python 3.12+）：

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 测试

测试随镜像一起发布，可在容器内执行：

```bash
docker run --rm knife-edge python -m pytest tests -v
```

本地则 `pip install -r requirements.txt && python -m pytest tests -v`。
重点用例：擦边 `h = 0` 损耗 ≈ 6 dB、深度通视损耗趋零、频率加倍 `v` 按 `√2`
变化、批量结果各自独立互不覆盖。
