export class GitNode {
  name: string;
  avatar: string;
  label: string;
  id: string;

  constructor(name: string, avatar: string = "", type: string, id: string) {
    this.name = name;
    this.avatar = avatar;
    this.label = type;
    this.id = id;
  }
}
