from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import STL


FECHA_FUENTE = "septiembre 2026"

# Paleta de colores para todas las gráficas.
PLOT_COLOR = "#1C1F1A"
PAPER_COLOR = "#262B23"


ENTIDADES = {
    0: "México",
    1: "Aguascalientes",
    2: "Baja California",
    3: "Baja California Sur",
    4: "Campeche",
    5: "Coahuila",
    6: "Colima",
    7: "Chiapas",
    8: "Chihuahua",
    9: "Ciudad de México",
    10: "Durango",
    11: "Guanajuato",
    12: "Guerrero",
    13: "Hidalgo",
    14: "Jalisco",
    15: "Estado de México",
    16: "Michoacán",
    17: "Morelos",
    18: "Nayarit",
    19: "Nuevo León",
    20: "Oaxaca",
    21: "Puebla",
    22: "Querétaro",
    23: "Quintana Roo",
    24: "San Luis Potosí",
    25: "Sinaloa",
    26: "Sonora",
    27: "Tabasco",
    28: "Tamaulipas",
    29: "Tlaxcala",
    30: "Veracruz",
    31: "Yucatán",
    32: "Zacatecas",
}


def participacion_economica(id_industria, titulo, id_entidad):
    """
    Genera una gráfica mostrando la evolución
    del valor de le producción de aguacate respecto
    a una industria y entidad especificados.

    Parameters
    ----------
    id_industria : str
        El código de la dinsutria a comparar.

    titulo : str
        Este texto ayuda a formatear el título.

    id_entidad : int
        El identificador de la entidad a comparar.

    """

    # Cargamos el dataset del PIB estatal.
    pib = pd.read_csv("./assets/PIB_estatal.csv", index_col=00)

    # Filtramos por la clave de la industria especificada.
    pib = pib[pib["CLAVE_INDUSTRIA"] == id_industria]

    # Filtramos por la clave de la entidad especificada.
    pib = pib[pib["CVE_ENT"] == id_entidad]

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Filtramos poe entidad federativa.
    # Si la entidad es 0 omitimos este paso.
    if id_entidad != 0:
        df = df[df["CVE_ENT"] == id_entidad]

    # Calculamos el valor de la producción anual.
    df = df.groupby("AÑO").sum(numeric_only=True)[["VALOR_PRODUCCION"]]

    # Agregamos el valor corriente de la industria especificada.
    # Ajustamos el valor de millones a pesos.
    df["pib"] = pib["VALOR_CORRIENTE"] * 1000000

    # Calculamos el porcentaje respecto al PIB.
    df["porcentaje"] = df["VALOR_PRODUCCION"] / df["pib"] * 100

    # Quitamos registros incompletos.
    df = df.dropna(axis=0)

    # Escogemos los últimos 20 años.
    df = df.tail(20)

    # Dependiendo la magnitud del porcentaje será el formato del texto.
    valor_ref = df["porcentaje"].min()

    if valor_ref >= 10:
        df["texto"] = df["porcentaje"].apply(lambda x: f"{x:,.01f}")
    elif valor_ref >= 1:
        df["texto"] = df["porcentaje"].apply(lambda x: f"{x:,.02f}")
    else:
        df["texto"] = df["porcentaje"].apply(lambda x: f"{x:,.03f}")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["porcentaje"],
            text=df["texto"],
            mode="markers+lines+text",
            fill="toself",
            marker_color="#8bc34a",
            line_width=5,
            marker_size=24,
            textfont_family="Oswald",
            textfont_color="#FFFFFF",
            textposition="top center",
            line_shape="spline",
        )
    )

    fig.update_xaxes(
        range=[df.index.min() - 0.6, df.index.max() + 0.6],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=len(df) + 1,
    )

    fig.update_yaxes(
        title=f"Porcentaje respecto {titulo}",
        ticksuffix="%",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Valor de la producción de <b>aguacate</b> en <b>{ENTIDADES[id_entidad]}</b> como porcentaje {titulo} ({df.index[0]}-{df.index[-1]})",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=140,
        margin_r=40,
        margin_b=125,
        title_font_size=34,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuentes: INEGI, SIAP (2026)",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./participacion_{id_industria}_{id_entidad}.png")


def participacion_produccion(id_entidad):
    """
    Genera una gráfica mostrando la evolución
    de la participación de una entidad en la
    producción nacinoal de aguacate (volumen).

    Parameters
    ----------
    id_industria : str
        El código de la dinsutria a comparar.

    titulo : str
        Este texto ayuda a formatear el título.

    id_entidad : int
        El identificador de la entidad a comparar.

    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Calculamos la producción anual por entidad.
    df = df.pivot_table(
        index="AÑO",
        columns="CVE_ENT",
        values="VOLUMEN_PRODUCCION",
        aggfunc="sum",
        fill_value=0,
    )

    # Calculamos el total nacoinal.
    df["total"] = df.sum(axis=1)

    # Calculamos la participación de la entidad con el total nacional.
    df["porcentaje"] = df[id_entidad] / df["total"] * 100

    # Escogemos los últimos 20 años.
    df = df.tail(20)

    # Dependiendo la magnitud del porcentaje será el formato del texto.
    valor_ref = df["porcentaje"].min()

    if valor_ref >= 10:
        df["texto"] = df["porcentaje"].apply(lambda x: f"{x:,.01f}")
    elif valor_ref >= 1:
        df["texto"] = df["porcentaje"].apply(lambda x: f"{x:,.02f}")
    else:
        df["texto"] = df["porcentaje"].apply(lambda x: f"{x:,.03f}")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["porcentaje"],
            text=df["texto"],
            mode="markers+lines+text",
            fill="toself",
            marker_color="#40c4ff",
            line_width=5,
            marker_size=24,
            textfont_family="Oswald",
            textfont_color="#FFFFFF",
            textposition="top center",
            line_shape="spline",
        )
    )

    fig.update_xaxes(
        range=[df.index.min() - 0.6, df.index.max() + 0.6],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=len(df) + 1,
    )

    fig.update_yaxes(
        title="Participación en la producción nacional (%)",
        ticksuffix="%",
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Participación de <b>{ENTIDADES[id_entidad]}</b> en la producción nacional de aguacate ({df.index[0]}-{df.index[-1]})",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=140,
        margin_r=40,
        margin_b=125,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuente: SIAP (2026)",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./participacion_{id_entidad}.png")


def top_destinos(año):
    """
    Genera una gráfica de barras mostrando los principales
    destinos de exportación de aguacate por volumen.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el catálogo de países.
    paises = pd.read_csv("./assets/paises.csv", index_col=0)

    # Este DataFrame será utilizado como diccionario más adelante.
    paises = paises["PAIS"]

    # Cargamos el dataset de exportaciones del INEGI.
    df = pd.read_csv("./data/inegi_exportaciones.csv")

    # Filtramos por el año que nos interesa.
    df = df[df["ANIO"] == año]

    # Seleccionamos solamete las exportaciones.
    df = df[df["TIPO"] == "Exportaciones"]

    # Convertimos de kilogramos a toneladas.
    df["CANTIDAD"] /= 1000

    # Vamos a extraer los valores totales.
    valor_usd = df["VAL_USD"].max()
    valor_mxn = df["VAL_MNX"].max()
    volumen = df["CANTIDAD"].max()

    # Quitamos filas sin valor en cantidad.
    df = df[~pd.isna(df["CANTIDAD"])]

    # Agrupamos por páis de destino usando el valor más alto.
    # En ocasiones las cifras reales no están en la categoría principal
    # sino en las subcategorías.
    df = df.groupby("PAIS_O_D").max(numeric_only=True)

    # Asignamos el nombre de cada país.
    df["nombre"] = df.index.map(paises)

    # Ordenamos por cantidad de kilogramos exportados.
    df.sort_values("CANTIDAD", inplace=True)

    # Calculamos el porcentaje enviado a cada país.
    df["porcentaje"] = df["CANTIDAD"] / volumen * 100

    # Los nombres largos los partimos en dos.
    df["nombre"] = df["nombre"].apply(lambda x: x.split("(")[0])
    df["nombre"] = df["nombre"].str.wrap(15).str.replace("\n", "<br>")

    # Creamos el texto para cada barra.
    df["texto"] = df.apply(
        lambda x: f" {x['CANTIDAD']:,.0f} ({x['porcentaje']:,.2f}%) ", axis=1
    )

    # Calculamos la razón.
    df["ratio"] = np.log10(df["CANTIDAD"]) / np.log10(df["CANTIDAD"].max())

    # Calculamos la posición del texto en cada barra.
    df["text_pos"] = df["ratio"].apply(lambda x: "inside" if x >= 0.91 else "outside")

    # Escogemos los 20 registros más altos.
    df = df.tail(20)

    # Preparamos las notas.
    notas = [
        "<b>Notas:</b>",
        "Se utilizó una escala logarítmica debido<br>a la gran diferencia entre valores.",
        f"Volumen total: {volumen:,.0f} toneladas",
        f"Valor en pesos: {valor_mxn / 1000000:,.0f} mdp",
        f"Valor en dolares: {valor_usd / 1000000:,.0f} mdd",
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["CANTIDAD"],
            y=df["nombre"],
            text=df["texto"],
            orientation="h",
            textposition=df["text_pos"],
            marker_color="#689f38",
            marker_line_width=0,
            textfont_family="Oswald",
            textfont_color="#FFFFFF",
            textfont_size=28,
            width=0.55,
            marker_cornerradius=50,
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
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=20,
    )

    fig.update_yaxes(
        ticks="outside",
        ticklen=10,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=False,
        gridwidth=0.5,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        showlegend=False,
        width=1920,
        height=1920,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Los {len(df)} principales destinos de exportación de <b>aguacate mexicano</b> durante {año}",
        title_x=0.5,
        title_y=0.975,
        margin_t=100,
        margin_r=40,
        margin_b=120,
        margin_l=280,
        title_font_size=40,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.99,
                y=0,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="bottom",
                bgcolor=PLOT_COLOR,
                borderwidth=1,
                bordercolor="#EEEEEE",
                borderpad=7,
                align="left",
                text="<br>".join(notas),
            ),
            dict(
                x=0.01,
                y=-0.055,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: INEGI (BCMM, {año})",
            ),
            dict(
                x=0.5,
                y=-0.055,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Toneladas exportadas (porcentaje del total)",
            ),
            dict(
                x=1.01,
                y=-0.055,
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
    Genera una gráfica mostrando la composicoón
    del mercado de destino de la producción de aguacate.
    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Agrupamos por año.
    df = df.groupby("AÑO").sum(numeric_only=True)

    # Cargamos el dataset de exportaciones del INEGI.
    exportacioes = pd.read_csv("./data/inegi_exportaciones.csv")

    # Seleccionamos solamente las exportaciones.
    exportacioes = exportacioes[exportacioes["TIPO"] == "Exportaciones"]

    # Agrupamos por año, seleccionando el vaor máximo.
    exportacioes = exportacioes.groupby("ANIO").max(numeric_only=True)

    # Agregamos las toneldas de exportación.
    df["exportaciones"] = exportacioes["CANTIDAD"] / 1000

    # Calculamos el consumo local.
    df["local"] = df["VOLUMEN_PRODUCCION"] - df["exportaciones"]

    # Calculamos los porcentajes.
    df["local_perc"] = df["local"] / df["VOLUMEN_PRODUCCION"] * 100
    df["export_perc"] = df["exportaciones"] / df["VOLUMEN_PRODUCCION"] * 100

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
            marker_color="#1565c0",
            name="Consumo local",
            textfont_family="Oswald",
            textposition="inside",
            insidetextanchor="middle",
            marker_line_width=0,
            textfont_size=24,
            textfont_color="#FFFFFF",
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["exportaciones"],
            text=df["export_perc"],
            texttemplate="%{text:,.1f}%",
            marker_color="#b71c1c",
            name="Exportaciones",
            textfont_family="Oswald",
            textposition="inside",
            insidetextanchor="middle",
            marker_line_width=0,
            textfont_size=24,
            textfont_color="#FFFFFF",
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.35,
        mirror=True,
        nticks=len(df) + 1,
    )

    fig.update_yaxes(
        title="Toneladas producidas al año",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
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
        legend_bordercolor="#EEEEEE",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución de la producción de <b>aguacate</b> en México según tipo de mercado ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=140,
        margin_r=40,
        margin_b=125,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuentes: INEGI, SIAP (2026)",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./composicion_produccion.png")


def tendencia_mensual(id_pais):
    """
    Genera una gráfica de barras mostrando la evolución
    de las exportaciones mensuales al país especificado.


    Parameters
    ----------
    id_pais : str
        El identificador del país que se desea visualizar.

    """

    # Cargamos el dataset de exportaciones de la Secretaría de Economia.
    df = pd.read_csv(
        "./data/se_exportaciones.csv", parse_dates=["Month"], index_col="Month"
    )

    # Convertimos las cifras a millones de dólares.
    df["Trade Value"] /= 1000000

    # Seleccionamos solamete las exportaciones.
    df = df[df["Flow"] == "Exportaciones"]

    # Filtramos por el país especificado.
    df = df[df["País / Región ID"] == id_pais.lower()]

    # Extraemos el nombre del país.
    nombre_pais = df["País / Región"].iloc[0]

    # Los datos ya son mensuales.
    # Nos falta explicitar la frecuencia.
    df = df.resample("MS").sum(numeric_only=True)

    # Calculamos la tendencia a 12 periodos.
    df["tendencia"] = STL(df["Trade Value"]).fit().trend

    df["color"] = df.index.map(lambda x: "#ffab00" if x.month == 2 else "#d81b60")

    # Seleccionamos los últimos 10 años.
    df = df.tail(120)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Trade Value"],
            marker_color=df["color"],
            name="Serie original",
            marker_line_width=0,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["tendencia"],
            mode="lines",
            name="Tendencia",
            line_width=5,
            line_color="#FFFFFF",
        )
    )

    fig.update_xaxes(
        ticks="outside",
        tickformat="%m<br>'%y",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title="Millones de dólares mensuales (corrientes)",
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=18,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        legend_orientation="h",
        showlegend=True,
        legend_x=0.5,
        legend_y=1.06,
        legend_xanchor="center",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución del valor de las exportaciones mensuales de <b>aguacate mexicano</b> a <b>{nombre_pais}</b> ({df.index.year.min()}-{df.index.year.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=120,
        margin_l=140,
        margin_r=40,
        margin_b=160,
        title_font_size=34,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: SE ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./exportaciones_{id_pais.lower()}.png")


def precio_medio_rural():
    """
    Genera una gráfica de barras comparando el precio
     medio rural el precio final al consumidor.
    """

    # Cargamos el dataset de la producción de aguacate en México.
    df = pd.read_csv("./data/siap_produccion.csv")

    # Agrupamos por año.
    df = df.groupby("AÑO").sum(numeric_only=True)

    # Convertimos las toneladas a kilogramos.
    df["VOLUMEN_PRODUCCION"] *= 1000

    # Calculamos el precio medio rural.
    df["pmr"] = df["VALOR_PRODUCCION"] / df["VOLUMEN_PRODUCCION"]

    # Cargamos el dataset de precios de PROFECO.
    precios = pd.read_csv(
        "./data/profeco_precios.csv",
        parse_dates=["FECHA_REGISTRO"],
        index_col="FECHA_REGISTRO",
    )

    # Agrupamos por el promedio anual.
    precios = precios.resample("YS").mean(numeric_only=True)
    precios.index = precios.index.year

    # Agregamos el precio final al consumidor.
    df["precio"] = precios["PRECIO"]

    # Quitamos las filas sin registros.
    df = df.dropna(axis=0)

    # Calculamos la razón.
    df["razon"] = df["precio"] / df["pmr"]

    # Preparamos el texto para el precio, que incluirá la razón.
    df["texto"] = df.apply(
        lambda x: f"{x['precio']:,.2f}<br>({x['razon']:,.1f}:1)", axis=1
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["pmr"],
            text=df["pmr"],
            texttemplate="%{text:,.2f}",
            marker_color="#009688",
            name="Precio medio rural (pesos por kg)",
            marker_line_width=0,
            textposition="outside",
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textfont_size=30,
        )
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["precio"],
            text=df["texto"],
            marker_color="#fb8c00",
            name="Precio al consumidor (pesos por kg)",
            marker_line_width=0,
            textposition="outside",
            textfont_color="#FFFFFF",
            textfont_family="Oswald",
            textfont_size=30,
        )
    )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        range=[0, df["precio"].max() * 1.16],
        title="Promedio anual en pesos mexicanos (corrientes)",
        ticks="outside",
        ticklen=10,
        title_standoff=18,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_bordercolor="#EEEEEE",
        legend_x=0.01,
        legend_y=0.98,
        legend_xanchor="left",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución del precio medio rural y al consumidor de <b>aguacate</b> en México ({df.index.min()}-{df.index.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_l=140,
        margin_r=40,
        margin_b=125,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text="Fuentes: SIAP, PROFECO (2026)",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Año de registro",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image("./precio_medio.png")


def precio_mensual(id_entidad, tipo):
    """
    Genera un serie de boxplots con la
    distribución del precio mensual del aguacate.

    Parameters
    ----------
    id_ entidad : int

        El identificador de la entidad a comparar.

    """

    # Cargamos el dataset de precios de PROFECO.
    df = pd.read_csv("./data/profeco_precios.csv", parse_dates=["FECHA_REGISTRO"])

    # Filtramos poe entidad federativa.
    # Si la entidad es 0 omitimos este paso.
    if id_entidad != 0:
        df = df[df["ESTADO"] == ENTIDADES[id_entidad]]

    df = df[df["FECHA_REGISTRO"].dt.year >= 2021]

    df["FECHA_REGISTRO"] = df["FECHA_REGISTRO"].apply(lambda x: x.replace(day=1))

    # Deflactamos las cifras si el parámetro 'tipo' es 'constante'.
    if tipo == "constante":
        # Cargamos el INPC mensual, el cual se alineará con nuestros precios mensuales.
        ipc = pd.read_csv("./assets/IPC.csv", parse_dates=["PERIODO"], index_col=0)

        # Utilizamos el mes más reciente como base.
        ipc = ipc["GENERAL"].iloc[-1] / ipc["GENERAL"]

        # Asignamos el cociente correspondiente a cada mes.
        df["factor"] = df["FECHA_REGISTRO"].map(ipc)

        # Deflactamos los precios originales.
        df["PRECIO"] *= df["factor"]

        titulo_y = "Pesos constantes a precios de agosto de 2026"
    else:
        titulo_y = "Pesos corrientes"

    # Calculamos medianas y conteos. Estos serán utilizados más adelante.
    estadisticas = df.groupby("FECHA_REGISTRO").agg(
        mediana=("PRECIO", "median"),
        conteo=("FECHA_REGISTRO", "count"),
    )

    # Vamos a crear una gráfica de caja para cada mes.
    fig = go.Figure()

    # Iteramos sobre cada mes y creamos su respectivo Box plot.
    for item in estadisticas.index:
        temp_df = df[df["FECHA_REGISTRO"] == item]

        fig.add_traces(
            go.Box(
                x=temp_df["FECHA_REGISTRO"],
                y=temp_df["PRECIO"],
                line_width=2,
                boxpoints=False,
                marker_line_width=0,
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=estadisticas.index,
            y=estadisticas["mediana"],
            mode="lines+markers",
            marker_size=10,
            line_width=2,
            marker_color="#FFFFFF",
            name="Mediana mensual",
        )
    )

    # Le daremos espaciado al rango del eje horizontal.
    fig.update_xaxes(
        range=[
            estadisticas.index.min().date() - timedelta(days=20),
            estadisticas.index.max().date() + timedelta(days=20),
        ],
        tickformat="%m<br>'%y",
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=25,
    )

    fig.update_yaxes(
        title=titulo_y,
        ticks="outside",
        ticklen=10,
        title_standoff=15,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=False,
        mirror=True,
    )

    fig.update_layout(
        colorway=[f"hsla({h}, 100%, 75%, 1.0)" for h in np.linspace(0, 250, 12)],
        showlegend=True,
        legend_itemsizing="constant",
        legend_xanchor="right",
        legend_yanchor="top",
        legend_x=0.99,
        legend_y=0.98,
        width=1920,
        height=1080,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución del precio al consumidor de <b>1 kg de aguacate</b> en <b>{ENTIDADES[id_entidad]}</b> ({estadisticas.index.year.min()}-{estadisticas.index.year.max()})",
        title_x=0.5,
        title_y=0.965,
        margin_t=90,
        margin_l=140,
        margin_r=40,
        margin_b=160,
        title_font_size=36,
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=PLOT_COLOR,
        annotations=[
            dict(
                x=0.5,
                y=0.035,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                borderwidth=1,
                bordercolor="#EEEEEE",
                bgcolor=PLOT_COLOR,
                borderpad=7,
                text=f"<b>Nota:</b> Cada mes cuenta con al menos <b>{estadisticas['conteo'].min():,.0f}</b> observaciones.",
            ),
            dict(
                x=0.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: PROFECO ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Mes y año de registro",
            ),
            dict(
                x=1.01,
                y=-0.162,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./precios_{tipo}_{id_entidad}.png")


def precio_anual(id_entidad, giro):
    """
    Genera un ridge plot, mostrando la distribución y evolución
    del precio del agaucate para la entidad especificada.


    """

    # Cargamos el dataset del IPC.
    ipc = pd.read_csv("./assets/IPC.csv", parse_dates=["PERIODO"], index_col=0)

    # Calculamos medianas anuales y seleccionamos inflación general.
    ipc = ipc.resample("YS").median()["GENERAL"]

    # Calculamos el cambio porcentual entre 2015 y 2026.
    primero = ipc.loc["2015-01-01"]
    ultimo = ipc.loc["2026-01-01"]
    ipc_cambio = (ultimo - primero) / primero * 100

    # Cargamos el dataset de precios de PROFECO.
    df = pd.read_csv("./data/profeco_precios.csv", parse_dates=["FECHA_REGISTRO"])

    # Filtramos poe entidad federativa.
    # Si la entidad es 0 omitimos este paso.
    if id_entidad != 0:
        df = df[df["ESTADO"] == ENTIDADES[id_entidad]]

    # Filtramos por tipo de giro.
    if giro == "mercados":
        df = df[df["GIRO"] == "MERCADOS"]
    elif giro == "autoservicio":
        df = df[df["GIRO"].str.contains("autoservicio", case=False)]
        giro = "tiendas de autoservicio"

    # Calculamos estadísticas para mostrar en nuestro eje vertical.
    estadisticas = df.groupby(df["FECHA_REGISTRO"].dt.year).agg(
        media=("PRECIO", "mean"),
        mediana=("PRECIO", "median"),
        conteo=("PRECIO", "count"),
    )

    # Calculamos el cambio porcentaul del precio mediano del aguacate.
    primero = estadisticas["mediana"].iloc[0]
    ultimo = estadisticas["mediana"].iloc[-1]
    precio_cambio = (ultimo - primero) / primero * 100

    # Preparamos una nota con los datos previamente calculados.
    nota = "<br>".join(
        [
            "<b>Nota:</b>",
            "Entre 2015 y 2026, la inflación",
            f"general acumulada fue del <b>{ipc_cambio:,.0f}%</b>.",
            "Mientras que el precio mediano",
            f"del aguacate incrementó en <b>{precio_cambio:,.0f}%</b>.",
        ]
    )

    fig = go.Figure()

    # Vamos a iterar sobre cada año de forma reversible.
    # Esto es para mostrar 2015 en la parte superior.
    for año, row in estadisticas.iloc[::-1].iterrows():
        temp_df = df[df["FECHA_REGISTRO"].dt.year == año]

        fig.add_trace(
            go.Violin(
                x=temp_df["PRECIO"],
                orientation="h",
                side="positive",
                name=f"<b>{año}</b><br>n={row['conteo']:,.0f}<br>media={row['media']:,.2f}<br>mediana={row['mediana']:,.2f}",
                width=2.0,
            )
        )

    fig.update_xaxes(
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        showline=True,
        gridwidth=0.8,
        mirror=True,
        nticks=35,
    )

    fig.update_yaxes(
        range=[-0.5, 12.2],
        tickfont_size=20,
        ticks="outside",
        tickcolor="#EEEEEE",
        linecolor="#EEEEEE",
        linewidth=2,
        showgrid=True,
        gridwidth=0.8,
        showline=True,
        mirror=True,
    )

    fig.update_layout(
        colorway=[f"hsla({h}, 100%, 80%, 1.0)" for h in np.linspace(0, 250, 12)],
        showlegend=False,
        width=1920,
        height=2400,
        font_family="Inter",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Evolución del precio de <b>1 kg de aguacate</b> en {ENTIDADES[id_entidad]} ({estadisticas.index.min()}-{estadisticas.index.max()})<br>(muestreo anual en {giro})",
        title_x=0.5,
        title_y=0.97,
        margin_t=140,
        margin_l=240,
        margin_r=40,
        margin_b=120,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.98,
                y=0.97,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                align="left",
                bgcolor=PLOT_COLOR,
                borderpad=7,
                bordercolor="#EEEEEE",
                borderwidth=1.6,
                text=nota,
            ),
            dict(
                x=0.01,
                y=-0.045,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: PROFECO ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.045,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Pesos mexicanos (corrientes)",
            ),
            dict(
                x=1.01,
                y=-0.045,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./precios_{giro}_{id_entidad}.png")


if __name__ == "__main__":
    participacion_economica("PIB", "del PIB", 0)
    participacion_economica("PIB", "del PIB", 16)
    participacion_economica("111", "de la agricultura", 0)
    participacion_economica("111", "de la agricultura", 16)

    participacion_produccion(14)
    participacion_produccion(16)

    top_destinos(2005)
    top_destinos(2025)

    composicion_produccion()

    tendencia_mensual("USA")
    tendencia_mensual("JPN")

    precio_medio_rural()

    precio_mensual(9, "constante")
    precio_mensual(9, "corriente")

    precio_anual(9, "autoservicio")
    precio_anual(9, "mercados")
