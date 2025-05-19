import {Component, Input} from '@angular/core';
import {BareUpdateEntry} from '../models/site';

@Component({
  selector: 'app-bare-update-box',
  imports: [],
  templateUrl: './bare-update-box.component.html',
  styleUrl: './bare-update-box.component.css'
})
export class BareUpdateBoxComponent {
    @Input() update!: BareUpdateEntry;
}
