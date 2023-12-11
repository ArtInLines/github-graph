export class GitEdge {
    source
    dest
    id
    label
    length
  
    constructor(source, dest, id, label, length) {
      this.source = source;
      this.dest = dest;
      this.id = id;
      this.label = label;
      this.length = length;
    }
  }
