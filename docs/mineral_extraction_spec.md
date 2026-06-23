# Mineral Influx and Electrophysiological Spec Sheet (`src/cardiac_ecg_engine.py`)

## 1. Overview
This module handles the mathematical modeling of metabolic and electrophysiological cascades that follow severe osteolytic structural degradation. When the sepsis redox engine triggers bone matrix dissolution, mineral ions are released into circulation, causing downstream cardiac electrical conductivity changes.

---

## 2. Mathematical Formulations

### A. Stoichiometric Calcium Mass Influx
Hydroxyapatite (\(Ca_{10}(PO_4)_6(OH)_2\)) consists of exactly \(39.89\%\) elemental calcium by mass. The rate of calcium mass entering the bloodstream (\(\dot{m}_{Ca}\), mg/sec) is coupled directly to the dynamic tissue cleavage flux:

\[\dot{m}_{Ca}(t) = 0.3989 \times \left( J_{\text{cleavage}} \times V_{\text{bone}} \right) \times 10^3 \quad (\text{mg/sec})\]

### B. Serum Calcium Concentration Matrix
Systemic blood values are determined via an ordinary differential equation (ODE) balancing mineral release with renal glomerular clearance metrics (\(GFR\)):

\[\frac{d[Ca^{2+}]_{\text{serum}}}{dt} = \frac{\dot{m}_{Ca}(t)}{V_{\text{blood}}} - \kappa_{\text{renal}} \cdot GFR \cdot [Ca^{2+}]_{\text{serum}}\]

### C. Hypercalcemic QT-Interval Shorter Correction
Elevated calcium concentrations change the action potential plateau phase, shortening ventricular repolarization metrics (\(QT_c\), in seconds):

\[QT_c(Ca) = QT_{\text{c\_baseline}} - \alpha_{\text{repol}} \times \ln\left(1.0 + \max\left(0.0, \, [Ca^{2+}]_{\text{serum}} - 10.5\right)\right)\]

Where \(QT_{\text{c\_baseline}} = 0.410\text{ s}\) and \(\alpha_{\text{repol}} = 0.085\).

---

## 3. Clinical Arrhythmia Threshold Boundaries

The system evaluates the calculated \(QT_c\) duration continuously to map electrical cardiac strain states:
*   **Sinus Bounds Secure**: \(QT_c > 320\text{ ms}\) (Normal homeostatic conduction).
*   **Short QT Syndrome (SQTS) Active**: \(QT_c \le 320\text{ ms}\). Shortened ventricular repolarization flags high risks of re-entrant circuits, triggering automated ventricular fibrillation alerts in the status registers.

---

## 4. Pipeline Integration Mapping

To evaluate cardiac tracking variables from your analytics loop, initialize the calculator directly alongside your current calcium data streams:

```python
from src.cardiac_ecg_engine import CardiacECGSimulationEngine

# 1. Instantiate the electrophysiology engine
ecg_engine = CardiacECGSimulationEngine(resting_heart_rate_bpm=75.0)

# 2. Run real-time check at an elevated osteolytic serum calcium profile (14.2 mg/dL)
ecg_report = ecg_engine.calculate_dynamic_qt_interval(serum_calcium_mg_dL=14.2)

print(f"Calculated QTc Interval: {ecg_report['calculated_qt_c_ms']} ms")
print(f"Cardiac Rhythm Status:    {ecg_report['cardiac_rhythm_status']}")
```
