import {Component, OnInit} from '@angular/core';
import {PredictService} from '../predict.service';
import {NgForm} from '@angular/forms';
import {Router} from '@angular/router';
@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {
    predictionRunning = false;
    rdkitError = false;
    constructor(private predictService: PredictService, private router: Router) {
    }

    ngOnInit() {
    }

    public predict(smilesInput) {
        this.predictService.moleculeSmiles = smilesInput;
        this.predictionRunning = true;
        return this.predictService.predict(smilesInput).subscribe(
            (prediction) => {
                this.predictService.prediction = prediction;
                this.router.navigate(['/prediction'])
            },
            err => {
        console.log(err);
        this.predictionRunning = false;
        this.rdkitError = true;
       // check error status code is 500, if so, do some action
      }
      );
    }

    onSubmit(f: NgForm) {
        this.predict(f.value);
    }

    removeWarning(): void {
        this.rdkitError = false;
    }
}
