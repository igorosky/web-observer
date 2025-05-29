
export interface UpdateEntryPreview {
  siteId: string;
  siteUrl: string;
  siteName: string;
  registeredAt: string;
  statusCode: number;
}

export interface BareUpdateEntry {
  registeredAt: string;
  change: string; //todo
  statusCode: number;
}

export interface SiteDetails {
  siteInfo: Site;
  updates: BareUpdateEntry[];
  trackedSince: string; //readonly
  description: string;
}

export interface Site {
  siteId: string; //readonly
  siteName: string;
  siteUrl: string; //readonly
  lastUpdateAt: string; //readonly
  cssSelector: string; //readonly
  elementName: string;
}

export interface SitePreview {
  siteId: string;
  siteName: string;
}
