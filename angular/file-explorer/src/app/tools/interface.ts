/*
 * Licensed to Gisaïa under one or more contributor
 * license agreements. See the NOTICE.txt file distributed with
 * this work for additional information regarding copyright
 * ownership. Gisaïa licenses this file to you under
 * the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

export interface IngestPayload {
  inputs: {
    collection: string;
    catalog: string;
    url?: string;
    directory?: string;
    annotations: string;
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