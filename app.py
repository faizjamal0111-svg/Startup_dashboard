import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title='Startup Analysis')

df = pd.read_csv('startup_cleaned.csv')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

st.sidebar.title('Startup Analysis')
option = st.sidebar.selectbox('Select one', ['Overall Analysis', 'Startup', 'Investor'])


# OVERALL ANALYSIS
def overall_analysis():
    st.title('Overall Analysis')

    # total funded startups
    funded = df['startup'].nunique()
    # total amount invested
    total = round(df['amount in Cr'].sum())
    # max investment
    max_investment = df.groupby('startup')['amount in Cr'].max().sort_values(ascending=False).head().values[0]
    # avg investment
    avg = round(total / funded)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Total funded startups', funded)
    with col2:
        st.metric('Total amount invested', str(total) + 'Cr')
    with col3:
        st.metric('Maximum investment', str(max_investment) + 'Cr')
    with col4:
        st.metric('Average amount invested', str(avg) + 'Cr')

    st.header('Month on Month Investments')
    selected_option = st.selectbox('Select Type', ['Total', 'Count'])
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount in Cr'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount in Cr'].count().reset_index()

    # sort numerically first
    temp_df = temp_df.sort_values(by=['year', 'month'])

    # create a proper datetime column
    temp_df['date'] = pd.to_datetime(temp_df['year'].astype(str) + '-' + temp_df['month'].astype(str) + '-01')

    # plot using datetime column
    st.line_chart(temp_df.set_index('date')['amount in Cr'])

    top_startup = df.groupby('startup')['amount in Cr'].sum().sort_values(ascending=False).head(20)
    top_investors = df.groupby('investors')['amount in Cr'].sum().sort_values(ascending=False).head(20)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Top funded startups')
        st.dataframe(top_startup)
    with col2:
        st.subheader('Top investors')
        st.dataframe(top_investors)

    col3, col4 = st.columns(2)
    with col3:
        top_city = df.groupby('city')['amount in Cr'].sum().sort_values(ascending=False).head()
        st.subheader('Top 5 cities')
        fig1, ax1 = plt.subplots()
        ax1.bar(top_city.index, top_city.values)

        st.pyplot(fig1)

    with col4:
        # type of funding
        funding = df.groupby('round')['amount in Cr'].sum().sort_values(ascending=False).head()
        st.subheader('Top 5 Rounds')
        fig2, ax2 = plt.subplots()
        ax2.pie(funding, labels=funding.index, autopct='%1.1f%%', )

        st.pyplot(fig2)

    col5, col6 = st.columns(2)

    with col5:
        top_sectors = df.groupby('vertical')['amount in Cr'].sum().sort_values(ascending=False).head(10)
        st.subheader('Top 10 funded sectors')
        fig3, ax3 = plt.subplots()
        ax3.pie(top_sectors, labels=top_sectors.index, autopct='%1.1f%%', )

        st.pyplot(fig3)

    with col6:
        sectors_count = df.groupby('vertical')['amount in Cr'].count().sort_values(ascending=False).head(10)
        st.subheader('Top 10 sectors')
        fig4, ax4 = plt.subplots()
        ax4.pie(sectors_count, labels=sectors_count.index, autopct='%1.1f%%', )

        st.pyplot(fig4)


# COMPANY DETAILS
def company_details(company):
    st.title(company)
    temp_df = df[df['startup'] == company]

    industry = temp_df['vertical'].values[0]
    subindustry = temp_df['subvertical'].values[0]
    location = temp_df['city'].values[0]
    total_money = temp_df['amount in Cr'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Industry Type', industry)
    with col2:
        st.metric('Sub Industry Type', subindustry)
    with col3:
        st.metric('Location', location)
    with col4:
        st.metric('Total Money invested', total_money)

    col5, col6 = st.columns(2)
    with col5:
        rounds = temp_df.groupby('round')['amount in Cr'].sum()
        st.subheader('Rounds')
        fig1, ax1 = plt.subplots()
        ax1.pie(rounds, labels=rounds.index, autopct='%1.1f%%')
        st.pyplot(fig1)

    with col6:
        # 2. Split the 'investors' string by comma and explode into individual rows
        discrete_investors = temp_df.assign(investors=temp_df['investors'].str.split(',')).explode('investors')

        # 3. Strip whitespace (to avoid " Sequoia" being different from "Sequoia")
        discrete_investors['investors'] = discrete_investors['investors'].str.strip()

        # 4. Now GroupBy
        investor_counts = discrete_investors.groupby('investors')['amount in Cr'].sum()

        # Plotting
        st.subheader('Investors')
        fig2, ax2 = plt.subplots()
        ax2.pie(investor_counts, labels=investor_counts.index, autopct='%1.1f%%')
        st.pyplot(fig2)


# INVESTOR DETAILS
def load_investor_details(investor):
    st.title(investor)
    # load recent 5 investments
    last_5_df = df[df['investors'].str.contains(investor)].head()[
        ['date', 'startup', 'vertical', 'city', 'amount in Cr']]
    st.subheader('Most recent investments')
    st.dataframe(last_5_df)

    col1, col2 = st.columns(2)
    with col1:
        # biggest investments
        biggest_investments = df[df['investors'].str.contains(investor)].groupby('startup')[
            'amount in Cr'].sum().sort_values(
            ascending=False).head()
        st.subheader('Biggest investments')
        st.dataframe(biggest_investments)

    with col2:
        vertical_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount in Cr'].sum()
        st.subheader('Sectors invested')
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series, labels=vertical_series.index, autopct='%1.1f%%', )

        st.pyplot(fig1)

    col3, col4 = st.columns(2)
    with col3:
        round_series = df[df['investors'].str.contains(investor)].groupby('round')['amount in Cr'].sum()
        st.subheader('Rounds')
        fig2, ax2 = plt.subplots()
        ax2.pie(round_series, labels=round_series.index, autopct='%1.1f%%', )

        st.pyplot(fig2)

    with col4:
        city_series = df[df['investors'].str.contains(investor)].groupby('city')['amount in Cr'].sum()
        st.subheader('Cities Invested')
        fig3, ax3 = plt.subplots()
        ax3.pie(city_series, labels=city_series.index, autopct='%1.1f%%', )

        st.pyplot(fig3)

    year_series = df[df['investors'].str.contains(investor)].groupby('year')['amount in Cr'].sum()
    st.subheader('Year on year Investment')
    fig4, ax4 = plt.subplots()
    ax4.plot(year_series.index, year_series.values)

    st.pyplot(fig4)


if option == 'Overall Analysis':
    overall_analysis()

elif option == 'Startup':
    selected_company = st.sidebar.selectbox('Select Startup', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Start Analysis')
    if btn1:
        company_details(selected_company)

else:
    selected_investor = st.sidebar.selectbox('Select Investor', sorted(df['investors'].unique().tolist()))
    btn2 = st.sidebar.button('Start Analysis')
    if btn2:
        load_investor_details(selected_investor)

