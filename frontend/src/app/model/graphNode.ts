import {Node} from "@swimlane/ngx-graph";

export class GraphNode implements Node {
  id: string;
  label: string;

  constructor(id: string, label: string) {
    this.id = id;
    this.label = label;
  }
}
