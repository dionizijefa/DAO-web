import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Prediction, SmilesInput} from './backend.types';
import {Observable} from 'rxjs';
import 'rxjs/add/operator/map'


const SERVER_URL = 'http://192.168.1.159:8081/';

@Injectable({
  providedIn: 'root'
})
export class PredictService {

  constructor(private http: HttpClient) { }

  public predict(smilesInput: SmilesInput): Observable<number> {
    return this.http.post<Prediction>(
        `${SERVER_URL}predict`, smilesInput
    ).map(
        (res) => res.predictedProbability
    );
  }
}

