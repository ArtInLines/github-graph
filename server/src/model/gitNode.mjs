export class GitNode {
    name
    avatar
    label
    id
  
    constructor(name, avatar, type, id) {
      this.name = name;
      this.avatar = avatar;
      this.label = type;
      this.id = id
    }
  }
