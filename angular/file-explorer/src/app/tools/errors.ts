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

import { HttpErrorResponse } from '@angular/common/http';
import { ToastrService } from 'ngx-toastr';

export function emitErrors(toastr: ToastrService, err: HttpErrorResponse, message404: string, message403: string, message500: string) {
  if (err.status === 404) {
    toastr.error(message404);
  } else if (err.status === 403) {
    toastr.warning(message403);
  } else if (err.status === 500) {
    if (!!err.error && !!err.error.detail) {
      toastr.error(err.error.detail);
    } else {
      toastr.error(message500);
    }
  }
}
