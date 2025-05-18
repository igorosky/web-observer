import {Component, Input} from '@angular/core';
import {UpdateEntry} from '../models/site';

@Component({
  selector: 'app-update-box',
  imports: [],
  templateUrl: './update-box.component.html',
  styleUrl: './update-box.component.css',
  standalone: true
})
export class UpdateBoxComponent {
  @Input() update!: UpdateEntry;
}
