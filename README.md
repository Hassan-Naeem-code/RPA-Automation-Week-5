# Inventory Bot Automation Platform (Week 5)

## Overview
This project demonstrates a scalable, observable, and maintainable Python-based inventory automation bot, ready for enterprise deployment.

## Quick Start
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Generate synthetic logs and metrics:**
   ```bash
   python scripts/generate_fake_logs.py
   ```
   - Output: `/data/inventory_fake.log` and `/data/inventory_metrics.prom`

3. **Run the bot with metrics endpoint:**
   See code snippets in `/docs/monitoring_plan.md` for Prometheus integration.

## Documentation
- Monitoring: `/docs/monitoring_plan.md`
- Maintenance: `/docs/maintenance_plan.md`
- ROI Model: `/docs/roi.md`

## Diagrams
- See `/diagrams/` for architecture and monitoring visuals.

## Slide Deck & Video
- [Add your exported slides and video link here]

## APA Citations
- All external references are cited in APA 7 format in the docs and slides.

---

**For a metrics demo, run the Prometheus example in `/docs/monitoring_plan.md` and view the `/data/inventory_metrics.prom` file.**
