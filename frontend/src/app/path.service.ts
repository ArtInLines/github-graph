import { Injectable } from '@angular/core';
import {PathResponse} from "./model/pathResponse";

@Injectable({
  providedIn: 'root'
})
export class PathService {
  url: string = "http://[2001:7c0:2320:2:f816:3eff:fe6a:d6af]:3000";
  constructor() { }

  async getShortestPath(startNode: string, destNode: string, startType: string, destType: string): Promise<PathResponse> {
    let res: Response = await fetch(this.url + "/getDistance?" + "start=" + startNode + "&end=" + destNode + "&typeStart=" + startType + "&typeEnd=" + destType);
    if ( res.status == 204 ) {
      throw new Error("Node doesn't exist");
    } else {
      return res.json().then((res: PathResponse) => {
        return res;
      });
    }
  }
}
