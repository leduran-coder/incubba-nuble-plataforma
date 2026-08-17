# Incubba Ñuble UBB · Plataforma de Postulación y Evaluación (Generación 2026)

Plataforma web (Streamlit + base de datos propia) para importar, evaluar y
analizar las postulaciones al programa de incubación Incubba Ñuble UBB,
siguiendo exactamente las rúbricas de las bases del concurso, más una
bonificación configurable por "potencial dinámico".

**¿Primera vez? Lee `docs/Guia_de_despliegue_Incubba_Nuble.docx`** — guía paso
a paso para publicar esta plataforma gratis, sin necesitar conocimientos de
programación.

## Estructura del proyecto

- `app.py` — página principal (login).
- `pages/` — Postulaciones, Evaluación, Resultados, Estadísticas, Configuración.
- `config/rubric.py` — **única fuente de verdad** de las rúbricas y pesos de las bases.
- `config/theme.py` — colores e identidad visual (muestreados de las bases oficiales).
- `db/` — modelos (SQLAlchemy) y conexión a la base de datos.
- `utils/importer.py` — importación flexible de CSV exportado desde Google Forms.
- `utils/scoring.py` — motor de cálculo de puntajes y bonificación.
- `utils/charts.py` — gráficos con paleta validada contra daltonismo/contraste.
- `sample_data/` — datos ficticios para practicar sin usar información real.
- `tests/smoke_test.py` — prueba de extremo a extremo del motor de datos/rúbrica.

## Correr localmente (para quien sepa un poco de Python)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Sin configurar nada más, usa una base de datos SQLite local en `./data/incubba.db`.
Para producción, define la variable de entorno `DATABASE_URL` (o un secreto de
Streamlit Cloud) apuntando a una base de datos Postgres (ver la guía de despliegue).

Usuario administrador de fábrica: `admin@incubba.cl` / `incubba2026` (cámbiala
apenas ingreses).
