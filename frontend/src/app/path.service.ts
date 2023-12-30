import { Injectable } from '@angular/core';
import {PathResponse} from "./model/pathResponse";

@Injectable({
  providedIn: 'root'
})
export class PathService {
  url: string = "http://localhost:3000";
  constructor() { }

  //this works on the assumption that a path is returned like a network as a set of nodes and a set of edges.
  //might have to be reworked in coordination with backend
  async getShortestPath(startNode: string, destNode: string, startType: string, destType: string): Promise<PathResponse> {
    return await fetch(this.url + "/getDistance?" + "start=" + startNode + "&end=" + destNode + "&typeStart=" + startType + "&typeEnd=" + destType)
      .then( res => res.json())
      .then( (res: PathResponse) => {
        return res;
      });
  }
}
