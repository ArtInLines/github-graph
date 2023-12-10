export class GitNode {
  name: string;
  avatar: string;
  label: string;

  constructor(name: string, avatar: string = "", type: string) {
    this.name = name;
    this.avatar = avatar;
    this.label = type;
  }
}
