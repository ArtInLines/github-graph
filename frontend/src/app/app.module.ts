import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import {NgxGraphModule} from "@swimlane/ngx-graph";
import { NetworkComponent } from './network/network.component';
import { HeaderComponent } from './header/header.component';
import { RequestComponent } from './request/request.component';
import {FormsModule} from "@angular/forms";

@NgModule({
  declarations: [
    AppComponent,
    NetworkComponent,
    HeaderComponent,
    RequestComponent
  ],
  imports: [
    BrowserModule,
    NgxGraphModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
