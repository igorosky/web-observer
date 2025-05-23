import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {SitePreview} from '../models/site';
import {Observable} from 'rxjs';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-search-bar',
  imports: [
    FormsModule
  ],
  templateUrl: './search-bar.component.html',
  styleUrl: './search-bar.component.css'
})
export class SearchBarComponent implements OnInit {

  @Input() availableSites$!: Observable<SitePreview[]>;
  @Output() siteSelected = new EventEmitter<SitePreview>();

  private sitesToSearch?: SitePreview[];
  protected searchText: string = '';
  protected filteredSites: SitePreview[] = [];

  ngOnInit(): void {
    const coll = Intl.Collator("pl");
    this.availableSites$.subscribe({
      next: (sites) => {
        sites = sites.sort((a, b) => coll.compare(a.siteName, b.siteName));
        this.sitesToSearch = sites;
        this.filteredSites = [...this.sitesToSearch];
      },
      error: (errorMessage) => {
        alert(`Searching disabled due to the following error: ${errorMessage}`)
      }
    })
  }

  filterResults() {
    if (this.sitesToSearch === undefined) return;
    const searchText = this.searchText.trim().toLowerCase();
    console.log(searchText)
    if (this.searchText === '') this.filteredSites = [...this.sitesToSearch];
    else {
      this.filteredSites = this.sitesToSearch.filter(site => site.siteName.toLowerCase().includes(searchText));
    }
  }

  onSiteSelect(site: SitePreview) {
    this.searchText = '';
    this.filteredSites = [];
    this.siteSelected.emit(site);
  }

  protected isFocused = false;

  onSearchFocus() {
    this.isFocused = true;
  }

  onSearchBlur() {
    setTimeout(() => {
      if(this.sitesToSearch !== undefined) this.filteredSites = [...this.sitesToSearch];
      this.searchText = '';
      this.isFocused = false;
    }, 120);
  }

}
