import { Routes } from '@angular/router';
import { PrimerComponenteComponent } from './components/primer-componente/primer-componente.component';

export const routes: Routes = [
  { path: '', component: PrimerComponenteComponent },
  { path: '**', redirectTo: '' }
];
