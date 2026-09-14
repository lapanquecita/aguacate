import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots


# Paleta de colores para todas las gráficas.
PLOT_COLOR = "#1C1F1A"
PAPER_COLOR = "#262B23"
HEADER_COLOR = "#43a047"


def plot_mapa_estatal(año):
    """
    Genera un mapa y tabla con la información
    de producción de aguacate por entidad.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Filtramos por el año que nos interesa.
    df = df[df["AÑO"] == año]

    # Agrupamos por entidad.
    df = df.groupby("ENTIDAD").sum(numeric_only=True)

    # Convertimos el valor de produccion a millones de pesos.
    df["VALOR_PRODUCCION"] /= 1000000

    # Calculamos el valor logarítmico (base 10) para el volumen de producción.
    df["log"] = np.log10(df["VOLUMEN_PRODUCCION"])

    # Calculamos el total nacional.
    subtitulo = f"Nacional: <b>{df['VOLUMEN_PRODUCCION'].sum():,.0f}</b> toneladas (con un valor de <b>{df['VALOR_PRODUCCION'].sum():,.0f}</b> MDP)"

    # Ordenamos por volumen de producción de mayor a menor.
    df.sort_values("VOLUMEN_PRODUCCION", ascending=False, inplace=True)

    # Estos valores serán usados para definir la escala en el mapa.
    valor_min = df["log"].min()
    valor_max = df["log"].max()

    # Vamos a crear nuestra escala con 11 intervalos.
    marcas = np.linspace(valor_min, valor_max, 11)
    etiquetas = list()

    # Creamos los textos para las etiqutas de la escala.
    for item in marcas:
        valor_original = 10**item

        # Depende del valor del valor original será su abreviación.
        if valor_original >= 1000000:
            etiquetas.append(f"{(10**item) / 1000000:,.1f}M")
        elif valor_original >= 1000:
            etiquetas.append(f"{(10**item) / 1000:,.0f}k")
        else:
            etiquetas.append(f"{10**item:,.0f}")

    # Cargamos el archivo GeoJSON de México.
    geojson = json.loads(open("./assets/mexico.json", "r", encoding="utf-8").read())

    fig = go.Figure()

    # Vamos a crear un mapa Choropleth con todas las variables anteriormente definidas.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index,
            z=df["log"],
            featureidkey="properties.NOM_ENT",
            colorscale="Aggrnyl",
            marker_line_width=0,
            zmin=valor_min,
            zmax=valor_max,
            colorbar=dict(
                x=0.03,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=2,
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=3,
                tickcolor="#EEEEEE",
                outlinecolor="#EEEEEE",
                ticklen=10,
            ),
        )
    )

    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=[item["properties"]["CVEGEO"] for item in geojson["features"]],
            z=[1 for _ in geojson["features"]],
            featureidkey="properties.CVEGEO",
            colorscale=["hsla(0, 0%, 0%, 0)", "hsla(0, 0%, 0%, 0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=2,
            showscale=False,
        )
    )

    # Personalizamos la apariencia del mapa.
    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor="#000000",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        showlegend=False,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=80,
        margin_r=40,
        margin_b=60,
        margin_l=40,
        width=1920,
        height=1080,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.025,
                xanchor="center",
                yanchor="top",
                text=f"Producción de <b>aguacate</b> en México por entidad durante {año}",
                font_size=42,
            ),
            dict(
                x=0.0275,
                y=0.46,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Toneladas producidas durante el año (escala logarítmica)",
            ),
            dict(
                x=0.005,
                y=-0.056,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SIAP ({año})",
            ),
            dict(
                x=0.5,
                y=-0.056,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1,
                y=-0.056,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./a.png")

    # Vamos a crear dos tablas, cada una con la información de 16 entidades.
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.03,
        specs=[[{"type": "table"}, {"type": "table"}]],
    )

    fig.add_trace(
        go.Table(
            columnwidth=[120, 120, 110],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Valor (MDP)</b>",
                    "<b>Toneladas ↓</b>",
                ],
                line_color="#EEEEEE",
                fill_color=HEADER_COLOR,
                align="center",
                height=45,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[:16],
                    df["VALOR_PRODUCCION"][:16],
                    df["VOLUMEN_PRODUCCION"][:16],
                ],
                fill_color=PLOT_COLOR,
                height=45,
                format=["", ",.1f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=1,
        row=1,
    )

    fig.add_trace(
        go.Table(
            columnwidth=[120, 120, 110],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Valor (MDP)</b>",
                    "<b>Toneladas ↓</b>",
                ],
                line_color="#EEEEEE",
                fill_color=HEADER_COLOR,
                align="center",
                height=45,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[16:],
                    df["VALOR_PRODUCCION"][16:],
                    df["VOLUMEN_PRODUCCION"][16:],
                ],
                fill_color=PLOT_COLOR,
                height=45,
                format=["", ",.1f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=2,
        row=1,
    )

    fig.update_layout(
        width=1920,
        height=840,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=28,
        margin_t=25,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        paper_bgcolor=PAPER_COLOR,
    )

    fig.write_image("./b.png")

    # Unimos el mapa y las tablas en una sola imagen.
    image1 = Image.open("./a.png")
    image2 = Image.open("./b.png")

    result_width = image1.width
    result_height = image1.height + image2.height

    result = Image.new("RGB", (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, image1.height))

    result.save(f"./entidades_{año}.png")

    # Borramos las imágenes originales.
    os.remove("./a.png")
    os.remove("./b.png")


def plot_mapa_municipal(año):
    """
    Genera un mapa municipal con la
    información de producción de aguacate.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Filtramos por el año que nos interesa.
    df = df[df["AÑO"] == año]

    # Convertimos los ID's de estado y municipio a strings para poder unirlos.
    df["CVE_ENT"] = df["CVE_ENT"].astype(str).str.zfill(2)
    df["CVE_MUN"] = df["CVE_MUN"].astype(str).str.zfill(3)

    # Creamos la clave única de cada municipio.
    df["CVE"] = df["CVE_ENT"] + df["CVE_MUN"]

    # Agrupamos por clave 'única de municipio.
    df = df.groupby("CVE").sum(numeric_only=True)

    # Eliminamos municipios sin producción.
    df = df[df["VOLUMEN_PRODUCCION"] != 0]

    # Calculamos el valor logarítmico (base 10).
    df["log"] = np.log10(df["VOLUMEN_PRODUCCION"])

    # Calculamos los valores para nuestro subtítulo.
    subtitulo = f"Nacional: <b>{df['VOLUMEN_PRODUCCION'].sum():,.0f}</b> toneladas (con un valor de: <b>{df['VALOR_PRODUCCION'].sum() / 1000000:,.0f}</b> millones de pesos)"

    # Calculamos algunas estadísticas descriptivas.
    estadisticas = [
        "Estadísticas descriptivas",
        "<b>(toneladas producidas)</b>",
        f"Media: <b>{df['VOLUMEN_PRODUCCION'].mean():,.1f}</b>",
        f"Mediana: <b>{df['VOLUMEN_PRODUCCION'].median():,.1f}</b>",
        f"DE: <b>{df['VOLUMEN_PRODUCCION'].std():,.1f}</b>",
        f"25%: <b>{df['VOLUMEN_PRODUCCION'].quantile(0.25):,.1f}</b>",
        f"75%: <b>{df['VOLUMEN_PRODUCCION'].quantile(0.75):,.1f}</b>",
        f"95%: <b>{df['VOLUMEN_PRODUCCION'].quantile(0.95):,.1f}</b>",
        f"Máximo: <b>{df['VOLUMEN_PRODUCCION'].max():,.1f}</b>",
    ]
    estadisticas = "<br>".join(estadisticas)

    # Estos valores serán usados para definir la escala en el mapa.
    min_val = df["log"].min()
    max_val = df["log"].max()

    # Vamos a crear nuestra escala con 11 intervalos.
    marcas = np.linspace(min_val, max_val, 11)
    etiquetas = list()

    # Creamos los textos para las etiqutas de la escala.
    for item in marcas:
        valor_original = 10**item

        # Depende del valor del valor original será su abreviación.
        if valor_original >= 1000000:
            etiquetas.append(f"{(10**item) / 1000000:,.1f}M")
        elif valor_original >= 1000:
            etiquetas.append(f"{(10**item) / 1000:,.0f}k")
        else:
            etiquetas.append(f"{10**item:,.0f}")

    # Cargamos el GeoJSON de municipios de México.
    geojson = json.loads(open("./assets/municipios.json", "r", encoding="utf-8").read())

    fig = go.Figure()

    # Configuramos nuestro mapa Choropleth con todas las variables antes definidas.
    # El parámetro 'featureidkey' debe coincidir con el de la variable 'geo' que
    # extrajimos en un paso anterior.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=df.index,
            z=df["log"],
            featureidkey="properties.CVEGEO",
            colorscale="Aggrnyl",
            marker_line_color="#FFFFFF",
            marker_line_width=1,
            zmin=min_val,
            zmax=max_val,
            colorbar=dict(
                x=0.035,
                y=0.5,
                thickness=150,
                ypad=400,
                ticks="outside",
                outlinewidth=5,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=5,
                tickcolor="#FFFFFF",
                ticklen=30,
                tickfont_size=80,
            ),
        )
    )

    # Vamos a sobreponer otro mapa Choropleth, el cual
    # tiene el único propósito de mostrar la división política
    # de las entidades federativas.

    # Cargamos el archivo GeoJSON de México.
    geo_borde = json.loads(open("./assets/mexico.json", "r", encoding="utf-8").read())

    # Este mapa tiene mucho menos personalización.
    # Lo único que necesitamos es que muestre los contornos
    # de cada entidad.
    fig.add_traces(
        go.Choropleth(
            geojson=geo_borde,
            locations=[item["properties"]["CVEGEO"] for item in geojson["features"]],
            z=[1 for _ in geo_borde["features"]],
            featureidkey="properties.CVEGEO",
            colorscale=["hsla(0, 0%, 0%, 0)", "hsla(0, 0%, 0%, 0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=4,
            showscale=False,
        )
    )

    # Personalizamos algunos aspectos del mapa, como el color del oceáno
    # y el del terreno.
    fig.update_geos(
        fitbounds="geojson",
        showocean=True,
        oceancolor="#000000",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#000000",
    )

    # Agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=False,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=120,
        margin_t=50,
        margin_r=100,
        margin_b=30,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=0.985,
                xanchor="center",
                yanchor="top",
                text=f"Toneladas producidas de <b>aguacate</b> en México por municipio durante {año}",
                font_size=140,
            ),
            dict(
                x=0.02,
                y=0.49,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Toneladas producidas durante el año (escala logarítmica)",
                font_size=100,
            ),
            dict(
                x=0.98,
                y=0.9,
                xanchor="right",
                yanchor="top",
                text=estadisticas,
                align="left",
                borderpad=30,
                bordercolor="#FFFFFF",
                bgcolor="#000000",
                borderwidth=5,
            ),
            dict(
                x=0.001,
                y=-0.003,
                xanchor="left",
                yanchor="bottom",
                text=f"Fuente: SIAP ({año})",
            ),
            dict(
                x=0.5,
                y=-0.003,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
            ),
            dict(
                x=1.0,
                y=-0.003,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./municipios_{año}.png")


def mapa_exportaciones_volumen(año):
    """
    Genera un mapa coroplético con la distribución
    de destinos de exportación de aguacate por volumen.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de exportaciones del INEGI.
    df = pd.read_csv("./data/inegi_exportaciones.csv")

    # Filtramos por el año que nos interesa.
    df = df[df["ANIO"] == año]

    # Seleccionamos solamete las exportaciones.
    df = df[df["TIPO"] == "Exportaciones"]

    # Quitamos registros sin volumen.
    df = df[~pd.isna(df["CANTIDAD"])]

    # Convertimos kilogramos a toneladas.
    df["CANTIDAD"] /= 1000

    # Agrupamos por páis de destino usando el valor más alto.
    # En ocasiones las cifras reales no están en la categoría principal
    # sino en las subcategorías.
    df = df.groupby("PAIS_O_D").max(numeric_only=True)

    # Extraemos totales para el subtítulo.
    volumen_total = df["CANTIDAD"].max()
    valor_total = df["VAL_MNX"].max()

    # Calculamos el valor logarítmico (base 10) para el volumen de exportación.
    df["log"] = np.log10(df["CANTIDAD"])

    # Escogemos los valores del total para formar el subtítulo.
    subtitulo = f"Total: <b>{volumen_total:,.0f}</b> toneladas con un valor de <b>{valor_total / 1000000:,.0f}</b> mdp"

    # Creamos la escala logarítmica usando el valor máximo y mínimo en nuestro DataFrame.
    valor_min = df["log"].min()
    valor_max = df["log"].max()

    # Creamos las marcas para la escala.
    marcas = np.arange(np.floor(valor_min), np.ceil(valor_max))

    textos = list()

    # Convertiremos los textos a base 10.
    for item in marcas:
        v, e = f"{10**item:e}".split("e")
        textos.append(f"{10 * float(v):.0f}<sup>{int(e)}</sup>")

    fig = go.Figure()

    fig.add_traces(
        go.Choropleth(
            locations=df.index,
            z=df["log"],
            colorscale="geyser_r",
            marker_line_color="#FFFFFF",
            showscale=True,
            showlegend=False,
            marker_line_width=2,
            zmax=valor_max,
            zmin=valor_min,
            colorbar=dict(
                x=0.03,
                y=0.42,
                thickness=150,
                ypad=840,
                ticks="outside",
                outlinewidth=5,
                outlinecolor="#FFFFFF",
                tickwidth=5,
                tickcolor="#FFFFFF",
                ticklen=30,
                tickfont_size=80,
                tickvals=marcas,
                ticktext=textos,
            ),
        )
    )

    fig.update_geos(
        fitbounds=False,
        showocean=True,
        oceancolor="#000000",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        font_size=120,
        font_family="Inter",
        font_color="#FFFFFF",
        margin_t=240,
        margin_r=100,
        margin_b=0,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.04,
                xanchor="center",
                yanchor="top",
                text=f"Destinos de exportación de <b>aguacate mexicano</b> durante {año}",
                font_size=140,
            ),
            dict(
                x=0.02,
                y=0.25,
                textangle=270,
                xanchor="left",
                yanchor="middle",
                text="Toneladas (escala logarítmica)",
                font_size=90,
            ),
            dict(
                x=0.001,
                y=-0.065,
                xanchor="left",
                yanchor="bottom",
                text=f"Fuente: INEGI (BCMM, {año})",
            ),
            dict(
                x=0.5,
                y=0.05,
                xanchor="center",
                yanchor="bottom",
                bgcolor=PLOT_COLOR,
                bordercolor="#FFFFFF",
                borderwidth=4,
                borderpad=7,
                text=f" <b>Nota:</b> Se identificaron <b>{len(df)}</b> destinos de exportación con información disponible. ",
            ),
            dict(
                x=0.5,
                y=-0.065,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
            ),
            dict(
                x=1.0,
                y=-0.065,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./exportaciones_volumen_{año}.png")


def mapa_exportaciones_valor(año):
    """
    Genera un mapa coroplético con la distribución
    de destinos de exportación de aguacate por monto.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de exportaciones de la Secretaría de Economía.
    df = pd.read_csv("./data/se_exportaciones.csv")

    # Filtramos por el año que nos interesa.
    df = df[df["Year"] == año]

    # Seleccionamos solamete las exportaciones.
    df = df[df["Flow"] == "Exportaciones"]

    # Agrupamos por país.
    df = df.groupby("País / Región ID").sum(numeric_only=True)

    # Calculamos el monto total.
    valor_total = df["Trade Value"].sum()

    # Calculamos el valor logarítmico (base 10) para el volumen de exportación.
    df["log"] = np.log10(df["Trade Value"])

    # Preparamos el subtítulo.
    subtitulo = f"Total: <b>{valor_total / 1000000:,.0f}</b> millones de dólares"

    # Creamos la escala logarítmica usando el valor máximo y mínimo en nuestro DataFrame.
    valor_min = df["log"].min()
    valor_max = df["log"].max()

    # Creamos las marcas para la escala.
    marcas = np.arange(np.floor(valor_min), np.ceil(valor_max))

    textos = list()

    # Convertiremos los textos a base 10.
    for item in marcas:
        v, e = f"{10**item:e}".split("e")
        textos.append(f"{10 * float(v):.0f}<sup>{int(e)}</sup>")

    fig = go.Figure()

    fig.add_traces(
        go.Choropleth(
            locations=df.index.str.upper(),
            z=df["log"],
            colorscale="geyser_r",
            marker_line_color="#FFFFFF",
            showscale=True,
            showlegend=False,
            marker_line_width=2,
            zmax=valor_max,
            zmin=valor_min,
            colorbar=dict(
                x=0.03,
                y=0.42,
                thickness=150,
                ypad=840,
                ticks="outside",
                outlinewidth=5,
                outlinecolor="#FFFFFF",
                tickwidth=5,
                tickcolor="#FFFFFF",
                ticklen=30,
                tickfont_size=80,
                tickvals=marcas,
                ticktext=textos,
            ),
        )
    )

    fig.update_geos(
        fitbounds=False,
        showocean=True,
        oceancolor="#000000",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        font_size=120,
        font_family="Inter",
        font_color="#FFFFFF",
        margin_t=240,
        margin_r=100,
        margin_b=0,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.04,
                xanchor="center",
                yanchor="top",
                text=f"Destinos de exportación de <b>aguacate mexicano</b> durante {año}",
                font_size=140,
            ),
            dict(
                x=0.02,
                y=0.25,
                textangle=270,
                xanchor="left",
                yanchor="middle",
                text="Dólares (escala logarítmica)",
                font_size=90,
            ),
            dict(
                x=0.001,
                y=-0.065,
                xanchor="left",
                yanchor="bottom",
                text=f"Fuente: SE (BCMM, {año})",
            ),
            dict(
                x=0.5,
                y=0.05,
                xanchor="center",
                yanchor="bottom",
                bgcolor=PLOT_COLOR,
                bordercolor="#FFFFFF",
                borderwidth=4,
                borderpad=7,
                text=f" <b>Nota:</b> Se identificaron <b>{len(df)}</b> destinos de exportación con información disponible. ",
            ),
            dict(
                x=0.5,
                y=-0.065,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
            ),
            dict(
                x=1.0,
                y=-0.065,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./exportaciones_valor_{año}.png")


def tabla_volumen(año):
    """
    Genera una tabla con los 30 municipios
    con mayor produccion de aguacate.

    Parameters
    ----------
    año : int
        El año que se desea analizar.

    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Seleccionamos los registros del año especificado.
    df = df[df["AÑO"] == año]

    # Unimos nombre de municipio y entidad.
    df["CVE"] = df["MUNICIPIO"] + ", " + df["ENTIDAD"]

    # Calculamos el total por municipio.
    df = df.groupby("CVE").sum(numeric_only=True)

    # Calculamos el porcentaje de cada municipio.
    df["porcentaje"] = df["VOLUMEN_PRODUCCION"] / df["VOLUMEN_PRODUCCION"].sum() * 100

    # Calculamos el total nacional.
    subtitulo = f"Nacional: <b>{df['VOLUMEN_PRODUCCION'].sum():,.0f}</b> toneladas"

    # Ordenamos por mayor a menor volumen.
    df.sort_values("porcentaje", ascending=False, inplace=True)

    # Seleccionamos las primeras 30 filas.
    df = df.head(30)

    # Para el rank resetearemos el índice y le sumaremos 1, para que sea del 1 al 30 en vez del 0 al 29.
    df.reset_index(inplace=True)
    df.index += 1

    fig = go.Figure()

    # Vamos a crear una tabla con 4 columnas.
    fig.add_trace(
        go.Table(
            columnwidth=[40, 200, 110, 90],
            header=dict(
                values=[
                    "<b>Pos.</b>",
                    "<b>Municipio, Entidad</b>",
                    "<b>Toneladas producidas</b>",
                    "<b>% del total</b>",
                ],
                font_color="#FFFFFF",
                line_width=1,
                fill_color=HEADER_COLOR,
                align="center",
                height=43,
            ),
            cells=dict(
                values=[
                    df.index,
                    df["CVE"],
                    df["VOLUMEN_PRODUCCION"],
                    df["porcentaje"],
                ],
                line_width=1,
                fill_color=PLOT_COLOR,
                height=43,
                suffix=["", "", "", "%"],
                format=["", "", ",.0f", ",.2f"],
                align=["center", "left", "center"],
            ),
        )
    )

    fig.update_layout(
        width=1280,
        height=1600,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=25,
        margin_t=180,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_x=0.5,
        title_y=0.95,
        title_font_size=40,
        title_text=f"Los 30 municipios de México con la mayor producción<br>de <b>aguacate</b> durante {año}",
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.015,
                y=0.02,
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SIAP ({año})",
            ),
            dict(
                x=0.57,
                y=0.02,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
            ),
            dict(
                x=1.01,
                y=0.02,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./tabla_{año}.png")


if __name__ == "__main__":
    plot_mapa_estatal(2005)
    plot_mapa_estatal(2025)

    plot_mapa_municipal(2005)
    plot_mapa_municipal(2025)

    tabla_volumen(2005)
    tabla_volumen(2025)

    mapa_exportaciones_volumen(2005)
    mapa_exportaciones_volumen(2025)

    mapa_exportaciones_valor(2006)
    mapa_exportaciones_valor(2025)
