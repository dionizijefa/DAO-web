import { Component, OnInit } from '@angular/core';
import {Explanation, Prediction, SmilesInput} from '../backend.types';
import {PredictService} from '../predict.service';
import {NgForm} from '@angular/forms';
import {
    create,
    forceCenter,
    forceCollide,
    forceLink,
    forceManyBody,
    forceSimulation,
    json,
    select
} from '../../custom-d3';
@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {
    public prediction: Prediction;
    public generatedPrediction = false;
    public moleculeSmiles: SmilesInput;
    public explainerRunning = false;
    public explanation: Explanation;
    public generatedExplanation = false;

    constructor(private predictService: PredictService) {
    }

    ngOnInit() {
    }

    public predict(smilesInput) {
        this.generatedPrediction = true;
        this.moleculeSmiles = smilesInput;
        return this.predictService.predict(smilesInput).subscribe(
            (prediction) => {
                this.prediction = prediction;
            },
        );
    }

    public explain(smilesInput) {
        return this.predictService.explain(smilesInput).subscribe(
            (explanation) => {
                this.explanation = explanation;
                this.explainerRunning = false;
                this.generatedExplanation = true;
                console.log(this.explanation.graph)
            },
        );
    }

    onSubmit(f: NgForm) {
        this.predict(f.value);
    }

    onExplain() {
        this.explainerRunning = true;
        this.explain(this.moleculeSmiles);
    }
}
