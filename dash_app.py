import dash
from dash.dependencies import Input, Output
from dash import dcc, html
import plotly.graph_objs as go
from sklearn.decomposition import PCA
import numpy as np
import pandas as pd
from db import fetch_papers_as_df
from link_extractor import decode_embedding
from flask import Flask, g


class DashApp:
    def __init__(self, db_name):
        self.db_name = db_name
        self.app = dash.Dash(__name__, server=Flask(__name__))
        self.df = pd.DataFrame(
            columns=["x", "y", "z", "created_at", "url"]
        )  # Initialize the DataFrame
        self.processed_urls = set()  # You might also want to persist this in flask.g if needed
        self.setup_layout()
        self.register_callbacks()
        self.setup_server()

    def setup_layout(self):
        self.app.layout = html.Div(
            [
                dcc.Graph(id="3d-plot"),
                dcc.Interval(id="interval-component", interval=1000, n_intervals=0),
            ]
        )

    def setup_server(self):
        @self.app.server.before_request
        def before_request():
            g.dash_df = pd.DataFrame()

    def register_callbacks(self):
        @self.app.callback(
            Output("3d-plot", "figure"), [Input("interval-component", "n_intervals")]
        )
        def update_graph(n):
            dash_df = g.get("dash_df", pd.DataFrame())
            new_df = self.fetch_and_process_new_papers()

            if not new_df.empty:
                dash_app.df = pd.concat([dash_app.df, new_df])

                print("~~~", len(dash_app.df))

                created_at_normalized = (
                    dash_app.df["created_at"] - dash_app.df["created_at"].min()
                ) / (dash_app.df["created_at"].max() - dash_app.df["created_at"].min())

                trace = go.Scatter3d(
                    x=dash_app.df["x"],
                    y=dash_app.df["y"],
                    z=dash_app.df["z"],
                    mode="markers",
                    text=dash_app.df["url"].apply(lambda x: x.split("/")[-1]),
                    marker=dict(
                        size=5,
                        opacity=0.8,
                        color=created_at_normalized,
                        colorscale="Viridis",
                        colorbar=dict(title="Created At"),
                    ),
                )
                layout = go.Layout(
                    margin={"l": 0, "r": 0, "b": 0, "t": 0},
                    scene=dict(xaxis=dict(title="X"), yaxis=dict(title="Y"), zaxis=dict(title="Z")),
                )
                return {"data": [trace], "layout": layout}
            else:
                return go.Figure()

    def fetch_and_process_new_papers(self):
        df = fetch_papers_as_df(self.db_name)

        if df.empty:
            return df

        if len(df) < 3:
            return pd.DataFrame(columns=["x", "y", "z", "created_at", "url"])

        df["decoded_embedding"] = df["embedding"].apply(decode_embedding)
        df = df[df["decoded_embedding"].apply(lambda x: x.shape[0]) > 0]

        embeddings_matrix = np.stack(df["decoded_embedding"].values)
        pca = PCA(n_components=3)
        pca_result = pca.fit_transform(embeddings_matrix)

        df["x"], df["y"], df["z"] = pca_result[:, 0], pca_result[:, 1], pca_result[:, 2]

        return df

    def run(self, debug=False):
        self.app.run_server(debug=debug)
