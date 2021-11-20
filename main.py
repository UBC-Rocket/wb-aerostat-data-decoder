"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""
import analyzer_direwolf

# Make sure to set TIME_STEP in config.
t = analyzer_direwolf.AprsFiAnalyzer("resources/launchData/launch_1_aprsFi_noQuotes.csv", 15)
t.output_vectors("outputs/L1_vec_noQ.csv")
t.save_datapoints("outputs/L1_dp_noQ.csv")

"""v = analyzer_direwolf.DirewolfAnalyzer("outputs/direwolfTestFile1July16.csv")
v.output_vectors()"""