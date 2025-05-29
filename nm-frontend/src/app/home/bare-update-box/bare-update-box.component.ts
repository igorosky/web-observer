import {Component, Input} from '@angular/core';
import {BareUpdateEntry} from '../models/site';
import {getStatusClass} from '../utils/utils';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-bare-update-box',
  imports: [
    NgClass
  ],
  templateUrl: './bare-update-box.component.html',
  styleUrl: './bare-update-box.component.css'
})
export class BareUpdateBoxComponent{

  @Input() update!: BareUpdateEntry;
  protected readonly getStatusClass = getStatusClass;
}
