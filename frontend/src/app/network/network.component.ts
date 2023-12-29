import {Component, OnInit} from '@angular/core';
import {NetworkService} from "../network.service";
import {Node, Edge, Layout, Graph} from "@swimlane/ngx-graph";
import {GitResponse} from "../model/gitResponse";
import {GraphNode} from "../model/graphNode";
import {GraphEdge} from "../model/graphEdge";


@Component({
  selector: 'app-network',
  templateUrl: './network.component.html',
  styleUrls: ['./network.component.css']
})
export class NetworkComponent implements OnInit {
  nodes: Node[] = new Array<Node>();
  edges: Edge[] = new Array<Edge>();
  draggedNode: Node | undefined;
  constructor() { }

  ngOnInit() {
    this.getMockData();
  }

  /*async getData() {
    let res: GitResponse = await this.networkService.getNetwork(1, 1, "User", "ArtInLines");
    console.log(res);
    this.nodes = res.nodes.map( gitNode => {
      return new GraphNode(gitNode.id, gitNode.name);
    });
    this.edges = res.rel.map( gitEdge => {
      return new GraphEdge(gitEdge.id, gitEdge.label, gitEdge.source, gitEdge.dest);
    });
  }*/

  // Method to toggle label visibility on click
  toggleLabel(node: GraphNode) {
    node.showFullLabel = !node.showFullLabel;
  }

  // Method to handle node dragging
  onNodeMouseDown(event: MouseEvent, node: GraphNode) {
    if (this.draggedNode === undefined) {
      this.draggedNode = node;
      node.dragHandler = this.nodeDragHandler;
      node.releaseHandler = this.nodeReleaseHandler;

      // Add event listeners to the document for mousemove and mouseup
      document.addEventListener('mousemove', this.nodeDragHandler);
      document.addEventListener('mouseup', this.nodeReleaseHandler);
    }
  }

  onNodeMouseUp(event: MouseEvent) {
    if (this.draggedNode !== undefined) {
      // Remove event listeners for mousemove and mouseup
      document.removeEventListener('mousemove', this.nodeDragHandler);
      document.removeEventListener('mouseup', this.nodeReleaseHandler);

      this.draggedNode = undefined;
    }
  }
// Function to update node position during dragging
  updateNodePosition(event: MouseEvent) {
    if (this.draggedNode) {
      // Update node position logic here
    }
  }

  // Drag handler function to track node dragging
  nodeDragHandler = (event: MouseEvent) => {
    this.updateNodePosition(event);
  };

  // Release handler function to stop tracking node dragging
  nodeReleaseHandler = (event: MouseEvent) => {
    this.onNodeMouseUp(event);
  };

  getMockData() {
    this.nodes = [
      new GraphNode('a', 'a'),
      new GraphNode('b', 'b'),
    ];

    this.edges = [
      new GraphEdge('0', 'l0', 'a', 'b')
    ];

  }

}
