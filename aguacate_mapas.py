"""
Este script contiene funciones para crear mapas con la información
de la producción y exportación de aguacate desde México.
"""

import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from plotly.subplots import make_subplots


PAPER_BGCOLOR = "#31363F"
PLOT_BGCOLOR = "#222831"


def plot_mapa_estatal(año):
    """
    Esta función crea un mapa y unas tablas con la información de producción
    de aguacate por entidad.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Filtramos por el año que nos interesa.
    df = df[df["Anio"] == año]

    # Agrupamos por entidad.
    df = df.groupby("Nomestado").sum(numeric_only=True)

    # Convertimos el valor de produccion a millones de pesos.
    df["Valorproduccion"] /= 1000000

    # Calculamos el valor logarítmico (base 10).
    df["log"] = np.log10(df["Volumenproduccion"])

    # Renombramos el Estado de México.
    df.index = df.index.map(lambda x: "Estado de México" if x == "México" else x)

    # Calculamos el total nacional.
    subtitulo = f"Nacional: {df['Volumenproduccion'].sum():,.0f} toneladas ({df['Valorproduccion'].sum():,.0f} MDP)"

    # Ordenamos por volumen de producción de mayor a menor.
    df = df.sort_values("Volumenproduccion", ascending=False)

    # Estas listas nos serviran para alimentar el mapa.
    ubicaciones = list()
    valores = list()

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
            etiquetas.append(f"{(10 ** item)/1000000:,.1f}M")
        elif valor_original >= 1000:
            etiquetas.append(f"{(10 ** item) / 1000:,.0f}k")
        else:
            etiquetas.append(f"{10 ** item:,.0f}")

    # Cargamos el archivo GeoJSON de México.
    geojson = json.loads(open("./assets/mexico.json", "r", encoding="utf-8").read())

    # Iteramos sobre cada entidad dentro de nuestro archivo GeoJSON de México.
    for item in geojson["features"]:
        geo = item["properties"]["NOMGEO"]

        # Alimentamos las listas creadas anteriormente con la ubicación y su valor per capita.
        ubicaciones.append(geo)

        # Si no hay valor, lo dejamos como nulo.
        try:
            valores.append(df.loc[geo, "log"])
        except Exception as _:
            valores.append(None)

    fig = go.Figure()

    # Vamos a crear un mapa Choropleth con todas las variables anteriormente definidas.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=ubicaciones,
            z=valores,
            featureidkey="properties.NOMGEO",
            colorscale="Aggrnyl_r",
            reversescale=True,
            marker_line_color="#FFFFFF",
            marker_line_width=1.0,
            zmin=min_val,
            zmax=max_val,
            colorbar=dict(
                x=0.03,
                y=0.5,
                ypad=50,
                ticks="outside",
                outlinewidth=1.5,
                outlinecolor="#FFFFFF",
                tickvals=marcas,
                ticktext=etiquetas,
                tickwidth=2,
                tickcolor="#FFFFFF",
                ticklen=10,
                tickfont_size=20,
            ),
        )
    )

    # Personalizamos la apariencia del mapa.
    fig.update_geos(
        fitbounds="locations",
        showocean=True,
        oceancolor=PLOT_BGCOLOR,
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=2,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        legend_x=0.01,
        legend_y=0.07,
        legend_bgcolor="#111111",
        legend_font_size=20,
        legend_bordercolor="#FFFFFF",
        legend_borderwidth=2,
        font_family="Lato",
        font_color="#FFFFFF",
        margin={"r": 40, "t": 50, "l": 40, "b": 30},
        width=1280,
        height=720,
        paper_bgcolor=PAPER_BGCOLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.01,
                xanchor="center",
                yanchor="top",
                text=f"Producción de <b>aguacate</b> en México por entidad durante el {año}",
                font_size=28,
            ),
            dict(
                x=0.52,
                y=-0.04,
                xanchor="center",
                yanchor="top",
                text=subtitulo,
                font_size=26,
            ),
            dict(
                x=0.0275,
                y=0.45,
                textangle=-90,
                xanchor="center",
                yanchor="middle",
                text="Toneladas producidas durante el año (escala logarítmica)",
                font_size=18,
            ),
            dict(
                x=0.01,
                y=-0.04,
                xanchor="left",
                yanchor="top",
                text="Fuente: SIAP (2024)",
                font_size=24,
            ),
            dict(
                x=1.01,
                y=-0.04,
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
                font_size=24,
            ),
        ],
    )

    fig.write_image("./0.png")

    # Vamos a crear dos tablas, cada una con la información de 16 entidades.
    fig = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.03,
        specs=[[{"type": "table"}, {"type": "table"}]],
    )

    fig.add_trace(
        go.Table(
            columnwidth=[145, 160],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Valor en MDP</b>",
                    "<b>Toneladas ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color="#e65100",
                align="center",
                height=29,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[:16],
                    df["Valorproduccion"][:16],
                    df["Volumenproduccion"][:16],
                ],
                fill_color=PLOT_BGCOLOR,
                height=29,
                format=["", ",.2f", ",.1f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=1,
        row=1,
    )

    fig.add_trace(
        go.Table(
            columnwidth=[145, 160],
            header=dict(
                values=[
                    "<b>Entidad</b>",
                    "<b>Valor en MDP</b>",
                    "<b>Toneladas ↓</b>",
                ],
                font_color="#FFFFFF",
                fill_color="#e65100",
                align="center",
                height=29,
                line_width=0.8,
            ),
            cells=dict(
                values=[
                    df.index[16:],
                    df["Valorproduccion"][16:],
                    df["Volumenproduccion"][16:],
                ],
                fill_color=PLOT_BGCOLOR,
                height=29,
                format=["", ",.2f", ",.1f"],
                line_width=0.8,
                align=["left", "center"],
            ),
        ),
        col=2,
        row=1,
    )

    fig.update_layout(
        showlegend=False,
        legend_borderwidth=1.5,
        xaxis_rangeslider_visible=False,
        width=1280,
        height=560,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title="",
        title_x=0.5,
        title_y=0.95,
        margin_t=20,
        margin_l=40,
        margin_r=40,
        margin_b=0,
        title_font_size=26,
        paper_bgcolor=PAPER_BGCOLOR,
    )

    fig.write_image("./1.png")

    # Unimos el mapa y las tablas en una sola imagen.
    image1 = Image.open("./0.png")
    image2 = Image.open("./1.png")

    result_width = 1280
    result_height = image1.height + image2.height

    result = Image.new("RGB", (result_width, result_height))
    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, image1.height))

    result.save(f"./entidades_{año}.png")

    # Borramos las imágenes originales.
    os.remove("./0.png")
    os.remove("./1.png")


def plot_mapa_municipal(año):
    """
    Esta función crea un mapa municipal con la información de producción de aguacate.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Filtramos por el año que nos interesa.
    df = df[df["Anio"] == año]

    # Convertimos los ID's de estado y municipio a strings para poder unirlos.
    df["Idestado"] = df["Idestado"].astype(str).str.zfill(2)
    df["Idmunicipio"] = df["Idmunicipio"].astype(str).str.zfill(3)

    # Creamos la clave única de cada municipio.
    df["CVE"] = df["Idestado"] + df["Idmunicipio"]

    # Agrupamos por clave 'única de municipio.
    df = df.groupby("CVE").sum(numeric_only=True)

    # Eliminamos municipios sin producción.
    df = df[df["Volumenproduccion"] != 0]

    # Calculamos el valor logarítmico (base 10).
    df["log"] = np.log10(df["Volumenproduccion"])

    # Calculamos los valores para nuestro subtítulo.
    subtitulo = f"Nacional: <b>{df['Volumenproduccion'].sum():,.0f}</b> toneladas (con un valor de: <b>{df['Valorproduccion'].sum() / 1000000:,.0f}</b> millones de pesos)"

    # Calculamos algunas estadísticas descriptivas.
    estadisticas = [
        "Estadísticas descriptivas",
        f"Media: <b>{df['Volumenproduccion'].mean():,.1f}</b>",
        f"Mediana: <b>{df['Volumenproduccion'].median():,.1f}</b>",
        f"DE: <b>{df['Volumenproduccion'].std():,.1f}</b>",
        f"25%: <b>{df['Volumenproduccion'].quantile(.25):,.1f}</b>",
        f"75%: <b>{df['Volumenproduccion'].quantile(.75):,.1f}</b>",
        f"95%: <b>{df['Volumenproduccion'].quantile(.95):,.1f}</b>",
        f"Máximo: <b>{df['Volumenproduccion'].max():,.1f}</b>",
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
            etiquetas.append(f"{(10 ** item)/1000000:,.1f}M")
        elif valor_original >= 1000:
            etiquetas.append(f"{(10 ** item) / 1000:,.0f}k")
        else:
            etiquetas.append(f"{10 ** item:,.0f}")

    # Cargamos el GeoJSON de municipios de México.
    geojson = json.loads(open("./assets/mexico2023.json", "r", encoding="utf-8").read())

    # Estas listas serán usadas para configurar el mapa Choropleth.
    ubicaciones = list()
    valores = list()

    # Iteramos sobre cada municipio e nuestro GeoJSON.
    for item in geojson["features"]:
        geo = str(item["properties"]["CVEGEO"])

        ubicaciones.append(geo)

        # Si el municipio no se encuentra en nuestro DataFrame,
        # agregamos un valor nulo.
        try:
            valores.append(df.loc[geo]["log"])
        except Exception as _:
            valores.append(None)

    fig = go.Figure()

    # Configuramos nuestro mapa Choropleth con todas las variables antes definidas.
    # El parámetro 'featureidkey' debe coincidir con el de la variable 'geo' que
    # extrajimos en un paso anterior.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson,
            locations=ubicaciones,
            z=valores,
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
    geojson_borde = json.loads(
        open("./assets/mexico.json", "r", encoding="utf-8").read()
    )

    # Estas listas serán usadas para configurar el mapa Choropleth.
    ubicaciones_borde = list()
    valores_borde = list()

    # Iteramos sobre cada entidad dentro de nuestro archivo GeoJSON de México.
    for item in geojson_borde["features"]:
        geo = item["properties"]["NOMGEO"]

        # Alimentamos las listas creadas anteriormente con la ubicación y su valor per capita.
        ubicaciones_borde.append(geo)
        valores_borde.append(1)

    # Este mapa tiene mucho menos personalización.
    # Lo único que necesitamos es que muestre los contornos
    # de cada entidad.
    fig.add_traces(
        go.Choropleth(
            geojson=geojson_borde,
            locations=ubicaciones_borde,
            z=valores_borde,
            featureidkey="properties.NOMGEO",
            colorscale=["hsla(0, 0, 0, 0)", "hsla(0, 0, 0, 0)"],
            marker_line_color="#FFFFFF",
            marker_line_width=4.0,
            showscale=False,
        )
    )

    # Personalizamos algunos aspectos del mapa, como el color del oceáno
    # y el del terreno.
    fig.update_geos(
        fitbounds="locations",
        showocean=True,
        oceancolor="#092635",
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
        font_family="Lato",
        font_color="#FFFFFF",
        margin_t=50,
        margin_r=100,
        margin_b=30,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor=PAPER_BGCOLOR,
        annotations=[
            dict(
                x=0.5,
                y=0.985,
                xanchor="center",
                yanchor="top",
                text=f"Toneladas producidas de <b>aguacate</b> en México por municipio durante el {año}",
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
                font_size=120,
            ),
            dict(
                x=0.001,
                y=-0.003,
                xanchor="left",
                yanchor="bottom",
                text="Fuente: SIAP (2024)",
                font_size=120,
            ),
            dict(
                x=0.5,
                y=-0.003,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
                font_size=120,
            ),
            dict(
                x=1.0,
                y=-0.003,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
                font_size=120,
            ),
        ],
    )

    fig.write_image(f"./municipios_{año}.png")


def mapa_exportaciones(año):
    """
    Esta función crea un mapa binario con las ubicaciones donde se ha exportado aguacate.

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

    # En el dataset, los totales no tienen código de país. Le aisgnaremos uno.
    df["PAIS_O_D"] = df["PAIS_O_D"].fillna("TOTAL")

    # Agrupamos por páis de destino usando el valor más alto.
    # En ocasiones las cifras reales no están en la categoría principal
    # sino en las subcategorías.
    df = df.groupby("PAIS_O_D").max(numeric_only=True)

    # Asignamos un valor dummy para nuestro mapa binario.
    df["valor"] = 1

    # Escogemos los valores del total para formar el subtítulo.
    subtitulo = f"Total: {df.loc['TOTAL', 'CANTIDAD']/1000:,.0f} toneladas con un valor de {df.loc['TOTAL', 'VAL_MNX']:,.0f} pesos"

    fig = go.Figure()

    # Creamos un sencillo mapa choropleth con solo dos colores y dos valores.
    fig.add_traces(
        go.Choropleth(
            locations=df.index,
            z=df["valor"],
            colorscale=["hsla(88, 50%, 60%, 0)", "hsla(88, 50%, 60%, 1.0)"],
            marker_line_color="#FFFFFF",
            showscale=False,
            showlegend=False,
            marker_line_width=2,
            zmax=1,
            zmin=0,
        )
    )

    fig.update_geos(
        showocean=True,
        oceancolor="#082032",
        showcountries=False,
        framecolor="#FFFFFF",
        framewidth=5,
        showlakes=False,
        coastlinewidth=0,
        landcolor="#1C0A00",
    )

    fig.update_layout(
        legend_bgcolor="#111111",
        legend_font_size=100,
        legend_bordercolor="#FFFFFF",
        legend_borderwidth=2,
        font_family="Lato",
        font_color="#FFFFFF",
        margin_t=120,
        margin_r=100,
        margin_b=0,
        margin_l=100,
        width=7680,
        height=4320,
        paper_bgcolor=PAPER_BGCOLOR,
        annotations=[
            dict(
                x=0.5,
                y=1.0,
                xanchor="center",
                yanchor="top",
                text=f"Destino de las exportaciones de <b>aguacate</b> desde México durante el {año}",
                font_size=160,
            ),
            dict(
                x=0.0,
                y=0.004,
                xanchor="left",
                yanchor="bottom",
                text="Fuente: INEGI (2024)",
                font_size=100,
            ),
            dict(
                x=0.5,
                y=0.004,
                xanchor="center",
                yanchor="bottom",
                text=subtitulo,
                font_size=100,
            ),
            dict(
                x=1.0,
                y=0.004,
                xanchor="right",
                yanchor="bottom",
                text="🧁 @lapanquecita",
                font_size=100,
            ),
        ],
    )

    fig.write_image(f"./exportaciones_{año}.png")


if __name__ == "__main__":
    plot_mapa_estatal(2004)
    plot_mapa_estatal(2023)

    plot_mapa_municipal(2004)
    plot_mapa_municipal(2023)

    mapa_exportaciones(2004)
    mapa_exportaciones(2023)
