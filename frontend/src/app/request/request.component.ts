import { Component } from '@angular/core';
import {NetworkComponent} from "../network/network.component";
import {NetworkService} from "../network.service";
import {GitResponse} from "../model/gitResponse";
import {GraphNode} from "../model/graphNode";
import {GraphEdge} from "../model/graphEdge";

@Component({
  selector: 'app-request',
  templateUrl: './request.component.html',
  styleUrls: ['./request.component.css']
})
export class RequestComponent {
  constructor(private networkService: NetworkService) { }
  protected network_graph: NetworkComponent = new NetworkComponent();
  type: string = 'User';
  root_name: string = 'ArtInLines';
  max_distance: number = 1;

  async requestData(): Promise<void> {
    let res: GitResponse = await this.networkService.getNetwork(1, this.max_distance, this.type, this.root_name);
    console.log("Received response from server: " + res);
    this.network_graph.nodes = res.nodes.map(gitNode => {
      return new GraphNode(gitNode.id, gitNode.name);
    });
    this.network_graph.edges = res.rel.map(gitEdge => {
      return new GraphEdge(gitEdge.id, gitEdge.label, gitEdge.source, gitEdge.dest);
    });
  }
}
