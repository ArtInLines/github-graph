import {Component, OnInit} from '@angular/core';
import {NetworkService} from "../network.service";
import {GitNode} from "../gitNode";
import {Node, Edge} from "@swimlane/ngx-graph";

@Component({
  selector: 'app-network',
  templateUrl: './network.component.html',
  styleUrls: ['./network.component.css']
})
export class NetworkComponent implements OnInit {
  nodes: Node[] = new Array<Node>();
  edges: Edge[] = new Array<Edge>();
  constructor(private networkService: NetworkService) { }

  async ngOnInit() {
    await this.getNodes();
  }

  async getNodes() {
    let gitNodes: GitNode[] = await this.networkService.getNetwork(0, 2, "User", "ArtInLines");
  }
}
