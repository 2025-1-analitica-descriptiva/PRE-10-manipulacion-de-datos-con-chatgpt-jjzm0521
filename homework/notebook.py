import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker # Necesario para FuncFormatter
import os

# --- Configuración de Nombres de Archivo y Directorios ---
# Se asume que este script se ejecuta desde la raíz del proyecto.
# Por ejemplo, si el script está en 'raiz_proyecto/homework/analisis_conductores.py',
# y lo ejecutas desde 'raiz_proyecto' con 'python homework/analisis_conductores.py',
# os.getcwd() será 'raiz_proyecto'.

# Directorio base para los archivos (relativo al CWD)
base_files_dir = 'files'

# Rutas de entrada usando os.path.join para portabilidad
input_dir = os.path.join(base_files_dir, 'input')
input_driver_file = os.path.join(input_dir, 'drivers.csv')
input_timesheet_file = os.path.join(input_dir, 'timesheet.csv')

# Directorios de salida usando os.path.join
# output_dir es para el CSV: files/output/
output_dir_for_csv = os.path.join(base_files_dir, 'output')
# plots_dir es para la imagen: files/plots/
output_dir_for_plots = os.path.join(base_files_dir, 'plots')

# Crear directorios de salida si no existen
os.makedirs(output_dir_for_csv, exist_ok=True)
os.makedirs(output_dir_for_plots, exist_ok=True)

# Rutas de los archivos de salida
output_summary_csv = os.path.join(output_dir_for_csv, 'summary.csv')
output_plot_png = os.path.join(output_dir_for_plots, 'top10_drivers.png')

# --- Cargar los Datos ---
try:
    print(f"Intentando cargar drivers desde: {os.path.abspath(input_driver_file)}")
    drivers_df = pd.read_csv(input_driver_file)
    print(f"Intentando cargar timesheet desde: {os.path.abspath(input_timesheet_file)}")
    timesheet_df = pd.read_csv(input_timesheet_file)
except FileNotFoundError:
    print(f"Error: Asegúrate de que los archivos '{input_driver_file}' y '{input_timesheet_file}' existan en las rutas especificadas.")
    print(f"Ruta de trabajo actual (desde donde se ejecuta el script): {os.getcwd()}")
    print(f"Ruta absoluta esperada para drivers: {os.path.abspath(input_driver_file)}")
    print(f"Ruta absoluta esperada para timesheet: {os.path.abspath(input_timesheet_file)}")
    exit()
except Exception as e:
    print(f"Ocurrió un error al cargar los archivos CSV: {e}")
    exit()

print("Archivos CSV cargados exitosamente.")
print("\nPrimeras filas de la tabla 'drivers':")
print(drivers_df.head())
print("\nPrimeras filas de la tabla 'timesheet':")
print(timesheet_df.head())

# --- 1. Calcular el promedio de "hours-logged" y "miles-logged" por driverId ---
print("\n--- 1. Promedios por conductor ('average_logs') ---")
average_logs = timesheet_df.groupby('driverId')[['hours-logged', 'miles-logged']].mean()
print(average_logs.head())

# --- 2. Crear "timesheet_with_means" ---
print("\n--- 2. Creando 'timesheet_with_means' ---")
# Calcular el promedio de 'hours-logged' por 'driverId' usando transform para mantener la forma original
mean_hours_transform = timesheet_df.groupby('driverId')['hours-logged'].transform('mean')
timesheet_with_means_df = timesheet_df.copy()
timesheet_with_means_df['mean_hours-logged'] = mean_hours_transform
print(timesheet_with_means_df.head())

# --- 3. Crear "timesheet_below" ---
print("\n--- 3. Creando 'timesheet_below' ---")
timesheet_below_df = timesheet_with_means_df[timesheet_with_means_df['hours-logged'] < timesheet_with_means_df['mean_hours-logged']]
print(timesheet_below_df.head())

# --- 4. Crear "sum_timesheet" ---
print("\n--- 4. Creando 'sum_timesheet' ---")
sum_timesheet_df = timesheet_df.groupby('driverId')[['hours-logged', 'miles-logged']].sum()
print(sum_timesheet_df.head())

# --- 5. Crear "summary" ---
print("\n--- 5. Creando 'summary' ---")
drivers_subset_df = drivers_df[['driverId', 'name']]
# Asegurarse de que driverId sea una columna en sum_timesheet_df para el merge
summary_df = pd.merge(sum_timesheet_df.reset_index(), drivers_subset_df, on='driverId', how='left')
print(summary_df.head())

# --- 6. Crear "min_max_timesheet" ---
print("\n--- 6. Creando 'min_max_timesheet' ---")
min_max_timesheet_df = timesheet_df.groupby('driverId')['hours-logged'].agg(['min', 'max']).rename(
    columns={'min': 'min_hours-logged', 'max': 'max_hours-logged'}
)
print(min_max_timesheet_df.head())

# --- 7. Guardar "summary" en un archivo CSV ---
print(f"\n--- 7. Guardando 'summary' en '{output_summary_csv}' ---")
summary_df.to_csv(output_summary_csv, index=False, header=True, sep=',')
print(f"Tabla 'summary' guardada exitosamente en {output_summary_csv}")

# --- 8. Crear "top10" ---
print("\n--- 8. Creando 'top10' ---")
top10_df = summary_df.sort_values(by='miles-logged', ascending=False).head(10)
print(top10_df)

# --- 9. Crear gráfico de barras horizontales ---
print(f"\n--- 9. Creando gráfico de barras y guardándolo en '{output_plot_png}' ---")
if not top10_df.empty:
    # Preparar datos para graficar, similar al notebook
    top10_plot_df = top10_df.set_index('name')

    plt.figure(figsize=(10, 7)) # Tamaño similar al del notebook
    
    # Graficar
    top10_plot_df['miles-logged'].plot.barh(color='tab:orange', alpha=0.7)
    
    plt.xlabel('Millas Registradas')
    plt.ylabel('Nombre del Conductor')
    plt.title('Top 10 Conductores por Millas Registradas')
    
    plt.gca().invert_yaxis() # Para que el conductor con más millas esté arriba
    
    # Formatear eje X para mostrar números con comas
    plt.gca().get_xaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
    )
    
    plt.xticks(rotation=45, ha='right') # Rotar etiquetas del eje X para mejor lectura
    
    # Estilo de los bordes (spines)
    plt.gca().spines['left'].set_color('lightgray')
    plt.gca().spines['bottom'].set_color('gray')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    plt.tight_layout() # Ajustar diseño para que todo encaje bien
    plt.savefig(output_plot_png, bbox_inches='tight')
    print(f"Gráfico guardado exitosamente en {output_plot_png}")
    # plt.show() # Descomentar si quieres mostrar el gráfico interactivamente
else:
    print("La tabla 'top10_df' está vacía. No se puede generar el gráfico.")

print("\n--- Proceso Completado ---")
print(f"Verifica la carpeta '{os.path.abspath(output_dir_for_csv)}' para el archivo CSV.")
print(f"Verifica la carpeta '{os.path.abspath(output_dir_for_plots)}' para el gráfico.")
