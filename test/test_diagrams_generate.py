from pathlib import Path

from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, EKS, Lambda
from diagrams.aws.database import Redshift
from diagrams.aws.integration import SQS
from diagrams.aws.storage import S3
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub
from diagrams.gcp.compute import AppEngine, Functions
from diagrams.gcp.database import BigTable
from diagrams.gcp.iot import IotCore
from diagrams.gcp.storage import GCS

import graphviz2drawio.graphviz2drawio


def test_event_processing():
    with Diagram("Event Processing", outformat=["dot", "svg"], show=False):
        source = EKS("k8s source")

        with Cluster("Event Flows"):
            with Cluster("Event Workers"):
                workers = [ECS("worker1"), ECS("worker2"), ECS("worker3")]

            queue = SQS("event queue")

            with Cluster("Processing"):
                handlers = [Lambda("proc1"), Lambda("proc2"), Lambda("proc3")]

        store = S3("events store")
        dw = Redshift("analytics")

        source >> workers >> queue >> handlers
        handlers >> store
        handlers >> dw
    converted = graphviz2drawio.graphviz2drawio.convert(Path("event_processing.dot"))

    assert (
        "color='#2d3436'&gt;Event Flows&lt;/font&gt;\" style=\"verticalAlign=top;"
        in converted
    )
    assert "strokeColor=#aeb6be;fillColor=#e5f5fd;" in converted
    assert "strokeColor=#aeb6be;fillColor=#ebf3e7;" in converted
    assert "image=data:image/png," in converted


def test_message_collecting():
    with Diagram("Message Collecting", outformat=["dot", "svg"], show=False):
        pubsub = PubSub("pubsub")

        with Cluster("Source of Data"):
            [IotCore("core1"), IotCore("core2"), IotCore("core3")] >> pubsub

        with Cluster("Targets"):
            with Cluster("Data Flow"):
                flow = Dataflow("data flow")

            with Cluster("Data Lake"):
                flow >> [BigQuery("bq"), GCS("storage")]

            with Cluster("Event Driven"):
                with Cluster("Processing"):
                    flow >> AppEngine("engine") >> BigTable("bigtable")

                with Cluster("Serverless"):
                    flow >> Functions("func") >> AppEngine("appengine")

        pubsub >> flow
    converted = graphviz2drawio.graphviz2drawio.convert(Path("message_collecting.dot"))

    assert (
        "color='#2d3436'&gt;Targets&lt;/font&gt;\" style=\"verticalAlign=top;"
        in converted
    )
    assert "strokeColor=#aeb6be;fillColor=#e5f5fd;" in converted
    assert "strokeColor=#aeb6be;fillColor=#ebf3e7;" in converted
    assert "strokeColor=#aeb6be;fillColor=#ece8f6;" in converted
    assert "image=data:image/png," in converted


def icon(node: object, label: str, size=30):
    class Node(node):
        def __init__(self) -> None:
            pass

    icon_path = Node()._load_icon()  # noqa: SLF001
    return (
        f'<<table border="0" width="100%"><tr><td fixedsize="true" '
        f'width="{size}" height="{size}"><img src="{icon_path}" /></td>'
        f"<td>{label}</td></tr></table>>"
    )


def test_event_processing_icon():
    with Diagram(
        "Event Processing Icon",
        show=False,
        outformat=["dot", "svg", "png"],
    ):
        source = EKS("k8s source")

        with Cluster(icon(ECS, "Event Flows")):
            with Cluster(icon(ECS, "Event Workers")):
                workers = [ECS("worker1"), ECS("worker2"), ECS("worker3")]

            queue = SQS("event queue")

            with Cluster("Processing"):
                handlers = [Lambda("proc1"), Lambda("proc2"), Lambda("proc3")]

        store = S3("events store")
        dw = Redshift("analytics")

        source >> workers >> queue >> handlers
        handlers >> store
        handlers >> dw
    converted = graphviz2drawio.graphviz2drawio.convert(
        Path("event_processing_icon.dot"),
    )
    assert (
        "color='#2d3436'&gt;Event Flows&lt;/font&gt;\" style=\"shape=image;"
        in converted
    )
    assert (
        "color='#2d3436'&gt;Event Workers&lt;/font&gt;\" style=\"shape=image;"
        in converted
    )
    assert "fillColor=none;" in converted
    assert "image=data:image/png," in converted
