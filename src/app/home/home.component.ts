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
    constructor(private predictService: PredictService, private router: Router) {
    }

    ngOnInit() {
    }

    public predict(smilesInput) {
        this.predictService.moleculeSmiles = smilesInput;
        return this.predictService.predict(smilesInput).subscribe(
            (prediction) => {
                this.predictService.prediction = prediction;
                this.router.navigate(['/prediction'])
            },
        );
    }

    onSubmit(f: NgForm) {
        this.predict(f.value);
    }
}
