export interface Site {
  siteId: string;
  siteName: string;
  siteUrl: string;
  lastUpdateAt: string;
}

export interface UpdateEntry {
  siteId: string;
  siteUrl: string;
  siteName: string;
  registeredAt: string;
}

export interface SiteDetails {
  siteInfo: Site;
  updates: UpdateEntry[];
  trackedSince: string;
  //whatever else will be needed
}
