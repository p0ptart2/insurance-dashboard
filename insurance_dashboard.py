import pandas as pd
import panel as pn
from plotly.subplots import make_subplots
import numpy_financial as npf
import plotly.express as px
# from amortization.schedule import amortization_schedule
# from tabulate import tabulate

# Extensions
pn.extension('tabulator','plotly')

# Styles: change later
ACCENT = "teal"

# Data Extraction
@pn.cache()  # only download data once
def get_data():
    return pd.read_csv("insurance.csv")

source_data = get_data()

# Prepare Data
def prepare_data(data):
    data['age'] = data['age'].astype(int)
    data['charges'] = data['charges'].astype(float)
    data['bmi'] = data['bmi'].astype(float)
    return data.dropna()

prepared_data = prepare_data(source_data)

# Transform Data
# sliders: age, bmi, charges
# toggles: smoker, region, sex

# age slider
age_slider = pn.widgets.IntRangeSlider(
    name='Age Range',
    start=int(prepared_data['age'].min()),
    end=int(prepared_data['age'].max()),
    value=(int(prepared_data['age'].min()), int(prepared_data['age'].max())),
    step=1
)

max_age = age_slider.rx()[1]
min_age = age_slider.rx()[0]

# bmi slider
bmi_slider = pn.widgets.IntRangeSlider(
    name='BMI Range',
    start=int(prepared_data['bmi'].min()),
    end=int(prepared_data['bmi'].max()),
    value=(int(prepared_data['bmi'].min()), int(prepared_data['bmi'].max())),
    step=1
)

max_bmi = bmi_slider.rx()[1]
min_bmi = bmi_slider.rx()[0]

# charges slider
charges_slider = pn.widgets.IntRangeSlider(
    name='Charges Range',
    start=int(prepared_data['charges'].min()),
    end=int(prepared_data['charges'].max()),
    value=(int(prepared_data['charges'].min()), int(prepared_data['charges'].max())),
    step=1
)

max_charges = charges_slider.rx()[1]
min_charges = charges_slider.rx()[0]

# smoker menu
smoker_select = pn.widgets.Select(
    name='Smoker',
    options=list(prepared_data['smoker'].unique()) + ['All'],  # Add 'All' option to the list
    value='All'  # Set default value to 'All'
)

smoker = smoker_select.rx()

# region toggle
region_select = pn.widgets.Select(
    name='Region',
    options=list(prepared_data['region'].unique()) + ['All'],
    value='All'
)

region = region_select.rx()

# sex toggle
sex_select = pn.widgets.Select(
    name='Sex',
    options=list(prepared_data['sex'].unique()) + ['All'],
    # options=["male","female","All"],
    value='All'
)

sex = sex_select.rx()

# , min_charges, max_charges, smoker_status, region, sex
def filter_data(min_age, max_age, min_bmi, max_bmi, max_charges, min_charges, smoker, region, sex):
    age_filter = (prepared_data['age'] >= min_age) & (prepared_data['age'] <= max_age)
    bmi_filter = (prepared_data['bmi'] >= min_bmi) & (prepared_data['bmi'] <= max_bmi)
    charges_filter = (prepared_data['charges'] >= min_charges) & (prepared_data['charges'] <= max_charges)
    smoker_filter = (prepared_data['smoker'] == smoker) if smoker != 'All' else True
    region_filter = (prepared_data['region'] == region) if region != 'All' else True
    sex_filter = (prepared_data['sex'] == sex) if sex != 'All' else True
    #  
    data = prepared_data.loc[age_filter & bmi_filter & charges_filter & smoker_filter & region_filter & sex_filter]
    return data 

df = pn.rx(filter_data)(max_age=max_age, min_age=min_age, 
                        min_bmi=min_bmi, max_bmi=max_bmi, 
                        max_charges=max_charges, min_charges=min_charges, 
                        smoker=smoker, 
                        region=region, 
                        sex=sex)
table = pn.widgets.Tabulator(df, sizing_mode="stretch_both", name="Table", show_index=False, disabled=True, theme='fast')

# markdown
dashboard_md = pn.pane.Markdown(
    """
    # Insurance Dashboard
    This is a simple insurance dashboard that allows you to filter data based on age, BMI, charges, smoker status""")

# summary stats
# count
count = df.rx.len()
# total charges
total_charges = df['charges'].sum()
# mean charges
mean_charges = df['charges'].mean()
# stdevcharges
std_charges = df['charges'].std()
# median charges
median_charges = df['charges'].median()

# plotly express
def plot_age(min_age, max_age, min_bmi, max_bmi, max_charges, min_charges, smoker, region, sex):
    filtered_data = filter_data(min_age, max_age, min_bmi, max_bmi, max_charges, min_charges, smoker, region, sex)
    fig = px.histogram(filtered_data, x='age', color='sex', color_discrete_map={'male': 'blue', 'female': 'red'})
    # fig.update_traces(mode="markers", marker=dict(size=10))
    return fig

def plot_charges(min_age, max_age, min_bmi, max_bmi, max_charges, min_charges, smoker, region, sex):
    filtered_data = filter_data(min_age, max_age, min_bmi, max_bmi, max_charges, min_charges, smoker, region, sex)
    fig = px.histogram(filtered_data, x='charges', color='sex', color_discrete_map={'male': 'blue', 'female': 'red'})
    return fig

dynamic_plot_age = pn.bind(plot_age,
    min_age=min_age,
    max_age=max_age,
    min_bmi=min_bmi,
    max_bmi=max_bmi,
    min_charges=min_charges,
    max_charges=max_charges,
    smoker=smoker,
    region=region,
    sex=sex)

dynamic_plot_charges = pn.bind(plot_charges,
    min_age=min_age,
    max_age=max_age,
    min_bmi=min_bmi,
    max_bmi=max_bmi,
    min_charges=min_charges,
    max_charges=max_charges,
    smoker=smoker,
    region=region,
    sex=sex)

fig_age = pn.pane.Plotly(dynamic_plot_age, height=400, sizing_mode="stretch_width", name="Ages Hist")
fig_charges = pn.pane.Plotly(dynamic_plot_charges, height=400, sizing_mode="stretch_width", name="Charges Hist")

distribution_md = pn.pane.Markdown("""
# Distribtion of Charges
How can we determine the distribtution of charges by filtering the data?""")

# servables & layout
styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "4px",
    "padding": "10px",
}

pn.Column(dashboard_md).servable()
pn.FlexBox(pn.indicators.Number(value=count, name="Count", styles=styles),
        pn.indicators.Number(value=mean_charges, name="Mean Charges ($)", format="{value:,.0f}", styles=styles),
        pn.indicators.Number(value=total_charges, name="Total Charges ($)", format="{value:,.0f}", styles=styles),
        pn.indicators.Number(value=std_charges, name="Stdev Charges ($)", format="{value:,.0f}", styles=styles),
        pn.indicators.Number(value=median_charges, name="Median Charges ($)", format="{value:,.0f}", styles=styles),
    ).servable()
pn.Row(
    pn.Column(age_slider, bmi_slider, charges_slider, smoker_select, region_select, sex_select),
    pn.Tabs(fig_age, fig_charges, table, sizing_mode='scale_width', height=500, margin=10)).servable()
pn.Column(distribution_md).servable()
