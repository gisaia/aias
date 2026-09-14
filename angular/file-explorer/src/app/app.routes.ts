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

import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/home/home.component').then(m => m.HomeComponent)
  },
  {
    path: 'callback',
    redirectTo: '',
    pathMatch: 'full'
  },
  {
    path: 'login',
    loadComponent: () => import('arlas-wui-toolkit').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('arlas-wui-toolkit').then(m => m.RegisterComponent)
  },
  {
    path: 'verify/:id/user/:token',
    loadComponent: () => import('arlas-wui-toolkit').then(m => m.VerifyComponent)
  },
  {
    path: 'password_forgot',
    loadComponent: () => import('arlas-wui-toolkit').then(m => m.ForgotComponent)
  },
  {
    path: 'reset/:id/user/:token',
    loadComponent: () => import('arlas-wui-toolkit').then(m => m.ResetComponent)
  },
  {
    path: '**',
    redirectTo: ''
  }
];
