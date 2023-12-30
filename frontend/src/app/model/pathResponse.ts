import {GitNode} from "./gitNode";
import {GitEdge} from "./gitEdge";

export class PathResponse {
  segmentNodes: GitNode[];
  segmentEdges: GitEdge[];

  constructor(nodes: GitNode[], rel: GitEdge[]) {
    this.segmentNodes = nodes;
    this.segmentEdges = rel;
  }
}
