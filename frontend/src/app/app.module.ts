import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import {NgxGraphModule} from "@swimlane/ngx-graph";
import { NetworkComponent } from './network/network.component';
import { HeaderComponent } from './header/header.component';

@NgModule({
  declarations: [
    AppComponent,
    NetworkComponent,
    HeaderComponent
  ],
  imports: [
    BrowserModule,
    NgxGraphModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
