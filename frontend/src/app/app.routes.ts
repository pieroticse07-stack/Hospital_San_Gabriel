import { Routes } from '@angular/router';
import { FormularioPersonaComponent } from './components/formulario-persona/formulario-persona';

export const routes: Routes = [
  { path: '', component: FormularioPersonaComponent },
  { path: '**', redirectTo: '' }
];
