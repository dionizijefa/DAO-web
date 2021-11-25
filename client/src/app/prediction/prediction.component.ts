import {AfterViewInit, Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {Explanation, Prediction, SmilesInput} from '../backend.types';
import {PredictService} from '../predict.service';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.css']
})
export class PredictionComponent implements AfterViewInit {
    @ViewChild('moleculeVis') moleculeVis: ElementRef;
    @ViewChild('moleculeGraph') moleculeGraph: ElementRef;
    @ViewChild('featuresGraph') featuresGraph: ElementRef;
    @ViewChild('shap') shap: ElementRef;
    public prediction;
    public moleculeSmiles;
    public explainerRunning = false;
    public explanation: Explanation;
    public generatedExplanation = false;
    public generatedComplementary = false;
    public complementaryRunning = false;
    public complementary;
    public explainRequestError = false;
    public complementRequestError = false;


  constructor(private predictService: PredictService) {
      this.prediction = this.predictService.prediction
      this.moleculeSmiles = this.predictService.moleculeSmiles
    }

  ngAfterViewInit() {
      this.moleculeVis.nativeElement.innerHTML = this.predictService.prediction['moleculeVis']
  }

  public explain(smilesInput) {
        return this.predictService.explain(smilesInput).subscribe(
            (explanation) => {
                this.explanation = explanation;
                this.moleculeGraph.nativeElement.innerHTML = this.explanation['graph']
                this.featuresGraph.nativeElement.innerHTML = this.explanation['featureImportance']
                this.generatedExplanation = true;
                this.explainerRunning = false;
                this.explainRequestError = false;
            },
            err => {
              if (err.status === 429) {
                  this.explainRequestError = true;
                  this.explainerRunning = false;
              }
          }
        );
  }

  public complement(smilesInput, prediction) {
      return this.predictService.complement(smilesInput, prediction).subscribe(
          (complementary) => {
              this.generatedComplementary = true;
              this.complementary = complementary;
              this.shap.nativeElement.innerHTML = this.complementary['force']
              this.complementaryRunning = false;
              this.complementRequestError = false;
          },
          err => {
              if (err.status === 429) {
                  this.complementRequestError = true
                  this.complementaryRunning = false;
              }
          }
      );
  }

  onExplain() {
        this.explainerRunning = true;
        this.explain(this.moleculeSmiles);
    }

  onComplementary() {
        this.complementaryRunning = true;
        this.complement(this.moleculeSmiles, this.prediction['predictedProbability'])
    }

  removeWarning(): void {
        this.explainRequestError = false;
        this.complementRequestError = false;
  }
}
