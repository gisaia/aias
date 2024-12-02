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

import { CollectionViewer, DataSource, SelectionChange } from "@angular/cdk/collections";
import { FamService } from "../services/fam/fam.service";
import { BehaviorSubject, Observable, map, merge } from "rxjs";
import { FlatTreeControl } from "@angular/cdk/tree";
import { DynamicFileNode } from "./interface";

export class DynamicDataSource implements DataSource<DynamicFileNode> {
  dataChange = new BehaviorSubject<DynamicFileNode[]>([]);

  get data(): DynamicFileNode[] {
    return this.dataChange.value;
  }
  set data(value: DynamicFileNode[]) {
    this._treeControl.dataNodes = value;
    this.dataChange.next(value);
  }

  constructor(
    private _treeControl: FlatTreeControl<DynamicFileNode>,
    private famService: FamService
  ) { }

  connect(collectionViewer: CollectionViewer): Observable<DynamicFileNode[]> {
    this._treeControl.expansionModel.changed.subscribe(change => {
      if (
        (change as SelectionChange<DynamicFileNode>).added ||
        (change as SelectionChange<DynamicFileNode>).removed
      ) {
        this.handleTreeControl(change as SelectionChange<DynamicFileNode>);
      }
    });

    return merge(collectionViewer.viewChange, this.dataChange).pipe(map(() => this.data));
  }

  disconnect(collectionViewer: CollectionViewer): void { }

  /** Handle expand/collapse behaviors */
  handleTreeControl(change: SelectionChange<DynamicFileNode>) {
    if (change.added) {
      change.added.forEach(node => this.toggleNode(node, true));
    }
    if (change.removed) {
      change.removed
        .slice()
        .reverse()
        .forEach(node => this.toggleNode(node, false));
    }
  }

  /**
   * Toggle the node, remove from display list
   */
  toggleNode(node: DynamicFileNode, expand: boolean) {
    node.isLoading = true;
    const index = this.data.indexOf(node);
    if (expand) {
      this.famService.getFiles(node.path)
        .subscribe({
          next: (childrens: any[]) => {
            if (!childrens || index < 0) {
              // If no children, or cannot find the node
              return;
            }
            const nodes = childrens.map(
              child => this.famService.generateNode(child, node.level + 1)
            );
            this.data.splice(index + 1, 0, ...nodes);
            this.dataChange.next(this.data);
            node.isLoading = false
          }
        });
    } else {
      let count = 0;
      for (
        let i = index + 1;
        i < this.data.length && this.data[i].level > node.level;
        i++, count++
      ) { }
      this.data.splice(index + 1, count);
      this.dataChange.next(this.data);
      node.isLoading = false
    }

  }
}