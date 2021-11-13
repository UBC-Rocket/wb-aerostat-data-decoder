"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""
import analyzer_sd, analyzer_direwolf

# Make sure to set TIME_STEP in config.
t = analyzer_direwolf.DirewolfAnalyzer("resources/2021-10-31 hallway and outdoor.csv", 2.5)
t.output_vectors("windTest.csv")

"""v = analyzer_direwolf.DirewolfAnalyzer("direwolfTestFile1July16.csv")
v.output_vectors()"""