"""
Este script genera gráficas para el análisis del aguacate en México.
"""

from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go


PAPER_BGCOLOR = "#31363F"
PLOT_BGCOLOR = "#222831"


def comparacion_pib(campo, titulo, archivo):
    """
    Esta función compara el valor de la producción de aguacate
     con diversos componentes del PIB de México.

    Parameters
    ==========
    titulo : str
        El texto complementario para el título.

    campo : str
        El campo que se desea comparar.

    archivo : str
        El nombre que tendra el archivo generado.

    """

    # Cargamos el dataset del PIB nominal (corriente).
    pib = pd.read_csv("./assets/PIB_corriente.csv", parse_dates=["Fecha"], index_col=0)
    pib = pib.resample("YS").sum() / 4
    pib.index = pib.index.year

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Calculamos el valor de la producción anual.
    df = df.groupby("Anio").sum(numeric_only=True)[["Valorproduccion"]]

    # Agregamos la columna del PIB. Le quitamos los puntos decimales.
    df["pib"] = pib[campo] * 1000000

    # Calculamos el porcentaje respecto al PIB.
    df["perc"] = df["Valorproduccion"] / df["pib"] * 100

    # Calculamos el cambio orcentual.
    df["change"] = df["perc"].pct_change() * 100

    # Definimos los colores para crecimiento y reduciión.
    df["color"] = df["change"].apply(
        lambda x: "hsl(34, 100%, 20%)" if x < 0 else "hsl(93, 100%, 20%)"
    )

    df["bar_color"] = df["change"].apply(
        lambda x: "hsl(34, 100%, 65%)" if x < 0 else "hsl(93, 100%, 65%)"
    )

    # Escogemos los últimos 20 años.
    df = df.tail(20)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["perc"],
            text=df["perc"],
            marker_color=df["bar_color"],
            width=0.04,
            marker_line_width=0,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["perc"],
            mode="markers",
            marker_color=df["color"],
            marker_line_color=df["bar_color"],
            marker_line_width=2,
            marker_size=50,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["perc"] * 0.992,
            text=df["perc"],
            texttemplate="%{text:,.3f}",
            mode="text",
            textposition="middle center",
            textfont_family="Oswald",
            textfont_size=18,
        )
    )

    fig.update_xaxes(
        range=[df.index.min() - 0.6, df.index.max() + 0.6],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=False,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        range=[0, df["perc"].max() * 1.1],
        title=f"Porcentaje respecto {titulo}",
        ticksuffix="%",
        ticks="outside",
        separatethousands=True,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Valor de la producción de <b>aguacate</b> en México en relación {titulo} ({df.index[0]}-{df.index[-1]})",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_l=100,
        margin_r=40,
        margin_b=90,
        title_font_size=24,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuentes: INEGI y SIAP (2024)",
            ),
            dict(
                x=0.5,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./pib_{archivo}.png")


def top_exportaciones(año, textos_adentro):
    """
    Esta función crea una gráfica de barras con los países que más reciben aguacate desde México.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    textos_adentro : int
        El número de textos que irán adentro de las barras.

    """

    # Cargamos el catálogo de países.
    paises = pd.read_csv("./assets/paises.csv", index_col=0)

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

    # Asignamos el nombre de cada país.
    df["nombre"] = paises["nombre"]

    # Ordenamos por cantidad de kilogramos enviados.
    df.sort_values("CANTIDAD", ascending=False, inplace=True)

    # Calculamos el porcentaje enviado a cada país.
    df["perc"] = df["CANTIDAD"] / df.loc["TOTAL", "CANTIDAD"] * 100

    # Convertimos de kilogramos a toneladas.
    df["CANTIDAD"] /= 1000

    # Eescogemos solo el top 15.
    # Ignoramos la primera file, la cual es el total.
    df = df.iloc[1:16]

    # Los nombres largos los partimos en dos.
    df["nombre"] = df["nombre"].str.wrap(15).str.replace("\n", "<br>")

    # Creamos el texto para cada barra.
    df["texto"] = df.apply(
        lambda x: f" {x['CANTIDAD']:,.0f} ({x['perc']:,.2f}%) ", axis=1
    )

    # Creamos las posiciones de los textos.
    posiciones = ["outside" for _ in range(len(df))]

    for i in range(textos_adentro):
        posiciones[i] = "inside"

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["CANTIDAD"],
            y=df["nombre"],
            text=df["texto"],
            orientation="h",
            textposition=posiciones,
            marker_color="#e65100",
            marker_line_width=0,
            textfont_family="Oswald",
            textfont_color="#FFFFFF",
        )
    )

    # Para el eje horizontal usamos escala logarítmica debido
    # a la gran diferencia entre valores.
    fig.update_xaxes(
        exponentformat="SI",
        separatethousands=True,
        type="log",
        range=[
            np.log10(df["CANTIDAD"].min()) // 1,
            np.log10(df["CANTIDAD"].max() * 1.1),
        ],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=20,
    )

    fig.update_yaxes(
        autorange="reversed",
        ticks="outside",
        tickfont_size=16,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        showgrid=False,
        gridwidth=0.5,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Los 15 países que más importaron <b>aguacate</b> desde México durante el {año}",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_l=150,
        margin_r=40,
        margin_b=90,
        title_font_size=24,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: INEGI (2024)",
            ),
            dict(
                x=0.5,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Toneladas enviadas (porcentaje del total)",
            ),
            dict(
                x=1.01,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./top_exports_{año}.png")


def composicion_produccion():
    """
    Esta función muestra la evolución de la producción de aguacate en México por año.
    Se separa por tipo de mercado: local y exportación.
    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Agrupamos por año.
    df = df.groupby("Anio").sum(numeric_only=True)

    # Cargamos el dataset de exportaciones del INEGI.
    exportacioes = pd.read_csv("./data/inegi_exportaciones.csv")

    # Seleccionamos solamente las exportaciones.
    exportacioes = exportacioes[exportacioes["TIPO"] == "Exportaciones"]

    # Agrupamos por año, seleccionando el vaor máximo.
    exportacioes = exportacioes.groupby("ANIO").max(numeric_only=True)

    # Agregamos las toneldas de exportación.
    df["exportaciones"] = exportacioes["CANTIDAD"] / 1000

    # Calculamos el consumo local.
    df["local"] = df["Volumenproduccion"] - df["exportaciones"]

    # Calculamos los porcentajes.
    df["local_perc"] = df["local"] / df["Volumenproduccion"] * 100
    df["export_perc"] = df["exportaciones"] / df["Volumenproduccion"] * 100

    # Seleccionamos los últimos 20 años.
    df = df.tail(20)

    # Crearemos dos gráficas de barras apiladas.
    # Una para mercado interno y otra para exportaciones.
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["local"],
            text=df["local_perc"],
            texttemplate="%{text:,.1f}%",
            marker_color="#BE3144",
            name="Consumo local",
            textfont_family="Oswald",
            textposition="inside",
            insidetextanchor="middle",
            marker_line_width=0,
            textfont_size=15,
            textfont_color="#FFFFFF",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["exportaciones"],
            text=df["export_perc"],
            texttemplate="%{text:,.1f}%",
            marker_color="#F05941",
            name="Exportaciones",
            textfont_family="Oswald",
            textposition="inside",
            insidetextanchor="middle",
            marker_line_width=0,
            textfont_size=15,
            textfont_color="#FFFFFF",
        )
    )

    fig.update_xaxes(
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Toneladas producidas al año (proporción del destino)",
        ticks="outside",
        separatethousands=True,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.35,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        barmode="stack",
        legend_itemsizing="constant",
        showlegend=True,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        legend_font_size=14,
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Evolución de la producción de <b>aguacate</b> en México por tipo de mercado ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_r=40,
        margin_b=85,
        margin_l=100,
        title_font_size=22,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuentes: INEGI y SIAP (2024)",
            ),
            dict(
                x=0.5,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.13,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./composicion_produccion.png")


def tendencia_mensual():
    """
    Esta función genera una gráfica de barras de las exportaciones de aguacate de forma mensual.
    """

    # Cargamos el dataset de las cifras de exportación mensual.
    df = pd.read_csv(
        "./data/banxico_exportaciones.csv", parse_dates=["Fecha"], index_col=0
    )
    # Convertimos de miles de dólares a millones de dólares.
    df /= 1000

    # Calculamos el promedio móvil a 12 periodos.
    df["rolling"] = df["USD_miles"].rolling(12).mean()

    # Seleccionamos los últimos 102 meses.
    df = df.tail(102)

    # Creamos una copia del DataFrame exclusivamente para los meses de febrero.
    febrero = df.copy()
    febrero["USD_miles"] = febrero.apply(
        lambda x: x["USD_miles"] if x.name.month == 2 else None, axis=1
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["USD_miles"],
            marker_color="#8e24aa",
            name="Cifras nominales",
            marker_line_width=0,
        )
    )

    # Las barras de febrero se pondrán encima de las originales.
    # esto es para dar énfasis.
    fig.add_trace(
        go.Bar(
            x=febrero.index,
            y=febrero["USD_miles"],
            marker_color="#64dd17",
            name="Cifras nominales (febrero)",
            marker_line_width=0,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["rolling"],
            mode="lines",
            name="Promedio móvil",
            line_width=3,
            line_color="#ffe57f",
        )
    )

    fig.update_xaxes(
        ticks="outside",
        tickformat="%m<br>'%y",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Millones de dólares",
        ticks="outside",
        separatethousands=True,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.35,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        barmode="overlay",
        legend_itemsizing="constant",
        showlegend=True,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        legend_font_size=14,
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text="Evolución del valor de las exportaciones mensuales de <b>aguacate</b> desde México",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_r=40,
        margin_b=100,
        margin_l=100,
        title_font_size=22,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: Banxico (agosto 2024)",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./tendencia_mensual.png")


def precio_medio_rural():
    """
    Esta función crea una gráfica de barras comparando el precio medio rural
    y el precio final al consumidor.
    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Agrupamos por año.
    df = df.groupby("Anio").sum(numeric_only=True)

    # Convertimos las toneladas a kilogramos.
    df["Volumenproduccion"] *= 1000

    # Calculamos el precio medio rural.
    df["pmr"] = df["Valorproduccion"] / df["Volumenproduccion"]

    # Cargamos el dataset de precios de PROFECO.
    precios = pd.read_csv(
        "./data/profeco_precios.csv",
        parse_dates=["fecha_registro"],
        index_col="fecha_registro",
    )

    # Agrupamos por el promedio anual.
    precios = precios.resample("YS").mean(numeric_only=True)
    precios.index = precios.index.year

    # Agregamos el precio final al consumidor.
    df["precio"] = precios["precio"]

    # Quitamos las filas sin registros.
    df = df.dropna(axis=0)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["pmr"],
            text=df["pmr"],
            texttemplate="%{text:,.2f}",
            marker_color="#1565c0",
            name="Precio medio rural (pesos por kilogramo)",
            marker_line_width=0,
            textposition="outside",
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textfont_size=24,
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["precio"],
            text=df["precio"],
            texttemplate="%{text:,.2f}",
            marker_color="#d50000",
            name="Precio al consumidor (pesos por kilogramo)",
            marker_line_width=0,
            textposition="outside",
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textfont_size=24,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        range=[0, df["precio"].max() * 1.1],
        title="Promedio anual en pesos mexicanos (nominales)",
        ticks="outside",
        separatethousands=True,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.35,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        showlegend=True,
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        legend_font_size=14,
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text=f"Evolución del precio medio rural y al consumidor final de <b>aguacate</b> en México ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_r=40,
        margin_b=90,
        margin_l=100,
        title_font_size=22,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuentes: SIAP y PROFECO (2024)",
            ),
            dict(
                x=0.5,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.145,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./precio_medio.png")


def precio_mensual():
    """
    Esta función crea una gráfica de caja mostrando la evolución del precio
    del aguacate al consumidor final.
    """

    # Cargamos el dataset de precios de PROFECO.
    df = pd.read_csv(
        "./data/profeco_precios.csv",
        parse_dates=["fecha_registro"],
        index_col="fecha_registro",
    )

    # Vamos a crear una gráfica de caja para cada mes.
    fig = go.Figure()

    # Iteramos sobre cada año que deseemos graficar.
    for año in range(2019, 2024):
        for mes in range(1, 13):
            
            # Filtramos por mes y año.
            temp_df = df[(df.index.year == año) & (df.index.month == mes)]
            etiquetas = [datetime(año, mes, 1) for _ in range(len(temp_df))]

            fig.add_traces(
                go.Box(
                    x=etiquetas,
                    y=temp_df["precio"],
                    line_width=2,
                    boxpoints=False,
                    marker_line_width=0,
                )
            )

    fig.update_xaxes(
        tickformat="%m<br>'%y",
        ticks="outside",
        tickfont_size=14,
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Precio mensual en pesos mexicanos (nominales)",
        ticks="outside",
        separatethousands=True,
        tickfont_size=14,
        ticklen=10,
        title_standoff=6,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.35,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        colorway=[f"hsla({h}, 100%, 75%, 1.0)" for h in np.linspace(0, 360, 12)],
        showlegend=False,
        width=1280,
        height=720,
        font_family="Lato",
        font_color="#FFFFFF",
        font_size=18,
        title_text="Evolución del precio al consumidor final de <b>aguacate</b> en México (2019-2023)",
        title_x=0.5,
        title_y=0.965,
        margin_t=60,
        margin_r=40,
        margin_b=100,
        margin_l=100,
        title_font_size=22,
        paper_bgcolor=PAPER_BGCOLOR,
        plot_bgcolor=PLOT_BGCOLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: PROFECO (2024)",
            ),
            dict(
                x=0.5,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.16,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./precio_mensual.png")


if __name__ == "__main__":
    comparacion_pib("PIB", "al valor del PIB", 1)
    comparacion_pib("Actividades_primarias", "al valor de las actividades priamrias", 2)
    comparacion_pib("Agricultura", "al valor de la agricultura", 3)

    top_exportaciones(2004, 3)
    top_exportaciones(2023, 1)

    composicion_produccion()
    tendencia_mensual()
    precio_medio_rural()
    precio_mensual()
