import pandas
#pandas.options.plotting.backend = "plotly"
import plotly.express as px

data = pandas.read_csv("simulation_results.csv")

#data[["Date", "Value (USD)"]].plot()

fig = px.line(data, x="Date", y="Value (USD)")
fig.show()

