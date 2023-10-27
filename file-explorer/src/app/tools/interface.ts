export interface IngestPayload {
  inputs: {
    collection: string;
    catalog: string;
    url?: string;
    directory?: string;
  },
  outputs: any,
  response: "raw",
  subscriber: any
}

export class DynamicFileNode {
  constructor(
    public name: string,
    public path: string,
    public level = 1,
    public is_dir = false,
    public isLoading = false,
  ) { }
}

export interface Archive {
  name: string;
  path: string;
  is_dir: boolean;
  last_modification_date: string;
  creation_date: string;
  id: string;
  driver_name: string;
  status?: ProcessStatus;
}

export enum ProcessStatus {
  accepted = 'accepted',
  running = 'running',
  successful = 'successful',
  failed = 'failed',
  dismissed = 'dismissed'
}

export interface Process {
  processID: "download" | "ingest" | "directory_ingest",
  type: string,
  jobID: string,
  status: ProcessStatus,
  message: string,
  created: number,
  started: number,
  finished: number,
  updated: number,
  progress: number,
  links: any,
  resourceID: string;
}

export interface ProcessResult {
  total: number;
  status_list: Process[];
}