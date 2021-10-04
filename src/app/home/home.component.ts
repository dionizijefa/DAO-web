import { Component, OnInit } from '@angular/core';
import {Prediction, SmilesInput} from '../backend.types';
import {PredictService} from '../predict.service';
import {NgForm} from '@angular/forms';

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {
    public predictedProbability: number;
    public generatedPrediction = false;

    constructor(private predictService: PredictService) { }

    ngOnInit() {}

    public predict(smilesInput) {
        return this.predictService.predict(smilesInput).subscribe(
            (predictedProbability) => {
                this.predictedProbability = predictedProbability;
            }
        );
    }

    onSubmit(f: NgForm) {
        this.predict(f.value);
        this.generatedPrediction = true;
        console.log(f)
    }
}
