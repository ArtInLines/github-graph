import {Node} from "@swimlane/ngx-graph";

export class GraphNode implements Node {
  id: string;
  label: string;
  position: { x: number; y: number };

  // Properties for drag and drop
  initialX?: number;
  initialY?: number;
  dragHandler?: (event: MouseEvent) => void;
  releaseHandler?: (event: MouseEvent) => void;
  showFullLabel?: boolean = false;

  constructor(id: string, label: string) {
    this.id = id;
    this.label = label;
    this.position = { x: 0, y: 0 };
  }
}
