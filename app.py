import streamlit as st
import requests
import pandas as pd
import numpy as np
from joblib import Parallel, delayed
import matplotlib.pyplot as plt

st.title("Open Weather Map")

df = None
uploaded_file = st.file_uploader("Загрузите .csv файл с историей температуры", type="csv")
if uploaded_file is not None:
    st.success("Файл успешно загружен!")
    df = pd.read_csv(uploaded_file)

cities = [
    "New York",
    "London",
    "Paris",
    "Tokyo",
    "Moscow",
    "Sydney",
    "Berlin",
    "Beijing",
    "Rio de Janeiro",
    "Dubai",
    "Los Angeles",
    "Singapore",
    "Mumbai",
    "Cairo",
    "Mexico City"
]

selected_city = st.selectbox("Выберите город", cities)

api_key = st.text_input("Введите ваш OpenWeatherMap API ключ", type="password")
if api_key:
    test_url = f"http://api.openweathermap.org/data/2.5/weather?q=Moscow&appid={api_key}&units=metric&lang=ru"
    response = requests.get(test_url)
    if response.status_code == 200:
        st.success("API ключ введён!")
    else:
        st.error(response.json())

button = st.button("Показать статистику")
if button:
    if df is None:
        st.error("Файл не загружен!")
    elif 'city' not in df.columns:
        st.error("Файл не содержит столбец с городами!")
    elif 'temperature' not in df.columns:
        st.error("Файл не содержит столбец с температурами!")
    elif api_key is None or api_key == "":
        st.error("API ключ не введён!")
    else:
        city_df = df[df['city'] == selected_city]
        if city_df.empty:
            st.error("Город не найден в файле!")
        else:
            st.write(f'Средняя температура: {city_df["temperature"].mean():.2f}°C')
            st.write(f'Максимальная температура: {city_df["temperature"].max():.2f}°C')
            st.write(f'Минимальная температура: {city_df["temperature"].min():.2f}°C')
            st.write(f'Количество измерений: {city_df["temperature"].count()}')
            st.write(f'Стандартное отклонение: {city_df["temperature"].std():.2f}')

            means = {}
            stds = {}
            for season in city_df['season'].unique():
                means[season] = city_df[city_df['season'] == season]['temperature'].mean()
                stds[season] = city_df[city_df['season'] == season]['temperature'].std()

            city_df['is_anomaly'] = abs(city_df['temperature'] - means[city_df['season'].values[0]]) > 2 * stds[city_df['season'].values[0]]

            fig, ax = plt.subplots()
            norm_points = city_df[~city_df['is_anomaly']]
            anomaly_points = city_df[city_df['is_anomaly']]
            ax.scatter(norm_points.index, norm_points['temperature'], color='blue', label='Not Anomaly')
            ax.scatter(anomaly_points.index, anomaly_points['temperature'], color='red', label='Anomaly')
            ax.set_xlabel('Index')
            ax.set_ylabel('Temperature (°C)')
            ax.set_title(f'Temperatures in {selected_city}')
            ax.legend()
            st.pyplot(fig)

            for season in city_df['season'].unique():
                st.header(season)
                st.write(f'Средняя температура в {season}: {means[season]:.2f}°C')
                st.write(f'Стандартное отклонение в {season}: {stds[season]:.2f}')
                st.write(f"Количество измерений в {season}: {city_df[city_df['season'] == season]['temperature'].count()}")
                st.write(f"Максимальная температура в {season}: {city_df[city_df['season'] == season]['temperature'].max():.2f}°C")
                st.write(f"Минимальная температура в {season}: {city_df[city_df['season'] == season]['temperature'].min():.2f}°C")
                st.write(f"Количество аномалий в {season}: {city_df[city_df['season'] == season]['is_anomaly'].sum()}")
            
            URL = f'http://api.openweathermap.org/data/2.5/weather?q={selected_city}&appid={api_key}&units=metric&lang=ru'
            response = requests.get(URL)
            if response.status_code == 200:
                temp = response.json()['main']['temp']
                descr = response.json()['weather'][0]['description']
                st.write(f"Текущая температура: {temp:.2f}°C, {descr}")

                if abs(temp - city_df['temperature'].mean()) <= 2 * city_df['temperature'].std():
                    st.success(f"Аномалий не наблюдается в {selected_city}!")
                else:
                    st.error(f"Аномалия наблюдается в {selected_city}!")
            else:
                st.error(response.json())
