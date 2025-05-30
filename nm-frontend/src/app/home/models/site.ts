
export interface UpdateEntryPreview {
  siteId: string;
  siteUrl: string;
  siteName: string;
  registeredAt: string;
  statusCode: number;
  error: string | undefined;
}

export interface BareUpdateEntry {
  registeredAt: string;
  textChange: string | undefined;
  imageChangeUrl: string | undefined;
  statusCode: number;
  error: string | undefined;
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
  siteType: string;
}

export interface SitePreview {
  siteId: string;
  siteName: string;
}
