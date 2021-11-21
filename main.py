"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""
import analyzer_aprsfi

t = analyzer_aprsfi.AprsFiAnalyzer("resources/launchData/launch_1_aprsFi.csv", 15)
t.output_vectors("outputs/L1_vec.csv")
t.save_datapoints("outputs/L1_dp.csv")
