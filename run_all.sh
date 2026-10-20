#!/bin/sh
# Rebuild everything end to end
pip install -r requirements.txt
python python/01_generate_data.py
python python/02_build_db.py
python python/03_analysis_segmentation.py
