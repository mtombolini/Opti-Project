

# Optimización de Riego Agrícola

Este proyecto implementa un modelo de optimización para la planificación de riego agrícola utilizando Gurobi y Python. Permite evaluar decisiones de uso de recursos hídricos, métodos de riego, tecnologías de automatización y monitoreo, con base en datos técnicos y económicos reales.

## 📁 Estructura del Proyecto

- `main.py`: Script principal que orquesta la ejecución completa del modelo.
- `data_loader.py`: Carga, preprocesa y estructura todos los datos requeridos por el modelo, provenientes de `Data.xlsx`.
- `model_builder.py`: Construye el modelo de optimización con Gurobi utilizando los datos y parámetros.
- `solver.py`: Contiene la lógica de resolución del modelo.
- `output_handler.py`: Imprime y reporta los resultados relevantes de la solución obtenida.
- `config.py`: Define los conjuntos estáticos como número de áreas, días, fuentes y listas asociadas.
- `Data.xlsx`: Fuente principal de datos reales del problema.

## ⚙️ Cómo ejecutar

```bash
python main.py
```

El script:
1. Carga los datos (`data_loader.py`).
2. Construye el modelo (`model_builder.py`).
3. Resuelve el modelo (`solver.py`).
4. Reporta resultados (`output_handler.py`).
5. Si el modelo es inviable, genera diagnóstico IIS.

## 📊 Archivos y Funcionalidad

### `config.py`

Define los conjuntos base:
- `NA`: Número de sectores.
- `NT`: Número de días.
- `NF`: Número de fuentes.
- `A`, `T`, `F`: Listas indexadas de sectores, días y fuentes respectivamente.

### `data_loader.py`

Lee `Data.xlsx` y construye:

**Conjuntos:**
- `R`: Métodos de riego.
- `S`: Tipos de suelo.
- `E`: Tipos de energía.
- `P`: Pares fuente-energía.

**Parámetros:**
- `da`: Demanda hídrica por tipo de suelo.
- `eta`: Eficiencia por método de riego.
- `cW`: Costo unitario del agua.
- `beta`: Costo oportunidad por no cultivar.
- `cD`: Penalización por déficit hídrico.
- `Qmax`: Límite de extracción por fuente.
- `C`: Capacidad del estanque.
- `lltanque`: Recolección diaria de lluvia.
- `hf`, `eta_p`: Parámetros hidráulicos para energía.
- `cE`: Costo energético por fuente y día.
- `x_inv`, `phi_inv`, `ex`, `ephi`: Parámetros de inversión y consumo de tecnologías.
- `Qriego`: Caudal máximo por área.

Todos los valores son procesados desde hojas específicas del archivo Excel.

### `model_builder.py`

Define el modelo de optimización:
- Variables: riego (`qa`), cultivo (`za`), déficit (`delta`), uso de método (`ua`), etc.
- Función objetivo: minimiza costos de agua, energía, penalización por no cultivar, déficit y tecnología.
- 9 restricciones activas (R1-R9):
  - R1: método único por día y área.
  - R2: balance hídrico.
  - R3: límite de extracción.
  - R4: balance del estanque.
  - R5: automatización requiere monitoreo.
  - R6: activación de riego solo si se cultiva.
  - R7: [eliminada temporalmente].
  - R8: caudal máximo por área.
  - R9: déficit permitido solo si se cultiva.
  - R10: [eliminada temporalmente].

### `output_handler.py`

Imprime los resultados del modelo:
- Volúmenes de riego utilizados.
- Sectores cultivados.
- Déficit hídrico.
- Métodos de riego seleccionados.
- Costo total.
- Activación de tecnologías.

### `main.py`

Función `main()` que:
1. Llama a `load_data()`.
2. Construye el modelo.
3. Lo resuelve y diagnostica infeasibilidad si es necesario.
4. Imprime resultados.

## 🧪 Parámetros clave para experimentar

Puedes modificar estos parámetros en el Excel (`Data.xlsx`) para observar diferentes comportamientos:

- `beta`: Costo de oportunidad por no cultivar (`Areas`).
- `cD`: Penalización por déficit hídrico (`Penalización`).
- `cW`: Costo del agua por fuente (`Costo unitario agua`).
- `cE`: Costo energético por fuente (`implícito en código`).
- `hf`, `eta_p`: Parámetros hidráulicos (`Altura manometrica`, `Bomba`).
- `x_inv`, `phi_inv`: Costos de inversión de monitoreo y automatización (`automatico`).
- `eta`: Eficiencia de riego (`eficiencia metodos`).
- `da`: Demanda hídrica por tipo de suelo (`Suelos necesidades`).
- `lltanque`: Lluvia recolectada por día (`Promedio lluvia diario`).

## 🧠 Consideraciones

- Si ningún sector es cultivado, probablemente los costos superan los beneficios.
- Puedes forzar cultivo aumentando `beta` o reduciendo `cW`, `cD`, o `cE`.
- Si el modelo es inviable, se imprime el conjunto IIS para depurar.

## 🧩 Dependencias

- Python ≥ 3.8
- Gurobi
- Pandas
- openpyxl

Instalación sugerida:

```bash
pip install gurobipy pandas openpyxl
```

## 📍 Autoría

Proyecto desarrollado para la entrega 2 del curso ICS1113 – Optimización. Modelado, resolución e integración técnica por el equipo G78.