import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Prediction, SmilesInput} from './backend.types';
import {Observable} from 'rxjs';
import 'rxjs/add/operator/map'

const SERVER_URL = '/';


@Injectable({
  providedIn: 'root'
})
export class PredictService {

  constructor(private http: HttpClient) { }

  public predict(smilesInput: SmilesInput): Observable<any> {
    return this.http.post(
        '${SERVER_URL}predict', smilesInput
    ).map(
        (res) => res
    );
  }
}
