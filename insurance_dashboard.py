import pandas as pd
import panel as pn
import hvplot.pandas
import numpy_financial as npf
import plotly.express as px
# from amortization.schedule import amortization_schedule
# from tabulate import tabulate

# Extensions
pn.extension('tabulator','plotly')

# Styles: change later
ACCENT = "teal"

styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "4px",
    "padding": "10px",
}

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
markdown = pn.pane.Markdown(
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

# plotly express
def update_plot(min_age, max_age, min_bmi, max_bmi, max_charges, min_charges, smoker, region, sex):
    filtered_data = filter_data(min_age, max_age, min_bmi, max_bmi, max_charges, min_charges, smoker, region, sex)
    fig = px.histogram(filtered_data, x='age', color='sex')
    # fig.update_traces(mode="markers", marker=dict(size=10))
    return fig

dynamic_plot = pn.bind(update_plot,
    min_age=min_age,
    max_age=max_age,
    min_bmi=min_bmi,
    max_bmi=max_bmi,
    min_charges=min_charges,
    max_charges=max_charges,
    smoker=smoker,
    region=region,
    sex=sex)

fig = pn.pane.Plotly(dynamic_plot, height=400, sizing_mode="stretch_width", name="Plot")

# servables & layout
styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "4px",
    "padding": "10px",
}
pn.FlexBox(pn.indicators.Number(value=count, name="Count", styles=styles),
        pn.indicators.Number(value=mean_charges, name="Mean Charges ($)", format="${value:,.0f}", styles=styles),
        pn.indicators.Number(value=total_charges, name="Total Charges ($)", format="${value:,.0f}", styles=styles),
        pn.indicators.Number(value=std_charges, name="Stdev Charges ($)", format="${value:,.0f}", styles=styles),
    ).servable()
pn.Row(
    pn.Column(age_slider, bmi_slider, charges_slider, smoker_select, region_select, sex_select),
    pn.Tabs(fig, table, sizing_mode='scale_width', height=500, margin=10)).servable()

# test plot - static
# fig = px.scatter(prepared_data, x = 'age', y = 'charges', color='sex')
# fig.update_traces(mode="markers", marker=dict(size=10))
# fig.layout.autosize = True
# pn.pane.Plotly(fig, height=400, sizing_mode="stretch_width").servable()

# fig = px.scatter(, x='bmi', y='charges', color='sex', size='children')
# pn.pane.Plotly(fig, height=400, sizing_mode="stretch_width").servable()
# # fig = px.scatter(df, x='age', y='charges', color='sex')
# fig.update_traces(mode="markers", marker=dict(size=10))
# fig.layout.autosize = True
# pn.pane.Plotly(fig, height=400, sizing_mode="stretch_width").servable()

# Dashboard Stats
# average charges by region
# average charges by BMI and gender
# average charges by BMI and age


# TODO TVM Calculator
# import TVM_function_numpy
# TODO Loan Amortization
# import loan_function
# table = (x for x in amortization_schedule(150000, 0.1, 36))
# tabulate(
#         table,
#         headers=["Number", "Amount", "Interest", "Principal", "Balance"],
#         floatfmt=",.2f",
#         numalign="right"
#     )