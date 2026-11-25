---
name: acontraluz-charts
description: Estándar visual y de accesibilidad (WCAG) para todas las figuras interactivas en Plotly del proyecto A contra(luz), tanto en el Jupyter Notebook como en Streamlit.
---

# Skill: Visualizaciones Accesibles en Plotly (`acontraluz-charts`)

Usa este skill siempre que diseñes, modifiques o audites cualquier gráfica en `src/visualizacion.py`, `A_contraluz_tutorial.ipynb` o `app_streamlit.py`. Adapta las buenas prácticas de claridad ejecutiva y accesibilidad WCAG al contexto de veeduría ciudadana en español.

---

## 1. Paleta de Colores de Alto Contraste (Amigable con Daltonismo)
Usar fondo blanco limpio (`plot_bgcolor="white"`, `paper_bgcolor="white"`) y colores con contraste ≥ 3:1 entre series y ≥ 4.5:1 para texto:

- **Azul Institucional Principal (Planeado / Serie 1):** `#0B3C5D`
- **Naranja Cobre (Ejecutado / Desviación positiva / Alerta):** `#C84E00`
- **Azul Petróleo / Teal (Serie 3 / Competencia abierta):** `#1D7874`
- **Ámbar Dorado (Serie 4 / Contratación directa):** `#D9822B`
- **Morado Pizarra (Serie 5):** `#5B4B8A`
- **Gris Grafito (Referencia, líneas base 100%, cuadrícula sutil):** `#4A5568` (texto/ejes) y `#E2E8F0` (grilla)

**Regla fundamental de accesibilidad:** nunca depender *únicamente* del color para diferenciar categorías. Combinar color con al menos otro diferenciador:
- **Líneas:** usar distintos estilos (`solid`, `dash`, `dot`) y marcadores distintos (`circle`, `square`, `diamond`, `triangle-up`) con `width >= 2.5` y `size >= 8`.
- **Barras:** borde limpio (`line=dict(color="white", width=1)`), ordenadas por magnitud (salvo series cronológicas) y con **etiquetas directas de valor** cuando haya ≤ 10 barras.

---

## 2. Tipografía, Ejes, Unidades y Tooltips
- **Fuente:** `Inter, Arial, sans-serif` con tamaños legibles (`título: 16–18px`, `ejes: 13–14px`, `ticks: 12px`, `leyenda: 12px`).
- **Títulos y subtítulos claros en español:** indicar el fenómeno, el grupo de entidades y el periodo (`2022–2025`), más la fuente al pie (`Fuente: SECOP II y PAA vía datos.gov.co (2022–2025)`).
- **Unidades explícitas siempre:** especificar `Miles de millones COP`, `Millones COP`, `%`, `Índice HHI (0–10.000)` o `Número de contratos`. Nunca dejar ejes con notación científica confusa (`1e11`).
- **Tooltips (`hovertemplate`) limpios:** mostrar en español la entidad, año/categoría y cifras formateadas (ej. `$124,5 mil millones`, `84,2%`), desactivando etiquetas basura de `<extra></extra>`.
- **Límites de legibilidad:** máximo 6 series simultáneas en gráficos de líneas; si hay más categorías UNSPSC, mostrar Top 8–10 + `"Otros"`.

---

## 3. Accesibilidad y Narrativa (Notebook y Streamlit)
- Toda figura en el notebook o en Streamlit debe acompañarse de **texto real** (celda Markdown o `st.caption`) con:
  1. **Hallazgo principal** en 1–2 oraciones ligado a la pregunta de investigación.
  2. **Resumen textual / tabla complementaria** (o descarga CSV en Streamlit) para usuarios que prefieran leer los datos exactos.
- **Cero gráficos superfluos (Rubro 4):** si una figura no ayuda a responder la pregunta central ni a evidenciar R1–R8 o el Rubro 5, **no se incluye**.

---

## 4. Checklist Rápido antes de Aprobar una Figura
1. ¿Se distingue correctamente en escala de grises o con daltonismo?
2. ¿Ambos ejes tienen título en español y unidades claras (sin notación científica ambigua)?
3. ¿Las barras están ordenadas con sentido lógico y los tooltips están limpios?
4. ¿Incluye periodo (`2022–2025`), fuente y texto interpretativo conectado con la pregunta?
5. ¿La función recibe un `DataFrame` y retorna `go.Figure` sin rutas absolutas ni datos quemados?
