# Importing libraries
import streamlit as st
import pandas as pd
import numpy as np
import scipy as sp
import plotly as py
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import pycountry_convert as pc
import matplotlib.pyplot as plt
from PIL import Image
st.set_page_config(layout = 'wide')

# Loading AUB-OSB logo
image = Image.open("osb_logo.png")
#st.image(image)

logo = st.sidebar.image(image)

option = st.sidebar.selectbox(
    "Please select a dataset",
    ("Dataset Information Page","COVID19 Dataset", "HR Dataset")
)

if option == 'Dataset Information Page':
    st.title("Welcome to My Streamlit Assignment")
    st.subheader('Information About the Datasets')

    info = st.selectbox(
        "Click here to read some information about each dataset",
        ("COVID19 Dataset", "HR Dataset")
        )

    if info == 'COVID19 Dataset':
        col1, col2 = st.columns(2)
        with col1:
            st.header("COVID-19 Vaccination Progress ")
            st.info("""This dataset is composed of 43,439 records and 14 columns.
                        It contains information about the daily COVID-19 vaccinations
                        in all countries around the world starting from December 2020
                        until August 2021. Prior to constructing visualizations on the dataset,
                        some data mapiulation and cleaning was required.
                        """)

        with col2:
            image = Image.open("vaccine.jpeg")
            st.image(image)

    else:
        col1, col2 = st.columns(2)
        with col1:
            st.header("Human Resources Dataset")
            st.info("""This dataset is composed of 311 records and 36 columns.
                        It contains information collected by HR personnel about employees.
                        """)

        with col2:
            image = Image.open("HR.png")
            st.image(image)

elif option == 'COVID19 Dataset':
    # Dataset 1: COVID-19 Vaccinations

    # Loading the data
    df = pd.read_csv("/Users/dimadaouk/Documents/Data Visualization/Assignment 2- Vaccinations Dataset Plotly/vaccinations.csv")

    # Cleaning the dataset
    # Converting the date column's data type from object to datetime
    df['date'] = pd.to_datetime(df.date, format = '%Y-%m-%d', errors = 'coerce')

    # Adding a column 'date2' that only includes the month and year
    df['date2'] = df['date'].dt.strftime('%Y-%m')

    # Constructing a Pivot table
    cum_vaccine_by_location = pd.pivot_table(df,
                                             index = ['location', 'iso_code'],
                                             columns= 'date2',
                                             values = 'total_vaccinations',
                                             aggfunc = 'sum',
                                             fill_value = 0)
    # Re-arranging the pivot table
    cum_vaccine_by_location = cum_vaccine_by_location.stack().reset_index(level = 0).reset_index(level = 0).reset_index(level = 0)
    cum_vaccine_by_location.columns = ['date2', 'iso_code','location','total_vaccinations']

    # rearrange the columns
    cum_vaccine_by_location = cum_vaccine_by_location[['location', 'iso_code', 'date2', 'total_vaccinations']]

    # Adding a column (by appending the list to the df) that contains the cumulative total vaccinations
    cum_total_vaccinations = []
    total_vaccinations = 0
    for index, row in cum_vaccine_by_location.iterrows():
        if index == 0: # first record
            country = row['location']
            total_vaccinations = row['total_vaccinations']
            #cum_total_vaccinations.append(total_vaccinations)
        elif country ==  row['location']: #in same country
            total_vaccinations  = total_vaccinations + row['total_vaccinations']
            #cum_total_vaccinations.append(total_vaccinations)
        else: #new location / country
            country = row['location']
            total_vaccinations = row['total_vaccinations']

        cum_total_vaccinations.append(total_vaccinations)


    cum_vaccine_by_location2 = None
    cum_vaccine_by_location2 = cum_vaccine_by_location.copy()
    cum_vaccine_by_location2['cum_total_vaccinations'] = cum_total_vaccinations

    st.markdown('# COVID-19 Vaccination Progress')

    # Visualizing the wordwide COVID19 vaccination progress from 2020-12 to 2021-08-
    col1, col2 = st.columns(2)

    # Visualization 1: Choropleth Map
    with col1:
        st.markdown('### The Worldwide COVID-19 Vaccination Progress')

        fig = go.Figure(px.choropleth(cum_vaccine_by_location2, locations = 'iso_code', color = 'cum_total_vaccinations', hover_name = 'location',
                  animation_frame = 'date2', color_continuous_scale = px.colors.sequential.Plasma))
        st.plotly_chart(fig)

    # Visualization 2: Linechart
    with col2:
        st.markdown('### COVID19 Vaccination Trend by Continent')

        # Preparing the data
        # Function converting  iso country code to continent code
        def convert(iso_code3):
            try:
                alpha3_to_alpha2 = pc.country_alpha3_to_country_alpha2(iso_code3)
                alpha2_to_continent = pc.country_alpha2_to_continent_code(alpha3_to_alpha2)
                return alpha2_to_continent
            except:
                return ''

        # Applying the convert() function to the dataframe
        cum_vaccine_by_location2['continent'] = cum_vaccine_by_location2['iso_code'].apply(lambda iso_code: convert(iso_code))

        # Dropping records where continent is empty
        cum_vaccine_by_location2.drop(cum_vaccine_by_location2.loc[(cum_vaccine_by_location2['continent'] == '')].index,
                                      inplace = True)

        # Constructing a pivot table
        pivot_continent = pd.pivot_table(cum_vaccine_by_location2,
                          index = 'continent',
                          columns = 'date2',
                          values = 'cum_total_vaccinations',
                          aggfunc = 'sum',
                          fill_value = 0)

        # Converting pivot table to a dataframe
        df_continent = pivot_continent.stack().reset_index(level = 0).reset_index(level = 0)
        df_continent.columns = ['date2', 'continent', 'cum_total_vaccinations']

        # map continent code to continent name
        conti_names = {'AS':'Asia',
                       'SA':'South America',
                       'OC':'Oceania',
                       'AF':'Africa',
                       'EU':'Europe',
                       'NA':'North America'}

        df_continent['continent_name'] = df_continent['continent'].map(conti_names)

        # Plotting the linechart

        fig = px.line(df_continent, x = "date2", y = "cum_total_vaccinations",
                      color = 'continent_name')
        st.plotly_chart(fig, user_container_width = True)


else:
    # Dataset 2: HR dataset
    st.markdown('# HR Data')

    # Loading the data
    df = pd.read_csv("/Users/dimadaouk/Documents/Data Visualization/Assignment 2- HR Dataset Plotly/HRDataset_v14.csv")

    topic = st.radio(
    "Which topic would you like to explore?",
    ('Salaries', 'Employee Satisfaction', 'Recruitment and Performance'))

    if topic == 'Salaries':
        col1, col2 = st.columns(2)
        with col1:
            # Visualization 1: Violin Plots
            st.markdown('## Visualizing the Distribution of Employee Salaries Across Race')

            counts = df.RaceDesc.value_counts()

            df['Race'] = df['RaceDesc']

            # df.where() replaces the values where the condition is False
            df.Race.where(df.Race.isin(counts[counts >= 29].index),'Other', inplace = True)

            fig = px.violin(df, y = 'Salary', x ='Race', color = 'Sex', box = True, points = 'all')
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            # Visualization 2: Barplot
            st.markdown('## Visualizing the Relationship Between Gender and Salary Across Race')

            fig = px.bar(df, x = 'Sex', y = 'Salary', color = 'Race', barmode = 'group')
            st.plotly_chart(fig, user_container_width = True)


        # Visualization 7:
        st.markdown('## Visualizing Employee Salary Across Positions')

        fig = plt.figure(figsize=(25,10))
        sns.swarmplot(y=df['Salary'],
                      x=df['Position'])
        plt.xticks(rotation = 80)
        plt.title('Visualizing Employee Salary Across Positions')
        st.pyplot(fig, user_container_width = True)


    elif topic == 'Employee Satisfaction':

        col1, col2 = st.columns(2)
        with col1:

        # Visualization 4: Strip Charts
            st.markdown('## Visualizing the Relationship Between Employee Satisfaction and the Absences')

            fig = px.strip(df, x='EmpSatisfaction', y='Absences').update_traces(jitter = 1, opacity = 0.8)
            st.plotly_chart(fig, user_container_width = True)

        with col2:
            # Visualization 5: Parallel Coordinates Plot
            st.markdown('## Visualizing the Relationship Between Special Projects and Employee Satisfaction Per Department')

            df2 = df[["Department", "SpecialProjectsCount", "EmpSatisfaction", "DeptID"]]

            fig = px.parallel_coordinates(df2, color = 'DeptID', color_continuous_scale = ['red', 'green', 'blue'])
            st.plotly_chart(fig, user_container_width = True)

    else:
        st.write('Recruitment and performance')

        col1, col2 = st.columns(2)
        with col1:

            # Visualization 3: Stacked Barplot
            st.markdown('## Visualizing the Relationship Between Employee Performance and the Managers')

            # Grouping the data by manager name and employee performance score
            data = df.groupby(['ManagerName', 'PerformanceScore']).size().reset_index()

            # Adding a Count column
            data.columns = ['ManagerName', 'PerformanceScore', 'Count']

            # Arranging the values from largest to smallest
            data = data.sort_values('Count', ascending = False)

            # Display the data: barplot
            fig = px.bar(data, x = 'ManagerName', y = 'Count', color = 'PerformanceScore')
            st.plotly_chart(fig, user_container_width = True)

        with col2:
            # Visualization 6:
            st.markdown('## Visualizing the Recruitment Channels Used By HR')

            fig = px.pie(df, values = 'EmpID', names = 'RecruitmentSource')
            st.plotly_chart(fig, user_container_width = True)
