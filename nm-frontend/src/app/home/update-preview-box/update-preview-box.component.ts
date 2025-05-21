import {Component, Input} from '@angular/core';
import {UpdateEntryPreview} from '../models/site';
import {RouterLink} from '@angular/router';
import {NgClass} from '@angular/common';
import {getStatusClass} from '../utils/utils';

@Component({
  selector: 'app-update-box',
  imports: [
    RouterLink,
    NgClass
  ],
  templateUrl: './update-preview-box.component.html',
  styleUrl: './update-preview-box.component.css',
  standalone: true
})
export class UpdatePreviewBoxComponent {
  @Input() update!: UpdateEntryPreview;

  protected readonly getStatusClass = getStatusClass;
}
