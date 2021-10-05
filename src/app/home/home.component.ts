import { Component, OnInit } from '@angular/core';
import {Prediction, SmilesInput} from '../backend.types';
import {PredictService} from '../predict.service';
import {NgForm} from '@angular/forms';
import { Options } from '@angular-slider/ngx-slider';

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {
    public prediction: Prediction;
    public generatedPrediction = false;
    public approvedSlider: Options = {
            showTicksValues: true,
            floor: 0,
            ceil: 1,
            ticksArray: [0.2, 0.4, 0.6, 0.8],
            disabled: true,
            // stepsArray: [
            //   {value: 0.0, legend: 'With an error rate of at most 100% this class is true'},
            //   {value: 1.0, legend: 'With an error rate of at most 0% this class is true'},
            // ]
  };


    constructor(private predictService: PredictService) {
    }

    ngOnInit() {
    }

    public predict(smilesInput) {
        this.generatedPrediction = true;
        return this.predictService.predict(smilesInput).subscribe(
            (prediction) => {
                this.prediction = prediction;
            },
        );
    }

    onSubmit(f: NgForm) {
        this.predict(f.value);

    }
}
