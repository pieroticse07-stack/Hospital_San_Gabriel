import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Persona } from '../interfaces/persona';

@Injectable({
  providedIn: 'root'
})
export class PrimerComponenteService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/pacientes`;

  listar(): Observable<Persona[]> {
    return this.http.get<Persona[]>(this.baseUrl);
  }

  obtener(id: number): Observable<Persona> {
    return this.http.get<Persona>(`${this.baseUrl}/${id}`);
  }

  crear(persona: Persona): Observable<Persona> {
    return this.http.post<Persona>(this.baseUrl, persona);
  }

  actualizar(id: number, persona: Partial<Persona>): Observable<Persona> {
    return this.http.put<Persona>(`${this.baseUrl}/${id}`, persona);
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
