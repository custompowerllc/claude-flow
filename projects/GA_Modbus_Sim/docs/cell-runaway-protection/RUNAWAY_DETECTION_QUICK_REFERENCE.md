# P3E Cell Runaway Detection - Quick Reference Guide

## Delta Thresholds & Response Times

| Delta | Threshold Type | Response Time | Action Required |
|-------|----------------|---------------|-----------------|
| **8-15mV** | Normal (0A) | - | Normal operation |
| **>50mV** | Normal (20A, 5min) | - | Expected under load |
| **100mV** | Early Warning | Immediate alert | Enhanced monitoring |
| **300mV** | High Risk | **30 seconds** | Reduce current 50% |
| **500mV** | Critical | **<10 seconds** | Emergency shutdown |
| **700mV** | Catastrophic | **1 second** | BMS auto-shutdown |

## Critical Findings

### Current Impact
- **0A**: 8-15mV baseline
- **20A for 5 minutes**: >50mV normal
- **Sustained current**: Runaway catalyst

### Time Windows
- **300mV → 500mV**: 57 seconds
- **500mV → 700mV**: 32 seconds  
- **Total escalation**: <90 seconds

### High-Risk Conditions
- **SOC**: 42-45% during discharge
- **Current**: >5A sustained
- **Cell**: #6 most vulnerable

## Why 100mV is Optimal
✅ Above normal 20A operation (>50mV)  
✅ Early detection before escalation  
✅ Avoids false positives  
✅ 2x safety margin

---
*Critical: Automated response required >300mV*