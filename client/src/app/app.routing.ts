import { NgModule } from '@angular/core';
import { CommonModule, } from '@angular/common';
import { BrowserModule  } from '@angular/platform-browser';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { LandingComponent } from './landing/landing.component';
import {PredictionComponent} from './prediction/prediction.component';
import {DocumentationComponent} from './documentation/documentation.component';

const routes: Routes = [
    { path: '', redirectTo: 'landing', pathMatch: 'full' },
    { path: 'home', component: HomeComponent },
    { path: 'landing', component: LandingComponent },
    { path: 'prediction/:id', component: PredictionComponent },
    { path: 'documentation', component: DocumentationComponent},
    // { path: '**', component: LandingComponent },
];

@NgModule({
  imports: [
    CommonModule,
    BrowserModule,
    RouterModule.forRoot(routes, {
      useHash: true
    })
  ],
  exports: [
  ],
})
export class AppRoutingModule { }
