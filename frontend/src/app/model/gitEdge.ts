export class GitEdge {
  source: string;
  dest: string;
  id: string;
  label: string;
  length: number;

  constructor(source: string, dest: string, id: string, label: string, length: number) {
    this.source = source;
    this.dest = dest;
    this.id = id;
    this.label = label;
    this.length = length;
  }
}
