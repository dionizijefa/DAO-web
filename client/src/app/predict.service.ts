import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Prediction, SmilesInput} from './backend.types';
import {Observable} from 'rxjs';
import 'rxjs/add/operator/map'

// ovo kad samo flask koristimo
const SERVER_URL = 'http://0.0.0.0:8081/';

// const SERVER_URL = 'api/'
// ovo iznad je kad ide preko nginx-a

@Injectable({
  providedIn: 'root'
})
export class PredictService {
  public prediction: Prediction;
  public moleculeSmiles: SmilesInput;
  constructor(private http: HttpClient) { }


  public predict(smilesInput: SmilesInput): Observable<Prediction> {
    return this.http.post<Prediction>(
        `${SERVER_URL}predict`, smilesInput
    ).map(
        (res) => res,
    );
  }
}

