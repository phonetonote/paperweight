import logging
import dash
from dash.dependencies import Input, Output
from dash import dcc, html, dash_table
import plotly.graph_objs as go
from sklearn.decomposition import PCA
import numpy as np
import pandas as pd
from db import fetch_papers_as_df
from link_extractor import decode_embedding
from flask import Flask


# This is very much a v1, but we are at least rendering the embeddings in 3d,
# and showing a table with the paper data.
class DashApp:
    def __init__(self, db_name):
        logging.getLogger("werkzeug").setLevel(logging.WARNING)
        self.db_name = db_name
        self.app = dash.Dash(__name__, server=Flask(__name__))
        self.setup_layout()
        self.register_callbacks()

    def setup_layout(self):
        self.app.layout = html.Div(
            [
                html.Button("Refresh Data", id="refresh-button"),
                dcc.Graph(id="3d-plot"),
                dash_table.DataTable(
                    id="paper-table",
                    style_table={
                        "overflowX": "auto",
                        "width": "100%",
                        "maxWidth": "100%",
                    },
                    style_cell={"textAlign": "left", "padding": "5px"},
                    style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
                ),
            ],
            style={"width": "80%", "margin": "auto"},
        )

    def register_callbacks(self):
        @self.app.callback(
            [
                Output("3d-plot", "figure"),
                Output("paper-table", "data"),
                Output("paper-table", "columns"),
            ],
            [Input("refresh-button", "n_clicks")],
        )
        def update_graph(n_clicks):
            new_df = self.fetch_and_process_new_papers()

            if not new_df.empty and len(new_df) > 3:
                created_at_normalized = (new_df["created_at"] - new_df["created_at"].min()) / (
                    new_df["created_at"].max() - new_df["created_at"].min()
                )

                trace = go.Scatter3d(
                    x=new_df["x"],
                    y=new_df["y"],
                    z=new_df["z"],
                    mode="markers",
                    hovertext=new_df.apply(get_text, axis=1),
                    hoverinfo="text",
                    hoverinfosrc="hovertext",
                    marker=dict(
                        size=10,
                        opacity=0.8,
                        color=created_at_normalized,
                        colorscale="Plotly3",
                        colorbar=dict(title="created at. 1=new 0=old"),
                    ),
                )
                layout = go.Layout(
                    margin={"l": 0, "r": 0, "b": 0, "t": 0},
                    scene=dict(xaxis=dict(title=""), yaxis=dict(title=""), zaxis=dict(title="")),
                    height=900,
                )
                graph_figure = {"data": [trace], "layout": layout}
                table_data = new_df.to_dict("records")
                columns = [{"name": i, "id": i} for i in new_df.columns]

                return graph_figure, table_data, columns
            else:
                graph_figure = {"data": [], "layout": {}}
                table_data = []
                columns = []
                return graph_figure, table_data, columns

    def fetch_and_process_new_papers(self):
        df = fetch_papers_as_df(self.db_name)
        if df.empty:
            return df

        if len(df) <= 3:
            return pd.DataFrame(columns=["x", "y", "z", "created_at", "url"])

        df["decoded_embedding"] = df["embedding"].apply(decode_embedding)
        df = df[df["decoded_embedding"].apply(lambda x: x.shape[0]) > 0]

        embeddings_matrix = np.stack(df["decoded_embedding"].values)
        pca = PCA(n_components=3)
        df["url"] = df["url"].transform(trim_url)
        pca_result = pca.fit_transform(embeddings_matrix)

        df["x"], df["y"], df["z"] = pca_result[:, 0], pca_result[:, 1], pca_result[:, 2]
        return df[
            [
                "url",
                "title",
                "authors",
                "published_date",
                "summary",
                "institution",
                "location",
                "status",
                "created_at",
                "x",
                "y",
                "z",
            ]
        ]

    def run(self, debug=False):
        self.app.run_server(debug=debug)


def get_text(row):
    parts = [row["url"].split("/")[-1], row.get("title", "")]
    filtered_parts = [part for part in parts if part]
    return "<br>".join(filtered_parts)


def trim_url(url, max_length=50):
    if len(url) <= max_length:
        return url
    else:
        part_length = max_length // 2 - 2
        return url[:part_length] + "..." + url[-part_length:]
