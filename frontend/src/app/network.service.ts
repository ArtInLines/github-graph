import { Injectable } from '@angular/core';
import {GitResponse} from "./model/gitResponse";

@Injectable({
  providedIn: 'root'
})
export class NetworkService {
  url: string = "http://[2001:7c0:2320:2:f816:3eff:fe6a:d6af]:3000";
  constructor() { }

  async getNetwork(minDist: number, maxDist: number, type: string, start: string): Promise<GitResponse> {
    let res: Response = await fetch(this.url + "/getRelatives?" + "minDist=" + minDist + "&maxDist=" + maxDist + "&type=" + type + "&start=" + start);
    if ( res.status == 204 ) {
      throw new Error("Node doesn't exist");
    } else {
      return res.json().then((res: GitResponse) => {
        return res;
      });
    }
  }
}
