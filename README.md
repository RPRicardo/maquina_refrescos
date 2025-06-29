
# Simulador de Máquina Expendedora - Análisis Semántico

Este proyecto implementa un **simulador y analizador semántico** de una máquina expendedora utilizando **análisis descendente decorado** con atributos. Permite validar cadenas construidas con los símbolos:

- `$` → Insertar moneda (+1)
- `R` → Comprar refresco (costo 3 monedas, máximo 3 por bloque)
- `<` → Devolver moneda (-1)
- `{` y `}` → Abrir/Cerrar niveles de anidación (máximo 3 niveles)

---

## Modos de Ejecución

Al ejecutar el programa, se ofrece un menú:


1. Interfaz Gráfica
2. Modo Consola
3. Cargar desde archivo




## Requisitos

- Python 3.6+
- Tkinter (incluido en la mayoría de distribuciones de Python)

---

## Ejecución

```
python3 maquinaui_.py
```

---
