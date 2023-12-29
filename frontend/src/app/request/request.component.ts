import { Component } from '@angular/core';
import {NetworkComponent} from "../network/network.component";
import {NetworkService} from "../network.service";
import {GitResponse} from "../model/gitResponse";
import {GraphNode} from "../model/graphNode";
import {GraphEdge} from "../model/graphEdge";
import {PathService} from "../path.service";

@Component({
  selector: 'app-request',
  templateUrl: './request.component.html',
  styleUrls: ['./request.component.css']
})
export class RequestComponent {
  constructor(private networkService: NetworkService, private pathService: PathService) { }
  protected network_graph: NetworkComponent = new NetworkComponent();
  root_type: string = 'User';
  root_name: string = 'ArtInLines';
  max_distance: number = 1;
  dest_name: string = 'torvalds';
  dest_type: string = 'User';

  async requestData(): Promise<void> {
    let res: GitResponse = await this.networkService.getNetwork(1, this.max_distance, this.root_type, this.root_name);
    console.log('Received network response from server: ' + res);
    this.network_graph.nodes = res.nodes.map(gitNode => {
      return new GraphNode(gitNode.id, gitNode.name);
    });
    this.network_graph.edges = res.rel.map(gitEdge => {
      return new GraphEdge(gitEdge.id, gitEdge.label, gitEdge.source, gitEdge.dest);
    });
  }

  async getShortestPath(): Promise<void> {
    let res: GitResponse = await this.pathService.getShortestPath(this.root_name, this.dest_name, this.root_type, this.dest_type);
    console.log('Received path response from server: ' + res);
    let path_nodes: GraphNode[] = res.nodes.map(gitNode => {
      return new GraphNode(gitNode.id, gitNode.name);
    });
    let path_edges: GraphEdge[] = res.rel.map(gitEdge => {
      return new GraphEdge(gitEdge.id, gitEdge.label, gitEdge.source, gitEdge.dest);
    });

    this.network_graph.highlightPath(path_nodes, path_edges);
  }
}
