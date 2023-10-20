import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuardIamService, ForgotComponent, LoginComponent, RegisterComponent, ResetComponent, VerifyComponent } from 'arlas-wui-toolkit';
import { HomeComponent } from './components/home/home.component';

const routes: Routes = [
  {
    path: '', component: HomeComponent, canActivate: [AuthGuardIamService],
  },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'verify/:id/user/:token', component: VerifyComponent },
  { path: 'password_forgot', component: ForgotComponent },
  { path: 'reset/:id/user/:token', component: ResetComponent },
  // otherwise redirect to login
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
