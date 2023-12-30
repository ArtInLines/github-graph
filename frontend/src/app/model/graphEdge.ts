import {Edge} from "@swimlane/ngx-graph";

export class GraphEdge implements Edge {
  id: string;
  label: string;
  source: string;
  target: string;

  constructor(id: string, label: string, source: string, target: string) {
    this.id = id;
    this.label = label;
    this.source = source;
    this.target = target;
  }
}
