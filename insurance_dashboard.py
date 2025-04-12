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
    options=list(prepared_data['smoker'].unique())
)

smoker = smoker_select.rx()

# region toggle
region_select = pn.widgets.Select(
    name='Region',
    options=list(prepared_data['region'].unique())
)

region = region_select.rx()

# sex toggle
sex_select = pn.widgets.Select(
    name='Sex',
    options=list(prepared_data['sex'].unique())
)

sex = sex_select.rx()

def filter_data(min_age, max_age, min_bmi, max_bmi, min_charges, max_charges, smoker_status, region, sex):
    age_filter = (prepared_data['age'] >= min_age) & (prepared_data['age'] <= max_age)
    bmi_filter = (prepared_data['bmi'] >= min_bmi) & (prepared_data['bmi'] <= max_bmi)
    charges_filter = (prepared_data['charges'] >= min_charges) & (prepared_data['charges'] <= max_charges)
    smoker_filter = (prepared_data['smoker'] == smoker_status) if smoker_status != 'All' else True
    region_filter = (prepared_data['region'] == region) if region != 'All' else True
    sex_filter = (prepared_data['sex'] == sex) if sex != 'All' else True
    return prepared_data.loc[age_filter & bmi_filter & charges_filter & smoker_filter & region_filter & sex_filter]

def filter_test(min_age, max_age):
    data = prepared_data.loc[(prepared_data.age >= min_age) & (prepared_data.age <= max_age)]
    return data

read_params = pn.rx(
    "Max Age: {max_age},<br>"
    "Min Age: {min_age},<br>"
    "Max BMI: {max_bmi},<br>"
    "Min BMI: {min_bmi},<br>"
    "Smoker: {smoker},<br>"
    "Region: {region},<br>"
    "Sex: {sex}"
).format(max_age=max_age, min_age=min_age, max_bmi=max_bmi, min_bmi=min_bmi, smoker=smoker, region=region, sex=sex)        

pn.Column(read_params).servable()
df = pn.rx(filter_test)(max_age=max_age, min_age=min_age)
table = pn.widgets.Tabulator(df, sizing_mode="stretch_both", name="Table", show_index=False, disabled=True, theme='fast').servable()
# test plot - static
# fig = px.scatter(prepared_data, x = 'age', y = 'charges', color='sex')
# fig.update_traces(mode="markers", marker=dict(size=10))
# fig.layout.autosize = True
# pn.pane.Plotly(fig, height=400, sizing_mode="stretch_width").servable()

# test plot - dynamic
# df = pn.rx(filter_data(
#     prepared_data,
#     min_age=age_slider.value[0],
#     max_age=age_slider.value[1],
#     min_bmi=bmi_slider.value[0],
#     max_bmi=bmi_slider.value[1],
#     min_charges=charges_slider.value[0],
#     max_charges=charges_slider.value[1],
#     smoker_status=smoker_check.value,
#     region=region_select.value,
#     sex=sex_select.value))

# df = pn.rx(filter_test)(min_age=age_slider.value[0], max_age=age_slider.value[1])
# fig = px.scatter(df, x='age', y='charges', color='sex')
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