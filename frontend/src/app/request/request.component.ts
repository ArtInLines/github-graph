import {Component, OnInit} from '@angular/core';
import {NetworkService} from "../network.service";
import {GitResponse} from "../model/gitResponse";
import {GraphNode} from "../model/graphNode";
import {GraphEdge} from "../model/graphEdge";
import {PathService} from "../path.service";
import {GitNode} from "../model/gitNode";
import {GitEdge} from "../model/gitEdge";
import {PathResponse} from "../model/pathResponse";

@Component({
  selector: 'app-request',
  templateUrl: './request.component.html',
  styleUrls: ['./request.component.css']
})
export class RequestComponent implements OnInit{
  constructor(private networkService: NetworkService, private pathService: PathService) { }
  root_type: string = 'User';
  root_name: string = 'ArtInLines';
  max_distance: number = 1;
  dest_name: string = 'torvalds';
  dest_type: string = 'User';
  graph_nodes: GraphNode[] = new Array<GraphNode>();
  graph_edges: GraphEdge[] = new Array<GraphEdge>();
  path_nodes: GraphNode[] = new Array<GraphNode>();
  path_edges: GraphEdge[] = new Array<GraphEdge>();
  unknownRootNode: boolean = false;
  unknownDestNode: boolean = false;

  ngOnInit() {
    this.requestData();
  }

  async requestData(): Promise<void> {
    let res: GitResponse;
    try {
      res = await this.networkService.getNetwork(1, this.max_distance, this.root_type, this.root_name);
      console.log('Received network response from server');
      console.log(res);
    } catch (e) {
      this.unknownRootNode = true;
      return;
    }
    this.unknownRootNode = false;
    this.graph_nodes = res.nodes.map(gitNode => {
      return new GraphNode(gitNode.id, gitNode.name, gitNode.label);
    });
    this.graph_edges = res.rel.map(gitEdge => {
      return new GraphEdge(gitEdge.id, gitEdge.label, gitEdge.source, gitEdge.dest);
    });
  }

  async getShortestPath(): Promise<void> {
    let res: PathResponse;
    try {
      res = await this.pathService.getShortestPath(this.root_name, this.dest_name, this.root_type, this.dest_type);
      console.log('Received path response from server');
      console.log(res);
    } catch (e) {
      this.unknownDestNode = true;
      return;
    }
    this.unknownDestNode = false;
    this.graph_nodes = res.segmentNodes.map((gitNode: GitNode) => {
      return new GraphNode(gitNode.id, gitNode.name, gitNode.label);
    });
    this.graph_edges = res.segmentEdges.map((gitEdge: GitEdge) => {
      return new GraphEdge(gitEdge.id, gitEdge.label, gitEdge.source, gitEdge.dest);
    });
  }
}
