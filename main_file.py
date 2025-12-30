from pipeline_class import DataPipeline
import matplotlib.pyplot as plt
pipeline =  DataPipeline('online_retail.csv')
pipeline.run()
plt.show()