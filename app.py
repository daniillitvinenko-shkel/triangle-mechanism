import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, box

# 1. Настройка веб-страницы
st.set_page_config(
    page_title="Интерактивная модель триады",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Заголовки и описание без иконок с указанием авторства
st.title('Интерактивная динамическая модель триады "Бегущий треугольник"')
st.markdown("""
Визуализация модели триады P/A/I "Бегущий треугольник" Даниила Литвиненко. Управляйте с помощью ползунка ниже.
Наблюдайте за вращением конструкции, перетоком ренты (R) и смещением временной шкалы.
""")

# 2. Константы геометрии
start_year = 1935
end_year = 2030
years_per_rotation = 30

R_out = 3.0    
R_in = 1.3     
fill_fraction = 0.40  

# РАССЧИТАНА НОВАЯ ФАЗА: В 1935 году заданы углы так, чтобы в 2020 году 'I' был строго вверху (90°)
alpha_I = np.radians(30)    
alpha_P = np.radians(270)   
alpha_A = np.radians(150)   

def rotate_point(x, y, angle):
    co, si = np.cos(angle), np.sin(angle)
    return x * co - y * si, x * si + y * co

# 3. Элементы управления
current_year = st.slider(
    "Выберите год:", 
    min_value=float(start_year), 
    max_value=float(end_year), 
    value=float(start_year), 
    step=0.1,
    format="%.1f"
)

# 4. Логика отрисовки (Matplotlib)
fig, ax = plt.subplots(figsize)
