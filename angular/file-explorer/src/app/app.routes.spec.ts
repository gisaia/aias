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

import { describe, expect, it } from 'vitest';
import { routes } from './app.routes';
import { HomeComponent } from './components/home/home.component';
import { ForgotComponent, LoginComponent, RegisterComponent, ResetComponent, VerifyComponent } from 'arlas-wui-toolkit';

describe('App Routes', () => {
  it('should define all expected routes', () => {
    const paths = routes.map(r => r.path);
    expect(paths).toContain('');
    expect(paths).toContain('callback');
    expect(paths).toContain('login');
    expect(paths).toContain('register');
    expect(paths).toContain('verify/:id/user/:token');
    expect(paths).toContain('password_forgot');
    expect(paths).toContain('reset/:id/user/:token');
    expect(paths).toContain('**');
  });

  it('should redirect callback to empty path with full match', () => {
    const callbackRoute = routes.find(r => r.path === 'callback');
    expect(callbackRoute).toBeDefined();
    expect(callbackRoute?.redirectTo).toBe('');
    expect(callbackRoute?.pathMatch).toBe('full');
  });

  it('should redirect wildcard to empty path', () => {
    const wildcardRoute = routes.find(r => r.path === '**');
    expect(wildcardRoute).toBeDefined();
    expect(wildcardRoute?.redirectTo).toBe('');
  });

  it('should lazy load HomeComponent for empty path', async () => {
    const homeRoute = routes.find(r => r.path === '');
    expect(homeRoute?.loadComponent).toBeDefined();
    const component = await (homeRoute?.loadComponent as () => Promise<any>)();
    expect(component).toBe(HomeComponent);
  });

  it('should lazy load toolkit auth components', async () => {
    const loginRoute = routes.find(r => r.path === 'login');
    const registerRoute = routes.find(r => r.path === 'register');
    const verifyRoute = routes.find(r => r.path === 'verify/:id/user/:token');
    const forgotRoute = routes.find(r => r.path === 'password_forgot');
    const resetRoute = routes.find(r => r.path === 'reset/:id/user/:token');

    expect(await (loginRoute?.loadComponent as () => Promise<any>)()).toBe(LoginComponent);
    expect(await (registerRoute?.loadComponent as () => Promise<any>)()).toBe(RegisterComponent);
    expect(await (verifyRoute?.loadComponent as () => Promise<any>)()).toBe(VerifyComponent);
    expect(await (forgotRoute?.loadComponent as () => Promise<any>)()).toBe(ForgotComponent);
    expect(await (resetRoute?.loadComponent as () => Promise<any>)()).toBe(ResetComponent);
  });
});
