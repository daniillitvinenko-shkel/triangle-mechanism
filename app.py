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
st.title("Интерактивная динамическая модель триады \"Бегущий треугольник\"")
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
fig, ax = plt.subplots(figsize=(6, 6), dpi=120)
ax.set_xlim(-4.5, 4.5)
ax.set_ylim(-4.5, 4.5)
ax.axis('off')

# Расчет углов (ПО часовой стрелке)
angle_deg = - ((current_year - start_year) / years_per_rotation) * 360
angle_rad = np.radians(angle_deg)

# Координаты треугольников с учетом рассчитанной фазы
v_out = np.array([
    rotate_point(R_out * np.cos(alpha_I), R_out * np.sin(alpha_I), angle_rad),
    rotate_point(R_out * np.cos(alpha_P), R_out * np.sin(alpha_P), angle_rad),
    rotate_point(R_out * np.cos(alpha_A), R_out * np.sin(alpha_A), angle_rad)
])

v_in = np.array([
    rotate_point(R_in * np.cos(alpha_I), R_in * np.sin(alpha_I), angle_rad),
    rotate_point(R_in * np.cos(alpha_P), R_in * np.sin(alpha_P), angle_rad),
    rotate_point(R_in * np.cos(alpha_A), R_in * np.sin(alpha_A), angle_rad)
])

# Физика жидкости (гравитационный уровень рассчитывается автоматически)
inner_poly = Polygon(v_in)
y_min, y_max = np.min(v_in[:, 1]), np.max(v_in[:, 1])
target_area = inner_poly.area * fill_fraction

low, high = y_min, y_max
for _ in range(20):
    mid = (low + high) / 2
    water_box = box(-5, -5, 5, mid)
    if inner_poly.intersection(water_box).area < target_area:
        low = mid
    else:
        high = mid
y_level = (low + high) / 2

liquid_poly = inner_poly.intersection(box(-5, -5, 5, y_level))

if not liquid_poly.is_empty:
    if liquid_poly.geom_type == 'Polygon':
        lx, ly = liquid_poly.exterior.xy
        ax.fill(lx, ly, color='#5dade2', alpha=0.85, zorder=1)
    elif liquid_poly.geom_type == 'MultiPolygon':
        for poly in liquid_poly.geoms:
            lx, ly = poly.exterior.xy
            ax.fill(lx, ly, color='#5dade2', alpha=0.85, zorder=1)

# Отрисовка контуров
poly_out_patch = patches.Polygon(v_out, closed=True, fill=False, edgecolor='#2c3e50', linewidth=3, zorder=3)
poly_in_patch = patches.Polygon(v_in, closed=True, fill=False, edgecolor='#34495e', linewidth=2.5, zorder=3)
ax.add_patch(poly_out_patch)
ax.add_patch(poly_in_patch)

# Буквы P, A, I (соответствуют индексам v_out: 0=I, 1=P, 2=A)
labels = ['I', 'P', 'A']
for i, pt in enumerate(v_out):
    vector = pt / np.linalg.norm(pt)
    text_pos = pt + vector * 0.4
    ax.text(text_pos[0], text_pos[1], labels[i], ha='center', va='center',
            fontsize=16, fontweight='bold', color='#2c3e50', rotation=0)
            
# Буква R (статичная в центре)
ax.text(0, 0, 'R', ha='center', va='center', fontsize=18, fontweight='bold', 
        color='#2c3e50', rotation=0, zorder=4)

# Статичная рамка с бегущими годами
frame_x, frame_y, frame_w, frame_h = -1.2, 3.6, 2.4, 0.7
rect_frame = patches.Rectangle((frame_x, frame_y), frame_w, frame_h, 
                               facecolor='#f8f9f9', edgecolor='#7f8c8d', linewidth=2, zorder=5)
ax.add_patch(rect_frame)

year_spacing = 1.6  
for y_val in range(start_year - 2, end_year + 3):
    x_pos = (y_val - current_year) * year_spacing
    
    if frame_x - 1 < x_pos < frame_x + frame_w + 1:
        # Синхронное переключение цвета по round()
        is_current = (y_val == round(current_year))
        t_obj = ax.text(x_pos, frame_y + frame_h/2, str(y_val), 
                        ha='center', va='center', fontsize=15, 
                        fontweight='bold', color='#c0392b' if is_current else '#7f8c8d', 
                        zorder=6)
        t_obj.set_clip_path(rect_frame)

# Вывод графики на страницу
st.pyplot(fig, clear_figure=True)
