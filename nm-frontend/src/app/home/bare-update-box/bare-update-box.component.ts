import {Component, Input} from '@angular/core';
import {BareUpdateEntry} from '../models/site';
import {getStatusClass} from '../utils/utils';
import {NgClass, NgOptimizedImage} from '@angular/common';

@Component({
  selector: 'app-bare-update-box',
  imports: [
    NgClass,
    NgOptimizedImage
  ],
  templateUrl: './bare-update-box.component.html',
  styleUrl: './bare-update-box.component.css'
})
export class BareUpdateBoxComponent{
  protected showPreview = false;

  @Input() update!: BareUpdateEntry;
  protected readonly getStatusClass = getStatusClass;

  toggleShowPreview() {
    this.showPreview = !this.showPreview;
  }
}
