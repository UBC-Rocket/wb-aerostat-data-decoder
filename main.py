"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""
import analyzer_sd

t = analyzer_sd.SDAnalyzer("LOG_modified.csv")
t.output_vectors()
