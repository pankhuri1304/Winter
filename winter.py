import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import streamlit as st
import helper
import preprocessor
import webbrowser

st.set_page_config(
    page_title="Winter Olympics Analysis",
    page_icon="https://cdn.dnaindia.com/sites/default/files/styles/full/public/2018/02/13/650978-winter-olympics-2018-pti.jpg",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Hide the Streamlit menu bar
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Set the Streamlit theme to light mode
st.write("""
    <style>
    .streamlit-legacy-theme {
        color: #262730;
        background-color: #f0f2f6;
    }
    body {
        background-image: url("your_image_url_here");
        background-size: cover;
    }
    </style>
    """, unsafe_allow_html=True)


df = pd.read_csv('Athletes_winter_games.csv')
region = pd.read_csv('regions.csv')

df = preprocessor.preprocess(df, region)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 0.5rem;
                    padding-bottom: 0rem;
                    padding-left: 0rem;
                    padding-right: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)



st.sidebar.image("https://img.freepik.com/premium-vector/sport-icon-design_24908-6325.jpg")
st.sidebar.title('Winter Olympics Analysis')

user_menu = st.sidebar.radio(
    label='Select an option',
    options=('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis',"Athlete's Overall Information")
)
# Modules Start
col1, col2 = st.columns([400, 50])
with col1:
    if user_menu == 'Medal Tally':
        st.sidebar.header("Medal Tally")
        years, country = helper.country_year_list(df)

        selected_year = st.sidebar.selectbox("Select Year", years)
        selected_country = st.sidebar.selectbox("Select Country", country)

        medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
        if selected_year == "Overall" and selected_country == "Overall":
            st.title("Overall Tally")
        if selected_year != "Overall" and selected_country == "Overall":
            st.title("Medal Tally in " + str(selected_year) + " Olympics")
        if selected_year == "Overall" and selected_country != "Overall":
            st.title(selected_country + "'s Overall Performance")
        if selected_year != "Overall" and selected_country != "Overall":
            st.title(selected_country + "'s Performance in " + str(selected_year) + " Olympics")

        st.table(medal_tally)

        medal_df = df
        if selected_year != "Overall" and selected_country != "Overall":
            temp_df = medal_df[(medal_df['Year'] == selected_year) & (medal_df['region'] == selected_country)]

            ath_w_medals = temp_df[['Name', 'NOC', 'Sport', 'Event', 'Medal']].dropna(subset=['Medal'])
            ath_w_medals = ath_w_medals.drop(columns='NOC')
            ath_w_medals_gold = ath_w_medals[ath_w_medals['Medal'] == 'Gold']
            ath_w_medals_silver = ath_w_medals[ath_w_medals['Medal'] == 'Silver']
            ath_w_medals_bronze = ath_w_medals[ath_w_medals['Medal'] == 'Bronze']

            gold = pd.DataFrame(ath_w_medals_gold.value_counts()).reset_index().rename(columns={0: 'Total'})
            silver = pd.DataFrame(ath_w_medals_silver.value_counts()).reset_index().rename(columns={0: 'Total'})
            bronze = pd.DataFrame(ath_w_medals_bronze.value_counts()).reset_index().rename(columns={0: 'Total'})
            total = pd.DataFrame(ath_w_medals.drop(columns=['Medal']).value_counts()).reset_index().rename(
                columns={0: 'Total'})

            total = total.merge(gold[['Name', 'Sport', 'Event', 'Total']], on=['Name', 'Sport', 'Event'],
                                how='outer').rename(columns={'Total_x': 'Total', 'Total_y': 'Gold'})
            total = total.merge(silver[['Name', 'Sport', 'Event', 'Total']], on=['Name', 'Sport', 'Event'],
                                how='outer').rename(columns={'Total_x': 'Total', 'Total_y': 'Silver'})
            total_ath = total.merge(bronze[['Name', 'Sport', 'Event', 'Total']], on=['Name', 'Sport', 'Event'],
                                    how='outer').rename(columns={'Total_x': 'Total', 'Total_y': 'Bronze'})
            total_ath = total_ath.fillna(0).convert_dtypes()
            st.table(total_ath)

    if user_menu == 'Country-wise Analysis':
        st.title("Country-wise Analysis")
        try:
            country_list = df['region'].dropna().unique().tolist()
            country_list.sort()

            selected_country = st.selectbox('Select a Country', country_list)

            country_df = helper.year_wise_medal_tally(df, selected_country)
            fig = px.line(country_df, x='Year', y='Medal')
            st.title(selected_country + " Medal Tally Over Years")
            st.plotly_chart(fig)

            st.title(selected_country + " excels in the following sports")
            pt = helper.country_event_heatmap(df, selected_country)
            fig, ax = plt.subplots(figsize=(20, 20))
            ax = sns.heatmap(pt, annot=True)
            st.pyplot(fig)

            st.title("Top 10 athletes of " + selected_country)
            top10_df = helper.most_successful_country_wise(df, selected_country)
            st.table(top10_df)
        except:
            st.info("No athlete from this country has ever won an Olympic medal!")

    if user_menu == "Athlete-wise Analysis":
        athlete_df = df.drop_duplicates(subset=['Name', 'region'])

        x1 = athlete_df['Age'].dropna()
        x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
        x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
        x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

        fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                                 show_hist=False, show_rug=False)

        st.title("Distribution of Age")
        st.plotly_chart(fig)

        st.title("Distribution of Age wrt Sports")
        mlist = ['Gold', 'Silver', 'Bronze']
        selected_medal = st.selectbox("Select Medal", mlist)
        st.subheader("For "+selected_medal+" Medal")
        x = []
        name = []
        famous_sports = ['Alpine Skiing', 'Biathlon', 'Bobsleigh', 'Cross Country Skiing', 'Curling',
                         'Figure Skating', 'Freestyle Skiing', 'Ice Hockey', 'Luge', 'Military Ski Patrol',
                         'Nordic Combined', 'Short Track Speed Skating', 'Skeleton', 'Ski Jumping',
                         'Snowboarding', 'Speed Skating']
        for sport in famous_sports:
            temp_df = athlete_df[athlete_df['Sport'] == sport]
            x.append(temp_df[temp_df['Medal'] == selected_medal]['Age'].dropna())
            name.append(sport)

        fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
        fig.update_layout(autosize=False, width=600, height=400)
        st.plotly_chart(fig)

        sport_list = df['Sport'].unique().tolist()
        sport_list.sort()
        sport_list.insert(0, 'Overall')

        st.title("Men Vs Women Participation Over the Years")
        final = helper.men_vs_women(df)
        fig = px.line(final, x="Year", y=["Male", "Female"])
        fig.update_layout(autosize=False, width=600, height=400)
        st.plotly_chart(fig)

    if user_menu == "Athlete's Overall Information":
        names = helper.names_info(df)
        st.header("Athlete's Overall Information")
        selected_name = st.selectbox ("Select an athlete", names)

        z = helper.dataz(df, selected_name)
        st.table(z)

        y = helper.datay(df, selected_name)
        st.table(y)

        x = helper.data(df, selected_name)
        st.table(x)

with col2:
    st.markdown('<a href="https://pankhuri1304-front-front-85jphc.streamlit.app/" target="_self" style="padding: 8px 10px; background-color: white; color: Black; text-align: center; text-decoration: none; display: inline-block; border-radius: 4px; border: 1px solid black; cursor: pointer;">Home</a>', unsafe_allow_html=True)

if user_menu == "Overall Analysis":
    editions = df['Year'].unique().shape[0]
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x='Edition', y='region')
    st.title("Participating Nations Over the Years")
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x='Edition', y='Event')
    st.title("Events Over the Years")
    st.plotly_chart(fig)

    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x='Edition', y='Name')
    st.title("Athletes Over the Years")
    st.plotly_chart(fig)

    st.title("No. of Events over time(Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
        annot=True)
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    selected_sport = st.selectbox("Select a Sport", sport_list)

    x = helper.most_successful(df, selected_sport)
    st.table(x)
