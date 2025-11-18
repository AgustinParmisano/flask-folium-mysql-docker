# Archivos de Datos para Importación

Esta carpeta contiene archivos CSV de ejemplo que pueden ser importados en el mapa.

## Formato de los Archivos CSV

Todos los archivos CSV deben tener las siguientes columnas:

- `latitud`: Latitud del punto (decimal, ej: -34.9215)
- `longitud`: Longitud del punto (decimal, ej: -57.9545)
- `nombre`: Nombre del punto (texto)
- `ciudad`: Ciudad a la que pertenece (texto, ej: "La Plata")
- `tipo`: Tipo de punto (texto: "edificio", "parque", "zona", "fibra_optica")

## Archivos Disponibles

### edificios.csv
Contiene información de edificios importantes de La Plata.

**Ejemplo:**
```csv
latitud,longitud,nombre,ciudad,tipo
-34.9215,-57.9545,Catedral de La Plata,La Plata,edificio
-34.9200,-57.9500,Edificio Municipal,La Plata,edificio
```

### parques.csv
Contiene información de parques. Al importar, se trazarán zonas circulares alrededor de cada parque.

**Ejemplo:**
```csv
latitud,longitud,nombre,ciudad,tipo
-34.9100,-57.9500,Paseo del Bosque,La Plata,parque
-34.9300,-57.9600,Parque Saavedra,La Plata,parque
```

### zonas.csv
Contiene información de zonas genéricas (plazas, áreas, etc.).

**Ejemplo:**
```csv
latitud,longitud,nombre,ciudad,tipo
-34.9190,-57.9550,Plaza Moreno,La Plata,zona
-34.9185,-57.9540,Plaza San Martín,La Plata,zona
```

### fibra_optica.csv
Contiene puntos de cables de fibra óptica. Los puntos se conectarán con líneas en el orden que aparecen en el archivo.

**Ejemplo:**
```csv
latitud,longitud,nombre,ciudad,tipo
-34.9220,-57.9530,Punto Fibra 1,La Plata,fibra_optica
-34.9205,-57.9520,Punto Fibra 2,La Plata,fibra_optica
```

## Cómo Usar

1. **Desde el sidebar del mapa:**
   - Haz clic en "Seleccionar CSV" para elegir un archivo
   - Luego haz clic en "Importar [Tipo]" para cargar los datos

2. **Archivos por defecto:**
   - Si no seleccionas un archivo, el sistema intentará usar los archivos por defecto de esta carpeta
   - Si no existen archivos por defecto, intentará cargar desde la base de datos

## Notas

- Los archivos deben estar en formato CSV con codificación UTF-8
- La primera fila debe contener los nombres de las columnas
- Los valores numéricos (latitud, longitud) deben usar punto (.) como separador decimal
- El campo `tipo` debe coincidir exactamente con uno de los tipos soportados

