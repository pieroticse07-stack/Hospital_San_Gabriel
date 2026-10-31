import { Component } from '@angular/core';
import { PrimerComponenteComponent } from './components/primer-componente/primer-componente.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [PrimerComponenteComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {}
