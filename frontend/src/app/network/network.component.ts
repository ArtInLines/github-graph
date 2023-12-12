import {Component, OnInit} from '@angular/core';
import {NetworkService} from "../network.service";
import {Node, Edge} from "@swimlane/ngx-graph";
import {GitResponse} from "../model/gitResponse";
import {GraphNode} from "../model/graphNode";
import {GraphEdge} from "../model/graphEdge";

@Component({
  selector: 'app-network',
  templateUrl: './network.component.html',
  styleUrls: ['./network.component.css']
})
export class NetworkComponent implements OnInit {
  nodes: Node[] = new Array<Node>();
  edges: Edge[] = new Array<Edge>();
  constructor(private networkService: NetworkService) { }

  ngOnInit() {
    this.getData();
  }

  async getData() {
    let res: GitResponse = await this.networkService.getNetwork(1, 1, "User", "ArtInLines");
    console.log(res);
    this.nodes = res.nodes.map( gitNode => {
      return new GraphNode(gitNode.id, gitNode.name);
    });
    this.edges = res.rel.map( gitEdge => {
      return new GraphEdge(gitEdge.id, gitEdge.label, gitEdge.source, gitEdge.dest);
    });
  }

  getMockData() {
    this.nodes = [
      new GraphNode('a', 'a'),
      new GraphNode('b', 'b'),
    ];

    this.edges = [
      new GraphEdge('0', 'l0', 'a', 'b')
    ];
  }
}
