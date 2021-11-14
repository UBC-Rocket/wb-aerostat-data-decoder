"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""
import analyzer_sd, analyzer_direwolf

# Make sure to set TIME_STEP in config.
t = analyzer_direwolf.AprsFiAnalyzer("resources/launchData/launch_1_aprsFi_quotesInCommentSubbed.csv", 2.5)
t.output_vectors("launch1Output_quotesSubbed.csv")
t.save_datapoints("Launch1ProcessedDatapoints.csv")

"""v = analyzer_direwolf.DirewolfAnalyzer("direwolfTestFile1July16.csv")
v.output_vectors()"""