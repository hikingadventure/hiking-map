import pandas as pd
import numpy as np
import dash                     #(version 1.0.0)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

import plotly.graph_objs as go

import plotly.express as px

import requests
import base64
import json

#connecting to WordPress database
api_url = 'https://wander-erlebnis.ch/staging/wp-json/wp/v2/programm' 
response = requests.get(api_url, 'lxml')
response_list = json.loads(response.text)

#loop over a database and get data needed

list_tours = [340, 1034, 341, 1137]
tour_name = []
list_max_number_of_people = []
list_booked = []
list_date_oneday = []
list_date_severaldays = []
list_lat = []
list_long = []
list_link = []
list_difficulty = []

for i in list_tours:
  
  output_dict = [x for x in response_list if x['id'] == i]
  tour_name.append(i)
  max_number_of_people = [sub['anzahl_teilnehmende'] for sub in output_dict ]
  list_max_number_of_people.append(max_number_of_people)
  booked = [sub['buchungen'] for sub in output_dict ]
  list_booked.append(booked)
  date_oneday = [sub['datum_eintageswanderung'] for sub in output_dict ]
  list_date_oneday.append(date_oneday)
  date_severaldays = [sub['beginn_mehrtageswanderung'] for sub in output_dict ]
  list_date_severaldays.append(date_severaldays)
  latitude = [sub['breitengrad'] for sub in output_dict ]
  list_lat.append(latitude)
  longitude = [sub['laengengrad'] for sub in output_dict ]
  list_long.append(longitude)
  link = [sub['link'] for sub in output_dict ]
  list_link.append(link)
  difficulty = [sub['schwierigkeit_de'] for sub in output_dict ]
  list_difficulty.append(difficulty)


#getting rid of list of lists
list_max_number_of_people = [j for i in list_max_number_of_people for j in i]
list_booked = [j for i in list_booked for j in i]

#creating table from data
df_table = pd.DataFrame()
df_table["Tour"] = tour_name
df_table["Booked"] = list_booked
df_table["max_num_people"] = list_max_number_of_people
df_table["date_one_day"] = list_date_oneday
df_table["date_several_days"] = list_date_severaldays
df_table["breitengrad"] = list_lat
df_table["laengengrad"] = list_long
df_table["link"] = list_link
df_table["difficulty"] = list_difficulty


corrected_values = {340:"Vom Rheintal über die Kreuzberge ins Appenzellerland",
                    1034:"Hirzli-Planggenstock",
                    341:"Hoch über dem Urner Haupttal",
                    1137:"Mostelberg-Einsiedeln"}

df_table['Tour'] = df_table['Tour'].map(corrected_values)

#get rid of lists in columns
df_table["date_one_day"] = df_table.apply(lambda x: pd.Series(x['date_one_day']),axis=1).stack().reset_index(level=1, drop=True)
df_table["date_several_days"] = df_table.apply(lambda x: pd.Series(x['date_several_days']),axis=1).stack().reset_index(level=1, drop=True)
df_table["breitengrad"] = df_table.apply(lambda x: pd.Series(x['breitengrad']),axis=1).stack().reset_index(level=1, drop=True)
df_table["laengengrad"] = df_table.apply(lambda x: pd.Series(x['laengengrad']),axis=1).stack().reset_index(level=1, drop=True)
df_table["link"] = df_table.apply(lambda x: pd.Series(x['link']),axis=1).stack().reset_index(level=1, drop=True)
df_table["difficulty"] = df_table.apply(lambda x: pd.Series(x['difficulty']),axis=1).stack().reset_index(level=1, drop=True)


#difficulty lvl
df_table["difficulty_lvl"] = df_table["difficulty"].str[:2]

#Combine 2 columns into one
df_table["Date"] = df_table["date_one_day"] + df_table["date_several_days"]

#calculating Tour Lenght
list_tour_lenght = []
for i in range(len(df_table["date_one_day"])):
  if df_table["date_one_day"][i] == "":
    list_tour_lenght.append("Several days")
  else:
    list_tour_lenght.append("One day")

df_table["Tour_Length"] = list_tour_lenght
df_table["color"] = ["blue", "green", "red", "orange"]


#df_table["Date"] =  pd.to_datetime(df_table["Date"])
df_table["Date"] = df_table["Date"].str.replace(".","")


#calculating fully booked/ places available
availability = []
for i in range(len(df_table)):
  if df_table["Booked"][i] == df_table["max_num_people"][i]:
    availability.append("fully booked")
    #print("fully booked")
  else:
    availability.append("places available")
    #print("places available")

df_table["Availability"] = availability



#print(df_table)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

blackbold={'color':'black', 'font-weight': 'bold', "font-family":"New Panam Skyline"}

background_color = '#E4FFC9'
#style={"font-family": "Burnest Rough Regular"}

app.layout = html.Div([
    dbc.Row([

    dbc.Col(children=[
            
        dbc.Row([ 
                
            html.Div([
                html.H1(UPCOMING HIKES)
                dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True}),
                #html.P("Explanation: Move the mouse over a colored point on the map for information about date and availability. \
                #    The detailed tour program can be found here:", 
                #    style={'textAlign': 'center', "backgroundColor":'#E4FFC9', "font-family": "Burnest Rough Regular"}),
                #html.Pre(id='web_link', children=[],
                #    #style={'padding-bottom':'20px','padding-left':'2px','height':'100vh'}
                #    )

            ])      

        ])

    ],width=8)

]),
    dbc.Row([

    dbc.Col(children=[
        dbc.Row([

            html.Div([
                html.Label(children=['Please select. '], style={"backgroundColor":'#E4FFC9', "font-family": "Arial"}),
                dbc.Checklist(id='tour_lenght_name',
                        options=[{'label':str(b),'value':b} for b in sorted(df_table['Tour_Length'].unique())],
                        value=[b for b in sorted(df_table['Tour_Length'].unique())],
                        style={"backgroundColor":'#E4FFC9', "font-family": "Arial", 'padding-bottom':'20px'}
                        )
            ],style={'color': '#7C7672', 'fontSize': 16, "backgroundColor":'#E4FFC9', 'padding-left':'40px'})   

        ]),
        
        dbc.Row([ 
                
            html.Div([
                html.P("Explanation: Move the mouse over the red bubbles for information about date, difficulty and availability. A click on the bubble will display the link to the detailed tour information below:", 
                    #style={'textAlign': 'center', "backgroundColor":'#E4FFC9', "font-family": "Arial"}
                    )
            ], style={'color': '#7C7672', 'fontSize': 14, "backgroundColor":'#E4FFC9', 'padding-left':'40px'})      

        ])

    ], lg=7)

]),
    dbc.Row([

    dbc.Col(children=[

        dbc.Row([ 
                
            html.Div([
                html.Pre(id='web_link', children=[],
                    #'height':'100vh'
                    style={'padding-bottom':'20px','padding-left':'30px', "backgroundColor":'#E4FFC9'}
                    )
            ])      

        ])

    ], lg=7)

]),


])



# Output of Graph
@app.callback(Output('graph', 'figure'),
              [Input('tour_lenght_name', 'value')

              ])

def update_figure(chosen_lenght):
    
    df_sub = df_table[(df_table['Tour_Length'].isin(chosen_lenght))]
    
    #df_sub = df_table[(df_table['Tour_Length'].isin(chosen_lenght)) &
    #            (df_table['Date'].isin(chiden_day))]

    

    # Create figure
    locations=[
    go.Scattermapbox(
        lat=df_sub['breitengrad'],
        lon=df_sub['laengengrad'],
        mode='markers',
        #hovertext=df_sub["Tour"],

        #text=[df_sub['Tour'][i] + '</b><br><br>' + df_sub['Date'][i] for i in range(df_sub.shape[0])],
        text=df_sub['Tour'] + '</b><br>' + df_sub['Date'] + '</b><br>' + df_sub["difficulty_lvl"] + '</b><br>' + df_sub['Availability'],
        #hoverinfo='text',
        hovertemplate = "<b>%{text}</b>" + "<extra></extra>",
        marker=go.scattermapbox.Marker(
            color="red",
            size = [20, 20, 20, 20]
            #showscale=True,
            #colorbar={'title':'Meters up', 'titleside':'top', 'thickness':4, 'ticksuffix':' m'},
        ),
        unselected={'marker': {'opacity': 0.8}},
        selected={'marker': {'opacity': 0.5, 'size': 18}},
        customdata=df_sub['link']

    
)]



    return {
            'data': locations,
            'layout': go.Layout(
            uirevision= 'foo', #preserves state of figure/map after callback activated
            clickmode= 'event+select',
            hovermode='closest',
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            hoverdistance=2,
            title=dict(text="UPCOMING HIKES",font=dict(family="Burnest Rough Regular",size=35, color='#7C7672')),
            mapbox_style="open-street-map",
            width=800, 
            height=500,
            mapbox=dict(
            center=go.layout.mapbox.Center(lat=47, lon=9),
            zoom=8),
            margin=dict(
        l=30,
        r=30,
        b=30,
        t=80,
        pad=4
    ),
        )
    }





# callback for Web_link
@app.callback(
    Output('web_link', 'children'),
    [Input('graph', 'clickData')])
def display_click_data(clickData):

    if clickData is None:
        #return 'Tour program, linked'
        return
    else:
        # print (clickData)
        the_link = clickData['points'][0]['customdata']
        name = clickData['points'][0]['text']
        button_name = name.split("<",1)[0]
        if the_link is None:
            return 'No Website Available'
        else:
            #return html.A(the_link, href=the_link, target="_blank")
            #for i in df_table['Tour']:
            #    a = i
                        
            return html.A(dbc.Button("Link to hike: "+button_name, color="success"), href=the_link, target="_blank")





if __name__ == '__main__':
    app.run_server()  # Turn off reloader if inside Jupyter

