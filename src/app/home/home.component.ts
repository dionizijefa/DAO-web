import {AfterViewInit, Component, ElementRef, OnInit, ViewChild, ViewChildren} from '@angular/core';
import {Explanation, Prediction, SmilesInput} from '../backend.types';
import {PredictService} from '../predict.service';
import {NgForm} from '@angular/forms';
import {NONE_TYPE} from "@angular/compiler";
@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {
    @ViewChild('moleculeVis') moleculeVis: ElementRef;
    @ViewChild('moleculeGraph') moleculeGraph: ElementRef;
    @ViewChild('featuresGraph') featuresGraph: ElementRef;
    @ViewChild('shap') shap: ElementRef;
    public prediction: Prediction;
    public moleculeSmiles: SmilesInput;
    public explainerRunning = false;
    public explanation: Explanation;
    public generatedExplanation = false;
    public generatedComplementary = false;
    public complementaryRunning = false;
    public complementary;

    constructor(private predictService: PredictService) {
    }

    ngOnInit() {
    }

    public predict(smilesInput) {
        this.moleculeSmiles = smilesInput;
        return this.predictService.predict(smilesInput).subscribe(
            (prediction) => {
                this.prediction = prediction;
                this.moleculeVis.nativeElement.innerHTML = this.prediction['moleculeVis']
                console.log(this.prediction['similarities'])
            },
        );
    }

    public explain(smilesInput) {
        return this.predictService.explain(smilesInput).subscribe(
            (explanation) => {
                this.explanation = explanation;
                this.moleculeGraph.nativeElement.innerHTML = this.explanation['graph']
                this.featuresGraph.nativeElement.innerHTML = this.explanation['featureImportance']
                this.generatedExplanation = true;
                this.explainerRunning = false;
            },
        );
    }

    public complement(smilesInput, prediction) {
        return this.predictService.complement(smilesInput, prediction).subscribe(
            (complementary) => {
                this.generatedComplementary = true;
                this.complementary = complementary;
                this.shap.nativeElement.innerHTML = this.complementary['force']
                this.complementaryRunning = false;
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

    onComplementary() {
        this.complementaryRunning = true;
        this.complement(this.moleculeSmiles, this.prediction['predictedProbability'])
    }
}
