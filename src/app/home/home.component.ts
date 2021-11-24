import {Component, OnInit} from '@angular/core';
import {PredictService} from '../predict.service';
import {NgForm} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {
    predictionRunning = false;
    rdkitError = false;
    requestError = false;
    constructor(private predictService: PredictService, private router: Router) {
    }

    ngOnInit() {
    }

    public predict(smilesInput) {
        this.predictService.moleculeSmiles = smilesInput;
        this.removeWarning();
        this.predictionRunning = true;
        return this.predictService.predict(smilesInput).subscribe(
            (prediction) => {
                this.predictService.prediction = prediction;
                this.router.navigate(['/prediction', smilesInput['smilesInput']])
            },
            err => {
        if (err.status === 429) {
            this.requestError = true;
        } else {
            this.rdkitError = true;
        }
        this.predictionRunning = false;
       // check error status code is 500, if so, do some action
      }
      );
    }

    onSubmit(f: NgForm) {
        this.predict(f.value);
    }

    removeWarning(): void {
        this.rdkitError = false;
        this.requestError = false;
    }
}
