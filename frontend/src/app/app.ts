import { Component } from '@angular/core';
import { FormularioPersonaComponent } from './components/formulario-persona/formulario-persona';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormularioPersonaComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {}
