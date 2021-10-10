"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""
import analyzer_sd, analyzer_direwolf

# Make sure to set TIME_STEP in config.
t = analyzer_sd.SDAnalyzer("sdTestFile2Simple.csv")
t.output_vectors()

"""v = analyzer_direwolf.DirewolfAnalyzer("direwolfTestFile1July16.csv")
v.output_vectors()"""