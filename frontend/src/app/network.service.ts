import { Injectable } from '@angular/core';
import {GitNode} from "./gitNode";

@Injectable({
  providedIn: 'root'
})
export class NetworkService {
  url: string = "http://localhost:3000";
  constructor() { }

  async getNetwork(minDist: number, maxDist: number, type: string, start: string): Promise<Array<GitNode>> {
    return await fetch(this.url + "/getRelatives?" + "minDist=" + minDist + "&maxDist=" + maxDist + "&type=" + type + "&start=" + start)
      .then( res => res.json())
      .then( (res: Array<GitNode>) => {
        return res;
      });
  }
}
