import {GitNode} from "./gitNode";
import {GitEdge} from "./gitEdge";

export class GitResponse {
  nodes: GitNode[];
  rel: GitEdge[];

  constructor(nodes: GitNode[], rel: GitEdge[]) {
    this.nodes = nodes;
    this.rel = rel;
  }
}
