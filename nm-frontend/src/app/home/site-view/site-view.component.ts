import {Component, inject, OnInit} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {HomeLoaderService} from '../home-loader.service';
import {SiteDetails} from '../models/site';
import {BareUpdateBoxComponent} from '../bare-update-box/bare-update-box.component';

@Component({
  selector: 'app-site-view',
  imports: [
    BareUpdateBoxComponent
  ],
  templateUrl: './site-view.component.html',
  styleUrl: './site-view.component.css'
})
export class SiteViewComponent implements OnInit {

  private homeLoaderService: HomeLoaderService = inject(HomeLoaderService);

  constructor(private activatedRoute: ActivatedRoute) {
  }

  siteFetchErrorMessage?: string = undefined;
  currentSite?: SiteDetails = undefined;

  ngOnInit(): void {
    this.activatedRoute.params.subscribe(params => {
      const siteId: string | undefined = params['site_id'];
      if(siteId === undefined) {
        this.currentSite = undefined;
        this.siteFetchErrorMessage = 'Site ID not provided. Cannot fetch details.';
        return;
      }
      this.fetchSiteDetails(siteId);
    })
  }

  private fetchSiteDetails(siteId: string){
    this.homeLoaderService.fetchSiteInfo(siteId).subscribe({
      next: (site) => {
        this.currentSite = site;
      },
      error: (errorMessage: string) => {
        this.siteFetchErrorMessage = errorMessage;
        this.currentSite = undefined;
      },
    })
  }

  refetchCurrentSiteDetails(){
    if(this.currentSite === undefined) return;
    this.fetchSiteDetails(this.currentSite.siteInfo.siteId);
  }
}
