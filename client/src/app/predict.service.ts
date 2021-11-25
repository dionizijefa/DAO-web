import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Complementary, Explanation, Prediction, SmilesInput} from './backend.types';
import {Observable} from 'rxjs';
import 'rxjs/add/operator/map'


// const SERVER_URL = 'http://192.168.2.111:8081/';
const SERVER_URL = 'http://localhost:5000/'

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

  public explain(smilesInput: SmilesInput): Observable<Explanation> {
    return this.http.post<Explanation>(
        `${SERVER_URL}explain`, smilesInput
    ).map(
        (res) => res,
    );
  }

  public complement(smilesInput: SmilesInput, prediction: Prediction): Observable<Complementary> {
    return this.http.post<Complementary>(
        `${SERVER_URL}complement`, [smilesInput, prediction],
    ).map(
        (res) => res,
    );
  }
}

