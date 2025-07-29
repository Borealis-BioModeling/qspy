"""
QSPy Model Diagram Generation Utilities
=======================================

This module provides utilities for generating flowchart-style diagrams of QSPy/PySB models.
It leverages mergram and pyvipr to visualize model structure, including compartments,
species, and reactions, and can export diagrams as Mermaid, Markdown, or HTML blocks.

Classes
-------
ModelMermaidDiagrammer : Generates and exports flowchart diagrams for a given model.

Examples
--------
>>> from qspy.diagrams import ModelDiagram
>>> diagram = ModelDiagram(model)
>>> print(diagram.markdown_block)
>>> diagram.write_mermaid_file("model_flowchart.mmd")
"""

from pathlib import Path

from mergram.flowchart import Flowchart, Node, Link, Subgraph, Style
from pyvipr.pysb_viz.static_viz import PysbStaticViz
from pysb.core import SelfExporter
import seaborn as sns

from qspy.config import METADATA_DIR


class ModelMermaidDiagrammer:
    """
    Generates a Mermaid flowchart diagram of a QSPy/PySB model.

    This class builds a flowchart representation of the model, including compartments,
    species, and reactions, and provides export options for Mermaid, Markdown, and HTML.

    Parameters
    ----------
    model : pysb.Model, optional
        The model to visualize. If None, uses the current SelfExporter.default_model.
    output_dir : str or Path, optional
        Directory to write diagram files (default: METADATA_DIR).

    Attributes
    ----------
    model : pysb.Model
        The model being visualized.
    flowchart : Flowchart
        The generated flowchart object.
    static_viz : PysbStaticViz
        Static visualization helper for the model.
    has_compartments : bool
        Whether the model contains compartments.
    output_dir : Path
        Directory for output files.

    Methods
    -------
    write_mermaid_file(file_path)
        Write the flowchart to a Mermaid file.
    markdown_block
        Return the flowchart as a Markdown block.
    html_block
        Return the flowchart as an HTML block.
    """

    def __init__(self, model=None, output_dir=METADATA_DIR):
        """
        Initialize the ModelMermaidDiagrammer.

        Parameters
        ----------
        model : pysb.Model, optional
            The model to visualize. If None, uses the current SelfExporter.default_model.
        output_dir : str or Path, optional
            Directory to write diagram files (default: METADATA_DIR).
        """
        self.model = model
        if model is None:
            self.model = SelfExporter.default_model
        self.flowchart = Flowchart(self.model.name)
        self.static_viz = PysbStaticViz(self.model)
        self.has_compartments = len(self.model.compartments) > 0
        self._build_flowchart()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        chart_file = self.output_dir / f"{self.model.name}_flowchart.mmd"
        self.write_mermaid_file(chart_file.as_posix())
        setattr(self.model, "mermaid_diagram", self)
        return

    @staticmethod
    def _sanitize_label(label):
        """
        Sanitize a label by removing compartment information.

        Parameters
        ----------
        label : str
            The label to sanitize.

        Returns
        -------
        str
            The sanitized label without compartment information.
        """
        #print(label)
        if "** " in label:
            if "-" in label:
                # Remove compartment from labels with bound monomers
                # e.g., "molec_a() ** CENTRAL % molec_b() ** TUMOR"
                # becomes "molec_a() % molec_b()"
                parts = label.split("-")
                return parts[0].split("** ")[0] + ":" + parts[1].split("** ")[0]
            else:
                # Remove compartment info
                # e.g., "molec_a() ** CENTRAL" -> "molec_a()"
                return label.split("** ")[0]
        return label

    def _build_flowchart(self):
        """
        Build the flowchart representation of the model.

        Parses the model's compartments, species, and reactions, and adds them as nodes,
        subgraphs, and links to the flowchart.
        """
        if self.has_compartments:
            nx_graph = self.static_viz.compartments_data_graph()
        else:
            nx_graph = self.static_viz.species_graph()
        # Add nodes and edges for unidirection `>> None` reactions.
        # This is to handle cases where a reaction has no products.
        for reaction in self.model.reactions_bidirectional:
            reactants = set(reaction["reactants"])
            products = set(reaction["products"])
            rule = self.model.rules[reaction["rule"][0]]
            k_f = rule.rate_forward.name
            if len(products) < 1:
                for s in reactants:
                    s_id = f"s{s}"
                    node_comp = nx_graph.nodes[s_id]["parent"]
                    nx_graph.add_node(
                        "none",
                        NodeType="none",
                        parent=node_comp,
                        label='"fa:fa-circle-xmark"',
                        background_color="#fff",
                    )
                    nx_graph.add_edge(s_id, "none", k_f=k_f, k_r=" ")

        # Parse the networkx graph nodes into flowchart nodes.
        # Create subgraphs for compartments if they exist.
        # Otherwise, create nodes for species.
        flow_nodes = dict()
        for node_id, node_attr in nx_graph.nodes.data():
            if node_attr["NodeType"] == "compartment":
                if node_id not in self.flowchart.subgraphs:
                    self.flowchart += Subgraph(node_id)
            elif node_attr["NodeType"] == "species":
                flow_node = Node(
                    node_id,
                    label=self._sanitize_label(node_attr.get("label", node_id)),
                    fill=node_attr.get("background_color", "#fff"),
                )
                compartment = node_attr["parent"]
                if compartment not in self.flowchart.subgraphs:
                    self.flowchart += Subgraph(compartment)
                self.flowchart.subgraphs[compartment] += flow_node
                flow_nodes[node_id] = flow_node
            elif node_attr["NodeType"] == "none":
                flow_node = Node(
                    node_id,
                    label=self._sanitize_label(node_attr.get("label", node_id)),
                    fill=node_attr.get("background_color", "#fff"),
                    shape="fr-circ",
                )
                self.flowchart += flow_node
                flow_nodes[node_id] = flow_node
        # Go through the reactions and get the names of rate constants
        # and add them to the networkx edge attributes.
        for reaction in self.model.reactions_bidirectional:
            reactants = set(reaction["reactants"])
            products = set(reaction["products"])
            rule = self.model.rules[reaction["rule"][0]]
            k_f = rule.rate_forward.name
            if rule.rate_reverse is None:
                k_r = " "
            else:
                k_r = rule.rate_reverse.name

            for s in reactants:
                s_id = f"s{s}"
                for p in products:
                    p_id = f"s{p}"
                    if nx_graph.has_edge(s_id, p_id):
                        nx_graph[s_id][p_id]["k_f"] = k_f
                        nx_graph[s_id][p_id]["k_r"] = k_r

        for source, target, edge_attr in nx_graph.edges.data():
            if source in flow_nodes and target in flow_nodes:
                self.flowchart += Link(
                    flow_nodes[source],
                    flow_nodes[target],
                    text=edge_attr.get("k_f", " "),
                )
                if edge_attr.get("source_arrow_shape") == "triangle":
                    # Reaction is reversible
                    self.flowchart += Link(
                        flow_nodes[target],
                        flow_nodes[source],
                        text=edge_attr.get("k_r", " "),
                    )
        # Add colors to subgraphs for compartments
        comp_colors = sns.color_palette(
            "Set2", n_colors=len(self.flowchart.subgraphs)
        ).as_hex()
        for subgraph in self.flowchart.subgraphs.values():
            s_id = subgraph.title
            style = Style(
                s_id,
                rx="10px",
                fill=comp_colors.pop(0),
                color="#000",
            )
            self.flowchart += style

        return

    @property
    def markdown_block(self):
        """
        Return the flowchart as a Markdown block.

        Returns
        -------
        str
            Markdown representation of the flowchart.
        """
        return self.flowchart.to_markdown()

    @property
    def html_block(self):
        """
        Return the flowchart as an HTML block.

        Returns
        -------
        str
            HTML representation of the flowchart.
        """
        return self.flowchart.to_html()

    def write_mermaid_file(self, file_path):
        """
        Write the flowchart to a Mermaid file.

        Parameters
        ----------
        file_path : str or Path
            Path to the output Mermaid (.mmd) file.

        Returns
        -------
        None
        """
        self.flowchart.write(file_path)
        return
