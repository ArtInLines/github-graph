import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import {NgxGraphModule} from "@swimlane/ngx-graph";
import { NetworkComponent } from './network/network.component';

@NgModule({
  declarations: [
    AppComponent,
    NetworkComponent
  ],
  imports: [
    BrowserModule,
    NgxGraphModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
