import {Component, Input} from '@angular/core';
import {Node, Edge} from "@swimlane/ngx-graph";
import {GraphNode} from "../model/graphNode";
import {Subject} from "rxjs";


@Component({
  selector: 'app-network',
  templateUrl: './network.component.html',
  styleUrls: ['./network.component.css']
})
export class NetworkComponent {
  @Input() nodes: Node[] = new Array<Node>();
  @Input() edges: Edge[] = new Array<Edge>();
  @Input() path_nodes: Node[] = new Array<Node>();
  @Input() path_edges: Edge[] = new Array<Edge>();
  draggedNode: GraphNode | undefined;

  center$: Subject<boolean> = new Subject();
  centerGraph() {
    this.center$.next(true)
  }

  /*getEdgeColor(edgeLabel: string): string {
    // Define a mapping of edge labels to colors
    const colorMap: { [key: string]: string } = {
      'Follows': 'red',
      'Owns': 'blue',
      'Contributed': 'purple'
    };
    return colorMap[edgeLabel] || 'gray'; // Fallback color if label not found
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
      document.addEventListener('mousemove', this.onMouseMove);
    }
  }
  onMouseUp = () => {
    // Remove event listeners for mousemove and mouseup
    document.removeEventListener('mousemove', this.onMouseMove);
    document.removeEventListener('mouseup', this.onMouseUp);
  };
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
    if (this.draggedNode && this.draggedNode.position) {
      this.draggedNode.position.x = event.clientX;
      this.draggedNode.position.y = event.clientY;
  }}

  onMouseMove = (event: MouseEvent) => {
    if (this.draggedNode) {
      this.updateNodePosition(event);
    }
  };

  // Drag handler function to track node dragging
  nodeDragHandler = (event: MouseEvent) => {
    this.updateNodePosition(event);
  };

  // Release handler function to stop tracking node dragging
  nodeReleaseHandler = (event: MouseEvent) => {
    this.onNodeMouseUp(event);
  };

  highlightPath(): void {
    //TODO: write code that highlights all edges and nodes from input in existing graph
  }
}
