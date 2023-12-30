import {Node} from "@swimlane/ngx-graph";

export class GraphNode implements Node {
  id: string;
  label: string;
  position: { x: number; y: number };
  type: string;

  // Properties for drag and drop
  //initialX?: number;
  //initialY?: number;
  dragHandler?: (event: MouseEvent) => void;
  releaseHandler?: (event: MouseEvent) => void;
  showFullLabel?: boolean = true;

  constructor(id: string, label: string, type: string) {
    this.id = id;
    this.label = label;
    this.position = { x: 0, y: 0 };
    this.type = type;
  }
}
