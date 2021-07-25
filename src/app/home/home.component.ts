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
    public smilesInput: SmilesInput = new SmilesInput();
    public predictedProbability: Prediction;

    constructor(private predictService: PredictService) { }

    ngOnInit() {}

    public predict() {
        this.predictService.predict(this.smilesInput).subscribe(
            (predictedProbability) => {
                this.predictedProbability = predictedProbability;
            }
        );
    }

    onSubmit(f: NgForm) {
        console.log(f.value)
    }
}
