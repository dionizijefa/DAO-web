import {AfterViewInit, Component, ElementRef, ViewChild} from '@angular/core';
import {PredictService} from '../predict.service';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.css']
})
export class PredictionComponent implements AfterViewInit {
    @ViewChild('moleculeVis') moleculeVis: ElementRef;
    public prediction;
    public moleculeSmiles;


  constructor(private predictService: PredictService) {
      this.prediction = this.predictService.prediction
      this.moleculeSmiles = this.predictService.moleculeSmiles
    }

  ngAfterViewInit() {
      // this.moleculeVis.nativeElement.innerHTML = this.predictService.prediction['moleculeVis']
  }
}
