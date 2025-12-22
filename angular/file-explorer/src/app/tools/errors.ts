import { HttpErrorResponse } from "@angular/common/http";
import { ToastrService } from "ngx-toastr";

export function emitErrors(toastr: ToastrService, err: HttpErrorResponse, message404: string, message403: string, message500: string) {
  if (err.status === 404) {
    toastr.error(message404)
  } else if (err.status === 403) {
    toastr.warning(message403)
  } else if (err.status === 500) {
    if (!!err.error && !!err.error.detail) {
      toastr.error(err.error.detail);
    } else {
      toastr.error(message500)
    }
  }
}