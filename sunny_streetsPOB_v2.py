# state of progress: complete mapbox graph, line 251 (objects + callback)
# state of progress (latest): fix the error -->ValueError: invalid literal for int() with base 10: '1:55', which seems to indicate that dfc[features] includes mixed data types, while it should only be integers

import plotly.graph_objects as go
import dash
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
# dash bootstrap 1.0 or higher

dfc = pd.read_csv(
    "https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Analytic_Web_Apps/VizForGood/Scatter_mapbox/Volaby-Sunny_Street-detailed-stats%202019%20-%202021%20-%20V3.csv"
)
dfp = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Analytic_Web_Apps/VizForGood/Scatter_mapbox/Sunny%20Street%20-%20Patient%20data%203%20years.csv")

# Data Processing *********************************************************
# *************************************************************************
dfc["Activity"] = dfc["Activity"].replace(
    {
        "Hervey Bay Neighbourhood/ Community Centre ": "Hervey Bay Neighbourhood",
        "Maroochydore Neighbourhood Centre Community Event ": "Maroochydore Neighbourhood Centre",
    }
)

# create shift periods for the bottom map
dfc["Start Time"] = pd.to_datetime(
    dfc["Start Time"], format="%I:%M %p").dt.hour
dfc["shift_start"] = ""
dfc.loc[dfc["Start Time"] >= 19, "shift_start"] = "night"
dfc.loc[dfc["Start Time"] < 12, "shift_start"] = "morning"
dfc.loc[
    (dfc["Start Time"] >= 12) & (dfc["Start Time"] < 19), "shift_start"
] = "afternoon"
dfc_shift = dfc.groupby(["Latitude", "Longitude", "Activity", "shift_start"])[
    ["Medical Consults"]
].sum()
dfc_shift.reset_index(inplace=True)

# calculate average shift time for bottom histogram graph
avg_shift_time = round(dfc["Length minutes"].mean())

# re-organize dataframe for the top map
dfc_gpd = dfc.groupby(["Latitude", "Longitude", "Activity"])[
    [
        "Medical Consults",
        "Nurse Practitioner Consults",
        "Nursing/Paramedic Consults",
        "Conversations about health education",
        "Allied Health",
        "Referrals (Formal and informal)",
        "Patient Conversations",
        "Service provider conversations",
        "Mental health",
        "Suicide prevention/planning",
        "Substance use",
        "Medication education",
        "Patients turned away",
        "Telehealth consults that happened at Clinic",
        "Length minutes",
    ]
].sum()
dfc_gpd.reset_index(inplace=True)

# reformat time column to a proper datetime data type column
dfc['activity_date'] = pd.to_datetime(
    dfc['Activity Date'], format='%m/%d/%Y', errors='ignore')
dfc["year"] = dfc['activity_date'].dt.year
dfc['month'] = dfc['activity_date'].dt.month
dfc["day"] = dfc["activity_date"].dt.day

activity_list = list(dfc["Activity"].value_counts().sort_index().index)
activity_list.reverse()
activity_values = list(dfc["Activity"].value_counts().sort_index().values)
activity_values.reverse()

dfc["Activity_label"] = dfc["Activity"]
# dfc.pivot_table(values='Activity', index=["year"],
#                 columns=['Activity_label'], aggfunc={"Activity": "count"}, fill_value=0)
shift_byActivityDate = dfc.pivot_table(values='Activity', index=["activity_date"],
                                       columns=['Activity_label'], aggfunc={"Activity": "count"}, fill_value=0).sum(axis=1).cumsum().values
activityCentre_timeline = dfc.pivot_table(values='Activity', index=["activity_date"],
                                          columns=['Activity_label'], aggfunc={"Activity": "count"}, fill_value=0)

dfc["Activity"] = [x.strip(' ') for x in dfc["Activity"]]
dfc["Activity_label"] = dfc["Activity"]

my_dict = {}
for i in dfc["Activity"].unique():
    my_dict[f"{i}"] = dfc.pivot_table(values='Activity', index=["activity_date"],
                                      columns=['Activity_label'], aggfunc={"Activity": "count"}, fill_value=0)[i].values


options = [{"label": i, "value": i}
           for i in my_dict.keys()]
options2 = [{"label": i, "value": i}
            for i in dfp["Year"].unique()[:3].astype(int)]
features = dfc.select_dtypes(exclude=[object]).columns.drop(["Latitude",
                                                             "Longitude",
                                                            "activity_date",
                                                             'year',
                                                             "month",
                                                             "day"])
dfc[features] = dfc[features].astype('int64')

options3 = [{"label": i, "value": i}
            for i in dfc[features].astype(int)]
pivot_df = pd.pivot_table(dfc, values=dfc[features],
                          index=["Latitude", "Longitude"],
                          aggfunc="sum").reset_index(level=[0, 1])
features

barchart = go.Figure(
    data=[go.Bar(
        x=activity_values,
        y=activity_list,
        orientation='h')],
    layout=go.Layout(
        title=go.layout.Title(
            text="Distribution of Total Shifts by Activity Centre"),
        title_x=0.5))


barchart_df = dfp.loc[dfp["Year"] == 2019].groupby(
    "Year")["Ethnicity"].value_counts(normalize=True, ascending=True)*100
barchart_df2 = dfp.loc[dfp["Year"] == 2020].groupby(
    "Year")["Ethnicity"].value_counts(normalize=True, ascending=True)*100
barchart_df3 = dfp.loc[dfp["Year"] == 2021].groupby(
    "Year")["Ethnicity"].value_counts(normalize=True, ascending=True)*100
barchart_df = barchart_df.to_frame()
barchart_df2 = barchart_df2.to_frame()
barchart_df3 = barchart_df3.to_frame()

barchart_df.rename(columns={"Ethnicity": "Ethnicity_pct"}, inplace=True)
barchart_df2.rename(columns={"Ethnicity": "Ethnicity_pct"}, inplace=True)
barchart_df3.rename(columns={"Ethnicity": "Ethnicity_pct"}, inplace=True)
barchart_df.reset_index(level=[0, 1], inplace=True)
barchart_df2.reset_index(level=[0, 1], inplace=True)
barchart_df3.reset_index(level=[0, 1], inplace=True)
barchart_df["Ethnicity_cnt"] = dfp.loc[dfp["Year"] == 2019].groupby(
    "Year")["Ethnicity"].value_counts(ascending=True).values
barchart_df2["Ethnicity_cnt"] = dfp.loc[dfp["Year"] == 2020].groupby(
    "Year")["Ethnicity"].value_counts(ascending=True).values
barchart_df2
barchart_df3["Ethnicity_cnt"] = dfp.loc[dfp["Year"] == 2021].groupby(
    "Year")["Ethnicity"].value_counts(ascending=True).values
barchart_df3.shape

ethnicity_2019 = px.bar(barchart_df,
                        x=barchart_df["Ethnicity_pct"],
                        y=barchart_df["Ethnicity"],
                        orientation='h',
                        hover_data=["Ethnicity_cnt"],
                        hover_name="Ethnicity",
                        labels={})
ethnicity_2020 = px.bar(barchart_df2,
                        x=barchart_df2["Ethnicity_pct"],
                        y=barchart_df2["Ethnicity"],
                        orientation='h',
                        hover_data=["Ethnicity_cnt"],
                        hover_name="Ethnicity",
                        labels={})
ethnicity_2021 = px.bar(barchart_df3,
                        x=barchart_df3["Ethnicity_pct"],
                        y=barchart_df3["Ethnicity"],
                        orientation='h',
                        hover_data=["Ethnicity_cnt"],
                        hover_name="Ethnicity",
                        labels={})


app = dash.Dash(
    __name__, external_stylesheets=[
        dbc.themes.SUPERHERO])  # , suppress_callback_exceptions=True)

server = app.server

# Build Layout **
app.layout = dbc.Container(
    [dbc.Container(
        [html.H1(
            "Sunny Streets Dashboard",
            style={"background-color": "#33CCCC",
                   "textAlign": "center"},
            className="display-3"),
         html.Img(
            src="https://raw.githubusercontent.com/pierreolivierbonin/test_dash_app/main/vfsg_logo_light.png",
            style={"maxHeight": "800px",
                   "maxWidth": "400px"}
        )
        ],
        className="p-5 bg-light rounded-1 mt-3 mb-5 h-50",
    ),
        dbc.Row(
        [
            dbc.Col(
                [
                    html.Div([

                        html.H3("Question 1a:"),
                        html.P("How have the services changed since 2019?",
                               style={"fontSize": 20}),
                        html.H5('Select one or compare across locations:',
                                style={"paddingRight": "0px"}),
                        html.Div([

                            dcc.Dropdown(id='my_dropdown',
                                         value=["Gympie"],
                                         options=options,
                                         multi=True,
                                         placeholder="Select an activity centre")
                        ], style={'color': '#212121', "fontSize": 20, "display": "inline-block", "verticalAlign": "top", "width": "100%"}),
                        html.Div([
                            dcc.Graph(id="my_graph"
                                      )], style={"fontSize": 20,  "verticalAlign": "top", "width": "100%", "paddingBottom": "30px"}
                                 )
                    ]
                    )
                ],
                width=5,
            ),
            dbc.Col([
                    html.Div([
                        html.H3("Question 1b:"),
                        html.P(
                            "How do activity centres compare in terms of total shifts?"),
                        html.H5('Examine the distribution:',
                                style={"paddingRight": "0px", "width": "100%"}),
                        dcc.Graph(id="my_graph2",
                                  figure=barchart)
                    ], style={"fontSize": 20, "display": "inline-block", "verticalAlign": "center", "paddingRight": "0px", "paddingLeft": "0px", "width": "100%"}),

                    ],
                    width=5,
                    )
        ], justify="center"
    ), dbc.Row([
        dbc.Col([
            html.H3("Question 2:"),
            html.P("How have the patient demographics changed since 2019?",
                   style={"fontSize": 20}),
            html.H5('Select a year to examine the distribution:',
                    style={"paddingRight": "0px"}),
            html.Div([
                dcc.Dropdown(id='my_dropdown2',
                             value=2019,
                             options=options2,
                             multi=False,
                             placeholder="Select a year")
            ], style={'color': '#212121', "fontSize": 20, "display": "inline-block", "verticalAlign": "top", "width": "100%"}),
            html.Div([
                dcc.Graph(id="my_graph3"
                          )], style={"fontSize": 20,  "verticalAlign": "top", "width": "100%", "paddingBottom": "30px"}
                     )], width=5
        ),
        dbc.Col(
            [html.Br(),
             html.Br(),
             html.Br(),
             html.H5('Examine the geographic distribution of interventions:',
                     style={"paddingRight": "0px"}),
             html.Div([
                 dcc.Dropdown(id='my_dropdown3',
                              value="Length minutes",
                              options=options3,
                              multi=False,
                              placeholder="Select a feature")
             ], style={'color': '#212121', "fontSize": 20, "display": "inline-block", "verticalAlign": "top", "width": "100%"}),
                dcc.Graph(
                    id="map2")
             ],
            width=5,
        )

    ], justify="center"
    )

    ], fluid=True)


@ app.callback(
    Output('my_graph', 'figure'),
    [Input("my_dropdown", "value")],
    prevent_initial_call=False
)
def update_graph(option_slctd):
    color_palette = ["cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgrey", "darkgreen", "darkmagenta", "darkolivegreen",
                     "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deepskyblue"]
    date_list = activityCentre_timeline.index
    my_dict = {}
    for i in dfc["Activity"].unique():
        my_dict[f"{i}"] = dfc.pivot_table(values='Activity', index=["activity_date"],
                                          columns=['Activity_label'], aggfunc={"Activity": "count"}, fill_value=0)[i].values
    traces = []
    for option, color in zip(option_slctd, color_palette):
        traces.append(go.Scatter(x=date_list,
                                 y=my_dict[option].cumsum(),
                                 marker_color=color,
                                 name=option))
    fig = {
        'data': traces,
        'layout': {"title": "Cumulative Distribution of Shifts Over Time",
                   "title_x": 0.5
                   }
    }

    return fig


@ app.callback(
    Output('my_graph3', 'figure'),
    [Input("my_dropdown2", "value")],
    prevent_initial_call=False
)
def update_graph(option_slctd):
    if option_slctd == 2019:
        fig1 = ethnicity_2019
        fig1.update_layout({"yaxis": {"title": "", "visible": True},
                            "xaxis": {"title": "Percentage (%)"}})
        return fig1
    elif option_slctd == 2020:
        fig2 = ethnicity_2020
        fig2.update_layout({"yaxis": {"title": "", "visible": True},
                            "xaxis": {"title": "Percentage (%)"}})
        return fig2
    elif option_slctd == 2021:
        fig3 = ethnicity_2021
        fig3.update_layout({"yaxis": {"title": "", "visible": True},
                            "xaxis": {"title": "Percentage (%)"}})
        return fig3


@ app.callback(
    Output('map2', 'figure'),
    [Input("my_dropdown3", "value")],
    prevent_initial_call=False
)
def update_graph(option_slctd):
    px.set_mapbox_access_token(open("myToken.mapbox_token").read())
    fig = px.scatter_mapbox(pivot_df,
                            lat="Latitude",
                            lon="Longitude",
                            hover_data={
                                f"{option_slctd}": True,
                                "Longitude": False,
                                "Latitude": False,
                            },
                            color=option_slctd,
                            size=option_slctd,
                            size_max=30,
                            zoom=6,
                            labels={option_slctd: option_slctd},
                            mapbox_style="dark")
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
